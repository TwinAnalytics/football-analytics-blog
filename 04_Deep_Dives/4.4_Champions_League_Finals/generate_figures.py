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
cl_seasons = comp_df[comp_df['competition_name'] == 'Champions League'].copy()
print(f'CL seasons: {len(cl_seasons)}')

def outcome_is_goal(o):
    if isinstance(o, dict):
        return o.get('name', '') == 'Goal'
    return str(o) == 'Goal'

finals_stats = []
all_finals_matches = []

for _, season_row in cl_seasons.iterrows():
    try:
        matches = load_matches(season_row['competition_id'], season_row['season_id'])
        # Each CL season in Statsbomb appears to be just 1 game (the final)
        for _, match_row in matches.iterrows():
            match_id = match_row['match_id']
            home = match_row['home_team']
            away = match_row['away_team']
            home_team = home['home_team_name'] if isinstance(home, dict) else home
            away_team = away['away_team_name'] if isinstance(away, dict) else away
            hs = match_row['home_score']
            as_ = match_row['away_score']
            all_finals_matches.append({
                'match_id': match_id,
                'season': season_row['season_name'],
                'home': home_team,
                'away': away_team,
                'home_score': hs,
                'away_score': as_,
            })
    except Exception:
        continue

print(f'CL matches loaded: {len(all_finals_matches)}')
for m in all_finals_matches[:5]:
    print(f"  {m['season']}: {m['home']} {m['home_score']}-{m['away_score']} {m['away']}")

# Compute xG per match
print('Computing xG for each final...')
for match_info in all_finals_matches:
    try:
        raw = load_events(match_info['match_id'])
        df = flatten_events(raw)
        shots = df[(df['type'] == 'Shot') & df['shot_statsbomb_xg'].notna()]
        home_xg = shots[shots['team'] == match_info['home']]['shot_statsbomb_xg'].sum()
        away_xg = shots[shots['team'] == match_info['away']]['shot_statsbomb_xg'].sum()
        match_info['home_xg'] = home_xg
        match_info['away_xg'] = away_xg
        match_info['total_shots'] = len(shots)
    except Exception:
        match_info['home_xg'] = 0
        match_info['away_xg'] = 0
        match_info['total_shots'] = 0

finals_df = pd.DataFrame(all_finals_matches).sort_values('season')
print(finals_df[['season', 'home', 'away', 'home_score', 'away_score', 'home_xg', 'away_xg']].to_string())

# ── Figure 1: xG vs goals across finals ──────────────────────────────────────
fig, ax = plt.subplots(figsize=(11, 6))
fig.patch.set_facecolor('#0D1117')
ax.set_facecolor('#0D1117')

x = np.arange(len(finals_df))
ax.bar(x - 0.2, finals_df['home_xg'], 0.35, color='#00B8A9', alpha=0.8, label='Home xG')
ax.bar(x + 0.2, finals_df['away_xg'], 0.35, color='#a855f7', alpha=0.8, label='Away xG')

short_labels = [f"{r['season'][:4]}\n{r['home'].split()[-1]}\nvs {r['away'].split()[-1]}"
                for _, r in finals_df.iterrows()]
ax.set_xticks(x)
ax.set_xticklabels(short_labels, color='#F9FAFB', fontsize=6, rotation=0)
ax.set_ylabel('xG', color='#94A3B8', fontsize=11)
ax.set_title('Champions League Finals — xG for Both Teams', color='#F9FAFB', fontweight='bold', fontsize=13)
ax.tick_params(colors='#94A3B8')
ax.spines[:].set_color('#21262D')
ax.legend(facecolor='#161B22', edgecolor='#21262D', labelcolor='#F9FAFB')
plt.tight_layout()
plt.savefig(f'{FIGURES}/cl_finals_xg.png', dpi=150, bbox_inches='tight', facecolor='#0D1117')
plt.close()
print('Saved cl_finals_xg.png')

# ── Figure 2: Cumulative xG for the most exciting final ──────────────────────
most_goals_idx = finals_df.apply(lambda r: r['home_score'] + r['away_score'], axis=1).idxmax()
best_match = finals_df.loc[most_goals_idx]
print(f"Featured final: {best_match['season']} {best_match['home']} vs {best_match['away']}")

