# SPDX-License-Identifier: GPL-3.0-or-later
"""Selection-only defaults, optional labels and compatible saved references."""

import json
import math
from pathlib import Path
import sys
from types import SimpleNamespace
from unittest.mock import patch

import bpy
from mathutils import Matrix, Quaternion, Vector

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
import height_axis as addon

checks = []


def check(name, condition):
    assert condition, name
    checks.append(name)


def select(obj=None):
    for other in bpy.context.view_layer.objects:
        other.select_set(other == obj)
    bpy.context.view_layer.objects.active = obj
    bpy.context.view_layer.update()


def close(a, b):
    return abs(a - b) < 1e-5


addon.register()
scene, settings = bpy.context.scene, bpy.context.scene.height_axis
check('new scenes require selection without enabling the main display',
      settings.only_with_selection and not settings.enabled)
check('new scenes keep mouse-tip placement opt-in', not settings.ruler_at_mouse)
check('new scenes start without a loaded or visible figure',
      not settings.show_reference and settings.reference_mesh is None)
check('new scenes hide half-height values and retain 24 px minor ticks',
      not settings.show_half_height and close(settings.tick_spacing, 24))
check('default positional response is a slight 0.02 seconds', close(settings.follow_smoothing, .02))
goal = addon.placement.target((0, 0, 0), (1, 0, 0), 2, 1, .35, 0, 1.8, 0, 'responsive')
addon.placement.follow('responsive', goal, settings.follow_smoothing, now=0)
goal['anchor'] = Vector((10, 0, 0))
addon.placement.follow('responsive', goal, settings.follow_smoothing, now=1 / 60)
fraction = addon.placement._states['responsive']['anchor'].x / 10
check('one 60 Hz frame follows over half the movement while retaining slight easing', .5 < fraction < 1)
addon.placement.follow('responsive', goal, settings.follow_smoothing, now=.1)
check('default response settles within one percent in 0.1 seconds',
      (addon.placement._states['responsive']['anchor'] - goal['anchor']).length < .1)
addon.placement.clear()

language = bpy.context.preferences.view.language
bpy.context.preferences.view.language = 'zh_HANS'
bpy.context.preferences.view.use_translate_interface = True
check('selection-only checkbox has the extension Chinese translation',
      bpy.app.translations.pgettext_iface('Only With Selection') == '\u4ec5\u9009\u4e2d\u65f6\u663e\u793a')
check('half-height checkbox has the extension Chinese translation',
      bpy.app.translations.pgettext_iface('Show Half-Height Value') == '\u663e\u793a\u534a\u9ad8\u6570\u503c')
check('mouse-tip checkbox has the extension Chinese translation',
      bpy.app.translations.pgettext_iface('Ruler at Mouse Tip') == '\u5c3a\u5b50\u5bf9\u9f50\u9f20\u6807\u5c16\u7aef')
bpy.context.preferences.view.language = language

