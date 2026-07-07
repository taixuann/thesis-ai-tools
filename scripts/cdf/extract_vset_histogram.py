#!/usr/bin/env python3
"""Extract V_set from cu-c-pda(q)-ito Keithley LVM files.
   v3: histogram (pooled) + per-device CDF scatter (D2D)

Usage:
    python3 extract_vset_histogram.py

Outputs to cdf/:
    - vset_all_q.csv             all extracted V_set values
    - vset_histogram_q.pdf/png   histogram (pooled D2D, no r1-c4)
    - vset_cdf_d2d_q.pdf/png     per-device CDF scatter (D2D variability)
"""

import os, csv, re
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

PROTOCOL = '/Users/tai/workspace/projects/active_projects/res_internship/protocol/2.2_cu-c_cu-ta_pda(n,q,c)/4_iv'
OUTPUT   = os.path.dirname(os.path.abspath(__file__))

plt.rcParams.update({
    'font.family': 'sans-serif',
    'font.sans-serif': ['Helvetica', 'Arial'],
    'axes.linewidth': 0.8,
    'xtick.direction': 'out',
    'ytick.direction': 'out',
    'xtick.major.size': 3,
    'ytick.major.size': 3,
})

DEVICE_COLORS = {
    'r1-c3': '#E69F00', 'r2-c3': '#56B4E9', 'r3-c3': '#009E73',
    'r4-c2': '#0072B2', 'r4-c4': '#D55E00', 'r5-c3': '#CC79A7',
    'r5-c4': '#000000', 'r6-c3': '#F0E442', 'r6-c4': '#332288',
    'r2-c4': '#AA3377', 'r3-c4': '#44BB99',
}
DEVICE_MARKERS = {
    'r1-c3': 'o', 'r2-c3': 's', 'r3-c3': '^',
    'r4-c2': 'D', 'r4-c4': 'v', 'r5-c3': '<',
    'r5-c4': '>', 'r6-c3': 'p', 'r6-c4': 'h',
    'r2-c4': 'X', 'r3-c4': '*',
}

def parse_lvm(filepath):
    v, i = [], []
    with open(filepath) as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith('***End_of_Header***') or \
               line.startswith('LabVIEW') or line.startswith('Writer_Version') or \
               line.startswith('Reader_Version') or line.startswith('Separator') or \
               line.startswith('Decimal_Separator') or line.startswith('Multi_Headings') or \
               line.startswith('X_Columns') or line.startswith('Time_Pref') or \
               line.startswith('Operator') or line.startswith('Date') or \
               line.startswith('Time') or line.startswith('Channels') or \
               line.startswith('Samples') or line.startswith('X_Dimension') or \
               line.startswith('X0') or line.startswith('Delta_X') or \
               line.startswith('X_Value') or line.startswith('Comment'):
                continue
            parts = line.split('\t')
            if len(parts) >= 2:
                try:
                    v.append(float(parts[0].strip()))
                    i.append(float(parts[1].strip()))
                except ValueError:
                    continue
    return np.array(v), np.array(i)

def detect_vset(v, i):
    if len(v) < 10:
        return None, 'too_short'
    imax = np.argmax(v)
    if imax < 5:
        return None, 'no_forward_sweep'
    v_fwd = v[:imax+1]
    i_fwd = i[:imax+1]
    if len(v_fwd) < 10:
        return None, 'too_short'
    mask = v_fwd > 0.05
    v_fwd = v_fwd[mask]
    i_fwd = i_fwd[mask]
    if len(v_fwd) < 5:
        return None, 'too_short_after_filter'
    abs_i = np.abs(i_fwd)
    log_i = np.log10(np.clip(abs_i, 1e-15, None))
    grad = np.gradient(log_i, v_fwd)
    grad_smooth = np.convolve(grad, np.ones(3)/3, mode='same')
    peak_idx = np.argmax(grad_smooth)
    max_grad = grad_smooth[peak_idx]
    if max_grad < 2:
        return None, f'gradient_too_low({max_grad:.1f})'
    v_set = float(v_fwd[peak_idx])
    if peak_idx >= len(v_fwd) - 1:
        return None, f'peak_at_last_point({v_set:.3f}V)'
    if v_set < 0.05:
        return None, f'vset_too_low({v_set:.3f}V)'
    i_start = np.median(abs_i[:3])
    i_set = abs_i[peak_idx]
    if i_set < i_start * 3:
        return None, f'jump_too_small({i_set/i_start:.1f}x)'
    return v_set, 'pass'

# ── Main ──
print('=' * 60)
print('V_set Extraction v3: cu-c-pda(q)-ito Keithley LVM')
print('=' * 60)

