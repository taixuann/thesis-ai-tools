#!/usr/bin/env python3
"""Final CDF: D2D + S2S + B2B
   Scatter circles only + Weibull fit lines on top.
   Colors: red/blue/black with darker edges.
   B2B filters V_set < 0.2V (suspected shorts/noise).
"""

import os, re
import numpy as np
from scipy import stats
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

OUTPUT = os.path.dirname(os.path.abspath(__file__))

SEARCH_DIRS = [
    '/Users/tai/workspace/projects/active_projects/res_internship/protocol/2.2_cu-c_cu-ta_pda(n,q,c)/4_iv',
    '/Users/tai/workspace/projects/active_projects/res_internship/protocol/2.5_cu-c-pda(n3,q4,q5)_ito(2)/3_iv-sweep',
    '/Users/tai/workspace/projects/active_projects/res_internship/data/raw',
    '/Users/tai/workspace/projects/active_projects/res_internship/data/240626',
]
gtiit_root = '/Users/tai/workspace/projects/active_projects/res_internship/data/gtiit'
for d in sorted(os.listdir(gtiit_root)):
    dd = os.path.join(gtiit_root, d)
    if os.path.isdir(dd):
        SEARCH_DIRS.append(dd)

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
    with open(filepath, encoding='utf-8-sig', errors='replace') as f:
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

def check_bipolar_ratio(v, i, min_ratio=3):
    """Require positive-range peak current >> negative-range peak current."""
    pos = v > 0.1; neg = v < -0.1
    if not np.any(pos) or not np.any(neg): return True
    p_pos = float(np.max(np.abs(i[pos])))
    p_neg = float(np.max(np.abs(i[neg])))
    if p_neg <= 0: return True
    return (p_pos / p_neg) >= min_ratio

def detect_vset(v, i):
    """Try log-gradient first, fall back to linear dI/dV for gradual switching."""
    vs = detect_vset_log(v, i)
    if vs is not None:
        return vs if check_bipolar_ratio(v, i) else None
    vs = detect_vset_linear(v, i)
    if vs is not None:
        return vs if check_bipolar_ratio(v, i) else None
    return None

def detect_vset_log(v, i):
    if len(v) < 10: return None
    imax = np.argmax(v)
    if imax < 5: return None
    v_fwd = v[:imax+1]; i_fwd = i[:imax+1]
    if len(v_fwd) < 10: return None
    mask = v_fwd > 0.05
    v_fwd = v_fwd[mask]; i_fwd = i_fwd[mask]
    if len(v_fwd) < 5: return None
    abs_i = np.abs(i_fwd)
    log_i = np.log10(np.clip(abs_i, 1e-15, None))
    grad = np.gradient(log_i, v_fwd)
    grad_smooth = np.convolve(grad, np.ones(3)/3, mode='same')
    peak_idx = np.argmax(grad_smooth)
    if grad_smooth[peak_idx] < 2: return None
    if peak_idx >= len(v_fwd) - 1: return None
    v_set = float(v_fwd[peak_idx])
    if v_set < 0.05: return None
    i_start = np.median(abs_i[:3])
    if abs_i[peak_idx] < i_start * 2.5: return None
    return v_set

def detect_vset_linear(v, i):
    """Detect gradual SET onset using linear dI/dV."""
    if len(v) < 10: return None
    imax = np.argmax(v)
    if imax < 5: return None
    v_fwd = v[:imax+1]; i_fwd = i[:imax+1]
    if len(v_fwd) < 10: return None
    mask = v_fwd > 0.05
    v_fwd = v_fwd[mask]; i_fwd = i_fwd[mask]
    if len(v_fwd) < 5: return None
    abs_i = np.abs(i_fwd)
    i_start = float(np.median(abs_i[:3]))
    if i_start > 1e-7: return None

    g_lin = np.gradient(abs_i, v_fwd)
    g_lin_s = np.convolve(g_lin, np.ones(3)/3, mode='same')
    peak_idx = np.argmax(g_lin_s)
    if peak_idx >= len(v_fwd) - 1: return None

    # Onset: walk back from peak to where gradient drops to 20%
    onset_idx = peak_idx
    peak_grad = g_lin_s[peak_idx]
    for j in range(peak_idx, 0, -1):
        if g_lin_s[j] < peak_grad * 0.2:
            onset_idx = j
            break
    v_set = float(v_fwd[onset_idx])
    if v_set < 0.1: return None

    i_ratio = float(abs_i[peak_idx] / i_start if i_start > 0 else 0)
    if i_ratio < 5: return None
    if abs_i[peak_idx] < 1e-6: return None

    noise = np.std(g_lin_s[:5])
    if noise < 1e-15: return None
    snr = (g_lin_s[peak_idx] - np.median(g_lin_s[:5])) / noise
    if snr < 10: return None

    return v_set

