"""
Convert Statsbomb event JSON files to CSV on demand.
Usage:
    python to_csv.py --match_id 3895302
    python to_csv.py --competition "1. Bundesliga" --season "2023/2024"
    python to_csv.py --all    # converts every match (takes a while, ~20GB)
"""
import json
import os
import sys
import argparse
import pandas as pd

DATA_DIR = "/Users/stefanhofmann/Documents/Bewerbung/Interviews/Hudl/statsbomb_explorer/open-data/data"
CSV_DIR  = "/Users/stefanhofmann/Documents/Bewerbung/Portfolio/Blog/assets/csv/events"


def flatten_events(raw, match_id=None):
    rows = []
    for e in raw:
        row = {
            "match_id":     match_id,
            "event_id":     e.get("id"),
            "index":        e.get("index"),
            "period":       e.get("period"),
            "minute":       e.get("minute"),
            "second":       e.get("second"),
            "type":         e.get("type", {}).get("name"),
            "team":         e.get("team", {}).get("name"),
            "player":       e.get("player", {}).get("name"),
            "position":     e.get("position", {}).get("name"),
            "play_pattern": e.get("play_pattern", {}).get("name"),
        }
        loc = e.get("location")
        if loc:
            row["x"], row["y"] = loc[0], loc[1]
        for key in ["pass", "shot", "carry", "dribble", "pressure",
                    "ball_receipt", "interception", "duel", "clearance", "block"]:
            sub = e.get(key, {})
            if sub:
                for k, v in sub.items():
                    col = f"{key}_{k}"
                    if isinstance(v, dict):
                        row[col] = v.get("name")
                    elif isinstance(v, list):
                        row[col] = str(v)
                    else:
                        row[col] = v
        rows.append(row)
    return pd.DataFrame(rows)


def convert_match(match_id, out_dir=CSV_DIR):
    os.makedirs(out_dir, exist_ok=True)
    path = os.path.join(DATA_DIR, "events", f"{match_id}.json")
    if not os.path.exists(path):
        print(f"No events file for match_id {match_id}")
        return
    with open(path, encoding="utf-8") as f:
        raw = json.load(f)
    df = flatten_events(raw, match_id=match_id)
    out = os.path.join(out_dir, f"{match_id}.csv")
    df.to_csv(out, index=False)
    print(f"Saved {len(df)} events -> {out}")
    return df


def convert_season(competition_name, season_name, out_dir=CSV_DIR):
    matches_path = os.path.join(
        os.path.dirname(__file__), "..", "csv", "all_matches.csv"
    )
    all_matches = pd.read_csv(matches_path)
    season_matches = all_matches[
        (all_matches["competition"] == competition_name) &
        (all_matches["season"] == season_name)
    ]
    if season_matches.empty:
        print(f"No matches found for {competition_name} {season_name}")
        return
    print(f"Converting {len(season_matches)} matches for {competition_name} {season_name}...")
    for _, m in season_matches.iterrows():
        convert_match(int(m["match_id"]), out_dir=out_dir)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--match_id", type=int)
    parser.add_argument("--competition", type=str)
    parser.add_argument("--season", type=str)
    parser.add_argument("--all", action="store_true")
    args = parser.parse_args()

    if args.match_id:
        convert_match(args.match_id)
    elif args.competition and args.season:
        convert_season(args.competition, args.season)
    elif args.all:
        events_dir = os.path.join(DATA_DIR, "events")
        for fname in sorted(os.listdir(events_dir)):
            mid = int(fname.replace(".json", ""))
            convert_match(mid)
    else:
        parser.print_help()
