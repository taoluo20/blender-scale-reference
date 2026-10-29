# SPDX-License-Identifier: GPL-3.0-or-later
"""Export real viewport screenshots in an isolated GUI Blender process.

Run after tests have generated tests/fixtures/mannequin.blend. Set the three
BLENDER_USER_* directories to a disposable configuration before launching.
The script creates a local study scene, exports four previews, then quits.
"""

import json
import math
import os
from pathlib import Path
import sys

import bpy
from mathutils import Quaternion

ROOT = Path(__file__).resolve().parents[1]
assert all(os.environ.get(key) for key in ('BLENDER_USER_CONFIG', 'BLENDER_USER_SCRIPTS', 'BLENDER_USER_EXTENSIONS'))
sys.path.insert(0, str(ROOT))
import height_axis as addon

OUTPUT = Path(os.environ.get('HEIGHT_AXIS_PREVIEW_OUTPUT', ROOT / 'docs' / 'images'))
OUTPUT.mkdir(parents=True, exist_ok=True)
TEMP = ROOT / 'verification' / 'preview-temporary'
TEMP.mkdir(parents=True, exist_ok=True)
bpy.context.preferences.filepaths.temporary_directory = str(TEMP)
bpy.context.preferences.view.language = 'en_US'
bpy.context.preferences.view.use_translate_interface = True
bpy.context.preferences.view.show_splash = False
bpy.context.preferences.view.show_tooltips = False
addon.VIEW3D_PT_height_axis_appearance.bl_options = set()
addon.register()
scene = bpy.context.scene
scene.unit_settings.system = 'METRIC'
scene.unit_settings.length_unit = 'METERS'

target = bpy.data.objects.get('Cube')
target.name = 'Scale Study'
target.scale = (0.65, 0.5, 1.6)
target.location.z = 1.6
bevel = target.modifiers.new('Soft edges', 'BEVEL')
bevel.width = 0.04
bevel.segments = 3
material = bpy.data.materials.new('Study grey')
material.diffuse_color = (0.52, 0.57, 0.63, 1)
target.data.materials.clear()
target.data.materials.append(material)
for obj in scene.objects:
    obj.select_set(obj == target)
bpy.context.view_layer.objects.active = target
scene.height_axis.enabled = True
scene.height_axis.left_offset = 52
scene.height_axis.font_size = 15
REFERENCE_MODEL = Path(os.environ.get('HEIGHT_AXIS_REFERENCE_MODEL', ROOT / 'tests' / 'fixtures' / 'mannequin.blend'))
bpy.ops.view3d.height_axis_load_reference(filepath=str(REFERENCE_MODEL))
scene.height_axis.show_reference = False

window = bpy.context.window
area = next(area for area in window.screen.areas if area.type == 'VIEW_3D')
space = area.spaces.active
region = next(region for region in area.regions if region.type == 'WINDOW')
ui = next(region for region in area.regions if region.type == 'UI')
evidence = []


def setup():
    space.show_region_ui = '--auto' not in sys.argv
    space.shading.type = 'SOLID'
    space.shading.color_type = 'MATERIAL'
    space.shading.show_cavity = True
    space.overlay.show_floor = True
    space.overlay.show_extras = False
    space.region_3d.view_perspective = 'PERSP'
    space.region_3d.view_rotation = (Quaternion((0, 0, 1), math.radians(12)) @
                                    Quaternion((1, 0, 0), math.radians(90)))
    space.region_3d.view_location = (0, 0, 1.45)
    space.region_3d.view_distance = 7.5
    area.tag_redraw()


