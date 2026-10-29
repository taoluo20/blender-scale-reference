# SPDX-License-Identifier: GPL-3.0-or-later
"""Repeated viewport failures log once and recover without blocking other guides."""

import json
from pathlib import Path
import sys
from unittest.mock import patch

import bpy

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
import height_axis as addon

checks = []


def check(name, condition):
    assert condition, name
    checks.append(name)


def fail_reference(*args, **kwargs):
    raise RuntimeError('controlled reference draw failure')


def fail_layout(*args, **kwargs):
    raise RuntimeError('controlled layout failure')


addon.register()
settings = bpy.context.scene.height_axis
settings.enabled = False
guide = {'detail_alpha': 1}
figure = {'tag': 'live'}
area = next(item for item in bpy.context.screen.areas if item.type == 'VIEW_3D')
region = next(item for item in area.regions if item.type == 'WINDOW')

with bpy.context.temp_override(area=area, region=region), \
        patch.object(addon.attachments, 'layouts', return_value=[]) as layouts, \
        patch.object(addon, 'display_layout', return_value=(guide, figure)), \
        patch.object(addon.reference, 'draw_reference', side_effect=fail_reference) as draw, \
        patch('builtins.print') as log:
    addon._draw()
    check('first reference failure is logged and retained',
          log.call_count == 1 and 'controlled reference draw failure' in addon._last_error)
    addon._draw()
    check('continuous identical reference failure is logged once', log.call_count == 1)
    draw.side_effect = None
    addon._draw()
    check('successful frame clears the reference error', addon._last_error == '' and log.call_count == 1)
    draw.side_effect = fail_reference
    addon._draw()
    check('a reference failure after recovery is logged again', log.call_count == 2)

    visited = []

    def draw_separately(context, model, opacity):
        visited.append(model['tag'])
        if model['tag'] == 'broken':
            raise RuntimeError('one attachment failed')

    layouts.return_value = [(guide, {'tag': 'broken'}, settings),
                            (guide, {'tag': 'healthy'}, settings)]
    draw.side_effect = draw_separately
    addon._draw()
    check('a broken attachment leaves other attachments and live figure drawing',
          visited == ['broken', 'healthy', 'live'] and 'one attachment failed' in addon._last_error)

    layouts.return_value = []
    layouts.side_effect = fail_layout
    log.reset_mock()
    addon._draw()
    check('outer layout failure is logged and retained',
          log.call_count == 1 and 'controlled layout failure' in addon._last_error)
    addon._draw()
    check('continuous identical layout failure is logged once', log.call_count == 1)
    layouts.side_effect = None
    draw.side_effect = None
    addon._draw()
    check('successful frame clears the layout error', addon._last_error == '' and log.call_count == 1)

addon.unregister()
result = {'blender': bpy.app.version_string, 'passed': len(checks), 'checks': checks}
output = ROOT / 'verification'
output.mkdir(exist_ok=True)
(output / f'draw-errors-checks-{bpy.app.version[0]}.{bpy.app.version[1]}.json').write_text(
    json.dumps(result, indent=2), encoding='utf-8')
print('DRAW_ERROR_CHECKS=' + json.dumps(result))
