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

def outcome_is_goal(o):
    if isinstance(o, dict):
        return o.get('name', '') == 'Goal'
    return str(o) == 'Goal'

tournament_stats = {}
for comp_name, season_name, label in [
    ("Women's World Cup", "2019", "WWC 2019"),
    ("Women's World Cup", "2023", "WWC 2023"),
]:
    row = comp_df[(comp_df['competition_name'] == comp_name) & (comp_df['season_name'] == season_name)]
    if row.empty:
        print(f'No data for {label}')
        continue
    row = row.iloc[0]
    matches = load_matches(row['competition_id'], row['season_id'])
    print(f'{label}: {len(matches)} matches')

    xg_list, goals_list, pass_counts = [], [], []
    total_passes, total_duration = 0, 0

    for match_id in matches['match_id']:
        try:
            raw = load_events(match_id)
            df = flatten_events(raw)

            shots = df[df['type'] == 'Shot']
            passes = df[df['type'] == 'Pass']
            xg_list.extend(shots['shot_statsbomb_xg'].dropna().tolist())
            goals_list.extend(shots['shot_outcome'].apply(outcome_is_goal).tolist())
            pass_counts.append(len(passes))

            duration = df['minute'].max() if not df['minute'].isna().all() else 90
            total_passes += len(passes)
            total_duration += duration
        except Exception:
            continue

    tournament_stats[label] = {
        'total_xg': sum(xg_list),
        'total_goals': sum(goals_list),
        'total_shots': len(xg_list),
        'avg_xg_per_match': sum(xg_list) / len(matches),
        'conversion_rate': sum(goals_list) / len(xg_list) if xg_list else 0,
        'passes_per_match': total_passes / len(matches),
        'n_matches': len(matches),
    }

print(tournament_stats)

if len(tournament_stats) < 2:
    print('Need both tournaments')
    exit()

labels = list(tournament_stats.keys())
metrics = {
    'Avg xG per Match': 'avg_xg_per_match',
    'Shot Conversion (%)': 'conversion_rate',
    'Passes per Match': 'passes_per_match',
    'Total Goals': 'total_goals',
}

# ── Figure 1: Side-by-side comparison ────────────────────────────────────────
fig, axes = plt.subplots(1, 4, figsize=(16, 5))
fig.patch.set_facecolor('#0D1117')
colors = ['#3b82f6', '#00B8A9']

for ax, (metric_label, key) in zip(axes, metrics.items()):
    ax.set_facecolor('#0D1117')
    vals = [tournament_stats[l][key] for l in labels]
    if key == 'conversion_rate':
        vals = [v * 100 for v in vals]
    bars = ax.bar(labels, vals, color=colors, width=0.5)
    diff = (vals[1] - vals[0]) / vals[0] * 100 if vals[0] != 0 else 0
    ax.set_title(metric_label, color='#F9FAFB', fontsize=10, fontweight='bold')
    ax.set_ylabel(metric_label, color='#94A3B8', fontsize=9)
    ax.tick_params(colors='#F9FAFB', labelsize=8)
    ax.spines[:].set_color('#21262D')
    for bar, val in zip(bars, vals):
        ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() * 0.5,
                f'{val:.1f}', ha='center', va='center', color='white', fontsize=10, fontweight='bold')

fig.suptitle("Women's World Cup: 2019 vs 2023", color='#F9FAFB', fontweight='bold', fontsize=14)
plt.tight_layout()
plt.savefig(f'{FIGURES}/wwc_comparison.png', dpi=150, bbox_inches='tight', facecolor='#0D1117')
plt.close()
print('Saved wwc_comparison.png')

# ── Figure 2: xG distribution comparison ──────────────────────────────────────
fig2, ax2 = plt.subplots(figsize=(9, 5))
fig2.patch.set_facecolor('#0D1117')
ax2.set_facecolor('#0D1117')

for label, color in zip(labels, colors):
    row = comp_df[(comp_df['competition_name'] == "Women's World Cup") &
                  (comp_df['season_name'] == label.split()[-1])].iloc[0]
    matches = load_matches(row['competition_id'], row['season_id'])
    xg_vals = []
    for match_id in matches['match_id']:
        try:
            raw = load_events(match_id)
            df = flatten_events(raw)
            shots = df[(df['type'] == 'Shot') & df['shot_statsbomb_xg'].notna()]
            xg_vals.extend(shots['shot_statsbomb_xg'].tolist())
        except Exception:
            continue
    ax2.hist(xg_vals, bins=30, alpha=0.55, color=color, label=label, density=True)

ax2.set_xlabel('xG per Shot', color='#94A3B8', fontsize=11)
ax2.set_ylabel('Density', color='#94A3B8', fontsize=11)
ax2.set_title("Shot Quality Distribution — WWC 2019 vs 2023", color='#F9FAFB', fontweight='bold', fontsize=13)
ax2.tick_params(colors='#94A3B8')
ax2.spines[:].set_color('#21262D')
ax2.legend(facecolor='#161B22', edgecolor='#21262D', labelcolor='#F9FAFB')
plt.tight_layout()
plt.savefig(f'{FIGURES}/wwc_xg_distribution.png', dpi=150, bbox_inches='tight', facecolor='#0D1117')
plt.close()
print('Saved wwc_xg_distribution.png')
print('All 4.3 figures done.')
