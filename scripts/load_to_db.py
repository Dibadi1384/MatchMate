"""
Load extracted Chrome, YouTube, Calendar, and Maps JSON for a user into SQLite.
Ensures user exists, then upserts user_chrome_data, user_youtube_data, user_calendar_data, user_maps_data.
"""
import json
import os
import sqlite3
import argparse
from pathlib import Path

_scripts_dir = Path(__file__).resolve().parent
if str(_scripts_dir) not in __import__("sys").path:
    __import__("sys").path.insert(0, str(_scripts_dir))

from extract_chrome import extract_chrome
from extract_youtube import extract_youtube
from extract_calendar import extract_calendar
from extract_maps import extract_maps

DEFAULT_USER_ID = "diba-darooneh_1234"
DEFAULT_DB_PATH = "matchmate.db"


def get_connection(db_path: str = None):
    path = db_path or os.environ.get("SQLITE_DB", DEFAULT_DB_PATH)
    conn = sqlite3.connect(path)
    conn.row_factory = sqlite3.Row
    return conn


def init_schema(conn: sqlite3.Connection):
    """Create tables if they don't exist (SQLite schema)."""
    schema_sql = (Path(__file__).resolve().parent.parent / "schema.sql").read_text(encoding="utf-8")
    conn.executescript(schema_sql)
    conn.commit()


def ensure_user(conn: sqlite3.Connection, user_id: str, display_name: str = None):
    display_name = display_name or user_id
    conn.execute(
        """
        INSERT INTO users (user_id, display_name, updated_at)
        VALUES (?, ?, datetime('now'))
        ON CONFLICT (user_id) DO UPDATE SET
            display_name = COALESCE(excluded.display_name, users.display_name),
            updated_at = datetime('now')
        """,
        (user_id, display_name),
    )
    conn.commit()


def upsert_chrome(conn: sqlite3.Connection, user_id: str, chrome_json: dict):
    json_str = json.dumps(chrome_json, ensure_ascii=False)
    conn.execute(
        """
        INSERT INTO user_chrome_data (user_id, chrome_json, updated_at)
        VALUES (?, ?, datetime('now'))
        ON CONFLICT (user_id) DO UPDATE SET
            chrome_json = excluded.chrome_json,
            updated_at = datetime('now')
        """,
        (user_id, json_str),
    )
    conn.commit()


def upsert_youtube(conn: sqlite3.Connection, user_id: str, youtube_json: dict):
    json_str = json.dumps(youtube_json, ensure_ascii=False)
    conn.execute(
        """
        INSERT INTO user_youtube_data (user_id, youtube_json, updated_at)
        VALUES (?, ?, datetime('now'))
        ON CONFLICT (user_id) DO UPDATE SET
            youtube_json = excluded.youtube_json,
            updated_at = datetime('now')
        """,
        (user_id, json_str),
    )
    conn.commit()


def upsert_calendar(conn: sqlite3.Connection, user_id: str, calendar_json: dict):
    json_str = json.dumps(calendar_json, ensure_ascii=False)
    conn.execute(
        """
        INSERT INTO user_calendar_data (user_id, calendar_json, updated_at)
        VALUES (?, ?, datetime('now'))
        ON CONFLICT (user_id) DO UPDATE SET
            calendar_json = excluded.calendar_json,
            updated_at = datetime('now')
        """,
        (user_id, json_str),
    )
    conn.commit()


def upsert_maps(conn: sqlite3.Connection, user_id: str, maps_json: dict):
    json_str = json.dumps(maps_json, ensure_ascii=False)
    conn.execute(
        """
        INSERT INTO user_maps_data (user_id, maps_json, updated_at)
        VALUES (?, ?, datetime('now'))
        ON CONFLICT (user_id) DO UPDATE SET
            maps_json = excluded.maps_json,
            updated_at = datetime('now')
        """,
        (user_id, json_str),
    )
    conn.commit()


