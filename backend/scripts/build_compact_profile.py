"""
Build compact text from a user's Chrome + YouTube JSON (loaded from SQLite)
and store it in user_compact_profile. Used before sending to Gemini.

Data in DB is already stripped + deduped (last 10000 unique by title/query from extraction).
"""
import json
import os
import sqlite3
import argparse
from pathlib import Path

DEFAULT_DB_PATH = "matchmate.db"
# Extraction gives at most 10000 history, 10000 watch, 10000 search. Use all or cap for token limit.
MAX_HISTORY = 10000
MAX_WATCH = 10000
MAX_SEARCH_YT = 10000
MAX_SUBSCRIPTIONS = 500
MAX_BOOKMARKS = 500
MAX_COMPACT_CHARS = 120_000
MAX_CALENDAR_EVENTS = 3000
MAX_MAPS_PLACES = 1000


def get_connection(db_path: str = None) -> sqlite3.Connection:
    path = db_path or os.environ.get("SQLITE_DB", DEFAULT_DB_PATH)
    conn = sqlite3.connect(path)
    conn.row_factory = sqlite3.Row
    return conn


def init_schema(conn: sqlite3.Connection):
    schema_path = Path(__file__).resolve().parent.parent / "schema.sql"
    if schema_path.exists():
        conn.executescript(schema_path.read_text(encoding="utf-8"))
        conn.commit()


def build_compact_from_jsons(
    chrome_data: dict,
    youtube_data: dict,
    calendar_data: dict = None,
    maps_data: dict = None,
) -> str:
    """Build compact text from chrome, youtube, calendar, maps (already stripped + unique where applicable)."""
    parts = []
    chrome_data = chrome_data or {}
    youtube_data = youtube_data or {}
    calendar_data = calendar_data or {}
    maps_data = maps_data or {}

    # ----- Chrome (data already up to 10000 unique, stripped) -----
    parts.append("=== CHROME (browser history, bookmarks) ===\n")
    history = (chrome_data.get("browser_history") or [])[:MAX_HISTORY]
    for i, h in enumerate(history):
        title = (h.get("title") or "").strip()
        url = (h.get("url") or "").strip()
        if title or url:
            parts.append(f"  {i+1}. {title} | {url}\n")
    parts.append("\nBookmarks:\n")
    for b in (chrome_data.get("bookmarks") or [])[:MAX_BOOKMARKS]:
        title = (b.get("title") or "").strip()
        url = (b.get("url") or "").strip()
        if title or url:
            parts.append(f"  - {title} | {url}\n")

    # ----- YouTube (data already up to 10000 unique watch/search, stripped) -----
    parts.append("\n=== YOUTUBE (watch history, search, subscriptions) ===\n")
    watch = (youtube_data.get("watch_history") or [])[:MAX_WATCH]
    for i, w in enumerate(watch):
        title = (w.get("title") or "").strip()
        url = (w.get("url") or "").strip()
        if title or url:
            parts.append(f"  Watched: {title} | {url}\n")
    parts.append("\nSearch history:\n")
    for s in (youtube_data.get("search_history") or [])[:MAX_SEARCH_YT]:
        q = (s.get("query") or "").strip()
        if q:
            parts.append(f"  - {q}\n")
    csv_data = youtube_data.get("csv_data") or {}
    subs = csv_data.get("subscriptions/subscriptions") or []
    if subs:
        parts.append("\nSubscribed channels:\n")
        for row in subs[:MAX_SUBSCRIPTIONS]:
            if isinstance(row, dict):
                title = row.get("Channel title", row.get("Channel title (Original)", ""))
                parts.append(f"  - {title}\n")
            else:
                parts.append(f"  - {row}\n")
    playlists_key = "playlists/playlists"
    if playlists_key in csv_data and csv_data[playlists_key]:
        parts.append("\nPlaylists:\n")
        for row in csv_data[playlists_key][:100]:
            if isinstance(row, dict):
                title = row.get("Playlist title (original)", row.get("Playlist title", ""))
                parts.append(f"  - {title}\n")

    # ----- Calendar -----
    events = (calendar_data.get("events") or [])[:MAX_CALENDAR_EVENTS]
    if events:
        parts.append("\n=== CALENDAR (events) ===\n")
        for e in events:
            summary = (e.get("summary") or "").strip()
            location = (e.get("location") or "").strip()
            if summary or location:
                parts.append(f"  {summary} | {location}\n")

    # ----- Maps -----
    places = (maps_data.get("labelled_places") or [])[:MAX_MAPS_PLACES]
    if places:
        parts.append("\n=== MAPS (labelled places) ===\n")
        for p in places:
            name = (p.get("name") or "").strip()
            address = (p.get("address") or "").strip()
            if name or address:
                parts.append(f"  {name} | {address}\n")
    if maps_data.get("commute_routes"):
        parts.append("\nMaps commute routes: (present)\n")
    if maps_data.get("added_dishes"):
        parts.append("\nMaps added dishes/activities: (present)\n")

    text = "".join(parts)
    if len(text) > MAX_COMPACT_CHARS:
        text = text[:MAX_COMPACT_CHARS] + "\n\n[truncated]"
    return text


