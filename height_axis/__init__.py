# SPDX-License-Identifier: GPL-3.0-or-later
"""A passive height ruler. All mouse and keyboard events pass through."""

import math
from pathlib import Path
import traceback

import blf
import bpy
import gpu
from bpy.app.handlers import persistent
from bpy.props import BoolProperty, EnumProperty, FloatProperty, FloatVectorProperty, IntProperty, PointerProperty, StringProperty
from bpy.types import Operator, Panel, PropertyGroup
from bpy_extras import view3d_utils
from bpy_extras.io_utils import ImportHelper
from gpu_extras.batch import batch_for_shader
from mathutils import Matrix, Vector

from .core import format_number, metric_ticks, metric_units, ruler_detail, visible_line_fraction
from . import reference, freeze, localization, fonts, placement, attachments


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
    if unit == 'AUTO':
        metres = abs(span) * _scene_scale(scene)
        unit = 'MM' if 0 < metres < 0.01 else 'CM' if 0 < metres < 1 else 'M'
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


def selection_name(context):
    objects = [obj for obj in context.selected_objects
               if obj.visible_get(view_layer=context.view_layer) and _object_bounds(context, obj) is not None]
    if not objects:
        return ''
    active = context.view_layer.objects.active
    main = active if active in objects else objects[0]
    return main.name if len(objects) == 1 else f'{main.name} (+{len(objects) - 1})'


def _project(region, rv3d, point):
    result = view3d_utils.location_3d_to_region_2d(region, rv3d, point)
    if result is None or not all(math.isfinite(v) and abs(v) < 1e7 for v in result):
        return None
    return result


def _mouse_plane_point(region, rv3d, coordinate, height=0.0):
    """Invert the viewport projection restricted to a horizontal world plane."""
    projection = rv3d.perspective_matrix
    plane = Matrix(tuple((projection[row][0], projection[row][1],
                          projection[row][2] * height + projection[row][3])
                         for row in (0, 1, 3)))
    try:
        ground = plane.inverted() @ Vector((2 * coordinate[0] / region.width - 1,
                                           2 * coordinate[1] / region.height - 1, 1))
    except ValueError:
        return None
    if abs(ground.z) < 1e-8:
        return None
    point = Vector((ground.x / ground.z, ground.y / ground.z, height))
    clip = projection @ point.to_4d()
    if not all(math.isfinite(value) for value in clip) or clip.w <= 0 or abs(clip.z) > clip.w:
        return None
    return point


def _below_ground_view(context):
    if context.region_data.view_location.z >= 0:
        return False
    found = False
    for obj in context.visible_objects:
        bounds = _object_bounds(context, obj)
        if bounds is not None:
            if bounds[1][2] >= 0:
                return False
            found = True
    return found


def ruler_layout(context, require_enabled=True):
    settings = _settings(context.scene)
    if not _needs_display(settings) or (require_enabled and not settings.enabled):
        return None
    if settings.frozen:
        guide = freeze.ruler_layout(context, _project, _unit)
        return _decorate_ruler(context, guide) if guide else None
    return _live_ruler_layout(context, require_enabled)


