"""
Generates a synthetic physical performance dataset for the blog series.

Based on published benchmarks from peer-reviewed sports science literature
on physical demands in professional football:
- Total distance: 9,500–12,500m (position-dependent)
- High-speed running (>19.8 km/h): 700–1,200m
- Sprint distance (>25.2 km/h): 150–550m
- Max speed: 28–36 km/h
- High accelerations (>3 m/s²): 15–40 per game

Position profiles follow Mohr et al. (2003), Bradley et al. (2009),
and Di Salvo et al. (2007).

Run this once to generate the CSV used by all notebooks in this series.
"""

import numpy as np
import pandas as pd
import os

np.random.seed(42)

POSITIONS = {
    'Goalkeeper': {
        'total_distance':   (5800,  700),
        'running':          (350,   100),
        'hsr':              (150,    60),
        'sprint':           (40,     30),
        'hi':               (190,    70),
        'max_speed':        (27.5,   2.0),
        'count_sprint':     (3,       3),
        'count_hsr':        (10,      6),
        'count_hi':         (13,      7),
        'med_acc':          (60,     20),
        'high_acc':         (12,      6),
        'med_dec':          (58,     20),
        'high_dec':         (10,      5),
        'mmin':             (62,      8),
    },
    'Center Back': {
        'total_distance':   (10200, 900),
        'running':          (750,   150),
        'hsr':              (350,   100),
        'sprint':           (80,     50),
        'hi':               (430,   120),
        'max_speed':        (30.5,   2.2),
        'count_sprint':     (6,       4),
        'count_hsr':        (22,      9),
        'count_hi':         (28,     11),
        'med_acc':          (110,    25),
        'high_acc':         (20,      8),
        'med_dec':          (105,    25),
        'high_dec':         (18,      7),
        'mmin':             (108,    10),
    },
    'Full Back': {
        'total_distance':   (11400, 900),
        'running':          (1050,  200),
        'hsr':              (650,   150),
        'sprint':           (220,   100),
        'hi':               (870,   200),
        'max_speed':        (32.5,   2.0),
        'count_sprint':     (16,      7),
        'count_hsr':        (42,     14),
        'count_hi':         (58,     18),
        'med_acc':          (140,    30),
        'high_acc':         (26,     10),
        'med_dec':          (130,    28),
        'high_dec':         (22,      9),
        'mmin':             (118,    10),
    },
    'Defensive Midfielder': {
        'total_distance':   (11800, 800),
        'running':          (900,   180),
        'hsr':              (500,   130),
        'sprint':           (130,    75),
        'hi':               (630,   175),
        'max_speed':        (31.0,   2.0),
        'count_sprint':     (10,      6),
        'count_hsr':        (33,     12),
        'count_hi':         (43,     15),
        'med_acc':          (155,    35),
        'high_acc':         (28,     10),
        'med_dec':          (148,    33),
        'high_dec':         (24,      9),
        'mmin':             (122,    10),
    },
    'Central Midfielder': {
        'total_distance':   (12100, 850),
        'running':          (1000,  200),
        'hsr':              (600,   150),
        'sprint':           (160,    85),
        'hi':               (760,   200),
        'max_speed':        (31.5,   2.2),
        'count_sprint':     (12,      6),
        'count_hsr':        (38,     13),
        'count_hi':         (50,     16),
        'med_acc':          (160,    35),
        'high_acc':         (30,     10),
        'med_dec':          (152,    32),
        'high_dec':         (26,      9),
        'mmin':             (124,    11),
    },
    'Wide Midfielder': {
        'total_distance':   (11600, 900),
        'running':          (1100,  220),
        'hsr':              (800,   180),
        'sprint':           (280,   110),
        'hi':               (1080,  240),
        'max_speed':        (33.0,   2.0),
        'count_sprint':     (20,      8),
        'count_hsr':        (50,     16),
        'count_hi':         (70,     20),
        'med_acc':          (150,    32),
        'high_acc':         (28,     10),
        'med_dec':          (140,    30),
        'high_dec':         (24,      9),
        'mmin':             (120,    11),
    },
    'Attacking Midfielder': {
        'total_distance':   (11000, 900),
        'running':          (950,   200),
        'hsr':              (700,   170),
        'sprint':           (240,   100),
        'hi':               (940,   230),
        'max_speed':        (32.5,   2.2),
        'count_sprint':     (18,      7),
        'count_hsr':        (45,     15),
        'count_hi':         (63,     19),
        'med_acc':          (145,    30),
        'high_acc':         (27,     10),
        'med_dec':          (138,    28),
        'high_dec':         (23,      9),
        'mmin':             (115,    11),
    },
    'Striker': {
        'total_distance':   (10500, 950),
        'running':          (850,   190),
        'hsr':              (750,   180),
        'sprint':           (320,   120),
        'hi':               (1070,  250),
        'max_speed':        (33.5,   2.2),
        'count_sprint':     (22,      8),
        'count_hsr':        (47,     16),
        'count_hi':         (69,     20),
        'med_acc':          (130,    28),
        'high_acc':         (25,      9),
        'med_dec':          (125,    27),
        'high_dec':         (22,      8),
        'mmin':             (110,    12),
    },
}

