# SPDX-License-Identifier: GPL-3.0-or-later
"""Small, Blender-independent ruler arithmetic."""

import math


def nice_step(span, pixel_span, minimum_pixels=48.0):
    """Choose a readable 1/2/5 interval, with bounded label density."""
    if not math.isfinite(span) or span <= 0:
        return 1.0
    target = span / max(1.0, abs(pixel_span) / minimum_pixels)
    power = 10.0 ** math.floor(math.log10(target))
    fraction = target / power
    for candidate in (1.0, 2.0, 5.0, 10.0):
        if fraction <= candidate:
            return candidate * power
    return 10.0 * power


def tick_values(span, step):
    if span <= 0 or step <= 0:
        return [0.0]
    count = min(200, int(math.floor(span / step + 1e-8)))
    return [index * step for index in range(count + 1)]


def format_number(value):
    if abs(value) < 1e-10:
        return "0"
    return f"{value:.4g}"
