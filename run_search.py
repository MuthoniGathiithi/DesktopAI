#!/usr/bin/env python3
import argparse
import json
import sys
from search_utils import find_files_by_name, _get_roots


def main():
    parser = argparse.ArgumentParser(description='Quick CLI to search for files by name. Safe, cross-platform.')
    parser.add_argument('--name', '-n', required=True, help='Name or substring to search for (e.g. "obed")')
    parser.add_argument('--root', '-r', help='Single root path to start from (default: auto-detected roots)')
    parser.add_argument('--max', '-m', type=int, default=200, help='Maximum results to return')
    parser.add_argument('--case', action='store_true', help='Perform a case-sensitive search')
    parser.add_argument('--json', dest='as_json', action='store_true', help='Print results as JSON')

    args = parser.parse_args()

    roots = None
    if args.root:
        roots = [args.root]
    else:
        roots = _get_roots()

    print(f"Searching for: '{args.name}' in roots: {roots} (case-sensitive={args.case})...\n")

    matches = find_files_by_name(args.name, root_paths=roots, max_results=args.max, case_sensitive=args.case)

    if not matches:
        print("No matches found — check the name and try again (you may need sudo privileges to search some folders).")
        sys.exit(1)

    if args.as_json:
        print(json.dumps(matches, indent=2))
        return

    for i, m in enumerate(matches, 1):
        print(f"{i}. {m}")

    print(f"\nFound {len(matches)} matches (showing up to {args.max}).")


if __name__ == '__main__':
    main()