def main():
    ap = argparse.ArgumentParser(description="Load Chrome/YouTube data for a user into SQLite")
    ap.add_argument("--user-id", default=DEFAULT_USER_ID, help=f"User ID (default: {DEFAULT_USER_ID})")
    ap.add_argument("--chrome-dir", type=Path, help="Path to Chrome export folder (extracts to JSON)")
    ap.add_argument("--youtube-dir", type=Path, help="Path to YouTube export folder (extracts to JSON)")
    ap.add_argument("--calendar-dir", type=Path, help="Path to Calendar export folder (extracts from ICS)")
    ap.add_argument("--maps-dir", type=Path, help="Path to Maps export folder")
    ap.add_argument("--chrome-json", type=Path, help="Path to pre-extracted Chrome JSON file")
    ap.add_argument("--youtube-json", type=Path, help="Path to pre-extracted YouTube JSON file")
    ap.add_argument("--calendar-json", type=Path, help="Path to pre-extracted Calendar JSON file")
    ap.add_argument("--maps-json", type=Path, help="Path to pre-extracted Maps JSON file")
    ap.add_argument("--db", default=os.environ.get("SQLITE_DB", DEFAULT_DB_PATH), help=f"SQLite DB file path (default: {DEFAULT_DB_PATH})")
    ap.add_argument("--dry-run", action="store_true", help="Extract only; write JSON to current dir, do not connect to DB")
    args = ap.parse_args()

    chrome_data = None
    youtube_data = None
    calendar_data = None
    maps_data = None

    if args.chrome_dir:
        chrome_data = extract_chrome(args.chrome_dir)
    elif args.chrome_json and args.chrome_json.exists():
        with open(args.chrome_json, "r", encoding="utf-8") as f:
            chrome_data = json.load(f)

    if args.youtube_dir:
        youtube_data = extract_youtube(args.youtube_dir)
    elif args.youtube_json and args.youtube_json.exists():
        with open(args.youtube_json, "r", encoding="utf-8") as f:
            youtube_data = json.load(f)

    if args.calendar_dir:
        calendar_data = extract_calendar(args.calendar_dir)
    elif args.calendar_json and args.calendar_json.exists():
        with open(args.calendar_json, "r", encoding="utf-8") as f:
            calendar_data = json.load(f)

    if args.maps_dir:
        maps_data = extract_maps(args.maps_dir)
    elif args.maps_json and args.maps_json.exists():
        with open(args.maps_json, "r", encoding="utf-8") as f:
            maps_data = json.load(f)

    if not chrome_data and not youtube_data and not calendar_data and not maps_data:
        print("Provide at least one of: --chrome-dir/--chrome-json, --youtube-dir/--youtube-json, --calendar-dir/--calendar-json, --maps-dir/--maps-json")
        return 2

    if args.dry_run:
        if chrome_data:
            Path("extracted_chrome.json").write_text(json.dumps(chrome_data, indent=2, ensure_ascii=False), encoding="utf-8")
            print("Chrome JSON written to extracted_chrome.json")
        if youtube_data:
            Path("extracted_youtube.json").write_text(json.dumps(youtube_data, indent=2, ensure_ascii=False), encoding="utf-8")
            print("YouTube JSON written to extracted_youtube.json")
        if calendar_data:
            Path("extracted_calendar.json").write_text(json.dumps(calendar_data, indent=2, ensure_ascii=False), encoding="utf-8")
            print("Calendar JSON written to extracted_calendar.json")
        if maps_data:
            Path("extracted_maps.json").write_text(json.dumps(maps_data, indent=2, ensure_ascii=False), encoding="utf-8")
            print("Maps JSON written to extracted_maps.json")
        return 0

    conn = get_connection(args.db)
    try:
        init_schema(conn)
        ensure_user(conn, args.user_id)
        if chrome_data:
            upsert_chrome(conn, args.user_id, chrome_data)
            print("Chrome data upserted for", args.user_id)
        if youtube_data:
            upsert_youtube(conn, args.user_id, youtube_data)
            print("YouTube data upserted for", args.user_id)
        if calendar_data:
            upsert_calendar(conn, args.user_id, calendar_data)
            print("Calendar data upserted for", args.user_id)
        if maps_data:
            upsert_maps(conn, args.user_id, maps_data)
            print("Maps data upserted for", args.user_id)
        print("Database:", Path(args.db).resolve())
    finally:
        conn.close()
    return 0


if __name__ == "__main__":
    exit(main() or 0)
