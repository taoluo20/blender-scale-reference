# SPDX-License-Identifier: GPL-3.0-or-later
"""Load a display-only, normalized reference without keeping imported scene objects."""

import math
from pathlib import Path

import bpy
import gpu
from gpu_extras.batch import batch_for_shader
from mathutils import Matrix, Vector

TRIANGLE_LIMIT = 150_000
SUPPORTED = {'.blend', '.fbx', '.obj', '.gltf', '.glb', '.stl'}
_batch_key = None
_batch = None
_mesh_shader = None
_image_shader = None
_screen_batch = None
_screen_size = None
_offscreen = None


def _all_ids():
    result = set()
    for prop in bpy.data.bl_rna.properties:
        if prop.type == 'COLLECTION':
            result.update(item for item in getattr(bpy.data, prop.identifier)
                          if isinstance(item, bpy.types.ID))
    return result


def _import_file(filepath, scene):
    extension = Path(filepath).suffix.lower()
    if extension == '.blend':
        with bpy.data.libraries.load(filepath, link=False) as (source, target):
            target.objects = source.objects
        for obj in target.objects:
            if obj is not None:
                scene.collection.objects.link(obj)
    elif extension == '.fbx':
        bpy.ops.import_scene.fbx(filepath=filepath, use_anim=False, use_image_search=False)
    elif extension == '.obj':
        bpy.ops.wm.obj_import(filepath=filepath)
    elif extension in {'.gltf', '.glb'}:
        bpy.ops.import_scene.gltf(filepath=filepath, import_pack_images=False)
    elif extension == '.stl':
        bpy.ops.wm.stl_import(filepath=filepath)


def _flatten(context, up_axis):
    positions, triangles = [], []
    conversion = Vector({'Z': (0, 0, 1), 'Y': (0, 1, 0), 'X': (1, 0, 0)}[up_axis]).rotation_difference(
        Vector((0, 0, 1))).to_matrix().to_4x4()
    depsgraph = context.evaluated_depsgraph_get()
    rig_helpers = {bone.custom_shape for obj in context.scene.objects if obj.type == 'ARMATURE'
                   for bone in obj.pose.bones if bone.custom_shape is not None}
    for instance in depsgraph.object_instances:
        obj = instance.object
        if (obj.type not in {'MESH', 'CURVE', 'SURFACE', 'FONT', 'META'} or obj.hide_viewport
                or obj.hide_render or obj.original in rig_helpers):
            continue
        if not instance.show_self:
            continue
        mesh = obj.to_mesh()
        if mesh is None:
            continue
        try:
            mesh.calc_loop_triangles()
            if not mesh.loop_triangles:
                continue
            start = len(positions)
            matrix = conversion @ instance.matrix_world
            positions.extend(tuple(matrix @ vertex.co) for vertex in mesh.vertices)
            triangles.extend(tuple(start + index for index in triangle.vertices) for triangle in mesh.loop_triangles)
        finally:
            obj.to_mesh_clear()
    if not triangles:
        raise ValueError('The file contains no visible mesh surfaces')
    return positions, triangles