try:
    raw = load_events(best_match['match_id'])
    df = flatten_events(raw)
    shots = df[(df['type'] == 'Shot') & df['shot_statsbomb_xg'].notna()].sort_values('minute')

    fig2, ax2 = plt.subplots(figsize=(11, 5))
    fig2.patch.set_facecolor('#0D1117')
    ax2.set_facecolor('#0D1117')

    for team, color in [(best_match['home'], '#00B8A9'), (best_match['away'], '#a855f7')]:
        ts = shots[shots['team'] == team].copy()
        if ts.empty:
            continue
        ts['cum_xg'] = ts['shot_statsbomb_xg'].cumsum()
        minutes = [0] + list(ts['minute']) + [90]
        cum = [0] + list(ts['cum_xg']) + [ts['cum_xg'].iloc[-1]]
        short = team.split()[-1]
        ax2.step(minutes, cum, where='post', color=color, linewidth=2.5, label=short)
        goals = ts[ts['shot_outcome'].apply(outcome_is_goal)]
        for _, g in goals.iterrows():
            ax2.axvline(g['minute'], color=color, linewidth=0.8, linestyle=':', alpha=0.5)

    home_s = best_match['home'].split()[-1]
    away_s = best_match['away'].split()[-1]
    ax2.set_title(f"CL Final {best_match['season']} — {home_s} {int(best_match['home_score'])}-{int(best_match['away_score'])} {away_s}",
                  color='#F9FAFB', fontweight='bold', fontsize=13)
    ax2.set_xlabel('Minute', color='#94A3B8', fontsize=11)
    ax2.set_ylabel('Cumulative xG', color='#94A3B8', fontsize=11)
    ax2.tick_params(colors='#94A3B8')
    ax2.spines[:].set_color('#21262D')
    ax2.legend(facecolor='#161B22', edgecolor='#21262D', labelcolor='#F9FAFB')
    plt.tight_layout()
    plt.savefig(f'{FIGURES}/cl_final_cumxg.png', dpi=150, bbox_inches='tight', facecolor='#0D1117')
    plt.close()
    print('Saved cl_final_cumxg.png')

    # ── Figure 3: Shot map of featured final ─────────────────────────────────
    fig3, (ax3a, ax3b) = plt.subplots(1, 2, figsize=(18, 7))
    fig3.patch.set_facecolor('#0D1117')

    all_shots_m = df[df['type'] == 'Shot'].copy()
    all_shots_m = all_shots_m[all_shots_m['x'].notna()]
    all_shots_m['is_goal'] = all_shots_m['shot_outcome'].apply(outcome_is_goal)

    def normalize(x, y):
        return (120 - x, 80 - y) if x < 60 else (x, y)

    for ax, team, title, color in [
        (ax3a, best_match['home'], best_match['home'].split()[-1], '#00B8A9'),
        (ax3b, best_match['away'], best_match['away'].split()[-1], '#a855f7'),
    ]:
        draw_pitch(ax, color='#0D1117', line_color='#21262D')
        ts = all_shots_m[all_shots_m['team'] == team].copy()
        ts[['xn', 'yn']] = ts.apply(lambda r: pd.Series(normalize(r['x'], r['y'])), axis=1)
        ax.scatter(ts[~ts['is_goal']]['xn'], ts[~ts['is_goal']]['yn'],
                   s=ts[~ts['is_goal']]['shot_statsbomb_xg'].fillna(0.1) * 1000,
                   color=color, alpha=0.6, edgecolors='white', linewidths=1, zorder=3, marker='o')
        ax.scatter(ts[ts['is_goal']]['xn'], ts[ts['is_goal']]['yn'],
                   s=ts[ts['is_goal']]['shot_statsbomb_xg'].fillna(0.1) * 1000,
                   color='white', alpha=0.9, edgecolors=color, linewidths=2, zorder=4, marker='*')
        ax.set_title(title, color='#F9FAFB', fontweight='bold', fontsize=12)

    fig3.suptitle(f"Shot Maps — CL Final {best_match['season']}", color='#F9FAFB', fontweight='bold', fontsize=14)
    plt.tight_layout()
    plt.savefig(f'{FIGURES}/cl_final_shot_map.png', dpi=150, bbox_inches='tight', facecolor='#0D1117')
    plt.close()
    print('Saved cl_final_shot_map.png')

except Exception as e:
    print(f'Error in featured final: {e}')

print('All 4.4 figures done.')
