import sys
import os
import ast
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

def parse_loc(s):
    try:
        v = ast.literal_eval(s) if isinstance(s, str) else s
        return float(v[0]), float(v[1])
    except Exception:
        return None, None

all_carries = []
print(f'Loading carries from {len(matches)} matches...')
for i, match_id in enumerate(matches['match_id']):
    if i % 50 == 0:
        print(f'  {i}/{len(matches)}')
    try:
        raw = load_events(match_id)
        df = flatten_events(raw)
        carries = df[df['type'] == 'Carry'].copy()
        if carries.empty:
            continue
        keep = ['player', 'team', 'x', 'y', 'carry_end_location']
        existing = [c for c in keep if c in carries.columns]
        all_carries.append(carries[existing])
    except Exception:
        continue

if not all_carries:
    print('No carry data')
    exit()

carries_df = pd.concat(all_carries, ignore_index=True)

loc_parsed = carries_df['carry_end_location'].apply(parse_loc)
carries_df['carry_end_x'] = [v[0] for v in loc_parsed]
carries_df['carry_end_y'] = [v[1] for v in loc_parsed]
carries_df = carries_df.dropna(subset=['x', 'y', 'carry_end_x', 'carry_end_y'])

carries_df['dx'] = carries_df['carry_end_x'] - carries_df['x']
carries_df['dy'] = carries_df['carry_end_y'] - carries_df['y']
carries_df['distance'] = np.sqrt(carries_df['dx']**2 + carries_df['dy']**2)
carries_df['progressive'] = (carries_df['dx'] > 5) & (carries_df['x'] > 40)

print(f'Total carries: {len(carries_df)} | Progressive: {carries_df["progressive"].sum()}')

# ── Figure 1: Arrow map of Barcelona progressive carries ──────────────────────
barca = carries_df[(carries_df['team'] == 'Barcelona') & carries_df['progressive'] & (carries_df['distance'] > 5)]
sample = barca.sample(min(200, len(barca)), random_state=42)

fig, ax = plt.subplots(figsize=(14, 9))
fig.patch.set_facecolor('#0D1117')
draw_pitch(ax, color='#0D1117', line_color='#21262D')
for _, row in sample.iterrows():
    ax.annotate('', xy=(row['carry_end_x'], row['carry_end_y']),
                xytext=(row['x'], row['y']),
                arrowprops=dict(arrowstyle='->', color='#00B8A9', lw=1.2, alpha=0.5))
ax.set_title('Barcelona — Progressive Carries, La Liga 2015/16', color='#F9FAFB', fontweight='bold', fontsize=13)
plt.tight_layout()
plt.savefig(f'{FIGURES}/progressive_carries_arrows.png', dpi=150, bbox_inches='tight', facecolor='#0D1117')
plt.close()
print('Saved progressive_carries_arrows.png')

# ── Figure 2: Top players by progressive carries ─────────────────────────────
player_carries = carries_df[carries_df['progressive']].groupby('player').size().reset_index(name='prog_carries')
player_carries = player_carries.sort_values('prog_carries', ascending=False).head(15)
player_carries['short'] = player_carries['player'].apply(lambda p: p.split()[-1] if len(p.split()) > 1 else p)

fig2, ax2 = plt.subplots(figsize=(10, 7))
fig2.patch.set_facecolor('#0D1117')
ax2.set_facecolor('#0D1117')
ax2.barh(range(len(player_carries)), player_carries['prog_carries'], color='#00B8A9', alpha=0.85)
ax2.set_yticks(range(len(player_carries)))
ax2.set_yticklabels(player_carries['short'], color='#F9FAFB', fontsize=9)
ax2.set_xlabel('Progressive Carries', color='#94A3B8', fontsize=11)
ax2.set_title('Top Carriers — La Liga 2015/16', color='#F9FAFB', fontweight='bold', fontsize=13)
ax2.tick_params(colors='#94A3B8')
ax2.spines[:].set_color('#21262D')
plt.tight_layout()
plt.savefig(f'{FIGURES}/top_carriers.png', dpi=150, bbox_inches='tight', facecolor='#0D1117')
plt.close()
print('Saved top_carriers.png')

# ── Figure 3: Carry zone heatmap ──────────────────────────────────────────────
from mplsoccer import Pitch

fig3, (ax3a, ax3b) = plt.subplots(1, 2, figsize=(18, 7))
fig3.patch.set_facecolor('#0D1117')
pitch = Pitch(pitch_type='statsbomb', pitch_color='#0D1117', line_color='#21262D', line_zorder=2)

for ax, team, title in [(ax3a, 'Barcelona', 'Barcelona — Carry Start Zones'),
                         (ax3b, 'Real Madrid', 'Real Madrid — Carry Start Zones')]:
    pitch.draw(ax=ax)
    tc = carries_df[carries_df['team'] == team]
    if tc.empty:
        continue
    stats = pitch.bin_statistic(tc['x'], tc['y'], statistic='count', bins=(24, 16))
    pitch.heatmap(stats, ax=ax, cmap='YlGn', edgecolors='#0D1117', alpha=0.85)
    ax.set_title(title, color='#F9FAFB', fontweight='bold', fontsize=12)

plt.tight_layout()
plt.savefig(f'{FIGURES}/carry_heatmap.png', dpi=150, bbox_inches='tight', facecolor='#0D1117')
plt.close()
print('Saved carry_heatmap.png')
print('All 2.5 figures done.')
