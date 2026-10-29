# SPDX-License-Identifier: GPL-3.0-or-later
"""Scene-saved object attachments, independent of live following and Freeze."""

import json
import sys
from functools import lru_cache
from types import SimpleNamespace
from uuid import uuid4

import bpy
from bpy.props import BoolProperty, CollectionProperty, IntProperty, PointerProperty, StringProperty
from bpy.types import Operator, Panel, PropertyGroup, UIList


STYLE_FIELDS = ('enabled', 'show_reference', 'reference_metres', 'reference_name', 'reference_yaw',
                'reference_opacity', 'object_gap_metres', 'left_offset', 'follow_smoothing',
                'show_extensions', 'font_size', 'line_width', 'tick_spacing', 'opacity',
                'line_color', 'text_color', 'font_path', 'units', 'show_half_height')
GEOMETRY_TYPES = {'MESH', 'CURVE', 'SURFACE', 'FONT', 'META', 'VOLUME'}


def _addon():
    return sys.modules[__package__]


def _changed(self, context):
    addon = _addon()
    addon.placement.clear()
    addon._changed(self, context)


@lru_cache(maxsize=128)
def config_data(raw):
    try:
        data = json.loads(raw)
        if data.get('version') == 1:
            # 1.4.0 attachments always displayed the half-height label.
            saved = dict(data['style'])
            saved.setdefault('show_half_height', True)
            if all(name in saved for name in STYLE_FIELDS):
                return saved
    except (ValueError, TypeError, KeyError, AttributeError):
        pass
    return None


def style(entry):
    data = config_data(entry.config)
    return SimpleNamespace(**data, frozen=False, reference_mesh=entry.reference_mesh) if data else None


def cache_key(view_key, entry):
    return (*view_key, 'attachment', entry.uid)


def has_visible(scene):
    return any(entry.visible and entry.target for entry in scene.height_axis_attachments)


def target_available(context, entry):
    target = entry.target
    return bool(target and target.name in context.view_layer.objects
                and target.visible_get(view_layer=context.view_layer))


def target_in_scene(scene, entry):
    return bool(entry.target and entry.target.name in scene.objects)


def layouts(context):
    addon = _addon()
    for entry in context.scene.height_axis_attachments:
        key = cache_key(addon._view_key(context), entry)
        settings = style(entry)
        if not entry.visible or not settings or not target_available(context, entry):
            addon.placement.forget(key)
            continue
        guide = addon._live_ruler_layout(context, require_enabled=False, settings=settings,
                                         target=entry.target, cache_key=key)
        if guide is None:
            addon.placement.forget(key)
            continue
        figure = addon.reference.reference_layout(context, guide, addon._project,
                    addon._scene_scale(context.scene), settings=settings, ignore_freeze=True)
        yield guide, figure, settings


class HEIGHTAXIS_Attachment(PropertyGroup):
    uid: StringProperty(options={'HIDDEN'})
    target: PointerProperty(type=bpy.types.Object)
    target_name: StringProperty(options={'HIDDEN'})
    visible: BoolProperty(name='Visible', default=True, update=_changed)
    selected: BoolProperty(name='Select for Batch', default=False)
    config: StringProperty(options={'HIDDEN'})
    reference_mesh: PointerProperty(type=bpy.types.Mesh)


class VIEW3D_OT_height_axis_attach(Operator):
    bl_idname = 'view3d.height_axis_attach'
    bl_label = 'Attach to Object'
    bl_description = 'Keep the current ruler and figure settings beside the active object while live following continues'
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):
        obj = context.active_object
        settings = getattr(context.scene, 'height_axis', None)
        return (context.mode == 'OBJECT' and obj is not None and obj.type in GEOMETRY_TYPES
                and obj in context.selected_objects and settings is not None and _addon()._needs_display(settings))

    def execute(self, context):
        target = context.active_object
        addon = _addon()
        if (not target.visible_get(view_layer=context.view_layer)
                or addon._object_bounds(context, target) is None):
            self.report({'WARNING'}, bpy.app.translations.pgettext_iface('Choose a visible geometric object'))
            return {'CANCELLED'}
        settings = context.scene.height_axis
        data = {name: getattr(settings, name) for name in STYLE_FIELDS}
        data['line_color'], data['text_color'] = list(settings.line_color), list(settings.text_color)
        data['show_reference'] = bool(settings.show_reference and settings.reference_mesh)
        # Resolve paths now so saving the blend elsewhere cannot change the chosen font.
        if data['font_path']:
            data['font_path'] = bpy.path.abspath(data['font_path'])
        entry = context.scene.height_axis_attachments.add()
        entry.uid = uuid4().hex
        entry.target, entry.target_name = target, target.name
        entry.config = json.dumps({'version': 1, 'style': data}, separators=(',', ':'))
        # The normalized reference is immutable. ID pointers retain it across live replacements.
        if data['show_reference']:
            entry.reference_mesh = settings.reference_mesh
        context.scene.height_axis_attachment_index = len(context.scene.height_axis_attachments) - 1
        _changed(self, context)
        return {'FINISHED'}


class VIEW3D_OT_height_axis_attachment_select(Operator):
    bl_idname = 'view3d.height_axis_attachment_select'
    bl_label = 'Select Attachment Entries'
    bl_options = {'REGISTER', 'UNDO'}
    select: BoolProperty(default=True)

    def execute(self, context):
        for entry in context.scene.height_axis_attachments:
            entry.selected = self.select
        return {'FINISHED'}


