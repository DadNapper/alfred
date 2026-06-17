---
name: scraplands-cursor-handoff
description: >-
  Writes Cursor implementation prompts for Scraplands. Use when handing off code
  changes, debugging with repo access, commits, or Studio MCP investigation to
  Cursor.
---

# Scraplands → Cursor Handoff

Hermes plans; Cursor implements. Full spec: repo `ai/workflows/cursor_prompt_mode.md`.

## Model routing

Drafting long Cursor handoff prompts (P0 task files, multi-file context packs) can be **`delegate_task`**'d to a subagent on OpenRouter `qwen/qwen3-coder`. The main GPT-5.5 agent reviews scope, risk, and final wording before Oz sends to Cursor. See `scraplands-hermes/references/model_routing.md`.

## Before handoff — confirm

- [ ] Actually a **code task** (not Studio-only property/layout work)?
- [ ] Right `Readmes/*.md` named for the feature area?
- [ ] Streaming / mobile / save-risk called out if applicable?
- [ ] Scope bounded (files, explicit non-goals)?
- [ ] Model tier appropriate (premium for persistence, remotes, economy)?
- [ ] Oz should Studio-test before commit?

Do **not** send vague prompts on high-risk systems (DataService, rebirth, remotes, automation).

## Context pack (attach only what's needed)

**Often include:**
- `@AGENTS.md`, `ai/workflows/cursor_implementation.md`
- Relevant `ai/engineering/*.md` for files being edited
- Relevant `Readmes/` feature doc(s)
- `ai/active/current_priorities.md` if touching active focus

**When relevant:**
- `ai/memory/decisions.md`, `ai/memory/systems_reference.md`
- Specific script paths
- Feedback row summary (not full CSV)
- `Readmes/ux/carry_item_interaction_routing.md` before carry/placement edits

**Do not attach blindly:** whole directories, unrelated READMEs, full PlayerFeedback.csv.

## P0 Bug Task Files

When player feedback or triage produces multiple P0 fixes, create one active markdown task per root-cause class under:

```text
ai/tasks/active/p0-<root-cause>.md
```

Use `Status: ready_for_cursor` and include:

- player evidence with feedback row/version references
- why the issue is P0
- non-negotiable constraints, especially DataService, StreamingEnabled, economy, remotes, and UI limits
- required Cursor `@` attachments
- likely scripts to inspect
- investigation plan before implementation
- acceptance criteria / Studio smoke tests
- explicit out-of-scope guardrails
- a Cursor-ready prompt block

For high-risk Scraplands bugs, prefer **separate root-cause task files** over one large catch-all prompt. Cursor should implement one P0 at a time; Hermes reviews scope/diff and Oz validates in Studio/live before commit/ship.

## Prompt template

```markdown
## Goal
[One sentence: player-visible or engineering outcome]

## Mode
[bug fix | feature | refactor | commit prep | debug session | docs only]

## Constraints (non-negotiable)
- StreamingEnabled: yes (almost always)
- Persistence: [DataService / partial saves / v2 — if applicable]
- Studio-first: [what in Studio vs code]
- Do not break: [miner pickup, carry routing, rebirth saves, etc.]

## Context
- README(s): [paths]
- Related decisions: [from decisions.md]
- placeVersion / feedback row: [if from triage]

## Scope
- Files likely touched: [list or "discover via search"]
- Out of scope: [explicit exclusions]

## Acceptance criteria
1. [Observable behavior or test step]
2. [Regression checks]

## Model hint
[cheap | premium — and why]

## Commit
[yes — prep commit + README changelog | no — implementation only]
```

## Model routing (tell Cursor explicitly)

**Premium:** persistence, economy, rebirth, remotes, replication, StreamingEnabled, monetization, multi-file server work.

**Cheap:** copy, changelogs, formatting, small client-only tweaks, docs under `ai/`.

## Task-type shortcuts

| Type | Hermes provides |
|------|-----------------|
| Small fix | Goal + file hint + acceptance criteria + "minimal diff" |
| Multi-file feature | Phased steps ("Step 1: schema + server only") |
| Debug session | Reference `ai/workflows/debugging_workflow.md`; max 3 fix iterations |
| Commit prep / "ready to ship" | Point Cursor to `ai/workflows/ready_to_ship.md`: review diff, update README changelogs/localization, run checks, suggest or use commit message, and commit/push only when appropriate |

## Player-facing UI

Ask Oz: **TutorialGui or NotificationGui?** before Cursor touches GUI code. Hierarchy in Studio first.

## Anti-patterns (never prompt Cursor this way)

- "Refactor the whole mining system" without README review
- "Add a new ScreenGui in code" without GUI decision
- Save bypassing DataService or full-config overwrite
- "Scan Workspace every frame"
- "Install Rojo"
- Commit + push without Oz's explicit request
- Gameplay bugs with no acceptance criteria