def get_user_jsons(conn: sqlite3.Connection, user_id: str) -> tuple:
    """Load chrome_json and youtube_json for user from SQLite."""
    cur = conn.execute("SELECT chrome_json FROM user_chrome_data WHERE user_id = ?", (user_id,))
    row = cur.fetchone()
    chrome_data = json.loads(row["chrome_json"]) if row else None
    cur = conn.execute("SELECT youtube_json FROM user_youtube_data WHERE user_id = ?", (user_id,))
    row = cur.fetchone()
    youtube_data = json.loads(row["youtube_json"]) if row else None
    return chrome_data, youtube_data


def get_calendar_maps(conn: sqlite3.Connection, user_id: str) -> tuple:
    """Load calendar_json and maps_json for user from SQLite."""
    cur = conn.execute("SELECT calendar_json FROM user_calendar_data WHERE user_id = ?", (user_id,))
    row = cur.fetchone()
    calendar_data = json.loads(row["calendar_json"]) if row else None
    cur = conn.execute("SELECT maps_json FROM user_maps_data WHERE user_id = ?", (user_id,))
    row = cur.fetchone()
    maps_data = json.loads(row["maps_json"]) if row else None
    return calendar_data, maps_data


def upsert_compact_profile(conn: sqlite3.Connection, user_id: str, compact_text: str):
    conn.execute(
        """
        INSERT INTO user_compact_profile (user_id, compact_text, updated_at)
        VALUES (?, ?, datetime('now'))
        ON CONFLICT (user_id) DO UPDATE SET
            compact_text = excluded.compact_text,
            updated_at = datetime('now')
        """,
        (user_id, compact_text),
    )
    conn.commit()


def main():
    ap = argparse.ArgumentParser(
        description="Build compact profile from user's Chrome+YouTube JSON in SQLite and save to user_compact_profile"
    )
    ap.add_argument("--user-id", required=True, help="User ID (e.g. diba-darooneh_1234)")
    ap.add_argument("--db", default=os.environ.get("SQLITE_DB", DEFAULT_DB_PATH), help="SQLite DB path")
    args = ap.parse_args()

    conn = get_connection(args.db)
    try:
        init_schema(conn)
        chrome_data, youtube_data = get_user_jsons(conn, args.user_id)
        calendar_data, maps_data = get_calendar_maps(conn, args.user_id)
        if not chrome_data and not youtube_data and not calendar_data and not maps_data:
            print("No chrome, youtube, calendar, or maps data found for user:", args.user_id)
            return 1
        compact = build_compact_from_jsons(chrome_data or {}, youtube_data or {}, calendar_data, maps_data)
        upsert_compact_profile(conn, args.user_id, compact)
        print("Compact profile saved for", args.user_id, "| length:", len(compact), "chars")
    finally:
        conn.close()
    return 0


if __name__ == "__main__":
    exit(main() or 0)
