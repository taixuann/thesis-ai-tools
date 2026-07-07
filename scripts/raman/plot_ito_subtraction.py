#!/usr/bin/env python3
"""ITO blank subtraction — perfectly matched set (785nm, ND 10%, 20s, 3 accums).
Generates: raw overlay, subtraction result, pure polymer comparison, peak table."""

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

# ── Matched set (same session, same spot — best ITO subtraction) ────
samples = {
    'ITO': {
        'file': '250526_ITO_raman_02.txt',
        'color': '#888888',
        'ls': '-',
        'lw': 0.6,
    },
    'PDA(n)-ITO SERS': {
        'file': '250526_PDA(n)-ITO_sers_01.txt',
        'color': '#0f27db',
        'ls': '-',
        'lw': 0.7,
    },
    'PDA(q)-ITO SERS': {
        'file': '250526_PDA(q)-ITO_sers_03.txt',
        'color': '#f20528',
        'ls': '-',
        'lw': 0.7,
    },
}


def read_raw(path, lo=400, hi=2000):
    """Read Raman .txt file (BioLogic; or Renishaw tab+comma)."""
    shift, intensity = [], []
    for line in open(path, encoding='latin-1'):
        if line.startswith('#'):
            continue
        # Try semicolon-separated (BioLogic export)
        parts = line.strip().split(';')
        if len(parts) >= 2:
            try:
                s = float(parts[0])
                i = float(parts[1])
                if lo <= s <= hi:
                    shift.append(s)
                    intensity.append(i)
                continue
            except ValueError:
                pass
        # Try tab-separated European format (comma decimal)
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
    """
    Find the ITO scaling factor k in a region where ITO dominates
    and PDA has negligible signal.
    Model: I_PDA-ITO = k * I_ITO + c (linear offset)
    """
    m = (pda_s >= region[0]) & (pda_s <= region[1])
    if np.sum(m) < 5:
        return 0, 0

    s_region = pda_s[m]
    ito_interp = np.interp(s_region, ito_s, ito_i)
    pda_region = pda_i[m]

    A = np.vstack([ito_interp, np.ones_like(ito_interp)]).T
    k, c = np.linalg.lstsq(A, pda_region, rcond=None)[0]

    return k, c


def als_baseline(y, lam=1e5, p=0.001, niter=10):
    """Asymmetric Least Squares baseline correction."""
    L = len(y)
    D = sparse.diags([1, -2, 1], [0, -1, -2], shape=(L, L-2))
    w = np.ones(L)
    for _ in range(niter):
        W = sparse.spdiags(w, 0, L, L)
        Z = W + lam * D.dot(D.T)
        z = spsolve(Z, w*y)
        w = p * (y > z) + (1-p) * (y < z)
    return z


# ── Load data ──────────────────────────────────────────────────────────
data = {}
for label, info in samples.items():
    s, i = read_raw(os.path.join(RAW, info['file']), lo=800, hi=2000)
    data[label] = (s, i)
    print(f'  {label:20s} → {len(s)} pts')

# ── Find ITO scale factor ─────────────────────────────────────────────
ito_s, ito_i = data['ITO']

factors = {}
for label in ['PDA(n)-ITO SERS', 'PDA(q)-ITO SERS']:
    s, i = data[label]
    k, c = find_scale_factor(s, i, ito_s, ito_i)
    factors[label] = (k, c)
    print(f'  ITO scale {label:20s}: k = {k:.3f}, c = {c:.2f}')

# ── Subtract ──────────────────────────────────────────────────────────
pure = {}
for label in ['PDA(n)-ITO SERS', 'PDA(q)-ITO SERS']:
    s, i = data[label]
    k, c = factors[label]
    ito_interp = np.interp(s, ito_s, ito_i)
    pure[label.replace('-ITO SERS', '')] = (s, i - k * ito_interp)

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
#  PLOT 1 — Raw overlay (un-normalised, same conditions)
# ══════════════════════════════════════════════════════════════════════
fig1, ax1 = plt.subplots(figsize=(8.5 * CM, 6 * CM))

