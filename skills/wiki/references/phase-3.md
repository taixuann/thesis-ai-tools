---
description: Phase 3 — Wiki Integration & References Workflow
---

# 💎 Phase 3: Wiki Integration & References

This phase is the final stage of deep research. The `wiki-ingester` moves the approved permanent notes from the cluster's `artifacts/` folder into candidate wiki pages, processes raw literature PDFs, and writes index pages. The `wiki-references` updates the bibliography, populates the `wiki-literature/` master reference vault, symlinks notes, and executes candidate promotion.

---

## 📋 Step-by-Step Checklist & Commands

### 1. Ingest Permanent Note and Sources (`wiki-ingester`)
*   **Action**: Split the approved `artifacts/permanent_note.md` into atomic candidate pages under `wiki/candidates/` according to page types (`concepts/`, `mechanisms/`, `applications/`, etc.).
*   **Action**: For any newly added literature sources, run the local Zotero ingester script:
    ```bash
    python3 /Users/tai/.gemini/skills/wiki/scripts/ingest_paper.py --key <ITEM_KEY> --cluster <cluster_slug>
    ```

### 2. Update bibliography and vaults (`wiki-references`)
*   **Action**: Update the master references registry and BibTeX database.
*   **Action**: Populate the `wiki/references/` vault with ontology-tagged reference markdown notes containing key parameters and summaries.
*   **Action**: Link the master reference note to the cluster's local `sources/` directory by creating a relative symbolic link:
    ```bash
    ln -s ../../<citekey>.md wiki/references/cluster_<cluster_slug>/sources/<citekey>.md
    ```

### 3. Verify Candidate Compliance (Run Linter)
Run the compliance linter to ensure perfect tags, bilateral link symmetry, citation boundaries, and formatting:
```bash
python3 /Users/tai/.gemini/skills/wiki-linter/scripts/wiki-linter.py
```
*   **Action**: Address all warnings and resolve all critical errors before promoting.

### 4. Promote Candidates to Live Wiki
Move candidate pages from the `candidates/` folder to their respective live directories:
```bash
mv wiki/candidates/concepts/*.md wiki/concepts/
mv wiki/candidates/mechanisms/*.md wiki/mechanisms/
mv wiki/candidates/applications/*.md wiki/applications/
mv wiki/candidates/entities/*.md wiki/entities/
mv wiki/candidates/methods/*.md wiki/methods/
mv wiki/candidates/sources/*.md wiki/sources/
```

### 5. Navigation & Log Alignment
*   **Action**: Update the master catalog index at [index.md](file:///Users/tai/workspace/wiki/index.md) and append a detailed entry to [log.md](file:///Users/tai/workspace/wiki/log.md).
*   **Action**: Run `python3 /Users/tai/.gemini/skills/wiki-linter/scripts/wiki-linter.py` one final time to verify vault health.

---

## 🧠 Context & Re-remembering Snippet (Memory Anchor)

*Copy the block below and paste it into the active dialogue or memory log at the start of this phase to guide the AI:*

```yaml
phase: 3_wiki_integration_and_references
active_cluster: cluster_{cluster_slug}
objectives:
  - Ingest permanent notes and run Docling on new sources
  - Update BibTeX, populate wiki-literature/ vault, and symlink sources
  - Verify candidates with wiki-linter
  - Promote candidates to live directories
  - Rebuild index.md and update log.md
candidates_generated: [list of files split into candidates/]
sources_symlinked: [list of symlinks created under sources/]
linter_validation: [clean | issues_to_resolve]
promoted_files: [list of files moved to live directories]
index_and_log_updated: [yes | no]
```
