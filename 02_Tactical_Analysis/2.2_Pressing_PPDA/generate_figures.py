import sys
import os
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

sys.path.append('/Users/stefanhofmann/Documents/Bewerbung/Portfolio/Blog/assets/helpers')
from data_loader import load_competitions, load_matches, load_events, flatten_events

FIGURES = 'figures'
os.makedirs(FIGURES, exist_ok=True)

comp_df = load_competitions()
row = comp_df[(comp_df['competition_name'] == 'La Liga') & (comp_df['season_name'] == '2015/2016')].iloc[0]
matches = load_matches(row['competition_id'], row['season_id'])

# PPDA = opponent passes in own defensive third / defensive actions in own defensive third
# Defensive actions: Pressure, Tackle, Interception, Block, Foul Won (by pressing team)
DEFENSIVE_ACTIONS = {'Pressure', 'Tackle', 'Interception', 'Block'}

team_ppda = {}

print(f'Processing {len(matches)} matches...')
for i, match_id in enumerate(matches['match_id']):
    if i % 50 == 0:
        print(f'  {i}/{len(matches)}')
    try:
        raw = load_events(match_id)
        df = flatten_events(raw)
        match_row = matches[matches['match_id'] == match_id].iloc[0]
        home = match_row['home_team']
        home_team = home['home_team_name'] if isinstance(home, dict) else home
        away = match_row['away_team']
        away_team = away['away_team_name'] if isinstance(away, dict) else away

        for pressing_team, opp_team in [(home_team, away_team), (away_team, home_team)]:
            # Opp passes in their own half (x < 60) — that's the defensive third for the pressing team
            opp_passes_deep = df[
                (df['team'] == opp_team) &
                (df['type'] == 'Pass') &
                (df['x'] < 40)  # opp's defensive third
            ]
            # Pressing team's defensive actions in that zone
            press_actions = df[
                (df['team'] == pressing_team) &
                (df['type'].isin(DEFENSIVE_ACTIONS)) &
                (df['x'] > 60)  # in opp's half = pressing high
            ]
            n_passes = len(opp_passes_deep)
            n_actions = len(press_actions)
            if pressing_team not in team_ppda:
                team_ppda[pressing_team] = {'passes': 0, 'actions': 0}
            team_ppda[pressing_team]['passes'] += n_passes
            team_ppda[pressing_team]['actions'] += n_actions
    except Exception:
        continue

ppda_df = pd.DataFrame([
    {'team': t, 'ppda': v['passes'] / max(v['actions'], 1)}
    for t, v in team_ppda.items()
]).sort_values('ppda')
ppda_df['short'] = ppda_df['team'].apply(lambda t: t.split()[-1] if len(t.split()) > 1 else t)

# Load league standings (from match results)
standings = {}
for _, m in matches.iterrows():
    home = m['home_team']
    away = m['away_team']
    hn = home['home_team_name'] if isinstance(home, dict) else home
    an = away['away_team_name'] if isinstance(away, dict) else away
    hs = m['home_score']
    as_ = m['away_score']
    for team, pts in [(hn, 3 if hs > as_ else (1 if hs == as_ else 0)),
                       (an, 3 if as_ > hs else (1 if hs == as_ else 0))]:
        standings[team] = standings.get(team, 0) + pts

# ── Figure 1: PPDA ranking ────────────────────────────────────────────────────
fig, ax = plt.subplots(figsize=(10, 7))
fig.patch.set_facecolor('#0D1117')
ax.set_facecolor('#0D1117')

colors = ['#00B8A9' if p < ppda_df['ppda'].median() else '#94A3B8' for p in ppda_df['ppda']]
ax.barh(range(len(ppda_df)), ppda_df['ppda'], color=colors)
ax.set_yticks(range(len(ppda_df)))
ax.set_yticklabels(ppda_df['short'], color='#F9FAFB', fontsize=9)
ax.set_xlabel('PPDA (lower = more intense pressing)', color='#94A3B8', fontsize=11)
ax.set_title('Pressing Intensity — La Liga 2015/16', color='#F9FAFB', fontweight='bold', fontsize=13)
ax.axvline(ppda_df['ppda'].median(), color='white', linewidth=1, linestyle='--', alpha=0.5)
ax.tick_params(colors='#94A3B8')
ax.spines[:].set_color('#21262D')
plt.tight_layout()
plt.savefig(f'{FIGURES}/ppda_ranking.png', dpi=150, bbox_inches='tight', facecolor='#0D1117')
plt.close()
print('Saved ppda_ranking.png')

# ── Figure 2: PPDA vs Points ──────────────────────────────────────────────────
ppda_df['points'] = ppda_df['team'].map(standings)

fig2, ax2 = plt.subplots(figsize=(9, 7))
fig2.patch.set_facecolor('#0D1117')
ax2.set_facecolor('#0D1117')

ax2.scatter(ppda_df['ppda'], ppda_df['points'], color='#00B8A9', edgecolors='white', linewidths=1, s=80, zorder=3)
for _, r in ppda_df.iterrows():
    ax2.annotate(r['short'], (r['ppda'], r['points']),
                 textcoords='offset points', xytext=(5, 3), fontsize=7.5, color='#F9FAFB', alpha=0.85)

# Trend line
if ppda_df['ppda'].notna().all() and ppda_df['points'].notna().all():
    z = np.polyfit(ppda_df['ppda'], ppda_df['points'], 1)
    p = np.poly1d(z)
    x_line = np.linspace(ppda_df['ppda'].min(), ppda_df['ppda'].max(), 100)
    ax2.plot(x_line, p(x_line), color='#94A3B8', linewidth=1, linestyle='--', alpha=0.6)

ax2.set_xlabel('PPDA (lower = more pressing)', color='#94A3B8', fontsize=11)
ax2.set_ylabel('League Points', color='#94A3B8', fontsize=11)
ax2.set_title('Does Pressing Win Points? — La Liga 2015/16', color='#F9FAFB', fontweight='bold', fontsize=13)
ax2.tick_params(colors='#94A3B8')
ax2.spines[:].set_color('#21262D')
plt.tight_layout()
plt.savefig(f'{FIGURES}/ppda_vs_points.png', dpi=150, bbox_inches='tight', facecolor='#0D1117')
plt.close()
print('Saved ppda_vs_points.png')
print('All 2.2 figures done.')