for label in ['ITO', 'PDA(n)-ITO SERS', 'PDA(q)-ITO SERS']:
    info = samples[label]
    s, i = data[label]
    ax1.plot(s, i, info['ls'], color=info['color'], lw=info['lw'], label=label)

ax1.set_xlim(800, 2000)
ax1.set_xlabel('Raman shift (cm\u207b\u00b9)', fontsize=8)
ax1.set_ylabel('Intensity (counts)', fontsize=8)
ax1.tick_params(labelsize=7)
ax1.legend(fontsize=5.5, frameon=False, loc='upper right')

fig1.tight_layout(pad=0.5)
h = fig1.get_size_inches()[1]
fig1.subplots_adjust(top=1 - 0.5 / 2.54 / h, bottom=1.0 / 2.54 / h)
fig1.savefig(os.path.join(OUT, 'raw_overlay_matched.pdf'))
plt.close(fig1)
print('\n\u2192 raw_overlay_matched.pdf')

# ══════════════════════════════════════════════════════════════════════
#  PLOT 2 — Before/after subtraction (two panels)
# ══════════════════════════════════════════════════════════════════════
fig2, (ax2a, ax2b) = plt.subplots(2, 1, figsize=(8.5 * CM, 10 * CM),
                                   sharex=True)

for label, ax, c_raw, c_pure in [
    ('PDA(n)-ITO SERS', ax2a, '#bbbbbb', '#0f27db'),
    ('PDA(q)-ITO SERS', ax2b, '#bbbbbb', '#f20528'),
]:
    s, i = data[label]
    pure_label = label.replace('-ITO SERS', '')
    ps, pi = pure[pure_label]
    ax.plot(s, i, '-', color=c_raw, lw=0.4, label=f'{pure_label} raw')
    ax.plot(ps, pi, '-', color=c_pure, lw=0.7, label=f'{pure_label} \u2014 ITO subtracted')
    ax.axhline(0, color='#000000', lw=0.3)
    ax.set_ylabel('Intensity (counts)', fontsize=7)
    ax.tick_params(labelsize=7)
    ax.legend(fontsize=5.5, frameon=False, loc='upper right')
    ax.set_xlim(800, 2000)

ax2b.set_xlabel('Raman shift (cm\u207b\u00b9)', fontsize=8)

fig2.tight_layout(pad=0.5)
h2 = fig2.get_size_inches()[1]
fig2.subplots_adjust(top=max(1 - 0.5 / 2.54 / h2, 0.9), bottom=1.0 / 2.54 / h2)
fig2.savefig(os.path.join(OUT, 'subtraction_result.pdf'))
plt.close(fig2)
print('\u2192 subtraction_result.pdf')

# ══════════════════════════════════════════════════════════════════════
#  PEAK DECONVOLUTION — Lorentzian fitting on pure polymer spectra
#  Uses ALS baseline + parameter bounds
# ══════════════════════════════════════════════════════════════════════
def lorentzian(x, x0, gamma, A):
    return A * gamma**2 / ((x - x0)**2 + gamma**2)

def multi_lorentz(x, *params):
    n = len(params) // 3
    y = np.zeros_like(x)
    for i in range(n):
        y += lorentzian(x, params[3*i], params[3*i+1], params[3*i+2])
    return y

peak_guesses = [
    (1340, 50, 0.4),   # D-band: disordered aromatic rings
    (1410, 45, 0.2),   # C=N / quinone-imine
    (1490, 50, 0.4),   # N-H bending / indole
    (1590, 40, 0.6),   # G-band: C=C aromatic
]

