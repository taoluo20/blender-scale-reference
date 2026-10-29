# SPDX-License-Identifier: GPL-3.0-or-later
"""Persistent world-space snapshots of a displayed ruler and reference figure."""

import json
from functools import lru_cache

from bpy_extras import view3d_utils
from mathutils import Matrix, Vector

from .core import format_number


@lru_cache(maxsize=16)
def read_snapshot(raw):
    if not raw:
        return None
    data = json.loads(raw)
    return data if data.get('version') == 1 else None


def capture(context, guide, figure):
    """Lift the actual displayed line/ticks into their respective depth planes."""
    region, rv3d = context.region, context.region_data
    anchor, span = Vector(guide['world_anchor']), guide['span']

    def lift(point, value):
        depth = anchor + Vector((0, 0, value))
        return tuple(view3d_utils.region_2d_to_location_3d(region, rv3d, point, depth))

    points = guide.get('points', ((guide['x'], guide['y0']), (guide['x'], guide['y1'])))
    ticks = guide.get('tick_points', [((guide['x'], y), label) for y, label in guide['ticks']])
    world_points = guide.get('world_points')
    data = {'version': 1, 'span': span, 'label': guide['label'], 'source_mode': guide['mode'],
            'anchor': tuple(anchor), 'diagram': guide['collapsed'],
            'points': world_points if world_points is not None else [lift(points[0], 0), lift(points[1], span)],
            'midpoint': guide.get('world_midpoint') or lift(guide.get('midpoint', (Vector(points[0]) + Vector(points[1])) / 2), span / 2),
            'ticks': guide.get('tick_world') if world_points is not None else [
                [value, lift(point, value)] for value, (point, _) in zip(guide['tick_values'], ticks)],
            'extensions': guide.get('extension_world', []),
            'figure_matrix': [list(row) for row in figure['matrix']] if figure else None,
            'figure_height': figure['height'] if figure else None}
    return json.dumps(data, separators=(',', ':'), ensure_ascii=False)


def ruler_layout(context, project, unit):
    settings = context.scene.height_axis
    data = read_snapshot(settings.frozen_data)
    if data is None:
        return None
    points = [project(context.region, context.region_data, Vector(point)) for point in data['points']]
    if any(point is None for point in points):
        return None
    middle_world = data.get('midpoint', (Vector(data['points'][0]) + Vector(data['points'][1])) / 2)
    middle = project(context.region, context.region_data, Vector(middle_world))
    if middle is None:
        middle = (points[0] + points[1]) / 2
    extensions = [project(context.region, context.region_data, Vector(point)) for point in data.get('extensions', [])]
    factor, suffix = unit(context.scene, settings, data['span'])
    ticks, tick_points, values = [], [], []
    for value, world in data['ticks']:
        point = project(context.region, context.region_data, Vector(world))
        if point is None:
            continue
        label = f'{format_number(value * factor)} {suffix}'
        ticks.append((point.y, label))
        tick_points.append((tuple(point), label))
        values.append(value)
    return {'x': points[0].x, 'y0': points[0].y, 'y1': points[1].y,
            'span': data['span'], 'height_text': f"{format_number(data['span'] * factor)} {suffix}",
            'label': data['label'], 'mode': data['source_mode'], 'ticks': ticks,
            'tick_points': tick_points, 'tick_values': values, 'points': [tuple(point) for point in points],
            'midpoint': tuple(middle),
            'collapsed': data['diagram'], 'scale': context.preferences.system.ui_scale or 1.0,
            'world_anchor': data['anchor'], 'attachment_x': points[0].x, 'mouse': None,
            'extensions': [tuple(point) for point in extensions] if all(point is not None for point in extensions) else [],
            'frozen': True, 'world_points': data['points']}


def reference_layout(context, project):
    from . import reference
    settings = context.scene.height_axis
    data = read_snapshot(settings.frozen_data)
    if not data or not data['figure_matrix'] or settings.reference_mesh is None:
        return None
    matrix = Matrix(data['figure_matrix'])
    screen = reference.screen_bounds(context, settings.reference_mesh, matrix, project)
    if screen is None:
        return None
    return {'matrix': matrix, 'bounds': screen, 'height': data['figure_height'],
            'mesh': settings.reference_mesh, 'frozen': True}
