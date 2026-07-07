---
description: Phase 2 — Zettelkasten Writing Loop Workflow
---

# ✍️ Phase 2: Zettelkasten Writing Loop

This phase refines raw thoughts into structured, literature-grounded knowledge. The human drafts raw notes inside `artifacts/`, the `wiki-writer` structures and polishes them, and the `wiki-librarian` performs rigorous claim verification against sources and Deep Research reports before checking schema compliance.

---

## 📋 Step-by-Step Checklist & Commands

### 1. Create Skeleton Draft Templates (Temp Files)
*   **Action**: The agent (Antigravity/Writer) creates temporary section outlines/skeleton files in:
    `wiki/references/cluster_{cluster_slug}/artifacts/draft_{section_slug}.md`
*   **Structure**: Include layout prompts, experimental checklists, and a list of approved sources mapped to this section's goals.

### 2. Human Raw Drafting (CITATION-FREE)
*   **Action**: The human writes raw scientific thoughts, observations, and experimental descriptions directly inside the draft skeleton file. 
*   **Rule**: Omit citations entirely during this step to maintain natural flow and focus on raw content.

### 3. Writer Sentence Structuring & Coherence Polish
*   **Action**: The `wiki-writer` reviews the raw draft and polishes it:
    *   Enhances sentence flow, transitions, and clarity.
    *   Ensures the human's authentic voice is preserved (no autonomous walls-of-text or expansions).
    *   Keeps the text citation-free at this stage.

### 4. Librarian Claims Matching & Citation Insertion
*   **Action**: The `wiki-librarian` reviews the polished draft:
    *   Compares the text against the cluster's approved sources, reports, and PDFs.
    *   Matches scientific assertions to literature evidence and automatically inserts inline citations: `^[source-basename.md:line_range]`.
    *   Spots logical contradictions, gaps, or physical fitting errors (e.g. SCLC/Schottky diagnostics) and flags them with Socratic critique.

### 5. Compile Refined Literature Note
*   **Action**: The human reviews the Librarian's suggestions and generates a refined, cited note:
    `wiki/references/cluster_{cluster_slug}/artifacts/literature_note.md`

### 6. Finalize Permanent Note (`permanent_note.md`)
*   **Action**: Undergo a final polish to produce the consolidated:
    `wiki/references/cluster_{cluster_slug}/artifacts/permanent_note.md`
*   **Action**: The `wiki-librarian` performs the final quality gate to guarantee:
    *   100% of claims are traceably grounded in sources/reports (no training memory assumptions).
    *   The page fits the YAML frontmatter and tag ontology defined in [SCHEMA.md](file:///Users/tai/workspace/wiki/SCHEMA.md).

---

## 🧠 Context & Re-remembering Snippet (Memory Anchor)

*Copy the block below and paste it into the active dialogue or memory log at the start of this phase to guide the AI:*

```yaml
phase: 2_zettelkasten_writing_loop
active_cluster: cluster_{cluster_slug}
objectives:
  - Draft raw thoughts under artifacts/draft_note.md
  - Run Writer formatting and logical flow cycles
  - Run Librarian claims validation and contradictions checks
  - Compile literature_note.md and permanent_note.md
draft_status: [draft | literature | permanent]
provenance_citations_verified: [yes | no]
librarian_gate_status: [pending | approved]
next_phase: phase_3_wiki_integration
```
