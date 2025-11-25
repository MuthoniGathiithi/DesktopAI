"""
AI-assisted smart search helper
- Uses fuzzy matching (fuzzywuzzy) to score candidates by filename similarity
- Boosts results from recent activity and the premium index when available
- Falls back to fast direct scan when needed

This makes the assistant behave more like an "intelligent" search assistant (no cloud models required).
"""
from typing import List, Tuple
from datetime import datetime, timedelta
import os

try:
    from fuzzywuzzy import fuzz
    from fuzzywuzzy import process
except Exception:
    # fuzzywuzzy missing -> fallback to basic substring scoring
    fuzz = None
    process = None

# Try to use premium_search index and direct search functions if available
try:
    from premium_search import premium_search, find_files_direct
except Exception:
    premium_search = None
    find_files_direct = None


def _fuzzy_score(query: str, candidate: str) -> int:
    if process:
        # return fuzzy ratio for substring matching too
        return fuzz.token_set_ratio(query, candidate)
    # simple substring heuristic
    q = query.lower()
    c = candidate.lower()
    if q == c:
        return 100
    if q in c:
        return 85
    if c in q:
        return 80
    # no match -> 0
    return 0


def _recency_boost(file_path: str) -> int:
    """Boost score for recently-accessed files (if premium_search has access_history)."""
    try:
        if not premium_search:
            return 0
        # check access_history table for latest access
        conn = __import__('sqlite3').connect(premium_search.search_db)
        cur = conn.cursor()
        cur.execute('SELECT timestamp FROM access_history WHERE file_path = ? ORDER BY timestamp DESC LIMIT 1', (file_path,))
        row = cur.fetchone()
        conn.close()
        if not row:
            return 0
        ts = datetime.fromisoformat(row[0])
        secs = (datetime.now() - ts).total_seconds()
        # higher boost for more recent (less seconds) — simple exponential decay
        if secs < 3600:  # within last hour
            return 15
        if secs < 86400:  # within last day
            return 10
        if secs < 7 * 86400:
            return 5
        return 0
    except Exception:
        return 0


def _index_presence_boost(file_path: str) -> int:
    # If the premium index has additional content matches, give a boost
    try:
        if not premium_search:
            return 0
        if file_path in premium_search.file_index:
            return 5
    except Exception:
        pass
    return 0


def smart_search(query: str, max_results: int = 200, use_index: bool = True, roots: List[str] = None) -> List[Tuple[str, int]]:
    """Search and return ranked (file_path, score) pairs.

    Steps:
    - If premium index exists and use_index True, gather candidates from filename matches
      and content cache for quick scoring.
    - Score candidates with fuzzy matching, add recency and indexing boosts.
    - If candidates are sparse/low-scoring, run a fast direct scan (find_files_direct) and include results.
    - Return ordered list of tuples (path, total_score), highest first.
    """
    query = query.strip()
    if not query:
        return []

    candidates = {}

    # 1) gather index candidates
    if use_index and premium_search:
        try:
            # search by filename struct via sqlite, plus content cache
            conn = __import__('sqlite3').connect(premium_search.search_db)
            cur = conn.cursor()
            # filename LIKE matches
            cur.execute("SELECT file_path, filename FROM file_index WHERE filename LIKE ? LIMIT 500", (f"%{query}%",))
            for row in cur.fetchall():
                path, fname = row[0], row[1] if len(row) > 1 else os.path.basename(row[0])
                score = _fuzzy_score(query, fname)
                candidates[path] = max(candidates.get(path, 0), score)

            # search content cache for query terms
            cur.execute('SELECT file_path, content_text FROM content_cache WHERE content_text LIKE ? LIMIT 500', (f"%{query}%",))
            for row in cur.fetchall():
                path, content = row[0], (row[1] or '')
                # content match -> good score
                score = _fuzzy_score(query, os.path.basename(path))
                score = max(score, 60)  # content match baseline
                candidates[path] = max(candidates.get(path, 0), score)
            conn.close()
        except Exception:
            # ignore index errors
            pass

    # 2) Attach recency and presence boosts
    scored = []
    for path, base in list(candidates.items()):
        boost = _recency_boost(path) + _index_presence_boost(path)
        total = base + boost
        scored.append((path, total))

    # 3) If not enough high quality results, fallback to direct scan
    if len(scored) < 10 or all(s[1] < 60 for s in scored):
        try:
            # Use direct finder
            if find_files_direct:
                scan_roots = roots
                results = find_files_direct(query, root_paths=scan_roots, max_results=1000, case_sensitive=False)
            else:
                # try import local helper
                from search_utils import find_files_by_name as _find
                results = _find(query, root_paths=roots, max_results=1000, case_sensitive=False)

            for rpath in results:
                base = _fuzzy_score(query, os.path.basename(rpath))
                # avoid duplicates
                if rpath in candidates:
                    total = max(candidates[rpath], base) + _recency_boost(rpath) + _index_presence_boost(rpath)
                else:
                    total = base + _recency_boost(rpath) + _index_presence_boost(rpath)
                candidates[rpath] = total
        except Exception:
            pass

    # Final ranking
    final = [(p, int(s)) for p, s in candidates.items()]
    final.sort(key=lambda x: x[1], reverse=True)
    # Trim results
    return final[:max_results]


if __name__ == '__main__':
    import argparse, json
    parser = argparse.ArgumentParser(description='Smart, fuzzy, context-aware file search (local only).')
    parser.add_argument('--q', '-q', required=True)
    parser.add_argument('--max', '-m', type=int, default=100)
    args = parser.parse_args()

    res = smart_search(args.q, max_results=args.max)
    print(json.dumps(res, indent=2))