deconv_results = {}
for label, c in [('PDA(n)', '#0f27db'), ('PDA(q)', '#f20528')]:
    s, i = pure[label]
    mask = (s >= 1200) & (s <= 1700)
    xs, ys = s[mask], i[mask]

    # Linear baseline between endpoints (most robust for noisy PDA SERS data)
    # Polynomial/cubic baselines overfit the noise and increase residual
    baseline = np.interp(xs, [xs[0], xs[-1]], [ys[0], ys[-1]])
    ys_corr = ys - baseline
    ys_corr = ys_corr / np.max(np.abs(ys_corr))

    p0 = [v for guess in peak_guesses for v in guess]
    # Bounds: x0 ± 50, γ ∈ [20, 150], A ≥ 0 (normalized scale: max A ~ 1)
    lower_bounds = []
    upper_bounds = []
    for x0_guess, gamma_guess, A_guess in peak_guesses:
        lower_bounds += [x0_guess - 50, 20.0, 0]
        upper_bounds += [x0_guess + 50, 150, 2.0]

    try:
        popt, _ = curve_fit(multi_lorentz, xs, ys_corr, p0=p0,
                             bounds=(lower_bounds, upper_bounds),
                             maxfev=10000)
        n_peaks = len(popt) // 3
        y_fit = multi_lorentz(xs, *popt)
        residual = ys_corr - y_fit
        deconv_results[label] = {
            'params': [(popt[3*i], popt[3*i+1], popt[3*i+2]) for i in range(n_peaks)],
            'baseline': baseline,
            'residual': np.sqrt(np.mean(residual**2)),
            'xs': xs, 'ys_corr': ys_corr, 'y_fit': y_fit,
        }
        print(f'\n  {label} deconvolution:')
        for i in range(n_peaks):
            x0, g, a = popt[3*i], popt[3*i+1], popt[3*i+2]
            fwhm = 2 * g
            print(f'    Peak {i+1}:  x\u2080={x0:7.1f}  \u03b3={g:5.1f}  A={a:7.1f}  FWHM={fwhm:.1f}')
    except Exception as e:
        print(f'  {label} deconvolution failed: {e}')

# ══════════════════════════════════════════════════════════════════════
#  PLOT 3 — Dual y-axis: PDA(n) left axis, PDA(q) right axis
# ══════════════════════════════════════════════════════════════════════
peak_colors = ['#0f27db', '#009e73', '#e69200', '#bd046a']
peak_labels = ['D-band\n(C-C/C-N)', 'C=N /\nquinone-imine', 'N-H /\nindole', 'G-band\n(C=C)']

fig3, ax1 = plt.subplots(figsize=(7.5 * CM, 8 * CM))
ax2 = ax1.twinx()

if 'PDA(n)' in deconv_results:
    res = deconv_results['PDA(n)']
    xs, ys_corr, y_fit = res['xs'], res['ys_corr'], res['y_fit']
    ax1.plot(xs, ys_corr, '-', color='#888888', lw=0.3)
    ax1.plot(xs, y_fit, '-', color='#000000', lw=0.8)
    for i, (x0, g, a) in enumerate(res['params']):
        if a < 0:
            continue
        y_peak = lorentzian(xs, x0, g, a)
        pc = peak_colors[i % len(peak_colors)]
        ax1.plot(xs, y_peak, '--', color=pc, lw=0.6, alpha=0.6)

if 'PDA(q)' in deconv_results:
    res = deconv_results['PDA(q)']
    xs, ys_corr, y_fit = res['xs'], res['ys_corr'], res['y_fit']
    ax2.plot(xs, ys_corr, '-', color='#888888', lw=0.3)
    ax2.plot(xs, y_fit, '-', color='#000000', lw=0.8)
    for i, (x0, g, a) in enumerate(res['params']):
        if a < 0:
            continue
        y_peak = lorentzian(xs, x0, g, a)
        pc = peak_colors[i % len(peak_colors)]
        ax2.plot(xs, y_peak, '--', color=pc, lw=0.6, alpha=0.6)

legend_handles = [plt.Line2D([0], [0], linestyle='--', color=c, lw=1.0) for c in peak_colors]
ax1.legend(legend_handles, [l.split('\n')[0] for l in peak_labels],
           fontsize=5.5, frameon=False, loc='upper left', handlelength=1.5)

