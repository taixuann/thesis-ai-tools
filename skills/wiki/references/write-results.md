---
description: Global Results & Discussion Playbook
---

# 📊 /write-results: Results & Discussion Playbook

This workflow guides the creation of the Results & Discussion section. It enforces the academic standard of separating **objective data observations** from **theoretical mechanism modeling and fitting**, while ensuring direct comparison to literature benchmarks.

---

## 📋 Academic Layout Structure

1. **Morphological, Structural, or Physical Characterization:**
   - Sizing, film thickness, spectroscopy peaks (Raman, XRD, XPS), and morphology.
   - Assignment of peaks/features to specific physical or chemical configurations.
2. **Functional/Operational Performance:**
   - Primary operational data (I-V sweeps, kinetics, output metrics, stability, efficiency).
   - Quantitative extraction of key metrics (switching fields, ON/OFF ratios, retention).
3. **Physical Modeling & Parameter Extraction:**
   - Fitting raw data to theoretical models (e.g., SCLC slopes, Poole-Frenkel or Schottky emission, activation energy plots).
   - Extracted physical parameters (permittivity, barrier heights, trap levels) along with fitting goodness-of-fit metrics ($R^2$, error bars).
4. **Discussion & Literature Benchmarking:**
   - Comparison of extracted parameters with published values.
   - Mapping contested dimensions, anomalies, and structural discrepancies.

---

## 🔬 Data-Gathering Questionnaire

Copy the questionnaire below, fill it in with raw details, and paste it into the chat to begin drafting:

```markdown
### Results & Discussion Data Gathering
- **Structural Observations:** [e.g., 30 nm film thickness, Raman peak at 1380 cm^-1 for catechols]
- **Operational Performance Data:** [e.g., volatile threshold switching, 0.4V threshold voltage, 10^3 ON/OFF]
- **Physical Models for Fitting:** [e.g., SCLC in low-field, Poole-Frenkel at high-field]
- **Extracted Fitting Parameters:** [e.g., low-field log-log slope ~1.1, extracted dielectric constant epsilon_r = 2.8]
- **Goodness of Fit Metrics:** [e.g., R^2 = 0.992 for PF fitting]
- **Literature Benchmarks & Comparisons:** [e.g., operating voltage 0.4V is lower than the typical 1.0V reported by Author et al.]
- **Key Discrepancies / Anomalies:** [e.g., high cycle-to-cycle variability due to random proton distribution]
```

---

## ✍️ Execution Steps

1. **Data vs. Interpretation Audit:** The AI verifies that raw observations are reported first, and fittings/interpretations are clearly demarcated.
2. **Model Validation:** The AI checks that extracted physical parameters (e.g., dielectric constants, barrier heights) are physically realistic.
3. **Benchmark Check:** The AI ensures that comparison tables or text map directly to approved reference sources.
