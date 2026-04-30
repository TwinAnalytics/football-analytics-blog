import sys
import os
import ast
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

def parse_loc(s):
    try:
        v = ast.literal_eval(s) if isinstance(s, str) else s
        return float(v[0]), float(v[1])
    except Exception:
        return None, None

all_passes = []
print(f'Loading {len(matches)} matches...')
for i, match_id in enumerate(matches['match_id']):
    if i % 50 == 0:
        print(f'  {i}/{len(matches)}')
    try:
        raw = load_events(match_id)
        df = flatten_events(raw)
        passes = df[df['type'] == 'Pass'].copy()
        if passes.empty:
            continue
        keep = ['player', 'team', 'x', 'y', 'pass_end_location', 'pass_technique',
                'pass_outcome', 'pass_shot_assist', 'pass_goal_assist', 'pass_switch']
        existing = [c for c in keep if c in passes.columns]
        all_passes.append(passes[existing])
    except Exception:
        continue

if not all_passes:
    print('No pass data found')
    exit()

passes_df = pd.concat(all_passes, ignore_index=True)

# Parse end location
loc_parsed = passes_df['pass_end_location'].apply(parse_loc)
passes_df['pass_end_x'] = [v[0] for v in loc_parsed]
passes_df['pass_end_y'] = [v[1] for v in loc_parsed]

def is_through_ball(technique):
    if isinstance(technique, dict):
        return technique.get('name', '') == 'Through Ball'
    if isinstance(technique, str):
        try:
            return ast.literal_eval(technique).get('name', '') == 'Through Ball'
        except Exception:
            return 'Through Ball' in technique
    return False

passes_df['is_through'] = passes_df.get('pass_technique', pd.Series(dtype=object)).apply(is_through_ball)
through_balls = passes_df[passes_df['is_through']].copy()
through_balls['is_complete'] = through_balls['pass_outcome'].isna()
through_balls['is_shot_assist'] = through_balls.get('pass_shot_assist', pd.Series(dtype=object)).fillna(False).astype(bool)
through_balls['is_goal_assist'] = through_balls.get('pass_goal_assist', pd.Series(dtype=object)).fillna(False).astype(bool)

print(f'Total through balls: {len(through_balls)}')
print(f'Completed: {through_balls["is_complete"].sum()}')

# ── Figure 1: Through ball origin heatmap ────────────────────────────────────
from mplsoccer import Pitch

completed = through_balls[through_balls['is_complete'] & through_balls['x'].notna()].copy()

fig1, ax1 = plt.subplots(figsize=(12, 8))
fig1.patch.set_facecolor('#0D1117')
pitch = Pitch(pitch_type='statsbomb', pitch_color='#0D1117', line_color='#21262D', line_zorder=2)
pitch.draw(ax=ax1)

if not completed.empty:
    stats = pitch.bin_statistic(completed['x'], completed['y'], statistic='count', bins=(24, 16))
    pitch.heatmap(stats, ax=ax1, cmap='YlGn', edgecolors='#0D1117', alpha=0.8)

ax1.set_title('Through Ball Origins — La Liga 2015/16 (Completed)', color='#F9FAFB', fontweight='bold', fontsize=13)
plt.tight_layout()
plt.savefig(f'{FIGURES}/through_ball_origins.png', dpi=150, bbox_inches='tight', facecolor='#0D1117')
plt.close()
print('Saved through_ball_origins.png')

# ── Figure 2: Top players by through balls ────────────────────────────────────
player_stats = through_balls.groupby('player').agg(
    total=('is_through', 'count'),
    completed=('is_complete', 'sum'),
    shot_assists=('is_shot_assist', 'sum'),
    goal_assists=('is_goal_assist', 'sum')
).reset_index()
player_stats = player_stats[player_stats['total'] >= 5].sort_values('total', ascending=False).head(15)
PLAYER_SHORT = {
    'Lionel Andrés Messi Cuccittini':        'Messi',
    'Andrés Iniesta Luján':                  'Iniesta',
    'Neymar da Silva Santos Junior':         'Neymar',
    'Luis Alberto Suárez Díaz':             'Suárez',
    'Manuel Agudo Durán':                    'Nolito',
    'Luka Modrić':                           'Modrić',
    'Jonathan Viera Ramos':                  'Viera',
    'Luis Alberto Romero Alconchel':         'Luis Alberto',
    'Fabián Ariel Orellana Valenzuela':      'Orellana',
    'Ivan Rakitić':                          'Rakitić',
    'Sergio Busquets i Burgos':              'Busquets',
    'Daniel Alves da Silva':                 'Alves',
    'Jorge Resurrección Merodio':            'Koke',
    'Gabriel Fernández Arenas':              'Gabi',
    'Beñat Etxebarria Urkiaga':              'Beñat',
}
player_stats['short'] = player_stats['player'].map(PLAYER_SHORT).fillna(player_stats['player'].apply(lambda p: p.split()[-1]))

fig2, ax2 = plt.subplots(figsize=(10, 7))
fig2.patch.set_facecolor('#0D1117')
ax2.set_facecolor('#0D1117')

y = range(len(player_stats))
ax2.barh(y, player_stats['total'], color='#94A3B8', alpha=0.6, label='Total')
ax2.barh(y, player_stats['completed'], color='#00B8A9', alpha=0.85, label='Completed')
ax2.barh(y, player_stats['shot_assists'], color='#a855f7', alpha=0.85, label='Shot Assists')
ax2.set_yticks(y)
ax2.set_yticklabels(player_stats['short'], color='#F9FAFB', fontsize=9)
ax2.set_xlabel('Count', color='#94A3B8', fontsize=11)
ax2.set_title('Top Through Ball Players — La Liga 2015/16', color='#F9FAFB', fontweight='bold', fontsize=13)
ax2.tick_params(colors='#94A3B8')
ax2.spines[:].set_color('#21262D')
ax2.legend(facecolor='#161B22', edgecolor='#21262D', labelcolor='#94A3B8')
plt.tight_layout()
plt.savefig(f'{FIGURES}/through_ball_players.png', dpi=150, bbox_inches='tight', facecolor='#0D1117')
plt.close()
print('Saved through_ball_players.png')

# ── Figure 3: Completion rate comparison ─────────────────────────────────────
overall = passes_df['pass_outcome'].isna().mean()
through_comp = through_balls['is_complete'].mean() if not through_balls.empty else 0

fig3, ax3 = plt.subplots(figsize=(7, 5))
fig3.patch.set_facecolor('#0D1117')
ax3.set_facecolor('#0D1117')
labels = ['All Passes', 'Through Balls']
vals = [overall * 100, through_comp * 100]
bars = ax3.bar(labels, vals, color=['#94A3B8', '#00B8A9'], width=0.4)
for bar, val in zip(bars, vals):
    ax3.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.5, f'{val:.1f}%',
             ha='center', color='#F9FAFB', fontsize=12, fontweight='bold')
ax3.set_ylim(0, 105)
ax3.set_ylabel('Completion Rate (%)', color='#94A3B8', fontsize=11)
ax3.set_title('Pass Completion: All vs Through Balls', color='#F9FAFB', fontweight='bold', fontsize=13)
ax3.tick_params(colors='#94A3B8')
ax3.spines[:].set_color('#21262D')
plt.tight_layout()
plt.savefig(f'{FIGURES}/through_ball_completion.png', dpi=150, bbox_inches='tight', facecolor='#0D1117')
plt.close()
print('Saved through_ball_completion.png')
print('All 2.3 figures done.')
