# Steps to make the Gemini profile script functional

**Quick checklist:** Get API key → `pip install google-generativeai` → build compact (if needed) → set `GEMINI_API_KEY` → run `predict_profile_gemini.py --user-id <id>`.

---

## 1. Get a Gemini API key

1. Open [Google AI Studio](https://aistudio.google.com/).
2. Sign in with your Google account.
3. Click **Get API key** (or go to **API keys** in the menu).
4. Create an API key and copy it.

You will pass this key to the script via an environment variable (do **not** put it in code).

---

## 2. Install the Gemini SDK

From the project root:

```bash
pip install -r requirements.txt
```

Or only the Gemini dependency:

```bash
pip install google-genai
```
(We use the current `google-genai` package; the older `google-generativeai` is deprecated.)

---

## 3. Ensure compact profile exists for the user

The script needs compact text for each user (from Chrome + YouTube data). If you haven’t already:

```bash
python scripts/build_compact_profile.py --user-id diba-darooneh_1234
```

Use the same `--db` as in step 4 if your DB is not the default `matchmate.db`.

---

## 4. Run the prediction script

Set the API key and run:

**Windows (PowerShell):**

```powershell
$env:GEMINI_API_KEY = "your-api-key-here"
python scripts/predict_profile_gemini.py --user-id diba-darooneh_1234
```

**Windows (CMD):**

```cmd
set GEMINI_API_KEY=your-api-key-here
python scripts/predict_profile_gemini.py --user-id diba-darooneh_1234
```

**Linux / macOS:**

```bash
export GEMINI_API_KEY="your-api-key-here"
python scripts/predict_profile_gemini.py --user-id diba-darooneh_1234
```

Alternatively you can use `GOOGLE_API_KEY` instead of `GEMINI_API_KEY`.

---

## 5. What the script does

- Reads that user’s **compact text** from the table `user_compact_profile` (or builds it from Chrome/YouTube JSON and saves it).
- Sends the compact text to **Gemini** with a prompt that asks for a JSON with: age_range, location, job_occupation, education, hobbies, sports, entertainment_interests, music_taste, fashion, fitness_health, culture_ethnic_background, religious_beliefs, political_takes, languages_spoken, relationship_status, personality_type, communication_style, humor_style, values, lifestyle, social_energy, life_goals, dating_intentions, love_language, dealbreakers, favorite_cuisine, self_description.
- **Parses** the JSON from Gemini’s response.
- **Upserts** one row into **`user_gemini_profile`** (SQLite table).
- **Writes/overwrites** **`profile_predictions.csv`** with all rows from `user_gemini_profile` (so the CSV and table stay in sync).

---

## 6. Options

| Option | Description |
|--------|-------------|
| `--user-id USER_ID` | Run for this user only. |
| `--all-users` | Run for every user that has a row in `user_compact_profile`. |
| `--db PATH` | SQLite DB path (default: `matchmate.db`). |
| `--csv PATH` | Output CSV path (default: `profile_predictions.csv`). |
| `--model NAME` | Gemini model (default: `gemini-2.0-flash`). |
| `--csv-only` | Don’t call Gemini; only regenerate the CSV from the current `user_gemini_profile` table. |

**Examples:**

```bash
# One user, default DB and CSV
python scripts/predict_profile_gemini.py --user-id diba-darooneh_1234

# All users with compact profile
python scripts/predict_profile_gemini.py --all-users

# Custom DB and CSV path
python scripts/predict_profile_gemini.py --user-id diba-darooneh_1234 --db data/matchmate.db --csv out/profiles.csv

# Only refresh CSV from existing table
python scripts/predict_profile_gemini.py --csv-only
```

---

## 7. Where results are stored

- **SQLite:** Table **`user_gemini_profile`** (columns: `user_id`, `age_range`, `location`, `job_occupation`, `education`, `hobbies`, `sports`, `entertainment_interests`, `music_taste`, `fashion`, `fitness_health`, `culture_ethnic_background`, `religious_beliefs`, `political_takes`, `languages_spoken`, `relationship_status`, `personality_type`, `communication_style`, `humor_style`, `values`, `lifestyle`, `social_energy`, `life_goals`, `dating_intentions`, `love_language`, `dealbreakers`, `favorite_cuisine`, `self_description`, timestamps).
- **CSV:** File **`profile_predictions.csv`** (or the path you pass to `--csv`) with the same columns.

Both are updated every time you run the script for a user (or `--all-users`).