settings.enabled = True
settings.follow_smoothing = 0
settings.units = 'M'
target = scene.objects['Cube']
area = next(a for a in bpy.context.screen.areas if a.type == 'VIEW_3D')
region = next(r for r in area.regions if r.type == 'WINDOW')
area.spaces.active.region_3d.view_perspective = 'PERSP'
with bpy.context.temp_override(area=area, region=region):
    select(target)
    guide, figure = addon.display_layout(bpy.context)
    check('default selection mode displays the measured object without a figure',
          guide is not None and guide['label'] == target.name and figure is None)
    select()
    addon._hover[bpy.context.window.as_pointer()] = (area.as_pointer(), (region.width / 2, region.height / 2))
    check('deselection hides the live ruler even when a mouse position is available',
          addon.display_layout(bpy.context) == (None, None))
    select(target)
    check('reselection restores the live measurement', addon.display_layout(bpy.context)[0]['label'] == target.name)
    bpy.ops.view3d.height_axis_attach()
    select()
    check('selection-only live hiding preserves existing object attachments',
          addon.display_layout(bpy.context) == (None, None) and len(list(addon.attachments.layouts(bpy.context))) == 1)
    settings.only_with_selection = False
    mouse, _ = addon.display_layout(bpy.context)
    check('disabling selection-only restores mouse following without a name',
          mouse is not None and mouse['mode'] == 'REFERENCE' and mouse['label'] == ''
          and addon.ruler_name(bpy.context, mouse) is None)
    rv3d = area.spaces.active.region_3d
    original_cursor = scene.cursor.location.copy()
    original_rotation = rv3d.view_rotation.copy()
    original_scale = scene.unit_settings.scale_length
    rv3d.view_rotation = (Quaternion((0, 0, 1), math.radians(12))
                          @ Quaternion((1, 0, 0), math.radians(90)))
    for projection in ('PERSP', 'ORTHO'):
        rv3d.view_perspective = projection
        positions = []
        pixel_errors = []
        for cursor_z in (-8, 0, 12):
            scene.cursor.location = (1.25, -.75, cursor_z)
            for fraction in (.2, .8):
                addon._hover[bpy.context.window.as_pointer()] = (
                    area.as_pointer(), (region.width * fraction, region.height * fraction))
                mouse, _ = addon.display_layout(bpy.context)
                assert mouse is not None, (projection, cursor_z, fraction)
                base, top = mouse['world_points']
                assert close(base[2], 0) and close(top[2], settings.reference_metres / addon._scene_scale(scene))
                positions.append(Vector(base))
                expected = Vector((region.width * fraction - settings.left_offset * (bpy.context.preferences.system.ui_scale or 1.0),
                                   region.height * fraction))
                pixel_errors.append((Vector(mouse['points'][0]) - expected).length)
        check(f'{projection} mouse rulers start at world zero across mouse and cursor heights', True)
        check(f'{projection} grounded mouse rulers retain horizontal following',
              (positions[0].xy - positions[1].xy).length > .01)
        check(f'{projection} ground bases match the mouse pixel and left gap', max(pixel_errors) < .01)
        check(f'{projection} ground placement is independent of 3D cursor height',
              all((positions[index] - positions[0]).length < 1e-5 for index in (2, 4)))
        original_gap = settings.left_offset
        settings.left_offset = 500
        settings.ruler_at_mouse = True
        tip, _ = addon.display_layout(bpy.context)
        pixel = Vector(addon._hover[bpy.context.window.as_pointer()][1])
        check(f'{projection} mouse-tip placement matches the pointer despite a nonzero gap',
              tip is not None and (Vector(tip['points'][0]) - pixel).length < .01
              and close(tip['world_points'][0][2], 0))
        settings.ruler_at_mouse = False
        settings.left_offset = original_gap
        restored, _ = addon.display_layout(bpy.context)
        expected = pixel - Vector((original_gap * (bpy.context.preferences.system.ui_scale or 1), 0))
        check(f'{projection} disabling mouse-tip placement restores the saved left gap',
              (Vector(restored['points'][0]) - expected).length < .01)
    rv3d.view_perspective = 'PERSP'
    scene.unit_settings.scale_length = .5
    mouse, _ = addon.display_layout(bpy.context)
    check('grounded mouse rulers respect non-metre scene scales',
          mouse is not None and close(mouse['world_points'][0][2], 0)
          and close(mouse['world_points'][1][2] * addon._scene_scale(scene), settings.reference_metres))
    scene.unit_settings.scale_length = original_scale
    settings.follow_smoothing = .02
    addon.placement.clear()
    with patch.object(addon.placement.time, 'monotonic', return_value=10):
        first, _ = addon.display_layout(bpy.context)
    addon._hover[bpy.context.window.as_pointer()] = (area.as_pointer(), (region.width * .3, region.height * .3))
    with patch.object(addon.placement.time, 'monotonic', return_value=10 + 1 / 60):
        moving, _ = addon.display_layout(bpy.context)
    check('mouse follow smoothing stays on the ground while moving horizontally',
          close(moving['world_points'][0][2], 0)
          and (Vector(first['world_points'][0]) - Vector(moving['world_points'][0])).length > .01)
    settings.follow_smoothing = 0
    scene.cursor.location = original_cursor
    rv3d.view_rotation = original_rotation
    addon.placement.clear()
    original_location = target.location.copy()
    original_view_location = rv3d.view_location.copy()
    target.location.z = -8
    bpy.context.view_layer.update()
    rv3d.view_location.z = 0
    check('underground objects alone do not release the zero-height constraint',
          not addon._below_ground_view(bpy.context))
    rv3d.view_location.z = -5
    check('underground geometry and view centre release the zero-height constraint',
          addon._below_ground_view(bpy.context))
    below_positions = []
    for fraction in (.2, .8):
        pixel = Vector((region.width * fraction, region.height * fraction))
        addon._hover[bpy.context.window.as_pointer()] = (area.as_pointer(), tuple(pixel))
        mouse, _ = addon.display_layout(bpy.context)
        depth = addon.view3d_utils.region_2d_to_location_3d(region, rv3d, pixel, rv3d.view_location)
        expected = pixel - Vector((settings.left_offset * (bpy.context.preferences.system.ui_scale or 1.0), 0))
        assert mouse is not None and close(mouse['world_points'][0][2], depth.z)
        assert (Vector(mouse['points'][0]) - expected).length < .01
        below_positions.append(mouse['world_points'][0][2])
    check('released underground rulers follow mouse height while preserving the screen gap',
          abs(below_positions[0] - below_positions[1]) > .01)
    settings.ruler_at_mouse = True
    tip, _ = addon.display_layout(bpy.context)
    check('mouse-tip placement also aligns the released underground ruler',
          (Vector(tip['points'][0]) - pixel).length < .01 and close(tip['world_points'][0][2], depth.z))
    settings.ruler_at_mouse = False
    settings.follow_smoothing = .02
    addon.display_layout(bpy.context)
    rv3d.view_location.z = 0
    mouse, _ = addon.display_layout(bpy.context)
    check('returning to a ground-constrained view restores zero height immediately',
          close(mouse['world_points'][0][2], 0))
    settings.follow_smoothing = 0
    rv3d.view_location.z = -5
    raised = target.copy()
    scene.collection.objects.link(raised)
    raised.location.z = 1
    bpy.context.view_layer.update()
    check('a visible object reaching zero prevents underground release',
          not addon._below_ground_view(bpy.context))
    raised.hide_set(True)
    check('hidden objects do not block underground release', addon._below_ground_view(bpy.context))
    target.hide_set(True)
    check('an empty visible scene does not release the zero-height constraint',
          not addon._below_ground_view(bpy.context))
    target.hide_set(False)
    bpy.data.objects.remove(raised, do_unlink=True)
    target.location = original_location
    rv3d.view_location = original_view_location
    bpy.context.view_layer.update()
    addon.placement.clear()
    settings.reference_name = 'Should not appear under a mouse ruler.blend'
    check('loaded-model names do not become mouse measurement captions',
          addon.display_layout(bpy.context)[0]['label'] == '')
    settings.frozen = True
    frozen_raw = settings.frozen_data
    check('new mouse Freeze snapshots retain their ground-zero starting point',
          close(json.loads(frozen_raw)['points'][0][2], 0))
    settings.ruler_at_mouse = True
    unchanged, _ = addon.display_layout(bpy.context)
    check('mouse-tip toggles do not move an existing frozen placement',
          settings.frozen_data == frozen_raw and unchanged['world_points'] == json.loads(frozen_raw)['points'])
    settings.ruler_at_mouse = False
    settings.only_with_selection = True
    frozen, _ = addon.display_layout(bpy.context)
    check('explicit mouse Freeze remains visible after selection-only is enabled',
          settings.frozen and frozen is not None and settings.frozen_data == frozen_raw)
    legacy_mouse = json.loads(frozen_raw)
    legacy_mouse['label'] = 'Legacy Reference Model'
    settings.frozen_data = json.dumps(legacy_mouse)
    frozen, _ = addon.display_layout(bpy.context)
    check('old mouse Freeze snapshots do not display their retained model names',
          frozen['mode'] == 'REFERENCE' and addon.ruler_name(bpy.context, frozen) is None)
    settings.frozen = False
    check('unfreezing without selection returns to the new hidden state',
          addon.display_layout(bpy.context) == (None, None))
    empty = bpy.data.objects.new('Unmeasurable Helper', None)
    scene.collection.objects.link(empty)
    select(empty)
    check('a selected Empty does not count as measurable geometry', addon.display_layout(bpy.context) == (None, None))
    select(target)

    selected, _ = addon.display_layout(bpy.context)
    settings.ruler_at_mouse = True
    unchanged, _ = addon.display_layout(bpy.context)
    check('mouse-tip placement does not change selected-object measurements',
          unchanged['mode'] == 'SELECTION' and unchanged['world_points'] == selected['world_points'])
    settings.ruler_at_mouse = False

