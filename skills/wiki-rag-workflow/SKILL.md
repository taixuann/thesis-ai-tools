# Skill: wiki-rag-workflow

Hybrid RAG query engine for the materials science wiki. Uses triple retrieval (BM25 + dense vectors + knowledge graph) with reciprocal rank fusion and citation enforcement.

## Architecture

```
Query → Agent Router
           │
    ┌──────┼──────┐
  BM25  Vector  Graph
  (exact) (semantic) (relationships)
    │      │      │
    └──────┴──────┘
           │
      RRF Fusion
           │
    Top-K Sources (with chunk IDs)
           │
    Answer Generation (LLM + enforced citations)
```

## How to Query

```bash
# From wiki root:
python3 .rag/query.py 'your question here'

# For programmatic use:
python3 .rag/query.py --json 'your question here'
```

The system classifies queries into two types:
- **simple** (facts, definitions): BM25 + Vector only, fast
- **complex** (relationships, comparisons): BM25 + Vector + Graph traversal, deeper

## Index Structure (`.rag/`)

| File | Purpose |
|------|---------|
| `index.json` | Document summaries with metadata tags |
| `chunks.json` | 3,252 hierarchical chunks (parent-child by markdown headings) |
| `vectors.npy` | 384-dim dense embeddings (all-MiniLM-L6-v2) |
| `bm25.pkl` | BM25 sparse keyword index |
| `graph.json` | Knowledge graph: 251 nodes, 970 edges (entities + wikilinks) |
| `retrieval_meta.json` | Index metadata |

## Citation System

Every chunk has a stable ID: `citekey#section#chunk_N`
Examples:
- `redox-switching#competing-mechanisms#chunk_53`
- `pda#introduction#chunk_1`

The query engine outputs a **Citation Map** — a structured mapping of sources to chunk IDs, enabling:
1. Every answer claim traces to a specific chunk
2. Researcher agent uses these IDs for inline citations
3. No hallucinated sources (only chunks in the index are referenceable)

## When to Load

Load this skill when:
- User says "rag: [question]" or "query: [question]"
- User asks about the wiki's literature or sources
- You need to find relationships between papers or concepts
- You need citation-backed answers from the wiki corpus

## Workflow

1. **Load skill** → `skill(name="wiki-rag-workflow")`
2. **Query RAG** → `python3 .rag/query.py 'your question'` (reads output)
3. **Read sources** → Use Citation Map to read specific source files for more detail
4. **Generate answer** → Use retrieved chunks + citations to formulate response
5. **Cite everything** → Every claim must reference its chunk ID
