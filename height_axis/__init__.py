# SPDX-License-Identifier: GPL-3.0-or-later
"""A passive height ruler. All mouse and keyboard events pass through."""

import itertools
import math
import traceback

import blf
import bpy
import gpu
from bpy.app.handlers import persistent
from bpy.props import BoolProperty, EnumProperty, FloatProperty, IntProperty, PointerProperty, StringProperty
from bpy.types import Operator, Panel, PropertyGroup
from bpy_extras import view3d_utils
from bpy_extras.io_utils import ImportHelper
from gpu_extras.batch import batch_for_shader
from mathutils import Vector

from .core import format_number, nice_step, tick_values
from . import reference, freeze, localization


_registered = False
_draw_handle = None
_sessions = {}
_hover = {}
_bounds_cache = {}
_epoch = 0
_last_error = ""
_shader = None
_last_live = {}


def _settings(scene):
    return getattr(scene, "height_axis", None)


def _needs_display(settings):
    return settings and (settings.enabled or (settings.show_reference and settings.reference_mesh))


def _needs_tracking(settings):
    return _needs_display(settings) and not settings.frozen


def _scene_scale(scene):
    # Blender uses scale_length even in scenes whose displayed unit system is NONE.
    return max(scene.unit_settings.scale_length, 1e-12)


def _unit(scene, settings, span):
    unit = settings.units
    if unit == 'SCENE':
        if scene.unit_settings.system == 'IMPERIAL':
            unit = 'FT'
        else:
            requested = scene.unit_settings.length_unit
            unit = {'MILLIMETERS': 'MM', 'CENTIMETERS': 'CM',
                    'METERS': 'M', 'FEET': 'FT', 'INCHES': 'IN'}.get(requested)
            if unit is None:
                metres = abs(span) * _scene_scale(scene)
                unit = 'MM' if 0 < metres < 0.01 else 'CM' if 0 < metres < 1 else 'M'
    per_metre, suffix = {'M': (1.0, 'm'), 'CM': (100.0, 'cm'),
                         'MM': (1000.0, 'mm'), 'FT': (1 / 0.3048, 'ft'),
                         'IN': (1 / 0.0254, 'in')}[unit]
    return _scene_scale(scene) * per_metre, suffix


def _object_bounds(context, obj):
    """World extents of actual evaluated vertices, not a rotated local box."""
    key = (obj.as_pointer(), _epoch)
    if key in _bounds_cache:
        return _bounds_cache[key]
    if obj.type not in {'MESH', 'CURVE', 'SURFACE', 'FONT', 'META', 'VOLUME'}:
        return None
    temporary = None
    evaluated = None
    try:
        if obj.type == 'MESH' and obj.mode == 'EDIT':
            import bmesh
            points = (vert.co for vert in bmesh.from_edit_mesh(obj.data).verts)
            matrix = obj.matrix_world
        else:
            depsgraph = context.evaluated_depsgraph_get()
            evaluated = obj.evaluated_get(depsgraph)
            matrix = evaluated.matrix_world
            if evaluated.type == 'MESH':
                points = (vert.co for vert in evaluated.data.vertices)
            elif obj.type == 'VOLUME':
                points = (Vector(corner) for corner in evaluated.bound_box)
            else:
                temporary = evaluated.to_mesh()
                points = (vert.co for vert in temporary.vertices) if temporary else iter(())
        low, high = [math.inf] * 3, [-math.inf] * 3
        for point in points:
            world = matrix @ point
            for axis in range(3):
                low[axis] = min(low[axis], world[axis])
                high[axis] = max(high[axis], world[axis])
        result = (tuple(low), tuple(high)) if all(math.isfinite(v) for v in low + high) else None
    finally:
        if temporary is not None and evaluated is not None:
            evaluated.to_mesh_clear()
    _bounds_cache[key] = result
    return result


def selection_bounds(context):
    bounds = [_object_bounds(context, obj) for obj in context.selected_objects
              if obj.visible_get(view_layer=context.view_layer)]
    bounds = [item for item in bounds if item is not None]
    if not bounds:
        return None
    low = tuple(min(item[0][axis] for item in bounds) for axis in range(3))
    high = tuple(max(item[1][axis] for item in bounds) for axis in range(3))
    return low, high


def _project(region, rv3d, point):
    result = view3d_utils.location_3d_to_region_2d(region, rv3d, point)
    if result is None or not all(math.isfinite(v) and abs(v) < 1e7 for v in result):
        return None
    return result