camera_data = bpy.data.cameras.new('Ground Projection Checks')
camera = bpy.data.objects.new('Ground Projection Checks', camera_data)
scene.collection.objects.link(camera)
camera_data.clip_start, camera_data.clip_end = .01, 2000
camera_data.ortho_scale = 16
test_region = SimpleNamespace(width=1600, height=1000)
depsgraph = bpy.context.evaluated_depsgraph_get()


def camera_view(eye, look_at, projection='PERSP', roll=0):
    camera_data.type = projection
    bpy.context.view_layer.update()
    direction = Vector(look_at) - Vector(eye)
    rotation = direction.to_track_quat('-Z', 'Y') @ Quaternion((0, 0, 1), math.radians(roll))
    view = (Matrix.Translation(eye) @ rotation.to_matrix().to_4x4()).inverted()
    perspective = camera.calc_matrix_camera(depsgraph, x=test_region.width, y=test_region.height) @ view
    return SimpleNamespace(perspective_matrix=perspective, view_matrix=view, is_perspective=projection == 'PERSP')


for name, view in (
        ('perspective', camera_view((5, -12, 8), (0, 0, 0))),
        ('rolled perspective', camera_view((5, -12, 8), (0, 0, 0), roll=23)),
        ('orthographic', camera_view((5, -12, 8), (0, 0, 0), 'ORTHO')),
        ('top perspective', camera_view((0, 0, 10), (0, 0, 0)))):
    errors = []
    for x, y in ((.2, .25), (.7, .35), (.55, .4)):
        pixel = Vector((test_region.width * x, test_region.height * y))
        point = addon._mouse_plane_point(test_region, view, pixel)
        assert point is not None and close(point.z, 0), name
        errors.append((addon._project(test_region, view, point) - pixel).length)
    check(f'{name} inverse ground projection reproduces target pixels', max(errors) < .01)
