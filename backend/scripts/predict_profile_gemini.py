"""
Call Gemini with a user's compact profile, parse the JSON response,
upsert into user_gemini_profile, and refresh the predictions CSV.

Requires: GEMINI_API_KEY or GOOGLE_API_KEY (in env or in .env file).
"""
import csv
import json
import os
import re
import sqlite3
import argparse
from pathlib import Path
from typing import Optional

# Load .env from script dir or project root so GEMINI_API_KEY is set
_scripts_dir = Path(__file__).resolve().parent
_project_root = _scripts_dir.parent
for _env_path in (_scripts_dir / ".env", _project_root / ".env"):
    if _env_path.exists():
        try:
            from dotenv import load_dotenv
            load_dotenv(_env_path)
        except ImportError:
            pass
        break
if str(_scripts_dir) not in __import__("sys").path:
    __import__("sys").path.insert(0, str(_scripts_dir))

from build_compact_profile import (
    get_connection,
    init_schema,
    get_user_jsons,
    build_compact_from_jsons,
    upsert_compact_profile,
)

DEFAULT_DB_PATH = "matchmate.db"
DEFAULT_CSV_PATH = "profile_predictions.csv"

# CSV/DB columns (user_id added separately); order matches schema and CSV header
GEMINI_PROFILE_KEYS = [
    "age_range",
    "location",
    "job_occupation",
    "education",
    "hobbies",
    "sports",
    "entertainment_interests",
    "music_taste",
    "fashion",
    "fitness_health",
    "culture_ethnic_background",
    "religious_beliefs",
    "political_takes",
    "languages_spoken",
    "relationship_status",
    "personality_type",
    "communication_style",
    "humor_style",
    "values",
    "lifestyle",
    "social_energy",
    "life_goals",
    "dating_intentions",
    "love_language",
    "dealbreakers",
    "favorite_cuisine",
    "self_description",
]

SYSTEM_PROMPT = """You are analyzing anonymized browsing and YouTube activity to infer attributes of one person for a dating/profile context. Infer broad patterns from the full picture. Use "Unclear" only when there is no relevant signal. Prefer short phrases or keywords.

Return ONLY a valid JSON object with exactly these keys (no other text, no markdown):
- age_range
- location
- job_occupation
- education
- hobbies
- sports
- entertainment_interests
- music_taste
- fashion
- fitness_health
- culture_ethnic_background
- religious_beliefs
- political_takes
- languages_spoken
- relationship_status
- personality_type
- communication_style
- humor_style
- values
- lifestyle
- social_energy
- life_goals
- dating_intentions
- love_language
- dealbreakers
- favorite_cuisine
- self_description"""


def get_compact_text(conn: sqlite3.Connection, user_id: str, ensure_saved: bool = True) -> Optional[str]:
    """Get compact text from user_compact_profile, or build from chrome/youtube JSON and optionally save."""
    row = conn.execute(
        "SELECT compact_text FROM user_compact_profile WHERE user_id = ?",
        (user_id,),
    ).fetchone()
    if row:
        return row[0]
    chrome_data, youtube_data = get_user_jsons(conn, user_id)
    if not chrome_data and not youtube_data:
        return None
    compact = build_compact_from_jsons(chrome_data or {}, youtube_data or {})
    if ensure_saved:
        upsert_compact_profile(conn, user_id, compact)
    return compact


def call_gemini(compact_text: str, api_key: str, model: str = "gemini-2.0-flash") -> str:
    try:
        from google import genai
    except ImportError:
        raise SystemExit("Install the Gemini SDK: pip install google-genai")

    client = genai.Client(api_key=api_key)
    contents = SYSTEM_PROMPT + "\n\n--- Activity data ---\n\n" + compact_text[:120000]
    response = client.models.generate_content(model=model, contents=contents)
    if not response or not getattr(response, "text", None):
        raise RuntimeError("Empty response from Gemini")
    return response.text.strip()


def parse_gemini_json(raw: str) -> dict:
    """Extract JSON from Gemini response (strip markdown code blocks if present)."""
    raw = raw.strip()
    # Remove ```json ... ``` or ``` ... ```
    m = re.search(r"```(?:json)?\s*([\s\S]*?)\s*```", raw)
    if m:
        raw = m.group(1).strip()
    return json.loads(raw)


def normalize_row(user_id: str, data: dict) -> dict:
    """Map Gemini JSON to DB/CSV row (all values strings)."""
    row = {"user_id": user_id}
    for k in GEMINI_PROFILE_KEYS:
        v = data.get(k)
        if v is None:
            row[k] = ""
        elif isinstance(v, list):
            row[k] = "; ".join(str(x) for x in v)
        else:
            row[k] = str(v).strip()
    return row


