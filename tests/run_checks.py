#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later
"""Run Blender integration checks in an isolated configuration."""

import argparse
import json
import os
from pathlib import Path
import subprocess
import tempfile

ROOT = Path(__file__).resolve().parents[1]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--blender', required=True, help='Path to the Blender executable')
    parser.add_argument('--font', help='Optional local TTF, OTF or TTC for custom-font checks')
    args = parser.parse_args()
    output = ROOT / 'verification'
    output.mkdir(exist_ok=True)
    reports = []
    with tempfile.TemporaryDirectory(prefix='height-axis-tests-') as temporary:
        env = os.environ.copy()
        if args.font:
            env['HEIGHT_AXIS_TEST_FONT'] = str(Path(args.font).resolve())
        for key, name in [('BLENDER_USER_CONFIG', 'config'), ('BLENDER_USER_SCRIPTS', 'scripts'),
                          ('BLENDER_USER_EXTENSIONS', 'extensions')]:
            folder = Path(temporary) / name
            folder.mkdir()
            env[key] = str(folder)
        for filename in ('check_blender.py', 'check_reference.py', 'check_freeze.py', 'check_appearance.py', 'check_motion.py'):
            result = subprocess.run([args.blender, '--background', '--factory-startup', '--python-exit-code', '1',
                                     '--python', str(ROOT / 'tests' / filename)], capture_output=True, env=env)
            (output / (Path(filename).stem + '.log')).write_bytes(result.stdout + result.stderr)
            if result.returncode:
                print((result.stdout + result.stderr).decode('utf-8', errors='replace'))
                raise SystemExit(result.returncode)
            print(f'{filename}: passed')
            report = next(line.split('=', 1)[1] for line in result.stdout.decode('utf-8', errors='replace').splitlines()
                          if line.startswith(('HEIGHT_AXIS_CHECKS=', 'REFERENCE_CHECKS=', 'FREEZE_CHECKS=', 'APPEARANCE_CHECKS=', 'MOTION_CHECKS=')))
            reports.append(json.loads(report))
    print(json.dumps([{'blender': item['blender'], 'passed': item['passed']} for item in reports], indent=2))


if __name__ == '__main__':
    main()