level = camera_view((0, -12, 3), (0, 0, 3))
check('horizon and sky pixels have no forward ground placement',
      addon._mouse_plane_point(test_region, level, (800, 500)) is None
      and addon._mouse_plane_point(test_region, level, (800, 800)) is None)
check('pixels below the horizon retain a visible ground placement',
      addon._mouse_plane_point(test_region, level, (800, 200)) is not None)
edge_on = camera_view((0, -12, 3), (0, 0, 3), 'ORTHO')
check('edge-on orthographic ground projections fail cleanly',
      addon._mouse_plane_point(test_region, edge_on, (800, 200)) is None)
camera_data.clip_end = 5
clipped = camera_view((0, -12, 3), (0, 0, 3))
check('ground intersections beyond the far clip are hidden',
      addon._mouse_plane_point(test_region, clipped, (800, 200)) is None)
bpy.data.objects.remove(camera, do_unlink=True)
bpy.data.cameras.remove(camera_data)

ctx = SimpleNamespace(scene=scene, region=SimpleNamespace(width=1000, height=800))
model = {'span': 3.2, 'scale': 1, 'points': ((400, 80), (400, 680)), 'midpoint': (400, 320),
         'label': target.name, 'mode': 'SELECTION', 'detail_alpha': 1, 'height_text': '3.2 m'}
check('default label presentation retains only the full height',
      [text for _, text in addon.ruler_labels(ctx, model)] == ['3.2 m'])
settings.show_half_height = True
check('half-height toggle restores the physical midpoint value',
      [text for _, text in addon.ruler_labels(ctx, model)] == ['1.6 m', '3.2 m'])
settings.show_half_height = False
for detail in (0, .25, .5, 1):
    labels, name = addon.ruler_readout(ctx, dict(model, detail_alpha=detail))
    assert len(labels) == 1 and labels[0][1:] == ('3.2 m', 1.0) and name[3] == 1