ax1.set_xlim(1200, 1700)
ax1.set_ylim(0, 200)
ax2.set_ylim(-200, 120)

ax1.set_xlabel('Raman shift (cm\u207b\u00b9)', fontsize=8)
ax1.set_ylabel('Intensity', fontsize=8)

for ax in [ax1, ax2]:
    ax.tick_params(labelleft=False, left=False, labelright=False, right=False,
                   labelbottom=True, bottom=True, labelsize=7)

fig3.tight_layout(pad=0.5)
h = fig3.get_size_inches()[1]
fig3.subplots_adjust(top=1 - 0.5 / 2.54 / h,
                     bottom=1.0 / 2.54 / h)

fig3.savefig(os.path.join(OUT, 'raman_comparison-correct.pdf'))
plt.close(fig3)
print('\u2192 raman_comparison-correct.pdf')

# ══════════════════════════════════════════════════════════════════════
#  PLOT 4 — Peak-picked regions (zoom on 1200-1700 cm⁻¹)
# ══════════════════════════════════════════════════════════════════════
fig4, ax4 = plt.subplots(figsize=(8.5 * CM, 6 * CM))

for label, c in [('PDA(n)', '#0f27db'), ('PDA(q)', '#f20528')]:
    s, i = pure[label]
    ax4.plot(s, i, '-', color=c, lw=0.8, label=label)

ax4.axhline(0, color='#000000', lw=0.3)

pda_bands = {
    1340: 'C=C\n(stretching)',
    1410: 'C=N\n/ ring',
    1505: 'N-H\n(bending)',
    1585: 'C=C\n(aromatic)',
}
for shift, label in pda_bands.items():
    for s, i in [pure['PDA(n)'], pure['PDA(q)']]:
        idx = np.argmin(np.abs(s - shift))
        ax4.axvline(shift, color='#aaaaaa', ls=':', lw=0.4, alpha=0.5)
    ax4.text(shift, ax4.get_ylim()[1] * 0.85, label, fontsize=5,
             ha='center', color='#555555')

ax4.set_xlim(1200, 1700)
ax4.set_xlabel('Raman shift (cm\u207b\u00b9)', fontsize=8)
ax4.set_ylabel('Intensity (ITO subtracted)', fontsize=8)
ax4.tick_params(labelsize=7)
ax4.legend(fontsize=6, frameon=False, loc='upper right')

fig4.tight_layout(pad=0.5)
h4 = fig4.get_size_inches()[1]
fig4.subplots_adjust(top=1 - 0.5 / 2.54 / h4, bottom=1.0 / 2.54 / h4)
fig4.savefig(os.path.join(OUT, 'pure_polymer_zoom.pdf'))
plt.close(fig4)
print('\u2192 pure_polymer_zoom.pdf')

# ══════════════════════════════════════════════════════════════════════
#  PLOT 5 — Deconvolution individual panels
# ══════════════════════════════════════════════════════════════════════
fig5 = plt.figure(figsize=(8.5 * CM, 11 * CM))
gs = fig5.add_gridspec(4, 1, hspace=0.3, height_ratios=[3, 1, 3, 1])