def _live_ruler_layout(context, require_enabled=True, settings=None, target=None, cache_key=None):
    """Place a vertical world-space ruler outside a view-independent envelope."""
    region, rv3d = context.region, context.region_data
    settings = settings or _settings(context.scene)
    key = cache_key or _view_key(context)
    if (not _needs_display(settings) or (require_enabled and not settings.enabled)
            or not region or not rv3d):
        return None
    scale = _scene_scale(context.scene)
    ui_scale = context.preferences.system.ui_scale or 1.0
    right = rv3d.view_rotation @ Vector((1, 0, 0))
    figure_height = settings.reference_metres / scale
    mesh = settings.reference_mesh if settings.show_reference else None
    figure_bounds = mesh.get('height_axis_bounds') if mesh else None
    figure_radius = (math.hypot(max(abs(figure_bounds[0]), abs(figure_bounds[3])),
                                max(abs(figure_bounds[1]), abs(figure_bounds[4]))) * figure_height
                     if figure_bounds else 0)
    bounds = _object_bounds(context, target) if target else selection_bounds(context)
    if target and not bounds:
        placement.forget(key)
        return None
    if not target and not bounds and settings.only_with_selection:
        placement.forget(key)
        return None
    if bounds:
        low, high = bounds
        span = max(0.0, high[2] - low[2])
        anchor = Vector(((low[0] + high[0]) / 2, (low[1] + high[1]) / 2, low[2]))
        radius = math.hypot(high[0] - low[0], high[1] - low[1]) / 2
        gap = settings.object_gap_metres / scale
        label = target.name if target else selection_name(context)
        mode = 'ATTACHMENT' if target else 'SELECTION'
        identity = (mode, target.as_pointer() if target else tuple(sorted(obj.as_pointer() for obj in context.selected_objects)))
        mouse_position = None
    elif context.selected_objects:
        # Cameras, lights and empty helpers have no measurable surface height.
        placement.forget(_view_key(context))
        return None
    else:
        hover = _hover.get(context.window.as_pointer())
        if not hover or hover[0] != context.area.as_pointer():
            placement.forget(key)
            return None
        mouse = Vector(hover[1])
        below_ground = _below_ground_view(context)
        height = (view3d_utils.region_2d_to_location_3d(region, rv3d, mouse, rv3d.view_location).z
                  if below_ground else 0.0)
        anchor = _mouse_plane_point(region, rv3d, mouse, height)
        if anchor is None:
            placement.forget(key)
            return None
        if settings.ruler_at_mouse:
            gap = 0.0
        else:
            shifted = _mouse_plane_point(region, rv3d, mouse - Vector((settings.left_offset * ui_scale, 0)), height)
            if shifted is None:
                placement.forget(key)
                return None
            right = anchor - shifted
            gap = right.length
        radius = 0.0
        span = figure_height
        label = ''
        mode = 'REFERENCE'
        identity = (mode, 'VIEW_DEPTH' if below_ground else 'GROUND', settings.ruler_at_mouse)
        mouse_position = tuple(mouse)
    goal = placement.target(anchor, right, span, radius, gap, figure_radius, figure_height,
                            settings.reference_yaw, identity)
    if mode == 'REFERENCE' and settings.ruler_at_mouse and figure_radius > 0:
        goal['anchor'] += anchor - placement.geometry(goal)['points'][0]
    world = placement.follow(key, goal, settings.follow_smoothing)
    points = [_project(region, rv3d, point) for point in world['points']]
    middle = _project(region, rv3d, world['midpoint'])
    if any(point is None for point in points) or middle is None:
        placement.forget(key)
        return None
    p0, p1 = points
    extensions = [_project(region, rv3d, point) for point in world['source_points']]
    factor, suffix = _unit(context.scene, settings, span)
    guide = {'cache_key': key, 'x': p0.x, 'y0': p0.y, 'y1': p1.y, 'span': span,
             'height_text': f'{format_number(span * factor)} {suffix}', 'label': label, 'mode': mode,
             'points': [tuple(point) for point in points], 'midpoint': tuple(middle),
             'world_points': [tuple(point) for point in world['points']],
             'world_midpoint': tuple(world['midpoint']), 'world_right': tuple(world['right']),
             'world_anchor': tuple(world['points'][0]), 'figure_matrix': world['figure_matrix'],
             'attachment_x': p0.x, 'mouse': mouse_position,
             'collapsed': (p1 - p0).length < 2 * ui_scale, 'scale': ui_scale,
             'extension_world': [tuple(point) for point in world['source_points']] if mode != 'REFERENCE' else [],
             'extensions': [tuple(point) for point in extensions] if mode != 'REFERENCE' and all(point is not None for point in extensions) else []}
    return _decorate_ruler(context, guide, settings)


