import os
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

FIGURES = 'figures'
os.makedirs(FIGURES, exist_ok=True)
GPS_PATH = '/Users/stefanhofmann/Documents/Bewerbung/Portfolio/Blog/03_Physical_Performance/assets/physical_data_synthetic.csv'

df = pd.read_csv(GPS_PATH)
df = df[df['minutes_played'] >= 45].copy()

POS_FULL = ['Goalkeeper', 'Center Back', 'Full Back', 'Defensive Midfielder',
            'Central Midfielder', 'Wide Midfielder', 'Attacking Midfielder', 'Striker']
POS_LABEL = ['GK', 'CB', 'FB', 'DM', 'CM', 'WM', 'AM', 'ST']
pos_map = dict(zip(POS_FULL, POS_LABEL))

df['pos_short'] = df['position'].map(pos_map)
df = df[df['pos_short'].notna()]
pos_order_short = [p for p in POS_LABEL if p in df['pos_short'].unique()]

# ── Figure 1: Max speed by position ──────────────────────────────────────────
fig, ax = plt.subplots(figsize=(10, 6))
fig.patch.set_facecolor('#0D1117')
ax.set_facecolor('#0D1117')

pos_speed = df.groupby('pos_short')['max_speed'].apply(list)
data_list = [pos_speed[p] for p in pos_order_short if p in pos_speed.index]
bplot = ax.boxplot(data_list,
                   positions=range(len(data_list)),
                   patch_artist=True, widths=0.5,
                   medianprops=dict(color='white', linewidth=2))

for patch in bplot['boxes']:
    patch.set_facecolor('#00B8A9')
    patch.set_alpha(0.7)
for el in ['whiskers', 'caps', 'fliers']:
    for item in bplot[el]:
        item.set_color('#94A3B8')

ax.set_xticks(range(len(data_list)))
ax.set_xticklabels(pos_order_short, color='#F9FAFB', fontsize=10)
ax.set_ylabel('Max Speed (km/h)', color='#94A3B8', fontsize=11)
ax.set_title('Max Speed Distribution by Position', color='#F9FAFB', fontweight='bold', fontsize=13)
ax.tick_params(colors='#94A3B8')
ax.spines[:].set_color('#21262D')
plt.tight_layout()
plt.savefig(f'{FIGURES}/max_speed_by_position.png', dpi=150, bbox_inches='tight', facecolor='#0D1117')
plt.close()
print('Saved max_speed_by_position.png')

# ── Figure 2: Sprint count and sprint distance by position ────────────────────
fig2, (ax2a, ax2b) = plt.subplots(1, 2, figsize=(14, 5))
fig2.patch.set_facecolor('#0D1117')

pos_sprint_count = df.groupby('pos_short')['count_sprint'].mean().reindex(pos_order_short)
pos_sprint_dist = df.groupby('pos_short')['sprinting_distance'].mean().reindex(pos_order_short)

for ax, data, title, ylabel in [
    (ax2a, pos_sprint_count, 'Avg Sprint Count by Position', 'Sprints per match'),
    (ax2b, pos_sprint_dist, 'Avg Sprinting Distance by Position', 'Sprinting Distance (m)'),
]:
    ax.set_facecolor('#0D1117')
    bars = ax.bar(range(len(data)), data.values, color='#00B8A9', alpha=0.85, edgecolor='#0D1117')
    ax.set_xticks(range(len(data)))
    ax.set_xticklabels(pos_order_short, color='#F9FAFB', fontsize=9)
    ax.set_ylabel(ylabel, color='#94A3B8', fontsize=10)
    ax.set_title(title, color='#F9FAFB', fontweight='bold', fontsize=12)
    ax.tick_params(colors='#94A3B8')
    ax.spines[:].set_color('#21262D')
    for bar in bars:
        v = bar.get_height()
        if not np.isnan(v):
            ax.text(bar.get_x() + bar.get_width()/2, v + 0.3, f'{v:.0f}',
                    ha='center', color='#F9FAFB', fontsize=8)

plt.tight_layout()
plt.savefig(f'{FIGURES}/sprint_profile_by_position.png', dpi=150, bbox_inches='tight', facecolor='#0D1117')
plt.close()
print('Saved sprint_profile_by_position.png')

# ── Figure 3: Speed zone stacked bar ─────────────────────────────────────────
pos_means = df.groupby('pos_short')[['total_distance', 'running_distance', 'hsr_distance', 'sprinting_distance']].mean().reindex(pos_order_short)

fig3, ax3 = plt.subplots(figsize=(11, 6))
fig3.patch.set_facecolor('#0D1117')
ax3.set_facecolor('#0D1117')

low_intensity = (pos_means['total_distance'] - pos_means['running_distance'] - pos_means['hsr_distance'] - pos_means['sprinting_distance']).clip(lower=0)
running = pos_means['running_distance']
hsr = pos_means['hsr_distance']
sprinting = pos_means['sprinting_distance']

x = np.arange(len(pos_order_short))
ax3.bar(x, low_intensity, label='Walking/Jogging', color='#374151', width=0.6)
ax3.bar(x, running, bottom=low_intensity, label='Running (14–19.8 km/h)', color='#3b82f6', width=0.6)
ax3.bar(x, hsr, bottom=low_intensity + running, label='HSR (19.8–25.2 km/h)', color='#00B8A9', width=0.6)
ax3.bar(x, sprinting, bottom=low_intensity + running + hsr, label='Sprinting (>25.2 km/h)', color='#a855f7', width=0.6)

ax3.set_xticks(x)
ax3.set_xticklabels(pos_order_short, color='#F9FAFB', fontsize=10)
ax3.set_ylabel('Distance (m per match)', color='#94A3B8', fontsize=11)
ax3.set_title('Speed Zone Profile by Position', color='#F9FAFB', fontweight='bold', fontsize=13)
ax3.tick_params(colors='#94A3B8')
ax3.spines[:].set_color('#21262D')
ax3.legend(facecolor='#161B22', edgecolor='#21262D', labelcolor='#F9FAFB', fontsize=9)
plt.tight_layout()
plt.savefig(f'{FIGURES}/speed_zones_stacked.png', dpi=150, bbox_inches='tight', facecolor='#0D1117')
plt.close()
print('Saved speed_zones_stacked.png')
print('All P.2 figures done.')
