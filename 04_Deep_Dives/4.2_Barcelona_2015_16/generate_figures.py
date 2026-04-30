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
row = comp_df[(comp_df['competition_name'] == 'La Liga') & (comp_df['season_name'] == '2015/2016')].iloc[0]
matches = load_matches(row['competition_id'], row['season_id'])
print(f'La Liga 2015/16: {len(matches)} matches')

def outcome_is_goal(o):
    if isinstance(o, dict):
        return o.get('name', '') == 'Goal'
    return str(o) == 'Goal'

team_xg_for = {}
team_xg_against = {}
team_goals_for = {}
team_goals_against = {}
team_points = {}

msn_players = {'Messi': [], 'Suárez': [], 'Neymar': []}

print('Processing all matches...')
for i, (_, match_row) in enumerate(matches.iterrows()):
    if i % 50 == 0:
        print(f'  {i}/{len(matches)}')
    match_id = match_row['match_id']
    home = match_row['home_team']
    away = match_row['away_team']
    home_team = home['home_team_name'] if isinstance(home, dict) else home
    away_team = away['away_team_name'] if isinstance(away, dict) else away
    hs = match_row['home_score']
    as_ = match_row['away_score']

    for team in [home_team, away_team]:
        team_goals_for.setdefault(team, 0)
        team_goals_against.setdefault(team, 0)
        team_xg_for.setdefault(team, 0)
        team_xg_against.setdefault(team, 0)
        team_points.setdefault(team, 0)

    # Points
    if hs > as_:
        team_points[home_team] += 3
    elif hs == as_:
        team_points[home_team] += 1
        team_points[away_team] += 1
    else:
        team_points[away_team] += 3

    team_goals_for[home_team] += hs
    team_goals_for[away_team] += as_
    team_goals_against[home_team] += as_
    team_goals_against[away_team] += hs

    try:
        raw = load_events(match_id)
        df = flatten_events(raw)
        shots = df[df['type'] == 'Shot'].copy()
        shots = shots[shots['shot_statsbomb_xg'].notna()]
        shots['is_goal'] = shots['shot_outcome'].apply(outcome_is_goal)

        for team in [home_team, away_team]:
            opp = away_team if team == home_team else home_team
            ts = shots[shots['team'] == team]
            team_xg_for[team] = team_xg_for.get(team, 0) + ts['shot_statsbomb_xg'].sum()
            team_xg_against[opp] = team_xg_against.get(opp, 0) + ts['shot_statsbomb_xg'].sum()

        # MSN shots
        for player_key, keywords in [('Messi', ['Messi']), ('Suárez', ['Suárez', 'Suarez']), ('Neymar', ['Neymar'])]:
            mask = shots['player'].apply(lambda p: any(k in str(p) for k in keywords))
            ps = shots[mask]
            if not ps.empty:
                msn_players[player_key].append({'xg': ps['shot_statsbomb_xg'].sum(), 'goals': ps['is_goal'].sum()})
    except Exception:
        continue

# Build standings
standings = pd.DataFrame({
    'team': list(team_points.keys()),
    'points': list(team_points.values()),
    'goals': [team_goals_for[t] for t in team_points.keys()],
    'goals_against': [team_goals_against[t] for t in team_points.keys()],
    'xg_for': [team_xg_for[t] for t in team_points.keys()],
    'xg_against': [team_xg_against[t] for t in team_points.keys()],
}).sort_values('points', ascending=False)
standings['xg_points_rank'] = standings['xg_for'].rank(ascending=False).astype(int)
standings['actual_rank'] = range(1, len(standings)+1)
TEAM_SHORT = {
    'Athletic Club':          'Athletic',
    'Atlético Madrid':        'Atlético',
    'Barcelona':              'Barcelona',
    'Celta Vigo':             'Celta',
    'Eibar':                  'Eibar',
    'Espanyol':               'Espanyol',
    'Getafe':                 'Getafe',
    'Granada':                'Granada',
    'Las Palmas':             'Las Palmas',
    'Levante UD':             'Levante',
    'Málaga':                 'Málaga',
    'RC Deportivo La Coruña': 'Deportivo',
    'Rayo Vallecano':         'Rayo',
    'Real Betis':             'Betis',
    'Real Madrid':            'Real Madrid',
    'Real Sociedad':          'Sociedad',
    'Sevilla':                'Sevilla',
    'Sporting Gijón':         'Sporting',
    'Valencia':               'Valencia',
    'Villarreal':             'Villarreal',
}
standings['short'] = standings['team'].map(TEAM_SHORT).fillna(standings['team'])

print(standings[['short', 'points', 'goals', 'xg_for', 'actual_rank']].head(10).to_string())

