#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later
"""Build a reproducible extension ZIP, optionally validating it with Blender."""

import argparse
import hashlib
import os
from pathlib import Path
import subprocess
import tempfile
import tomllib
import zipfile

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / 'height_axis'


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--blender', help='Blender executable for extension validation')
    args = parser.parse_args()
    manifest = tomllib.loads((SOURCE / 'blender_manifest.toml').read_text(encoding='utf-8'))
    target = ROOT / 'dist' / f"height-axis-{manifest['version']}.zip"
    target.parent.mkdir(exist_ok=True)
    with zipfile.ZipFile(target, 'w', compression=zipfile.ZIP_DEFLATED, compresslevel=9) as archive:
        for path in sorted(SOURCE.rglob('*')):
            if not path.is_file() or '__pycache__' in path.parts or path.suffix in {'.pyc', '.zip'}:
                continue
            entry = zipfile.ZipInfo(path.relative_to(SOURCE).as_posix(), (1980, 1, 1, 0, 0, 0))
            entry.compress_type = zipfile.ZIP_DEFLATED
            entry.external_attr = 0o100644 << 16
            archive.writestr(entry, path.read_bytes(), compress_type=zipfile.ZIP_DEFLATED, compresslevel=9)
    digest = hashlib.sha256(target.read_bytes()).hexdigest()
    (target.parent / 'SHA256SUMS.txt').write_text(f'{digest}  {target.name}\n', encoding='utf-8')
    if args.blender:
        with tempfile.TemporaryDirectory(prefix='height-axis-build-') as temporary:
            env = os.environ.copy()
            for key, folder in [('BLENDER_USER_CONFIG', 'config'), ('BLENDER_USER_SCRIPTS', 'scripts'),
                                ('BLENDER_USER_EXTENSIONS', 'extensions')]:
                directory = Path(temporary) / folder
                directory.mkdir()
                env[key] = str(directory)
            subprocess.run([args.blender, '--background', '--factory-startup', '--command', 'extension',
                            'validate', str(target)], check=True, env=env)
    print(f'Built {target.name} ({target.stat().st_size:,} bytes)\nSHA256 {digest}')
    return target


if __name__ == '__main__':
    main()
