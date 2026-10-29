# SPDX-License-Identifier: GPL-3.0-or-later
"""Object attachments coexist with live guides and preserve independent saved looks."""

import json
import math
from pathlib import Path
import sys
from unittest.mock import patch

import bpy
from mathutils import Quaternion, Vector

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
import height_axis as addon

checks = []


def check(name, condition):
    assert condition, name
    checks.append(name)


def close(a, b):
    return abs(a - b) < 1e-5


def select(obj=None):
    for other in bpy.context.view_layer.objects:
        other.select_set(other == obj)
    bpy.context.view_layer.objects.active = obj
    bpy.context.view_layer.update()


addon.register()
scene = bpy.context.scene
settings = scene.height_axis
check('a new scene has no attachments', len(scene.height_axis_attachments) == 0)
target_a = bpy.data.objects['Cube']
target_a.name = 'Target A'
target_a.location = (-3, 0, 1.6)
target_a.scale = (.65, .5, 1.6)
target_b = target_a.copy()
target_b.data = target_a.data.copy()
scene.collection.objects.link(target_b)
target_b.name = 'Target B'
target_b.location = (3, 0, 1.2)
target_b.scale = (.5, .4, 1.2)
scene.unit_settings.system = 'METRIC'
settings.enabled = True
settings.follow_smoothing = 0
bpy.ops.view3d.height_axis_load_reference(filepath=str(ROOT / 'tests/fixtures/mannequin.blend'))
mesh = settings.reference_mesh
settings.line_color = (.7, .9, 1, .6)
settings.reference_opacity = .35
settings.tick_spacing = 36
settings.font_size = 19
settings.font_path = str(ROOT / 'tests/missing-attachment.ttf')
select(target_a)
objects_before = set(scene.objects)
check('attach operator creates an entry', bpy.ops.view3d.height_axis_attach() == {'FINISHED'})
entry = scene.height_axis_attachments[0]
check('attachment uses an object pointer and stable identity', entry.target == target_a and bool(entry.uid))
check('attachment leaves live Freeze off', not settings.frozen)
check('attachment adds no selectable objects', set(scene.objects) == objects_before)
check('attachment retains the current reference mesh', entry.reference_mesh == mesh)
saved_style = addon.attachments.style(entry)
check('ruler and figure choices are captured together', saved_style.enabled and saved_style.show_reference)
check('font paths are resolved at creation', not saved_style.font_path.startswith('//'))
check('appearance is snapshotted independently', saved_style.font_size == 19 and close(saved_style.tick_spacing, 36))

