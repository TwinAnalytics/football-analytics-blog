import sys
import os
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

sys.path.append('/Users/stefanhofmann/Documents/Bewerbung/Portfolio/Blog/assets/helpers')
from data_loader import load_competitions, load_matches, load_events, flatten_events
from pitch import draw_pitch

FIGURES = 'figures'
os.makedirs(FIGURES, exist_ok=True)

comp_df = load_competitions()
la_liga_seasons = comp_df[comp_df['competition_name'] == 'La Liga'].copy()
print(f'La Liga seasons available: {len(la_liga_seasons)}')
print(la_liga_seasons[['season_name', 'competition_id', 'season_id']].to_string())

def outcome_is_goal(o):
    if isinstance(o, dict):
        return o.get('name', '') == 'Goal'
    return str(o) == 'Goal'

def is_messi(name):
    return 'Messi' in str(name)

season_stats = []
messi_touch_maps = {}

for _, season_row in la_liga_seasons.sort_values('season_name').iterrows():
    season = season_row['season_name']
    print(f'Loading {season}...')
    try:
        matches = load_matches(season_row['competition_id'], season_row['season_id'])
        xg_total = 0
        goals_total = 0
        shots_total = 0
        assists_total = 0
        touches_x, touches_y = [], []

        for match_id in matches['match_id']:
            try:
                raw = load_events(match_id)
                df = flatten_events(raw)
                messi_df = df[df['player'].apply(is_messi)]
                if messi_df.empty:
                    continue

                shots = messi_df[messi_df['type'] == 'Shot']
                xg_total += shots['shot_statsbomb_xg'].sum()
                goals_total += shots['shot_outcome'].apply(outcome_is_goal).sum()
                shots_total += len(shots)

                passes = messi_df[messi_df['type'] == 'Pass']
                assists_total += passes['pass_goal_assist'].fillna(False).astype(bool).sum()

                touches = messi_df[messi_df['x'].notna()]
                touches_x.extend(touches['x'].tolist())
                touches_y.extend(touches['y'].tolist())
            except Exception:
                continue

        if shots_total > 0:
            season_stats.append({
                'season': season,
                'xg': xg_total,
                'goals': goals_total,
                'shots': shots_total,
                'assists': assists_total
            })
            if touches_x:
                messi_touch_maps[season] = (touches_x, touches_y)
    except Exception as e:
        print(f'  Error: {e}')
        continue

stats_df = pd.DataFrame(season_stats).sort_values('season')
print(stats_df)

if stats_df.empty:
    print('No data found')
    exit()

# ── Figure 1: xG and goals per season ────────────────────────────────────────
fig, ax = plt.subplots(figsize=(12, 6))
fig.patch.set_facecolor('#0D1117')
ax.set_facecolor('#0D1117')

x = np.arange(len(stats_df))
width = 0.35
ax.bar(x - width/2, stats_df['xg'], width, label='xG', color='#00B8A9', alpha=0.8)
ax.bar(x + width/2, stats_df['goals'], width, label='Goals', color='#a855f7', alpha=0.8)
ax.set_xticks(x)
ax.set_xticklabels(stats_df['season'], rotation=45, ha='right', color='#F9FAFB', fontsize=8)
ax.set_ylabel('Count', color='#94A3B8', fontsize=11)
ax.set_title("Messi — xG vs Goals per Season (La Liga)", color='#F9FAFB', fontweight='bold', fontsize=13)
ax.tick_params(colors='#94A3B8')
ax.spines[:].set_color('#21262D')
ax.legend(facecolor='#161B22', edgecolor='#21262D', labelcolor='#F9FAFB')
plt.tight_layout()
plt.savefig(f'{FIGURES}/messi_xg_career.png', dpi=150, bbox_inches='tight', facecolor='#0D1117')
plt.close()
print('Saved messi_xg_career.png')

# ── Figure 2: Shots per season trend ─────────────────────────────────────────
fig2, ax2 = plt.subplots(figsize=(12, 5))
fig2.patch.set_facecolor('#0D1117')
ax2.set_facecolor('#0D1117')
ax2.plot(stats_df['season'], stats_df['shots'], color='#00B8A9', linewidth=2.5, marker='o', markersize=6)
ax2.fill_between(range(len(stats_df)), stats_df['shots'], alpha=0.15, color='#00B8A9')
ax2.set_xticks(range(len(stats_df)))
ax2.set_xticklabels(stats_df['season'], rotation=45, ha='right', color='#F9FAFB', fontsize=8)
ax2.set_ylabel('Shots per Season', color='#94A3B8', fontsize=11)
ax2.set_title("Messi — Shot Volume per Season (La Liga)", color='#F9FAFB', fontweight='bold', fontsize=13)
ax2.tick_params(colors='#94A3B8')
ax2.spines[:].set_color('#21262D')
plt.tight_layout()
plt.savefig(f'{FIGURES}/messi_shots_career.png', dpi=150, bbox_inches='tight', facecolor='#0D1117')
plt.close()
print('Saved messi_shots_career.png')

# ── Figure 3: Touch map — early vs peak vs late ───────────────────────────────
from mplsoccer import Pitch

seasons_available = sorted(messi_touch_maps.keys())
selected = {}
if len(seasons_available) >= 3:
    selected['Early'] = seasons_available[0]
    selected['Peak'] = seasons_available[len(seasons_available)//2]
    selected['Late'] = seasons_available[-1]

if selected:
    fig3, axes3 = plt.subplots(1, len(selected), figsize=(18, 7))
    fig3.patch.set_facecolor('#0D1117')
    pitch = Pitch(pitch_type='statsbomb', pitch_color='#0D1117', line_color='#21262D', line_zorder=2)

    for ax, (label, season) in zip(axes3, selected.items()):
        pitch.draw(ax=ax)
        xs, ys = messi_touch_maps[season]
        stats = pitch.bin_statistic(xs, ys, statistic='count', bins=(24, 16))
        pitch.heatmap(stats, ax=ax, cmap='YlGn', edgecolors='#0D1117', alpha=0.85)
        ax.set_title(f'{label} ({season})', color='#F9FAFB', fontweight='bold', fontsize=12)

    fig3.suptitle("Messi Touch Map Evolution — La Liga", color='#F9FAFB', fontweight='bold', fontsize=14, y=1.02)
    plt.tight_layout()
    plt.savefig(f'{FIGURES}/messi_touch_evolution.png', dpi=150, bbox_inches='tight', facecolor='#0D1117')
    plt.close()
    print('Saved messi_touch_evolution.png')

print('All 4.1 figures done.')
