#!/usr/bin/env python3
"""3-line CDF: D2D (r1-c4) + S2S (matrix) + B2B (q5 batch comparison)

Output:
  cdf/vset_d2d_s2s_b2b.pdf/png
  cdf/vset_all_b2b.csv
"""

import os, csv, re
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

PROTOCOL_Q   = '/Users/tai/workspace/projects/active_projects/res_internship/protocol/2.2_cu-c_cu-ta_pda(n,q,c)/4_iv'
PROTOCOL_Q5  = '/Users/tai/workspace/projects/active_projects/res_internship/protocol/2.5_cu-c-pda(n3,q4,q5)_ito(2)/3_iv-sweep'
REANALYZED   = '/Users/tai/workspace/projects/active_projects/res_internship/results/data/iv_iv-bipolar-sweep/iv_sweep_endurance_600cycles-iv/iv_sweep_per_cycle_reanalyzed.csv'
OUTPUT       = os.path.dirname(os.path.abspath(__file__))

plt.rcParams.update({
    'font.family': 'sans-serif',
    'font.sans-serif': ['Helvetica', 'Arial'],
    'axes.linewidth': 0.8,
    'xtick.direction': 'out',
    'ytick.direction': 'out',
    'xtick.major.size': 3,
    'ytick.major.size': 3,
})

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

def parse_keysight(filepath):
    v, i = [], []
    with open(filepath, encoding='utf-8-sig') as f:
        for line in f:
            line = line.strip()
            if line.startswith('DataValue'):
                parts = line.split(',')
                if len(parts) >= 3:
                    try:
                        v.append(float(parts[1]))
                        i.append(float(parts[2]))
                    except ValueError:
                        continue
    return np.array(v), np.array(i)

def detect_vset(v, i):
    if len(v) < 10:
        return None
    imax = np.argmax(v)
    if imax < 5:
        return None
    v_fwd = v[:imax+1]
    i_fwd = i[:imax+1]
    if len(v_fwd) < 10:
        return None
    mask = v_fwd > 0.05
    v_fwd = v_fwd[mask]
    i_fwd = i_fwd[mask]
    if len(v_fwd) < 5:
        return None
    abs_i = np.abs(i_fwd)
    log_i = np.log10(np.clip(abs_i, 1e-15, None))
    grad = np.gradient(log_i, v_fwd)
    grad_smooth = np.convolve(grad, np.ones(3)/3, mode='same')
    peak_idx = np.argmax(grad_smooth)
    max_grad = grad_smooth[peak_idx]
    if max_grad < 2:
        return None
    v_set = float(v_fwd[peak_idx])
    if peak_idx >= len(v_fwd) - 1:
        return None
    if v_set < 0.05:
        return None
    i_start = np.median(abs_i[:3])
    i_set = abs_i[peak_idx]
    if i_set < i_start * 3:
        return None
    return v_set

# Load data
print('=' * 60)
print('3-Line CDF: D2D (r1-c4) + S2S (matrix) + B2B (q5)')
print('=' * 60)

print('\nLoading r1-c4 (D2D)...')
v_d2d = []
with open(REANALYZED) as f:
    for row in csv.DictReader(f):
        vs = row.get('v_set', '').strip()
        if vs and float(vs) > 0.1:
            v_d2d.append(float(vs))
v_d2d = np.array(v_d2d)
print(f'  {len(v_d2d)} values, median={np.median(v_d2d):.4f}V')

print('\nLoading non-r1-c4 q (S2S)...')
all_files = sorted(os.listdir(PROTOCOL_Q))
files = [os.path.join(PROTOCOL_Q, f) for f in all_files
         if 'cu-c-pda(q)-ito' in f and 'iv-bipolar-sweep' in f and f.endswith('.csv')]
non_r1c4 = [f for f in files if 'r1-c4' not in os.path.basename(f)]
v_s2s = []
seen = set()
for fpath in non_r1c4:
    basename = os.path.basename(fpath)
    m = re.search(r'cu-c-pda\(q\)-ito_([\w-]+?)_iv-bipolar-sweep_(\d+)', basename)
    if not m:
        continue
    key = (m.group(1), int(m.group(2)))
    if key in seen:
        continue
    seen.add(key)
    v_set = detect_vset(*parse_lvm(fpath))
    if v_set is not None:
        v_s2s.append(v_set)
