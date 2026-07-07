# Review Workflow — Draft → Review → Permanent

Load this module when the user asks you to review or polish a draft.

## Three-Phase Workflow

### Phase 1: Draft (Tai writes)
Tai writes raw thoughts, observations, data — citation-free. The agent does NOT write content.

**Agent role**: Read Tai's draft, understand the structure, identify what kind of section it is (Introduction, Methods, Results, Discussion etc.) and load the relevant mission/ module. Prepare the review checklist.

### Phase 2: Review with Citations
Agent reviews the draft against the writing principles and inserts citations.

1. **Structural review**: Does it follow the correct section template? GPS rhythm? Funnel structure?
2. **Prose review**: Clarity, conciseness, active/passive, weasel words, AI-tell detection
3. **Citation insertion**: 
   - Load relevant wiki writing skill (e.g., `write-intro` for Introduction)
   - Use the paper-search MCP tools (`search_papers`, `search_arxiv`) or the wiki-research-workflow skill to verify DOI/paper lookups if needed
   - Insert markdown citations: `(Author et al., 2020)`
   - Flag missing citations: "This claim needs a source — X, Y, or Z could support it"
4. **Flag issues, don't fix silently**: Present issues to Tai with suggested fixes

### Phase 3: Permanent File
After Tai approves the review:

1. Apply approved fixes
2. Final citation verification (every claim grounded, every reference complete)
3. Format final document per project or general template
4. Write to the target file location

## Review Checklist

**Structure & Narrative**:
- [ ] Does every section follow GPS (Goal → Problem → Solution)?
- [ ] Are paragraphs chained with transitions?
- [ ] Do section intros match what subsections deliver?
- [ ] Does every paragraph end with a closer?
- [ ] Can the nugget be stated in one sentence?

**Prose & Style**:
- [ ] No filler phrases
- [ ] No "not X, but Y" negation-contrast structures
- [ ] No AI-tell words or patterns
- [ ] Calibrated confidence: assertive for facts, hedged for mechanisms
- [ ] One idea per sentence

**Figures & Tables**:
- [ ] Every float cross-referenced and discussed
- [ ] Captions self-sufficient
- [ ] Figure-text-caption consistency verified

**Citations & Bibliography**:
- [ ] Every claim traced to a source
- [ ] All named methods cited at first use per section
- [ ] Bibliography entries complete and consistent
