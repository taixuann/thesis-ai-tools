#!/usr/bin/env python3
"""Refined deconvolution zoom: pure_polymer_zoom style + deconvolution components.
Normalized, dual y-axis with specified ranges, labels from deconvolution."""

import os, csv
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
from scipy.optimize import curve_fit
from scipy import sparse
from scipy.sparse.linalg import spsolve

RAW = '/Users/tai/workspace/projects/active_projects/res_internship/results/data/characterization_raman/sources'
OUT = '/Users/tai/workspace/projects/active_projects/res_internship/results/data/characterization_raman'
os.makedirs(OUT, exist_ok=True)

samples = {
    'ITO': {'file': '250526_ITO_raman_02.txt'},
    'PDA(n)-ITO SERS': {'file': '250526_PDA(n)-ITO_sers_01.txt'},
    'PDA(q)-ITO SERS': {'file': '250526_PDA(q)-ITO_sers_03.txt'},
}

def read_raw(path, lo=800, hi=2000):
    shift, intensity = [], []
    for line in open(path, encoding='latin-1'):
        if line.startswith('#'):
            continue
        parts = line.strip().split(';')
        if len(parts) >= 2:
            try:
                shift.append(float(parts[0]))
                intensity.append(float(parts[1]))
                continue
            except ValueError:
                pass
        parts = line.strip().split('\t')
        if len(parts) >= 2:
            try:
                s = float(parts[0].replace(',', '.'))
                i = float(parts[1].replace(',', '.'))
                if lo <= s <= hi:
                    shift.append(s)
                    intensity.append(i)
            except ValueError:
                continue
    return np.array(shift), np.array(intensity)

def find_scale_factor(pda_s, pda_i, ito_s, ito_i, region=(1050, 1150)):
    m = (pda_s >= region[0]) & (pda_s <= region[1])
    if np.sum(m) < 5:
        return 0, 0
    s_region = pda_s[m]
    ito_interp = np.interp(s_region, ito_s, ito_i)
    pda_region = pda_i[m]
    A = np.vstack([ito_interp, np.ones_like(ito_interp)]).T
    k, c = np.linalg.lstsq(A, pda_region, rcond=None)[0]
    return k, c

data = {}
for label, info in samples.items():
    s, i = read_raw(os.path.join(RAW, info['file']))
    data[label] = (s, i)

ito_s, ito_i = data['ITO']
factors = {}
for label in ['PDA(n)-ITO SERS', 'PDA(q)-ITO SERS']:
    s, i = data[label]
    k, c = find_scale_factor(s, i, ito_s, ito_i)
    factors[label] = (k, c)

pure = {}
for label in ['PDA(n)-ITO SERS', 'PDA(q)-ITO SERS']:
    s, i = data[label]
    k, c = factors[label]
    ito_interp = np.interp(s, ito_s, ito_i)
    pure[label.replace('-ITO SERS', '')] = (s, i - k * ito_interp)

def lorentzian(x, x0, gamma, A):
    return A * gamma**2 / ((x - x0)**2 + gamma**2)

def multi_lorentz(x, *params):
    n = len(params) // 3
    y = np.zeros_like(x)
    for i in range(n):
        y += lorentzian(x, params[3*i], params[3*i+1], params[3*i+2])
    return y

peak_guesses = [
    (1340, 50, 0.4),
    (1410, 45, 0.2),
    (1490, 50, 0.4),
    (1590, 40, 0.6),
]

