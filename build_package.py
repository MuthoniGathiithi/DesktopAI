#!/usr/bin/env python3
"""
Build a single-file executable with PyInstaller.

Notes:
- Build on the target OS (i.e., run on Windows to build a Windows .exe, run on Linux to build a Linux binary).
- The entry point is `entry_point.py` which will start the GUI by default and supports --cli for command-line usage.
- The produced binary will contain all Python dependencies included in the repository and installed in the environment used to build.

Usage examples:
    python3 build_package.py --output dist

You need PyInstaller installed in the build environment (requirements.txt includes pyinstaller). If you want cross-platform builds, use CI (GitHub Actions) or run Wine.
"""
import argparse
import shutil
import subprocess
import sys
import os

parser = argparse.ArgumentParser(description='Build DesktopAI single-file binary using PyInstaller')
parser.add_argument('--entry', '-e', default='entry_point.py', help='Entry Python script (default: entry_point.py)')
parser.add_argument('--name', '-n', default='DesktopAI', help='Name for the built binary')
parser.add_argument('--output', '-o', default='dist', help='Output directory for the build')
parser.add_argument('--windowed', action='store_true', help='Use windowed mode on supported platforms (no console window)')
parser.add_argument('--extra', '-x', nargs='*', default=[], help='Extra pyinstaller args (strings)')
args = parser.parse_args()

if not shutil.which('pyinstaller'):
    print('PyInstaller was not found in PATH. Install it in the build environment (pip install pyinstaller).')
    sys.exit(1)

entry = args.entry
name = args.name
out_dir = args.output
windowed = args.windowed
extra_args = args.extra

# Build command
cmd_parts = [
    'pyinstaller',
    '--onefile',
    '--name', name,
    f'--distpath {out_dir}',
]

# Use windowed on Windows by default if requested
if windowed or (os.name == 'nt' and not '--console' in extra_args):
    cmd_parts.append('--windowed')

# Keep a small icon placeholder — user can replace with their .ico later
# cmd_parts.append('--icon=assets/desktopai.ico')

# Hidden imports that sometimes confuse PyInstaller
hidden_imports = ['fuzzywuzzy.process', 'fuzzywuzzy.fuzz']
for hi in hidden_imports:
    cmd_parts.append(f"--hidden-import={hi}")

# Extra CLI args
for a in extra_args:
    cmd_parts.append(a)

# entry script
cmd_parts.append(entry)

cmd = ' '.join(cmd_parts)
print('Running:', cmd)

ret = subprocess.run(cmd, shell=True)
if ret.returncode == 0:
    print('\nBuild finished — result is in:', out_dir)
    print('Note: build the binary on target OS for best compatibility (Windows exe on Windows, Linux binary on Linux).')
else:
    print('\nBuild failed. Check pyinstaller output for errors.')
    sys.exit(ret.returncode)
