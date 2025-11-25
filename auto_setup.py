#!/usr/bin/env python3
import os
import platform
import subprocess
import shutil
import sys
from pathlib import Path

# Auto setup script
# - creates and/or uses a virtual environment
# - installs python dependencies from requirements.txt
# - optionally installs some system packages on Linux (if user supplies --install-system)

PYPROJECT_DIR = Path(__file__).resolve().parent
REQUIREMENTS_FILE = PYPROJECT_DIR / 'requirements.txt'


def run(cmd, check=True):
    print(f"-> {cmd}")
    return subprocess.run(cmd, shell=True, check=check)


def detect_os():
    return platform.system().lower()


def ensure_python_venv(venv_dir='.venv'):
    venv_path = Path(venv_dir).resolve()
    if not venv_path.exists():
        print(f"Creating virtualenv at {venv_path} ...")
        run(f"{sys.executable} -m venv {venv_path}")
    else:
        print(f"Virtualenv already exists at {venv_path}")
    return venv_path


def pip_install_in_venv(venv_path, requirements_file=REQUIREMENTS_FILE):
    # Use the venv pip
    pip = venv_path / ('Scripts' if os.name == 'nt' else 'bin') / 'pip'
    if not pip.exists():
        print("pip not found inside venv; trying to use system pip")
        pip_cmd = 'pip'
    else:
        pip_cmd = str(pip)

    if not requirements_file.exists():
        print(f"No requirements.txt found at {requirements_file}")
        return False

    print("Installing python packages from requirements.txt (this may take a while)...")
    run(f"{pip_cmd} install -r \"{requirements_file}\"")
    return True


def install_system_packages_linux(non_interactive=False):
    choices = ['scrot', 'network-manager', 'alsa-utils', 'libreoffice', 'gnome-terminal']
    print("The script can optionally install common system packages on Debian/Ubuntu-like systems:")
    print(" -> ", choices)

    if non_interactive:
        accept = True
    else:
        ans = input("Install these system packages now? (requires sudo) [y/N]: ").strip().lower()
        accept = ans == 'y'

    if not accept:
        print("Skipping system package installation. You can run the following commands manually (sudo required):")
        print("sudo apt update && sudo apt install -y scrot network-manager alsa-utils libreoffice gnome-terminal")
        return False

    # Check for apt
    if shutil.which('apt') is None:
        print("apt not found on this system; cannot auto-install system packages. Please install them manually.")
        return False

    cmd = "sudo apt update && sudo apt install -y " + ' '.join(choices)
    run(cmd)
    return True


def windows_instructions():
    print("For Windows, the script will install Python packages with pip.")
    print("System-level dependencies like LibreOffice should be installed via choco/winget if desired.")
    print("Example (PowerShell as admin):")
    print("  winget install LibreOffice.LibreOffice")
    print("  choco install libreoffice -y")


if __name__ == '__main__':
    import argparse
    import shutil

    parser = argparse.ArgumentParser(description='Auto-setup DesktopAI environment (venv + pip + optional system deps)')
    parser.add_argument('--venv', '-v', default='.venv', help='Virtualenv path (default: .venv)')
    parser.add_argument('--no-venv', action='store_true', help='Do not create/use virtualenv; just use system pip')
    parser.add_argument('--install-system', action='store_true', help='Attempt to install system packages (Linux only, requires sudo)')
    parser.add_argument('--non-interactive', action='store_true', help='Run without asking confirmations')

    args = parser.parse_args()

    os_type = detect_os()
    print(f"Detected OS: {os_type}")

    if not args.no_venv:
        venv = ensure_python_venv(args.venv)
        pip_install_in_venv(venv)
    else:
        print("Skipping virtualenv creation, installing into current Python environment")
        run(f"pip install -r \"{REQUIREMENTS_FILE}\"")

    if os_type == 'linux' and args.install_system:
        install_system_packages_linux(non_interactive=args.non_interactive)
    elif os_type == 'windows' and args.install_system:
        print("Automatic system package installation for Windows is not implemented; see help for manual steps.")
        windows_instructions()

    print('\nSetup complete. To run the app (in the venv) use:')
    if args.no_venv:
        print('  python ai_operator.py')
    else:
        print(f'  source {args.venv}/bin/activate && python ai_operator.py')