# ── Figure 1: xG table vs actual table ───────────────────────────────────────
top10 = standings.head(10)
fig, ax = plt.subplots(figsize=(10, 6))
fig.patch.set_facecolor('#0D1117')
ax.set_facecolor('#0D1117')

x = np.arange(len(top10))
ax.bar(x - 0.2, top10['points'], width=0.35, label='Actual Points', color='#00B8A9', alpha=0.85)
ax.bar(x + 0.2, top10['xg_for'], width=0.35, label='xG For', color='#a855f7', alpha=0.85)

ax.set_xticks(x)
ax.set_xticklabels(top10['short'], color='#F9FAFB', fontsize=9, rotation=30, ha='right')
ax.set_ylabel('Points / xG', color='#94A3B8', fontsize=11)
ax.set_title('Actual Points vs xG — La Liga 2015/16 Top 10', color='#F9FAFB', fontweight='bold', fontsize=13)
ax.tick_params(colors='#94A3B8')
ax.spines[:].set_color('#21262D')
ax.legend(facecolor='#161B22', edgecolor='#21262D', labelcolor='#F9FAFB')
plt.tight_layout()
plt.savefig(f'{FIGURES}/xg_table_comparison.png', dpi=150, bbox_inches='tight', facecolor='#0D1117')
plt.close()
print('Saved xg_table_comparison.png')

# ── Figure 2: MSN trio comparison ────────────────────────────────────────────
msn_summary = {
    player: {
        'xg': sum(m['xg'] for m in data),
        'goals': sum(m['goals'] for m in data)
    }
    for player, data in msn_players.items()
}

fig2, ax2 = plt.subplots(figsize=(8, 5))
fig2.patch.set_facecolor('#0D1117')
ax2.set_facecolor('#0D1117')

players = list(msn_summary.keys())
xg_vals = [msn_summary[p]['xg'] for p in players]
goal_vals = [msn_summary[p]['goals'] for p in players]
x = np.arange(len(players))
ax2.bar(x - 0.2, xg_vals, 0.35, label='xG', color='#00B8A9', alpha=0.85)
ax2.bar(x + 0.2, goal_vals, 0.35, label='Goals', color='#a855f7', alpha=0.85)
ax2.set_xticks(x)
ax2.set_xticklabels(players, color='#F9FAFB', fontsize=12, fontweight='bold')
ax2.set_ylabel('Count', color='#94A3B8', fontsize=11)
ax2.set_title('MSN Trio — xG vs Goals, La Liga 2015/16', color='#F9FAFB', fontweight='bold', fontsize=13)
ax2.tick_params(colors='#94A3B8')
ax2.spines[:].set_color('#21262D')
ax2.legend(facecolor='#161B22', edgecolor='#21262D', labelcolor='#F9FAFB')
plt.tight_layout()
plt.savefig(f'{FIGURES}/msn_comparison.png', dpi=150, bbox_inches='tight', facecolor='#0D1117')
plt.close()
print('Saved msn_comparison.png')

# ── Figure 3: xG for vs xG against scatter ───────────────────────────────────
fig3, ax3 = plt.subplots(figsize=(9, 7))
fig3.patch.set_facecolor('#0D1117')
ax3.set_facecolor('#0D1117')

highlight = ['Barcelona', 'Real Madrid']
for _, r in standings.iterrows():
    color = '#00B8A9' if r['team'] == 'Barcelona' else ('#a855f7' if r['team'] == 'Real Madrid' else '#94A3B8')
    size = 120 if r['team'] in highlight else 50
    ax3.scatter(r['xg_against'], r['xg_for'], color=color, s=size, edgecolors='white', linewidths=1, zorder=3)
    if r['team'] in highlight:
        ax3.annotate(r['short'], (r['xg_against'], r['xg_for']),
                     textcoords='offset points', xytext=(6, 4), color='#F9FAFB', fontsize=10, fontweight='bold')

ax3.set_xlabel('xG Against (lower = better defense)', color='#94A3B8', fontsize=11)
ax3.set_ylabel('xG For (higher = better attack)', color='#94A3B8', fontsize=11)
ax3.set_title('Attack vs Defense — La Liga 2015/16', color='#F9FAFB', fontweight='bold', fontsize=13)
ax3.tick_params(colors='#94A3B8')
ax3.spines[:].set_color('#21262D')
plt.tight_layout()
plt.savefig(f'{FIGURES}/attack_defense_scatter.png', dpi=150, bbox_inches='tight', facecolor='#0D1117')
plt.close()
print('Saved attack_defense_scatter.png')
print('All 4.2 figures done.')
