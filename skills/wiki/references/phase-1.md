---
description: Phase 1 — Discovery & Staging Workflow
---

# 🔬 Phase 1: Discovery & Staging

This phase establishes the structural container for deep research, designs the Socratic strategy, and compiles the initial reference staging catalog. Literature discovery is executed through a dual loop: the AI searches via local tools, and the human runs Gemini Deep Research, downloading synthesized reports directly to the cluster.

---

## 📋 Step-by-Step Checklist & Commands

### 1. Scaffold Cluster Container
Create the self-contained Grounded Research Cluster structure inside `wiki/references/` (e.g. `cluster_pda_conduction`):
```bash
mkdir -p wiki/references/cluster_{cluster_slug}/{sources,artifacts}
touch wiki/references/cluster_{cluster_slug}/cluster.json
touch wiki/references/cluster_{cluster_slug}/local-context.md
touch wiki/references/cluster_{cluster_slug}/search-queries.md
```

### 2. Configure Metadata (`cluster.json`)
*   **Action**: Populate `cluster.json` with target composition objectives, notebook IDs, and strategic PhD linkages.

### 3. Setup Context Routing
*   **Action**: In the cluster's root `local-context.md` file, write a central router map linking to shared contexts:
    ```markdown
    # Local Context Router
    This file aggregates local experimental variables and long-term PhD goals to ground all literature discovery.
    - Lab Experimental Variables: [pda_lab_context.md](file:///Users/tai/workspace/wiki/references/_shared/pda_lab_context.md)
    - Neuromorphic Linkages: [neuromorphic_phd_goals.md](file:///Users/tai/workspace/wiki/references/_shared/neuromorphic_phd_goals.md)
    ```

### 4. Formulate Socratic Probing Queries
*   **Action**: Under `search-queries.md`, write **3+ highly specific nano, atomic, or molecular scale probing questions** (interfacial transfer, carrier transport kinetics, etc.) along with target formatting parameters and prompts.

### 5. Execute Dual Literature Discovery
*   **AI Discovery**: Run literature search tools (arXiv, OpenAlex, EuropePMC) to find candidate papers and populate:
    `wiki/references/cluster_{cluster_slug}/artifacts/list-references-staging.md`
    *(Mandatory: Ensure the candidate list always includes comprehensive foundational reviews or tutorial-style papers for each mechanism or principle to establish basic understanding before moving to narrow research studies).*
*   **Human Deep Research**: Copy the context from `local-context.md` and queries/prompts from `search-queries.md` to run in Gemini Deep Research (typing "implement" for rapid execution). Download the resulting reports/documents directly into:
    `wiki/references/cluster_{cluster_slug}/artifacts/`

### 6. Source-by-Source Discussion & Purpose Assignment
*   **Action**: Proactively discuss each candidate source and Deep Research report with the human:
    *   Assess research relevance, data quality, and reliability.
    *   Determine the exact purpose/section of the thesis it belongs in (e.g., CV kinetics, SCLC fitting, etc.).
    *   Record these approved sources and their assigned roles in `cluster.json` or the reference logs.

### 7. Zotero Curation & Local Ingestion
*   **Action**: Save the selected approved papers into the designated Zotero collection and trigger the local Zotero ingester script on the keys:
    ```bash
    python3 /Users/tai/.gemini/skills/wiki/scripts/ingest_paper.py --key [ITEM_KEY] --cluster [CLUSTER_SLUG]
    ```

---

## 🧠 Context & Re-remembering Snippet (Memory Anchor)

*Copy the block below and paste it into the active dialogue or memory log at the start of this phase to guide the AI:*

```yaml
phase: 1_discovery_and_staging
active_cluster: cluster_{cluster_slug}
objectives:
  - Scaffold folder structure
  - Configure cluster.json metadata
  - Generate Socratic search queries and format prompts
  - Run dual AI/human search and populate artifacts/ folder
search_query_document: [pending | completed]
candidates_listed: [0 | number of papers in list-references-staging.md]
deep_research_reports: [list of files downloaded to artifacts/]
next_phase: phase_2_writing_loop
```