def _decorate_ruler(context, guide, settings=None):
    settings, region, rv3d = settings or _settings(context.scene), context.region, context.region_data
    span, scale = guide['span'], _scene_scale(context.scene)
    a, b = (Vector(point) for point in guide['world_points'])
    visible = visible_line_fraction(*guide['points'], region.width, region.height)
    start, end = visible if visible else (0, 0)
    if getattr(rv3d, 'is_perspective', False):
        depths = [-(rv3d.view_matrix @ point).z for point in (a, b)]
        def world_fraction(value):
            denominator = depths[1] * (1 - value) + depths[0] * value
            return value * depths[0] / denominator if denominator > 1e-12 else value
        start, end = world_fraction(start), world_fraction(end)
    centre = (start + end) / 2
    delta = min(0.01, max(0.00001, (end - start) / 10))
    sample = [_project(region, rv3d, a.lerp(b, fraction)) for fraction in (centre - delta / 2, centre + delta / 2)]
    density = ((sample[1] - sample[0]).length / max(span * scale * delta, 1e-12)
               if all(point is not None for point in sample) else 0)
    density = placement.density(guide.get('cache_key', _view_key(context)), density, settings.follow_smoothing)
    guide['detail_alpha'] = ruler_detail(density * span * scale, guide['scale'])
    guide['compact_alpha'] = 1 - guide['detail_alpha']
    weights = metric_units(density)
    guide['metric_units'] = weights
    guide['pixels_per_metre'] = density
    factor, suffix = _unit(context.scene, settings, span)
    ticks, styles, world_ticks = [], [], []
    values = metric_ticks(span * scale, density, (start * span * scale, end * span * scale),
                          minimum_pixels=settings.tick_spacing * guide['scale']) if visible and guide['detail_alpha'] > 0.001 else []
    for metres, alpha, length in values:
        value = metres / scale
        world = a.lerp(b, value / span) if span > 0 else a
        point = _project(region, rv3d, world)
        if point is None:
            continue
        label = f'{format_number(value * factor)} {suffix}'
        ticks.append((tuple(point), label))
        styles.append((tuple(point), alpha, length))
        world_ticks.append((value, tuple(world)))
    guide['tick_points'], guide['tick_styles'], guide['tick_world'] = ticks, styles, world_ticks
    guide['ticks'] = [(point[1], label) for point, label in ticks]
    guide['tick_values'] = [value for value, _ in world_ticks]
    return guide


def _view_key(context):
    return (context.scene.as_pointer(), context.window.as_pointer(), context.area.as_pointer(), context.region.as_pointer())


def _live_display(context):
    guide = _live_ruler_layout(context, require_enabled=False)
    if not guide:
        return None, None
    figure = reference.reference_layout(context, guide, _project, _scene_scale(context.scene), ignore_freeze=True)
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
            placement.clear()
        else:
            self.frozen = False
            self.freeze_message = 'Display a ruler or figure in the viewport before freezing'
    else:
        self.frozen_data, self.freeze_message = '', ''
        placement.clear()
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


def _text(text, x, y, size, color, region, right=True, font_id=0, max_width=None):
    blf.size(font_id, size)
    if max_width is not None and blf.dimensions(font_id, text)[0] > max_width:
        if blf.dimensions(font_id, '...')[0] > max_width:
            return
        low, high = 0, len(text)
        while low < high:
            middle = (low + high + 1) // 2
            if blf.dimensions(font_id, text[:middle] + '...')[0] <= max_width:
                low = middle
            else:
                high = middle - 1
        text = text[:low] + '...'
    width, _ = blf.dimensions(font_id, text)
    if right:
        x -= width
    if y < 6 or y > region.height - size - 4:
        return
    blf.disable(font_id, blf.SHADOW)
    blf.color(font_id, *color)
    blf.position(font_id, x, y, 0)
    blf.draw(font_id, text)


def ruler_labels(context, model, unit=None, compact=False, settings=None):
    """Only physical half-height and full-height values, left of their marks."""
    settings, region = settings or _settings(context.scene), context.region
    size = max(9, round(settings.font_size * model['scale']))
    if unit is None and settings.units == 'AUTO' and model.get('metric_units'):
        unit = max(model['metric_units'], key=lambda item: item[1])[0]
    if unit:
        factor, suffix = {'M': (1.0, 'm'), 'CM': (100.0, 'cm'), 'MM': (1000.0, 'mm')}[unit]
        factor *= _scene_scale(context.scene)
    else:
        factor, suffix = _unit(context.scene, settings, model['span'])
    if compact:
        points, values = [Vector(model['midpoint'])], [model['span']]
    elif settings.show_half_height:
        points = [Vector(model['midpoint']), Vector(model['points'][1])]
        values = [model['span'] / 2, model['span']]
    else:
        points, values = [Vector(model['points'][1])], [model['span']]
    name_height = (max(8, round(size * 0.72)) + 4 * model['scale']
                   if model.get('label') and model.get('mode') != 'REFERENCE' else 0)
    labels = []
    for index, (point, value) in enumerate(zip(points, values)):
        if point.y < 0 or point.y > region.height:
            continue
        bottom_margin = 8 + name_height if index == len(points) - 1 else 8
        y = max(bottom_margin, min(point.y - size * 0.35, region.height - size - 8))
        labels.append(((point.x - 12 * model['scale'], y), f'{format_number(value * factor)} {suffix}'))
    if len(labels) == 2 and abs(labels[0][0][1] - labels[1][0][1]) < size + name_height + 12:
        return labels[1:]
    return labels


