---
name: publication-plotting
description: Publication-ready scientific figures for journal submission (Nature, Science, Cell). Multi-panel layouts, colorblind-safe palettes, Nature/ACS/journal styling, memristor I-V figures, error bars. References sci-plot-config and sci-theme-plotting for science-cli data. Load when user says "publication figure", "journal figure", "Nature plot", "colorblind palette", "multi-panel figure", "publication-ready plot", "figure export", or any plotting task requiring journal submission standards.
license: MIT
metadata: {"version": "1.0", "port": "scientific-visualization → opencode"}
---

# Publication Plotting

Publication-ready scientific figures. Ported from Gemini's `scientific-visualization` skill + `plots_nature_theme.md` (antigravity).

## Overview

Scientific visualization transforms data into clear, accurate figures for publication. Create journal-ready plots with multi-panel layouts, error bars, significance markers, and colorblind-safe palettes. Export as PDF/EPS/TIFF using matplotlib, seaborn, and plotly.

This skill covers:
- **Publication-quality figures** — multi-panel, proper fonts, correct DPI
- **Nature-themed memristor I-V plots** — inward ticks, spine removal, high-contrast palettes
- **Journal-specific formatting** — Nature, Science, Cell, ACS, PLOS
- **Colorblind accessibility** — Okabe-Ito, viridis, grayscale testing
- **Statistically rigorous plots** — error bars, significance marks, sample sizes

---

## When to Use This Skill

- Creating plots or visualizations for journal manuscripts
- Preparing figures for submission (Nature, Science, Cell, PLOS, ACS, etc.)
- Making colorblind-friendly and accessible figures
- Building multi-panel figures with consistent styling
- Exporting figures at correct resolution and format
- Improving existing figures to meet publication standards
- Creating memristor I-V or endurance figures with Nature styling

---

## Quick Start: Publication-Quality Figure

```python
import matplotlib.pyplot as plt
import numpy as np

# Apply publication style
plt.style.use('~/.config/opencode/skills/publication-plotting/assets/publication.mplstyle')

# Single-column figure (Nature: 89mm = 3.5 inches)
fig, ax = plt.subplots(figsize=(3.5, 2.5))

x = np.linspace(0, 10, 100)
ax.plot(x, np.sin(x), label='sin(x)')
ax.plot(x, np.cos(x), label='cos(x)')

ax.set_xlabel('Time (seconds)')
ax.set_ylabel('Amplitude (mV)')
ax.legend(frameon=False)
ax.spines['top'].set_visible(False)
ax.spines['right'].set_visible(False)

# Save at 300 DPI
fig.savefig('figure1.pdf', dpi=300, bbox_inches='tight')
```

## Quick Start: Nature-Style Memristor I-V

### 🎨 Nature Publication Styling Standard

Use this directly for science-cli exported data:

| Element | Specification |
|---------|---------------|
| **Fonts** | Arial / Helvetica for labels and tick annotations |
| **Layout** | Single-column 3.5 × 3.2 inches |
| **Ticks** | Inward-pointing (`direction='in'`) on all axes |
| **Spines** | Remove top and right; bottom and left = 1.0 pt black |
| **Colors** | High-contrast: emerald green, cobalt blue, warm orange, royal purple |
| **Format** | Vector `.svg` + raster `.png` at 600 DPI |

```python
import matplotlib.pyplot as plt
import matplotlib as mpl

# Nature theme configuration
mpl.rcParams.update({
    'font.family': 'sans-serif',
    'font.sans-serif': ['Arial', 'Helvetica'],
    'font.size': 8,
    'axes.labelsize': 9,
    'axes.linewidth': 1.0,
    'xtick.labelsize': 7,
    'ytick.labelsize': 7,
    'xtick.direction': 'in',
    'ytick.direction': 'in',
    'xtick.top': True,
    'ytick.right': True,
    'lines.linewidth': 1.5,
})

# High-contrast Nature palette
nature_colors = ['#009E73', '#0072B2', '#E69F00', '#CC79A7',
                 '#56B4E9', '#D55E00', '#F0E442', '#000000']

fig, ax = plt.subplots(figsize=(3.5, 3.2))

# Plot I-V data (voltage vs current)
ax.plot(voltage, current, color=nature_colors[0], linewidth=1.5)
ax.set_xlabel('Voltage (V)')
ax.set_ylabel('Current (A)')

# Nature-standard spine removal
ax.spines['top'].set_visible(False)
ax.spines['right'].set_visible(False)

fig.savefig('iv_curve_nature.svg', dpi=600, bbox_inches='tight')
fig.savefig('iv_curve_nature.png', dpi=600, bbox_inches='tight')
```