v_s2s = np.array(v_s2s)
print(f'  {len(v_s2s)} values, median={np.median(v_s2s):.4f}V')

print('\nLoading q5 (B2B)...')
all_q5 = sorted(os.listdir(PROTOCOL_Q5))
q5_files = [os.path.join(PROTOCOL_Q5, f) for f in all_q5
            if 'cu-c-pda(q5)' in f and 'iv-bipolar-sweep' in f and f.endswith('.csv')]
v_q5 = []
q5_detail = []
for fpath in q5_files:
    basename = os.path.basename(fpath)
    m = re.search(r'cu-c-pda\(q5\)-ito\(2\)_([\w-]+?)_iv-bipolar-sweep_(\d+)', basename)
    dev = m.group(1) if m else '?'
    swp = m.group(2) if m else '?'
    v_set = detect_vset(*parse_keysight(fpath))
    if v_set is not None:
        v_q5.append(v_set)
        q5_detail.append((dev, swp, v_set))
    else:
        q5_detail.append((dev, swp, None))
v_q5 = np.array(v_q5)
print(f'  {len(v_q5)} valid values, median={np.median(v_q5):.4f}V' if len(v_q5) > 0 else '  0 valid')
print(f'  (19/25 sweeps show no switching — q5 needs forming at higher voltage)')
print(f'  Valid sweeps:')
for dev, swp, v in q5_detail:
    if v is not None:
        print(f'    {dev} s{swp}: V_set={v:.3f}V')

# Save CSV
csv_path = os.path.join(OUTPUT, 'vset_all_b2b.csv')
with open(csv_path, 'w') as f:
    f.write('group,source,n,v_set\n')
    for v in v_d2d:
        f.write(f'D2D,r1-c4,{len(v_d2d)},{v:.6f}\n')
    for v in v_s2s:
        f.write(f'S2S,matrix,{len(v_s2s)},{v:.6f}\n')
    for v in v_q5:
        f.write(f'B2B,q5,{len(v_q5)},{v:.6f}\n')
print(f'\nCSV → {csv_path}')

# Plot
print('\nPlotting 3-line CDF...')
fig, ax = plt.subplots(figsize=(6.5 * 0.394, 6 * 0.394))

lines = [
    ('D2D (r1-c4)',     v_d2d,  '#0072B2', 'o', 2, 0.75, '(same cell, 600 cycles)'),
    ('S2S (matrix)',    v_s2s,  '#D55E00', 's', 3, 0.75, '(11 devices, 31 sweeps)'),
    ('B2B (q5 batch)',  v_q5,   '#000000', '^', 4, 0.75, '(2 devices, 6 sweeps)'),
]

for label, vals, color, marker, ms, lw, note in lines:
    s = np.sort(vals)
    n = len(s)
    y = np.arange(1, n + 1) / n
    ax.plot(s, y * 100, color=color, marker=marker, linestyle='-',
            markersize=ms, linewidth=lw, label=f'{label}  n={n}',
            markerfacecolor=color, markeredgecolor='black', markeredgewidth=0.3,
            alpha=0.9)

ax.set_xlabel('$V_\\mathrm{set}$ (V)', fontsize=8)
ax.set_ylabel('Cumulative Probability (%)', fontsize=8)
ax.tick_params(labelsize=6)
ax.spines['top'].set_visible(False)
ax.spines['right'].set_visible(False)
ax.legend(fontsize=6, frameon=False)

ax.set_xlim(0, 1.1)
ax.set_ylim(-5, 105)

plt.tight_layout(pad=0.3)

out_pdf = os.path.join(OUTPUT, 'vset_d2d_s2s_b2b.pdf')
out_png = os.path.join(OUTPUT, 'vset_d2d_s2s_b2b.png')
fig.savefig(out_pdf, dpi=600, facecolor='white')
fig.savefig(out_png, dpi=600, facecolor='white')
plt.close(fig)
print(f'  → {out_pdf}')
print(f'  → {out_png}')

print('\nDone.')