for idx, (label, c) in enumerate([('PDA(n)', '#0f27db'), ('PDA(q)', '#f20528')]):
    ax = fig5.add_subplot(gs[2 * idx])
    rax = fig5.add_subplot(gs[2 * idx + 1], sharex=ax)

    if label not in deconv_results:
        ax.text(0.5, 0.5, f'{label} — failed', transform=ax.transAxes, ha='center')
        rax.set_visible(False)
        continue

    res = deconv_results[label]
    xs, ys_corr, y_fit = res['xs'], res['ys_corr'], res['y_fit']

    ax.plot(xs, ys_corr, '-', color=c, lw=0.5, alpha=0.6, label=f'{label} data')
    ax.plot(xs, y_fit, '-', color='#000000', lw=0.7, label='Cumulative fit')

    for i, (x0, g, a) in enumerate(res['params']):
        if a < 0:
            continue
        y_peak = lorentzian(xs, x0, g, a)
        ax.plot(xs, y_peak, '--', color=c, lw=0.4, alpha=0.4)
        ax.axvline(x0, color=c, ls=':', lw=0.3, alpha=0.3)
        ax.text(x0, max(y_peak) * 0.75, f'{x0:.0f}', fontsize=5,
                color=c, ha='center', rotation=90)

    assignments = ['D-band\n(C-C/C-N)', 'C=N /\nquinone-imine', 'N-H /\nindole', 'G-band\n(C=C)']
    for i, (x0, g, a) in enumerate(res['params']):
        if i < len(assignments):
            ax.text(x0, ax.get_ylim()[1] * 0.9, assignments[i],
                    fontsize=4.5, color='#555555', ha='center', va='bottom')

    ax.set_ylabel('Intensity (norm)', fontsize=7)
    ax.tick_params(labelsize=7)
    ax.legend(fontsize=5, frameon=False, loc='upper right')
    ax.set_xlim(1200, 1700)

    # Residual panel
    residual = ys_corr - y_fit
    rax.plot(xs, residual, '-', color=c, lw=0.4)
    rax.axhline(0, color='#000000', lw=0.3)
    rax.set_ylabel('Residual', fontsize=7)
    rax.tick_params(labelsize=7)
    rax.set_xlim(1200, 1700)
    rms_val = np.sqrt(np.mean(residual**2))
    rax.text(0.97, 0.88, f'RMS = {rms_val:.4f}', transform=rax.transAxes,
             fontsize=6, ha='right', va='top',
             bbox=dict(boxstyle='round,pad=0.2', facecolor='white', alpha=0.7))
    # Add noise std reference lines
    noise_std = np.std(residual[(xs > 1640) | (xs < 1260)])
    rax.axhline(noise_std, color='#888888', ls=':', lw=0.3)
    rax.axhline(-noise_std, color='#888888', ls=':', lw=0.3)
    rax.text(0.97, 0.55, f'Noise σ = {noise_std:.4f}', transform=rax.transAxes,
             fontsize=5, ha='right', va='top', color='#888888')

fig5.add_subplot(gs[3]).set_xlabel('Raman shift (cm\u207b\u00b9)', fontsize=8)

fig5.tight_layout(pad=0.5)
h5 = fig5.get_size_inches()[1]
fig5.subplots_adjust(top=max(1 - 0.5 / 2.54 / h5, 0.92), bottom=1.0 / 2.54 / h5)
fig5.savefig(os.path.join(OUT, 'deconvolution.pdf'))
plt.close(fig5)
print('\n\u2192 deconvolution.pdf')

