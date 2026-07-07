#!/usr/bin/env python3
"""Parse CasaXPS export files and plot C 1s, N 1s, O 1s overlay figures.

Layout:
- Left y-axis: Doping (normalized signal, range 0-2)
- Right y-axis: Normal (normalized signal inverted, range -1 to 1)
- Deconvolution components shown as filled peaks above background
"""

from pathlib import Path
import matplotlib.pyplot as plt
import numpy as np

HERE = Path(__file__).parent
FIGS = HERE / "figures"
FIGS.mkdir(exist_ok=True)

plt.rcParams.update({
    "font.family": "sans-serif",
    "font.sans-serif": ["Helvetica"],
    "font.size": 10,
    "axes.linewidth": 0.8,
    "axes.labelsize": 10,
    "xtick.major.width": 0.6,
    "xtick.direction": "out",
    "xtick.major.size": 3,
    "xtick.labelsize": 8,
})


def parse_xps_file(path):
    """Parse CasaXPS export file, return rich dict per region."""
    text = path.read_text()
    sections = text.split("\nCycle 0:")
    regions = {}

    for sec in sections:
        if not sec.strip():
            continue
        lines = sec.strip().split("\n")
        header_line = lines[0].strip()

        region = None
        for tag in ["C 1s", "N 1s", "O 1s"]:
            if tag in header_line:
                region = tag.replace(" ", "")
                break
        if region is None:
            continue

        data_start = None
        header_parts = []
        counts_idx = bg_idx = -1
        for i, line in enumerate(lines):
            if line.startswith("K.E."):
                header_parts = line.strip().split("\t")
                data_start = i + 1
                for j, p in enumerate(header_parts):
                    if p == "Counts":
                        counts_idx = j
                    elif p == "Background":
                        bg_idx = j
                break

        if data_start is None or counts_idx < 0 or bg_idx < 0:
            continue

        comp_names = header_parts[counts_idx + 1:bg_idx]

        try:
            be_idx = header_parts.index("B.E.")
            cps_idx = header_parts.index("CPS")
            bg_cps_idx = header_parts.index("Background CPS")
            env_cps_idx = header_parts.index("Envelope CPS")
        except ValueError:
            continue

        n_comps = len(comp_names)
        comp_cps_idx = list(range(cps_idx + 1, cps_idx + 1 + n_comps))

        be, cps, bg, env = [], [], [], []
        comps = {n: [] for n in comp_names}
        for line in lines[data_start:]:
            line = line.strip()
            if not line:
                continue
            parts = line.split("\t")
            needed = max(comp_cps_idx + [be_idx, cps_idx, bg_cps_idx, env_cps_idx])
            if len(parts) <= needed:
                continue
            try:
                be.append(float(parts[be_idx]))
                cps.append(float(parts[cps_idx]))
                bg.append(float(parts[bg_cps_idx]))
                env.append(float(parts[env_cps_idx]))
                for j, nm in enumerate(comp_names):
                    comps[nm].append(float(parts[comp_cps_idx[j]]))
            except (ValueError, IndexError):
                continue

        if not be:
            continue
        order = np.argsort(be)[::-1]
        result = {
            "be": np.array(be)[order],
            "cps": np.array(cps)[order],
            "background": np.array(bg)[order],
            "envelope": np.array(env)[order],
            "components": {nm: np.array(comps[nm])[order] for nm in comp_names},
            "comp_names": comp_names,
        }
        regions[region] = result
    return regions


FITTING_PALETTE = ["#0072B2", "#E69F00", "#D55E00", "#009E73", "#CC79A7"]

REGION_LABELS = {"C1s": "C 1s", "N1s": "N 1s", "O1s": "O 1s"}


X_LIMITS = {"C1s": (280, 295), "N1s": (410, 395), "O1s": (542.5, 525)}
Y1_LIMITS = {"C1s": (0.25, 2), "N1s": (0.8, 1.3), "O1s": (0.45, 1.6)}
Y2_LIMITS = {"C1s": (-0.75, 1.1), "N1s": (0.73, 1.02), "O1s": (0, 1.1)}