def ruler_name(context, model, compact=False, settings=None):
    if not model.get('label') or model.get('mode') == 'REFERENCE':
        return None
    point = Vector(model['midpoint'] if compact else model['points'][1])
    if point.y < 0 or point.y > context.region.height:
        return None
    scale = model['scale']
    size = max(9, round((settings or _settings(context.scene)).font_size * scale))
    small = max(8, round(size * 0.72))
    numeric_y = max(8 + small + 4 * scale, min(point.y - size * 0.35, context.region.height - size - 8))
    return ((point.x - 12 * scale, numeric_y - small - 4 * scale), model['label'], small)


def ruler_readout(context, model, unit=None, settings=None):
    """Move one full-height readout between detailed and compact presentation."""
    detail = model['detail_alpha']
    normal = ruler_labels(context, model, unit, settings=settings)
    compact = ruler_labels(context, model, unit, compact=True, settings=settings)
    full_text = compact[0][1] if compact else model['height_text']
    full = next((label for label in normal if label[1] == full_text), None)
    labels = [(point, text, detail) for point, text in normal if text != full_text]
    if full and compact:
        point = Vector(compact[0][0]).lerp(Vector(full[0]), detail)
        labels.append((tuple(point), full_text, 1.0))
    elif full:
        labels.append((*full, detail))
    elif compact:
        labels.append((*compact[0], 1 - detail))
    normal_name, compact_name = ruler_name(context, model, settings=settings), ruler_name(context, model, compact=True, settings=settings)
    name = None
    if normal_name and compact_name:
        point = Vector(compact_name[0]).lerp(Vector(normal_name[0]), detail)
        name = (tuple(point), *normal_name[1:], 1.0)
    elif normal_name:
        name = (*normal_name, detail)
    elif compact_name:
        name = (*compact_name, 1 - detail)
    return labels, name


def _draw_model(context, model, figure, settings=None):
    global _last_error
    try:
        region, settings = context.region, settings or _settings(context.scene)
        detail = model['detail_alpha']
        if figure and (not settings.enabled or detail > 0.001):
            reference.draw_reference(context, dict(figure, opacity=settings.reference_opacity),
                                     opacity=detail if settings.enabled else 1)
        if not settings.enabled:
            return
        scale = model['scale']
        p0, p1 = (Vector(point) for point in model['points'])
        color = (*settings.line_color[:3], settings.line_color[3] * settings.opacity * detail)
        cap, width = 7 * scale, settings.line_width * scale
        middle = Vector(model['midpoint'])
        anchors = []
        for point in (p0, middle, p1):
            if all((point - old).length > 2 * scale for old in anchors):
                anchors.append(point)
        marks = [(point - Vector((cap, 0)), point) for point in anchors]
        old_blend = gpu.state.blend_get()
        gpu.state.blend_set('ALPHA')
        try:
            if detail > 0.001 and settings.show_extensions and model['extensions']:
                extensions = [(point, (px, py)) for (px, py), point in
                              zip(model['extensions'], (p0, p1))]
                _lines(extensions, (*color[:3], color[3] * 0.3), max(0.35, width * 0.45), region)
            if detail > 0.001:
                _lines([(p0, p1)], color, width, region)
                _lines(marks, color, max(0.35, width * 0.65), region)
            groups = {}
            for point, alpha, length in model['tick_styles']:
                point = Vector(point)
                if any((point - mark).length <= 2 * scale for mark in anchors):
                    continue
                # Each decimal level shares an opacity, so a fade costs one draw call.
                groups.setdefault(alpha, []).append((point - Vector((5 * length * scale, 0)), point))
            for alpha, segments in groups.items():
                _lines(segments, (*color[:3], color[3] * alpha), max(0.35, width * 0.65), region)
            identifier = fonts.font_id(settings.font_path)
            # Handoff between units without superimposing different numerals.
            unit, unit_alpha = max(model['metric_units'], key=lambda item: item[1]) if settings.units == 'AUTO' else (None, 1)
            size = max(9, round(settings.font_size * scale))
            labels, name = ruler_readout(context, model, unit, settings=settings)
            for (x, y), label, visibility in labels:
                alpha = unit_alpha * visibility
                if alpha <= 0.001:
                    continue
                text_color = (*settings.text_color[:3], settings.text_color[3] * settings.opacity * alpha)
                _text(label, x, y, size, text_color, region, font_id=identifier)
            if name and name[3] > 0.001:
                (x, y), label, small, visibility = name
                text_color = (*settings.text_color[:3], settings.text_color[3] * settings.opacity * visibility * 0.75)
                _text(label, x, y, small, text_color, region, font_id=identifier,
                      max_width=max(0, min(260 * scale, x - 6)))
        finally:
            gpu.state.blend_set(old_blend)
    except Exception:
        _last_error = traceback.format_exc()


