import sys
import json
import os
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

# ── Load all La Liga 2015/16 shots ──────────────────────────────────────────
comp_df = load_competitions()
row = comp_df[(comp_df['competition_name'] == 'La Liga') & (comp_df['season_name'] == '2015/2016')].iloc[0]
matches = load_matches(row['competition_id'], row['season_id'])

all_shots = []
for match_id in matches['match_id']:
    try:
        raw = load_events(match_id)
        df = flatten_events(raw)
        shots = df[df['type'] == 'Shot'].copy()
        if shots.empty:
            continue
        shots['match_id'] = match_id
        home = matches.loc[matches['match_id'] == match_id, 'home_team'].iloc[0]
        away = matches.loc[matches['match_id'] == match_id, 'away_team'].iloc[0]
        shots['home_team'] = home['home_team_name'] if isinstance(home, dict) else home
        shots['away_team'] = away['away_team_name'] if isinstance(away, dict) else away
        all_shots.append(shots[['match_id', 'team', 'player', 'shot_statsbomb_xg', 'shot_outcome', 'home_team', 'away_team']])
    except Exception:
        continue

shots_df = pd.concat(all_shots, ignore_index=True)
shots_df = shots_df[shots_df['shot_statsbomb_xg'].notna()]

# Team-level: sum xG vs actual goals
def outcome_is_goal(o):
    if isinstance(o, dict):
        return o.get('name', '') == 'Goal'
    return str(o) == 'Goal'

shots_df['is_goal'] = shots_df['shot_outcome'].apply(outcome_is_goal)
team_stats = shots_df.groupby('team').agg(
    xg=('shot_statsbomb_xg', 'sum'),
    goals=('is_goal', 'sum')
).reset_index()
team_stats['short'] = team_stats['team'].apply(lambda t: t.split()[-1] if len(t.split()) > 1 else t)

# ── Figure 1: xG vs Goals scatter ───────────────────────────────────────────
fig, ax = plt.subplots(figsize=(9, 7))
fig.patch.set_facecolor('#0D1117')
ax.set_facecolor('#0D1117')

ax.scatter(team_stats['xg'], team_stats['goals'],
           color='#00B8A9', edgecolors='white', linewidths=1, s=80, zorder=3)

mn = min(team_stats['xg'].min(), team_stats['goals'].min()) - 5
mx = max(team_stats['xg'].max(), team_stats['goals'].max()) + 5
ax.plot([mn, mx], [mn, mx], color='#94A3B8', linewidth=1, linestyle='--', alpha=0.6, label='xG = Goals')

for _, r in team_stats.iterrows():
    ax.annotate(r['short'], (r['xg'], r['goals']),
                textcoords='offset points', xytext=(5, 3),
                fontsize=7.5, color='#F9FAFB', alpha=0.85)

ax.set_xlabel('xG (Expected Goals)', color='#94A3B8', fontsize=11)
ax.set_ylabel('Actual Goals', color='#94A3B8', fontsize=11)
ax.set_title('xG vs Actual Goals — La Liga 2015/16', color='#F9FAFB', fontweight='bold', fontsize=13)
ax.tick_params(colors='#94A3B8')
ax.spines[:].set_color('#21262D')
ax.legend(facecolor='#161B22', edgecolor='#21262D', labelcolor='#94A3B8')
plt.tight_layout()
plt.savefig(f'{FIGURES}/xg_vs_goals.png', dpi=150, bbox_inches='tight', facecolor='#0D1117')
plt.close()
print('Saved xg_vs_goals.png')

# ── Figure 2: Cumulative xG for a specific match ─────────────────────────────
# Barcelona 6-0 Athletic Club (match 266149)
MATCH_ID = 266149
raw = load_events(MATCH_ID)
df = flatten_events(raw)
match_row = matches[matches['match_id'] == MATCH_ID].iloc[0]
home = match_row['home_team']
home_team = home['home_team_name'] if isinstance(home, dict) else home
away = match_row['away_team']
away_team = away['away_team_name'] if isinstance(away, dict) else away

