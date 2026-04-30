import sys
import os
import json
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.patches import Polygon
from matplotlib.collections import PatchCollection
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

three_sixty_dir = os.path.join(DATA_DIR, 'three-sixty')
available_360 = {int(f.replace('.json', '')) for f in os.listdir(three_sixty_dir) if f.endswith('.json')}
match_ids_with_360 = [mid for mid in matches['match_id'] if mid in available_360]
print(f'Matches with 360°: {len(match_ids_with_360)}')

# Use first match with 360° data
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

# Find a pass with freeze frame + visible area
passes = df[df['type'] == 'Pass'].copy()
chosen = None
for _, p in passes.iterrows():
    eid = p.get('event_id')
    if eid in frames_dict:
        fr = frames_dict[eid]
        if fr.get('visible_area') and fr.get('freeze_frame'):
            chosen = (p, fr)
            break

if chosen is None:
    # Just use any event with freeze frame
    for _, ev in df.iterrows():
        eid = ev.get('event_id')
        if eid in frames_dict:
            fr = frames_dict[eid]
            if fr.get('visible_area') and len(fr.get('freeze_frame', [])) > 3:
                chosen = (ev, fr)
                break

if chosen:
    event, frame = chosen
    freeze = frame.get('freeze_frame', [])
    visible_area = frame.get('visible_area', [])

    # ── Figure 1: Single frame with visible area ─────────────────────────────
    fig, ax = plt.subplots(figsize=(14, 9))
    fig.patch.set_facecolor('#0D1117')
    draw_pitch(ax, color='#0D1117', line_color='#21262D')

    # Visible area polygon
    if visible_area and len(visible_area) >= 6:
        xs = visible_area[0::2]
        ys = visible_area[1::2]
        poly = plt.Polygon(list(zip(xs, ys)), fill=True, facecolor='#00B8A9', alpha=0.08, edgecolor='#00B8A9',
                           linewidth=1.5, linestyle='--')
        ax.add_patch(poly)

    # Players
    for player in freeze:
        loc = player.get('location', [0, 0])
        is_teammate = player.get('teammate', False)
        is_keeper = isinstance(player.get('position'), dict) and player['position'].get('name') == 'Goalkeeper'

        color = '#eab308' if is_keeper else ('#00B8A9' if is_teammate else '#a855f7')
        size = 200 if is_keeper else 150
        ax.scatter(loc[0], loc[1], s=size, color=color, edgecolors='white', linewidths=1.5, zorder=4)

    # Event location
    ex, ey = event.get('x', 60), event.get('y', 40)
    ax.scatter(ex, ey, s=300, color='white', zorder=6, edgecolors='#00B8A9', linewidths=3)

    legend_elements = [
        mpatches.Patch(facecolor='#00B8A9', alpha=0.15, edgecolor='#00B8A9', linestyle='--', label='Visible area'),
        mpatches.Patch(color='#00B8A9', label='Attacking team'),
        mpatches.Patch(color='#a855f7', label='Defending team'),
        mpatches.Patch(color='#eab308', label='Goalkeeper'),
    ]
    ax.legend(handles=legend_elements, facecolor='#161B22', edgecolor='#21262D', labelcolor='#F9FAFB',
              loc='upper left', fontsize=9)
    ax.set_title(f'360° Freeze Frame — {home_team.split()[-1]} vs {away_team.split()[-1]}',
                 color='#F9FAFB', fontweight='bold', fontsize=13)
    plt.tight_layout()
    plt.savefig(f'{FIGURES}/360_freeze_frame.png', dpi=150, bbox_inches='tight', facecolor='#0D1117')
    plt.close()
    print('Saved 360_freeze_frame.png')

# ── Figure 2: Pressing distance distribution from 360° ───────────────────────
pressing_distances = []
pressure_events = df[df['type'] == 'Pressure'].copy()
for _, pev in pressure_events.iterrows():
    eid = pev.get('event_id')
    if eid not in frames_dict:
        continue
    fr = frames_dict[eid]
    ff = fr.get('freeze_frame', [])
    px, py = pev.get('x', 0), pev.get('y', 0)
    for player in ff:
        if player.get('teammate', True):
            continue
        loc = player.get('location', [0, 0])
        dist = np.sqrt((loc[0] - px)**2 + (loc[1] - py)**2)
        pressing_distances.append(dist)

if pressing_distances:
    fig2, ax2 = plt.subplots(figsize=(9, 5))
    fig2.patch.set_facecolor('#0D1117')
    ax2.set_facecolor('#0D1117')
    ax2.hist(pressing_distances[:5000], bins=40, color='#00B8A9', alpha=0.8, edgecolor='#0D1117')
    ax2.set_xlabel('Distance to Nearest Opponent (yards)', color='#94A3B8', fontsize=11)
    ax2.set_ylabel('Count', color='#94A3B8', fontsize=11)
    ax2.set_title('Space at Pressure Events — Bundesliga 2023/24', color='#F9FAFB', fontweight='bold', fontsize=13)
    ax2.axvline(np.median(pressing_distances), color='white', linewidth=1.5, linestyle='--',
                label=f'Median: {np.median(pressing_distances):.1f}y')
    ax2.tick_params(colors='#94A3B8')
    ax2.spines[:].set_color('#21262D')
    ax2.legend(facecolor='#161B22', edgecolor='#21262D', labelcolor='#94A3B8')
    plt.tight_layout()
    plt.savefig(f'{FIGURES}/pressing_distance_360.png', dpi=150, bbox_inches='tight', facecolor='#0D1117')
    plt.close()
    print('Saved pressing_distance_360.png')

print('All 2.6 figures done.')
