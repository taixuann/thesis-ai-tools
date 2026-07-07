"""Plot PPF conductance: G = I/V at pulse plateau, 50 pulses."""
import matplotlib.pyplot as plt
import matplotlib
import csv
import numpy as np

matplotlib.rcParams.update({
    "font.family": "Helvetica", "font.size": 8,
    "axes.linewidth": 1, "xtick.major.width": 1, "ytick.major.width": 1,
    "xtick.direction": "out", "ytick.direction": "out",
    "xtick.major.size": 4, "ytick.major.size": 4,
})

# Read data
pulses, currents = [], []
with open("pulse-ppf.txt") as f:
    reader = csv.DictReader(f, delimiter="\t")
    for row in reader:
        pulses.append(int(row["index"]))
        currents.append(float(row["avg_current_a"]))

# Calculate conductance
G0 = 77.5e-6  # 2e^2/h in Siemens
V_read = 2.0  # pulse plateau voltage
G_ms = [i / V_read * 1000 for i in currents]   # mS
G_G0 = [i / V_read / G0 for i in currents]     # quantum units

# Linear fit
z = np.polyfit(pulses, G_G0, 1)
p = np.poly1d(z)

fig, ax = plt.subplots(figsize=(4, 3))

ax.plot(pulses, G_G0, "o", color="#388E3C", markersize=3, linewidth=0)
ax.plot(pulses, p(pulses), "--", color="#388E3C", linewidth=0.8, alpha=0.7)

ax.set_xlabel("Pulse number")
ax.set_ylabel("Conductance (G₀)")
ax.set_title("PPF pulse train", fontsize=9)

# Annotations
ax.text(5, 6.28, f"slope = {z[0]*50:.3f} G₀/50 pulses", fontsize=7, color="#388E3C")
ax.text(5, 6.24, f"G₁ = {G_G0[0]:.2f} G₀", fontsize=7, color="#555")
ax.text(5, 6.20, f"G₅₀ = {G_G0[-1]:.2f} G₀", fontsize=7, color="#555")
ax.text(5, 6.16, f"Δ = {(G_G0[-1]/G_G0[0]-1)*100:.1f}%", fontsize=7, color="#555")

ax.set_ylim(6.0, 6.4)
ax.set_xlim(0, 52)

fig.tight_layout()
fig.savefig("conductance_ppf.pdf", bbox_inches="tight", dpi=300)
print(f"Saved conductance_ppf.pdf")
print(f"G₁ = {G_G0[0]:.3f} G₀, G₅₀ = {G_G0[-1]:.3f} G₀")
print(f"Slope = {z[0]*50:.4f} G₀/50 pulses, Δ = {(G_G0[-1]/G_G0[0]-1)*100:.2f}%")
