# SPDX-License-Identifier: GPL-3.0-or-later
"""Headless geometry, animation timing and metric-detail transition checks."""

import json
import math
from pathlib import Path
import sys
from types import SimpleNamespace
from unittest.mock import patch

import bpy
from mathutils import Vector

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
import height_axis as addon
from height_axis import core, placement

checks = []


def check(name, condition):
    assert condition, name
    checks.append(name)


def close(a, b, tolerance=1e-5):
    return abs(a - b) < tolerance


def target(anchor=(0, 0, 0), angle=0, identity='object'):
    return placement.target(anchor, (math.cos(angle), math.sin(angle), 0), 3.2,
                            1.4, 0.35, 0.25, 1.8, 0, identity)


addon.register()
settings = bpy.context.scene.height_axis
check('connection lines default off', not settings.show_extensions)
check('zoom-adaptive metric units default on', settings.units == 'AUTO')
check('follow has a nonzero default response', settings.follow_smoothing > 0)
check('separate ruler opacity is available', close(settings.opacity, 1))
check('minor ticks default to a sparser 24 pixel fade threshold', close(settings.tick_spacing, 24))
check('width offset defaults outside the widest extent', settings.object_gap_metres > 0)
language = bpy.context.preferences.view.language
bpy.context.preferences.view.language = 'zh_HANS'
check('placement section uses the extension translation',
      bpy.app.translations.pgettext_iface('Placement & Follow') == '放置与跟随')
check('minor tick spacing has a translated control',
      bpy.app.translations.pgettext_iface('Tick Spacing (px)') == '小刻度间距 (px)')
bpy.context.preferences.view.language = language
settings.object_gap_metres = -0.25
check('width offset permits moving inside the widest extent', settings.object_gap_metres < 0)
settings.object_gap_metres = 0.35

check('distant rulers reduce to a measurement', core.ruler_detail(8) == 0)
check('nearby rulers retain their full detail', core.ruler_detail(120) == 1)
check('near-far transition is continuous and respects UI scale', close(core.ruler_detail(52), 0.5) and close(core.ruler_detail(104, 2), 0.5))
label_ctx = SimpleNamespace(scene=bpy.context.scene, region=SimpleNamespace(width=1000, height=800))
label_model = {'span': 3.2, 'scale': 1, 'points': ((400, 80), (400, 680)),
               'midpoint': (400, 320), 'label': 'Object with a name longer than thirty-two characters'}
settings.units = 'M'
compact_labels = addon.ruler_labels(label_ctx, label_model, compact=True)
check('compact mode contains exactly the full measurement', [label for _, label in compact_labels] == ['3.2 m'])
name = addon.ruler_name(label_ctx, label_model, compact=True)
check('compact name is smaller and below the measurement',
      name[0][1] < compact_labels[0][0][1] and name[2] < settings.font_size and name[1] == label_model['label'])
regular_labels = addon.ruler_labels(label_ctx, label_model)
regular_name = addon.ruler_name(label_ctx, label_model)
check('normal mode also places the object name below full height', regular_name[0][1] < regular_labels[-1][0][1])
bottom = dict(label_model, points=((400, 0), (400, 2)), midpoint=(400, 1))
check('compact label keeps room for its name at the lower edge', addon.ruler_name(label_ctx, bottom, compact=True)[0][1] >= 8)

positions = []
for detail in (0, 0.25, 0.5, 0.75, 1):
    readout = dict(label_model, detail_alpha=detail, height_text='3.2 m')
    labels, name = addon.ruler_readout(label_ctx, readout)
    full = [item for item in labels if item[1] == '3.2 m']
    assert len(full) == 1 and full[0][2] == 1 and name[3] == 1
    assert name[0][1] < full[0][0][1]
    positions.append(full[0][0][1])
check('detail transition draws the full measurement and name exactly once', True)
check('full measurement moves continuously from midpoint to endpoint',
      all(close(b - a, (positions[-1] - positions[0]) / 4, 1e-4) for a, b in zip(positions, positions[1:])))
readout = dict(label_model, detail_alpha=1, height_text='3.2 m', points=((400, 80), (400, 900)))
labels, name = addon.ruler_readout(label_ctx, readout)
check('readout transition does not revive an offscreen full-height label',
      all(text != '3.2 m' or alpha == 0 for _, text, alpha in labels) and name[3] == 0)

distances, lengths = [], []
for index in range(73):
    goal = target(angle=index * math.tau / 72)
    world = placement.geometry(goal)
    base, top = world['points']
    distances.append((base - goal['anchor']).length)
    lengths.append((top - base).length)
    assert close(base.z, 0) and close(top.z, 3.2)
