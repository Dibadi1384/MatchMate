"""
Extract YouTube/YouTube Music user-data folder into a single JSON.
Watch/search: stop-word removal, then last 10000 (watch) / 10000 (search) unique by stripped title/query (newest-first).
"""
import json
import csv
import re
import argparse
from pathlib import Path

from stop_words import strip_stop_words

WATCH_LIMIT = 10000
SEARCH_LIMIT = 10000


def _read_file(path: Path, max_mb: float = 100.0) -> str:
    """Read file in chunks to handle very large HTML."""
    path = Path(path)
    if not path.exists():
        return ""
    size_mb = path.stat().st_size / (1024 * 1024)
    if size_mb > max_mb:
        # For huge files, read in chunks and only keep content we need
        return _read_large_html(path)
    with open(path, "r", encoding="utf-8", errors="replace") as f:
        return f.read()


def _read_large_html(path: Path, chunk_size: int = 512 * 1024) -> str:
    """Read large HTML in chunks and concatenate (for regex parsing)."""
    out = []
    with open(path, "r", encoding="utf-8", errors="replace") as f:
        while True:
            chunk = f.read(chunk_size)
            if not chunk:
                break
            out.append(chunk)
    return "".join(out)


# Watched <a href="https://www.youtube.com/watch?v=VIDEO_ID">Title</a> ... then date like "6 Mar 2026, 17:00:48 GMT-05:00"
WATCH_PATTERN = re.compile(
    r'Watched\s+<a\s+href="(https://www\.youtube\.com/watch\?v=([^"]+))">([^<]*)</a>',
    re.IGNORECASE,
)
# Date after the watch block: "6 Mar 2026, 17:00:48 GMT-05:00" or "28 Feb 2026, 18:55:01 GMT-05:00"
DATE_PATTERN = re.compile(
    r"(\d{1,2}\s+\w+\s+\d{4},\s*\d{1,2}:\d{2}:\d{2}\s+GMT[^\s<]*)"
)


def extract_watch_history(html_content: str) -> list:
    raw = []
    for m in WATCH_PATTERN.finditer(html_content):
        url, video_id, title = m.group(1), m.group(2), m.group(3)
        rest = html_content[m.end() : m.end() + 400]
        date_m = DATE_PATTERN.search(rest)
        watched_at = date_m.group(1).strip() if date_m else None
        raw.append({
            "video_id": video_id,
            "url": url,
            "title": title.strip(),
            "watched_at": watched_at,
        })
    # Newest first. Dedup by stripped title; keep first WATCH_LIMIT unique.
    seen = set()
    result = []
    for entry in raw:
        title = (entry.get("title") or "").strip()
        stripped = strip_stop_words(title)
        key = stripped.lower() if stripped else ""
        if key in seen:
            continue
        seen.add(key)
        out = dict(entry)
        out["title"] = stripped
        result.append(out)
        if len(result) >= WATCH_LIMIT:
            break
    return result


# Searched for "query" or similar
SEARCH_PATTERN = re.compile(
    r'Searched for\s+[^<]*</div>|">Searched for\s+([^<"]+)',
    re.IGNORECASE,
)


def extract_search_history(html_content: str) -> list:
    raw = []
    for m in re.finditer(r'Searched for\s+([^<]+?)(?:<|$)', html_content, re.IGNORECASE):
        query = m.group(1).strip().strip('"')
        if not query or query in ("YouTube", "here"):
            continue
        rest = html_content[m.end() : m.end() + 300]
        date_m = DATE_PATTERN.search(rest)
        searched_at = date_m.group(1).strip() if date_m else None
        raw.append({"query": query, "searched_at": searched_at})
    # Dedup by stripped query; keep first SEARCH_LIMIT unique.
    seen = set()
    result = []
    for entry in raw:
        query = (entry.get("query") or "").strip()
        stripped = strip_stop_words(query)
        key = stripped.lower() if stripped else ""
        if key in seen:
            continue
        seen.add(key)
        result.append({"query": stripped, "searched_at": entry.get("searched_at")})
        if len(result) >= SEARCH_LIMIT:
            break
    return result


def csv_to_json(path: Path) -> list:
    if not path.exists():
        return []
    rows = []
    with open(path, "r", encoding="utf-8", errors="replace") as f:
        try:
            reader = csv.DictReader(f)
            for row in reader:
                rows.append(dict(row))
        except Exception:
            return []
    return rows


def collect_csvs(youtube_dir: Path) -> dict:
    """Recursively load all CSVs under youtube_dir into a nested dict by relative path."""
    result = {}
    youtube_dir = Path(youtube_dir)
    for p in youtube_dir.rglob("*.csv"):
        rel = p.relative_to(youtube_dir)
        key = str(rel).replace("\\", "/").replace(".csv", "")
        # Use last part as key if single file in folder (e.g. subscriptions/subscriptions -> subscriptions)
        parts = key.split("/")
        if len(parts) > 1 and parts[-1] == parts[-2]:
            key = "/".join(parts[:-1]) + "/" + parts[-1]
        result[key] = csv_to_json(p)
    return result


def extract_youtube(youtube_dir: Path) -> dict:
    youtube_dir = Path(youtube_dir)
    history_dir = youtube_dir / "history"
    watch_html = _read_file(history_dir / "watch-history.html")
    search_html = _read_file(history_dir / "search-history.html")

    return {
        "watch_history": extract_watch_history(watch_html),
        "search_history": extract_search_history(search_html),
        "csv_data": collect_csvs(youtube_dir),
    }


def main():
    ap = argparse.ArgumentParser(description="Extract YouTube user-data to JSON")
    ap.add_argument(
        "youtube_dir",
        type=Path,
        help="Path to YouTube and YouTube Music export folder",
    )
    ap.add_argument("-o", "--output", type=Path, help="Write JSON to file (default: stdout)")
    args = ap.parse_args()
    out = extract_youtube(args.youtube_dir)
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        with open(args.output, "w", encoding="utf-8") as f:
            json.dump(out, f, indent=2, ensure_ascii=False)
    else:
        print(json.dumps(out, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