def plot_region_on_ax(ax, ndata, ddata, region):
    """Plot one region on a given axes with twinx. Returns (ax1, ax2)."""
    be = ndata["be"]
    n_max = ndata["envelope"].max()
    d_max = ddata["envelope"].max()

    n_env = ndata["envelope"] / n_max
    d_env = ddata["envelope"] / d_max
    n_bg = ndata["background"] / n_max
    d_bg = ddata["background"] / d_max

    def get_comp_norm(data, scale_max):
        bg = data["background"]
        return {nm: np.maximum(data["components"][nm] - bg, 0) / scale_max
                for nm in data["comp_names"]}

    n_comp = get_comp_norm(ndata, n_max)
    d_comp = get_comp_norm(ddata, d_max)

    n_raw = ndata["cps"] / n_max
    d_raw = ddata["cps"] / d_max
    n_comps = ddata["comp_names"]
    n_colors = FITTING_PALETTE[:len(n_comps)]

    # Doping on y1 (left)
    ax.scatter(be, d_raw, c="#666666", edgecolors="#666666", s=1, alpha=0.35, zorder=5)
    for i, nm in enumerate(ddata["comp_names"]):
        c = n_colors[i]
        comp_curve = d_bg + d_comp[nm]
        ax.fill_between(be, d_bg, comp_curve, color=c, alpha=0.35, label=nm)
        ax.plot(be, comp_curve, color=c, linewidth=1.5)
    ax.plot(be, d_env, color="#B2182B", linewidth=2)
    ax.plot(be, d_bg, color="#B2182B", linewidth=0.5, linestyle="--")

    # Normal on y2 (right)
    ax2 = ax.twinx()
    ax2.scatter(be, n_raw, c="#666666", edgecolors="#666666", s=1, alpha=0.35, zorder=5)
    ax2.plot(be, n_bg, color="#2166AC", linewidth=0.5, linestyle="--")
    for i, nm in enumerate(ndata["comp_names"]):
        c = n_colors[i]
        comp_curve = n_bg + n_comp[nm]
        ax2.fill_between(be, n_bg, comp_curve, color=c, alpha=0.35)
        ax2.plot(be, comp_curve, color=c, linewidth=1.5)
    ax2.plot(be, n_env, color="#2166AC", linewidth=2)

    # Limits
    xl = X_LIMITS.get(region)
    if xl:
        ax.set_xlim(*xl)
    ax.set_ylim(*Y1_LIMITS.get(region, (0, 2)))
    ax2.set_ylim(*Y2_LIMITS.get(region, (-1, 1)))

    ax.tick_params(axis="y", which="both", left=False, labelleft=False)
    ax2.tick_params(axis="y", which="both", right=False, labelright=False)

    ax.set_xlabel("Binding Energy (eV)")
    ax.set_ylabel("Intensity (counts)")
    ax2.set_ylabel("")

    ax.text(0.97, 0.92, REGION_LABELS.get(region, region),
            transform=ax.transAxes, fontsize=12, weight="bold",
            ha="right", va="top")

    from matplotlib.patches import Patch
    legend_elements = [
        Patch(facecolor=n_colors[i], alpha=0.6, label=n)
        for i, n in enumerate(n_comps)
    ]
    ax.legend(handles=legend_elements, frameon=False, fontsize=9,
              loc="upper left")

    return ax, ax2


def main():
    ndata = parse_xps_file(HERE / "normal")
    ddata = parse_xps_file(HERE / "doping")

    # Single combined figure: 3 panels side-by-side
    fig, axes = plt.subplots(1, 3, figsize=(15, 8),
                             gridspec_kw={"wspace": 0.25},
                             constrained_layout=True)

    regions = ["C1s", "N1s", "O1s"]
    for i, region in enumerate(regions):
        if region not in ndata or region not in ddata:
            print(f"  WARNING: {region} not found, skipping")
            continue
        plot_region_on_ax(axes[i], ndata[region], ddata[region], region)

    w_cm, h_cm = 15 * 2.54, 8 * 2.54
    outpath = FIGS / "xps_overlay.pdf"
    fig.savefig(outpath, dpi=300)
    plt.close(fig)
    print(f"  Saved {outpath}")


if __name__ == "__main__":
    main()