def _draw():
    global _last_error
    context = bpy.context
    if not _registered or context.area.type != 'VIEW_3D':
        return
    if not context.space_data.overlay.show_overlays:
        placement.forget_view(_view_key(context))
        return
    previous_error = _last_error
    _last_error = ''
    try:
        for model, figure, settings in attachments.layouts(context):
            _draw_model(context, model, figure, settings)
        model, figure = display_layout(context)
        if model:
            _draw_model(context, model, figure)
        else:
            placement.forget(_view_key(context))
    except Exception:
        _last_error = traceback.format_exc()
    if _last_error and _last_error != previous_error:
        print('[Scale Reference] ' + _last_error)


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
    keys = {(window.scene.as_pointer(), window.as_pointer(), area.as_pointer(), region.as_pointer())
            for window in bpy.context.window_manager.windows for area in window.screen.areas
            if area.type == 'VIEW_3D' for region in area.regions if region.type == 'WINDOW'}
    for key in tuple(keys):
        scene = next(window.scene for window in bpy.context.window_manager.windows if window.as_pointer() == key[1])
        keys.update(attachments.cache_key(key, entry) for entry in scene.height_axis_attachments if entry.visible and entry.target)
    placement.retain(keys)
    if any(_needs_display(_settings(window.scene)) or attachments.has_visible(window.scene)
           for window in bpy.context.window_manager.windows):
        if placement.animating():
            _redraw()
        return 1 / 60
    placement.clear()
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
    placement.clear()
    reference.clear_gpu()
    fonts.clear()


@persistent
def _undo_changed(*_args):
    _bounds_cache.clear()
    _last_live.clear()
    placement.clear()
    reference.clear_gpu()
    _redraw()


class HEIGHTAXIS_Settings(PropertyGroup):
    enabled: BoolProperty(name='Show Scale Reference', default=False,
                          description='Show the selected geometry height, or a mouse-following reference ruler', update=_changed)
    only_with_selection: BoolProperty(name='Only With Selection', default=True, update=_changed,
                                      description='Hide live guides without selected geometry; keep frozen and attached references')
    ruler_at_mouse: BoolProperty(name='Ruler at Mouse Tip', default=False, update=_changed,
                                description='Place the ruler base at the mouse tip instead of using the left gap; applies when no geometry is selected')
    frozen: BoolProperty(name='Freeze', default=False, update=_freeze_changed,
                         description='Pin the current ruler and figure in world space; uncheck to resume following')
    frozen_data: StringProperty(options={'HIDDEN'})
    freeze_message: StringProperty(options={'HIDDEN', 'SKIP_SAVE'})
    reference_metres: FloatProperty(name='Reference Height (m)', default=1.8, min=0.001, soft_max=100,
                                    precision=3, description='Reference ruler and figure height, always entered in metres', update=_changed)
    left_offset: IntProperty(name='Mouse Gap (px)', default=64, min=16, max=500, update=_changed)
    object_gap_metres: FloatProperty(name='Width Offset (m)', default=0.35, soft_min=-2, soft_max=5,
                                    precision=3, update=_changed,
                                    description='Offset from the widest horizontal extent; negative values move inside and may change surface clearance during orbit')
    follow_smoothing: FloatProperty(name='Follow Smoothing (s)', default=0.02, min=0, max=1,
                                    precision=3, update=_changed)
    show_extensions: BoolProperty(name='Show Connection Lines', default=False, update=_changed)
    font_size: IntProperty(name='Font Size', default=14, min=10, max=28, update=_changed)
    line_width: FloatProperty(name='Line Width (px)', default=1.1, min=0.25, max=8, precision=2, update=_changed)
    tick_spacing: FloatProperty(name='Tick Spacing (px)', default=24, min=4, max=80, soft_max=48,
                                 precision=1, update=_changed,
                                 description='Minimum screen spacing for minor ticks to fade in; larger values show fewer ticks')
    show_half_height: BoolProperty(name='Show Half-Height Value', default=False, update=_changed,
                                   description='Label the physical midpoint in addition to the full height; keep tick spacing unchanged')
    opacity: FloatProperty(name='Ruler Opacity', default=1, min=0, max=1, subtype='FACTOR', update=_changed)
    line_color: FloatVectorProperty(name='Line Color', subtype='COLOR', size=4,
                                    min=0, max=1, default=(1, 1, 1, 0.65), update=_changed)
    text_color: FloatVectorProperty(name='Text Color', subtype='COLOR', size=4,
                                    min=0, max=1, default=(1, 1, 1, 0.75), update=_changed)
    font_path: StringProperty(name='Font File', subtype='FILE_PATH', default='', update=_changed)
    units: EnumProperty(name='Display Units', default='AUTO', update=_changed,
                        items=[('AUTO', 'Auto (m / cm / mm)', ''), ('SCENE', 'Scene', ''), ('M', 'm', ''), ('CM', 'cm', ''),
                               ('MM', 'mm', ''), ('FT', 'ft', ''), ('IN', 'in', '')])
    show_reference: BoolProperty(name='Show Reference Figure', default=False, update=_changed)
    reference_mesh: PointerProperty(type=bpy.types.Mesh)
    reference_name: StringProperty(name='Reference Model', default='')
    reference_yaw: FloatProperty(name='Figure Rotation', subtype='ANGLE', default=0, update=_changed)
    reference_opacity: FloatProperty(name='Figure Opacity', default=0.8, min=0.05, max=1,
                                     subtype='FACTOR', update=_changed)


