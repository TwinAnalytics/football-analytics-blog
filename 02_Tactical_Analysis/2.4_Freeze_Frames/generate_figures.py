import sys
import os
import json
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import numpy as np

sys.path.append('/Users/stefanhofmann/Documents/Bewerbung/Portfolio/Blog/assets/helpers')
from data_loader import load_competitions, load_matches, load_events, flatten_events
from pitch import draw_pitch

DATA_DIR = '/Users/stefanhofmann/Documents/Bewerbung/Interviews/Hudl/statsbomb_explorer/open-data/data'
FIGURES = 'figures'
os.makedirs(FIGURES, exist_ok=True)

comp_df = load_competitions()
row = comp_df[(comp_df['competition_name'] == '1. Bundesliga') & (comp_df['season_name'] == '2023/2024')].iloc[0]
matches = load_matches(row['competition_id'], row['season_id'])
print(f'Bundesliga 2023/24: {len(matches)} matches')

three_sixty_dir = os.path.join(DATA_DIR, 'three-sixty')
available_360 = {int(f.replace('.json', '')) for f in os.listdir(three_sixty_dir) if f.endswith('.json')}
match_ids_with_360 = [mid for mid in matches['match_id'] if mid in available_360]
print(f'Matches with 360°: {len(match_ids_with_360)}')

MATCH_ID = match_ids_with_360[0]
match_row = matches[matches['match_id'] == MATCH_ID].iloc[0]
home = match_row['home_team']
away = match_row['away_team']
home_team = home['home_team_name'] if isinstance(home, dict) else home
away_team = away['away_team_name'] if isinstance(away, dict) else away

raw = load_events(MATCH_ID)
df = flatten_events(raw)

with open(os.path.join(three_sixty_dir, f'{MATCH_ID}.json')) as f:
    frames = json.load(f)

frames_dict = {fr['event_uuid']: fr for fr in frames}
print(f'Frame entries: {len(frames_dict)}')

def outcome_is_goal(o):
    if isinstance(o, dict):
        return o.get('name', '') == 'Goal'
    return str(o) == 'Goal'

# Find a shot with freeze frame
shots = df[df['type'] == 'Shot'].copy()
goal_with_frame = None
goals = shots[shots['shot_outcome'].apply(outcome_is_goal)]
for _, g in goals.iterrows():
    eid = g.get('event_id')
    if eid in frames_dict:
        goal_with_frame = (g, frames_dict[eid])
        break

if goal_with_frame is None:
    for _, s in shots.iterrows():
        eid = s.get('event_id')
        if eid in frames_dict:
            goal_with_frame = (s, frames_dict[eid])
            break

if goal_with_frame:
    shot_event, frame = goal_with_frame
    freeze = frame.get('freeze_frame', [])

    fig, ax = plt.subplots(figsize=(14, 9))
    fig.patch.set_facecolor('#0D1117')
    draw_pitch(ax, color='#0D1117', line_color='#21262D')

    sx, sy = shot_event.get('x', 0), shot_event.get('y', 0)

    for player in freeze:
        loc = player.get('location', [0, 0])
        px, py = loc[0], loc[1]
        is_teammate = player.get('teammate', False)
        pos = player.get('position', {})
        is_keeper = player.get('keeper', False)
        color = '#eab308' if is_keeper else ('#00B8A9' if is_teammate else '#a855f7')
        size = 200 if is_keeper else 150
        ax.scatter(px, py, s=size, color=color, edgecolors='white', linewidths=1.5, zorder=4)

    ax.scatter(sx, sy, s=300, color='white', edgecolors='#00B8A9', linewidths=3, zorder=5, marker='*')
    ax.plot([sx, 120], [sy, 40], color='white', linewidth=0.8, linestyle='--', alpha=0.4)

    outcome = shot_event.get('shot_outcome', {})
    outcome_name = outcome.get('name', '') if isinstance(outcome, dict) else str(outcome)
    xg_val = shot_event.get('shot_statsbomb_xg', 0) or 0

    legend_elements = [
        mpatches.Patch(color='#00B8A9', label='Attacking team'),
        mpatches.Patch(color='#a855f7', label='Defending team'),
        mpatches.Patch(color='#eab308', label='Goalkeeper'),
        plt.scatter([], [], marker='*', c='white', s=200, label=f'Shooter (xG={xg_val:.2f})'),
    ]
    ax.legend(handles=legend_elements, facecolor='#161B22', edgecolor='#21262D', labelcolor='#F9FAFB',
              loc='upper left', fontsize=9)
    ax.set_title(f'Freeze Frame — {outcome_name} | {home_team.split()[-1]} vs {away_team.split()[-1]}',
                 color='#F9FAFB', fontweight='bold', fontsize=13)
    plt.tight_layout()
    plt.savefig(f'{FIGURES}/freeze_frame_shot.png', dpi=150, bbox_inches='tight', facecolor='#0D1117')
    plt.close()
    print('Saved freeze_frame_shot.png')
else:
    print('No shot with frame found')

# ── Figure 2: Defenders between shooter and goal (aggregate all 360° matches) ──
defender_counts = []
for match_id in match_ids_with_360:
    try:
        raw2 = load_events(match_id)
        df2 = flatten_events(raw2)
        with open(os.path.join(three_sixty_dir, f'{match_id}.json')) as f2:
            frames2 = json.load(f2)
        fd2 = {fr['event_uuid']: fr for fr in frames2}

        for _, shot in df2[df2['type'] == 'Shot'].iterrows():
            eid = shot.get('event_id')
            if eid not in fd2:
                continue
            ff = fd2[eid].get('freeze_frame', [])
            sx = shot.get('x', 0)
            n_def = sum(
                1 for p in ff
                if not p.get('teammate', True)
                and not (isinstance(p.get('position'), dict) and p['position'].get('name') == 'Goalkeeper')
                and p.get('location', [0])[0] > sx
            )
            defender_counts.append(n_def)
    except Exception:
        continue

if defender_counts:
    fig2, ax2 = plt.subplots(figsize=(8, 5))
    fig2.patch.set_facecolor('#0D1117')
    ax2.set_facecolor('#0D1117')
    counts_series = pd.Series(defender_counts).value_counts().sort_index()
    ax2.bar(counts_series.index, counts_series.values, color='#00B8A9', alpha=0.85, edgecolor='#0D1117')
    ax2.set_xlabel('Defenders between Shooter and Goal', color='#94A3B8', fontsize=11)
    ax2.set_ylabel('Number of Shots', color='#94A3B8', fontsize=11)
    ax2.set_title('Defensive Cover at Time of Shot — Bundesliga 2023/24', color='#F9FAFB', fontweight='bold', fontsize=13)
    ax2.tick_params(colors='#94A3B8')
    ax2.spines[:].set_color('#21262D')
    plt.tight_layout()
    plt.savefig(f'{FIGURES}/defenders_in_front.png', dpi=150, bbox_inches='tight', facecolor='#0D1117')
    plt.close()
    print('Saved defenders_in_front.png')

print('All 2.4 figures done.')