area = next(a for a in bpy.context.screen.areas if a.type == 'VIEW_3D')
region = next(r for r in area.regions if r.type == 'WINDOW')
area.spaces.active.region_3d.view_perspective = 'PERSP'
with bpy.context.temp_override(area=area, region=region):
    select(target_b)
    attached = list(addon.attachments.layouts(bpy.context))
    live, live_figure = addon.display_layout(bpy.context)
    check('selecting B retains the attached reference beside A', len(attached) == 1 and attached[0][0]['label'] == 'Target A')
    check('B still has its separate live ruler and figure', live['label'] == 'Target B' and live_figure is not None)
    with patch.object(addon, '_draw_model') as draw:
        addon._draw()
    check('draw submits both attached and live references', draw.call_count == 2 and not addon._last_error)
    settings.show_reference = False
    bpy.ops.view3d.height_axis_attach()
    settings.enabled, settings.show_reference = False, True
    select(target_a)
    settings.reference_metres = 1.6
    bpy.ops.view3d.height_axis_attach()
    attached = list(addon.attachments.layouts(bpy.context))
    check('multiple attachments coexist', len(attached) == 3)
    check('ruler-only entry contains no reference mesh', not attached[1][2].show_reference and attached[1][1] is None
          and scene.height_axis_attachments[1].reference_mesh is None)
    check('figure-only entry does not enable its ruler', not attached[2][2].enabled and attached[2][1] is not None)
    check('figure-only snapshot retains its own physical height', close(attached[2][1]['height'], 1.6))
    settings.enabled = True
    settings.reference_metres, settings.font_size, settings.tick_spacing = 2.5, 12, 6
    settings.line_color = (1, .2, .2, .9)
    original_config = scene.height_axis_attachments[0].config
    old_mesh = scene.height_axis_attachments[0].reference_mesh
    bpy.ops.view3d.height_axis_load_reference(filepath=str(ROOT / 'tests/fixtures/mannequin.blend'))
    check('replacing the live figure does not replace attached meshes', settings.reference_mesh != old_mesh
          and scene.height_axis_attachments[0].reference_mesh == old_mesh)
    bpy.ops.view3d.height_axis_clear_reference()
    check('removing the live figure preserves saved attachment geometry', old_mesh.name in bpy.data.meshes and old_mesh.users >= 2)
    attached = list(addon.attachments.layouts(bpy.context))
    check('live style changes leave old appearance unchanged', attached[0][2].font_size == 19
          and close(attached[0][2].line_color[0], .7) and scene.height_axis_attachments[0].config == original_config)
    check('attached figure opacity is independent', close(attached[0][2].reference_opacity, .35))
    target_a.location += Vector((1, 2, 3))
    target_a.scale.z *= 2
    bpy.context.view_layer.update()
    attached = list(addon.attachments.layouts(bpy.context))
    guide = attached[0][0]
    check('target scaling updates the attached ruler height', close(guide['span'], 6.4))
    check('target movement updates the attachment base', close(guide['world_points'][0][2], 1.4))
    check('target scale does not stretch reference figure height', close(attached[0][1]['height'], 1.8))
    for angle in (0, 75, 170, 265):
        area.spaces.active.region_3d.view_rotation = (Quaternion((0, 0, 1), math.radians(angle))
                                                    @ Quaternion((1, 0, 0), math.radians(90)))
        guide = list(addon.attachments.layouts(bpy.context))[0][0]
        low, high = addon._object_bounds(bpy.context, target_a)
        centre = Vector(((low[0] + high[0]) / 2, (low[1] + high[1]) / 2, low[2]))
        right = area.spaces.active.region_3d.view_rotation @ Vector((1, 0, 0))
        check('attachment remains on view-left through orbit ' + str(angle),
              (Vector(guide['world_points'][0]) - centre).dot(right) < 0)
    modifier = target_a.modifiers.new('Height Array', 'ARRAY')
    modifier.count = 2
    modifier.relative_offset_displace = (0, 0, 1)
    bpy.context.view_layer.update()
    check('evaluated modifier changes update attachment height', close(list(addon.attachments.layouts(bpy.context))[0][0]['span'], 12.8))
    target_a.name = 'Renamed Target A'
    check('renaming a target retains the pointer and new readout name',
          scene.height_axis_attachments[0].target == target_a
          and list(addon.attachments.layouts(bpy.context))[0][0]['label'] == target_a.name)
    target_a.hide_set(True)
    check('hidden targets suppress their attachments', len(list(addon.attachments.layouts(bpy.context))) == 1)
    target_a.hide_set(False)
    select()
    addon._hover[bpy.context.window.as_pointer()] = (area.as_pointer(), (region.width * .65, region.height * .5))
    mouse, _ = addon.display_layout(bpy.context)
    check('mouse reference continues independently of the list', mouse['mode'] == 'REFERENCE' and len(list(addon.attachments.layouts(bpy.context))) == 3)
    select(target_b)
    settings.frozen = True
    frozen_data = settings.frozen_data
    target_a.location.z += 1
    bpy.context.view_layer.update()
    attached = list(addon.attachments.layouts(bpy.context))
    check('live Freeze does not freeze object attachments', settings.frozen and settings.frozen_data == frozen_data
          and close(attached[0][0]['world_points'][0][2], 2.4))
    count = len(scene.height_axis_attachments)
    bpy.ops.view3d.height_axis_attach()
    check('creating an attachment preserves an existing live Freeze', settings.frozen and len(scene.height_axis_attachments) == count + 1)
    bpy.ops.view3d.height_axis_attachment_remove(index=count)
    settings.frozen = False
    scene.height_axis_attachments[0].selected = True
    scene.height_axis_attachments[2].selected = True
    bpy.ops.view3d.height_axis_attachment_visibility(visible=False)
    check('batch hide affects only checked entries', [e.visible for e in scene.height_axis_attachments] == [False, True, False])
    check('batch hide does not hide targets', target_a.visible_get() and target_b.visible_get())
    bpy.ops.view3d.height_axis_attachment_visibility(visible=True)
    check('batch show restores all checked entries', all(e.visible for e in scene.height_axis_attachments))
    bpy.ops.view3d.height_axis_attachment_select(select=True)
    check('select all checks every entry', all(e.selected for e in scene.height_axis_attachments))
    bpy.ops.view3d.height_axis_attachment_select(select=False)
    check('select none clears the batch selection', not any(e.selected for e in scene.height_axis_attachments))
    scene.height_axis_attachments[1].visible = False
    check('single-entry visibility is independent', len(list(addon.attachments.layouts(bpy.context))) == 2)
    area.spaces.active.overlay.show_overlays = False
    with patch.object(addon, '_draw_model') as draw:
        addon._draw()
    check('Overlays off suppresses attached and live drawing', not draw.called)
    key = addon._view_key(bpy.context)
    check('Overlays off clears attachment animation caches', not any(k[:len(key)] == key for k in addon.placement._states))
    area.spaces.active.overlay.show_overlays = True