check('orbit keeps a stable physical envelope distance', max(distances) - min(distances) < 1e-5)
check('orbit preserves real vertical length', all(close(length, 3.2) for length in lengths))
near = placement.geometry(target())
far_goal = target()
far_goal['gap'] += 0.75
far = placement.geometry(far_goal)
check('gap control adds its specified physical distance', close((far['points'][0] - near['points'][0]).length, 0.75))
inside_goal = target()
inside_goal['gap'] = -0.35
inside = placement.geometry(inside_goal)
check('negative width offsets move the whole reference inward', close((inside['points'][0] - near['points'][0]).length, 0.7))
inside_goal['gap'], inside_goal['figure_radius'] = -1000, 0
inside = placement.geometry(inside_goal)
check('inward adjustment never flips the ruler to the opposite side', close(inside['points'][0].x, 0))

placement.clear()
first = placement.follow('lag', target(), 0.12, now=0)
step = placement.follow('lag', target((10, 0, 0)), 0.12, now=1 / 60)
travel = step['points'][0].x - first['points'][0].x
check('movement has visible lag without snapping', 0 < travel < 10)
check('optional connectors still reach the actual moving target', close(step['source_points'][0].x, 10))
last_x = step['points'][0].x
for index in range(2, 121):
    result = placement.follow('lag', target((10, 0, 0)), 0.12, now=index / 60)
    assert result['points'][0].x >= last_x - 1e-6
    last_x = result['points'][0].x
expected = placement.geometry(target((10, 0, 0)))['points'][0]
check('follow settles without overshoot', (result['points'][0] - expected).length < 1e-4)


def run_frames(fps):
    placement.clear()
    placement.follow('fps', target(), 0.12, now=0)
    for index in range(1, fps + 1):
        value = placement.follow('fps', target((10, 0, 0), angle=1), 0.12, now=index / fps)
    return value


slow, fast = run_frames(30), run_frames(120)
check('follow timing is independent of frame rate', (slow['points'][0] - fast['points'][0]).length < 1e-4)
placement.clear()
placement.follow('wrap', target(angle=math.pi - 0.05), 0.12, now=0)
wrapped = placement.follow('wrap', target(angle=-math.pi + 0.05), 0.12, now=0.05)
check('orbit takes the short arc across the angle boundary', wrapped['right'].x < -0.99)
snapped = placement.follow('wrap', target((10, 0, 0)), 0, now=0.06)
check('zero response explicitly permits immediate following', (snapped['points'][0] - expected).length < 1e-5)
isolated = placement.follow('other view', target((30, 0, 0)), 0.12, now=0)
check('each viewport owns independent animation state', isolated['points'][0].x > 20)
placement.forget('other view')
check('viewport animation can be discarded independently', 'other view' not in placement._states)

alphas = []
for density in (2401, 4800, 9599):
    ticks = core.metric_ticks(1.8, density, (0.02, 0.08))
    alphas.append(next(alpha for value, alpha, _ in ticks if close(value, 0.03)))
check('new decimal marks fade in continuously', 0 < alphas[0] < alphas[1] < alphas[2] < 1)
dense = core.metric_ticks(3.2, 120, minimum_pixels=6)
sparse = core.metric_ticks(3.2, 120)
check('new default reveals fewer marks than the previous density', len(sparse) < len(dense))
check('spacing control retains exact decimal physical locations',
      all(close(value * 1000, round(value * 1000)) for value, _, _ in dense + sparse))
alphas = [next(alpha for value, alpha, _ in core.metric_ticks(3.2, 500, minimum_pixels=spacing) if close(value, 0.1))
          for spacing in (12, 24, 48)]
check('increasing spacing fades fine marks continuously', 0 < alphas[-1] < alphas[1] < alphas[0] <= 1)
ticks = core.metric_ticks(1000, 100000, (500, 500.012))
check('millimetre detail on long rulers stays bounded', 5 < len(ticks) < 100)
check('metric detail reaches one millimetre', any(close(value, 500.001) for value, _, _ in ticks))
check('detail never invents subdivisions below one millimetre', all(close(value * 1000, round(value * 1000)) for value, _, _ in ticks))
check('coarse and fine levels do not double-draw marks', len({round(value, 9) for value, _, _ in ticks}) == len(ticks))
check('clipping retains a segment crossing the viewport', core.visible_line_fraction((100, -1000), (100, 2000), 800, 600) is not None)
check('clipping rejects a fully offscreen ruler', core.visible_line_fraction((-100, 0), (-100, 800), 800, 600) is None)
for density in (100, 800, 1000, 1600, 8000, 10000, 16000, 100000):
    weights = core.metric_units(density)
    assert close(sum(weight for _, weight in weights), 1) and all(0 <= weight <= 1 for _, weight in weights)
