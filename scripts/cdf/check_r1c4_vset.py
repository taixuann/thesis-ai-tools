#!/usr/bin/env python3
"""Check r1-c4 V_set detection — show IV curves with detected V_set."""

import os, re, numpy as np
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
    if os.path.isdir(dd): SEARCH_DIRS.append(dd)

def parse_lvm(filepath):
    v, i = [], []
    with open(filepath) as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith('***End_of_Header***') or \
               any(line.startswith(k) for k in ['LabVIEW','Writer_Version','Reader_Version',
               'Separator','Decimal_Separator','Multi_Headings','X_Columns','Time_Pref',
               'Operator','Date','Time','Channels','Samples','X_Dimension','X0','Delta_X',
               'X_Value','Comment']): continue
            parts = line.split('\t')
            if len(parts) >= 2:
                try:
                    v.append(float(parts[0].strip()))
                    i.append(float(parts[1].strip()))
                except ValueError: continue
    return np.array(v), np.array(i)

def check_bipolar_ratio(v, i, min_ratio=3):
    pos = v > 0.1; neg = v < -0.1
    if not np.any(pos) or not np.any(neg): return True
    p_pos = float(np.max(np.abs(i[pos])))
    p_neg = float(np.max(np.abs(i[neg])))
    if p_neg <= 0: return True
    return (p_pos / p_neg) >= min_ratio

def detect_vset(v, i):
    vs = detect_vset_log(v, i)
    if vs is not None: return vs if check_bipolar_ratio(v, i) else None
    vs = detect_vset_linear(v, i)
    if vs is not None: return vs if check_bipolar_ratio(v, i) else None
    return None

def detect_vset_log(v, i):
    if len(v) < 10: return None
    imax = np.argmax(v)
    if imax < 5: return None
    v_fwd = v[:imax+1]; i_fwd = i[:imax+1]
    if len(v_fwd) < 10: return None
    mask = v_fwd > 0.05; v_fwd = v_fwd[mask]; i_fwd = i_fwd[mask]
    if len(v_fwd) < 5: return None
    abs_i = np.abs(i_fwd)
    log_i = np.log10(np.clip(abs_i, 1e-15, None))
    grad = np.gradient(log_i, v_fwd)
    grad_smooth = np.convolve(grad, np.ones(3)/3, mode='same')
    peak_idx = np.argmax(grad_smooth)
    if grad_smooth[peak_idx] < 2 or peak_idx >= len(v_fwd) - 1: return None
    v_set = float(v_fwd[peak_idx])
    if v_set < 0.05: return None
    if np.median(abs_i[:3]) > 0 and abs_i[peak_idx] < np.median(abs_i[:3]) * 2.5: return None
    return v_set

def detect_vset_linear(v, i):
    if len(v) < 10: return None
    imax = np.argmax(v)
    if imax < 5: return None
    v_fwd = v[:imax+1]; i_fwd = i[:imax+1]
    if len(v_fwd) < 10: return None
    mask = v_fwd > 0.05; v_fwd = v_fwd[mask]; i_fwd = i_fwd[mask]
    if len(v_fwd) < 5: return None
    abs_i = np.abs(i_fwd)
    i_start = float(np.median(abs_i[:3]))
    if i_start > 1e-7: return None
    g_lin = np.gradient(abs_i, v_fwd)
    g_lin_s = np.convolve(g_lin, np.ones(3)/3, mode='same')
    peak_idx = np.argmax(g_lin_s)
    if peak_idx >= len(v_fwd) - 1: return None
    onset_idx = peak_idx
    for j in range(peak_idx, 0, -1):
        if g_lin_s[j] < g_lin_s[peak_idx] * 0.2: onset_idx = j; break
    v_set = float(v_fwd[onset_idx])
    if v_set < 0.1: return None
    if abs_i[peak_idx] < i_start * 5: return None
    if abs_i[peak_idx] < 1e-6: return None
    noise = np.std(g_lin_s[:5])
    if noise < 1e-15: return None
    if (g_lin_s[peak_idx] - np.median(g_lin_s[:5])) / noise < 10: return None
    return v_set

