"""
Extract Chrome user-data folder into a single JSON.
Browser history: stop-word removal on titles, then keep last 1000 unique by (stripped) title (newest-first).
"""
import json
import csv
import argparse
from pathlib import Path
from html.parser import HTMLParser

from stop_words import strip_stop_words

HISTORY_LIMIT = 10000


class BookmarksParser(HTMLParser):
    """Parse Netscape Bookmarks.html into list of {title, url, add_date, icon_uri}."""

    def __init__(self):
        super().__init__()
        self.bookmarks = []
        self._in_anchor = False
        self._current = None

    def handle_starttag(self, tag, attrs):
        if tag == "a":
            self._in_anchor = True
            d = dict(attrs)
            self._current = {
                "url": d.get("href", ""),
                "title": "",
                "add_date": d.get("add_date", ""),
                "icon_uri": d.get("icon_uri", ""),
            }

    def handle_endtag(self, tag):
        if tag == "a" and self._current:
            self.bookmarks.append(self._current)
            self._current = None
        self._in_anchor = False

    def handle_data(self, data):
        if self._in_anchor and self._current is not None:
            self._current["title"] = data.strip() or self._current.get("title", "")


def parse_bookmarks(html_path: Path) -> list:
    if not html_path.exists():
        return []
    with open(html_path, "r", encoding="utf-8", errors="replace") as f:
        parser = BookmarksParser()
        parser.feed(f.read())
    return parser.bookmarks


def load_json_safe(path: Path, default=None):
    if default is None:
        default = {}
    if not path.exists():
        return default
    try:
        with open(path, "r", encoding="utf-8", errors="replace") as f:
            return json.load(f)
    except (json.JSONDecodeError, OSError):
        return default


def extract_history(chrome_dir: Path) -> list:
    history_path = chrome_dir / "History.json"
    if not history_path.exists():
        return []
    data = load_json_safe(history_path, {})
    entries = data.get("Browser History") or []
    if not isinstance(entries, list):
        return []
    # Newest first. Dedup by stripped title: same (stripped) title = not unique; keep first HISTORY_LIMIT unique.
    seen = set()
    result = []
    for entry in entries:
        title = (entry.get("title") or "").strip()
        stripped = strip_stop_words(title)
        key = stripped.lower() if stripped else ""
        if key in seen:
            continue
        seen.add(key)
        # Store entry with stripped title; keep url and other fields
        out = dict(entry)
        out["title"] = stripped
        result.append(out)
        if len(result) >= HISTORY_LIMIT:
            break
    return result


def extract_dictionary(chrome_dir: Path) -> list:
    csv_path = chrome_dir / "Dictionary.csv"
    if not csv_path.exists():
        return []
    rows = []
    with open(csv_path, "r", encoding="utf-8", errors="replace") as f:
        reader = csv.DictReader(f)
        for row in reader:
            rows.append(dict(row))
    return rows


def _dedup_by_stripped_title(items: list, title_key: str, limit: int) -> list:
    """Dedup by stripped title (same title = not unique), keep first `limit` unique. Preserves order."""
    seen = set()
    result = []
    for item in items:
        title = (item.get(title_key) or "").strip()
        stripped = strip_stop_words(title)
        key = stripped.lower() if stripped else ""
        if key in seen:
            continue
        seen.add(key)
        out = dict(item)
        out[title_key] = stripped
        result.append(out)
        if len(result) >= limit:
            break
    return result


def extract_chrome(chrome_dir: Path) -> dict:
    chrome_dir = Path(chrome_dir)
    bookmarks_raw = parse_bookmarks(chrome_dir / "Bookmarks.html")
    bookmarks = _dedup_by_stripped_title(bookmarks_raw, "title", limit=500)
    return {
        "browser_history": extract_history(chrome_dir),
        "bookmarks": bookmarks,
        "reading_list": parse_bookmarks(chrome_dir / "Reading list.html"),
        "addresses_and_more": load_json_safe(chrome_dir / "Addresses and more.json"),
        "settings": load_json_safe(chrome_dir / "Settings.json"),
        "extensions": load_json_safe(chrome_dir / "Extensions.json"),
        "device_information": load_json_safe(chrome_dir / "Device Information.json"),
        "os_settings": load_json_safe(chrome_dir / "OS Settings.json"),
        "dictionary": extract_dictionary(chrome_dir),
    }


def main():
    ap = argparse.ArgumentParser(description="Extract Chrome user-data to JSON")
    ap.add_argument("chrome_dir", type=Path, help="Path to Chrome export folder (e.g. user-data/Chrome)")
    ap.add_argument("-o", "--output", type=Path, help="Write JSON to file (default: stdout)")
    args = ap.parse_args()
    out = extract_chrome(args.chrome_dir)
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        with open(args.output, "w", encoding="utf-8") as f:
            json.dump(out, f, indent=2, ensure_ascii=False)
    else:
        print(json.dumps(out, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
