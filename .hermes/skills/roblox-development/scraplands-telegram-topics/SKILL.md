---
name: scraplands-telegram-topics
description: >-
  Routes Scraplands Hermes behavior for ad hoc Telegram threads. Use when a
  Telegram thread/topic is identified, or when choosing operational mode (ideas,
  dev, QA, publishing, feedback, analytics, agent ops).
---

# Scraplands Telegram Topics

Oz now creates Telegram topics/threads ad hoc. Do **not** assume a fixed, pre-established set of Telegram topics or depend on hard-coded topic IDs.

Full repo instructions live in `ai/telegram/README.md`; behavior mode files live in `ai/telegram/topics/`.

## Runtime routing

For each Telegram message:

1. Read the current thread/topic title when available.
2. Read Oz's actual request and recent thread context.
3. Infer the best behavior mode from intent, not from a topic ID.
4. Load the matching repo file under `ai/telegram/topics/` as operational context.
5. If the title and request disagree, prioritize the request.
6. Ask a clarifying question only if the ambiguity materially changes the work product; otherwise choose the safest mode and proceed.

`ai/telegram/topic_map.example.json` is legacy/example-only and should not be treated as live routing config.

## Behavior mode → usage

| Mode file | Purpose | Hermes should | Avoid |
|-------|---------|---------------|-------|
| `ideas.md` | Brainstorm, UX exploration | Explore options; create/update GitHub issues when ideas become actionable; use GitHub labels/project fields for prioritization; capture durable system decisions in `ai/memory/` | Implementation-ready prompts without design pass |
| `active_dev.md` | Execution | Work from GitHub issues; tell Oz to copy the issue URL/body into Cursor; QA checklists; update GitHub status/labels | Endless brainstorming; vague scope; local `ai/tasks/` files |
| `qa_bugs.md` | Regressions, repro | Triage symptoms; cluster issues; hand off with repro steps | Feature ideation |
| `publishing.md` | Release prep | Summarize what shipped; rollout risks; localization reminder | Unscoped new features |
| `feedback_triage.md` | Player CSV / pain points | Watermark workflow in `Feedback/triage/player_feedback_triage.md` | Re-triaging from scratch each time |
| `analytics.md` | Telemetry, retention | Trends and hypotheses; route actionable bugs to QA behavior | Direct code changes |
| `agent_ops.md` | Git, infra, automation | Clear failure reports; suggest fixes (`scraplands-git-workflow`) | Design brainstorming |

## Runtime context stack

For each message:

1. Matching behavior mode (repo: `ai/telegram/topics/<mode>.md`)
2. `ai/identity/ux_principles.md` + `ai/identity/anti_patterns.md` when copy/UX involved
3. `ai/workflows/<mode>.md` for the task type
4. `ai/systems/` or `ai/memory/` when economy/progression touched

Telegram chat history is **not** durable memory — write outcomes to repo files.
