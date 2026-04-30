import sys
import os
import json
import pandas as pd
import matplotlib.pyplot as plt
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
match_ids_360 = [mid for mid in matches['match_id'] if mid in available_360]
print(f'Matches with 360°: {len(match_ids_360)}')

team_distances = {}
print('Processing matches...')
for match_id in match_ids_360[:15]:
    try:
        raw = load_events(match_id)
        df = flatten_events(raw)
        with open(os.path.join(three_sixty_dir, f'{match_id}.json')) as f:
            frames = json.load(f)
        frames_dict = {fr['event_uuid']: fr for fr in frames}

        pressure_events = df[df['type'] == 'Pressure']
        for _, pev in pressure_events.iterrows():
            eid = pev.get('event_id')
            if eid not in frames_dict:
                continue
            fr = frames_dict[eid]
            ff = fr.get('freeze_frame', [])
            px, py = pev.get('x', 0), pev.get('y', 0)
            team = pev.get('team', 'Unknown')
            opponents = [p for p in ff if not p.get('teammate', True)]
            if not opponents:
                continue
            min_dist = min(
                np.sqrt((p.get('location', [0,0])[0]-px)**2 + (p.get('location', [0,0])[1]-py)**2)
                for p in opponents
            )
            team_distances.setdefault(team, []).append(min_dist)
    except Exception as e:
        continue

print(f'Teams with pressing data: {len(team_distances)}')
for t, d in list(team_distances.items())[:5]:
    print(f'  {t}: {len(d)} events, median={np.median(d):.2f}')

# ── Figure 1: Pressing distance histogram ────────────────────────────────────
fig, ax = plt.subplots(figsize=(10, 6))
fig.patch.set_facecolor('#0D1117')
ax.set_facecolor('#0D1117')

if team_distances:
    teams_sorted = sorted(team_distances.items(), key=lambda x: np.median(x[1]))
    top_teams = teams_sorted[:3] + (teams_sorted[-3:] if len(teams_sorted) > 3 else [])
    colors = ['#00B8A9', '#3b82f6', '#22c55e', '#a855f7', '#f97316', '#ef4444']
    for (team, dists), color in zip(top_teams, colors):
        short = team.split()[-1] if len(team.split()) > 1 else team
        ax.hist(dists, bins=25, alpha=0.5, color=color,
                label=f'{short} (med={np.median(dists):.1f})', density=True)

ax.set_xlabel('Distance to Ball Carrier at Pressure (yards)', color='#94A3B8', fontsize=11)
ax.set_ylabel('Density', color='#94A3B8', fontsize=11)
ax.set_title('Pressing Distance Distribution — Bundesliga 2023/24', color='#F9FAFB', fontweight='bold', fontsize=13)
ax.tick_params(colors='#94A3B8')
ax.spines[:].set_color('#21262D')
if team_distances:
    ax.legend(facecolor='#161B22', edgecolor='#21262D', labelcolor='#F9FAFB', fontsize=8)
plt.tight_layout()
plt.savefig(f'{FIGURES}/pressing_distance_hist.png', dpi=150, bbox_inches='tight', facecolor='#0D1117')
plt.close()
print('Saved pressing_distance_hist.png')

# ── Figure 2: Median pressing distance ranking ────────────────────────────────
rows = [{'team': t, 'median_dist': np.median(d), 'n': len(d)}
        for t, d in team_distances.items() if len(d) >= 10]
team_median = pd.DataFrame(rows)

if not team_median.empty:
    team_median = team_median.sort_values('median_dist')
    team_median['short'] = team_median['team'].apply(
        lambda t: t.split()[-1] if len(t.split()) > 1 else t)

    fig2, ax2 = plt.subplots(figsize=(10, 6))
    fig2.patch.set_facecolor('#0D1117')
    ax2.set_facecolor('#0D1117')
    med = team_median['median_dist'].median()
    colors_bar = ['#00B8A9' if m < med else '#94A3B8' for m in team_median['median_dist']]
    ax2.barh(range(len(team_median)), team_median['median_dist'], color=colors_bar)
    ax2.set_yticks(range(len(team_median)))
    ax2.set_yticklabels(team_median['short'], color='#F9FAFB', fontsize=9)
    ax2.set_xlabel('Median Pressing Distance (yards) — lower = tighter', color='#94A3B8', fontsize=11)
    ax2.set_title('Pressing Tightness by Team — Bundesliga 2023/24', color='#F9FAFB', fontweight='bold', fontsize=13)
    ax2.tick_params(colors='#94A3B8')
    ax2.spines[:].set_color('#21262D')
    ax2.axvline(med, color='white', linewidth=1, linestyle='--', alpha=0.5)
    plt.tight_layout()
    plt.savefig(f'{FIGURES}/pressing_tightness_ranking.png', dpi=150, bbox_inches='tight', facecolor='#0D1117')
    plt.close()
    print('Saved pressing_tightness_ranking.png')
else:
    print('Not enough pressing data for ranking chart')

print('All P.5 figures done.')