TEAMS = [
    'Arsenal', 'Aston Villa', 'Bournemouth', 'Brentford', 'Brighton',
    'Chelsea', 'Crystal Palace', 'Everton', 'Fulham', 'Ipswich Town',
    'Leicester City', 'Liverpool', 'Manchester City', 'Manchester United',
    'Newcastle United', 'Nottingham Forest', 'Southampton', 'Tottenham Hotspur',
    'West Ham United', 'Wolverhampton Wanderers'
]

SQUAD_POSITIONS = (
    ['Goalkeeper'] * 1 +
    ['Center Back'] * 2 +
    ['Full Back'] * 2 +
    ['Defensive Midfielder'] * 1 +
    ['Central Midfielder'] * 2 +
    ['Wide Midfielder'] * 2 +
    ['Attacking Midfielder'] * 1 +
    ['Striker'] * 2
)  # 16 outfield starters + GK (but we model 14 outfield + 1 GK per game)


def sample_player(pos, minutes=90):
    p = POSITIONS[pos]
    scale = minutes / 90.0

    def norm(key, low=0):
        val = np.random.normal(p[key][0], p[key][1]) * scale
        return max(low, round(val, 1))

    total  = norm('total_distance', 100)
    run    = min(norm('running', 0), total * 0.18)
    hsr    = min(norm('hsr', 0), run * 1.5)
    sprint = min(norm('sprint', 0), hsr * 0.9)
    hi     = hsr + sprint * 0.3

    return {
        'position':                       pos,
        'minutes_played':                 minutes,
        'total_distance':                 total,
        'mmin':                           round(total / minutes, 1) if minutes > 0 else 0,
        'running_distance':               round(run, 1),
        'hsr_distance':                   round(hsr, 1),
        'sprinting_distance':             round(sprint, 1),
        'hi_distance':                    round(hi, 1),
        'count_hsr':                      max(0, int(np.random.normal(p['count_hsr'][0], p['count_hsr'][1]) * scale)),
        'count_sprint':                   max(0, int(np.random.normal(p['count_sprint'][0], p['count_sprint'][1]) * scale)),
        'count_hi':                       max(0, int(np.random.normal(p['count_hi'][0], p['count_hi'][1]) * scale)),
        'count_medium_acceleration':      max(0, int(np.random.normal(p['med_acc'][0], p['med_acc'][1]) * scale)),
        'count_high_acceleration':        max(0, int(np.random.normal(p['high_acc'][0], p['high_acc'][1]) * scale)),
        'count_medium_deceleration':      max(0, int(np.random.normal(p['med_dec'][0], p['med_dec'][1]) * scale)),
        'count_high_deceleration':        max(0, int(np.random.normal(p['high_dec'][0], p['high_dec'][1]) * scale)),
        'max_speed':                      round(max(20, np.random.normal(p['max_speed'][0], p['max_speed'][1])), 2),
    }


def generate_season(n_matches=380):
    rows = []
    match_id = 1000

    matchups = []
    for i, home in enumerate(TEAMS):
        for away in TEAMS:
            if home != away:
                matchups.append((home, away))

    np.random.shuffle(matchups)
    matchups = matchups[:n_matches]

    player_counter = 1

    team_squads = {}
    for team in TEAMS:
        squad = []
        for pos in SQUAD_POSITIONS:
            squad.append({
                'player_id':   player_counter,
                'player_name': f'Player {player_counter}',
                'position':    pos,
                'team':        team,
            })
            player_counter += 1
        team_squads[team] = squad

    for home, away in matchups:
        for team in [home, away]:
            squad = team_squads[team]
            starters = squad[:15]
            subs = squad[15:]
            for p in starters:
                minutes = 90 if np.random.random() > 0.25 else int(np.random.uniform(55, 85))
                row = sample_player(p['position'], minutes)
                row.update({
                    'match_id':    match_id,
                    'team':        team,
                    'player_id':   p['player_id'],
                    'player_name': p['player_name'],
                    'opponent':    away if team == home else home,
                    'is_home':     team == home,
                })
                rows.append(row)
            if np.random.random() > 0.1:
                n_subs = np.random.choice([1, 2, 3], p=[0.1, 0.3, 0.6])
                for p in subs[:n_subs]:
                    minutes = int(np.random.uniform(15, 45))
                    row = sample_player(p['position'], minutes)
                    row.update({
                        'match_id':    match_id,
                        'team':        team,
                        'player_id':   p['player_id'],
                        'player_name': p['player_name'],
                        'opponent':    away if team == home else home,
                        'is_home':     team == home,
                    })
                    rows.append(row)
        match_id += 1

    df = pd.DataFrame(rows)
    col_order = [
        'match_id', 'team', 'opponent', 'is_home',
        'player_id', 'player_name', 'position', 'minutes_played',
        'total_distance', 'mmin', 'running_distance',
        'hsr_distance', 'sprinting_distance', 'hi_distance',
        'count_hsr', 'count_sprint', 'count_hi',
        'count_medium_acceleration', 'count_high_acceleration',
        'count_medium_deceleration', 'count_high_deceleration',
        'max_speed',
    ]
    return df[col_order]


if __name__ == '__main__':
    out = os.path.join(os.path.dirname(__file__), 'physical_data_synthetic.csv')
    df = generate_season(n_matches=380)
    df.to_csv(out, index=False)
    print(f'Generated {len(df)} rows across {df["match_id"].nunique()} matches')
    print(f'Saved to {out}')
    print()
    print(df.groupby('position')[['total_distance', 'sprinting_distance', 'max_speed']].mean().round(1))
