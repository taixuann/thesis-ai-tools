---
name: wiki
description: >-
  Use when you need to manage the knowledge wiki: synthesize information from
  multiple sources into structured wiki pages, manage bibliographic references
  (BibTeX), maintain the wiki ontology and structure, or process NotebookLM
  artifacts into the wiki vault.
---

# Wiki — Knowledge Curation

Comprehensive wiki management for the thesis knowledge base: ingest, synthesize, reference, and structure knowledge about pH-modulated polydopamine memristors and related topics.

## Core Principles

1. **Structure first** — Every piece of knowledge has a place in the wiki hierarchy.
2. **Traceability** — Every claim traces back to a source (paper, experiment, note).
3. **Interlinking** — No page is an island. Every page links to at least 2 others.
4. **Curated growth** — Quality over quantity. Better a small clean wiki than a large messy one.

---

## 1. Knowledge Synthesis

Synthesize information from multiple sources into structured, interlinked wiki pages.

### Phase 1: Gather
Collect all relevant sources — papers with extracted metadata, data analysis results, existing wiki pages, user notes.

### Phase 2: Identify Connections
Map relationships: Which entities appear in multiple sources? Which mechanisms connect to phenomena? What contradictions or gaps exist?

### Phase 3: Structure

#### Wiki page template
```markdown
---
title: Concept Name
created: YYYY-MM-DD
updated: YYYY-MM-DD
type: concept | mechanism | entity | method
tags: [tag1, tag2]
sources: [path/to/source]
confidence: high | medium | low
relations:
  is_a: parent-concept
  part_of: broader-topic
  related_to: [related-concept-1, related-concept-2]
---

## Overview
<One-paragraph definition>

## Key Properties / Characteristics
<Bulleted or table format>

## Relationship to Other Concepts
- Link to [[related-concept-1]]: <description>

## Evidence
<What the sources say, with citations>

## Open Questions
<What's still unknown or debated>

## References
<Full citations>
```

### Wiki directory structure
```
wiki/
├── SCHEMA.md              # Master schema: conventions, taxonomy, rules
├── index.md               # Content catalog (auto-synced)
├── log.md                 # Chronological action log
├── raw/                   # Immutable source materials
├── concepts/              # Conceptual knowledge
├── mechanisms/            # Physical/chemical mechanisms
├── applications/          # Application domains
├── entities/              # People, organizations, materials
├── methods/               # Experimental and computational methods
├── comparisons/           # Side-by-side analyses
├── queries/               # Filed query results
├── references/            # Bibliographic references
├── .rag/                  # Local RAG indexes and database files (LightRAG/GraphRAG)
└── _archive/              # Superseded content
```

---

## 2. Reference Curation

Manage the wiki's bibliographic reference database: BibTeX entries, deduplication, metadata updates.

### Storage
```
wiki/references/
├── index.md              # Master list of all references with keys
├── <citekey>.bib         # One BibTeX file per reference
└── clusters/
    └── <cluster-slug>/   # Thematic groups of references
        ├── index.md
        └── ...
```

### Adding a new reference
1. Check for duplicates by author+year or DOI
2. Create BibTeX file with DOI, URL, author, year, journal
3. Add entry to `references/index.md`
4. Link to wiki pages that cite it

### BibTeX template
```bib
@article{AuthorYearKey,
  title     = {Full Title},
  author    = {Author1 and Author2},
  year      = {YYYY},
  journal   = {Journal Name},
  doi       = {10.xxxx/xxxxx},
  url       = {https://doi.org/xxxx}
}
```

### Auditing
Periodically check: DOI validity, retraction status, citation count changes, duplicate entries.

---

## 3. Ontology Management

Manage the wiki's knowledge structure — taxonomy, concept hierarchy, entity relationships.

### Wiki page types
| Type | Purpose | Located in |
|------|---------|-----------|
| `concept` | Abstract ideas, phenomena | `concepts/` |
| `mechanism` | Physical/chemical mechanisms | `mechanisms/` |
| `entity` | People, materials, organizations | `entities/` |
| `method` | Experimental/computational methods | `methods/` |
| `application` | Application domains | `applications/` |

### Relationship types
| Relationship | Example |
|-------------|---------|
| is_a | memristor is_a device |
| part_of | filament is_part_of switching mechanism |
| causes | voltage causes conductance change |
| measured_by | conductance measured_by electrical characterization |
| related_to | neuromorphic_computing related_to memristor |

### Structural audits
- Directory balance — are all subdirectories being used?
- Concept coverage — orphan tags with only 1 page?
- Link density — average ≥ 2 outbound links per page
- Navigation — index.md → any page in ≤ 3 clicks
- Schema adherence — pages follow SCHEMA.md conventions

---

## 4. Local Zotero & Docling Ingestion Pipeline

Automate local ingestion of literature directly from Zotero using SQLite note extraction, docling, tag mapping, and linter checks.

### Script Location
```bash
/Users/tai/.gemini/skills/wiki/scripts/ingest_paper.py
```

### Ingestion Command
Run the script passing the Zotero item key and an optional cluster slug to symlink to:
```bash
python3 /Users/tai/.gemini/skills/wiki/scripts/ingest_paper.py --key [ITEM_KEY] [--cluster [CLUSTER_SLUG]]
```

### Ingestion Flow
1. **Find Metadata**: Loads cached paper metadata from `~/.cache/zotero-tui/papers.json` using the Item Key.
2. **Retrieve Beaver Note**: Copies `zotero.sqlite` temporarily to bypass active database locks and retrieves the attached Beaver note HTML content.
3. **Parse Note**: Converts the note HTML to clean Markdown (retaining summary, findings, fabrication, and parameter tables).
4. **Copy Raw PDF**: Locates the paper's PDF inside Zotero storage `~/Zotero/storage/[ITEM_KEY]/` and copies it to `wiki/raw/pdfs/[citekey].pdf`.
5. **Parse PDF**: Converts the PDF to Markdown using `docling` and saves it to `wiki/raw/markdown/[citekey].md` for raw text indexing and future Q&A.
6. **Tag Mapping**: Extracts local item tags (including Zotero Beaver `#` tags) from the SQLite database and maps them to clean ontology/local namespace tags.
7. **Candidate Source Page**: Creates the source candidate page at `wiki/candidates/sources/[citekey].md` combining the mapped frontmatter metadata and the parsed markdown note content.
8. **Cluster Symlinking**: Creates a relative symbolic link from `wiki/references/cluster_[cluster_slug]/sources/[citekey].md` pointing to `../../../sources/[citekey].md`.
9. **Zotero Status Update**: Updates the paper's pipeline status to `wiki-ingested` and syncs tags.
10. **Linter Check**: Runs the linter script `wiki-linter.py` to verify the page conforms to SCHEMA.md and rules.

---

## Common Pitfalls

- **Letting schema drift** — keep SCHEMA.md in sync with actual wiki content
- **Orphan pages** — every page must have ≥ 2 outbound links and be reachable from index.md
- **Duplicate references** — always check by DOI before adding a new reference
- **Ad-hoc directories** — don't create directories outside the defined hierarchy
- **Missing frontmatter** — every wiki page needs type, tags, sources, and relations
- **Stale references** — periodically re-check DOIs and citation counts
- **Over-engineering** — keep the ontology simple until scale demands complexity