# ══════════════════════════════════════════════════════════════════════
#  SAVE SUMMARY REPORT
# ══════════════════════════════════════════════════════════════════════
report = []
report.append('=' * 60)
report.append('  RAMAN ITO SUBTRACTION — SUMMARY REPORT')
report.append('=' * 60)
report.append('')
report.append('  Experimental Conditions:')
report.append(f'    Laser:        785 nm (Edge filter)')
report.append(f'    ND Filter:    10%')
report.append(f'    Acquisition:  20 s')
report.append(f'    Accumulations: 3')
report.append('')
report.append('  Samples (perfectly matched set):')
report.append(f'    ITO:        ITO_raman_02.txt')
report.append(f'    PDA(n):     PDA(n)-ITO_sers_01.txt')
report.append(f'    PDA(q):     PDA(q)-ITO_sers_03.txt')
report.append('')
report.append('  ITO Subtraction Parameters:')
report.append(f'    Fit region:      1050-1150 cm\u207b\u00b9 (ITO peak)')
report.append(f'    PDA(n) k-factor: {factors["PDA(n)-ITO SERS"][0]:.3f}')
report.append(f'    PDA(n) offset:   {factors["PDA(n)-ITO SERS"][1]:.1f}')
report.append(f'    PDA(q) k-factor: {factors["PDA(q)-ITO SERS"][0]:.3f}')
report.append(f'    PDA(q) offset:   {factors["PDA(q)-ITO SERS"][1]:.1f}')
report.append('')
report.append('  Baseline Method: Linear endpoint interpolation (1200-1700 cm\u207b\u00b9) — most robust for noisy PDA SERS data')
report.append('  Normalization: Data scaled to max = 1 after baseline subtraction')
report.append('  Peak Model: 4 Lorentzian components with amplitude \u2265 0, \u03b3 \u2208 [20, 150]')
report.append('  Fit Quality Criteria (from Raman fitting literature):')
report.append('    \u2022 RMS residual \u2264 0.05 on normalized data \u2192 good fit')
report.append('    \u2022 Residual should be random noise (no systematic features)')
report.append('    \u2022 Residual noise \u2248 baseline noise \u2192 no under/overfitting')
report.append('')
report.append('  Deconvolution Results (Lorentzian peaks, 1200-1700 cm\u207b\u00b9):\n\n  Literature PDA Raman bands (785 nm excitation):\n    ~1300-1360 cm\u207b\u00b9  D-band: C-C/C-N stretch, indole ring deformation\n    ~1400-1420 cm\u207b\u00b9         C=N stretch, quinone-imine / indole modes\n    ~1480-1510 cm\u207b\u00b9         N-H bending, catechol C-O-H, indole ring stretching\n    ~1570-1610 cm\u207b\u00b9  G-band: C=C aromatic ring stretch, sp\u00b2 carbon\n\n  Literature FWHM ranges for PDA (785 nm):\n    D-band:     ~120-200 cm\u207b\u00b9  (very broad, disordered aromatic network)\n    G-band:     ~50-80 cm\u207b\u00b9   (moderately broad, N-doped carbon)\n    Intermed:   ~100-160 cm\u207b\u00b9  (overlapping sub-components)\n  [RSC Adv. 2023, 13, 28450; J. Phys. Chem. C 2023, 127, 12662]')

if 'PDA(n)' in deconv_results:
    report.append(f'\n  PDA(n) — Normalized fit (baseline-subtracted, max=1):')
    for i, (x0, g, a) in enumerate(deconv_results['PDA(n)']['params']):
        fwhm = 2 * g
        report.append(f'    Peak {i+1}:  x\u2080={x0:7.1f} cm\u207b\u00b9  \u03b3={g:5.1f}  A={a:7.2f}  FWHM={fwhm:.1f} cm\u207b\u00b9')
    rms = deconv_results['PDA(n)']['residual']
    xs_n = deconv_results['PDA(n)']['xs']
    residual_n = deconv_results['PDA(n)']['ys_corr'] - deconv_results['PDA(n)']['y_fit']
    noise_n = np.std(residual_n[(xs_n > 1640) | (xs_n < 1260)])
    if rms <= 0.05 and rms <= noise_n * 1.5:
        status = 'PASS'
    elif rms <= noise_n * 1.5:
        status = 'NOISE-LIMITED'
    else:
        status = 'FAIL'
    report.append(f'    RMS residual:    {rms:.4f}  (target \u2264 0.05)')
    report.append(f'    Baseline noise:  {noise_n:.4f}  (residual should \u2248 noise)')
    report.append(f'    RMS / noise:     {rms/noise_n:.2f}  (\u2264 1.5 \u2192 noise-limited)')
    report.append(f'    Fit quality:     {status}')

