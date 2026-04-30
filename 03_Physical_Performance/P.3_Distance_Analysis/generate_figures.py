import os
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

FIGURES = 'figures'
os.makedirs(FIGURES, exist_ok=True)
GPS_PATH = '/Users/stefanhofmann/Documents/Bewerbung/Portfolio/Blog/03_Physical_Performance/assets/physical_data_synthetic.csv'

df = pd.read_csv(GPS_PATH)

POS_FULL = ['Goalkeeper', 'Center Back', 'Full Back', 'Defensive Midfielder',
            'Central Midfielder', 'Wide Midfielder', 'Attacking Midfielder', 'Striker']
POS_LABEL = ['GK', 'CB', 'FB', 'DM', 'CM', 'WM', 'AM', 'ST']
pos_map = dict(zip(POS_FULL, POS_LABEL))
df['pos_short'] = df['position'].map(pos_map)

starters = df[df['minutes_played'] >= 60].copy()

colors_map = {'GK':'#94A3B8','CB':'#3b82f6','FB':'#00B8A9','DM':'#22c55e',
              'CM':'#eab308','AM':'#f97316','WM':'#80F5E3','ST':'#ef4444'}

# ── Figure 1: Total distance vs HI distance scatter ──────────────────────────
fig, ax = plt.subplots(figsize=(9, 7))
fig.patch.set_facecolor('#0D1117')
ax.set_facecolor('#0D1117')

for pos_short, color in colors_map.items():
    sub = starters[starters['pos_short'] == pos_short]
    if sub.empty:
        continue
    ax.scatter(sub['total_distance'], sub['hsr_distance'], alpha=0.3, s=20,
               color=color, label=pos_short)

ax.set_xlabel('Total Distance (m)', color='#94A3B8', fontsize=11)
ax.set_ylabel('High-Speed Running Distance (m)', color='#94A3B8', fontsize=11)
ax.set_title('Total Distance vs HSR Distance by Position', color='#F9FAFB', fontweight='bold', fontsize=13)
ax.tick_params(colors='#94A3B8')
ax.spines[:].set_color('#21262D')
ax.legend(facecolor='#161B22', edgecolor='#21262D', labelcolor='#F9FAFB', fontsize=9,
          markerscale=2, ncol=2)
plt.tight_layout()
plt.savefig(f'{FIGURES}/total_vs_hsr.png', dpi=150, bbox_inches='tight', facecolor='#0D1117')
plt.close()
print('Saved total_vs_hsr.png')

# ── Figure 2: Home vs Away ────────────────────────────────────────────────────
outfield = starters[starters['position'] != 'Goalkeeper']
home_away = outfield.groupby('is_home')[['total_distance', 'mmin', 'hsr_distance', 'sprinting_distance']].mean()

fig2, axes = plt.subplots(1, 4, figsize=(14, 5))
fig2.patch.set_facecolor('#0D1117')
metrics = ['total_distance', 'mmin', 'hsr_distance', 'sprinting_distance']
labels = ['Total Dist (m)', 'm/min', 'HSR Dist (m)', 'Sprint Dist (m)']

for ax, metric, label in zip(axes, metrics, labels):
    ax.set_facecolor('#0D1117')
    vals = [home_away.loc[False, metric], home_away.loc[True, metric]] if (False in home_away.index and True in home_away.index) else [0, 0]
    bars = ax.bar(['Away', 'Home'], vals, color=['#94A3B8', '#00B8A9'], width=0.5)
    ax.set_title(label, color='#F9FAFB', fontsize=10, fontweight='bold')
    ax.tick_params(colors='#94A3B8')
    ax.spines[:].set_color('#21262D')
    if vals[0] > 0:
        diff = (vals[1] - vals[0]) / vals[0] * 100
        ax.text(0.5, 0.95, f'{diff:+.1f}%', ha='center', color='#00B8A9' if diff > 0 else '#ef4444',
                fontsize=9, fontweight='bold', transform=ax.transAxes)

fig2.suptitle('Home vs Away Physical Load (Outfield Starters)', color='#F9FAFB', fontweight='bold', fontsize=13)
plt.tight_layout()
plt.savefig(f'{FIGURES}/home_vs_away.png', dpi=150, bbox_inches='tight', facecolor='#0D1117')
plt.close()
print('Saved home_vs_away.png')

# ── Figure 3: Starters vs Substitutes ────────────────────────────────────────
df_out = df[df['position'] != 'Goalkeeper'].copy()
df_out['role'] = df_out['minutes_played'].apply(lambda m: 'Starter (≥60 min)' if m >= 60 else 'Substitute (<60 min)')

fig3, ax3 = plt.subplots(figsize=(9, 5))
fig3.patch.set_facecolor('#0D1117')
ax3.set_facecolor('#0D1117')

for role, color in [('Starter (≥60 min)', '#00B8A9'), ('Substitute (<60 min)', '#a855f7')]:
    sub = df_out[df_out['role'] == role]['mmin']
    ax3.hist(sub, bins=30, alpha=0.6, color=color, label=role, density=True, edgecolor='#0D1117')

ax3.set_xlabel('Meters per Minute (m/min)', color='#94A3B8', fontsize=11)
ax3.set_ylabel('Density', color='#94A3B8', fontsize=11)
ax3.set_title('Intensity: Starters vs Substitutes', color='#F9FAFB', fontweight='bold', fontsize=13)
ax3.tick_params(colors='#94A3B8')
ax3.spines[:].set_color('#21262D')
ax3.legend(facecolor='#161B22', edgecolor='#21262D', labelcolor='#F9FAFB')
plt.tight_layout()
plt.savefig(f'{FIGURES}/starters_vs_subs.png', dpi=150, bbox_inches='tight', facecolor='#0D1117')
plt.close()
print('Saved starters_vs_subs.png')
print('All P.3 figures done.')
