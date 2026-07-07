#!/usr/bin/env python3
"""Raman/SERS overlay — 785nm, ND 10%, 20s, 3 accums matched comparison."""

import os, csv
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np

RES = '/Users/tai/workspace/projects/active_projects/res_internship/protocol/3.1_raman-characterization/3-raman/results'

# Matched set: 785nm, ND 10%, 20s, 3 accums
samples = [
    ('ITO',       '250526_ITO(3)_raman_02_processed.csv',       '#000000'),
    ('PDA(n)',    '250526_PDA(n1)-ITO(3)_sers_01_processed.csv', '#0f27db'),
    ('PDA(q)',    '250526_PDA(q1)-ITO(3)_sers_03_processed.csv', '#f20528'),
]

def read_csv(path, norm=True):
    shift, intensity = [], []
    with open(path) as f:
        reader = csv.DictReader(f)
        for row in reader:
            shift.append(float(row['shift(cm⁻¹)']))
            intensity.append(float(row['intensity']))
    shift, intensity = np.array(shift), np.array(intensity)
    if norm:
        mx = np.max(intensity)
        if mx > 0:
            intensity = intensity / mx
    return shift, intensity

plt.rcParams.update({
    'font.family': 'sans-serif',
    'font.sans-serif': ['Helvetica', 'Arial'],
    'axes.linewidth': 0.8,
    'xtick.direction': 'out',
    'ytick.direction': 'out',
    'xtick.major.size': 3,
    'ytick.major.size': 3,
})

CM = 1 / 2.54

# ══════════════════════════════════════════════════════════════════════
#  INDIVIDUAL PLOTS
# ══════════════════════════════════════════════════════════════════════
for label, fn, c in samples:
    shift, intensity = read_csv(os.path.join(RES, fn))
    fig, ax = plt.subplots(figsize=(8 * CM, 5 * CM))
    ax.plot(shift, intensity, '-', color=c, lw=0.6)
    ax.set_xlim(800, 2000)
    ax.set_xlabel('Raman shift (cm⁻¹)', fontsize=8)
    ax.set_ylabel('Normalized intensity', fontsize=8)
    ax.tick_params(labelsize=7)
    fig.tight_layout(pad=0.5)
    h = fig.get_size_inches()[1]
    fig.subplots_adjust(top=1 - 0.5 / 2.54 / h, bottom=1.0 / 2.54 / h)
    out = os.path.join(RES, f'raman_{label}_indiv.pdf')
    fig.savefig(out)
    plt.close()
    print(f'  → raman_{label}_indiv.pdf  ({len(shift)} pts)')

# ══════════════════════════════════════════════════════════════════════
#  OVERLAY PLOT
# ══════════════════════════════════════════════════════════════════════
fig, ax = plt.subplots(figsize=(8 * CM, 6 * CM))

offsets = [0, 1.2, 0.6]  # ITO=0, PDA(n)=+1.2, PDA(q)=+0.6

for (label, fn, c), off in zip(samples, offsets):
    shift, intensity = read_csv(os.path.join(RES, fn))
    ax.plot(shift, intensity + off, '-', color=c, lw=0.7, label=label)

ax.set_xlim(800, 2000)
ax.set_xlabel('Raman shift (cm⁻¹)', fontsize=8)
ax.set_ylabel('Intensity (a.u.)', fontsize=8)
ax.tick_params(labelsize=7)
ax.legend(fontsize=6.5, frameon=False, loc='upper right')

fig.tight_layout(pad=0.5)
h = fig.get_size_inches()[1]
fig.subplots_adjust(top=1 - 0.5 / 2.54 / h, bottom=1.0 / 2.54 / h)

out = os.path.join(RES, 'overlay_raman_sers_785nm.pdf')
fig.savefig(out)
plt.close()
print(f'\n→ overlay_raman_sers_785nm.pdf\nDone.')
