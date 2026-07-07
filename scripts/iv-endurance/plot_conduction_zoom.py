#!/usr/bin/env python3
"""Forward + reverse sweep — cycle 005. Two outputs:
   1. conduction_zoom_cycle005.pdf  — linear V, log₁₀|I| (clean)
   2. conduction_slopes_cycle005.pdf — log-log with slope guide lines
"""

import os
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np

RAW_DIR = '/Users/tai/workspace/projects/active_projects/res_internship/data/raw'
OUT_DIR = '/Users/tai/workspace/projects/active_projects/res_internship/results/data/iv_iv-bipolar-sweep/results'
os.makedirs(OUT_DIR, exist_ok=True)

FN = '130526-090105_keithley-2400_cu-c-pda(q)-ito_r1-c4_iv-bipolar-sweep_005.csv'

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

V, I = parse_iv(os.path.join(RAW_DIR, FN))

# Split: 0 → +Vmax → 0
idx_max = np.argmax(V)
after_max = V[idx_max:]
idx_zero = np.argmin(np.abs(after_max)) + idx_max

V_fwd_raw = V[:idx_max+1]
I_fwd_raw_abs = np.abs(I[:idx_max+1])
V_rev_raw = V[idx_max:idx_zero+1]
I_rev_raw_abs = np.abs(I[idx_max:idx_zero+1])

# Filter zeros for log
mask_fwd = I_fwd_raw_abs > 0
mask_rev = I_rev_raw_abs > 0

V_fwd = V_fwd_raw[mask_fwd]
I_fwd_abs = I_fwd_raw_abs[mask_fwd]
logI_fwd = np.log10(I_fwd_abs)

V_rev = V_rev_raw[mask_rev]
I_rev_abs = I_rev_raw_abs[mask_rev]
logI_rev = np.log10(I_rev_abs)

print(f'Forward: {len(V_fwd)} pts, logI [{logI_fwd[0]:.1f}, {logI_fwd[-1]:.1f}]')
print(f'Reverse: {len(V_rev)} pts')

# ── Style ──────────────────────────────────────────────────────────────
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
#  PLOT 1 — Linear V, log₁₀ |I|  (clean, 4 × 5 cm)
# ══════════════════════════════════════════════════════════════════════
fig1, ax1 = plt.subplots(figsize=(4 * CM, 5 * CM))

ax1.plot(V_fwd, logI_fwd, 'o-', color='#000000', ms=4, lw=0.8,
         markerfacecolor='#000000', markeredgewidth=0)
ax1.plot(V_rev, logI_rev, 's-', color='#000000', ms=3, lw=0.8,
         markerfacecolor='#000000', markeredgewidth=0)

ax1.set_xlim(0, None)
ax1.set_xlabel('Voltage (V)', fontsize=8)
ax1.set_ylabel('log₁₀ |I| (A)', fontsize=8)
ax1.tick_params(labelsize=7)

fig1.tight_layout(pad=0.5)
h1 = fig1.get_size_inches()[1]
fig1.subplots_adjust(top=1 - 0.5 / 2.54 / h1, bottom=1.0 / 2.54 / h1)

out1 = os.path.join(OUT_DIR, 'conduction_zoom_cycle005.pdf')
fig1.savefig(out1)
plt.close(fig1)
print(f'→ {out1}')

# ══════════════════════════════════════════════════════════════════════
#  PLOT 2 — Log-log with fitted slopes  (5 × 5 cm)
# ══════════════════════════════════════════════════════════════════════
from scipy.optimize import curve_fit

# Fit regions — use only V > 0
pos = V_fwd > 1e-6
V_pos = V_fwd[pos]
logI_pos = logI_fwd[pos]

m_noise = V_pos < 0.3
m_set = (V_pos >= 0.55) & (V_pos < 0.72)

def lin(x, a, b):
    return a * x + b

logV = np.log10(V_pos)

p_noise, _ = curve_fit(lin, logV[m_noise], logI_pos[m_noise])
p_set, _ = curve_fit(lin, logV[m_set], logI_pos[m_set])

slope_noise = p_noise[0]
slope_set = p_set[0]

print(f'  Pre-SET slope: {slope_noise:.3f}')
print(f'  SET slope:     {slope_set:.2f}')

fig2, ax2 = plt.subplots(figsize=(5 * CM, 5 * CM))

ax2.loglog(V_fwd, I_fwd_abs, 'o-', color='#000000', ms=4, lw=0.8,
           markerfacecolor='#000000', markeredgewidth=0, zorder=3)
ax2.loglog(V_rev, I_rev_abs, 's-', color='#f20528', ms=3, lw=0.8,
           markerfacecolor='#f20528', markeredgewidth=0, zorder=2, alpha=0.5)

# Fitted lines
Vn = np.logspace(logV[m_noise][0], logV[m_noise][-1], 20)
In = 10**lin(np.log10(Vn), *p_noise)
ax2.loglog(Vn, In, '--', color='#0f27db', lw=1.0, zorder=1)

Vs = np.logspace(logV[m_set][0], logV[m_set][-1], 20)
Is = 10**lin(np.log10(Vs), *p_set)
ax2.loglog(Vs, Is, '--', color='#f20528', lw=1.0, zorder=1)

# Labels
ax2.annotate(f'Pre-SET\nslope = {slope_noise:.2f}',
             xy=(0.02, 1.2e-8), fontsize=5.5, color='#0f27db', ha='left')
ax2.annotate(f'SET\nslope = {slope_set:.0f}',
             xy=(0.6, 2e-7), fontsize=5.5, color='#f20528', ha='left',
             bbox=dict(boxstyle='round,pad=0.2', fc='white', ec='none', alpha=0.8))

ax2.set_xlabel('Voltage (V)', fontsize=8)
ax2.set_ylabel('|Current| (A)', fontsize=8)
ax2.tick_params(labelsize=7)

fig2.tight_layout(pad=0.5)
h2 = fig2.get_size_inches()[1]
fig2.subplots_adjust(top=1 - 0.5 / 2.54 / h2, bottom=1.0 / 2.54 / h2)

out2 = os.path.join(OUT_DIR, 'conduction_slopes_cycle005.pdf')
fig2.savefig(out2)
plt.close(fig2)
print(f'→ {out2}')
print('Done.')