class VIEW3D_OT_height_axis_choose_font(Operator, ImportHelper):
    bl_idname = 'view3d.height_axis_choose_font'
    bl_label = 'Choose Font File'
    bl_description = 'Choose a local TTF, OTF or TTC font for the ruler labels'
    bl_options = {'REGISTER', 'UNDO'}
    filename_ext = ''
    filter_glob: StringProperty(default='*.ttf;*.otf;*.ttc', options={'HIDDEN'})

    def execute(self, context):
        try:
            fonts.font_id(self.filepath, strict=True)
        except ValueError as error:
            self.report({'ERROR'}, bpy.app.translations.pgettext_iface(str(error)))
            return {'CANCELLED'}
        context.scene.height_axis.font_path = self.filepath
        return {'FINISHED'}


class VIEW3D_OT_height_axis_default_font(Operator):
    bl_idname = 'view3d.height_axis_default_font'
    bl_label = 'Use Default Font'
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        context.scene.height_axis.font_path = ''
        return {'FINISHED'}


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
    bl_label = 'Scale Reference Mouse Tracker'
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
    bl_label = 'Scale Reference'
    bl_idname = 'VIEW3D_PT_height_axis'
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'Scale'

    def draw(self, context):
        layout, settings = self.layout, _settings(context.scene)
        layout.prop(settings, 'enabled')
        layout.prop(settings, 'only_with_selection')
        mouse = layout.row()
        mouse.enabled = not settings.only_with_selection and not settings.frozen
        mouse.prop(settings, 'ruler_at_mouse')
        row = layout.row()
        row.active = bool(_needs_display(settings)) or settings.frozen
        row.prop(settings, 'frozen')
        if settings.freeze_message:
            layout.label(text=settings.freeze_message, icon='INFO')
        if settings.frozen:
            layout.label(text='Pinned in world space', icon='LOCKED')
        elif context.selected_objects:
            layout.label(text='Selection: view-left')
        elif settings.only_with_selection:
            layout.label(text='No selection', icon='RESTRICT_SELECT_ON')
        elif settings.ruler_at_mouse:
            layout.label(text='No selection: mouse tip')
        else:
            layout.label(text='No selection: mouse-left')
        geometry = layout.column()
        geometry.active = bool(_needs_display(settings))
        geometry.enabled = not settings.frozen
        geometry.prop(settings, 'reference_metres')
        row = layout.row()
        row.active = bool(_needs_display(settings))
        row.prop(settings, 'units', text='Units')
        if not context.space_data.overlay.show_overlays:
            layout.label(text='Viewport Overlays are off', icon='INFO')
        if _last_error:
            layout.label(text='Draw error; see the system console', icon='ERROR')