def ruler_layout(context, require_enabled=True):
    settings = _settings(context.scene)
    if not _needs_display(settings) or (require_enabled and not settings.enabled):
        return None
    if settings.frozen:
        return freeze.ruler_layout(context, _project, _unit)
    return _live_ruler_layout(context, require_enabled)


def _live_ruler_layout(context, require_enabled=True):
    """Return the exact draw model, also used by the Blender integration checks."""
    region, rv3d = context.region, context.region_data
    settings = _settings(context.scene)
    if (not _needs_display(settings) or (require_enabled and not settings.enabled)
            or not region or not rv3d):
        return None
    ui_scale = context.preferences.system.ui_scale
    offset = settings.left_offset * ui_scale
    bounds = selection_bounds(context)
    if bounds:
        low, high = bounds
        span = max(0.0, high[2] - low[2])
        bottom = Vector(((low[0] + high[0]) / 2, (low[1] + high[1]) / 2, low[2]))
        top = bottom + Vector((0, 0, span))
        p0, p1 = _project(region, rv3d, bottom), _project(region, rv3d, top)
        if p0 is None or p1 is None:
            return None
        corners = [_project(region, rv3d, Vector(corner))
                   for corner in itertools.product(*zip(low, high))]
        visible = [point for point in corners if point is not None]
        if not visible:
            return None
        if (max(p.x for p in visible) < 0 or min(p.x for p in visible) > region.width
                or max(p.y for p in visible) < 0 or min(p.y for p in visible) > region.height):
            return None
        x = max(16 * ui_scale, min(p.x for p in visible) - offset)
        x = min(x, region.width - 16 * ui_scale)
        label = 'SELECTION' if len(context.selected_objects) > 1 else context.selected_objects[0].name
        mode = 'SELECTION'
        centre_y = (p0.y + p1.y) / 2
        attachment_x, mouse_position = min(p.x for p in visible) - offset, None
    elif context.selected_objects:
        # Cameras, lights and empty helpers have no measurable surface height.
        return None
    else:
        hover = _hover.get(context.window.as_pointer())
        if not hover or hover[0] != context.area.as_pointer():
            return None
        mouse = Vector(hover[1])
        bottom = view3d_utils.region_2d_to_location_3d(
            region, rv3d, mouse, context.scene.cursor.location)
        span = settings.reference_metres / _scene_scale(context.scene)
        bottom.z -= span / 2
        top = bottom + Vector((0, 0, span))
        p0, p1 = _project(region, rv3d, bottom), _project(region, rv3d, top)
        if p0 is None or p1 is None:
            return None
        shift = mouse.y - (p0.y + p1.y) / 2
        p0.y += shift
        p1.y += shift
        x = mouse.x - offset
        label, mode, centre_y = 'REFERENCE', 'REFERENCE', mouse.y
        attachment_x, mouse_position = x, tuple(mouse)
    collapsed = abs(p1.y - p0.y) < 32 * ui_scale
    if collapsed:
        # Z has no useful vertical projection in a top/near-top view. The number
        # remains exact; use an explicitly marked diagram rather than a fake scale.
        half = 90 * ui_scale
        p0.y, p1.y = centre_y - half, centre_y + half
    factor, suffix = _unit(context.scene, settings, span)
    display_span = span * factor
    step_display = nice_step(display_span, p1.y - p0.y)
    step = step_display / factor
    ticks, values = [], []
    for value in tick_values(span, step):
        if collapsed or mode == 'REFERENCE':
            # Reference endpoints have a common screen translation; preserve the
            # perspective distribution of intermediate world-Z points as well.
            if collapsed or span <= 1e-12:
                y = p0.y + (p1.y - p0.y) * (value / span if span > 0 else 0)
            else:
                projected = _project(region, rv3d, bottom + Vector((0, 0, value)))
                if projected is None:
                    continue
                y = projected.y + shift
        else:
            projected = _project(region, rv3d, bottom + Vector((0, 0, value)))
            if projected is None:
                continue
            y = projected.y
        ticks.append((y, f'{format_number(value * factor)} {suffix}'))
        values.append(value)
    return {'x': x, 'y0': p0.y, 'y1': p1.y, 'span': span,
            'height_text': f'{format_number(display_span)} {suffix}',
            'label': label[:32], 'mode': mode, 'ticks': ticks, 'tick_values': values,
            'collapsed': collapsed, 'scale': ui_scale,
            'world_anchor': tuple(bottom), 'attachment_x': attachment_x, 'mouse': mouse_position,
            'extensions': ((p0.x, p0.y), (p1.x, p1.y)) if mode == 'SELECTION' and not collapsed else ()}


