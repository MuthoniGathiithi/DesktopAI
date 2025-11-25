import os
import platform
from typing import List


def _get_roots() -> List[str]:
    """Return a list of reasonable filesystem roots to search depending on the OS."""
    system = platform.system().lower()
    if system == "windows":
        # Walk common drives on Windows (C:\, D:\, etc.). We will detect present drives.
        drives = []
        for letter in "ABCDEFGHIJKLMNOPQRSTUVWXYZ":
            drive = f"{letter}:\\"
            if os.path.exists(drive):
                drives.append(drive)
        return drives or ["C:\\"]
    else:
        # Unix-like: start at root (/) and also user's home as safe start
        roots = [os.path.expanduser("~"), "/"]
        # Ensure unique and existing
        return [r for r in dict.fromkeys(roots) if os.path.exists(r)]


def find_files_by_name(name: str, root_paths: List[str] = None, max_results: int = 500, case_sensitive: bool = False) -> List[str]:
    """Search the filesystem for files or directories that contain `name` in their basename.

    - name: a filename or substring to match (e.g., 'obed' or 'report.pdf')
    - root_paths: list of starting directories to search; if None, auto-detect roots
    - max_results: stop after collecting this many matches to avoid long blocking runs
    - case_sensitive: if False, do a case-insensitive search

    The search avoids reading file contents and safely skips directories where permissions raise exceptions.
    Returns a list of absolute paths matching the name.
    """
    matches = []

    if not name:
        return matches

    if root_paths is None:
        root_paths = _get_roots()

    # Normalize search string
    needle = name if case_sensitive else name.lower()

    for root in root_paths:
        # os.walk will follow symlinks only when followlinks=True; we keep default False to avoid loops
        for current_dir, dirs, files in os.walk(root, topdown=True, onerror=None):
            # Filter out obviously unreadable/system directories for speed and safety
            try:
                # Skip hidden and some system folders in Unix
                # For Windows, skip Recycle Bin like directories starting with '$'
                dirs[:] = [d for d in dirs if not d.startswith('.') and not d.startswith('$')]
            except Exception:
                pass

            # Check filenames
            for fname in files:
                try:
                    compare = fname if case_sensitive else fname.lower()
                    if needle in compare:
                        matches.append(os.path.join(current_dir, fname))
                        if len(matches) >= max_results:
                            return matches
                except Exception:
                    continue

            # Also check directory names if user might search for directory
            for dname in list(dirs):
                try:
                    compare = dname if case_sensitive else dname.lower()
                    if needle in compare:
                        matches.append(os.path.join(current_dir, dname))
                        if len(matches) >= max_results:
                            return matches
                except Exception:
                    continue

    return matches
