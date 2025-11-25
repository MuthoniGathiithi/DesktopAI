#!/usr/bin/env python3
"""
Lightweight entry point for the DesktopAI bundle.

- default: start GUI (ai_operator.start_gui)
- --cli: run a simple search CLI or other non-GUI helpers

This file is meant to be used as the PyInstaller entry point when creating a single-file binary.
"""
import argparse
import sys
import platform

parser = argparse.ArgumentParser(prog='DesktopAI', description='DesktopAI — single-file bundle entry')
parser.add_argument('--cli', action='store_true', help='Run in CLI mode (no GUI).')
parser.add_argument('--search', '-s', help='Run a simple direct search (name substring).')
parser.add_argument('--max', '-m', type=int, default=200, help='Max results for a direct search')
parser.add_argument('--case', action='store_true', help='Case-sensitive search')
args = parser.parse_args()

if args.cli:
    # CLI mode — if search requested, run direct search
    if args.search:
        try:
            from premium_search import find_files_smart
        except Exception:
            find_files_smart = None

        try:
            from premium_search import find_files_direct
        except Exception:
            # fallback
            from search_utils import find_files_by_name as find_files_direct

        roots = None
        # Prefer AI smart search results if available
        if find_files_smart:
            ai_res = find_files_smart(args.search, max_results=args.max)
            if ai_res:
                # ai_res may be list of (path,score)
                if all(isinstance(x, tuple) for x in ai_res):
                    results = [p for p, s in ai_res]
                else:
                    results = ai_res
            else:
                results = find_files_direct(args.search, max_results=args.max, case_sensitive=args.case)
        else:
            results = find_files_direct(args.search, max_results=args.max, case_sensitive=args.case)
        if not results:
            print('No results found')
            sys.exit(1)

        for i, r in enumerate(results, 1):
            print(f"{i}. {r}")

        print(f"\nFound {len(results)} matches (showing up to {args.max}).")
        sys.exit(0)

    # No search — provide useful info
    print('DesktopAI CLI mode\nUse --search <term> to run a direct filesystem search (fast, safe).')
    sys.exit(0)

# Default: run GUI
try:
    # import here so tests and packaging can choose CLI without creating GUI components
    import ai_operator
    ai_operator.start_gui()
except Exception as e:
    print('Unable to start GUI: ', e)
    print('You can run with --cli to use the lightweight CLI')
    sys.exit(1)
