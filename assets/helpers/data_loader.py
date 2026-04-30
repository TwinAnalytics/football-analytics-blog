"""
Shared data loading utilities used across all blog notebooks.
"""
import json
import os
import pandas as pd

DATA_DIR = "/Users/stefanhofmann/Documents/Bewerbung/Interviews/Hudl/statsbomb_explorer/open-data/data"


def load_competitions():
    with open(os.path.join(DATA_DIR, "competitions.json"), encoding="utf-8") as f:
        return pd.DataFrame(json.load(f))


def load_matches(competition_id, season_id):
    path = os.path.join(DATA_DIR, "matches", str(competition_id), f"{season_id}.json")
    with open(path, encoding="utf-8") as f:
        return pd.DataFrame(json.load(f))


def load_events(match_id):
    path = os.path.join(DATA_DIR, "events", f"{match_id}.json")
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def load_360(match_id):
    path = os.path.join(DATA_DIR, "three-sixty", f"{match_id}.json")
    if not os.path.exists(path):
        return None
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def flatten_events(raw):
    rows = []
    for e in raw:
        row = {
            "index":        e.get("index"),
            "period":       e.get("period"),
            "minute":       e.get("minute"),
            "second":       e.get("second"),
            "type":         e.get("type", {}).get("name"),
            "team":         e.get("team", {}).get("name"),
            "player":       e.get("player", {}).get("name"),
            "position":     e.get("position", {}).get("name"),
            "play_pattern": e.get("play_pattern", {}).get("name"),
            "event_id":     e.get("id"),
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


def get_competition_id(name, gender="male"):
    """Helper to quickly get competition_id and available seasons."""
    comps = load_competitions()
    filtered = comps[(comps["competition_name"] == name) & (comps["competition_gender"] == gender)]
    return filtered[["competition_id", "season_id", "season_name"]].sort_values("season_name")


def load_all_matches_for_season(competition_name, season_name, gender="male"):
    """Load all events for every match in a season. Returns dict {match_id: events_df}."""
    comps = load_competitions()
    row = comps[
        (comps["competition_name"] == competition_name) &
        (comps["season_name"] == season_name) &
        (comps["competition_gender"] == gender)
    ].iloc[0]
    matches = load_matches(row["competition_id"], row["season_id"])
    return matches