def _view_key(context):
    return (context.scene.as_pointer(), context.window.as_pointer(), context.area.as_pointer())


def _live_display(context):
    guide = _live_ruler_layout(context, require_enabled=False)
    if not guide:
        return None, None
    figure = reference.reference_layout(context, guide, _project, _scene_scale(context.scene), ignore_freeze=True)
    if figure:
        guide['x'] = figure['bounds'][0] - 22 * guide['scale']
    guide['points'] = ((guide['x'], guide['y0']), (guide['x'], guide['y1']))
    guide['tick_points'] = [((guide['x'], y), label) for y, label in guide['ticks']]
    stored_figure = figure or reference.reference_layout(
        context, guide, _project, _scene_scale(context.scene), ignore_freeze=True, ignore_visibility=True)
    _last_live[_view_key(context)] = freeze.capture(context, guide, stored_figure)
    return guide, figure


def display_layout(context):
    settings = _settings(context.scene)
    if not settings or not settings.frozen:
        return _live_display(context)
    guide = ruler_layout(context, require_enabled=False)
    figure = reference.reference_layout(context, guide, _project, _scene_scale(context.scene)) if guide else None
    return guide, figure


def _freeze_changed(self, context):
    if self.frozen:
        raw = None
        area = context.area
        if area and area.type == 'VIEW_3D' and context.window:
            region = next((r for r in area.regions if r.type == 'WINDOW'), None)
            if region and _needs_display(self):
                with context.temp_override(area=area, region=region):
                    _live_display(context)
                    raw = _last_live.get(_view_key(context))
        if raw:
            self.frozen_data, self.freeze_message = raw, ''
        else:
            self.frozen = False
            self.freeze_message = 'Display a ruler or figure in the viewport before freezing'
    else:
        self.frozen_data, self.freeze_message = '', ''
    _changed(self, context)


def _lines(segments, color, width, region):
    global _shader
    if not segments:
        return
    if _shader is None:
        _shader = gpu.shader.from_builtin('POLYLINE_UNIFORM_COLOR')
    vertices = [(x, y, 0) for segment in segments for x, y in segment]
    batch = batch_for_shader(_shader, 'LINES', {'pos': vertices})
    _shader.bind()
    _shader.uniform_float('viewportSize', gpu.state.viewport_get()[2:])
    _shader.uniform_float('lineWidth', width)
    _shader.uniform_float('color', color)
    batch.draw(_shader)


def _text(text, x, y, size, color, region, right=True):
    blf.size(0, size)
    width, _ = blf.dimensions(0, text)
    if right:
        x -= width
    x = max(5, min(x, region.width - width - 5))
    if y < 6 or y > region.height - size - 4:
        return
    blf.enable(0, blf.SHADOW)
    blf.shadow(0, 5, 0.0, 0.0, 0.0, 0.95)
    blf.shadow_offset(0, 1, -1)
    blf.color(0, *color)
    blf.position(0, x, y, 0)
    blf.draw(0, text)
    blf.disable(0, blf.SHADOW)


