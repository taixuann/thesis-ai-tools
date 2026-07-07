"""Plot conductance data: STP voltage sweep + PPF facilitation."""
import matplotlib.pyplot as plt
import matplotlib
import pandas as pd
import numpy as np

matplotlib.rcParams.update({
    "font.family": "Helvetica", "font.size": 8,
    "axes.linewidth": 1, "xtick.major.width": 1, "ytick.major.width": 1,
    "xtick.direction": "out", "ytick.direction": "out",
    "xtick.major.size": 4, "ytick.major.size": 4,
})

# --- Panel A: STP conductance vs voltage ---
df_stp = pd.read_csv("conductance_stp_voltagesweep.csv", comment="#")

fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(7, 3.2), gridspec_kw={"wspace": 0.45})

ax1.plot(df_stp["Voltage_V"], df_stp["G_rise_G0"], "o-", color="#D32F2F",
         markersize=5, linewidth=1.2, label="Rise (filament formed)")
ax1.plot(df_stp["Voltage_V"], df_stp["G_fall_G0"], "s--", color="#1976D2",
         markersize=5, linewidth=1.2, label="Fall (after dissolution)")
ax1.axhline(y=1, color="gray", linewidth=0.6, linestyle=":", alpha=0.5)
ax1.text(1.3, 1.8, "1 G₀ (single atom)", fontsize=7, color="gray", alpha=0.7)
ax1.set_xlabel("Pulse amplitude (V)")
ax1.set_ylabel("Conductance (G₀)")
ax1.set_title("STP voltage sweep", fontsize=9)
ax1.legend(fontsize=7, frameon=False)
ax1.set_ylim(0, 32)

# --- Panel B: PPF conductance vs pulse number ---
df_ppf = pd.read_csv("conductance_ppf.csv", comment="#")

ax2.plot(df_ppf["Pulse"], df_ppf["G_G0"], "o-", color="#388E3C",
         markersize=3, linewidth=0.8)
ax2.set_xlabel("Pulse number")
ax2.set_ylabel("Conductance (G₀)")
ax2.set_title("PPF pulse train", fontsize=9)
ax2.set_ylim(6.0, 6.4)

# Fit line
z = np.polyfit(df_ppf["Pulse"], df_ppf["G_G0"], 1)
p = np.poly1d(z)
ax2.plot(df_ppf["Pulse"], p(df_ppf["Pulse"]), "--", color="#388E3C",
         linewidth=0.6, alpha=0.6)
ax2.text(35, 6.05, f"slope = {z[0]*50:.2f} G₀/50 pulses",
         fontsize=7, color="#388E3C")

fig.savefig("conductance_overview.pdf", bbox_inches="tight", dpi=300)
print("Saved conductance_overview.pdf")
