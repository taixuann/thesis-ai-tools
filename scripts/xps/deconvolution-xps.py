#!/usr/bin/env python3
"""
XPS peak deconvolution for PDA films: C 1s, N 1s, and O 1s core levels.

Reads raw spectral data (BE vs intensity) for both normal and doping
conditions. Performs peak fitting with mixed lineshapes (GL for symmetric
peaks, LA for asymmetric features) and outputs component parameters.

Usage:
    python deconvolution-xps.py <data_dir>

Data directory structure (e.g., xps-v2 16-07-24-123/):
    c_1s-normal.csv    c_1s-dope.csv
    n_1s-normal.csv    n_1s-dope.csv
    o_1s-normal.csv    o_1s-dope.csv

Each CSV: BE, intensity, component_1, ..., component_N, total_fit
"""

import sys
from pathlib import Path
import numpy as np
import matplotlib.pyplot as plt


# ---------------------------------------------------------------------------
# Lineshape functions
# ---------------------------------------------------------------------------

def gl(x, center, height, fwhm, mu=0.30):
    """Gaussian-Lorentzian product: GL(mu) with mu fraction Lorentzian."""
    sigma = fwhm / (2 * np.sqrt(2 * np.log(2)))
    g = np.exp(-((x - center) / sigma) ** 2)
    l = 1 / (1 + ((x - center) / (fwhm / 2)) ** 2)
    return height * ((1 - mu) * g + mu * l)


def la(x, center, height, fwhm, alpha=1.4, beta=1.4, cutoff=100):
    """Asymmetric Lorentzian: LA(alpha, beta, cutoff)."""
    sigma = fwhm / 2
    left = 1 / (1 + ((x - center) / sigma) ** 2) ** alpha
    right = 1 / (1 + ((x - center) / sigma) ** 2) ** beta
    cutoff_mask = np.exp(-((x - center) / (cutoff * sigma)) ** 2)
    asym = np.where(x <= center, left, right) * cutoff_mask
    return height * asym


# ---------------------------------------------------------------------------
# Region configuration
# ---------------------------------------------------------------------------

REGIONS = {
    "C1s": {
        "file_tag": "c_1s",
        "x_range": (280, 295),
        "bg_type": "shirley",
        "components": [
            {"name": "C-C/C=C",  "lineshape": "GL",  "mu": 0.30, "center": 284.7, "fwhm": 1.4},
            {"name": "C-N",      "lineshape": "GL",  "mu": 0.30, "center": 285.7, "fwhm": 1.6},
            {"name": "C-O",      "lineshape": "GL",  "mu": 0.30, "center": 286.5, "fwhm": 1.6},
            {"name": "C=O",      "lineshape": "GL",  "mu": 0.30, "center": 287.8, "fwhm": 1.6},
            {"name": "pi-pi*",   "lineshape": "LA",  "alpha": 1.4, "beta": 1.4, "cutoff": 100, "center": 290.1, "fwhm": 2.8},
        ],
    },
    "N1s": {
        "file_tag": "n_1s",
        "x_range": (404, 395),
        "bg_type": "shirley",
        "components": [
            {"name": "C=N-",     "lineshape": "GL",  "mu": 0.30, "center": 399.0, "fwhm": 1.7},
            {"name": "-NH-",     "lineshape": "GL",  "mu": 0.30, "center": 400.2, "fwhm": 1.6},
            {"name": "NH3+",     "lineshape": "GL",  "mu": 0.30, "center": 401.7, "fwhm": 1.7},
        ],
    },
    "O1s": {
        "file_tag": "o_1s",
        "x_range": (542, 525),
        "bg_type": "shirley",
        "components": [
            {"name": "C-O/O-H",  "lineshape": "GL",  "mu": 0.30, "center": 532.8, "fwhm": 2.0},
            {"name": "C=O",      "lineshape": "GL",  "mu": 0.30, "center": 531.4, "fwhm": 1.8},
            {"name": "O-C=O/H2O","lineshape": "GL",  "mu": 0.30, "center": 534.5, "fwhm": 2.2},
        ],
    },
}


# ---------------------------------------------------------------------------
# Background
# ---------------------------------------------------------------------------

def shirley_bg(x, intensity):
    """Iterative Shirley background."""
    bg = np.full_like(intensity, intensity[0])
    for _ in range(20):
        bg_new = np.full_like(intensity, intensity[0])
        total_int = intensity - bg
        total = np.trapz(total_int, x)
        for i in range(len(x)):
            left = np.trapz(total_int[i:], x[i:])
            bg_new[i] = intensity[0] + (intensity[-1] - intensity[0]) * left / total
        if np.max(np.abs(bg_new - bg)) < 1e-6:
            break
        bg = bg_new
    return bg


# ---------------------------------------------------------------------------
# Fitting
# ---------------------------------------------------------------------------

