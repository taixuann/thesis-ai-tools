#!/usr/bin/env python3
"""Three-line table PDF — rows: Normal/Doping, cols: peaks, cells: Area %."""

import os
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

OUT = '/Users/tai/workspace/projects/active_projects/res_internship/protocol/3.1_raman-characterization/3-raman/results'
TARGET = '/Users/tai/workspace/projects/active_projects/res_internship/results/data/characterization_raman'

CM = 1 / 2.54

# ── Data ───────────────────────────────────────────────────────────────
# Peak positions/areas from deconvolution
# Format: (x0, area %, or '—' if excluded)
peaks = {
    'D-band':           ('1296', '13.5', '1348', '17.9'),
    'C=N / quinone-imine': ('1409',  '—', '1406', '14.4'),
    'N-H / indole':     ('1488', '46.7', '1480', '42.7'),
    'G-band':           ('1579', '39.7', '1592', '25.0'),
}

col_labels = list(peaks.keys())
row_labels = ['Doping', 'Normal']

cell_text = []
# Build cell content: "x₀ cm⁻¹\nArea: X.X%"
for row_idx, label in enumerate(row_labels):
    row_data = []
    for peak_name, vals in peaks.items():
        x0 = vals[row_idx * 2]
        pct = vals[row_idx * 2 + 1]
        row_data.append(f'{x0} cm⁻¹\n{pct}%')
    cell_text.append(row_data)

# Match data order to row order: Doping first, Normal second
cell_text.reverse()

# ── Render ─────────────────────────────────────────────────────────────
plt.rcParams.update({
    'font.family': 'sans-serif',
    'font.sans-serif': ['Helvetica', 'Arial'],
})

fig, ax = plt.subplots(figsize=(7.5 * CM, 8 * CM))
ax.axis('off')

# Title
ax.text(0.5, 0.90, 'Table 1. Lorentzian deconvolution of Raman spectra',
        transform=ax.transAxes, fontsize=6.5, fontweight='bold',
        ha='center', va='center')

ax.text(0.5, 0.865, 'PDA normal vs. PDA doping — 785 nm, ND 10%, 20 s, 3 accums',
        transform=ax.transAxes, fontsize=5, ha='center', va='center',
        style='italic', color='#555555')

# Short column labels to fit
col_labels_short = ['D-band', 'C=N\nquinone-imine', 'N-H\nindole', 'G-band']

# Row label column + 4 peak columns
n_cols = len(col_labels) + 1  # +1 for row labels
n_rows = len(row_labels) + 1  # +1 for header

# Build full table including row labels
all_text = [[''] + col_labels_short]
for i, label in enumerate(row_labels):
    all_text.append([label] + cell_text[i])

bbox = [0.04, 0.22, 0.92, 0.55]
tbl = ax.table(cellText=all_text, loc='center', cellLoc='center', bbox=bbox)
tbl.auto_set_font_size(False)
tbl.set_fontsize(5.5)

# Style
for key, cell in tbl.get_celld().items():
    cell.set_linewidth(0)
    cell.set_edgecolor('white')
    # Header row and row labels
    if key[0] == 0 or key[1] == 0:
        cell.set_text_props(fontweight='bold', fontsize=5.5)

# Three horizontal lines
x0, x1 = bbox[0], bbox[0] + bbox[2]
y0, y1 = bbox[1], bbox[1] + bbox[3]
row_h = bbox[3] / n_rows

ax.plot([x0, x1], [y1, y1], transform=ax.transAxes, color='black', lw=0.8)
ax.plot([x0, x1], [y1 - row_h, y1 - row_h], transform=ax.transAxes, color='black', lw=0.5)
ax.plot([x0, x1], [y0, y0], transform=ax.transAxes, color='black', lw=0.8)

# Footnote
ax.text(x0, y0 - 0.06,
        'Peak 2 (C=N) in PDA normal: negative amplitude, excluded.\n'
        'Area = A × γ × π (Lorentzian).  D/G = D-band / G-band area ratio.',
        transform=ax.transAxes, fontsize=4.5, color='#555555', ha='left', va='top')

# ── Save ───────────────────────────────────────────────────────────────
fig.subplots_adjust(left=0, right=1, bottom=0, top=1)
for d in [OUT, TARGET]:
    os.makedirs(d, exist_ok=True)
    fp = os.path.join(d, 'raman_table.pdf')
    fig.savefig(fp)
    print(f'→ {fp}')

plt.close()
print('Done.')
