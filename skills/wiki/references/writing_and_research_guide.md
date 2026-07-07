# Materials Science Wiki: Writing & Research Guide (v3.0)

This guide serves as a persistent reference for writing, formulating queries, and structuring notes across the three phases of the research workflow. It provides Socratic frameworks, progressive summarization guidelines, and human-AI collaborative drafting templates.

---

## 🚦 Phase 0: Orientation & Graph Validation

### Linter Audit Checklist
Before modifying or creating any page, always run `python3 /Users/tai/.gemini/skills/wiki-linter/scripts/wiki-linter.py` to verify:
1.  **Bilateral Backlink Symmetry**: If a concept cites a source, the source index page MUST contain a double-bracket wikilink back to the concept.
2.  **Double-bracket Link Integrity**: All wikilinks `[[page-slug]]` must resolve to actual pages within the `wiki/` directory.
3.  **Strict Inline Citations**: Every scientific claim must terminate in an inline provenance citation of the form: `^[source-basename.md:line_range]` or `^[source-basename.md:page]`.
4.  **YAML Frontmatter Compliance**: Must contain title, tags, sources, last_updated, confidence, and contested dimensions mapped to valid ontology values.

---

## 🔬 Phase 1: Socratic Probing & Query Formulation

To extract precise physical parameters (e.g. PDA thickness, CV voltage sweeps, defect levels), write Socratic probing queries under `search-queries.md` targeting the six categories of questioning:
1.  **Nano/Atomic Scale Behavior**: E.g. "What atomic configuration does PDA adopt at the TiO2 interface, and how does it affect the charge transfer rate?"
2.  **Kinetics & Dynamic Interconversion**: E.g. "What is the proton transfer rate constant of electropolymerized PDA films during cyclic voltammetry sweeps at pH 7?"
3.  **Quantitative & Experimental Boundaries**: E.g. "What are the film thickness, threshold voltage, and ON/OFF ratio values reported in [source]?"
4.  **Assumptions & Ideological Frameworks**: E.g. "What physical model (e.g. Poole-Frenkel or Schottky) is assumed for the conduction fitting, and does it account for temperature-dependent currents?"
5.  **Contradictions & Outliers**: E.g. "Why does [source A] report volatile switching while [source B] reports non-volatile switching under the same bias range?"
6.  **Contextual Linking**: E.g. "How does the quinone-hydroquinone redox mechanism in PDA link to synaptic plasticity behaviors like STP and LTP?"

---

## ✍️ Phase 2: Zettelkasten Writing & Progressive Summarization

To distill raw text into permanent notes, follow this hierarchy of summarization:
1.  **Staging List**: Index raw sources and assign roles (`list-references-staging.md`).
2.  **Draft Note**: Capture raw takeaways, annotations, and initial thoughts.
3.  **Literature Note**: Refine the draft into structured key claims, physical parameters, and context links with line-range citations.
4.  **Permanent Note**: Synthesize multiple literature notes into a singular, highly cohesive permanent note (`permanent_note.md`) detailing the concepts, mechanisms, and applications ready for integration.

### Collaborative Drafting Guidelines
*   **Step 1: Raw Voice**: The human drafts the core structure and thesis link without citation noise.
*   **Step 2: Grammar & Flow**: The AI reviews the draft, correcting tone and removing banned expressions (e.g. "delve", "testament").
*   **Step 3: Librarian Ingestion**: The AI parses the cluster source markdowns, finds supporting lines, and inserts the precise citations (`^[source.md:L10-L15]`).

---

## 💎 Phase 3: Integration & Vault Sync

### Candidate Promotion and Symlinking
1.  **Crystallize Candidates**: Split the approved `permanent_note.md` into atomic Candidate files under `wiki/candidates/`.
2.  **Vault Preservation**: Save the master reference notes to `wiki/references/` and raw files under `wiki/raw/`.
3.  **Link Vault to Cluster**: Link the master vault note back to the cluster's local `sources/` folder:
    ```bash
    ln -s ../../[citekey].md wiki/references/cluster_[cluster_slug]/sources/[citekey].md
    ```
4.  **Promote and Rebuild**: Run the linter, move candidates to live folders, and update `index.md` / `log.md`.
5.  **Local Ingest**: Run the local Zotero ingester script on literature keys: `python3 /Users/tai/.gemini/skills/wiki/scripts/ingest_paper.py --key [ITEM_KEY] --cluster [CLUSTER_SLUG]`
