# SPDX-License-Identifier: GPL-3.0-or-later
"""Scene-selected BLF fonts, loaded once and released with the extension."""

from pathlib import Path

import blf
import bpy

_loaded = {}
_errors = {}


def _path(filepath):
    return str(Path(bpy.path.abspath(filepath)).resolve())


def font_id(filepath, strict=False):
    if not filepath:
        return 0
    path = _path(filepath)
    try:
        source = Path(path)
        if source.suffix.lower() not in {'.ttf', '.otf', '.ttc'}:
            raise ValueError('Choose a TTF, OTF or TTC font file')
        stamp = source.stat().st_mtime_ns
        cached = _loaded.get(path)
        if cached and cached[0] == stamp:
            _errors.pop(path, None)
            return cached[1]
        if cached:
            blf.unload(path)
            _loaded.pop(path, None)
        identifier = blf.load(path)
        if identifier < 0:
            raise ValueError('Unable to load the selected font')
        _loaded[path] = (stamp, identifier)
        _errors.pop(path, None)
        return identifier
    except (OSError, ValueError, RuntimeError) as error:
        _errors[path] = str(error)
        if strict:
            raise ValueError(str(error)) from error
        return 0


def unavailable(filepath):
    return bool(filepath and _path(filepath) in _errors)


def clear():
    for path in tuple(_loaded):
        blf.unload(path)
    _loaded.clear()
    _errors.clear()
