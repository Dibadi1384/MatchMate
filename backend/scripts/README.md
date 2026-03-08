# Chrome & YouTube → SQLite pipeline

## Overview

- **Extraction (new pipeline):** For Chrome and YouTube we **first** apply stop-word removal to titles/queries, **then** keep the **last 10000 unique** items by (stripped) title/query (newest-first). Same stripped title = not unique; we keep the most recent of each.
- **Chrome:** `user-data/Chrome` → JSON with browser history (10000 unique stripped titles), bookmarks (500 unique), plus settings, extensions, etc.
- **YouTube:** `user-data/YouTube and YouTube Music` → JSON with watch history (10000 unique stripped titles), search history (10000 unique stripped queries), plus all CSVs.
- **Database:** SQLite stores users and their Chrome/YouTube JSON in `users`, `user_chrome_data`, and `user_youtube_data`. Compact text and compact JSON files use this data (already stripped and unique).

User ID links uploads to data (e.g. `diba-darooneh_1234` for the current demo folder).

## Setup

No database server or `pip install` required. Python’s built-in `sqlite3` is used. The loader creates the DB file and applies the schema automatically if they don’t exist.

## Usage

### Extract only (no DB)

```bash
# Chrome → JSON (stop-word strip, then last 10000 unique by title)
python scripts/extract_chrome.py user-data/Chrome -o extracted_chrome.json

# YouTube → JSON (stop-word strip, then last 10000 watch / 10000 search unique)
python scripts/extract_youtube.py "user-data/YouTube and YouTube Music" -o extracted_youtube.json
```

### Load into SQLite

Use either export **folders** (extraction runs automatically) or **pre-extracted JSON** files. The DB file (default `matchmate.db` in the current directory) and tables are created if missing.

```bash
# From folders (default user: diba-darooneh_1234, default DB: matchmate.db)
python scripts/load_to_db.py --chrome-dir "user-data/Chrome" --youtube-dir "user-data/YouTube and YouTube Music"

# Custom user ID and DB path
python scripts/load_to_db.py --user-id diba-darooneh_1234 --chrome-dir "user-data/Chrome" --youtube-dir "user-data/YouTube and YouTube Music" --db data/matchmate.db

# From pre-extracted JSON files
python scripts/load_to_db.py --chrome-json extracted_chrome.json --youtube-json extracted_youtube.json
```

Optional env: `SQLITE_DB` (path to SQLite file).

### Dry run (extract and write JSON, no DB)

```bash
python scripts/load_to_db.py --chrome-dir "user-data/Chrome" --youtube-dir "user-data/YouTube and YouTube Music" --dry-run
```

## Schema (Option A, SQLite)

- **users:** `id`, `user_id` (unique), `display_name`, `created_at`, `updated_at`
- **user_chrome_data:** `user_id` → `chrome_json` (TEXT), one row per user
- **user_youtube_data:** `user_id` → `youtube_json` (TEXT), one row per user

Schema file: `schema.sql` in project root (applied automatically by the loader when the DB is created).

## Stop words and compact JSON

- **`scripts/stop_words.py`** defines the shared stop-word list and `strip_stop_words()` used by the extractors and `build_compact_json.py`.
- **Compact JSON files** (stop-word-stripped, per user): `python scripts/build_compact_json.py --user-id USER_ID` → writes `compact_json/USER_ID.json`.
