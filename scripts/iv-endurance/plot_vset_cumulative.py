#!/usr/bin/env python3
"""Cumulative probability plots of V_set for iv_sweep_endurance_600cycles-iv.

Produces two publication-ready figures:
  1. vset_cdf_by_compliance  — CDF of V_set split by compliance regime
  2. vset_weibull            — Weibull plot of V_set (full-compliance subset)

Data source: iv_sweep_per_cycle_reanalyzed.csv (preferred SCLC method)
              + iv_sweep_per_cycle.csv (for compliance/I_peak columns).
"""

import os, sys, csv
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from scipy.optimize import curve_fit
from scipy.stats import linregress, norm

# ── Paths ──────────────────────────────────────────────────────────────
DATA_DIR = os.path.dirname(os.path.abspath(__file__))
REANALYZED = os.path.join(DATA_DIR, 'iv_sweep_per_cycle_reanalyzed.csv')
ORIGINAL   = os.path.join(DATA_DIR, 'iv_sweep_per_cycle.csv')

# ── Style (matching existing plots in this directory) ──────────────────
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

CM = 1 / 2.54  # cm → inches

C_SCATTER = '#000000'  # black (data points)
C_FIT     = '#009E73'  # green (Weibull fit line)

# ══════════════════════════════════════════════════════════════════════
# 1. LOAD & MERGE DATA
# ══════════════════════════════════════════════════════════════════════
print('Loading data ...')

# Read reanalyzed CSV (preferred V_set values)
reanalyzed = {}
with open(REANALYZED) as f:
    for row in csv.DictReader(f):
        cyc = int(row['cycle'])
        reanalyzed[cyc] = {
            'cycle': cyc,
            'v_set': float(row['v_set']) if row['v_set'] else np.nan,
            'ratio': float(row['ratio']) if row['ratio'] else np.nan,
        }

# Read original CSV (compliance info)
original = {}
with open(ORIGINAL) as f:
    for row in csv.DictReader(f):
        cyc = int(row['cycle'])
        original[cyc] = {
            'i_peak': float(row['I_peak_A']) if row['I_peak_A'] else 0,
            'reached_compliance': row['reached_compliance'].strip() == 'True',
            'ratio_orig': float(row['ratio_HRS_LRS']) if row['ratio_HRS_LRS'] else 0,
        }

# Merge on cycle number
merged = []
for cyc in sorted(set(reanalyzed) & set(original)):
    r = reanalyzed[cyc]
    o = original[cyc]
    merged.append({
        'cycle': cyc,
        'v_set': r['v_set'],
        'ratio': r['ratio'] if not np.isnan(r['ratio']) else o['ratio_orig'],
        'i_peak': o['i_peak'],
        'reached_compliance': o['reached_compliance'],
    })

print(f'  Merged {len(merged)} cycles')

# ── Apply clean filter (per README: ratio >= 10, V_set > 0.1, I_peak >= 9.99e-6) ──
clean = [d for d in merged
         if d['ratio'] >= 10
         and d['v_set'] > 0.1
         and not np.isnan(d['v_set'])
         and d['i_peak'] >= 9.99e-7]  # slightly relaxed — any measurable I

print(f'  Clean subset: {len(clean)} cycles')

# Split by compliance regime
full_comp = [d for d in clean if d['i_peak'] >= 9.99e-6 and d['reached_compliance']]
sub_comp  = [d for d in clean if d['i_peak'] < 9.99e-6 or not d['reached_compliance']]

print(f'  Full compliance (≥10 µA, reached): {len(full_comp)} cycles')
print(f'  Sub-compliance (<10 µA or not reached): {len(sub_comp)} cycles')

if len(full_comp) == 0:
    print('ERROR: No full-compliance data points. Cannot proceed.')
    sys.exit(1)

# ══════════════════════════════════════════════════════════════════════
# 2. HELPER: Empirical CDF
# ══════════════════════════════════════════════════════════════════════
def ecdf(x):
    """Return sorted x, cumulative probability F (Hazen median rank)."""
    x_sorted = np.sort(x)
    n = len(x_sorted)
    F = (np.arange(1, n + 1) - 0.3) / (n + 0.4)  # median rank
    return x_sorted, F

