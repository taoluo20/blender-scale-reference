"""Replay the real UI snapshot to check geometry, independent views and persistence."""
import json
import pathlib
import sys
from types import SimpleNamespace

import bpy
from mathutils import Matrix, Vector

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
import height_axis as addon

checks = []


def check(name, condition):
    assert condition, name
    checks.append(name)


def close_matrix(a, b):
    return all(abs(x - y) < 1e-6 for ra, rb in zip(a, b) for x, y in zip(ra, rb))


addon.register()
scene = bpy.context.scene
settings = scene.height_axis
check('freeze defaults off', not settings.frozen)
check('freeze without a displayed location is rejected', not settings.frozen_data)
settings.frozen = True
check('invalid freeze resets checkbox with explanation', not settings.frozen and bool(settings.freeze_message))
bpy.ops.view3d.height_axis_load_reference(filepath=str(ROOT / 'tests' / 'fixtures' / 'mannequin.blend'))
settings.enabled = True

ui = json.loads((ROOT / 'tests' / 'data' / 'freeze_capture.json').read_text(encoding='utf-8-sig'))
raw = ui['frozen_data']
settings.frozen_data = raw
# Stored RNA values are restored without update callbacks when Blender reads a blend file.
settings['frozen'] = True
check('frozen stops mouse tracking but keeps display enabled',
      bool(addon._needs_display(settings)) and not addon._needs_tracking(settings))


def project(region, view, point):
    p = view.rotation @ point
    return Vector((region.width / 2 + p.x * 80, region.height / 2 + p.z * 80 + p.y * 20))


ctx = SimpleNamespace(scene=scene, preferences=bpy.context.preferences,
                      region=SimpleNamespace(width=1000, height=800),
                      region_data=SimpleNamespace(rotation=Matrix.Identity(3)))
guide_a = addon.freeze.ruler_layout(ctx, project, addon._unit)
figure_a = addon.freeze.reference_layout(ctx, project)
data = addon.freeze.read_snapshot(raw)
check('captured ruler uses original world points', guide_a['world_points'] == data['points'])
check('captured figure keeps original world matrix', close_matrix(figure_a['matrix'], data['figure_matrix']))

cube = bpy.data.objects.get('Cube')
cube.location = (10, -5, 4)
cube.scale.z = 4
for obj in bpy.context.selected_objects:
    obj.select_set(False)
bpy.context.view_layer.update()
ctx.region_data.rotation = Matrix.Rotation(0.8, 3, 'Z')
guide_b = addon.freeze.ruler_layout(ctx, project, addon._unit)
figure_b = addon.freeze.reference_layout(ctx, project)
check('object movement and deselection do not change snapshot', settings.frozen_data == raw)
check('different view changes projection of fixed ruler',
      (Vector(guide_a['points'][0]) - Vector(guide_b['points'][0])).length > 1)
check('different view retains frozen ruler geometry and height',
      guide_b['world_points'] == guide_a['world_points'] and guide_b['span'] == guide_a['span'])
check('different view retains figure position and orientation', close_matrix(figure_a['matrix'], figure_b['matrix']))
check('different view projects the same figure differently', figure_a['bounds'] != figure_b['bounds'])
settings.reference_metres = 3.1
settings.reference_yaw = 0.9
check('frozen figure size and orientation remain captured',
      close_matrix(addon.freeze.reference_layout(ctx, project)['matrix'], figure_a['matrix']))

saved = ROOT / 'verification' / f'freeze-persistence-{bpy.app.version[0]}.{bpy.app.version[1]}.blend'
bpy.ops.wm.save_as_mainfile(filepath=str(saved))
bpy.ops.wm.open_mainfile(filepath=str(saved), load_ui=False)
settings = bpy.context.scene.height_axis
check('save and reopen retains freeze checkbox and world snapshot', settings.frozen and settings.frozen_data == raw)
check('save and reopen retains reference model', settings.reference_mesh is not None)
settings.frozen = False
check('unfreeze clears placement and resumes tracking', not settings.frozen_data
      and bool(addon._needs_tracking(settings)))
addon.unregister()
check('unregister clears cached live placements', not addon._last_live)

result = {'blender': bpy.app.version_string, 'passed': len(checks), 'checks': checks}
(ROOT / 'verification' / f'freeze-checks-{bpy.app.version[0]}.{bpy.app.version[1]}.json').write_text(
    json.dumps(result, ensure_ascii=False, indent=2), encoding='utf-8')
print('FREEZE_CHECKS=' + json.dumps(result, ensure_ascii=True))