def _draw():
    global _last_error
    try:
        context = bpy.context
        if not _registered or context.area.type != 'VIEW_3D':
            return
        if not context.space_data.overlay.show_overlays:
            return
        model, figure = display_layout(context)
        if not model:
            return
        region, settings = context.region, _settings(context.scene)
        if figure:
            reference.draw_reference(context, figure)
        if not settings.enabled:
            _last_error = ''
            return
        scale, x, y0, y1 = model['scale'], model['x'], model['y0'], model['y1']
        p0, p1 = (Vector(point) for point in model['points'])
        direction = p1 - p0
        normal = Vector((direction.y, -direction.x)).normalized() if direction.length > 1e-6 else Vector((1, 0))
        color = (0.35, 0.86, 1.0, 1.0) if model['mode'] == 'SELECTION' else (1.0, 0.74, 0.33, 1.0)
        size = max(9, round(settings.font_size * scale))
        cap = 8 * scale
        lines = [(p0, p1), (p0 - normal * cap, p0 + normal * cap),
                 (p1 - normal * cap, p1 + normal * cap)]
        lines += [(Vector(point) - normal * 5 * scale, point) for point, _ in model['tick_points']]
        old_blend = gpu.state.blend_get()
        gpu.state.blend_set('ALPHA')
        try:
            if model['extensions']:
                extensions = [(point + normal * cap, (px, py)) for (px, py), point in
                              zip(model['extensions'], (p0, p1))]
                _lines(extensions, (*color[:3], 0.22), 1.0 * scale, region)
            _lines(lines, (0.01, 0.015, 0.02, 0.9), 4.0 * scale, region)
            _lines(lines, color, 1.6 * scale, region)
            for point, label in model['tick_points']:
                point = Vector(point)
                if (point - p1).length < (size + 8) and (point - p0).length > 1:
                    continue
                _text(label, point.x - 12 * scale, point.y - size * 0.35, size, (0.91, 0.94, 0.98, 1), region)
            upper, lower = max(y0, y1), min(y0, y1)
            title_y = min(region.height - size - 10, upper + 14 * scale)
            upper_point, lower_point = (p0, p1) if p0.y > p1.y else (p1, p0)
            _text(model['height_text'], upper_point.x + cap, title_y, size + 2, color, region)
            caption = ('FREEZE / ' + model['label']) if settings.frozen else (
                'Z height / diagram' if model['collapsed'] else 'Z / ' + model['label'])
            _text(caption, lower_point.x + cap, max(8, lower - 25 * scale), max(9, size - 2), color, region)
        finally:
            gpu.state.blend_set(old_blend)
        _last_error = ''
    except Exception:
        error = traceback.format_exc()
        if error != _last_error:
            print('[Height Axis] ' + error)
            _last_error = error


def _redraw():
    for window in bpy.context.window_manager.windows:
        for area in window.screen.areas:
            if area.type == 'VIEW_3D':
                area.tag_redraw()


def _start_trackers():
    if bpy.app.background or not _registered:
        return
    manager = bpy.context.window_manager
    if manager.is_interface_locked:
        return
    live = set()
    for window in manager.windows:
        key = window.as_pointer()
        settings = _settings(window.scene)
        if not _needs_tracking(settings):
            _sessions.pop(key, None)
            _hover.pop(key, None)
            continue
        live.add(key)
        if key in _sessions:
            continue
        area = next((area for area in window.screen.areas if area.type == 'VIEW_3D'), None)
        if area:
            region = next((region for region in area.regions if region.type == 'WINDOW'), None)
            if region:
                with bpy.context.temp_override(window=window, area=area, region=region):
                    bpy.ops.view3d.height_axis_tracker('INVOKE_DEFAULT')
    for key in set(_sessions) - live:
        _sessions.pop(key, None)
        _hover.pop(key, None)


def _service():
    if not _registered:
        return None
    _start_trackers()
    return 0.3


def _changed(self, context):
    _start_trackers()
    _redraw()


@persistent
def _depsgraph_changed(scene, depsgraph):
    global _epoch
    _epoch += 1
    _bounds_cache.clear()


@persistent
def _load_pre(*_args):
    _sessions.clear()
    _hover.clear()
    _bounds_cache.clear()
    _last_live.clear()
    reference.clear_gpu()


@persistent
def _undo_changed(*_args):
    _bounds_cache.clear()
    _last_live.clear()
    reference.clear_gpu()
    _redraw()


class HEIGHTAXIS_Settings(PropertyGroup):
    enabled: BoolProperty(name='Show Height Axis', default=False,
                          description='Show the selected geometry height, or a mouse-following reference ruler', update=_changed)
    frozen: BoolProperty(name='Freeze', default=False, update=_freeze_changed,
                         description='Pin the current ruler and figure in world space; uncheck to resume following')
    frozen_data: StringProperty(options={'HIDDEN'})
    freeze_message: StringProperty(options={'HIDDEN', 'SKIP_SAVE'})
    reference_metres: FloatProperty(name='Reference Height (m)', default=1.8, min=0.001, soft_max=100,
                                    precision=3, description='Reference ruler and figure height, always entered in metres', update=_changed)
    left_offset: IntProperty(name='Left Offset (px)', default=64, min=16, max=500, update=_changed)
    font_size: IntProperty(name='Font Size', default=14, min=10, max=28, update=_changed)
    units: EnumProperty(name='Display Units', default='SCENE', update=_changed,
                        items=[('SCENE', 'Scene', ''), ('M', 'm', ''), ('CM', 'cm', ''),
                               ('MM', 'mm', ''), ('FT', 'ft', ''), ('IN', 'in', '')])
    show_reference: BoolProperty(name='Show Reference Figure', default=False, update=_changed)
    reference_mesh: PointerProperty(type=bpy.types.Mesh)
    reference_name: StringProperty(name='Reference Model', default='')
    reference_yaw: FloatProperty(name='Figure Rotation', subtype='ANGLE', default=0, update=_changed)
    reference_opacity: FloatProperty(name='Figure Opacity', default=0.8, min=0.05, max=1,
                                     subtype='FACTOR', update=_changed)