def weibull_transform(F):
    """Weibull y = ln(-ln(1 - F))."""
    return np.log(-np.log(1 - F))

def weibull_fit(v_set):
    """Fit Weibull distribution: returns (beta, eta, r_squared)."""
    x_sorted, F = ecdf(v_set)
    y = weibull_transform(F)
    x = np.log(x_sorted)
    slope, intercept, r_value, _, _ = linregress(x, y)
    beta = slope
    eta = np.exp(-intercept / beta)
    return beta, eta, r_value**2, x, y

# ══════════════════════════════════════════════════════════════════════
# 3. WEIBULL FIT (used by both plots)
# ══════════════════════════════════════════════════════════════════════
v_full = np.array([d['v_set'] for d in full_comp])

beta, eta, r2, x_w, y_w = weibull_fit(v_full)
print(f'Weibull fit: β = {beta:.3f}, η = {eta:.4f} V, R² = {r2:.4f}')

# Theoretical Weibull CDF: F(V) = 1 - exp(-(V/η)^β)
def weibull_cdf(V, eta, beta):
    return 1 - np.exp(-(V / eta)**beta)

# ══════════════════════════════════════════════════════════════════════
# 4. PLOT 1: CDF — black scatter + red Weibull fit
# ══════════════════════════════════════════════════════════════════════
print('\nPlot 1: CDF (scatter + Weibull fit) ...')

x_full, F_full = ecdf(v_full)

# Figure dimensions: 6.5 × 8 cm
W1, H1 = 6.5 * CM, 8 * CM

# Axes position: bottom 1 cm, top 0.5 cm padding
left   = 1.2 / 6.5
right  = 1 - 0.3 / 6.5
bottom = 1.0 / 8.0
top    = 1 - 0.5 / 8.0

fig = plt.figure(figsize=(W1, H1))
ax = fig.add_axes([left, bottom, right - left, top - bottom])

# Probability (probit) scale
y_probit = norm.ppf(F_full)
V_smooth = np.linspace(v_full.min(), v_full.max(), 500)
F_smooth = weibull_cdf(V_smooth, eta, beta)
y_fit_probit = norm.ppf(F_smooth)

# Scatter: red fill + dark red edge (downsampled every 3rd point)
ax.scatter(x_full[::3], y_probit[::3], s=30, facecolors='#CC0000',
           edgecolors='#990000', linewidths=0.5, alpha=0.85, zorder=2)

# Black fit line: theoretical Weibull CDF (on top layer, thicker)
ax.plot(V_smooth, y_fit_probit, '-', color='#000000', lw=0.75, zorder=3)

ax.set_xlim(0, 1.0)

# Probability axis (6 ticks)
prob_ticks = np.array([0.001, 0.01, 0.1, 0.5, 0.9, 0.99])
ytick_pos = norm.ppf(prob_ticks)
ytick_labels = ['0.1', '1', '10', '50', '90', '99']
ax.set_ylim(norm.ppf(0.001), norm.ppf(0.999))
ax.set_yticks(ytick_pos)
ax.set_yticklabels(ytick_labels, fontsize=6)
ax.set_xlabel('$V_\\mathrm{set}$ (V)', fontsize=8)
ax.set_ylabel('Cumulative probability (%)', fontsize=8)
ax.tick_params(axis='x', which='major', direction='out',
               labelsize=6, length=3)
ax.tick_params(axis='both', which='minor', length=0)

# Save
out_cdf = os.path.join(DATA_DIR, 'vset_cdf_by_compliance.pdf')
fig.savefig(out_cdf, dpi=600, facecolor='white')
out_cdf_png = out_cdf.replace('.pdf', '.png')
fig.savefig(out_cdf_png, dpi=600, facecolor='white')
plt.close(fig)
print(f'  → {out_cdf}')
print(f'  → {out_cdf_png}')

# ══════════════════════════════════════════════════════════════════════
# 5. PLOT 2: Weibull Plot (full compliance only)
# ══════════════════════════════════════════════════════════════════════
print('\nPlot 2: Weibull plot ...')