def load_reference(context, filepath, up_axis='Z', triangle_limit=TRIANGLE_LIMIT):
    """Transactional import: the previous reference survives failures."""
    path = Path(bpy.path.abspath(filepath)).resolve()
    if path.suffix.lower() not in SUPPORTED:
        raise ValueError('Choose a Blend, FBX, OBJ, glTF/GLB or STL model')
    if not path.is_file():
        raise ValueError('Model file not found')
    if context.mode != 'OBJECT':
        raise ValueError('Switch to Object Mode before loading a reference figure')
    original_scene, original_layer = context.scene, context.view_layer
    selected = list(context.selected_objects)
    active = original_layer.objects.active
    window = context.window
    old_window_scene = window.scene if window else None
    settings = original_scene.height_axis
    before = _all_ids()
    baked, retained = None, False
    try:
        scene = bpy.data.scenes.new('__HeightAxis_Import__')
        scene.unit_settings.system = 'NONE'
        scene.unit_settings.scale_length = 1
        if window:
            window.scene = scene
        with context.temp_override(scene=scene, view_layer=scene.view_layers[0], collection=scene.collection):
            _import_file(str(path), scene)
            context.view_layer.update()
            positions, triangles = _flatten(context, up_axis)
            provisional = bpy.data.meshes.new('__HeightAxis_Bake__')
            provisional.from_pydata(positions, [], triangles)
            provisional.update()
            if len(triangles) > triangle_limit:
                obj = bpy.data.objects.new('__HeightAxis_Simplify__', provisional)
                scene.collection.objects.link(obj)
                modifier = obj.modifiers.new('Reference display simplification', 'DECIMATE')
                modifier.ratio = triangle_limit / len(triangles)
                context.view_layer.update()
                evaluated = obj.evaluated_get(context.evaluated_depsgraph_get())
                baked = bpy.data.meshes.new_from_object(evaluated)
            else:
                baked = provisional
            low = Vector(tuple(min(v.co[axis] for v in baked.vertices) for axis in range(3)))
            high = Vector(tuple(max(v.co[axis] for v in baked.vertices) for axis in range(3)))
            height = high.z - low.z
            if not math.isfinite(height) or height <= 1e-9:
                raise ValueError('The imported model has zero height; check the imported up axis')
            origin = Vector(((low.x + high.x) / 2, (low.y + high.y) / 2, low.z))
            for vertex in baked.vertices:
                vertex.co = (vertex.co - origin) / height
            baked.name = 'HeightAxis Reference - ' + path.stem
            baked.materials.clear()
            baked.update()
            baked.calc_loop_triangles()
            baked['height_axis_bounds'] = [min(v.co[i] for v in baked.vertices) for i in range(3)] + [
                max(v.co[i] for v in baked.vertices) for i in range(3)]
        # Assign only after the window has returned to the user's scene.
        if window:
            window.scene = old_window_scene
        old_mesh = settings.reference_mesh
        settings.reference_mesh = baked
        settings.reference_name = path.name
        settings.reference_yaw = 0
        settings.show_reference = True
        retained = True
        if old_mesh and old_mesh.users == 0:
            bpy.data.meshes.remove(old_mesh)
        return baked
    finally:
        if window:
            window.scene = old_window_scene
        new_ids = _all_ids() - before
        if retained:
            new_ids.discard(baked)
        if new_ids:
            bpy.data.batch_remove(ids=new_ids)
        for obj in original_layer.objects:
            obj.select_set(obj in selected, view_layer=original_layer)
        original_layer.objects.active = active


def clear_reference(settings):
    mesh = settings.reference_mesh
    settings.show_reference = False
    settings.reference_mesh = None
    settings.reference_name = ''
    if mesh and mesh.users == 0:
        bpy.data.meshes.remove(mesh)
    clear_gpu()


def screen_bounds(context, mesh, matrix, project):
    import itertools
    bounds = mesh.get('height_axis_bounds')
    if bounds is None:
        return None
    points = [project(context.region, context.region_data, matrix @ Vector(corner))
              for corner in itertools.product(*zip(bounds[:3], bounds[3:]))]
    if any(point is None for point in points):
        return None
    return (min(p.x for p in points), min(p.y for p in points),
            max(p.x for p in points), max(p.y for p in points))


def reference_layout(context, guide, project, scene_scale, ignore_freeze=False, ignore_visibility=False):
    settings = context.scene.height_axis
    mesh = settings.reference_mesh
    if (not settings.show_reference and not ignore_visibility) or mesh is None:
        return None
    if settings.frozen and not ignore_freeze:
        from . import freeze
        return freeze.reference_layout(context, project)
    from bpy_extras import view3d_utils
    region, rv3d = context.region, context.region_data
    height = settings.reference_metres / scene_scale
    anchor = Vector(guide['world_anchor'])
    matrix = Matrix.Translation(anchor) @ Matrix.Rotation(settings.reference_yaw, 4, 'Z') @ Matrix.Scale(height, 4)
    def projected_bounds(transform):
        return screen_bounds(context, mesh, transform, project)

    screen = projected_bounds(matrix)
    if screen is None:
        return None
    target_right = guide['attachment_x']
    target_middle = guide['mouse'][1] if guide['mouse'] is not None else None
    # Translate in the camera plane to keep the figure to the left in every view.
    for _ in range(2):
        base = project(region, rv3d, matrix.translation)
        if base is None:
            return None
        dy = target_middle - (screen[1] + screen[3]) / 2 if target_middle is not None else 0
        target = base + Vector((target_right - screen[2], dy))
        position = view3d_utils.region_2d_to_location_3d(region, rv3d, target, matrix.translation)
        matrix.translation = position
        screen = projected_bounds(matrix)
        if screen is None:
            return None
    return {'matrix': matrix, 'bounds': screen, 'height': height, 'mesh': mesh}


