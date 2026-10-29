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


def smooth_factor(seconds, response):
    if response <= 0:
        return 1.0
    return -math.expm1(-max(0.0, seconds) / response)


def smoothstep(value):
    value = min(1.0, max(0.0, value))
    return value * value * (3 - 2 * value)


def ruler_detail(pixel_span, ui_scale=1.0):
    """Far views retain one readable measurement; nearby views reveal the ruler."""
    return smoothstep((pixel_span / max(ui_scale or 1.0, 1e-6) - 32) / 40)


def metric_units(pixels_per_metre):
    """Crossfade unit text as centimetres and millimetres become readable."""
    density = max(pixels_per_metre, 1e-12)
    centimetres = smoothstep(math.log2(density * 0.01 / 8))
    millimetres = smoothstep(math.log2(density * 0.001 / 8))
    return [('M', 1 - centimetres), ('CM', centimetres * (1 - millimetres)), ('MM', millimetres)]


def metric_ticks(span, pixels_per_metre, visible=None, minimum_pixels=24.0):
    """World-anchored decimal levels, fading in above the chosen screen spacing."""
    if span <= 0 or not math.isfinite(span) or pixels_per_metre <= 0:
        return []
    low, high = visible if visible is not None else (0.0, span)
    low, high = max(0.0, low), min(span, high)
    if low > high:
        return []
    power = max(0, math.floor(math.log10(span)))
    ticks = []
    for exponent in range(power, -4, -1):
        step = 10.0 ** exponent
        alpha = smoothstep(math.log2(max(pixels_per_metre * step / max(minimum_pixels, 1e-6), 1e-12)) / 2)
        if alpha <= 0:
            continue
        first = max(0, math.ceil(low / step - 1e-8))
        last = math.floor(high / step + 1e-8)
        # Clip before generating: even a kilometre ruler must stay bounded at mm zoom.
        if last - first > 400:
            continue
        for index in range(first, last + 1):
            if exponent != power and index % 10 == 0:
                continue
            ticks.append((index * step, alpha, 0.45 + 0.55 * alpha))
    return ticks


def visible_line_fraction(a, b, width, height, padding=16):
    """Liang-Barsky clipping in screen space, retaining segment parameters."""
    start, end = 0.0, 1.0
    dx, dy = b[0] - a[0], b[1] - a[1]
    for direction, distance in ((-dx, a[0] + padding), (dx, width + padding - a[0]),
                                (-dy, a[1] + padding), (dy, height + padding - a[1])):
        if abs(direction) < 1e-12:
            if distance < 0:
                return None
            continue
        ratio = distance / direction
        if direction < 0:
            start = max(start, ratio)
        else:
            end = min(end, ratio)
        if start > end:
            return None
    return start, end