class VIEW3D_OT_height_axis_attachment_visibility(Operator):
    bl_idname = 'view3d.height_axis_attachment_visibility'
    bl_label = 'Set Selected Attachments Visibility'
    bl_description = 'Show or hide the checked attachment entries without changing their target objects'
    bl_options = {'REGISTER', 'UNDO'}
    visible: BoolProperty(default=True)

    @classmethod
    def poll(cls, context):
        return any(entry.selected for entry in context.scene.height_axis_attachments)

    def execute(self, context):
        for entry in context.scene.height_axis_attachments:
            if entry.selected:
                entry.visible = self.visible
        _changed(self, context)
        return {'FINISHED'}


def remove_entries(scene, indices):
    """Remove overlay records only; never unlink or delete target objects."""
    meshes = set()
    for index in sorted(set(indices), reverse=True):
        entry = scene.height_axis_attachments[index]
        if entry.reference_mesh:
            meshes.add(entry.reference_mesh)
        scene.height_axis_attachments.remove(index)
    scene.height_axis_attachment_index = max(0, min(scene.height_axis_attachment_index,
                                                   len(scene.height_axis_attachments) - 1))
    for mesh in meshes:
        if mesh.users == 0 and mesh.name.startswith('HeightAxis Reference - ') and 'height_axis_bounds' in mesh:
            bpy.data.meshes.remove(mesh)
    _addon().reference.clear_gpu()


class VIEW3D_OT_height_axis_attachment_remove(Operator):
    bl_idname = 'view3d.height_axis_attachment_remove'
    bl_label = 'Remove Attachment'
    bl_description = 'Remove this viewport reference; keep the target object'
    bl_options = {'REGISTER', 'UNDO'}
    index: IntProperty(default=-1)

    def execute(self, context):
        if not 0 <= self.index < len(context.scene.height_axis_attachments):
            return {'CANCELLED'}
        remove_entries(context.scene, [self.index])
        _changed(self, context)
        return {'FINISHED'}


class VIEW3D_OT_height_axis_attachment_clear(Operator):
    bl_idname = 'view3d.height_axis_attachment_clear'
    bl_label = 'Delete All Attachments'
    bl_description = 'Delete all attachment records in this scene; keep every target object'
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):
        return bool(context.scene.height_axis_attachments)

    def execute(self, context):
        remove_entries(context.scene, range(len(context.scene.height_axis_attachments)))
        _changed(self, context)
        return {'FINISHED'}


class HEIGHTAXIS_UL_attachments(UIList):
    def draw_item(self, context, layout, data, item, icon, active_data, active_propname, index):
        row = layout.row(align=True)
        row.prop(item, 'selected', text='')
        if target_in_scene(context.scene, item):
            row.label(text=item.target.name, icon='OBJECT_DATA', translate=False)
        else:
            row.label(text=bpy.app.translations.pgettext_iface('Missing target') + ': ' + item.target_name,
                      icon='ERROR', translate=False)
        settings = style(item)
        if settings:
            if settings.enabled:
                row.label(text='', icon='DRIVER_DISTANCE')
            if settings.show_reference:
                row.label(text='', icon='OUTLINER_OB_ARMATURE')
        row.prop(item, 'visible', text='', icon='HIDE_OFF' if item.visible else 'HIDE_ON', emboss=False)
        row.operator('view3d.height_axis_attachment_remove', text='', icon='X', emboss=False).index = index


class VIEW3D_PT_height_axis_attachments(Panel):
    bl_label = 'Object Attachments'
    bl_idname = 'VIEW3D_PT_height_axis_attachments'
    bl_parent_id = 'VIEW3D_PT_height_axis'
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'Scale'

    def draw(self, context):
        layout, scene = self.layout, context.scene
        layout.operator('view3d.height_axis_attach', icon='CONSTRAINT')
        entries = scene.height_axis_attachments
        if not entries:
            layout.label(text='Keep references beside multiple objects', icon='INFO')
            return
        layout.template_list('HEIGHTAXIS_UL_attachments', '', scene, 'height_axis_attachments',
                             scene, 'height_axis_attachment_index', rows=4, maxrows=8)
        row = layout.row(align=True)
        row.operator('view3d.height_axis_attachment_select', text='Select All').select = True
        row.operator('view3d.height_axis_attachment_select', text='Select None').select = False
        row = layout.row(align=True)
        row.enabled = any(entry.selected for entry in entries)
        row.operator('view3d.height_axis_attachment_visibility', text='Show Selected', icon='HIDE_OFF').visible = True
        row.operator('view3d.height_axis_attachment_visibility', text='Hide Selected', icon='HIDE_ON').visible = False
        layout.operator('view3d.height_axis_attachment_clear', icon='TRASH')
        if any(not target_in_scene(scene, entry) for entry in entries):
            layout.label(text='Missing targets are skipped', icon='INFO')


CLASSES = (HEIGHTAXIS_Attachment, VIEW3D_OT_height_axis_attach,
           VIEW3D_OT_height_axis_attachment_select, VIEW3D_OT_height_axis_attachment_visibility,
           VIEW3D_OT_height_axis_attachment_remove, VIEW3D_OT_height_axis_attachment_clear,
           HEIGHTAXIS_UL_attachments, VIEW3D_PT_height_axis_attachments)


def register_properties():
    bpy.types.Scene.height_axis_attachments = CollectionProperty(type=HEIGHTAXIS_Attachment)
    bpy.types.Scene.height_axis_attachment_index = IntProperty(default=0, min=0)


def unregister_properties():
    del bpy.types.Scene.height_axis_attachment_index
    del bpy.types.Scene.height_axis_attachments
    config_data.cache_clear()