def screenshot(name):
    with bpy.context.temp_override(window=window, area=area, region=region):
        guide, figure = addon.display_layout(bpy.context)
        assert guide and not addon._last_error, addon._last_error
        bpy.ops.screen.screenshot_area(filepath=str(OUTPUT / name), hide_props_region=False)
        evidence.append({'file': name, 'state': 'frozen' if scene.height_axis.frozen else guide['mode'].lower(),
                         'world_height': guide['span'], 'reference_height': figure['height'] if figure else None,
                         'only_with_selection': scene.height_axis.only_with_selection,
                         'show_half_height': scene.height_axis.show_half_height,
                         'labels': addon.ruler_labels(bpy.context, guide),
                         'midpoint': list(guide['midpoint']),
                         'line_color': list(scene.height_axis.line_color),
                         'text_color': list(scene.height_axis.text_color),
                         'line_width': scene.height_axis.line_width,
                         'tick_spacing': scene.height_axis.tick_spacing,
                         'perspective': space.region_3d.view_perspective,
                         'custom_font': bool(scene.height_axis.font_path),
                         'draw_error': addon._last_error})


def mouse():
    scene.height_axis.only_with_selection = False
    target.select_set(False)
    bpy.context.view_layer.objects.active = None
    addon._hover[window.as_pointer()] = (area.as_pointer(), (region.width * 0.42, region.height * 0.53))
    area.tag_redraw()


def pin():
    with bpy.context.temp_override(window=window, area=area, region=region):
        scene.height_axis.frozen = True
        assert scene.height_axis.frozen
    space.region_3d.view_rotation = (Quaternion((0, 0, 1), math.radians(32)) @
                                    Quaternion((1, 0, 0), math.radians(90)))
    space.region_3d.view_perspective = 'PERSP'
    area.tag_redraw()


def chinese():
    bpy.context.preferences.view.language = 'zh_HANS'
    bpy.context.preferences.view.use_translate_interface = True
    translated = bpy.app.translations.pgettext_iface('Freeze')
    assert translated == '停止跟随', translated
    assert bpy.app.translations.pgettext_iface('Ruler Appearance') == '尺子外观'
    area.tag_redraw()


def appearance():
    scene.height_axis.line_width = 2.5
    scene.height_axis.line_color = (0.3, 0.85, 0.55, 0.65)
    scene.height_axis.text_color = (1, 0.8, 0.2, 0.8)
    font = os.environ.get('HEIGHT_AXIS_TEST_FONT')
    if font:
        bpy.ops.view3d.height_axis_choose_font(filepath=font)
    area.tag_redraw()


def reset_appearance():
    scene.height_axis.line_width = 1.1
    scene.height_axis.line_color = (1, 1, 1, 0.65)
    scene.height_axis.text_color = (1, 1, 1, 0.75)
    bpy.ops.view3d.height_axis_default_font()
    area.tag_redraw()


def finish():
    (OUTPUT / 'preview-evidence.json' if OUTPUT != ROOT / 'docs' / 'images' else ROOT / 'verification' / 'preview-evidence.json').write_text(
        json.dumps({'blender': bpy.app.version_string, 'screenshots': evidence,
                    'simplified_chinese_translation_verified': True}, indent=2), encoding='utf-8')
    print('HEIGHT_AXIS_PREVIEWS_COMPLETE')
    bpy.ops.wm.quit_blender('EXEC_DEFAULT')


STAGES = [(lambda: screenshot('selected.png'), 0.7),
          (mouse, 1.5), (lambda: screenshot('mouse.png'), 0.7),
          (pin, 1.5), (lambda: screenshot('frozen.png'), 0.7),
          (appearance, 1.0), (lambda: screenshot('appearance.png'), 0.7),
          (reset_appearance, 1.0),
          (chinese, 1.5), (lambda: screenshot('chinese-ui.png'), 0.5), (finish, 0.1)]
if '--chinese-only' in sys.argv:
    STAGES = [(mouse, 0.5), (pin, 1.0), (chinese, 1.0),
              (lambda: screenshot('chinese-ui.png'), 0.5), (finish, 0.1)]


def advance():
    if '--auto' not in sys.argv and (not (ROOT / 'verification' / 'PREVIEW_START').exists()
                                     or ui.active_panel_category != 'Scale'):
        return 0.5
    if not STAGES:
        return None
    action, wait = STAGES.pop(0)
    action()
    return wait


setup()
print('Open the Scale sidebar, then create verification/PREVIEW_START to capture the previews.')
bpy.app.timers.register(advance, first_interval=4.0)