check('half-height hiding keeps one full readout and the object name throughout zoom transitions', True)
mouse_model = dict(model, mode='REFERENCE', label='Legacy Model', points=((400, 0), (400, 2)), midpoint=(400, 1))
check('mouse labels reserve no caption space even with legacy nonempty labels',
      addon.ruler_labels(ctx, mouse_model, compact=True)
      == addon.ruler_labels(ctx, dict(mouse_model, label=''), compact=True))
check('compact mouse presentation omits model names',
      addon.ruler_readout(ctx, dict(mouse_model, detail_alpha=0))[1] is None)

with bpy.context.temp_override(area=area, region=region):
    settings.frozen = True
    raw = settings.frozen_data
    guide = addon.ruler_layout(bpy.context)
    with patch.object(addon.gpu.state, 'blend_get', return_value='NONE'), \
            patch.object(addon.gpu.state, 'blend_set'), \
            patch.object(addon, '_lines') as draw_lines, patch.object(addon, '_text'):
        addon._draw_model(bpy.context, dict(guide, detail_alpha=1), None)
    marks_without_half = draw_lines.call_args_list[1].args[0]
    settings.show_half_height = True
    guide_with_half = addon.ruler_layout(bpy.context)
    with patch.object(addon.gpu.state, 'blend_get', return_value='NONE'), \
            patch.object(addon.gpu.state, 'blend_set'), \
            patch.object(addon, '_lines') as draw_lines, patch.object(addon, '_text'):
        addon._draw_model(bpy.context, dict(guide_with_half, detail_alpha=1), None)
    check('half-height changes leave frozen placement and all three main crossbars unchanged',
          settings.frozen_data == raw and guide['world_points'] == guide_with_half['world_points']
          and len(marks_without_half) == 3 and marks_without_half == draw_lines.call_args_list[1].args[0])
    settings.show_half_height = False
    bpy.ops.view3d.height_axis_attach()
    entry = scene.height_axis_attachments[-1]
    check('new attachments capture the hidden half-height style independently',
          not addon.attachments.style(entry).show_half_height)
    settings.show_half_height = True
    check('changing live half-height does not change the attachment snapshot',
          not addon.attachments.style(entry).show_half_height)
    legacy = json.loads(entry.config)
    del legacy['style']['show_half_height']
    entry.config = json.dumps(legacy)
    old_style = addon.attachments.style(entry)
    check('1.4.0 attachment configs remain valid and retain their historical half-height labels',
          old_style is not None and old_style.show_half_height
          and [text for _, text in addon.ruler_labels(ctx, model, settings=old_style)] == ['1.6 m', '3.2 m'])

settings.only_with_selection = False
settings.show_half_height = True
settings.ruler_at_mouse = True
saved = ROOT / 'verification' / f'selection-defaults-persistence-{bpy.app.version[0]}.{bpy.app.version[1]}.blend'
bpy.ops.wm.save_as_mainfile(filepath=str(saved))
bpy.ops.wm.open_mainfile(filepath=str(saved), load_ui=False)
scene, settings = bpy.context.scene, bpy.context.scene.height_axis
check('both new checkbox overrides survive save and reopen', not settings.only_with_selection and settings.show_half_height)
check('mouse-tip placement survives save and reopen', settings.ruler_at_mouse)
check('saved legacy attachments still decode after reopening',
      len(scene.height_axis_attachments) == 2 and addon.attachments.style(scene.height_axis_attachments[-1]).show_half_height)
fresh = bpy.data.scenes.new('Fresh Defaults')
check('other fresh scenes retain selection-only and no midpoint defaults',
      fresh.height_axis.only_with_selection and not fresh.height_axis.show_half_height
      and not fresh.height_axis.show_reference and close(fresh.height_axis.follow_smoothing, .02))
check('other fresh scenes retain mouse-left placement by default', not fresh.height_axis.ruler_at_mouse)
addon.unregister()

result = {'blender': bpy.app.version_string, 'passed': len(checks), 'checks': checks}
(ROOT / 'verification' / f'selection-defaults-checks-{bpy.app.version[0]}.{bpy.app.version[1]}.json').write_text(
    json.dumps(result, indent=2), encoding='utf-8')
print('SELECTION_DEFAULTS_CHECKS=' + json.dumps(result))