def is_q_file(fname):
    f = fname.lower()
    return ('cu-c-pda(q)' in f or 'cu-c-pda(q4)' in f) and 'q5' not in f

def is_iv_file(fname):
    f = fname.lower()
    iv_kw = ['iv-bipolar-sweep', 'iv-sweep', 'iv list sweep', 'i_v list sweep', 'dual vsweep', '2-terminal']
    non_iv_kw = ['pulse', 'endurance', 'stp', 'ppf', 'relax', 'pattern', 'discard', 'plsdiv', 'test-full']
    if any(k in f for k in non_iv_kw): return False
    return any(k in f for k in iv_kw)

def skip_file(fname):
    return any(k in fname.lower() for k in ['discard']) or not fname.endswith('.csv')

# Collect r1-c4 pass/fail
seen = set()
r1c4_pass = []
for srcdir in SEARCH_DIRS:
    if not os.path.isdir(srcdir): continue
    for fname in sorted(os.listdir(srcdir)):
        if skip_file(fname): continue
        fpath = os.path.join(srcdir, fname)
        try:
            s = os.stat(fpath); ino = (s.st_dev, s.st_ino)
            if ino in seen: continue; seen.add(ino)
        except: pass
        if is_q_file(fname) and is_iv_file(fname) and 'r1-c4' in fname:
            v, i = parse_lvm(fpath)
            vs = detect_vset(v, i)
            if vs is not None:
                r1c4_pass.append((fname, vs, v, i))

print(f'Found {len(r1c4_pass)} r1-c4 files with valid V_set')

# Group by V_set range
low = [e for e in r1c4_pass if e[1] < 0.5]
mid = [e for e in r1c4_pass if 0.5 <= e[1] <= 0.7]
high = [e for e in r1c4_pass if e[1] > 0.7]
print(f'  V_set < 0.5V: {len(low)}')
print(f'  0.5V ≤ V_set ≤ 0.7V: {len(mid)}')
print(f'  V_set > 0.7V: {len(high)}')

# Pick 4 from each range
examples = []
for pool in [low, mid, high]:
    step = max(1, len(pool) // 4)
    for i in range(0, min(4, len(pool)), 1):
        examples.append(pool[i * step])

examples = examples[:12]
print(f'Plotting {len(examples)} examples across V_set ranges...')

fig, axes = plt.subplots(3, 4, figsize=(10 * 0.394 * 4, 2.5 * 0.394 * 3 * 4))
axes = axes.flatten()
fig.patch.set_facecolor('white')

for idx, (fname, vs, v, i) in enumerate(examples):
    ax = axes[idx]
    ax.plot(v, -i, '-k', linewidth=0.5)
    ax.axvline(vs, color='red', linewidth=0.8, linestyle='--')
    ax.plot(vs, np.interp(vs, v, -i), 'ro', markersize=3)
    ax.set_title(f'V_set={vs:.2f}V', fontsize=6)
    ax.tick_params(labelsize=5)
    ax.set_xlabel('Voltage (V)', fontsize=5)
    ax.set_ylabel('Current (A)', fontsize=5)
    ax.set_xlim(-0.2, 1.0)

for idx in range(len(examples), len(axes)):
    axes[idx].axis('off')

plt.tight_layout(pad=0.5)
out_pdf = os.path.join(OUTPUT, 'r1c4_vset_check.pdf')
out_png = os.path.join(OUTPUT, 'r1c4_vset_check.png')
fig.savefig(out_pdf, dpi=600, facecolor='white')
fig.savefig(out_png, dpi=600, facecolor='white')
plt.close(fig)
print(f'  → {out_pdf}\n  → {out_png}')
