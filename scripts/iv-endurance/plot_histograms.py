#!/usr/bin/env python3
"""Ratio + V_set histograms for iv_sweep_per_cycle_reanalyzed.csv"""

import os, csv
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
import numpy as np
from scipy.optimize import curve_fit

OUT_DIR = '/Users/tai/workspace/projects/active_projects/res_internship/results/data/iv_iv-bipolar-sweep/results'
DATA = '/Users/tai/workspace/projects/active_projects/res_internship/results/data/iv_iv-bipolar-sweep/iv_sweep_endurance_600cycles-iv/iv_sweep_per_cycle_reanalyzed.csv'

os.makedirs(OUT_DIR, exist_ok=True)

# ── Style ─────────────────────────────────────────────────────────────
plt.rcParams.update({
    'font.family': 'sans-serif',
    'font.sans-serif': ['Helvetica', 'Arial'],
    'text.usetex': False,
    'axes.linewidth': 0.8,
    'xtick.direction': 'out',
    'ytick.direction': 'out',
    'xtick.major.size': 3,
    'ytick.major.size': 3,
    'xtick.minor.size': 1.5,
    'ytick.minor.size': 1.5,
})

# ── Cauchy/Lorentz fit ────────────────────────────────────────────────
def lorentzian(x, x0, gamma, A):
    return A * gamma**2 / ((x - x0)**2 + gamma**2)

# ── Padding ────────────────────────────────────────────────────────────
def set_padding(fig):
    fig.tight_layout(pad=0.5)
    h = fig.get_size_inches()[1]
    fig.subplots_adjust(top=1 - 0.5 / 2.54 / h, bottom=1.0 / 2.54 / h)

# ── Read data ─────────────────────────────────────────────────────────
ratios, v_sets = [], []
with open(DATA, 'r') as f:
    for row in csv.DictReader(f):
        if row['ratio']:
            ratios.append(float(row['ratio']))
        if row['v_set']:
            v_sets.append(float(row['v_set']))

ratios = np.array(ratios)
v_sets = np.array(v_sets)
print(f'ratios: {len(ratios)}  v_set: {len(v_sets)}')

C_HIST = '#0000CC'
W_HIST, H_HIST = 6 / 2.54, 6 / 2.54     # ratio histogram
W_HIST_V, H_HIST_V = 4 / 2.54, 5 / 2.54  # v_set histogram

# ══════════════════════════════════════════════════════════════════════
# 1. RATIO HISTOGRAM  (x: 0–100)
# ══════════════════════════════════════════════════════════════════════
print('\nRatio histogram ...')
mask = ratios <= 100
r_clip = ratios[mask]
print(f'  {len(r_clip)} / {len(ratios)} values ≤ 100')

n_bins = int(np.clip(np.sqrt(len(r_clip)), 20, 80))
counts, bin_edges = np.histogram(r_clip, bins=n_bins)
bin_centers = (bin_edges[:-1] + bin_edges[1:]) / 2

# Fit
guess = (np.median(r_clip), np.std(r_clip) * 0.5, counts.max())
try:
    popt, _ = curve_fit(lorentzian, bin_centers, counts, p0=guess, maxfev=5000)
    x0_r, gamma_r, A_r = popt
    print(f'  x₀ = {x0_r:.2f},  γ = {gamma_r:.2f},  A = {A_r:.1f}')
    fit_ok = True
except Exception as e:
    print(f'  fit failed: {e}')
    fit_ok = False

fig, ax = plt.subplots(figsize=(W_HIST, H_HIST))
ax.bar(bin_centers, counts, width=np.diff(bin_edges),
       color=C_HIST, alpha=0.6, edgecolor='white', linewidth=0.3)

if fit_ok:
    x_fine = np.linspace(0, 100, 500)
    y_fit = lorentzian(x_fine, x0_r, gamma_r, A_r)
    ax.plot(x_fine, y_fit, '-', color='#000000', lw=1.0)
    ax.axvline(x0_r, color='#000000', ls='--', lw=0.8, alpha=0.6)

ax.set_xlim(0, 100)
ax.set_ylim(bottom=0)
ax.set_xlabel('Ratio $R_\\mathrm{off}/R_\\mathrm{on}$', fontsize=8)
ax.set_ylabel('Count', fontsize=8)
ax.tick_params(labelsize=7)
set_padding(fig)

out = os.path.join(OUT_DIR, 'ratio_hist_iv-600cycles.pdf')
fig.savefig(out)
plt.close(fig)
print(f'  → {out}')

# ══════════════════════════════════════════════════════════════════════
# 2. V_SET HISTOGRAM  (auto x-range, centred)
# ══════════════════════════════════════════════════════════════════════
print('\nV_set histogram ...')

n_bins = int(np.clip(np.sqrt(len(v_sets)), 20, 60))
counts, bin_edges = np.histogram(v_sets, bins=n_bins)
bin_centers = (bin_edges[:-1] + bin_edges[1:]) / 2

# Fit
guess = (np.median(v_sets), np.std(v_sets) * 0.5, counts.max())
try:
    popt, _ = curve_fit(lorentzian, bin_centers, counts, p0=guess, maxfev=5000)
    x0_v, gamma_v, A_v = popt
    print(f'  x₀ = {x0_v:.4f},  γ = {gamma_v:.4f},  A = {A_v:.1f}')
    fit_ok_v = True
except Exception as e:
    print(f'  fit failed: {e}')
    fit_ok_v = False

fig, ax = plt.subplots(figsize=(W_HIST_V, H_HIST_V))
ax.bar(bin_centers, counts, width=np.diff(bin_edges),
       color=C_HIST, alpha=0.6, edgecolor='white', linewidth=0.3)

if fit_ok_v:
    x_fine = np.linspace(bin_edges[0], bin_edges[-1], 500)
    y_fit = lorentzian(x_fine, x0_v, gamma_v, A_v)
    ax.plot(x_fine, y_fit, '-', color='#000000', lw=1.0)
    ax.axvline(x0_v, color='#000000', ls='--', lw=0.8, alpha=0.6)

    # Centre the peak
    half = max(x0_v - v_sets.min(), v_sets.max() - x0_v, 3 * gamma_v)
    half *= 1.15
    ax.set_xlim(x0_v - half, x0_v + half)

ax.set_ylim(bottom=0)
ax.set_xlabel('$V_\\mathrm{set}$ (V)', fontsize=8)
ax.set_ylabel('Count', fontsize=8)
ax.tick_params(labelsize=7)
set_padding(fig)

out = os.path.join(OUT_DIR, 'vset_hist_iv-600cycles.pdf')
fig.savefig(out)
plt.close(fig)
print(f'  → {out}')

print('\nDone.')