deconv_results = {}
for label in ['PDA(n)', 'PDA(q)']:
    s, i = pure[label]
    mask = (s >= 1200) & (s <= 1700)
    xs, ys = s[mask], i[mask]
    baseline = np.interp(xs, [xs[0], xs[-1]], [ys[0], ys[-1]])
    ys_corr = ys - baseline
    ys_corr = ys_corr / np.max(np.abs(ys_corr))
    p0 = [v for guess in peak_guesses for v in guess]
    lower_bounds = []
    upper_bounds = []
    for x0_guess, gamma_guess, A_guess in peak_guesses:
        lower_bounds += [x0_guess - 50, 20.0, 0]
        upper_bounds += [x0_guess + 50, 150, 2.0]
    popt, _ = curve_fit(multi_lorentz, xs, ys_corr, p0=p0,
                         bounds=(lower_bounds, upper_bounds), maxfev=10000)
    deconv_results[label] = {
        'params': [(popt[3*i], popt[3*i+1], popt[3*i+2]) for i in range(len(popt)//3)],
        'xs': xs, 'ys_corr': ys_corr,
        'y_fit': multi_lorentz(xs, *popt),
    }

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

peak_colors = ['#0f27db', '#009e73', '#e69200', '#bd046a']
peak_labels_short = ['D-band', 'C=N / quinone-imine', 'N-H / indole', 'G-band']

fig, ax1 = plt.subplots(figsize=(7.5 * CM, 8 * CM))
ax2 = ax1.twinx()

# ── y1 (left): PDA(q) — doping — ylim 0 to 0.4 ──
res_q = deconv_results['PDA(q)']
xs_q, ys_q, yf_q = res_q['xs'], res_q['ys_corr'], res_q['y_fit']

ax1.plot(xs_q, ys_q, '-', color='#888888', lw=0.4, label='PDA(q) data')
ax1.plot(xs_q, yf_q, '-', color='#000000', lw=0.7, label='PDA(q) fit')

for i, (x0, g, a) in enumerate(res_q['params']):
    yp = lorentzian(xs_q, x0, g, a)
    pc = peak_colors[i % len(peak_colors)]
    ax1.plot(xs_q, yp, '-', color=pc, lw=0.8)
    ax1.fill_between(xs_q, 0, yp, color=pc, alpha=0.25)

ax1.set_ylim(0, 2.2)
ax1.set_ylabel('Intensity (counts)', fontsize=7, color='#000000')
ax1.tick_params(labelsize=7, left=False, labelleft=False)

# ── y2 (right): PDA(n) — normal — ylim -0.5 to 0.9 ──
res_n = deconv_results['PDA(n)']
xs_n, ys_n, yf_n = res_n['xs'], res_n['ys_corr'], res_n['y_fit']

ax2.plot(xs_n, ys_n, '-', color='#cccccc', lw=0.4, label='PDA(n) data')
ax2.plot(xs_n, yf_n, '-', color='#555555', lw=0.7, label='PDA(n) fit')

for i, (x0, g, a) in enumerate(res_n['params']):
    yp = lorentzian(xs_n, x0, g, a)
    pc = peak_colors[i % len(peak_colors)]
    ax2.plot(xs_n, yp, '-', color=pc, lw=0.8)
    ax2.fill_between(xs_n, 0, yp, color=pc, alpha=0.25)

ax2.set_ylim(-1, 1)

ax1.tick_params(labelsize=7, left=False)
ax2.tick_params(labelsize=7, right=False, labelright=False)



ax1.set_xlim(1200, 1700)
ax1.set_xlabel('Raman shift (cm\u207b\u00b9)', fontsize=8)

handles = [plt.Line2D([0],[0], linestyle='--', color=peak_colors[i], lw=1.2) for i in range(4)]
labels = peak_labels_short
ax1.legend(handles, labels, fontsize=6, frameon=False,
           loc='upper left', handlelength=1.5)

fig.tight_layout(pad=0.5, h_pad=1.0)
h = fig.get_size_inches()[1]
fig.subplots_adjust(top=max(1 - 0.5 / 2.54 / h, 0.92),
                    bottom=1.0 / 2.54 / h)
fig.savefig(os.path.join(OUT, 'raman_deconvolution_zoom.pdf'))
plt.close(fig)
print(f'\u2192 raman_deconvolution_zoom.pdf')
print('Done.')
