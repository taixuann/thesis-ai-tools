# AI-Assisted Research Tools — Internship Thesis

This repository documents the AI agent system and analysis scripts used during the preparation of the internship thesis:

> **Fabrication and Characterization of PDA-based Crossbar Devices**
> Nguyen Xuan Tai — University of Science and Technology of Hanoi, July 2026

## Structure

```
ai-use/
├── agents/                 # OpenCode agent definitions
│   ├── academic.md         # Orchestrator — routes tasks to sub-agents
│   ├── writer.md           # Constrained prose generation with strict boundaries
│   ├── researcher.md       # RAG-based citation verification and literature search
│   ├── review.md           # Quality assurance and linting
│   └── experimenter.md     # Data fitting, modeling, and plotting
├── skills/                 # OpenCode skill libraries
│   ├── academic-writing-style/  # Writing workflow (Tai writes → AI drafts → Agent supports)
│   ├── citation-management/     # BibTeX, DOI conversion, reference verification
│   ├── publication-plotting/    # Nature/ACS styling, colorblind-safe palettes
│   ├── wiki/                    # Knowledge graph and literature vault management
│   └── wiki-rag-workflow/       # Hybrid RAG engine (BM25 + vectors + knowledge graph)
└── scripts/                # AI-assisted data analysis scripts
    ├── raman/              # Raman spectral deconvolution and ITO subtraction
    ├── xps/                # XPS peak fitting and overlay visualization
    ├── conductance/        # Quantum conductance analysis from pulse data
    ├── cdf/                # Weibull statistics and Vset variability analysis
    └── iv-endurance/       # DC sweep endurance plotting and conduction mechanism
```

## Agent Framework

The system runs on **OpenCode** (opencode-go), a CLI-based agent framework. Each agent has a specific role:

| Agent | Role | Model |
|-------|------|-------|
| **academic** | Task routing, orchestration, review | DeepSeek-v4-Flash |
| **writer** | Constrained prose under strict boundary rules | DeepSeek-v4-Flash |
| **researcher** | RAG queries, citation verification, paper ingestion | DeepSeek-v4-Flash |
| **experimenter** | Data analysis, fitting, plotting | DeepSeek-v4-Flash |
| **review** | Quality checks, linting, verification | DeepSeek-v4-Flash |

### Writing Constraints

The writer agent operated under strict boundary rules:
- No em-dashes or explanatory colons
- No booster adjectives or fluff phrases
- Every sentence required quantitative anchoring
- One paragraph per approval cycle
- Self-scan for banned phrases before output

## Skills

Skills are loaded on-demand by agents for specific tasks. Key skills:
- **wiki-rag-workflow**: Triple retrieval (BM25 + vectors + knowledge graph) with enforced citation
- **academic-writing-style**: IMRaD structure, sentence-level clarity, citation conventions
- **publication-plotting**: Publication-ready figures with journal-standard styling

## Data Analysis Scripts

Scripts were AI-assisted and verified by the author:

| Script | Purpose |
|--------|---------|
| `raman/plot_deconvolution_zoom.py` | Raman band deconvolution with Lorentzian fitting |
| `raman/plot_ito_subtraction.py` | ITO background subtraction for thin-film Raman |
| `xps/plot_xps_overlay.py` | 3-panel XPS overlay (C 1s, O 1s, N 1s) |
| `xps/export_xps_csv.py` | CasaXPS data export to CSV |
| `conductance/plot_conductance.py` | G = I/V in G₀ units from pulse transients |
| `conductance/plot_ppf_conductance.py` | PPF conductance evolution over 50 pulses |
| `cdf/plot_final_cdf.py` | Weibull cumulative probability of Vset |
| `iv-endurance/plot_overlay_c1_200_500.py` | 500-cycle DC endurance overlay |

## License

This repository documents the methodology for academic transparency. Scripts are provided as-is for reproducibility.
