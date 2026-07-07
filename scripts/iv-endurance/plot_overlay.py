#!/usr/bin/env python3
"""IV overlay: all 600 cycles in grey, highlight cycles 1, 498, 560, 600."""

import os, csv
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
import numpy as np

# ── Paths ──────────────────────────────────────────────────────────────
RAW_DIR = '/Users/tai/workspace/projects/active_projects/res_internship/data/raw'
REANALYZED = '/Users/tai/workspace/projects/active_projects/res_internship/results/data/iv_iv-bipolar-sweep/iv_sweep_endurance_600cycles-iv/iv_sweep_per_cycle_reanalyzed.csv'
OUT_DIR = '/Users/tai/workspace/projects/active_projects/res_internship/results/data/iv_iv-bipolar-sweep/results'
os.makedirs(OUT_DIR, exist_ok=True)

# ── Canonical style ────────────────────────────────────────────────────
CM = 1 / 2.54
W, H = 7, 5  # cm

PAD_L, PAD_R, PAD_B, PAD_T = 1.2, 0.35, 1.0, 0.5
TITLE_SZ, TICK_SZ = 8, 6
LEGEND_SZ, LEGEND_TITLE_SZ = 6, 7

COLORS = ['#f20528', '#e69200', '#0f27db', '#7B2D8E']  # red, orange, blue, purple
LABEL_MAP = {1: '1', 498: '500', 560: '560', 600: '600'}

GREY = '#cccccc'
GREY_LW = 0.3
GREY_ALPHA = 0.4
HIGHLIGHT_LW = 1.2

# ── Parse a LabVIEW IV CSV ────────────────────────────────────────────
def parse_iv(path):
    V, I = [], []
    for line in open(path):
        parts = [p for p in line.strip().split('\t') if p]
        if len(parts) >= 3:
            try:
                V.append(float(parts[0]))
                I.append(float(parts[1]))
            except ValueError:
                continue
    return np.array(V), np.array(I)

# ── Build the overlay ─────────────────────────────────────────────────
# Read reanalyzed CSV to get all filenames
cycles_files = []   # (cycle, filename)
highlight_files = {}  # cycle -> filename
with open(REANALYZED) as f:
    for row in csv.DictReader(f):
        cyc = int(row['cycle'])
        fn = row['filename']
        cycles_files.append((cyc, fn))
        if cyc in LABEL_MAP:
            highlight_files[cyc] = fn

print(f'Total cycles: {len(cycles_files)}')
print(f'Highlights: {list(highlight_files.keys())}')

# Figure
fig = plt.figure(figsize=(W * CM, H * CM))
left_n = PAD_L / W
right_n = 1 - PAD_R / W
bottom_n = PAD_B / H
top_n = 1 - PAD_T / H
ax = fig.add_axes([left_n, bottom_n, right_n - left_n, top_n - bottom_n])

# Plot all cycles in grey background
n_plotted = 0
for cyc, fn in cycles_files:
    fpath = os.path.join(RAW_DIR, fn)
    if not os.path.exists(fpath):
        continue
    V, I = parse_iv(fpath)
    if len(V) < 10:
        continue
    ax.plot(V, I * 1e6, color=GREY, lw=GREY_LW, alpha=GREY_ALPHA, zorder=1)
    n_plotted += 1

print(f'Grey background: {n_plotted} cycles')

# Highlight cycles
handles = []
for i, cyc in enumerate([1, 498, 560, 600]):
    fn = highlight_files.get(cyc)
    if not fn:
        print(f'  ⚠ cycle {cyc} not found')
        continue
    fpath = os.path.join(RAW_DIR, fn)
    V, I = parse_iv(fpath)
    color = COLORS[i % len(COLORS)]
    label = LABEL_MAP[cyc]
    ax.plot(V, I * 1e6, color=color, lw=HIGHLIGHT_LW, zorder=2)
    handles.append(Line2D([0], [0], color=color, lw=1.5, label=label))
    print(f'  {label}: {fpath}')

# Labels
ax.set_xlabel('Voltage (V)', fontsize=TITLE_SZ, fontfamily='Helvetica')
ax.set_ylabel('Current (µA)', fontsize=TITLE_SZ, fontfamily='Helvetica')
ax.tick_params(axis='both', direction='out', labelsize=TICK_SZ)
ax.tick_params(axis='both', which='major', length=3.5)
ax.tick_params(axis='both', which='minor', length=2)
ax.yaxis.set_major_locator(plt.MaxNLocator(nbins=5, steps=[1, 2, 5, 10]))
ax.grid(False)

# Legend
leg = ax.legend(
    handles=handles, fontsize=LEGEND_SZ,
    title='Cycle', title_fontsize=LEGEND_TITLE_SZ,
    loc='upper left', frameon=False,
)
if leg:
    leg.get_title().set_fontname('Helvetica')
    for t in leg.get_texts():
        t.set_fontname('Helvetica')

# Output
out = os.path.join(OUT_DIR, 'iv_overlay_600cycles.pdf')
fig.savefig(out, facecolor='white', edgecolor='none')
plt.close()
print(f'\n→ {out}  ({os.path.getsize(out)/1024:.0f} KB)')
print('Done.')
