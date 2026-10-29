# SPDX-License-Identifier: GPL-3.0-or-later
"""Check uncluttered labels, appearance persistence and local font recovery."""

import json
import math
import os
from pathlib import Path
import sys
from types import SimpleNamespace

import bpy
from mathutils import Vector

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
import height_axis as addon

checks = []


def check(name, condition):
    assert condition, name
    checks.append(name)


def close_values(a, b):
    return all(math.isclose(x, y, abs_tol=1e-6) for x, y in zip(a, b))


addon.register()
scene = bpy.context.scene
settings = scene.height_axis
scene.unit_settings.system = 'METRIC'
settings.units = 'M'
check('ruler defaults to translucent white', close_values(settings.line_color, (1, 1, 1, 0.65)))
check('text defaults to translucent white', close_values(settings.text_color, (1, 1, 1, 0.75)))
check('default font needs no external file', not settings.font_path and addon.fonts.font_id('') == 0)

ctx = SimpleNamespace(scene=scene, region=SimpleNamespace(width=1000, height=800))
model = {'span': 3.2, 'scale': 1, 'points': ((400, 80), (400, 680)), 'midpoint': (400, 320)}
labels = addon.ruler_labels(ctx, model)
check('only half and full physical height are labelled', [item[1] for item in labels] == ['1.6 m', '3.2 m'])
check('both labels are to the screen left of their marks', all(item[0][0] < 400 for item in labels))
check('half height follows its projected world point', math.isclose(labels[0][0][1], 320 - 14 * 0.35))
settings.units = 'CM'
check('half and full labels convert together',
      [item[1] for item in addon.ruler_labels(ctx, model)] == ['160 cm', '320 cm'])
settings.units = 'M'
short = dict(model, midpoint=(400, 670))
check('crowded short rulers retain only the full height', len(addon.ruler_labels(ctx, short)) == 1)
offscreen = dict(model, points=((400, 80), (400, 900)))
check('offscreen marks do not produce labels at the viewport edge',
      [item[1] for item in addon.ruler_labels(ctx, offscreen)] == ['1.6 m'])
left = dict(model, points=((-10, 80), (-10, 680)), midpoint=(-10, 320))
check('edge clipping never moves labels across the ruler',
      all(item[0][0] < -10 for item in addon.ruler_labels(ctx, left)))
zero = dict(model, span=0, points=((400, 80), (400, 80)), midpoint=(400, 80))
check('zero height is shown once', [item[1] for item in addon.ruler_labels(ctx, zero)] == ['0 m'])

raw = json.loads((ROOT / 'tests' / 'data' / 'freeze_capture.json').read_text(encoding='utf-8-sig'))['frozen_data']
settings.frozen_data = raw
settings['frozen'] = True
frozen_ctx = SimpleNamespace(scene=scene, region=ctx.region, region_data=None, preferences=bpy.context.preferences)


def project(region, view, point):
    return Vector((400 + point.x * 80, 200 + point.z * 80))


legacy = addon.freeze.ruler_layout(frozen_ctx, project, addon._unit)
data = json.loads(raw)
expected = project(ctx.region, None, (Vector(data['points'][0]) + Vector(data['points'][1])) / 2)
check('older frozen snapshots recover their physical midpoint', close_values(legacy['midpoint'], expected))
data['midpoint'] = [1, 2, 3]
settings.frozen_data = json.dumps(data)
current = addon.freeze.ruler_layout(frozen_ctx, project, addon._unit)
check('new frozen snapshots project the saved midpoint', close_values(current['midpoint'], project(ctx.region, None, Vector((1, 2, 3)))))

settings.line_width = 2.4
settings.line_color = (0.2, 0.8, 0.4, 0.45)
settings.text_color = (0.9, 0.3, 0.1, 0.55)
settings.font_size = 23
settings.tick_spacing = 36
check('appearance remains editable while frozen', math.isclose(settings.line_width, 2.4, abs_tol=1e-6))
font = os.environ.get('HEIGHT_AXIS_TEST_FONT')
if font:
    result = bpy.ops.view3d.height_axis_choose_font(filepath=font)
    check('font picker accepts an actual font file', result == {'FINISHED'} and settings.font_path == font)
    identifier = addon.fonts.font_id(font)
    check('custom font loads and is cached', identifier > 0 and addon.fonts.font_id(font) == identifier)
    try:
        bpy.ops.view3d.height_axis_choose_font(filepath=str(ROOT / 'tests' / 'missing.ttf'))
    except RuntimeError:
        pass
    check('failed font choice preserves the previous font', settings.font_path == font)
    bpy.ops.view3d.height_axis_default_font()
    check('default font button clears the selection', not settings.font_path)
    bpy.ops.view3d.height_axis_choose_font(filepath=font)

missing = str(ROOT / 'tests' / 'missing.ttf')
check('missing font falls back to default', addon.fonts.font_id(missing) == 0)
check('missing font exposes a UI warning', addon.fonts.unavailable(missing))
check('unsupported font format falls back safely', addon.fonts.font_id(str(ROOT / 'README.md')) == 0)
settings.font_path = missing
saved = ROOT / 'verification' / f'appearance-persistence-{bpy.app.version[0]}.{bpy.app.version[1]}.blend'
bpy.ops.wm.save_as_mainfile(filepath=str(saved))
bpy.ops.wm.open_mainfile(filepath=str(saved), load_ui=False)
settings = bpy.context.scene.height_axis
check('line width and font size survive save and reopen',
      math.isclose(settings.line_width, 2.4, abs_tol=1e-6) and settings.font_size == 23)
check('minor tick spacing survives save and reopen while frozen',
      math.isclose(settings.tick_spacing, 36, abs_tol=1e-6) and settings.frozen)
check('independent RGBA colors survive save and reopen',
      close_values(settings.line_color, (0.2, 0.8, 0.4, 0.45)) and close_values(settings.text_color, (0.9, 0.3, 0.1, 0.55)))
check('external font path survives save and reopen', settings.font_path == missing)
check('reopened scene with unavailable font still falls back', addon.fonts.font_id(settings.font_path) == 0)
addon.unregister()
check('font cache and warnings are released on disable', not addon.fonts._loaded and not addon.fonts._errors)

version = f'{bpy.app.version[0]}.{bpy.app.version[1]}'
result = {'blender': bpy.app.version_string, 'passed': len(checks), 'custom_font_tested': bool(font), 'checks': checks}
(ROOT / 'verification' / f'appearance-checks-{version}.json').write_text(json.dumps(result, indent=2), encoding='utf-8')
print('APPEARANCE_CHECKS=' + json.dumps(result))