---

## Core Principles

### 1. Resolution & File Format

| Type | DPI | Format |
|------|-----|--------|
| Line art / graphs | 600-1200 DPI | PDF, EPS, SVG (vector) |
| Photographs / microscopy | 300-600 DPI | TIFF, PNG |
| Combined | 300-600 DPI | TIFF, PDF |

> **Never use JPEG for scientific data** — lossy compression creates artifacts.

### 2. Colorblind Accessibility

Use the **Okabe-Ito palette** (distinguishable by all types of color blindness):

```python
okabe_ito = ['#E69F00', '#56B4E9', '#009E73', '#F0E442',
             '#0072B2', '#D55E00', '#CC79A7', '#000000']
plt.rcParams['axes.prop_cycle'] = plt.cycler(color=okabe_ito)
```

For heatmaps: use `viridis`, `plasma`, or `cividis` — never `jet` or `rainbow`.

**Always test figures in grayscale** to ensure interpretability.

### 3. Typography

- **Font family**: Arial or Helvetica (sans-serif)
- **Axis labels**: 7-9 pt at final size
- **Tick labels**: 6-8 pt minimum
- **Panel labels**: 8-12 pt, bold
- Sentence case: "Time (hours)" not "TIME (HOURS)"
- Always include units in parentheses

### 4. Figure Dimensions (Journal-Specific)

