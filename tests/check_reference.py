"""Actual format round trips, scene preservation, replacement and persistence."""
import hashlib
import json
import pathlib
import sys

import bpy

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
import height_axis as addon

fixtures = ROOT / 'tests' / 'fixtures'
fixtures.mkdir(exist_ok=True)
checks = []


def check(name, condition):
    assert condition, name
    checks.append(name)


addon.register()
original_scene = bpy.context.scene
source_scene = bpy.data.scenes.new('Fixture Source')
bpy.context.window.scene = source_scene
pieces = []


def box(name, location, scale):
    bpy.ops.mesh.primitive_cube_add(size=1, location=location)
    obj = bpy.context.object
    obj.name, obj.scale = name, scale
    pieces.append(obj)


box('Body', (0, 0, 1.2), (0.36, 0.22, 0.58))
box('Hips', (0, 0, 0.83), (0.31, 0.2, 0.2))
box('LegL', (-0.1, 0, 0.4), (0.13, 0.18, 0.8))
box('LegR', (0.1, 0, 0.4), (0.13, 0.18, 0.8))
box('ArmL', (-0.26, 0, 1.11), (0.12, 0.16, 0.68))
box('ArmR', (0.26, 0, 1.11), (0.12, 0.16, 0.68))
bpy.ops.mesh.primitive_uv_sphere_add(segments=16, ring_count=8, radius=0.17, location=(0, 0, 1.65))
bpy.context.object.name = 'Head'
pieces.append(bpy.context.object)
for obj in pieces:
    obj.select_set(True)
bpy.context.view_layer.update()

blend_path = fixtures / 'mannequin.blend'
bpy.data.libraries.write(str(blend_path), set(pieces))
bpy.ops.wm.obj_export(filepath=str(fixtures / 'mannequin.obj'), export_selected_objects=True)
bpy.ops.export_scene.fbx(filepath=str(fixtures / 'mannequin.fbx'), use_selection=True, bake_anim=False)
bpy.ops.export_scene.gltf(filepath=str(fixtures / 'mannequin.glb'), export_format='GLB', use_selection=True)
bpy.ops.export_scene.gltf(filepath=str(fixtures / 'mannequin.gltf'), export_format='GLTF_SEPARATE', use_selection=True)
bpy.ops.wm.stl_export(filepath=str(fixtures / 'mannequin.stl'), export_selected_objects=True)
bpy.context.window.scene = original_scene
bpy.data.scenes.remove(source_scene)
# Retain source datablocks so their original-file hashes and untouched IDs can be checked.
original_objects = set(bpy.data.objects)
original_scenes = set(bpy.data.scenes)
original_selected = tuple(bpy.context.selected_objects)
original_active = bpy.context.view_layer.objects.active
settings = original_scene.height_axis
last_mesh = None
for extension in ('blend', 'obj', 'fbx', 'glb', 'gltf', 'stl'):
    path = fixtures / ('mannequin.' + extension)
    source_hash = hashlib.sha256(path.read_bytes()).hexdigest()
    result = bpy.ops.view3d.height_axis_load_reference(filepath=str(path))
    check(extension + ' operator succeeds', result == {'FINISHED'})
    mesh = settings.reference_mesh
    check(extension + ' normalized height', abs(max(v.co.z for v in mesh.vertices) - 1) < 1e-5
          and abs(min(v.co.z for v in mesh.vertices)) < 1e-5)
    check(extension + ' no extra objects/scenes', set(bpy.data.objects) == original_objects
          and set(bpy.data.scenes) == original_scenes)
    check(extension + ' selection preserved', tuple(bpy.context.selected_objects) == original_selected
          and bpy.context.view_layer.objects.active == original_active)
    check(extension + ' source unchanged', hashlib.sha256(path.read_bytes()).hexdigest() == source_hash)
    check(extension + ' reference is display data only', mesh.users == 1
          and not any(obj.data == mesh for obj in bpy.data.objects if hasattr(obj, 'data')))
    check(extension + ' replacement removes old reference', last_mesh is None
          or last_mesh not in set(bpy.data.meshes))
    check(extension + ' enabled independently of ruler', settings.show_reference and not settings.enabled
          and bool(addon._needs_tracking(settings)))
    last_mesh = mesh

