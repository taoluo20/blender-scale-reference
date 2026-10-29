#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later
"""Checks that run without Blender: syntax, metadata and reproducible packaging."""

import ast
import hashlib
import importlib.util
import re
from pathlib import Path
import subprocess
import sys
import tomllib
import zipfile
from urllib.parse import unquote

ROOT = Path(__file__).resolve().parents[1]
for path in ROOT.rglob('*.py'):
    if not any(part in {'verification', '.git', 'dist', '__pycache__'} for part in path.parts):
        ast.parse(path.read_text(encoding='utf-8'), filename=str(path))
manifest = tomllib.loads((ROOT / 'height_axis' / 'blender_manifest.toml').read_text(encoding='utf-8'))
assert manifest['id'] == 'height_axis' and manifest['type'] == 'add-on'
documents = [ROOT / 'README.md', ROOT / 'CHANGELOG.md', ROOT / 'RELEASE_NOTES.md', *sorted((ROOT / 'docs').glob('*.md'))]
for document in documents:
    text = document.read_text(encoding='utf-8')
    assert '## 简体中文' in text, f'Bilingual document needs a complete Chinese section: {document.name}'
    english = text.split('## 简体中文', 1)[0]
    english = re.sub(r'\[简体中文\]\([^)]*\)', '', english)
    assert not re.search(r'[\u3400-\u9fff]', english), f'Chinese prose appears before the full English section: {document.name}'
    for target in re.findall(r'\]\(([^)]+)\)', text):
        if target.startswith(('http://', 'https://', '#', 'mailto:')):
            continue
        path = unquote(target.split('#')[0])
        assert (document.parent / path).exists(), f'Broken local documentation link: {document.name}: {path}'
spec = importlib.util.spec_from_file_location('height_axis_core', ROOT / 'height_axis' / 'core.py')
core = importlib.util.module_from_spec(spec)
spec.loader.exec_module(core)
step = core.nice_step(3.2, 400)
values = core.tick_values(3.2, step)
assert 0 < step <= 3.2 and values[0] == 0 and max(values) <= 3.2
assert len(values) <= 12
assert core.nice_step(0, 100) > 0
assert core.format_number(0.000000000001) == '0'
package = ROOT / 'dist' / f"scale-reference-{manifest['version']}.zip"
hashes = []
for _ in range(2):
    subprocess.run([sys.executable, str(ROOT / 'tools' / 'build.py')], check=True)
    hashes.append(hashlib.sha256(package.read_bytes()).hexdigest())
assert hashes[0] == hashes[1], 'Package should be reproducible'
with zipfile.ZipFile(package) as archive:
    assert archive.testzip() is None
    assert 'blender_manifest.toml' in archive.namelist() and '__init__.py' in archive.namelist()
    assert not any('__pycache__' in name or name.startswith('/') or '..' in name.split('/') for name in archive.namelist())
    for name in archive.namelist():
        assert archive.read(name) == (ROOT / 'height_axis' / name).read_bytes()
print('Syntax, metadata, English-first documents, links, ruler arithmetic and reproducible ZIP checks passed.')