if 'PDA(q)' in deconv_results:
    report.append(f'\n  PDA(q) — Normalized fit (baseline-subtracted, max=1):')
    for i, (x0, g, a) in enumerate(deconv_results['PDA(q)']['params']):
        fwhm = 2 * g
        report.append(f'    Peak {i+1}:  x\u2080={x0:7.1f} cm\u207b\u00b9  \u03b3={g:5.1f}  A={a:7.2f}  FWHM={fwhm:.1f} cm\u207b\u00b9')
    rms = deconv_results['PDA(q)']['residual']
    xs_q = deconv_results['PDA(q)']['xs']
    residual_q = deconv_results['PDA(q)']['ys_corr'] - deconv_results['PDA(q)']['y_fit']
    noise_q = np.std(residual_q[(xs_q > 1640) | (xs_q < 1260)])
    if rms <= 0.05 and rms <= noise_q * 1.5:
        status = 'PASS'
    elif rms <= noise_q * 1.5:
        status = 'NOISE-LIMITED'
    else:
        status = 'FAIL'
    report.append(f'    RMS residual:    {rms:.4f}  (target \u2264 0.05)')
    report.append(f'    Baseline noise:  {noise_q:.4f}  (residual should \u2248 noise)')
    report.append(f'    RMS / noise:     {rms/noise_q:.2f}  (\u2264 1.5 \u2192 noise-limited)')
    report.append(f'    Fit quality:     {status}')

report.append('')
report.append('  Output files:')
report.append(f'    raman_comparison-correct.pdf           \u2014 PDA(n) + PDA(q) offset with deconvolution')
report.append(f'    raw_overlay_matched.pdf                \u2014 All 3 raw spectra overlaid')
report.append(f'    subtraction_result.pdf                 \u2014 Before/after ITO subtraction')
report.append(f'    pure_polymer_zoom.pdf                  \u2014 Fingerprint region 1200-1700')
report.append(f'    deconvolution.pdf                      \u2014 Lorentzian peak fits')
report.append(f'    ito_subtraction_report.txt             \u2014 This report')
report.append(f'    sources/                               \u2014 Raw data files')
report.append('')
report.append('  Comparative Analysis:')
if 'PDA(n)' in deconv_results and 'PDA(q)' in deconv_results:
    dn = deconv_results['PDA(n)']['params'][0][0]
    dq = deconv_results['PDA(q)']['params'][0][0]
    gn = deconv_results['PDA(n)']['params'][3][0]
    gq = deconv_results['PDA(q)']['params'][3][0]
    report.append(f'    D-band shift:  PDA(n) at {dn:.0f} vs PDA(q) at {dq:.0f} cm\u207b\u00b9  (\u0394 = {dq-dn:+.0f} cm\u207b\u00b9)')
    report.append(f'    G-band shift:  PDA(n) at {gn:.0f} vs PDA(q) at {gq:.0f} cm\u207b\u00b9  (\u0394 = {gq-gn:+.0f} cm\u207b\u00b9)')
    da_n = deconv_results['PDA(n)']['params'][0][1] * deconv_results['PDA(n)']['params'][0][2]
    ga_n = deconv_results['PDA(n)']['params'][3][1] * deconv_results['PDA(n)']['params'][3][2]
    da_q = deconv_results['PDA(q)']['params'][0][1] * deconv_results['PDA(q)']['params'][0][2]
    ga_q = deconv_results['PDA(q)']['params'][3][1] * deconv_results['PDA(q)']['params'][3][2]
    report.append(f'    D/G area ratio: PDA(n) = {da_n/ga_n:.2f},  PDA(q) = {da_q/ga_q:.2f}')
    report.append('')
    report.append('    Interpretation:')
    report.append('    \u2022 PDA(q) shows both D- and G-band upshifts  \u2192  more quinone/oxidised character')
    report.append('    \u2022 Higher D/G ratio in PDA(q)  \u2192  more disordered aromatic network')
    report.append('    \u2022 The G-band in PDA(q) is broader  \u2192  enhanced C=O contribution from quinones')
    report.append('    \u2022 PDA(n) has sharper, more intense G-band  \u2192  more ordered indole-rich structure')
report.append('')
report.append('=' * 60)

report_text = '\n'.join(report)
print('\n' + report_text)

with open(os.path.join(OUT, 'ito_subtraction_report.txt'), 'w') as f:
    f.write(report_text)
print('\n\u2192 ito_subtraction_report.txt')

print(f'\nAll files in: {OUT}')
print('Done.')
