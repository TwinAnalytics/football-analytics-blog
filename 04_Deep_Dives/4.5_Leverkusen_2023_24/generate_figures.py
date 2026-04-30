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
row = comp_df[(comp_df['competition_name'] == '1. Bundesliga') & (comp_df['season_name'] == '2023/2024')].iloc[0]
matches = load_matches(row['competition_id'], row['season_id'])
print(f'Bundesliga 2023/24: {len(matches)} matches')

TARGET = 'Bayer Leverkusen'

def outcome_is_goal(o):
    if isinstance(o, dict):
        return o.get('name', '') == 'Goal'
    return str(o) == 'Goal'

# Find Leverkusen matches
lev_matches = []
for _, m in matches.iterrows():
    home = m['home_team']
    away = m['away_team']
    hn = home['home_team_name'] if isinstance(home, dict) else home
    an = away['away_team_name'] if isinstance(away, dict) else away
    if TARGET in hn or TARGET in an:
        lev_matches.append({
            'match_id': m['match_id'],
            'matchday': m.get('match_week', len(lev_matches)+1),
            'home': hn,
            'away': an,
            'home_score': m['home_score'],
            'away_score': m['away_score'],
            'is_home': TARGET in hn,
        })

print(f'Leverkusen matches: {len(lev_matches)}')
lev_matches.sort(key=lambda x: x['matchday'])

# Compute xG per match
print('Computing xG...')
for match_info in lev_matches:
    try:
        raw = load_events(match_info['match_id'])
        df = flatten_events(raw)
        shots = df[(df['type'] == 'Shot') & df['shot_statsbomb_xg'].notna()]
        lev_shots = shots[shots['team'] == TARGET]
        opp_shots = shots[shots['team'] != TARGET]
        match_info['lev_xg'] = lev_shots['shot_statsbomb_xg'].sum()
        match_info['opp_xg'] = opp_shots['shot_statsbomb_xg'].sum()
        match_info['lev_goals'] = lev_shots['shot_outcome'].apply(outcome_is_goal).sum() if len(lev_shots) > 0 else 0
        match_info['opp_goals'] = opp_shots['shot_outcome'].apply(outcome_is_goal).sum() if len(opp_shots) > 0 else 0
    except Exception:
        match_info['lev_xg'] = 0
        match_info['opp_xg'] = 0
        match_info['lev_goals'] = 0
        match_info['opp_goals'] = 0

lev_df = pd.DataFrame(lev_matches)
lev_df = lev_df.sort_values('matchday').reset_index(drop=True)

# Cumulative points
lev_df['points'] = lev_df.apply(
    lambda r: 3 if (r['is_home'] and r['home_score'] > r['away_score']) or
                   (not r['is_home'] and r['away_score'] > r['home_score'])
              else (1 if r['home_score'] == r['away_score'] else 0), axis=1
)
lev_df['cum_points'] = lev_df['points'].cumsum()
lev_df['cum_xg'] = lev_df['lev_xg'].cumsum()
lev_df['cum_xg_against'] = lev_df['opp_xg'].cumsum()

# ── Figure 1: xG for and against per match ───────────────────────────────────
fig, ax = plt.subplots(figsize=(14, 5))
fig.patch.set_facecolor('#0D1117')
ax.set_facecolor('#0D1117')

x = lev_df['matchday']
ax.plot(x, lev_df['lev_xg'], color='#00B8A9', linewidth=2, label='Leverkusen xG', marker='o', markersize=5)
ax.plot(x, lev_df['opp_xg'], color='#a855f7', linewidth=2, label='Opponent xG', marker='o', markersize=5)
ax.fill_between(x, lev_df['lev_xg'], lev_df['opp_xg'],
                where=lev_df['lev_xg'] >= lev_df['opp_xg'], alpha=0.15, color='#00B8A9')
ax.fill_between(x, lev_df['lev_xg'], lev_df['opp_xg'],
                where=lev_df['lev_xg'] < lev_df['opp_xg'], alpha=0.15, color='#a855f7')

