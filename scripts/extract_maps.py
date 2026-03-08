"""
Extract Maps user-data (JSON/CSV under Maps folder) into one JSON.
Stop-word removal on text fields; dedup where applicable.
"""
import json
import csv
import argparse
from pathlib import Path
#test
from stop_words import strip_stop_words

MAPS_PLACES_LIMIT = 2000


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


def csv_to_list(path: Path) -> list:
    if not path.exists():
        return []
    rows = []
    with open(path, "r", encoding="utf-8", errors="replace") as f:
        try:
            for row in csv.DictReader(f):
                rows.append(dict(row))
        except Exception:
            pass
    return rows


def extract_labelled_places(maps_dir: Path) -> list:
    """Labelled places: GeoJSON FeatureCollection -> list of {name, address} with strip+dedup."""
    for j in maps_dir.rglob("Labelled places.json"):
        data = load_json_safe(j, {})
        features = data.get("features") or data.get("places") or []
        seen = set()
        out = []
        for f in features:
            props = f.get("properties") or f
            name_val = (props.get("name") or props.get("title") or "").strip()
            addr = (props.get("address") or "").strip()
            n_strip = strip_stop_words(name_val)
            a_strip = strip_stop_words(addr)
            key = (n_strip.lower() or "", a_strip.lower() or "")
            if key in seen:
                continue
            seen.add(key)
            out.append({"name": n_strip or name_val, "address": a_strip or addr})
            if len(out) >= MAPS_PLACES_LIMIT:
                return out
        if out:
            return out
    return []


def extract_maps(maps_dir: Path) -> dict:
    maps_dir = Path(maps_dir)
    out = {
        "labelled_places": extract_labelled_places(maps_dir),
        "commute_routes": [],
        "added_dishes": [],
        "other": {},
    }
    # Commute routes
    for p in maps_dir.rglob("Commute routes.json"):
        data = load_json_safe(p, {})
        trips = data.get("trips") or []
        out["commute_routes"] = trips[:500]
        break
    # Added dishes, products, activities
    for p in maps_dir.rglob("*.json"):
        rel = p.relative_to(maps_dir)
        srel = str(rel).replace("\\", "/")
        if "Labelled places" in srel or "Commute routes" in srel:
            continue
        data = load_json_safe(p, {})
        if not data:
            continue
        if "contributions" in data:
            out["added_dishes"] = data.get("contributions") or []
        elif "features" in data or "trips" in data:
            continue
        else:
            key = srel.replace(".json", "").replace("/", "_")
            out["other"][key] = data
    # CSVs
    for p in maps_dir.rglob("*.csv"):
        rel = p.relative_to(maps_dir)
        key = str(rel).replace("\\", "/").replace(".csv", "").replace("/", "_")
        out["other"][key] = csv_to_list(p)
    return out


def main():
    ap = argparse.ArgumentParser(description="Extract Maps folder to JSON")
    ap.add_argument("maps_dir", type=Path, help="Path to Maps export folder")
    ap.add_argument("-o", "--output", type=Path, help="Write JSON to file")
    args = ap.parse_args()
    data = extract_maps(args.maps_dir)
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        with open(args.output, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
    else:
        print(json.dumps(data, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