saved = ROOT / 'verification' / f'attachments-persistence-{bpy.app.version[0]}.{bpy.app.version[1]}.blend'
bpy.ops.wm.save_as_mainfile(filepath=str(saved))
bpy.ops.wm.open_mainfile(filepath=str(saved), load_ui=False)
scene, settings = bpy.context.scene, bpy.context.scene.height_axis
entries = scene.height_axis_attachments
check('all records survive save and reopen', len(entries) == 3)
check('saved target pointer survives rename and reopen', entries[0].target.name == 'Renamed Target A')
check('per-entry visibility survives reopen', [e.visible for e in entries] == [True, False, True])
check('style and reference mesh survive reopen', entries[0].config == original_config and entries[0].reference_mesh is not None)
check('multiple references retain the shared immutable figure', entries[0].reference_mesh == entries[2].reference_mesh)
addon.unregister()
addon.register()
entries = scene.height_axis_attachments
check('disabling and reenabling retains saved attachment records', len(entries) == 3)
check('reenabled records retain target and reference pointers', entries[0].target is not None and entries[0].reference_mesh is not None)
check('new scene starts with an independent attachment list', not bpy.data.scenes.new('Independent Scene').height_axis_attachments)
for entry in entries:
    entry.visible = True
target_a = entries[0].target
bpy.data.objects.remove(target_a, do_unlink=True)
check('deleted targets become missing pointers without deleting entries', len(entries) == 3 and entries[0].target is None and entries[2].target is None)
with bpy.context.temp_override(area=area, region=region):
    check('missing targets are skipped without layout errors', len(list(addon.attachments.layouts(bpy.context))) == 1)
check('invalid row removal cancels safely', bpy.ops.view3d.height_axis_attachment_remove(index=99) == {'CANCELLED'})
select(scene.objects['Target B'])
bpy.ops.view3d.height_axis_attach()
temporary = scene.height_axis_attachments[-1]
scene.collection.objects.unlink(temporary.target)
check('unlinked targets are recognized as missing in this scene', not addon.attachments.target_in_scene(scene, temporary))
with bpy.context.temp_override(area=area, region=region):
    check('unlinked target records are skipped without draw errors', not list(addon.attachments.layouts(bpy.context)))
scene.collection.objects.link(temporary.target)
bpy.ops.view3d.height_axis_attachment_remove(index=len(entries) - 1)
objects_before = set(scene.objects)
bpy.ops.view3d.height_axis_attachment_remove(index=0)
check('single remove only deletes an attachment record', len(entries) == 2 and set(scene.objects) == objects_before)
bpy.ops.view3d.height_axis_attachment_clear()
check('clear all removes every attachment record', not scene.height_axis_attachments)
check('clear all preserves all remaining scene objects', set(scene.objects) == objects_before)
check('attachment mutations are registered as undoable', all('UNDO' in cls.bl_options for cls in (
      addon.attachments.VIEW3D_OT_height_axis_attach, addon.attachments.VIEW3D_OT_height_axis_attachment_remove,
      addon.attachments.VIEW3D_OT_height_axis_attachment_clear, addon.attachments.VIEW3D_OT_height_axis_attachment_visibility)))
addon.unregister()
check('disable unregisters attachment properties', not hasattr(bpy.types.Scene, 'height_axis_attachments'))

result = {'blender': bpy.app.version_string, 'passed': len(checks), 'checks': checks}
(ROOT / 'verification' / f'attachments-checks-{bpy.app.version[0]}.{bpy.app.version[1]}.json').write_text(json.dumps(result, indent=2), encoding='utf-8')
print('ATTACHMENT_CHECKS=' + json.dumps(result))