class VIEW3D_OT_height_axis_load_reference(Operator, ImportHelper):
    bl_idname = 'view3d.height_axis_load_reference'
    bl_label = 'Load Reference Figure'
    bl_description = 'Load a model as a height reference beside your selection or mouse'
    bl_options = {'REGISTER', 'UNDO'}
    filename_ext = ''
    filter_glob: StringProperty(default='*.blend;*.fbx;*.obj;*.gltf;*.glb;*.stl', options={'HIDDEN'})
    up_axis: EnumProperty(name='Imported Up Axis', default='Z',
                          items=[('Z', 'Z (usual choice)', ''), ('Y', 'Y', ''), ('X', 'X', '')])

    @classmethod
    def poll(cls, context):
        return context.mode == 'OBJECT'

    def draw(self, context):
        self.layout.prop(self, 'up_axis')

    def execute(self, context):
        try:
            mesh = reference.load_reference(context, self.filepath, self.up_axis)
        except Exception as error:
            tr = bpy.app.translations.pgettext_iface
            self.report({'ERROR'}, tr('Reference import failed') + ': ' + tr(str(error)))
            return {'CANCELLED'}
        if context.scene.height_axis.frozen:
            context.scene.height_axis.frozen = False
        _bounds_cache.clear()
        _changed(None, context)
        self.report({'INFO'}, bpy.app.translations.pgettext_iface('Reference figure loaded') + f' ({len(mesh.polygons):,} faces)')
        return {'FINISHED'}


class VIEW3D_OT_height_axis_clear_reference(Operator):
    bl_idname = 'view3d.height_axis_clear_reference'
    bl_label = 'Remove Reference Figure'
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        reference.clear_reference(context.scene.height_axis)
        _changed(None, context)
        return {'FINISHED'}


class VIEW3D_OT_height_axis_tracker(Operator):
    bl_idname = 'view3d.height_axis_tracker'
    bl_label = 'Height Axis Mouse Tracker'
    bl_options = {'INTERNAL'}

    def invoke(self, context, event):
        self.window_key = context.window.as_pointer()
        if self.window_key in _sessions:
            return {'CANCELLED'}
        self.token = object()
        _sessions[self.window_key] = self.token
        context.window_manager.modal_handler_add(self)
        return {'RUNNING_MODAL'}

    def modal(self, context, event):
        settings = _settings(context.window.scene) if context.window else None
        if (not _registered or _sessions.get(self.window_key) is not self.token
                or not _needs_tracking(settings)):
            if _sessions.get(self.window_key) is self.token:
                _sessions.pop(self.window_key, None)
                _hover.pop(self.window_key, None)
            return {'FINISHED'}
        if event.type == 'WINDOW_DEACTIVATE':
            _hover.pop(self.window_key, None)
            _redraw()
        elif event.type in {'MOUSEMOVE', 'INBETWEEN_MOUSEMOVE'}:
            _hover.pop(self.window_key, None)
            for area in context.window.screen.areas:
                if area.type != 'VIEW_3D':
                    continue
                if any(region.type in {'UI', 'TOOLS', 'HEADER', 'TOOL_HEADER'}
                       and region.width > 1 and region.height > 1
                       and region.x <= event.mouse_x < region.x + region.width
                       and region.y <= event.mouse_y < region.y + region.height
                       for region in area.regions):
                    continue
                region = next((region for region in area.regions if region.type == 'WINDOW'
                               and region.x <= event.mouse_x < region.x + region.width
                               and region.y <= event.mouse_y < region.y + region.height), None)
                if region:
                    _hover[self.window_key] = (area.as_pointer(),
                                               (event.mouse_x - region.x, event.mouse_y - region.y))
                    area.tag_redraw()
                    break
            # Also erase the old ruler when the mouse crosses into another editor.
            _redraw()
        return {'PASS_THROUGH'}