all_files = sorted(os.listdir(PROTOCOL))
files = [os.path.join(PROTOCOL, f) for f in all_files
         if 'cu-c-pda(q)-ito' in f and 'iv-bipolar-sweep' in f and f.endswith('.csv')]
non_r1c4 = [f for f in files if 'r1-c4' not in os.path.basename(f)]
print(f'\nFound {len(files)} total q-device files ({len(non_r1c4)} non-r1-c4)')

d2d_data = []
seen = set()
for fpath in non_r1c4:
    basename = os.path.basename(fpath)
    m = re.search(r'cu-c-pda\(q\)-ito_([\w-]+?)_iv-bipolar-sweep_(\d+)', basename)
    if not m:
        continue
    device = m.group(1)
    sweep_no = int(m.group(2))
    key = (device, sweep_no)
    if key in seen:
        continue
    seen.add(key)
    v_set, status = detect_vset(*parse_lvm(fpath))
    if status == 'pass':
        d2d_data.append({
            'device': device,
            'sweep': sweep_no,
            'v_set': v_set,
        })

print(f'  Extracted {len(d2d_data)} valid V_set values')

# Device breakdown
devices = {}
for d in d2d_data:
    devices.setdefault(d['device'], []).append(d['v_set'])
print(f'\nDevice breakdown (D2D):')
for dev, vals in sorted(devices.items()):
    print(f'  {dev}: {len(vals)} sweeps, V_set {np.median(vals):.3f}V [{np.min(vals):.3f}–{np.max(vals):.3f}]')

v_d2d = np.array([d['v_set'] for d in d2d_data])
print(f'\n{"=" * 60}')
print(f'D2D-only Summary: n={len(v_d2d)}, median={np.median(v_d2d):.4f}V')

# Save CSV
csv_path = os.path.join(OUTPUT, 'vset_all_q.csv')
with open(csv_path, 'w', newline='') as f:
    w = csv.writer(f)
    w.writerow(['device', 'sweep', 'v_set'])
    for d in d2d_data:
        w.writerow([d['device'], d['sweep'], f'{d["v_set"]:.6f}'])
print(f'  CSV → {csv_path}')

# ── PLOT 1: Histogram (pooled D2D) ──
print('\nPlotting histogram (pooled D2D)...')
fig, ax = plt.subplots(figsize=(6.5 * 0.394, 6 * 0.394))
n_bins = max(10, min(25, len(v_d2d) // 3))
bins = np.linspace(0, 1.0, n_bins + 1)
ax.hist(v_d2d, bins=bins, alpha=0.85, color='#0072B2', edgecolor='white', linewidth=0.5)
ax.set_xlabel('$V_\\mathrm{set}$ (V)', fontsize=8)
ax.set_ylabel('Count', fontsize=8)
ax.tick_params(labelsize=6)
ax.spines['top'].set_visible(False)
ax.spines['right'].set_visible(False)
plt.tight_layout(pad=0.3)
fig.savefig(os.path.join(OUTPUT, 'vset_histogram_q.pdf'), dpi=600, facecolor='white')
fig.savefig(os.path.join(OUTPUT, 'vset_histogram_q.png'), dpi=600, facecolor='white')
plt.close(fig)
print('  → vset_histogram_q.pdf/png')

# ── PLOT 2: Per-device CDF scatter (D2D) ──
print('Plotting per-device CDF scatter (D2D variability)...')
fig, ax = plt.subplots(figsize=(6.5 * 0.394, 6 * 0.394))

for dev, vals in sorted(devices.items()):
    svals = np.sort(vals)
    n = len(svals)
    y = np.arange(1, n + 1) / n
    color = DEVICE_COLORS.get(dev, '#333333')
    marker = DEVICE_MARKERS.get(dev, 'o')
    ax.plot(svals, y * 100, color=color, marker=marker, linestyle='none',
            markersize=5, label=f'{dev} (n={n})', markeredgecolor='black',
            markeredgewidth=0.3)

ax.set_xlabel('$V_\\mathrm{set}$ (V)', fontsize=8)
ax.set_ylabel('Cumulative Probability (%)', fontsize=8)
ax.tick_params(labelsize=6)
ax.spines['top'].set_visible(False)
ax.spines['right'].set_visible(False)
ax.legend(fontsize=5, frameon=False, ncol=2)
ax.set_xlim(0.3, 1.1)

plt.tight_layout(pad=0.3)
fig.savefig(os.path.join(OUTPUT, 'vset_cdf_d2d_q.pdf'), dpi=600, facecolor='white')
fig.savefig(os.path.join(OUTPUT, 'vset_cdf_d2d_q.png'), dpi=600, facecolor='white')
plt.close(fig)
print('  → vset_cdf_d2d_q.pdf/png')

print('\nDone.')
