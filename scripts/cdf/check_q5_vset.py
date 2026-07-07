#!/usr/bin/env python3
"""Plot q5 IV curves with detected V_set for visual verification (onset method)."""

import os, re, sys
import numpy as np
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
    pos = v > 0.1; neg = v < -0.1
    if not np.any(pos) or not np.any(neg): return True
    p_pos = float(np.max(np.abs(i[pos])))
    p_neg = float(np.max(np.abs(i[neg])))
    if p_neg <= 0: return True
    return (p_pos / p_neg) >= min_ratio

def detect_vset(v, i):
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

def is_q5_file(fname): return 'cu-c-pda(q5)' in fname.lower()

def is_iv_file(fname):
    f = fname.lower()
    iv_kw = ['iv-bipolar-sweep', 'iv-sweep', 'iv list sweep', 'i_v list sweep', 'dual vsweep', '2-terminal']
    non_iv_kw = ['pulse', 'endurance', 'stp', 'ppf', 'relax', 'pattern', 'discard', 'plsdiv', 'test-full']
    if any(k in f for k in non_iv_kw): return False
    return any(k in f for k in iv_kw)

def skip_file(fname):
    return any(k in fname.lower() for k in ['discard']) or not fname.endswith('.csv')

# Collect q5 files
q5_pass = []
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
        if is_q5_file(fname) and is_iv_file(fname):
            with open(fpath, encoding='utf-8-sig', errors='replace') as fh:
                sample = fh.read(50000)
            if 'DataValue' in sample or 'SetupTitle,' in sample:
                v, i = parse_keysight(fpath)
            else:
                v, i = parse_keysight(fpath)
            vs = detect_vset(v, i)
            if vs is not None and vs >= 0.2:
                m = re.search(r'(r[\d]+-c[\d]+)', fname)
                dev = m.group(1) if m else 'unknown'
                q5_pass.append((fname, dev, vs, v, i))

print(f'Found {len(q5_pass)} q5 files with valid V_set (onset method)')

# Pick diverse: one per device, then fill low/mid
seen_devs = set()
examples = []
for entry in q5_pass:
    fname, dev, vs, v, i = entry
    if dev not in seen_devs and len(examples) < 12:
        examples.append(entry); seen_devs.add(dev)

used_fnames = {e[0] for e in examples}
vset_sorted = sorted(q5_pass, key=lambda x: x[2])
for entry in vset_sorted:
    if len(examples) >= 12: break
    if entry[0] not in used_fnames:
        examples.append(entry); used_fnames.add(entry[0])

print(f'Plotting {len(examples)} examples...')

n_rows = int(np.ceil(len(examples) / 4))
fig, axes = plt.subplots(n_rows, 4, figsize=(10 * 0.394 * 4, 2.5 * 0.394 * n_rows * 4))
axes = axes.flatten()
fig.patch.set_facecolor('white')

for idx, (fname, dev, vs, v, i) in enumerate(examples):
    ax = axes[idx]
    ax.plot(v, -i, '-k', linewidth=0.5)
    ax.axvline(vs, color='red', linewidth=0.8, linestyle='--')
    ax.plot(vs, np.interp(vs, v, -i), 'ro', markersize=3)
    ax.set_title(f'{dev} V_set={vs:.2f}V', fontsize=6)
    ax.tick_params(labelsize=5)
    ax.set_xlabel('Voltage (V)', fontsize=5)
    ax.set_ylabel('Current (A)', fontsize=5)
    ax.set_xlim(0, 2.0)

for idx in range(len(examples), len(axes)):
    axes[idx].axis('off')

plt.tight_layout(pad=0.5)
out_pdf = os.path.join(OUTPUT, 'q5_vset_check.pdf')
out_png = os.path.join(OUTPUT, 'q5_vset_check.png')
fig.savefig(out_pdf, dpi=600, facecolor='white')
fig.savefig(out_png, dpi=600, facecolor='white')
plt.close(fig)
print(f'  → {out_pdf}\n  → {out_png}')
