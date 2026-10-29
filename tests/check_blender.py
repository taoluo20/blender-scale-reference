"""Run with Blender --background --factory-startup --python this_file."""
import json
import math
import pathlib
import sys

import bpy
from mathutils import Vector

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
import height_axis as addon

checks = []


def check(name, condition):
    assert condition, name
    checks.append(name)


def close(a, b):
    return math.isclose(a, b, abs_tol=1e-5, rel_tol=1e-5)


def select(*objects):
    for obj in bpy.context.view_layer.objects:
        obj.select_set(False)
    for obj in objects:
        obj.select_set(True)
    bpy.context.view_layer.objects.active = objects[0] if objects else None
    bpy.context.view_layer.update()


addon.register()
original_keymaps = tuple(bpy.context.window_manager.keyconfigs.addon.keymaps.keys())
scene = bpy.context.scene
settings = scene.height_axis
check('disabled by default', not settings.enabled)
settings.enabled = True

mesh = bpy.data.meshes.new('TestTetraMesh')
mesh.from_pydata([(0, 0, 0), (2, 0, 0), (0, 2, 0), (0, 0, 4)], [],
                 [(0, 1, 2), (0, 1, 3), (0, 2, 3), (1, 2, 3)])
tetra = bpy.data.objects.new('TestTetra', mesh)
scene.collection.objects.link(tetra)
tetra.rotation_euler = (math.radians(39), math.radians(21), 0.2)
tetra.scale = (1.2, 0.7, -1.6)
tetra.location = (2, 3, -4)
select(tetra)
expected = [tetra.matrix_world @ vertex.co for vertex in tetra.data.vertices]
bounds = addon.selection_bounds(bpy.context)
check('rotated mesh exact Z, negative and unapplied scale',
      close(bounds[0][2], min(p.z for p in expected))
      and close(bounds[1][2], max(p.z for p in expected)))

bpy.ops.mesh.primitive_cube_add(size=2, location=(0, 0, 0))
cube = bpy.context.object
array = cube.modifiers.new('VerticalArray', 'ARRAY')
array.count = 3
array.relative_offset_displace = (0, 0, 1)
select(cube)
bounds = addon.selection_bounds(bpy.context)
check('evaluated modifier height', close(bounds[1][2] - bounds[0][2], 6))
cube.scale.z = 2
bpy.context.view_layer.update()
bounds = addon.selection_bounds(bpy.context)
check('bounds refresh after live scaling', close(bounds[1][2] - bounds[0][2], 12))

select(cube, tetra)
bounds = addon.selection_bounds(bpy.context)
all_z = [p.z for p in expected] + [-2, 10]
check('multiple selection union', close(bounds[0][2], min(all_z))
      and close(bounds[1][2], max(all_z)))

cube.modifiers.clear()
cube.scale = (1, 1, 1)
select(cube)
bpy.ops.object.mode_set(mode='EDIT')
import bmesh
bm = bmesh.from_edit_mesh(cube.data)
for vert in bm.verts:
    if vert.co.z > 0:
        vert.co.z = 4
bmesh.update_edit_mesh(cube.data)
bpy.context.view_layer.update()
bounds = addon.selection_bounds(bpy.context)
check('live edit mesh bounds', close(bounds[1][2] - bounds[0][2], 5))
bpy.ops.object.mode_set(mode='OBJECT')

scene.unit_settings.system = 'METRIC'
scene.unit_settings.scale_length = 0.01
scene.unit_settings.length_unit = 'CENTIMETERS'
settings.units = 'SCENE'
factor, suffix = addon._unit(scene, settings, 180)
check('centimetre scene display', close(180 * factor, 180) and suffix == 'cm')
check('reference height stays 1.8 physical metres',
      close(settings.reference_metres / addon._scene_scale(scene), 180))
settings.units = 'M'
factor, suffix = addon._unit(scene, settings, 180)
check('explicit metres in centimetre scene', close(180 * factor, 1.8) and suffix == 'm')
settings.units = 'SCENE'
scene.unit_settings.system = 'IMPERIAL'
factor, suffix = addon._unit(scene, settings, 30.48)
check('imperial unit conversion', close(30.48 * factor, 1) and suffix == 'ft')

select()
check('no stale active object after deselection', addon.selection_bounds(bpy.context) is None)
camera = next(obj for obj in scene.objects if obj.type == 'CAMERA')
select(camera)
check('camera is not measured as geometry', addon.selection_bounds(bpy.context) is None)
check('no shortcuts added', original_keymaps == tuple(bpy.context.window_manager.keyconfigs.addon.keymaps.keys()))

for cycle in range(3):
    addon.unregister()
    check(f'cleanup properties cycle {cycle}', not hasattr(bpy.types.Scene, 'height_axis'))
    check(f'cleanup handlers cycle {cycle}', addon._depsgraph_changed not in bpy.app.handlers.depsgraph_update_post)
    check(f'cleanup modal state cycle {cycle}', not addon._sessions)
    if cycle < 2:
        addon.register()

result = {'blender': bpy.app.version_string, 'passed': len(checks), 'checks': checks}
(ROOT / 'verification').mkdir(exist_ok=True)
(ROOT / 'verification' / f'checks-{bpy.app.version[0]}.{bpy.app.version[1]}.json').write_text(
    json.dumps(result, ensure_ascii=False, indent=2), encoding='utf-8')
print('HEIGHT_AXIS_CHECKS=' + json.dumps(result, ensure_ascii=True))
