---
name: academic-writing-style
description: |-
  Three-phase academic writing workflow: Tai writes → AI drafts → Agent supports.
  Sentence-level clarity principles, IMRaD section structure, citation conventions,
  thesis chapter organization, and flow guidance. Use when the user says "write this
  section", "draft paragraph", "polish text", "check citations", "review writing",
  "help with paper", "thesis writing", or any academic writing task.
---

# Academic Writing Style

Three-phase academic writing: **Tai writes → AI drafts → Agent supports**.

This skill combines the writer's raw thoughts with AI-expanded prose and structured
review. It governs all academic writing across every workspace.

---

## Three-Phase Workflow

### Phase 1 — Tai Writes

Tai provides raw thoughts, observations, and data. **No citations needed at this stage.**

Focus is on getting content down:
- Key observations and results
- Interpretation and connections
- Data points, figures, trends
- Experimental details

**You**: Read, understand the section type, load the relevant `mission/` module.
Do not edit. Do not add citations. Just absorb.

### Phase 2 — AI Drafts

The agent takes Tai's skeleton and expands it into **flowing prose**. Two-stage process:

**Stage 1 — Outline with key points:**
Take Tai's raw content and organize it into a structured outline with the correct
IMRaD template from `references/templates.md`. Use `references/imrad_structure.md`
for section-specific guidance.

**Stage 2 — Convert to full paragraphs:**
Transform the outline into flowing prose:
- Every bullet point → complete sentence
- Add transitions (however, moreover, in contrast)
- Integrate citations naturally where sources are known
- Vary sentence structure for readability
- NEVER leave bullet points in the final output

**Same golden rule: Preserve Tai's voice.** Don't change meaning or add claims
not supported by Tai's input. Use the section-specific mission modules for guidance:
`mission/introduction.md`, `mission/methods.md`, `mission/results.md`, etc.

### Phase 3 — Agent Supports

Three-step review:

1. **Structural review** — Does it follow the correct template? IMRaD rhythm?
   Check `references/templates.md` and `references/checklist.md`.

2. **Prose review** — Clarity, conciseness, weasel words, AI-tell detection.
   Use `mission/principles.md` for sentence-level rules.

3. **Citation & quality gate**:
   - Insert markdown citations where sources are available
   - Flag missing sources clearly (`[CITATION NEEDED]`)
   - Verify against `references/reporting_guidelines.md` if applicable
   - Check figures/tables against `references/figures_tables.md`
   - Present issues to Tai with suggested fixes — never silently fix

Tai approves final version → write permanent file.

---

## Sub-Skill Modules (`mission/`)

| Module | When to Load |
|--------|-------------|
| `mission/principles.md` | Sentence-level prose: clarity, conciseness, active/passive |
| `mission/introduction.md` | Drafting/reviewing Introduction (funnel, gap, contribution) |
| `mission/methods.md` | Drafting/reviewing Methods (recipe, instrumentation) |
| `mission/results.md` | Drafting/reviewing Results (data-first, figure/text) |
| `mission/discussion.md` | Drafting/reviewing Discussion (interpret, compare, contextualize) |
| `mission/abstract.md` | Drafting/reviewing Abstract (structured/paragraph) |
| `mission/conclusion.md` | Drafting/reviewing Conclusion (capstone, synthesis) |
| `mission/limitations.md` | Placing/reviewing limitations |
| `mission/citations.md` | Citation style, wiki pipeline |
| `mission/review-workflow.md` | Phase 3 details |

---

## References

| File | Purpose |
|------|---------|
| `references/templates.md` | IMRaD, extended paper, thesis, review templates |
| `references/checklist.md` | Final review checklist |
| `references/imrad_structure.md` | Detailed IMRaD section content guidance |
| `references/citation_styles.md` | APA/AMA/Vancouver/Chicago/IEEE citation formats |
| `references/figures_tables.md` | Effective data visualization best practices |
| `references/reporting_guidelines.md` | CONSORT/STROBE/PRISMA/STARD checklists |
| `references/writing_principles.md` | Clarity, conciseness, accuracy, objectivity |

---

## Core Rules

1. **Tai writes → AI drafts → Agent supports.** Never generate claims autonomously.
   Phase 1 is all Tai. Phase 2 is expanding from Tai's skeleton. Phase 3 reviews.
2. **Preserve Tai's voice.** Match tone, vocabulary, style. Flag issues, don't silently fix.
3. **Never fabricate citations.** Use `[CITATION NEEDED]` markers for gaps.
4. **Flag, don't silently fix.** Present issues with suggested fixes, let Tai decide.

---

## LaTeX Professional Reports

For research reports, white papers, and technical documents (not journal manuscripts):
- Use `assets/scientific_report.sty` — LaTeX style package with Helvetica fonts,
  colored box environments (keyfindings, methodology, recommendations, limitations),
  professional table formatting, and scientific notation commands
- Use `assets/scientific_report_template.tex` as a starting template
- Compile with XeLaTeX or LuaLaTeX
- See `assets/REPORT_FORMATTING_GUIDE.md` for full usage

For journal manuscripts, use the appropriate journal template instead.

---

## Scripts

| Script | Purpose |
|--------|---------|
| `scripts/generate_schematic.py` | Generate scientific schematics and diagrams |
| `scripts/generate_schematic_ai.py` | AI-assisted schematic generation |
| `scripts/generate_image.py` | Generate publication-quality images |
