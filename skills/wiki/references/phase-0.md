---
description: Phase 0 — Orientation, Mode Selection, and Graph Validation Workflow
---

# 🚦 Phase 0: Orientation & Setup

This phase is the mandatory entry point of any research session. Its goal is to align on the current workspace status, select the research mode, and run a compliance lint sweep across candidate and live wiki folders to ensure zero broken links, invalid tags, or citation boundaries before any edits are made.

---

## 📋 Step-by-Step Checklist & Commands

### 1. Read Master Catalogs
*   **Action**: Scan [index.md](file:///Users/tai/workspace/wiki/index.md) to locate existing concept, mechanism, application, entity, method, or source pages.
*   **Action**: Scan the last 10 entries of [log.md](file:///Users/tai/workspace/wiki/log.md) to review recent crystallization and promotion logs.
*   **Action**: Check the sister vault `workspace/wiki-literature/` for existing reference content.

### 2. Verify Graph Stability (Run Linter)
Always run the workspace linter first to guarantee index and citation stability. Propose this command before modifying anything:
```bash
python3 /Users/tai/.gemini/skills/wiki-linter/scripts/wiki-linter.py
```

### 3. Establish Mode Selection
Determine if this session is **LIGHT** or **DEEP**:
*   **LIGHT Mode**: Used when organizing, linking, or making minor updates to existing files. Proceed directly to **Phase 2 — Zettelkasten Writing Loop**.
*   **DEEP Mode**: Used when the topic is entirely new, highly contested, or requires deep literature discovery and Socratic characterization. Proceed to **Phase 1 — Discovery & Staging**.

---

## 🧠 Context & Re-remembering Snippet (Memory Anchor)

*Copy the block below and paste it into the active dialogue or memory log at the start of this phase to guide the AI:*

```yaml
phase: 0_orientation_and_setup
active_cluster: N/A (Session initialization)
objectives:
  - Verify active index and content log state
  - Audit recent changes and active session context
  - Validate the graph using wiki-linter
current_linter_status: [clean | issues_detected]
active_blockers: [None | list recent failures]
next_phase: [phase_2_writing_loop | phase_1_discovery]
```