class VIEW3D_PT_height_axis(Panel):
    bl_label = 'Height Axis'
    bl_idname = 'VIEW3D_PT_height_axis'
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'Scale'

    def draw(self, context):
        layout, settings = self.layout, _settings(context.scene)
        layout.prop(settings, 'enabled')
        row = layout.row()
        row.active = bool(_needs_display(settings)) or settings.frozen
        row.prop(settings, 'frozen')
        if settings.freeze_message:
            layout.label(text=settings.freeze_message, icon='INFO')
        column = layout.column()
        column.active = bool(_needs_display(settings))
        geometry = column.column()
        geometry.enabled = not settings.frozen
        geometry.prop(settings, 'reference_metres')
        geometry.prop(settings, 'left_offset')
        column.prop(settings, 'units')
        column.prop(settings, 'font_size')
        layout.separator()
        layout.operator('view3d.height_axis_load_reference', icon='FILE_FOLDER')
        if settings.reference_mesh:
            layout.prop(settings, 'show_reference')
            layout.label(text=settings.reference_name, icon='OUTLINER_OB_MESH')
            row = layout.row()
            row.enabled = not settings.frozen
            row.prop(settings, 'reference_yaw')
            layout.prop(settings, 'reference_opacity')
            layout.operator('view3d.height_axis_clear_reference', icon='X')
        if context.mode != 'OBJECT':
            layout.label(text='Switch to Object Mode to load a figure', icon='INFO')
        layout.separator()
        if settings.frozen:
            layout.label(text='Pinned in world space', icon='LOCKED')
        else:
            layout.label(text='Selection: view-left')
            layout.label(text='No selection: mouse-left')
        if not context.space_data.overlay.show_overlays:
            layout.label(text='Enable viewport Overlays to see the guides', icon='INFO')
        if _last_error:
            layout.label(text='Draw error; see the system console', icon='ERROR')


_CLASSES = (HEIGHTAXIS_Settings, VIEW3D_OT_height_axis_load_reference,
            VIEW3D_OT_height_axis_clear_reference, VIEW3D_OT_height_axis_tracker, VIEW3D_PT_height_axis)


def register():
    global _registered, _draw_handle
    if _registered:
        return
    for cls in _CLASSES:
        bpy.utils.register_class(cls)
    bpy.types.Scene.height_axis = PointerProperty(type=HEIGHTAXIS_Settings)
    localization.register()
    _registered = True
    if not bpy.app.background:
        _draw_handle = bpy.types.SpaceView3D.draw_handler_add(_draw, (), 'WINDOW', 'POST_PIXEL')
        bpy.app.timers.register(_service, first_interval=0.1, persistent=True)
    bpy.app.handlers.depsgraph_update_post.append(_depsgraph_changed)
    bpy.app.handlers.load_pre.append(_load_pre)
    bpy.app.handlers.undo_post.append(_undo_changed)
    bpy.app.handlers.redo_post.append(_undo_changed)


def unregister():
    global _registered, _draw_handle, _shader, _last_error
    _registered = False
    if bpy.app.timers.is_registered(_service):
        bpy.app.timers.unregister(_service)
    _sessions.clear()
    _hover.clear()
    _bounds_cache.clear()
    _last_live.clear()
    reference.clear_gpu()
    if _draw_handle is not None:
        bpy.types.SpaceView3D.draw_handler_remove(_draw_handle, 'WINDOW')
        _draw_handle = None
    for handlers, callback in ((bpy.app.handlers.depsgraph_update_post, _depsgraph_changed),
                               (bpy.app.handlers.load_pre, _load_pre),
                               (bpy.app.handlers.undo_post, _undo_changed),
                               (bpy.app.handlers.redo_post, _undo_changed)):
        if callback in handlers:
            handlers.remove(callback)
    if hasattr(bpy.types.Scene, 'height_axis'):
        del bpy.types.Scene.height_axis
    for cls in reversed(_CLASSES):
        bpy.utils.unregister_class(cls)
    localization.unregister()
    _shader, _last_error = None, ''
    _redraw()
