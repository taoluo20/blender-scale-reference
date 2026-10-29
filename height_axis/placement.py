# SPDX-License-Identifier: GPL-3.0-or-later
"""Stable world-space placement and frame-rate independent follow animation."""

import math
import time

from mathutils import Matrix, Vector

from .core import smooth_factor

_states = {}
_densities = {}


def target(anchor, right, span, radius, gap, figure_radius, figure_height, yaw, identity):
    direction = Vector((right[0], right[1], 0))
    if direction.length < 1e-8:
        direction = Vector((1, 0, 0))
    direction.normalize()
    return {'anchor': Vector(anchor), 'angle': math.atan2(direction.y, direction.x),
            'span': span, 'radius': radius, 'gap': gap, 'figure_radius': figure_radius,
            'figure_height': figure_height, 'yaw': yaw, 'identity': identity}


def follow(key, goal, response, now=None):
    now = time.monotonic() if now is None else now
    previous = _states.get(key)
    if previous is None or previous['identity'] != goal['identity']:
        state = dict(goal, anchor=goal['anchor'].copy(), source_anchor=goal['anchor'].copy(), time=now, moving=False)
    else:
        factor = smooth_factor(now - previous['time'], response)
        state = dict(goal, source_anchor=goal['anchor'].copy(), time=now)
        state['anchor'] = previous['anchor'].lerp(goal['anchor'], factor)
        delta = (goal['angle'] - previous['angle'] + math.pi) % math.tau - math.pi
        state['angle'] = previous['angle'] + delta * factor
        for name in ('radius', 'gap', 'figure_radius'):
            state[name] = previous[name] + (goal[name] - previous[name]) * factor
        state['moving'] = ((state['anchor'] - goal['anchor']).length > 1e-6
                           or abs(delta * (1 - factor)) > 1e-5
                           or any(abs(state[name] - goal[name]) > 1e-6
                                  for name in ('radius', 'gap', 'figure_radius')))
    _states[key] = state
    return geometry(state)


def geometry(state):
    right = Vector((math.cos(state['angle']), math.sin(state['angle']), 0))
    anchor = state['anchor']
    outer = max(0.0, state['radius'] + state['gap'])
    figure_radius = state['figure_radius']
    figure_base = anchor - right * (outer + figure_radius)
    # Reserve a physical gap between the figure and ruler, independent of projection.
    ruler_base = (figure_base - right * (figure_radius + 0.08 * state['figure_height'])
                  if figure_radius > 0 else anchor - right * outer)
    top = ruler_base + Vector((0, 0, state['span']))
    matrix = (Matrix.Translation(figure_base) @ Matrix.Rotation(state['yaw'], 4, 'Z')
              @ Matrix.Scale(state['figure_height'], 4))
    source = state.get('source_anchor', anchor)
    return {'points': (ruler_base, top), 'midpoint': (ruler_base + top) / 2,
            'right': right, 'figure_matrix': matrix,
            'source_points': (source.copy(), source + Vector((0, 0, state['span'])))}


def density(key, goal, response, now=None):
    now = time.monotonic() if now is None else now
    value = math.log(max(goal, 1e-12))
    previous = _densities.get(key)
    if previous:
        factor = smooth_factor(now - previous['time'], max(0.08, response))
        value = previous['value'] + (value - previous['value']) * factor
    _densities[key] = {'value': value, 'time': now, 'moving': abs(value - math.log(max(goal, 1e-12))) > 1e-5}
    return math.exp(value)


def animating():
    return any(state['moving'] for state in (*_states.values(), *_densities.values()))


def forget(key):
    _states.pop(key, None)
    _densities.pop(key, None)


def clear():
    _states.clear()
    _densities.clear()


def retain(keys):
    for key in set(_states) | set(_densities):
        if key not in keys:
            forget(key)
