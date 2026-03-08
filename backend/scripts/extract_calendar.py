"""
Extract Calendar user-data (ICS) into JSON.
Stop-word removal on summary/location, then last CALENDAR_LIMIT unique (newest-first).
"""
import json
import argparse
import re
from pathlib import Path

from stop_words import strip_stop_words

CALENDAR_LIMIT = 5000


def _unfold_ics(lines: list) -> list:
    """Unfold long lines (lines starting with space belong to previous line)."""
    out = []
    for line in lines:
        if line.startswith((" ", "\t")) and out:
            out[-1] = out[-1].rstrip("\r\n") + line.strip()
        else:
            out.append(line)
    return out


def parse_ics(ics_path: Path) -> list:
    """Parse ICS file; return list of {summary, location, dtstart, dtend}."""
    if not ics_path.exists():
        return []
    with open(ics_path, "r", encoding="utf-8", errors="replace") as f:
        lines = _unfold_ics(f.readlines())
    events = []
    current = {}
    for line in lines:
        line = line.rstrip("\r\n")
        if line == "BEGIN:VEVENT":
            current = {}
        elif line == "END:VEVENT":
            if current:
                events.append(current)
            current = {}
        elif line.startswith("SUMMARY:"):
            current["summary"] = line[7:].replace("\\n", " ").replace("\\,", ",").strip()
        elif line.startswith("LOCATION:"):
            current["location"] = line[9:].replace("\\n", " ").replace("\\,", ",").strip()
        elif line.startswith("DTSTART"):
            # DTSTART;VALUE=DATE:20041006 or DTSTART:20210617T150000Z
            val = line.split(":", 1)[-1].strip()
            current["dtstart"] = val
        elif line.startswith("DTEND"):
            val = line.split(":", 1)[-1].strip()
            current["dtend"] = val
    return events


def extract_calendar(calendar_dir: Path) -> dict:
    calendar_dir = Path(calendar_dir)
    all_events = []
    for ics in calendar_dir.glob("*.ics"):
        all_events.extend(parse_ics(ics))
    # Sort by dtstart descending (newest first)
    all_events.sort(key=lambda e: e.get("dtstart", ""), reverse=True)
    # Dedup by stripped summary+location; keep first CALENDAR_LIMIT unique
    seen = set()
    result = []
    for ev in all_events:
        summary = (ev.get("summary") or "").strip()
        location = (ev.get("location") or "").strip()
        s_strip = strip_stop_words(summary)
        l_strip = strip_stop_words(location)
        key = (s_strip.lower() or "", l_strip.lower() or "")
        if key in seen:
            continue
        seen.add(key)
        result.append({
            "summary": s_strip or summary,
            "location": l_strip or location,
            "dtstart": ev.get("dtstart"),
            "dtend": ev.get("dtend"),
        })
        if len(result) >= CALENDAR_LIMIT:
            break
    return {"events": result}


def main():
    ap = argparse.ArgumentParser(description="Extract Calendar (ICS) to JSON")
    ap.add_argument("calendar_dir", type=Path, help="Path to Calendar export folder")
    ap.add_argument("-o", "--output", type=Path, help="Write JSON to file")
    args = ap.parse_args()
    out = extract_calendar(args.calendar_dir)
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        with open(args.output, "w", encoding="utf-8") as f:
            json.dump(out, f, indent=2, ensure_ascii=False)
    else:
        print(json.dumps(out, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
