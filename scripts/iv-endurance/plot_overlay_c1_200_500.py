#!/usr/bin/env python3
"""IV overlay: all cycles in grey, highlight cycles 1, 200, 500."""

import os, csv
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
import numpy as np

RAW_DIR = '/Users/tai/workspace/projects/active_projects/res_internship/data/raw'
REANALYZED = os.path.join(os.path.dirname(__file__), 'iv_sweep_per_cycle_reanalyzed.csv')
OUT_DIR = os.path.dirname(__file__)

CM = 1 / 2.54
W, H = 7, 5
PAD_L, PAD_R, PAD_B, PAD_T = 1.2, 0.35, 1.0, 0.5
TITLE_SZ, TICK_SZ = 8, 6
LEGEND_SZ = 6

COLORS = ['#333333', '#f20528', '#0f27db']
LABEL_MAP = {1: '1', 200: '200', 500: '500'}
GREY = '#cccccc'
GREY_LW = 0.3
GREY_ALPHA = 0.4
HIGHLIGHT_LW = 1.2

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

cycles_files = []
highlight_files = {}
with open(REANALYZED) as f:
    for row in csv.DictReader(f):
        cyc = int(row['cycle'])
        fn = row['filename']
        cycles_files.append((cyc, fn))
        if cyc in LABEL_MAP:
            highlight_files[cyc] = fn

fig = plt.figure(figsize=(W * CM, H * CM))
left_n = PAD_L / W
right_n = 1 - PAD_R / W
bottom_n = PAD_B / H
top_n = 1 - PAD_T / H
ax = fig.add_axes([left_n, bottom_n, right_n - left_n, top_n - bottom_n])

for cyc, fn in cycles_files:
    fpath = os.path.join(RAW_DIR, fn)
    if not os.path.exists(fpath):
        continue
    V, I = parse_iv(fpath)
    if len(V) < 10:
        continue
    if (I * 1e6).min() < -5:
        continue
    ax.plot(V, I * 1e6, color=GREY, lw=GREY_LW, alpha=GREY_ALPHA, zorder=1)

handles = []
for i, cyc in enumerate([1, 200, 500]):
    fn = highlight_files.get(cyc)
    if not fn:
        continue
    fpath = os.path.join(RAW_DIR, fn)
    V, I = parse_iv(fpath)
    color = COLORS[i % len(COLORS)]
    ax.plot(V, I * 1e6, color=color, lw=HIGHLIGHT_LW, zorder=2, label=LABEL_MAP[cyc])

ax.set_xlabel('Voltage (V)', fontsize=TITLE_SZ, fontfamily='Helvetica')
ax.set_ylabel('Current (µA)', fontsize=TITLE_SZ, fontfamily='Helvetica')
ax.tick_params(axis='both', direction='out', labelsize=TICK_SZ)
ax.tick_params(axis='both', which='major', length=3.5)
ax.tick_params(axis='both', which='minor', length=2)
ax.set_ylim(-5, None)
ax.yaxis.set_major_locator(plt.MaxNLocator(nbins=5, steps=[1, 2, 5, 10]))
ax.grid(False)

leg = ax.legend(fontsize=LEGEND_SZ, loc='lower right', frameon=False)
if leg:
    for t in leg.get_texts():
        t.set_fontname('Helvetica')

out = os.path.join(OUT_DIR, 'iv_overlay_highlight_c1_200_500.pdf')
fig.savefig(out, facecolor='white', edgecolor='none')
plt.close()
print(f'Done. → {out}')
