-- MatchMate: SQLite schema (Option A)
-- Users and their Chrome/YouTube export data linked by user_id

CREATE TABLE IF NOT EXISTS users (
    id           INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id      TEXT NOT NULL UNIQUE,
    display_name TEXT,
    created_at   TEXT DEFAULT (datetime('now')),
    updated_at   TEXT DEFAULT (datetime('now'))
);

CREATE TABLE IF NOT EXISTS user_chrome_data (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id     TEXT NOT NULL UNIQUE REFERENCES users(user_id) ON DELETE CASCADE,
    chrome_json TEXT NOT NULL,
    created_at  TEXT DEFAULT (datetime('now')),
    updated_at  TEXT DEFAULT (datetime('now'))
);

CREATE TABLE IF NOT EXISTS user_youtube_data (
    id           INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id      TEXT NOT NULL UNIQUE REFERENCES users(user_id) ON DELETE CASCADE,
    youtube_json TEXT NOT NULL,
    created_at   TEXT DEFAULT (datetime('now')),
    updated_at   TEXT DEFAULT (datetime('now'))
);

CREATE INDEX IF NOT EXISTS idx_user_chrome_data_user_id ON user_chrome_data(user_id);
CREATE INDEX IF NOT EXISTS idx_user_youtube_data_user_id ON user_youtube_data(user_id);

CREATE TABLE IF NOT EXISTS user_calendar_data (
    id            INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id       TEXT NOT NULL UNIQUE REFERENCES users(user_id) ON DELETE CASCADE,
    calendar_json TEXT NOT NULL,
    created_at    TEXT DEFAULT (datetime('now')),
    updated_at    TEXT DEFAULT (datetime('now'))
);
CREATE INDEX IF NOT EXISTS idx_user_calendar_data_user_id ON user_calendar_data(user_id);

CREATE TABLE IF NOT EXISTS user_maps_data (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id     TEXT NOT NULL UNIQUE REFERENCES users(user_id) ON DELETE CASCADE,
    maps_json   TEXT NOT NULL,
    created_at  TEXT DEFAULT (datetime('now')),
    updated_at  TEXT DEFAULT (datetime('now'))
);
CREATE INDEX IF NOT EXISTS idx_user_maps_data_user_id ON user_maps_data(user_id);

-- Compact text extracted from Chrome + YouTube + Calendar + Maps for sending to Gemini (one row per user)
CREATE TABLE IF NOT EXISTS user_compact_profile (
    id           INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id      TEXT NOT NULL UNIQUE REFERENCES users(user_id) ON DELETE CASCADE,
    compact_text TEXT NOT NULL,
    created_at   TEXT DEFAULT (datetime('now')),
    updated_at   TEXT DEFAULT (datetime('now'))
);
CREATE INDEX IF NOT EXISTS idx_user_compact_profile_user_id ON user_compact_profile(user_id);

-- Predictions returned from Gemini (one row per user)
DROP TABLE IF EXISTS user_gemini_profile;
CREATE TABLE user_gemini_profile (
    id                      INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id                 TEXT NOT NULL UNIQUE REFERENCES users(user_id) ON DELETE CASCADE,
    age_range               TEXT,
    location                TEXT,
    job_occupation          TEXT,
    education               TEXT,
    hobbies                 TEXT,
    sports                  TEXT,
    entertainment_interests TEXT,
    music_taste             TEXT,
    fashion                 TEXT,
    fitness_health          TEXT,
    culture_ethnic_background TEXT,
    religious_beliefs       TEXT,
    political_takes         TEXT,
    languages_spoken        TEXT,
    relationship_status    TEXT,
    personality_type        TEXT,
    communication_style     TEXT,
    humor_style             TEXT,
    "values"                TEXT,
    lifestyle               TEXT,
    social_energy           TEXT,
    life_goals              TEXT,
    dating_intentions       TEXT,
    love_language           TEXT,
    dealbreakers            TEXT,
    favorite_cuisine        TEXT,
    self_description        TEXT,
    created_at              TEXT DEFAULT (datetime('now')),
    updated_at              TEXT DEFAULT (datetime('now'))
);
CREATE INDEX IF NOT EXISTS idx_user_gemini_profile_user_id ON user_gemini_profile(user_id);