shots_m = df[df['type'] == 'Shot'].copy()
shots_m = shots_m[shots_m['shot_statsbomb_xg'].notna()].sort_values('minute')

for team, color, label in [(home_team, '#00B8A9', home_team), (away_team, '#a855f7', away_team)]:
    ts = shots_m[shots_m['team'] == team].copy()
    ts['cum_xg'] = ts['shot_statsbomb_xg'].cumsum()
    minutes = [0] + list(ts['minute']) + [90]
    values = [0] + list(ts['cum_xg']) + [ts['cum_xg'].iloc[-1] if len(ts) > 0 else 0]
    plt.step(minutes, values, where='post', color=color, linewidth=2, label=f'{label.split()[-1]}')

fig2, ax2 = plt.subplots(figsize=(10, 5))
fig2.patch.set_facecolor('#0D1117')
ax2.set_facecolor('#0D1117')

for team, color in [(home_team, '#00B8A9'), (away_team, '#a855f7')]:
    ts = shots_m[shots_m['team'] == team].copy()
    if ts.empty:
        continue
    ts['cum_xg'] = ts['shot_statsbomb_xg'].cumsum()
    minutes = [0] + list(ts['minute']) + [90]
    cum = [0] + list(ts['cum_xg']) + [ts['cum_xg'].iloc[-1]]
    short = team.split()[-1] if len(team.split()) > 1 else team
    ax2.step(minutes, cum, where='post', color=color, linewidth=2.5, label=short)
    # mark goals
    goals = ts[ts['shot_outcome'].apply(outcome_is_goal)]
    for _, g in goals.iterrows():
        ax2.axvline(g['minute'], color=color, linewidth=0.8, alpha=0.4, linestyle=':')

ax2.set_xlim(0, 95)
ax2.set_xlabel('Minute', color='#94A3B8', fontsize=11)
ax2.set_ylabel('Cumulative xG', color='#94A3B8', fontsize=11)
ax2.set_title(f'Cumulative xG — {home_team.split()[-1]} 6-0 {away_team.split()[-1]}', color='#F9FAFB', fontweight='bold', fontsize=13)
ax2.tick_params(colors='#94A3B8')
ax2.spines[:].set_color('#21262D')
ax2.legend(facecolor='#161B22', edgecolor='#21262D', labelcolor='#94A3B8')
plt.tight_layout()
plt.savefig(f'{FIGURES}/cumulative_xg.png', dpi=150, bbox_inches='tight', facecolor='#0D1117')
plt.close()
print('Saved cumulative_xg.png')

# ── Figure 3: Season xG ranking ─────────────────────────────────────────────
team_stats_sorted = team_stats.sort_values('xg', ascending=True)
fig3, ax3 = plt.subplots(figsize=(10, 7))
fig3.patch.set_facecolor('#0D1117')
ax3.set_facecolor('#0D1117')

y = range(len(team_stats_sorted))
ax3.barh(y, team_stats_sorted['xg'], color='#00B8A9', alpha=0.8, label='xG')
ax3.scatter(team_stats_sorted['goals'], y, color='white', s=60, zorder=4, label='Actual Goals')

ax3.set_yticks(y)
ax3.set_yticklabels(team_stats_sorted['short'], color='#F9FAFB', fontsize=9)
ax3.set_xlabel('Goals / xG', color='#94A3B8', fontsize=11)
ax3.set_title('xG vs Goals — La Liga 2015/16 Season Ranking', color='#F9FAFB', fontweight='bold', fontsize=13)
ax3.tick_params(colors='#94A3B8')
ax3.spines[:].set_color('#21262D')
ax3.legend(facecolor='#161B22', edgecolor='#21262D', labelcolor='#94A3B8')
plt.tight_layout()
plt.savefig(f'{FIGURES}/xg_season_ranking.png', dpi=150, bbox_inches='tight', facecolor='#0D1117')
plt.close()
print('Saved xg_season_ranking.png')

print('All 2.1 figures done.')