def is_q_file(fname):
    f = fname.lower()
    return ('cu-c-pda(q)' in f or 'cu-c-pda(q4)' in f) and 'q5' not in f

def is_q5_file(fname):
    return 'cu-c-pda(q5)' in fname.lower()

def is_iv_file(fname):
    f = fname.lower()
    iv_kw = ['iv-bipolar-sweep', 'iv-sweep', 'iv list sweep', 'i_v list sweep',
             'dual vsweep', '2-terminal']
    non_iv_kw = ['pulse', 'endurance', 'stp', 'ppf', 'relax', 'pattern',
                 'discard', 'plsdiv', 'test-full']
    if any(k in f for k in non_iv_kw): return False
    return any(k in f for k in iv_kw)

def skip_file(fname):
    return any(k in fname.lower() for k in ['discard']) or not fname.endswith('.csv')

def downsample(vals, max_n=16):
    if len(vals) <= max_n: return vals
    idx = np.round(np.linspace(0, len(vals) - 1, max_n)).astype(int)
    return np.sort(vals)[idx]

def weibull_params(vals):
    if len(vals) < 3: return None, None, None
    s = np.sort(vals); n = len(s)
    y = np.arange(1, n + 1) / (n + 1)
    slope, intercept, r_val, _, _ = stats.linregress(np.log(s), np.log(-np.log(1 - y)))
    beta = slope
    return np.exp(-intercept / beta), beta, r_val ** 2

def extract_batch(files, label, vset_min=0.0):
    vals = []; dev_map = {}
    for fpath in files:
        basename = os.path.basename(fpath)
        m = re.search(r'(r[\d]+-c[\d]+)', basename)
        dev = m.group(1) if m else 'unknown'
        with open(fpath, encoding='utf-8-sig', errors='replace') as fh:
            sample = fh.read(50000)
        if 'DataValue' in sample or 'SetupTitle,' in sample:
            v, i = parse_keysight(fpath)
        elif '\t' in sample:
            v, i = parse_lvm(fpath)
        else:
            v, i = parse_keysight(fpath)
        vs = detect_vset(v, i)
        if vs is not None and vs >= vset_min:
            vals.append(vs)
            dev_map.setdefault(dev, []).append(vs)
    n_total, n_pass = len(files), len(vals)
    print(f'  {label}: {n_pass}/{n_total} valid V_set (≥{vset_min}V)')
    for dev, vlist in sorted(dev_map.items()):
        if vlist: print(f'    {dev}: {len(vlist)} sweeps, median={np.median(vlist):.3f}V')
    return np.array(vals), dev_map

# ── Collect ──
print('=' * 60)
print('Final CDF: D2D + S2S + B2B (Weibull fit)')
print('=' * 60)

q_files, q5_files = [], []
seen = set()
for srcdir in SEARCH_DIRS:
    if not os.path.isdir(srcdir): continue
    for fname in sorted(os.listdir(srcdir)):
        if skip_file(fname): continue
        fpath = os.path.join(srcdir, fname)
        try:
            s = os.stat(fpath); ino = (s.st_dev, s.st_ino)
            if ino in seen: continue
            seen.add(ino)
        except: pass
        if is_q_file(fname) and is_iv_file(fname): q_files.append(fpath)
        elif is_q5_file(fname) and is_iv_file(fname): q5_files.append(fpath)
print(f'\nFound {len(q_files)} q-batch IV files, {len(q5_files)} q5-batch IV files')

print('\n--- D2D: r1-c4 all valid ---')
q_r1c4 = [f for f in q_files if 'r1-c4' in os.path.basename(f)]
v_d2d, d2d_devs = extract_batch(q_r1c4, 'D2D (r1-c4)', vset_min=0.4)