def _prepare_batch(mesh):
    global _batch, _batch_key, _mesh_shader
    key = (mesh.as_pointer(), len(mesh.vertices), len(mesh.polygons))
    if _batch_key == key and _batch is not None:
        return
    mesh.calc_loop_triangles()
    positions = [tuple(vertex.co) for vertex in mesh.vertices]
    light = Vector((0.35, -0.7, 0.8)).normalized()
    colors = []
    for vertex in mesh.vertices:
        shade = 0.42 + 0.58 * max(0, vertex.normal.dot(light))
        colors.append((0.42 * shade, 0.76 * shade, 0.96 * shade, 1))
    if _mesh_shader is None:
        _mesh_shader = gpu.shader.from_builtin('SMOOTH_COLOR')
    _batch = batch_for_shader(_mesh_shader, 'TRIS', {'pos': positions, 'color': colors},
                              indices=[tuple(tri.vertices) for tri in mesh.loop_triangles])
    _batch_key = key


def draw_reference(context, model):
    """Own depth buffer: the figure has self-occlusion without touching scene depth."""
    global _offscreen, _screen_size, _screen_batch, _image_shader
    region, rv3d = context.region, context.region_data
    width, height = region.width, region.height
    if width < 2 or height < 2:
        return
    _prepare_batch(model['mesh'])
    factor = min(1, 2048 / max(width, height))
    size = (max(1, round(width * factor)), max(1, round(height * factor)))
    if _offscreen is None or (_offscreen.width, _offscreen.height) != size:
        if _offscreen is not None:
            _offscreen.free()
        _offscreen = gpu.types.GPUOffScreen(*size)
    old_viewport = gpu.state.viewport_get()
    old_blend, old_depth, old_mask = gpu.state.blend_get(), gpu.state.depth_test_get(), gpu.state.depth_mask_get()
    try:
        with _offscreen.bind():
            gpu.state.viewport_set(0, 0, *size)
            gpu.state.active_framebuffer_get().clear(color=(0, 0, 0, 0), depth=1)
            gpu.state.blend_set('NONE')
            gpu.state.depth_test_set('LESS_EQUAL')
            gpu.state.depth_mask_set(True)
            with gpu.matrix.push_pop(), gpu.matrix.push_pop_projection():
                gpu.matrix.load_matrix(rv3d.view_matrix @ model['matrix'])
                gpu.matrix.load_projection_matrix(rv3d.window_matrix)
                _mesh_shader.bind()
                _batch.draw(_mesh_shader)
        gpu.state.viewport_set(*old_viewport)
        gpu.state.blend_set('ALPHA')
        gpu.state.depth_test_set('NONE')
        gpu.state.depth_mask_set(False)
        if _image_shader is None:
            _image_shader = gpu.shader.from_builtin('IMAGE_COLOR')
        if _screen_size != (width, height):
            _screen_batch = batch_for_shader(_image_shader, 'TRI_FAN', {
                'pos': [(0, 0, 0), (width, 0, 0), (width, height, 0), (0, height, 0)],
                'texCoord': [(0, 0), (1, 0), (1, 1), (0, 1)]})
            _screen_size = (width, height)
        _image_shader.bind()
        _image_shader.uniform_sampler('image', _offscreen.texture_color)
        _image_shader.uniform_float('color', (1, 1, 1, context.scene.height_axis.reference_opacity))
        _screen_batch.draw(_image_shader)
    finally:
        gpu.state.viewport_set(*old_viewport)
        gpu.state.blend_set(old_blend)
        gpu.state.depth_test_set(old_depth)
        gpu.state.depth_mask_set(old_mask)


def clear_gpu():
    global _offscreen, _batch, _batch_key, _screen_batch, _screen_size, _mesh_shader, _image_shader
    if _offscreen is not None:
        _offscreen.free()
    _offscreen, _batch, _batch_key, _screen_batch = None, None, None, None
    _screen_size, _mesh_shader, _image_shader = None, None, None
