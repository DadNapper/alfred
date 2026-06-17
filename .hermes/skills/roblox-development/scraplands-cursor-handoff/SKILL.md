---
name: scraplands-cursor-handoff
description: >-
  Writes Cursor implementation prompts for Scraplands. Use when handing off code
  changes, debugging with repo access, commits, or Studio MCP investigation to
  Cursor.
---

# Scraplands → Cursor Handoff

Hermes plans; Cursor implements. Full spec: repo `ai/workflows/cursor_prompt_mode.md`.

## Source of truth

GitHub Issues + the Scraplands GitHub Project are canonical for bugs, features, and implementation status.

The old `ai/tasks/` tracker is retired. Do **not** create local task files. If a handoff needs more detail than fits in the issue body, add that detail as a GitHub issue comment.

Oz's default fix workflow:

1. Open the canonical GitHub issue.
2. Copy the issue URL/body into Cursor.
3. Cursor implements from that issue context.
4. Cursor/Hermes links commits or PRs back to the issue.
5. Hermes closes the issue only after the fix is verified and published.

## Model routing

Drafting long Cursor handoff prompts or multi-file context packs can be **`delegate_task`**'d to a subagent on OpenRouter `qwen/qwen3-coder`. The main GPT-5.5 agent reviews scope, risk, and final wording before Oz sends to Cursor. See `scraplands-hermes/references/model_routing.md`.

## Before handoff — confirm

- [ ] Actually a **code task** (not Studio-only property/layout work)?
- [ ] GitHub issue number/URL included?
- [ ] Right `Readmes/*.md` named for the feature area?
- [ ] Streaming / mobile / save-risk called out if applicable?
- [ ] Scope bounded (files, explicit non-goals)?
- [ ] Model tier appropriate (premium for persistence, remotes, economy)?
- [ ] Oz should Studio-test before commit?

Do **not** send vague prompts on high-risk systems (DataService, rebirth, remotes, automation).

## Context pack (attach only what's needed)

**Often include:**
- GitHub issue URL/body, or issue number plus Hermes summary
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

## GitHub issue handoff pattern

For high-risk Scraplands bugs, prefer **separate GitHub issues per root-cause class** over one large catch-all issue. Cursor should implement one P0 at a time; Hermes reviews scope/diff and Oz validates in Studio/live before commit/ship.

Each actionable GitHub issue should include:

- player evidence with feedback row/version references
- why the issue is P0/P1/P2
- non-negotiable constraints, especially DataService, StreamingEnabled, economy, remotes, and UI limits
- required Cursor `@` attachments
- likely scripts to inspect
- investigation plan before implementation
- acceptance criteria / Studio smoke tests
- explicit out-of-scope guardrails

## Prompt template

```markdown
## GitHub issue
[#123 Title](https://github.com/DadNapper/scraplands/issues/123)

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

## Commit / issue linkage
[yes/no commit prep]
If committing, link with `Fixes #123` / `Closes #123` when appropriate, but keep the issue open until published.
```

## Model routing (tell Cursor explicitly)

**Premium:** persistence, economy, rebirth, remotes, replication, StreamingEnabled, monetization, multi-file server work.

**Cheap:** copy, changelogs, formatting, small client-only tweaks, docs under `ai/`.

## Task-type shortcuts

| Type | Hermes provides |
|------|-----------------|
| Small fix | GitHub issue + file hint + acceptance criteria + "minimal diff" |
| Multi-file feature | Phased steps in issue/comment ("Step 1: schema + server only") |
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
- Creating local `ai/tasks/` files instead of using GitHub issues/comments