print('\n--- S2S: non-r1-c4 all + r1-c4 sampled to match ---')
q_matrix = [f for f in q_files if 'r1-c4' not in os.path.basename(f)]
_, s2s_devs = extract_batch(q_matrix, 'S2S (non-r1-c4)', vset_min=0.4)
# Build S2S: non-r1-c4 raw + r1-c4 sampled to ~30 (a bit above largest non-r1-c4)
s2s_list = []
for dev, vlist in s2s_devs.items():
    s2s_list.extend(vlist)  # keep all non-r1-c4 as-is
# Add r1-c4 sampled to 80
r1c4_sampled = downsample(v_d2d.copy(), 80)
s2s_list.extend(r1c4_sampled)
v_s2s = np.array(s2s_list)
print(f'  S2S: {len(v_s2s)} values (non-r1-c4: {sum(len(v) for v in s2s_devs.values())} + r1-c4: {len(r1c4_sampled)}), median={np.median(v_s2s):.4f}V')

print('\n--- B2B: q5 batch ---')
v_b2b, b2b_devs = extract_batch(q5_files, 'B2B (q5)', vset_min=0.4)

print(f'\n{"=" * 60}')
print('Weibull Fit Parameters')
print(f'{"=" * 60}')

# B2B = q + q5 combined (downsampled per-device)
MAX_PER_DEV = 16
b2b_v2_list = []
for dev, vlist in d2d_devs.items():
    b2b_v2_list.extend(downsample(np.array(vlist), MAX_PER_DEV))
for dev, vlist in s2s_devs.items():
    b2b_v2_list.extend(downsample(np.array(vlist), MAX_PER_DEV))
for dev, vlist in b2b_devs.items():
    b2b_v2_list.extend(downsample(np.array(vlist), MAX_PER_DEV))
v_b2b_v2 = np.array(b2b_v2_list)
# Remove B2B points above 1.5V (negligible tail)
v_b2b_v2 = v_b2b_v2[v_b2b_v2 <= 1.5]
print(f'  B2B (q+q5, ds={MAX_PER_DEV}/dev, ≤1.5V): {len(v_b2b_v2)} values, median={np.median(v_b2b_v2):.4f}V')
eta_b2b_v2, beta_b2b_v2, rsq_b2b_v2 = weibull_params(v_b2b_v2)
if eta_b2b_v2: print(f'  Weibull: η={eta_b2b_v2:.4f}V  β={beta_b2b_v2:.4f}  R²={rsq_b2b_v2:.4f}')

groups = [
    ('Device-to-device',  v_s2s, '#0072B2', '#003366'),
    ('Sample-to-sample',  v_d2d, '#CC0000', '#990000'),
    ('Batch-to-batch',    v_b2b_v2, '#333333', '#000000'),
]
for label, vals, _, _ in groups:
    eta, beta, rsq = weibull_params(vals)
    if eta:
        print(f'  {label:<20} n={len(vals):4d}  η={eta:.4f}V  β={beta:.4f}  R²={rsq:.4f}')
    else:
        print(f'  {label:<20} n={len(vals):4d}  [too few points]')

csv_path = os.path.join(OUTPUT, 'vset_final.csv')
with open(csv_path, 'w') as f:
    f.write('group,source,n,v_set\n')
    for v in v_d2d: f.write(f'D2D,r1-c4,{len(v_d2d)},{v:.6f}\n')
    for v in v_s2s: f.write(f'S2S,q_batch_ds,{len(v_s2s)},{v:.6f}\n')
    for v in v_b2b: f.write(f'B2B,q5,{len(v_b2b)},{v:.6f}\n')
print(f'\nCSV → {csv_path}')

# ── Plot ──
groups = [
    ('Device-to-device',  v_s2s, '#0072B2', '#003366'),
    ('Sample-to-sample',  v_d2d, '#CC0000', '#990000'),
    ('Batch-to-batch',    v_b2b_v2, '#333333', '#000000'),
]
CM = 2.54
W1, H1 = 7, 5  # cm
PAD_L1, PAD_R1 = 1.0, 0.3  # cm
PAD_B1, PAD_T1 = 1.0, 0.5  # cm

fig = plt.figure(figsize=(W1 / CM, H1 / CM))
left = PAD_L1 / W1; right = 1 - PAD_R1 / W1
bottom = PAD_B1 / H1; top = 1 - PAD_T1 / H1
ax = fig.add_axes([left, bottom, right - left, top - bottom])

