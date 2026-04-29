# Football Analytics Blog

Python-based football analytics using Statsbomb Open Data and GPS tracking benchmarks.

## Structure

```
Blog/
├── BLOG_PLAN.md                    ← Full editorial plan (21 articles)
├── assets/
│   ├── helpers/
│   │   ├── data_loader.py          ← Shared loader functions (events, matches, 360°)
│   │   └── pitch.py                ← Reusable pitch drawing function
│   └── figures/                    ← Shared visualizations
│
├── 01_Einstieg/                    ← Series 1: Getting Started with Football Analytics
│   ├── 1.1_Event_Data_Einstieg/    ✓ done
│   ├── 1.2_Pitch_in_Python/        ✓ done
│   ├── 1.3_Shot_Maps/              ✓ done
│   ├── 1.4_Pass_Netzwerke/         ✓ done
│   └── 1.5_Heatmaps/              ✓ done
│
├── 02_Tactical_Analysis/           ← Series 2: Tactical Analysis
│   ├── 2.1_xG_Erklaert/
│   ├── 2.2_Pressing_PPDA/
│   ├── 2.3_Through_Balls/
│   ├── 2.4_Freeze_Frames/
│   ├── 2.5_Carries/
│   └── 2.6_360_Daten/
│
├── 03_Physical_Performance/        ← Series 3: Physical Performance Analytics
│   ├── assets/
│   │   ├── generate_data.py        ← Synthetic GPS dataset generator
│   │   └── physical_data_synthetic.csv
│   ├── P.1_GPS_Introduction/       ✓ done
│   ├── P.2_Sprint_Profiles/
│   ├── P.3_Distance_Analysis/
│   ├── P.4_Acceleration_Load/
│   └── P.5_Pressing_Space/
│
└── 04_Deep_Dives/                  ← Series 4: Deep Dive Analyses
    ├── 4.1_Messi_Karriere/
    ├── 4.2_Barcelona_2015_16/
    ├── 4.3_Frauen_WM_Vergleich/
    ├── 4.4_Champions_League_Finals/
    └── 4.5_Leverkusen_2023_24/
```

Each article folder contains:
- `article.md` — blog post
- `notebook.ipynb` — Jupyter notebook with full code
- `figures/` — exported visualizations

## Data Sources

**Statsbomb Open Data** (local):
```
/Users/stefanhofmann/Documents/Bewerbung/Interviews/Hudl/statsbomb_explorer/open-data/data/
```
3,464 matches · 75 seasons · 13 GB event data + 360° tracking

**Synthetic GPS Dataset** (Series 3):
```
/Users/stefanhofmann/Documents/Bewerbung/Portfolio/Blog/03_Physical_Performance/assets/physical_data_synthetic.csv
```
Generated from published sports science benchmarks (Mohr et al. 2003, Bradley et al. 2009, Di Salvo et al. 2007)

## Quick Start (Statsbomb notebooks)

```python
import sys
sys.path.append("/Users/stefanhofmann/Documents/Bewerbung/Portfolio/Blog/assets/helpers")

from data_loader import load_competitions, load_matches, load_events, flatten_events
from pitch import draw_pitch
```

## Quick Start (Physical Performance notebooks)

```python
import pandas as pd
df = pd.read_csv('/Users/stefanhofmann/Documents/Bewerbung/Portfolio/Blog/03_Physical_Performance/assets/physical_data_synthetic.csv')
```

## Publication Order

```
BATCH 1 — Series 1 complete (ready to publish)
  1.1 · 1.2 · 1.3 · 1.4 · 1.5

BATCH 2 — Series 2: Tactical Analysis
  2.1 xG · 2.2 PPDA · 2.3 Through Balls · 2.4 Freeze Frames · 2.5 Carries · 2.6 360°

BATCH 3 — Series 3: Physical Performance
  P.1 GPS Intro · P.2 Sprints · P.3 Distance · P.4 Accelerations · P.5 Pressing Space

BATCH 4 — Series 4: Deep Dives
  Messi · Barcelona 2015/16 · Women's WC · CL Finals · Leverkusen 2023/24
```