# Generate fit line
v_fit = np.linspace(v_full.min(), v_full.max(), 200)
x_fit_line = np.log(v_fit)
y_fit_line = beta * x_fit_line - beta * np.log(eta)

W2, H2 = 4.5 * CM, 4.5 * CM

fig, ax = plt.subplots(figsize=(W2, H2))

# Primary y-axis: ln(-ln(1-F))
ax.scatter(np.exp(x_w), y_w, s=8, color=C_SCATTER, alpha=0.7,
           edgecolors='none', zorder=2, label='Data')

# Fit line
ax.plot(np.exp(x_fit_line), y_fit_line, '-', color=C_FIT, lw=1.0,
        zorder=1, label=f'Weibull fit (β={beta:.2f})')

# Annotate
text = (f'$\\beta = {beta:.2f}$\n'
        f'$\\eta = {eta:.4f}\\,\\mathrm{{V}}$\n'
        f'$R^2 = {r2:.3f}$')
ax.text(0.95, 0.95, text, transform=ax.transAxes, fontsize=6,
        ha='right', va='top', color='#333333')

# Axis labels
ax.set_xlabel('$V_\\mathrm{set}$ (V)', fontsize=7)
ax.set_ylabel('$\\ln(-\\ln(1-F))$', fontsize=7)
ax.tick_params(labelsize=6)

# Secondary y-axis: cumulative probability
ax2 = ax.twinx()
# Map y-ticks on secondary axis: find cumulative probs that map to nice Weibull y-values
prob_ticks = np.array([0.01, 0.05, 0.1, 0.25, 0.5, 0.75, 0.9, 0.95, 0.99])
y_ticks2 = weibull_transform(prob_ticks)
# Filter to visible range
ylim = ax.get_ylim()
mask = (y_ticks2 >= ylim[0] - 1) & (y_ticks2 <= ylim[1] + 1)
prob_ticks = prob_ticks[mask]
y_ticks2 = y_ticks2[mask]
ax2.set_yticks(y_ticks2)
ax2.set_yticklabels([f'{p*100:.0f}%' for p in prob_ticks], fontsize=5.5)
ax2.set_ylabel('Cumulative probability $F$', fontsize=6)
ax2.tick_params(labelsize=5.5)

# Legend
lines1, labels1 = ax.get_legend_handles_labels()
ax.legend(lines1, labels1, fontsize=5.5, loc='lower right', frameon=False)

# Tight layout
fig.tight_layout(pad=0.3)

# Save
out_w = os.path.join(DATA_DIR, 'vset_weibull.pdf')
fig.savefig(out_w, dpi=600, facecolor='white')
out_w_png = out_w.replace('.pdf', '.png')
fig.savefig(out_w_png, dpi=300, facecolor='white')
plt.close(fig)
print(f'  → {out_w}')
print(f'  → {out_w_png}')

# ══════════════════════════════════════════════════════════════════════
# 5. SUMMARY
# ══════════════════════════════════════════════════════════════════════
print('\n' + '=' * 60)
print('SUMMARY')
print('=' * 60)
print(f'Full compliance (n={len(v_full)}):')
print(f'  Median V_set = {np.median(v_full):.4f} V')
print(f'  Mean V_set   = {np.mean(v_full):.4f} V')
print(f'  Std V_set    = {np.std(v_full):.4f} V')
print(f'  Weibull β    = {beta:.3f}   (larger = more deterministic)')
print(f'  Weibull η    = {eta:.4f} V  (63.2% percentile)')
print(f'  Weibull R²   = {r2:.4f}')
v_sub_arr = np.array([d['v_set'] for d in sub_comp])
if len(v_sub_arr) > 0:
    print(f'Sub-compliance (n={len(v_sub_arr)}):')
    print(f'  Median V_set = {np.median(v_sub_arr):.4f} V')
    print(f'  Mean V_set   = {np.mean(v_sub_arr):.4f} V')
    print(f'  Std V_set    = {np.std(v_sub_arr):.4f} V')
print(f'Output files in: {DATA_DIR}')
print('  vset_cdf_by_compliance.pdf / .png')
print('  vset_weibull.pdf / .png')
print('Done.')