| Journal | Single | 1.5 Column | Double |
|---------|--------|------------|--------|
| **Nature** | 89 mm (3.5") | 120 mm (4.7") | 183 mm (7.2") |
| **Science** | 55 mm (2.17") | 120 mm (4.7") | 175 mm (6.89") |
| **Cell** | 85 mm (3.35") | — | 178 mm (7.0") |
| **PLOS** | 83 mm (3.27") | 114 mm (4.49") | 173 mm (6.81") |
| **ACS** | 82.5 mm (3.25") | — | 178 mm (7.0") |

### 5. Multi-Panel Figures

```python
from string import ascii_uppercase

fig = plt.figure(figsize=(7, 4))
gs = fig.add_gridspec(2, 2, hspace=0.4, wspace=0.4)

ax1 = fig.add_subplot(gs[0, 0])
ax2 = fig.add_subplot(gs[0, 1])
ax3 = fig.add_subplot(gs[1, 0])
ax4 = fig.add_subplot(gs[1, 1])

for i, ax in enumerate([ax1, ax2, ax3, ax4]):
    ax.text(-0.15, 1.05, ascii_uppercase[i],
            transform=ax.transAxes, fontsize=10,
            fontweight='bold', va='top')
```

---

## Common Tasks

### Task 1: Publication-Ready Line Plot

1. Apply publication style (`assets/publication.mplstyle` or scripts)
2. Set figure size for target journal (see table above)
3. Use colorblind-friendly colors
4. Add error bars (SEM, SD, or CI — specify in caption)
5. Label axes with units
6. Remove unnecessary spines
7. Save in vector format

### Task 2: Nature-Style Memristor I-V Figure

1. Export data from science-cli: `sci export --study <study> --format csv`
2. Apply Nature styling configuration (see Quick Start above)
3. Use high-contrast colors for cycle overlays
4. For endurance overlays: semi-transparent grey envelope + highlighted cycles
5. Save as SVG (vector) + PNG (preview) at 600 DPI
6. Inward ticks, spine removal, Arial/Helvetica font

### Task 3: Colorblind-Friendly Heatmap

```python
import seaborn as sns
fig, ax = plt.subplots(figsize=(5, 4))
corr = df.corr()
mask = np.triu(np.ones_like(corr, dtype=bool))
sns.heatmap(corr, mask=mask, annot=True, fmt='.2f',
            cmap='RdBu_r', center=0, square=True,
            linewidths=1, cbar_kws={'shrink': 0.8}, ax=ax)
```

### Task 4: Prepare for Specific Journal

1. Check journal requirements in `references/journal_requirements.md`
2. Set figure dimensions per journal
3. Apply journal-specific style (Nature: lowercase panel labels; Science: (A),(B) format)
4. Export in required format (PDF for most, TIFF for ACS)
5. Verify DPI meets requirements

### Task 5: Statistical Comparison Plot

```python
import seaborn as sns

fig, ax = plt.subplots(figsize=(3.5, 3))
sns.boxplot(data=df, x='treatment', y='response',
            order=['Control', 'Low', 'High'], palette='Set2', ax=ax)
sns.stripplot(data=df, x='treatment', y='response',
              order=['Control', 'Low', 'High'],
              color='black', alpha=0.3, size=3, ax=ax)
ax.set_ylabel('Response (μM)')
sns.despine()

# Mark significance
ax.text(0.5, max_y * 1.1, '***', ha='center', fontsize=8)
```

---

## Statistical Rigor

**Always include:**
- Error bars (SD, SEM, or CI — specify which in caption)
- Sample size (n) in figure or caption
- Statistical significance markers (*, **, ***)
- Individual data points when possible (not just summary statistics)

## Grayscale Compatibility

All figures should be interpretable in grayscale:
- Use different line styles (solid, dashed, dotted)
- Use different marker shapes (circles, squares, triangles)
- Add hatching patterns to bars
- Ensure sufficient luminance contrast

---

## Common Pitfalls

1. ❌ **Font too small**: 6-7 pt minimum at final print size
2. ❌ **JPEG for graphs**: Never — use PDF/TIFF/PNG
3. ❌ **Red-green colors**: ~8% of males are colorblind
4. ❌ **Low resolution**: <300 DPI for images
5. ❌ **Missing units**: Every axis must have labeled units
6. ❌ **3D effects**: Distort perception — avoid completely
7. ❌ **Chart junk**: Remove unnecessary gridlines, shadows
8. ❌ **Truncated axes**: Start bar charts at zero
9. ❌ **No error bars**: Always show uncertainty
10. ❌ **Jet/rainbow colormaps**: Use viridis, plasma, cividis

---

## Resources

### Scripts (`scripts/`)
- **`figure_export.py`**: Export utilities — `save_publication_figure()`, `save_for_journal()`, `check_figure_size()`
- **`style_presets.py`**: Pre-configured styles — `apply_publication_style()`, `configure_for_journal()`

### Assets (`assets/`)
- **`color_palettes.py`**: Importable color constants — Okabe-Ito, Paul Tol palettes, `apply_palette()`
- **`publication.mplstyle`**: General publication-quality matplotlib style
- **`nature.mplstyle`**: Nature journal-specific matplotlib style

### References (`references/`)
- **`publication_guidelines.md`**: Comprehensive best practices and checklist
- **`color_palettes.md`**: Full colorblind-safe palette reference with Python examples
- **`journal_requirements.md`**: Journal-specific dimensions, formats, DPI requirements
- **`matplotlib_examples.md`**: Complete working examples for all plot types

---

## Checklist

Before submitting figures, verify:

- [ ] Resolution meets journal requirements (300+ DPI)
- [ ] File format is correct (vector for plots, TIFF for images)
- [ ] Figure size matches journal column width
- [ ] All text readable at final size (≥6 pt)
- [ ] Colors are colorblind-friendly
- [ ] Figure works in grayscale
- [ ] All axes labeled with units
- [ ] Error bars present with definition in caption
- [ ] Panel labels present and consistent
- [ ] No chart junk or 3D effects
- [ ] Fonts consistent across all figures
- [ ] Statistical significance clearly marked