def _sql_col(k: str) -> str:
    return f'"{k}"' if k == "values" else k


def upsert_gemini_profile(conn: sqlite3.Connection, user_id: str, row: dict):
    cols = "user_id, " + ", ".join(_sql_col(k) for k in GEMINI_PROFILE_KEYS) + ", updated_at"
    n = len(GEMINI_PROFILE_KEYS)
    placeholders = ", ".join("?" for _ in range(n + 1)) + ", datetime('now')"
    set_clause = ", ".join(f"{_sql_col(k)} = excluded.{_sql_col(k)}" for k in GEMINI_PROFILE_KEYS) + ", updated_at = datetime('now')"
    values = [row.get("user_id", user_id)] + [row.get(k, "") for k in GEMINI_PROFILE_KEYS]
    conn.execute(
        f"INSERT INTO user_gemini_profile ({cols}) VALUES ({placeholders}) ON CONFLICT (user_id) DO UPDATE SET {set_clause}",
        values,
    )
    conn.commit()


def write_csv_from_table(conn: sqlite3.Connection, csv_path: Path):
    """Write full CSV from user_gemini_profile (all users)."""
    cols = ["user_id"] + GEMINI_PROFILE_KEYS
    select_cols = ", ".join(_sql_col(c) for c in cols)
    rows = conn.execute(
        f"SELECT {select_cols} FROM user_gemini_profile ORDER BY user_id"
    ).fetchall()
    csv_path = Path(csv_path)
    csv_path.parent.mkdir(parents=True, exist_ok=True)
    with open(csv_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=cols)
        writer.writeheader()
        for r in rows:
            writer.writerow(dict(zip(cols, r)))
    print("CSV written:", csv_path.resolve())


def run_for_user(
    conn: sqlite3.Connection,
    user_id: str,
    api_key: str,
    model: str,
) -> bool:
    compact = get_compact_text(conn, user_id)
    if not compact:
        print("No compact profile for", user_id, "- run build_compact_profile.py first or ensure chrome/youtube data exists.")
        return False
    print("Calling Gemini for", user_id, "...")
    raw = call_gemini(compact, api_key, model=model)
    data = parse_gemini_json(raw)
    row = normalize_row(user_id, data)
    upsert_gemini_profile(conn, user_id, row)
    print("Saved to user_gemini_profile for", user_id)
    return True


def main():
    ap = argparse.ArgumentParser(
        description="Run Gemini on compact profile, save to user_gemini_profile and CSV"
    )
    ap.add_argument("--user-id", help="User ID (e.g. diba-darooneh_1234)")
    ap.add_argument("--all-users", action="store_true", help="Run for all users that have compact_profile")
    ap.add_argument("--db", default=os.environ.get("SQLITE_DB", DEFAULT_DB_PATH), help="SQLite DB path")
    ap.add_argument("--csv", default=DEFAULT_CSV_PATH, help="Output CSV path (default: profile_predictions.csv)")
    ap.add_argument("--model", default="gemini-2.0-flash", help="Gemini model name (e.g. gemini-2.0-flash, gemini-2.5-flash)")
    ap.add_argument("--csv-only", action="store_true", help="Only refresh CSV from table (no API call)")
    args = ap.parse_args()

    api_key = os.environ.get("GEMINI_API_KEY") or os.environ.get("GOOGLE_API_KEY")
    if not args.csv_only and not api_key:
        print("Set GEMINI_API_KEY or GOOGLE_API_KEY in the environment.")
        return 1

    conn = get_connection(args.db)
    try:
        init_schema(conn)
        if args.csv_only:
            write_csv_from_table(conn, args.csv)
            return 0
        if args.all_users:
            rows = conn.execute(
                "SELECT user_id FROM user_compact_profile ORDER BY user_id"
            ).fetchall()
            user_ids = [r[0] for r in rows]
            if not user_ids:
                print("No users with compact profile. Run build_compact_profile.py first.")
                return 1
        elif args.user_id:
            user_ids = [args.user_id]
        else:
            print("Provide --user-id USER_ID or --all-users")
            return 1
        for uid in user_ids:
            run_for_user(conn, uid, api_key, args.model)
        write_csv_from_table(conn, args.csv)
    finally:
        conn.close()
    return 0


if __name__ == "__main__":
    exit(main() or 0)