check('unit text crossfades with conserved opacity', True)
check('automatic units span metres through millimetres', core.metric_units(100)[0][1] == 1 and core.metric_units(100000)[2][1] == 1)
placement.clear()
placement.density('zoom', 100, 0.12, now=0)
check('wheel zoom detail is eased over time', 100 < placement.density('zoom', 10000, 0.12, now=1 / 60) < 10000)
placement.clear()
placement.density('near-far', 100, 0.12, now=0)
fades = [core.ruler_detail(placement.density('near-far', 1, 0.12, now=index / 60) * 3.2)
         for index in range(1, 121)]
check('pulling back eases through intermediate ruler visibility', any(0 < value < 1 for value in fades) and fades[-1] == 0)

area = next(area for area in bpy.context.screen.areas if area.type == 'VIEW_3D')
region = next(region for region in area.regions if region.type == 'WINDOW')
settings.enabled = True
settings.follow_smoothing = 0
bpy.context.scene.unit_settings.system = 'METRIC'
settings.units = 'M'
with bpy.context.temp_override(area=area, region=region):
    selected = bpy.context.view_layer.objects.active
    selected.name = label_model['label']
    guide, figure = addon.display_layout(bpy.context)
    check('headless viewport context produces world-space geometry', guide is not None and len(guide['world_points']) == 2)
    check('full object names are retained rather than truncated in the model', guide['label'] == selected.name)
    other = selected.copy()
    bpy.context.scene.collection.objects.link(other)
    other.select_set(True)
    check('combined selection names the active object and additional count', addon.selection_name(bpy.context) == selected.name + ' (+1)')
    bpy.data.objects.remove(other, do_unlink=True)
    with patch.object(placement, 'density', return_value=1):
        far_guide = addon.ruler_layout(bpy.context)
    check('distant layout hides full ruler marks', far_guide['detail_alpha'] == 0 and not far_guide['tick_styles'])
    check('near and far presentation weights conserve opacity', close(far_guide['compact_alpha'] + far_guide['detail_alpha'], 1))
    with patch.object(addon, 'display_layout', return_value=(far_guide, {'test': True})), \
            patch.object(addon.gpu.state, 'blend_get', return_value='NONE'), \
            patch.object(addon.gpu.state, 'blend_set'), \
            patch.object(addon, '_lines') as draw_lines, \
            patch.object(addon, '_text') as draw_text, \
            patch.object(addon.reference, 'draw_reference') as draw_figure:
        addon._draw()
    check('far draw issues no ruler, tick or figure calls', not draw_lines.called and not draw_figure.called and not addon._last_error)
    check('far draw issues only one measurement and one object-name call',
          len(draw_text.call_args_list) == 2 and draw_text.call_args_list[1].args[0] == selected.name)
    settings.units = 'AUTO'
    transition = dict(guide, detail_alpha=0.5, compact_alpha=0.5, metric_units=[('M', 0.5), ('CM', 0.5), ('MM', 0)])
    with patch.object(addon, 'display_layout', return_value=(transition, None)), \
            patch.object(addon.gpu.state, 'blend_get', return_value='NONE'), \
            patch.object(addon.gpu.state, 'blend_set'), \
            patch.object(addon, '_lines'), \
            patch.object(addon, '_text') as draw_text:
        addon._draw()
    texts = [call.args[0] for call in draw_text.call_args_list]
    check('unit and detail transitions never superimpose alternate readings',
          texts == ['1 m', '2 m', selected.name] and not addon._last_error)
    settings.units = 'M'
    for points in (((400, 80), (440, 680)), ((440, 680), (400, 80))):
        marks_model = dict(guide, points=points, midpoint=(420, 380), detail_alpha=1,
                           tick_styles=[((410, 230), 1, 1)], extensions=[])
        with patch.object(addon, 'display_layout', return_value=(marks_model, None)), \
                patch.object(addon.gpu.state, 'blend_get', return_value='NONE'), \
                patch.object(addon.gpu.state, 'blend_set'), \
                patch.object(addon, '_lines') as draw_lines, patch.object(addon, '_text'):
            addon._draw()
        main_marks = draw_lines.call_args_list[1].args[0]
        minor_marks = draw_lines.call_args_list[2].args[0]
        check('all three main marks end at the axis and extend horizontally left ' + str(points[0]),
              len(main_marks) == 3 and all(a.x < b.x and close(a.y, b.y) for a, b in main_marks)
              and {tuple(b) for _, b in main_marks} == {points[0], (420, 380), points[1]})
        check('minor marks stay screen-left even when the ruler projection reverses ' + str(points[0]),
              len(minor_marks) == 1 and all(a.x < b.x and close(a.y, b.y) for a, b in minor_marks)
              and not addon._last_error)
    base, top = (Vector(point) for point in guide['world_points'])
    check('live measurement is a real vertical 3D segment', close(base.x, top.x) and close(base.y, top.y) and close(top.z - base.z, guide['span']))
    projected = [addon._project(region, bpy.context.region_data, point) for point in (base, top)]
    check('each endpoint uses its own perspective projection', all((point - Vector(saved)).length < 1e-5 for point, saved in zip(projected, guide['points'])))
    bpy.context.scene.unit_settings.scale_length = 0.01
    settings.object_gap_metres = 0.5
    scaled = addon.ruler_layout(bpy.context)
    low, high = addon.selection_bounds(bpy.context)
    centre = Vector(((low[0] + high[0]) / 2, (low[1] + high[1]) / 2, low[2]))
    radius = math.hypot(high[0] - low[0], high[1] - low[1]) / 2
    check('object gap remains physical metres in scaled scenes',
          close(((Vector(scaled['world_points'][0]) - centre).length - radius) * 0.01, 0.5))
    bpy.context.scene.unit_settings.scale_length = 1
    settings.object_gap_metres = 0.35
    guide, figure = addon.display_layout(bpy.context)
    raw = addon.freeze.capture(bpy.context, guide, figure)
    snapshot = json.loads(raw)
    check('Freeze captures actual world endpoints without re-lifting',
          all((Vector(a) - Vector(b)).length < 1e-6 for a, b in zip(snapshot['points'], guide['world_points'])))
    check('connection geometry is retained for the optional toggle', len(snapshot['extensions']) == 2)
    check('Freeze retains the full associated object name', snapshot['label'] == selected.name)
    settings.frozen_data = raw
    settings['frozen'] = True
    frozen = addon.ruler_layout(bpy.context)
    check('frozen ruler retains adaptive tick layers', 'tick_styles' in frozen and frozen['world_points'] == snapshot['points'])
    with patch.object(placement, 'density', return_value=200):
        settings.tick_spacing = 6
        dense_frozen = addon.ruler_layout(bpy.context)
        settings.tick_spacing = 48
        sparse_frozen = addon.ruler_layout(bpy.context)
    check('frozen ruler spacing changes the visible minor tick layers',
          len(sparse_frozen['tick_styles']) < len(dense_frozen['tick_styles']))
    check('changing frozen density preserves snapshot and world endpoints',
          settings.frozen_data == raw and dense_frozen['world_points'] == sparse_frozen['world_points'] == snapshot['points'])
    settings.tick_spacing = 24
    with patch.object(placement, 'density', return_value=1):
        far_frozen = addon.ruler_layout(bpy.context)
    check('frozen ruler also supports measurement-only distance mode', far_frozen['detail_alpha'] == 0 and far_frozen['label'] == selected.name)
    settings['frozen'] = False
    bpy.ops.view3d.height_axis_load_reference(filepath=str(ROOT / 'tests' / 'fixtures' / 'mannequin.blend'))
    guide, figure = addon.display_layout(bpy.context)
    check('reference figure shares the same world placement', figure is not None and all(close(a, b) for row_a, row_b in zip(figure['matrix'], guide['figure_matrix']) for a, b in zip(row_a, row_b)))
    for obj in bpy.context.selected_objects:
        obj.select_set(False)
    bpy.context.view_layer.objects.active = None
    addon._hover[bpy.context.window.as_pointer()] = (area.as_pointer(), (region.width / 2, region.height / 2))
    mouse, figure = addon.display_layout(bpy.context)
    check('mouse following also produces a 3D ruler and figure', mouse is not None and mouse['mode'] == 'REFERENCE' and figure is not None)
    a, b = (Vector(point) for point in mouse['world_points'])
    check('mouse ruler retains its physical reference height', close((b - a).length, settings.reference_metres / addon._scene_scale(bpy.context.scene)))

settings.object_gap_metres = -0.875
settings.follow_smoothing = 0.23
settings.opacity = 0.4
settings.show_extensions = True
saved = ROOT / 'verification' / f'motion-persistence-{bpy.app.version[0]}.{bpy.app.version[1]}.blend'
bpy.ops.wm.save_as_mainfile(filepath=str(saved))
bpy.ops.wm.open_mainfile(filepath=str(saved), load_ui=False)
settings = bpy.context.scene.height_axis
check('new motion and opacity controls survive save and reopen', close(settings.object_gap_metres, -0.875) and close(settings.follow_smoothing, 0.23) and close(settings.opacity, 0.4) and settings.show_extensions)
check('loading a file clears transient animation state', not placement._states and not placement._densities)
addon.unregister()
check('disable releases animation caches', not placement._states and not placement._densities)

result = {'blender': bpy.app.version_string, 'passed': len(checks), 'checks': checks}
path = ROOT / 'verification' / f'motion-checks-{bpy.app.version[0]}.{bpy.app.version[1]}.json'
path.write_text(json.dumps(result, indent=2), encoding='utf-8')
print('MOTION_CHECKS=' + json.dumps(result))
