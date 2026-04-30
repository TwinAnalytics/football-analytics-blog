import os
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

FIGURES = 'figures'
os.makedirs(FIGURES, exist_ok=True)
GPS_PATH = '/Users/stefanhofmann/Documents/Bewerbung/Portfolio/Blog/03_Physical_Performance/assets/physical_data_synthetic.csv'

df = pd.read_csv(GPS_PATH)
df = df[df['minutes_played'] >= 60].copy()

POS_FULL = ['Goalkeeper', 'Center Back', 'Full Back', 'Defensive Midfielder',
            'Central Midfielder', 'Wide Midfielder', 'Attacking Midfielder', 'Striker']
POS_LABEL = ['GK', 'CB', 'FB', 'DM', 'CM', 'WM', 'AM', 'ST']
pos_map = dict(zip(POS_FULL, POS_LABEL))
df['pos_short'] = df['position'].map(pos_map)
df = df[df['pos_short'].notna()]
pos_order_short = [p for p in POS_LABEL if p in df['pos_short'].unique()]

colors_map = {'GK':'#94A3B8','CB':'#3b82f6','FB':'#00B8A9','DM':'#22c55e',
              'CM':'#eab308','AM':'#f97316','WM':'#80F5E3','ST':'#ef4444'}

# ── Figure 1: High acceleration count by position ────────────────────────────
fig, ax = plt.subplots(figsize=(10, 6))
fig.patch.set_facecolor('#0D1117')
ax.set_facecolor('#0D1117')

pos_accel = df.groupby('pos_short')['count_high_acceleration'].apply(list)
data_list = [pos_accel[p] for p in pos_order_short if p in pos_accel.index]
bplot = ax.boxplot(data_list,
                   positions=range(len(data_list)),
                   patch_artist=True, widths=0.5,
                   medianprops=dict(color='white', linewidth=2))
for patch in bplot['boxes']:
    patch.set_facecolor('#a855f7')
    patch.set_alpha(0.7)
for el in ['whiskers', 'caps', 'fliers']:
    for item in bplot[el]:
        item.set_color('#94A3B8')

ax.set_xticks(range(len(data_list)))
ax.set_xticklabels(pos_order_short, color='#F9FAFB', fontsize=10)
ax.set_ylabel('Count High Accelerations', color='#94A3B8', fontsize=11)
ax.set_title('Neuromuscular Load: High Acceleration Count by Position', color='#F9FAFB', fontweight='bold', fontsize=13)
ax.tick_params(colors='#94A3B8')
ax.spines[:].set_color('#21262D')
plt.tight_layout()
plt.savefig(f'{FIGURES}/acceleration_by_position.png', dpi=150, bbox_inches='tight', facecolor='#0D1117')
plt.close()
print('Saved acceleration_by_position.png')

# ── Figure 2: Acceleration vs total distance scatter ─────────────────────────
fig2, ax2 = plt.subplots(figsize=(9, 7))
fig2.patch.set_facecolor('#0D1117')
ax2.set_facecolor('#0D1117')

for pos_short, color in colors_map.items():
    sub = df[df['pos_short'] == pos_short]
    if sub.empty:
        continue
    ax2.scatter(sub['total_distance'], sub['count_high_acceleration'], alpha=0.35, s=18,
                color=color, label=pos_short)

ax2.set_xlabel('Total Distance (m)', color='#94A3B8', fontsize=11)
ax2.set_ylabel('Count High Accelerations', color='#94A3B8', fontsize=11)
ax2.set_title('Acceleration Load vs Total Distance', color='#F9FAFB', fontweight='bold', fontsize=13)
ax2.tick_params(colors='#94A3B8')
ax2.spines[:].set_color('#21262D')
ax2.legend(facecolor='#161B22', edgecolor='#21262D', labelcolor='#F9FAFB', fontsize=9, ncol=2)
plt.tight_layout()
plt.savefig(f'{FIGURES}/acceleration_vs_distance.png', dpi=150, bbox_inches='tight', facecolor='#0D1117')
plt.close()
print('Saved acceleration_vs_distance.png')

# ── Figure 3: Correlation heatmap of physical metrics ─────────────────────────
metrics = ['total_distance', 'mmin', 'hsr_distance', 'sprinting_distance',
           'count_high_acceleration', 'count_sprint', 'max_speed']
corr = df[metrics].corr()
labels = ['Total Dist', 'm/min', 'HSR Dist', 'Sprint Dist', 'Hi Accel', 'Sprint Count', 'Max Speed']

fig3, ax3 = plt.subplots(figsize=(9, 7))
fig3.patch.set_facecolor('#0D1117')
ax3.set_facecolor('#0D1117')

im = ax3.imshow(corr.values, cmap='RdYlGn', vmin=-1, vmax=1, aspect='auto')
ax3.set_xticks(range(len(labels)))
ax3.set_yticks(range(len(labels)))
ax3.set_xticklabels(labels, color='#F9FAFB', fontsize=8, rotation=45, ha='right')
ax3.set_yticklabels(labels, color='#F9FAFB', fontsize=8)

for i in range(len(labels)):
    for j in range(len(labels)):
        v = corr.values[i, j]
        ax3.text(j, i, f'{v:.2f}', ha='center', va='center',
                 fontsize=7, color='black' if abs(v) > 0.5 else '#F9FAFB')

cbar = plt.colorbar(im, ax=ax3)
cbar.ax.tick_params(colors='#94A3B8')
ax3.set_title('Correlation Matrix — Physical Metrics', color='#F9FAFB', fontweight='bold', fontsize=13)
plt.tight_layout()
plt.savefig(f'{FIGURES}/correlation_heatmap.png', dpi=150, bbox_inches='tight', facecolor='#0D1117')
plt.close()
print('Saved correlation_heatmap.png')
print('All P.4 figures done.')