def fit_region(be, raw, config):
    """Fit components to one region. Returns component dicts."""
    # Shirley background
    bg = shirley_bg(be, raw)
    signal = raw - bg
    signal = np.clip(signal, 0, None)

    comps = config["components"]
    n = len(comps)
    fitted = []

    # Iterative fitting: subtract neighbours, fit each peak
    for idx, comp in enumerate(comps):
        other_signal = np.copy(signal)
        for j in range(n):
            if j == idx:
                continue
            c = comps[j]
            if c["lineshape"] == "GL":
                other_signal -= gl(be, c["center"], np.max(signal) * 0.5, c["fwhm"], c.get("mu", 0.30))
            else:
                other_signal -= la(be, c["center"], np.max(signal) * 0.5, c["fwhm"],
                                   c.get("alpha", 1.4), c.get("beta", 1.4), c.get("cutoff", 100))
        other_signal = np.clip(other_signal, 0, None)

        # Fit height
        x0 = comp["center"]
        fw = comp["fwhm"]
        mask = (be > x0 - 2.5 * fw) & (be < x0 + 2.5 * fw)
        if not np.any(mask):
            height_est = np.max(other_signal) * 0.3
        else:
            height_est = np.max(other_signal[mask])

        # Refine height by least squares
        if comp["lineshape"] == "GL":
            model = gl(be, x0, 1.0, fw, comp.get("mu", 0.30))
        else:
            model = la(be, x0, 1.0, fw, comp.get("alpha", 1.4),
                       comp.get("beta", 1.4), comp.get("cutoff", 100))
        h = np.linalg.lstsq(model[:, None], other_signal, rcond=None)[0][0]
        h = max(h, 0)

        # Compute area
        if comp["lineshape"] == "GL":
            curve = gl(be, x0, h, fw, comp.get("mu", 0.30))
        else:
            curve = la(be, x0, h, fw, comp.get("alpha", 1.4),
                       comp.get("beta", 1.4), comp.get("cutoff", 100))
        area = np.trapz(curve, be)

        fitted.append({
            "name": comp["name"],
            "center": x0,
            "fwhm": fw,
            "height": h,
            "area": area,
            "curve": curve,
        })

    # Normalize area to percentage
    total_area = sum(f["area"] for f in fitted)
    for f in fitted:
        f["pct"] = 100 * f["area"] / total_area if total_area > 0 else 0

    return bg, fitted


# ---------------------------------------------------------------------------
# Plotting
# ---------------------------------------------------------------------------

COLORS = ["#0072B2", "#E69F00", "#D55E00", "#009E73", "#CC79A7"]


def plot_region(ax, be, raw, bg, fitted, config, label, color_scheme):
    """Plot one region on given axes."""
    ax.scatter(be, raw, c="#666666", s=2, alpha=0.4, zorder=2, label="Data")
    ax.plot(be, bg, color="#333333", linewidth=0.6, linestyle="--", label="Background")

    envelope = bg.copy()
    for i, f in enumerate(fitted):
        c = COLORS[i % len(COLORS)]
        ax.fill_between(be, bg, bg + f["curve"], color=c, alpha=0.25)
        ax.plot(be, bg + f["curve"], color=c, linewidth=1.0, label=f["name"])
        envelope += f["curve"]

    ax.plot(be, envelope, color=color_scheme, linewidth=1.5, label="Envelope")
    ax.set_xlabel("Binding Energy (eV)")
    ax.set_ylabel("Intensity")


def print_table(region, normal_fit, doping_fit):
    """Print ASCII deconvolution table."""
    print(f"\n{'='*70}")
    print(f"  {region}")
    print(f"{'='*70}")
    header = f"{'Component':<18} | {'Normal BE':>8} {'FWHM':>7} {'Area%':>7} | {'Doping BE':>8} {'FWHM':>7} {'Area%':>7}"
    print(header)
    print("-" * len(header))
    for nf, df in zip(normal_fit, doping_fit):
        print(f"{nf['name']:<18} | {nf['center']:>8.2f} {nf['fwhm']:>7.2f} {nf['pct']:>7.1f} | "
              f"{df['center']:>8.2f} {df['fwhm']:>7.2f} {df['pct']:>7.1f}")


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    if len(sys.argv) < 2:
        print(f"Usage: {sys.argv[0]} <data_directory>")
        print("Data directory must contain c_1s, n_1s, o_1s CSV files.")
        sys.exit(1)

    data_dir = Path(sys.argv[1])
    if not data_dir.is_dir():
        print(f"Error: {data_dir} not found")
        sys.exit(1)

    fig, axes = plt.subplots(2, 3, figsize=(18, 10))
    fig.subplots_adjust(hspace=0.35, wspace=0.30)

    for col_idx, (region_key, config) in enumerate(REGIONS.items()):
        tag = config["file_tag"]

        # Load normal and doping
        normal_csv = data_dir / f"{tag}-normal.csv"
        doping_csv = data_dir / f"{tag}-dope.csv"

        if not normal_csv.exists() or not doping_csv.exists():
            print(f"  WARNING: Missing files for {region_key}")
            continue

        n_data = np.loadtxt(normal_csv, skiprows=1, delimiter=",")
        d_data = np.loadtxt(doping_csv, skiprows=1, delimiter=",")

        n_be, n_raw = n_data[:, 0], n_data[:, 1]
        d_be, d_raw = d_data[:, 0], d_data[:, 1]

        # Fit
        n_bg, n_fit = fit_region(n_be, n_raw, config)
        d_bg, d_fit = fit_region(d_be, d_raw, config)

        # Print table
        print_table(region_key, n_fit, d_fit)

        # Plot normal
        ax_n = axes[0, col_idx]
        plot_region(ax_n, n_be, n_raw, n_bg, n_fit, config, "#2166AC", "#2166AC")
        ax_n.set_title(f"{region_key} — Normal")
        ax_n.invert_xaxis()
        ax_n.set_xlim(*config["x_range"])

        # Plot doping
        ax_d = axes[1, col_idx]
        plot_region(ax_d, d_be, d_raw, d_bg, d_fit, config, "#B2182B", "#B2182B")
        ax_d.set_title(f"{region_key} — Doping")
        ax_d.invert_xaxis()
        ax_d.set_xlim(*config["x_range"])

    outpath = data_dir / "deconvolution_results.pdf"
    fig.savefig(outpath, dpi=300, bbox_inches="tight")
    print(f"\n  Figure saved to {outpath}")
    plt.close(fig)


if __name__ == "__main__":
    main()
