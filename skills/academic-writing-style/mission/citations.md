# Citations — Style and Pipeline

Load this module when adding citations or reviewing reference lists.

## In-Text Format

**Author-year** format (primary convention):

```
Single author:   (Smith, 2020)
Two authors:     (Smith and Jones, 2020)
Three+ authors:  (Smith et al., 2020)
```

**Placement**:
- After the claim, before the period: "The forming voltage decreases with nitrogen doping (Kim et al., 2021)."
- Multiple sources: "(Smith, 2020; Jones et al., 2021; Lee and Park, 2022)" — ordered chronologically
- Author in sentence: "Kim et al. (2021) demonstrated that..."

## When to Cite What

| Claim Type | Cite |
|-----------|-------|
| Broad field context, well-established facts | Reviews |
| Specific experimental findings, data | Original research |
| Standard methods | Methods papers or reviews |
| Novel method modifications | Your own prior work |
| Theoretical frameworks | Original theory papers |
| Contradictions or debates | Both sides |

**Rule**: Never cite a paper you haven't read. Never rely on a review's summary without checking the original if central to your argument.

## Citation Pipeline (with Wiki Skills)

The full citation workflow uses wiki literature skills:

1. **Draft phase** — Tai writes without citations (raw thoughts)
2. **Review phase** — Agent reviews + inserts citations using wiki skills:
   - Load `skill(name="writing-research-guide")` from `wiki/.opencode/skills/writing-research-guide/` for Zettelkasten citation workflow
   - Load `skill(name="summary-writer")` for source extraction
   - Use the paper-search MCP tools (`search_papers`, `search_arxiv`) or the wiki-research-workflow skill for paper/DOI lookups if needed
3. **Verification phase** — Cross-reference citations against wiki sources
4. **Permanent phase** — Finalize with complete, consistent bibliography

## Reference List Formatting

- Every entry must have: authors, title, year, journal, volume, pages, DOI
- Author names consistent format across all entries
- Venue names consistent
- Title capitalization: protect proper nouns/acronyms with braces (`{HfO₂}`)
- No "to appear" / "forthcoming" markers in final output