class VIEW3D_PT_height_axis_reference(Panel):
    bl_label = 'Reference Figure'
    bl_idname = 'VIEW3D_PT_height_axis_reference'
    bl_parent_id = 'VIEW3D_PT_height_axis'
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'Scale'

    def draw(self, context):
        layout, settings = self.layout, _settings(context.scene)
        layout.operator('view3d.height_axis_load_reference', icon='FILE_FOLDER')
        if settings.reference_mesh:
            layout.prop(settings, 'show_reference')
            row = layout.row(align=True)
            row.label(text=settings.reference_name, icon='OUTLINER_OB_MESH', translate=False)
            row.operator('view3d.height_axis_clear_reference', text='', icon='X')
            row = layout.row()
            row.enabled = settings.show_reference and not settings.frozen
            row.prop(settings, 'reference_yaw')
            row = layout.row()
            row.active = settings.show_reference
            row.prop(settings, 'reference_opacity')
        if context.mode != 'OBJECT':
            layout.label(text='Switch to Object Mode to load a figure', icon='INFO')


class VIEW3D_PT_height_axis_placement(Panel):
    bl_label = 'Placement & Follow'
    bl_idname = 'VIEW3D_PT_height_axis_placement'
    bl_parent_id = 'VIEW3D_PT_height_axis'
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'Scale'
    bl_options = {'DEFAULT_CLOSED'}

    def draw(self, context):
        layout, settings = self.layout, _settings(context.scene)
        layout.active = bool(_needs_display(settings))
        geometry = layout.column()
        geometry.enabled = not settings.frozen
        geometry.prop(settings, 'object_gap_metres', slider=True)
        if settings.object_gap_metres < 0:
            geometry.label(text='Inside widest extent', icon='INFO')
            geometry.label(text='Orbit clearance may vary')
        mouse = geometry.row()
        mouse.enabled = not settings.ruler_at_mouse
        mouse.prop(settings, 'left_offset')
        geometry.prop(settings, 'follow_smoothing', slider=True)
        layout.prop(settings, 'show_extensions')


class VIEW3D_PT_height_axis_appearance(Panel):
    bl_label = 'Ruler Appearance'
    bl_idname = 'VIEW3D_PT_height_axis_appearance'
    bl_parent_id = 'VIEW3D_PT_height_axis'
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'Scale'
    bl_options = {'DEFAULT_CLOSED'}

    def draw(self, context):
        layout, settings = self.layout, _settings(context.scene)
        layout.prop(settings, 'font_size')
        layout.prop(settings, 'line_width')
        layout.prop(settings, 'tick_spacing', slider=True)
        layout.prop(settings, 'show_half_height')
        layout.prop(settings, 'opacity', slider=True)
        layout.prop(settings, 'line_color')
        layout.prop(settings, 'text_color')
        row = layout.row(align=True)
        row.operator('view3d.height_axis_choose_font', icon='FILE_FOLDER')
        if settings.font_path:
            row.operator('view3d.height_axis_default_font', text='', icon='LOOP_BACK')
            layout.label(text=Path(bpy.path.abspath(settings.font_path)).name, icon='FONT_DATA')
        if fonts.unavailable(settings.font_path):
            layout.label(text='Font unavailable; using Blender default', icon='INFO')


_CLASSES = (HEIGHTAXIS_Settings, VIEW3D_OT_height_axis_choose_font, VIEW3D_OT_height_axis_default_font,
            VIEW3D_OT_height_axis_load_reference, VIEW3D_OT_height_axis_clear_reference,
            VIEW3D_OT_height_axis_tracker, VIEW3D_PT_height_axis, VIEW3D_PT_height_axis_reference,
            VIEW3D_PT_height_axis_placement, VIEW3D_PT_height_axis_appearance, *attachments.CLASSES)


def register():
    global _registered, _draw_handle
    if _registered:
        return
    for cls in _CLASSES:
        bpy.utils.register_class(cls)
    bpy.types.Scene.height_axis = PointerProperty(type=HEIGHTAXIS_Settings)
    attachments.register_properties()
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
    placement.clear()
    reference.clear_gpu()
    fonts.clear()
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
    attachments.unregister_properties()
    for cls in reversed(_CLASSES):
        bpy.utils.unregister_class(cls)
    localization.unregister()
    _shader, _last_error = None, ''
    _redraw()
