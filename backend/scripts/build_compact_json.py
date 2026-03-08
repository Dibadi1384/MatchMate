"""
Build compact JSON files with stop words removed from all text fields.
Reads Chrome + YouTube JSON from SQLite, strips non-information words, writes one JSON file per user.
No new table—output is files only (e.g. compact_json/{user_id}.json).
"""
import json
import os
import sqlite3
import argparse
from pathlib import Path

# Reuse DB and sampling from build_compact_profile
_scripts_dir = Path(__file__).resolve().parent
if str(_scripts_dir) not in __import__("sys").path:
    __import__("sys").path.insert(0, str(_scripts_dir))

from build_compact_profile import (
    get_connection,
    init_schema,
    get_user_jsons,
    get_calendar_maps,
    MAX_HISTORY,
    MAX_WATCH,
    MAX_SEARCH_YT,
    MAX_SUBSCRIPTIONS,
    MAX_BOOKMARKS,
    MAX_CALENDAR_EVENTS,
    MAX_MAPS_PLACES,
)
from stop_words import strip_stop_words

DEFAULT_DB_PATH = "matchmate.db"
COMPACT_JSON_DIR = "compact_json"


def build_compact_stripped(
    chrome_data: dict,
    youtube_data: dict,
    calendar_data: dict = None,
    maps_data: dict = None,
) -> dict:
    """Build structured compact with stop words removed from all text fields (not from URLs)."""
    out = {"chrome": {}, "youtube": {}, "calendar": {}, "maps": {}}
    chrome_data = chrome_data or {}
    youtube_data = youtube_data or {}
    calendar_data = calendar_data or {}
    maps_data = maps_data or {}

    # Chrome history (already stripped + unique in pipeline)
    history = (chrome_data.get("browser_history") or [])[:MAX_HISTORY]
    out["chrome"]["browser_history"] = []
    for h in history:
        title = (h.get("title") or "").strip()
        url = (h.get("url") or "").strip()
        if title or url:
            out["chrome"]["browser_history"].append({
                "title": strip_stop_words(title),
                "url": url,
            })

    # Bookmarks
    bookmarks = (chrome_data.get("bookmarks") or [])[:MAX_BOOKMARKS]
    out["chrome"]["bookmarks"] = []
    for b in bookmarks:
        title = (b.get("title") or "").strip()
        url = (b.get("url") or "").strip()
        if title or url:
            out["chrome"]["bookmarks"].append({
                "title": strip_stop_words(title),
                "url": url,
            })

    # YouTube watch (already stripped + unique in pipeline)
    watch = (youtube_data.get("watch_history") or [])[:MAX_WATCH]
    out["youtube"]["watch_history"] = []
    for w in watch:
        title = (w.get("title") or "").strip()
        url = (w.get("url") or "").strip()
        if title or url:
            out["youtube"]["watch_history"].append({
                "title": strip_stop_words(title),
                "url": url,
            })

    # Search history
    search = (youtube_data.get("search_history") or [])[:MAX_SEARCH_YT]
    out["youtube"]["search_history"] = [strip_stop_words((s.get("query") or "").strip()) for s in search if (s.get("query") or "").strip()]

    # Subscriptions
    csv_data = youtube_data.get("csv_data") or {}
    subs = csv_data.get("subscriptions/subscriptions") or []
    out["youtube"]["subscriptions"] = []
    for row in subs[:MAX_SUBSCRIPTIONS]:
        if isinstance(row, dict):
            title = row.get("Channel title", row.get("Channel title (Original)", ""))
            t = strip_stop_words(str(title).strip())
            if t:
                out["youtube"]["subscriptions"].append(t)
        else:
            t = strip_stop_words(str(row).strip())
            if t:
                out["youtube"]["subscriptions"].append(t)

    # Playlists
    playlists_key = "playlists/playlists"
    out["youtube"]["playlists"] = []
    if playlists_key in csv_data and csv_data[playlists_key]:
        for row in csv_data[playlists_key][:100]:
            if isinstance(row, dict):
                title = row.get("Playlist title (original)", row.get("Playlist title", ""))
                t = strip_stop_words(str(title).strip())
                if t:
                    out["youtube"]["playlists"].append(t)

    # Calendar events
    events = (calendar_data.get("events") or [])[:MAX_CALENDAR_EVENTS]
    out["calendar"]["events"] = []
    for e in events:
        summary = strip_stop_words((e.get("summary") or "").strip())
        location = strip_stop_words((e.get("location") or "").strip())
        if summary or location:
            out["calendar"]["events"].append({"summary": summary, "location": location})

    # Maps labelled places
    places = (maps_data.get("labelled_places") or [])[:MAX_MAPS_PLACES]
    out["maps"]["labelled_places"] = []
    for p in places:
        name = strip_stop_words((p.get("name") or "").strip())
        address = strip_stop_words((p.get("address") or "").strip())
        if name or address:
            out["maps"]["labelled_places"].append({"name": name, "address": address})
    if maps_data.get("commute_routes"):
        out["maps"]["commute_routes"] = maps_data["commute_routes"]
    if maps_data.get("added_dishes"):
        out["maps"]["added_dishes"] = maps_data["added_dishes"]

    return out


def main():
    ap = argparse.ArgumentParser(
        description="Build compact JSON files (stop words removed) from Chrome+YouTube data in SQLite"
    )
    ap.add_argument("--user-id", required=True, help="User ID (e.g. diba-darooneh_1234)")
    ap.add_argument("--db", default=os.environ.get("SQLITE_DB", DEFAULT_DB_PATH), help="SQLite DB path")
    ap.add_argument("--out-dir", default=COMPACT_JSON_DIR, help=f"Output directory for JSON files (default: {COMPACT_JSON_DIR})")
    args = ap.parse_args()

    conn = get_connection(args.db)
    try:
        init_schema(conn)
        chrome_data, youtube_data = get_user_jsons(conn, args.user_id)
        calendar_data, maps_data = get_calendar_maps(conn, args.user_id)
        if not chrome_data and not youtube_data and not calendar_data and not maps_data:
            print("No chrome, youtube, calendar, or maps data found for user:", args.user_id)
            return 1
        data = build_compact_stripped(chrome_data, youtube_data, calendar_data, maps_data)
        out_dir = Path(args.out_dir)
        out_dir.mkdir(parents=True, exist_ok=True)
        out_path = out_dir / f"{args.user_id}.json"
        with open(out_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        print("Compact JSON written:", out_path.resolve())
    finally:
        conn.close()
    return 0


if __name__ == "__main__":
    exit(main() or 0)