# A posed skin plus an enormous bone widget must bake only the posed character.
rig_scene = bpy.data.scenes.new('Rig Fixture Source')
bpy.context.window.scene = rig_scene
bpy.ops.object.armature_add()
rig = bpy.context.object
rig.pose.bones[0].rotation_mode = 'XYZ'
rig.pose.bones[0].rotation_euler.y = 0.4
bpy.ops.mesh.primitive_cube_add(size=2, location=(0, 0, 1))
skin = bpy.context.object
skin.scale = (0.3, 0.2, 1)
group = skin.vertex_groups.new(name=rig.data.bones[0].name)
group.add(list(range(len(skin.data.vertices))), 1.0, 'REPLACE')
modifier = skin.modifiers.new('Skin', 'ARMATURE')
modifier.object = rig
bpy.ops.mesh.primitive_cube_add(size=50)
widget = bpy.context.object
rig.pose.bones[0].custom_shape = widget
bpy.context.view_layer.update()
evaluated = skin.evaluated_get(bpy.context.evaluated_depsgraph_get())
points = [evaluated.matrix_world @ v.co for v in evaluated.data.vertices]
width = max(p.x for p in points) - min(p.x for p in points)
height = max(p.z for p in points) - min(p.z for p in points)
rig_path = fixtures / 'posed-character.blend'
bpy.data.libraries.write(str(rig_path), {rig, skin, widget})
bpy.context.window.scene = original_scene
bpy.data.scenes.remove(rig_scene)
before_rig_ids = set(bpy.data.objects)
posed = addon.reference.load_reference(bpy.context, str(rig_path))
check('posed character deformation retained', abs(max(v.co.x for v in posed.vertices)
      - min(v.co.x for v in posed.vertices) - width / height) < 1e-5)
check('bone widgets excluded from character', len(posed.vertices) == 8)
check('rig import leaves no extra scene objects', set(bpy.data.objects) == before_rig_ids)

old_mesh = settings.reference_mesh
before_ids = addon.reference._all_ids()
bad = fixtures / 'empty.obj'
bad.write_text('# intentionally empty test mesh\n', encoding='utf-8')
try:
    addon.reference.load_reference(bpy.context, str(bad))
except (ValueError, RuntimeError):
    pass
else:
    raise AssertionError('Empty file must fail')
check('failed load preserves old reference', settings.reference_mesh == old_mesh)
check('failed import cleans all temporary IDs', addon.reference._all_ids() == before_ids)
check('failed import restores scene and selection', bpy.context.scene == original_scene
      and tuple(bpy.context.selected_objects) == original_selected)

reduced = addon.reference.load_reference(bpy.context, str(blend_path), triangle_limit=100)
reduced.calc_loop_triangles()
check('heavy reference display is simplified', len(reduced.loop_triangles) <= 105)
check('simplified reference still normalized', abs(max(v.co.z for v in reduced.vertices) - 1) < 1e-5)

settings.reference_metres = 1.75
settings.reference_yaw = 0.5
settings.reference_opacity = 0.6
saved = ROOT / 'verification' / f'reference-persistence-{bpy.app.version[0]}.{bpy.app.version[1]}.blend'
saved.parent.mkdir(exist_ok=True)
bpy.ops.wm.save_as_mainfile(filepath=str(saved))
bpy.ops.wm.open_mainfile(filepath=str(saved), load_ui=False)
settings = bpy.context.scene.height_axis
check('saved blend retains reference mesh', settings.reference_mesh is not None
      and len(settings.reference_mesh.vertices) > 0)
check('saved blend retains reference controls', settings.show_reference
      and abs(settings.reference_metres - 1.75) < 1e-5 and abs(settings.reference_yaw - 0.5) < 1e-5)
settings.enabled = True
objects_before_clear = set(bpy.data.objects)
result = bpy.ops.view3d.height_axis_clear_reference()
check('remove reference works independently', result == {'FINISHED'}
      and settings.reference_mesh is None and not settings.show_reference and settings.enabled)
check('remove does not delete source scene objects', set(bpy.data.objects) == objects_before_clear)
addon.unregister()
check('unregister removes reference operators', not hasattr(bpy.types, 'VIEW3D_OT_height_axis_load_reference'))

result = {'blender': bpy.app.version_string, 'passed': len(checks), 'checks': checks}
(ROOT / 'verification' / f'reference-checks-{bpy.app.version[0]}.{bpy.app.version[1]}.json').write_text(
    json.dumps(result, ensure_ascii=False, indent=2), encoding='utf-8')
print('REFERENCE_CHECKS=' + json.dumps(result, ensure_ascii=True))