for label, vals, fill, edge in groups:
    if len(vals) == 0: continue
    s = np.sort(vals); n = len(s)
    y = np.arange(1, n + 1) / (n + 1)
    ax.scatter(s, y * 100, marker='o', s=28, linewidths=0.5,
               facecolors=fill, edgecolors=edge, alpha=0.85, zorder=5)
    eta, beta, rsq = weibull_params(vals)
    if eta and beta:
        v_min = max(0.01, s.min() * 0.85)
        V_fit = np.linspace(v_min, s.max() * 1.15, 300)
        ax.plot(V_fit, (1 - np.exp(-(V_fit / eta) ** beta)) * 100,
                color=edge, linewidth=0.75, zorder=6)

handles = []
for _, vals, fill, edge in groups:
    if len(vals) == 0: continue
    handles.append(plt.Line2D([0], [0], marker='o', linestyle='None', markersize=6,
                   markerfacecolor=fill, markeredgecolor=edge, markeredgewidth=0.5))

leg = ax.legend(handles, ['Device-to-device', 'Sample-to-sample', 'Batch-to-batch'],
                fontsize=6, frameon=False, loc='lower right')
for text, (_, _, fill, _) in zip(leg.get_texts(), groups):
    text.set_color(fill)
ax.set_xlabel('$V_\\mathrm{set}$ (V)', fontsize=8)
ax.set_ylabel('Cumulative Probability (%)', fontsize=8)
ax.tick_params(labelsize=6)
ax.set_xticks([0, 0.5, 1.0, 1.5, 2.0])
ax.set_yticks([0, 20, 40, 60, 80, 100])
ax.set_xlim(0, 2.0); ax.set_ylim(-5, 105)

out_pdf = os.path.join(OUTPUT, 'vset_final_cdf.pdf')
out_png = os.path.join(OUTPUT, 'vset_final_cdf.png')
fig.savefig(out_pdf, dpi=600, facecolor='white')
fig.savefig(out_png, dpi=600, facecolor='white')
plt.close(fig)
print(f'  → {out_pdf}\n  → {out_png}')

# ── Weibull plot (log x-axis) ──
print('\n--- Weibull plot (log V_set) ---')
fig2, ax2 = plt.subplots(figsize=(6.5 * 0.394, 6 * 0.394))

for label, vals, fill, edge in groups:
    if len(vals) == 0: continue
    s = np.sort(vals); n = len(s)
    y = np.arange(1, n + 1) / (n + 1)
    ax2.semilogx(s, y * 100, marker='o', linestyle='None', markersize=4,
                  markerfacecolor=fill, markeredgecolor=edge, markeredgewidth=0.5, alpha=0.85, zorder=5)
    eta, beta, rsq = weibull_params(vals)
    if eta and beta:
        v_min = max(0.01, s.min() * 0.85)
        V_fit = np.logspace(np.log10(v_min), np.log10(s.max() * 1.15), 300)
        ax2.semilogx(V_fit, (1 - np.exp(-(V_fit / eta) ** beta)) * 100,
                     color=edge, linewidth=0.75, zorder=6)

handles2 = []
for _, vals, fill, edge in groups:
    if len(vals) == 0: continue
    handles2.append(plt.Line2D([0], [0], marker='o', linestyle='None', markersize=6,
                   markerfacecolor=fill, markeredgecolor=edge, markeredgewidth=0.5))

leg2 = ax2.legend(handles2, ['Device-to-device', 'Sample-to-sample', 'Batch-to-batch'],
                  fontsize=6, frameon=False, loc='upper left')
for text, (_, _, fill, _) in zip(leg2.get_texts(), groups):
    text.set_color(fill)

ax2.set_xlabel('$V_\\mathrm{set}$ (V)', fontsize=8)
ax2.set_ylabel('Cumulative Probability (%)', fontsize=8)
ax2.tick_params(labelsize=6)
ax2.set_xlim(0.1, 2.5)
ax2.set_xticks([0.1, 0.2, 0.5, 1.0, 2.5])
ax2.get_xaxis().set_major_formatter(plt.ScalarFormatter())
ax2.set_ylim(-5, 105)

plt.tight_layout(pad=0.3)

wb_pdf = os.path.join(OUTPUT, 'vset_final_weibull.pdf')
wb_png = os.path.join(OUTPUT, 'vset_final_weibull.png')
fig2.savefig(wb_pdf, dpi=600, facecolor='white')
fig2.savefig(wb_png, dpi=600, facecolor='white')
plt.close(fig2)
print(f'  → {wb_pdf}\n  → {wb_png}')
print('Done.')