ax.set_xlabel('Matchday', color='#94A3B8', fontsize=11)
ax.set_ylabel('xG', color='#94A3B8', fontsize=11)
ax.set_title('Bayer Leverkusen — xG per Match, Bundesliga 2023/24', color='#F9FAFB', fontweight='bold', fontsize=13)
ax.tick_params(colors='#94A3B8')
ax.spines[:].set_color('#21262D')
ax.legend(facecolor='#161B22', edgecolor='#21262D', labelcolor='#F9FAFB')
plt.tight_layout()
plt.savefig(f'{FIGURES}/leverkusen_xg_season.png', dpi=150, bbox_inches='tight', facecolor='#0D1117')
plt.close()
print('Saved leverkusen_xg_season.png')

# ── Figure 2: Cumulative xG vs actual points ──────────────────────────────────
# Expected points (simple: 3 if xg > opp_xg, else 0, 1 for draw)
lev_df['expected_result'] = lev_df.apply(
    lambda r: 3 if r['lev_xg'] > r['opp_xg'] + 0.3 else (1 if abs(r['lev_xg'] - r['opp_xg']) <= 0.3 else 0), axis=1
)
lev_df['cum_xg_points'] = lev_df['expected_result'].cumsum()

fig2, ax2 = plt.subplots(figsize=(12, 5))
fig2.patch.set_facecolor('#0D1117')
ax2.set_facecolor('#0D1117')

ax2.plot(lev_df['matchday'], lev_df['cum_points'], color='#00B8A9', linewidth=2.5, label='Actual Points')
ax2.plot(lev_df['matchday'], lev_df['cum_xg_points'], color='#eab308', linewidth=2, linestyle='--', label='xG-based Points')
ax2.fill_between(lev_df['matchday'], lev_df['cum_points'], lev_df['cum_xg_points'], alpha=0.12, color='#00B8A9')

ax2.set_xlabel('Matchday', color='#94A3B8', fontsize=11)
ax2.set_ylabel('Cumulative Points', color='#94A3B8', fontsize=11)
ax2.set_title('Leverkusen — Actual vs xG-Based Points, 2023/24', color='#F9FAFB', fontweight='bold', fontsize=13)
ax2.tick_params(colors='#94A3B8')
ax2.spines[:].set_color('#21262D')
ax2.legend(facecolor='#161B22', edgecolor='#21262D', labelcolor='#F9FAFB')
plt.tight_layout()
plt.savefig(f'{FIGURES}/leverkusen_points_vs_xg.png', dpi=150, bbox_inches='tight', facecolor='#0D1117')
plt.close()
print('Saved leverkusen_points_vs_xg.png')

# ── Figure 3: Pressing heatmap (touch map of pressure events) ─────────────────
from mplsoccer import Pitch

print('Building pressing heatmap...')
press_xs, press_ys = [], []
for match_info in lev_matches[:20]:
    try:
        raw = load_events(match_info['match_id'])
        df = flatten_events(raw)
        pressure = df[(df['type'] == 'Pressure') & (df['team'] == TARGET) & df['x'].notna()]
        press_xs.extend(pressure['x'].tolist())
        press_ys.extend(pressure['y'].tolist())
    except Exception:
        continue

if press_xs:
    fig3, ax3 = plt.subplots(figsize=(12, 8))
    fig3.patch.set_facecolor('#0D1117')
    pitch = Pitch(pitch_type='statsbomb', pitch_color='#0D1117', line_color='#21262D', line_zorder=2)
    pitch.draw(ax=ax3)
    stats = pitch.bin_statistic(press_xs, press_ys, statistic='count', bins=(24, 16))
    pitch.heatmap(stats, ax=ax3, cmap='YlGn', edgecolors='#0D1117', alpha=0.85)
    ax3.set_title('Leverkusen — Pressing Zones, Bundesliga 2023/24', color='#F9FAFB', fontweight='bold', fontsize=13)
    plt.tight_layout()
    plt.savefig(f'{FIGURES}/leverkusen_pressing.png', dpi=150, bbox_inches='tight', facecolor='#0D1117')
    plt.close()
    print('Saved leverkusen_pressing.png')

print('All 4.5 figures done.')
