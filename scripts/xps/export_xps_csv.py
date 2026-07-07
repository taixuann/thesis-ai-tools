#!/usr/bin/env python3
"""Export normalized XPS data per region per state as CSV files.

All curves at zero baseline (background-subtracted).
"""

from pathlib import Path
import numpy as np
from plot_xps_overlay import parse_xps_file

HERE = Path(__file__).parent

STATES = {"normal": HERE / "normal", "doping": HERE / "doping"}
REGIONS = ["C1s", "N1s", "O1s"]
OUT_DIR = HERE / "csv_exports"
OUT_DIR.mkdir(exist_ok=True)

for state, path in STATES.items():
    data = parse_xps_file(path)
    for region in REGIONS:
        if region not in data:
            continue
        d = data[region]
        scale = d["envelope"].max()
        be = d["be"]
        bg = d["background"] / scale
        intensity = (d["cps"] - d["background"]) / scale
        total_fit = (d["envelope"] - d["background"]) / scale
        comps = np.column_stack([
            np.maximum(d["components"][nm] - d["background"], 0) / scale
            for nm in d["comp_names"]
        ])
        header = "BE,intensity," + ",".join(d["comp_names"]) + ",total-fit"
        rows = np.column_stack([be, intensity, comps, total_fit])
        out = OUT_DIR / f"{state}_{region}.csv"
        np.savetxt(out, rows, delimiter=",", header=header, comments="",
                   fmt="%.8f")
        print(f"  Saved {out}")

print("Done. total-fit = sum(components)")
