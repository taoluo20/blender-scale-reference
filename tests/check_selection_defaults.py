# SPDX-License-Identifier: GPL-3.0-or-later
"""Selection-only defaults, optional labels and compatible saved references."""

import json
from pathlib import Path
import sys
from types import SimpleNamespace
from unittest.mock import patch

import bpy
from mathutils import Vector

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
    settings.reference_name = 'Should not appear under a mouse ruler.blend'
    check('loaded-model names do not become mouse measurement captions',
          addon.display_layout(bpy.context)[0]['label'] == '')
    settings.frozen = True
    frozen_raw = settings.frozen_data
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
saved = ROOT / 'verification' / f'selection-defaults-persistence-{bpy.app.version[0]}.{bpy.app.version[1]}.blend'
bpy.ops.wm.save_as_mainfile(filepath=str(saved))
bpy.ops.wm.open_mainfile(filepath=str(saved), load_ui=False)
scene, settings = bpy.context.scene, bpy.context.scene.height_axis
check('both new checkbox overrides survive save and reopen', not settings.only_with_selection and settings.show_half_height)
check('saved legacy attachments still decode after reopening',
      len(scene.height_axis_attachments) == 2 and addon.attachments.style(scene.height_axis_attachments[-1]).show_half_height)
fresh = bpy.data.scenes.new('Fresh Defaults')
check('other fresh scenes retain selection-only and no midpoint defaults',
      fresh.height_axis.only_with_selection and not fresh.height_axis.show_half_height
      and not fresh.height_axis.show_reference and close(fresh.height_axis.follow_smoothing, .02))
addon.unregister()

result = {'blender': bpy.app.version_string, 'passed': len(checks), 'checks': checks}
(ROOT / 'verification' / f'selection-defaults-checks-{bpy.app.version[0]}.{bpy.app.version[1]}.json').write_text(
    json.dumps(result, indent=2), encoding='utf-8')
print('SELECTION_DEFAULTS_CHECKS=' + json.dumps(result))
