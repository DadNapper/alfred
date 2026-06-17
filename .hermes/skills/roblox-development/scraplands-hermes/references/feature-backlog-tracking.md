# Scraplands GitHub Backlog Tracking

Use this when Oz asks to capture, import, triage, prioritize, or convert feature ideas.

## Source of truth

**GitHub Issues + the Scraplands GitHub Project are canonical for development tracking.**

Local repo docs are supporting artifacts:

- `ai/workflows/github_task_tracking.md` — complete GitHub issue/project workflow
- `ai/tools/github_issues.py` — Hermes helper functions for issues, labels, comments, search, priority, and linking commits/PRs
- `ai/features/*.md` — optional product-shaping docs for large ideas
- `ai/tasks/active/*.md` — optional long-form Cursor handoff specs linked from issues
- `ai/tasks/published/` — historical shipped records only, not the active tracker

## Recommended flow

```text
Telegram idea / player feedback / bug report
→ Hermes triage
→ duplicate search in GitHub
→ GitHub Issue
→ GitHub Project Status + Priority
→ optional feature spec or Cursor handoff linked from issue
→ development branch / commit / PR links issue
→ release verification
→ close issue
```

## Google Sheets vs GitHub

Use Google Sheets/CSV for raw player feedback, metrics, sortable triage batches, and external data.

Use GitHub as the canonical source for actionable feature intent and implementation work because Hermes/Cursor can retrieve it, it supports labels/status/priority, it can link commits/PRs, and it avoids parallel local backlogs.

After converting feedback into a GitHub issue, add the issue URL back to the sheet notes/status when appropriate.

## Importing feature CSVs or markdown backlog items

When Oz uploads a CSV backlog or asks to migrate markdown backlog items:

1. Read the source.
2. Cluster near-duplicates before creating tickets.
3. Search GitHub first:

   ```bash
   python ai/tools/github_issues.py search "is:open <keywords>"
   ```

4. Decide whether the source is additive or authoritative:
   - If Oz says it is the “last/latest CSV,” says he removed unnecessary features, or asks to remove anything not in it, treat that CSV as the authoritative replacement set.
   - In authoritative mode, close or comment on superseded GitHub issues rather than leaving stale duplicates.
   - In additive mode, create/update GitHub issues without blindly duplicating near-identical items.
5. Preserve useful wording from the newer source when it changes scope, but do not keep older scope/details that the latest authoritative source intentionally removed.
6. Create or update issues with: priority, area, source, captured/imported date, summary, player value, next action, and acceptance/shaping questions.
7. Keep rough ideas in `status:backlog`; only use `status:ready` when implementation scope is clear.
8. If an imported priority is malformed (e.g. `PO`), label `priority:needs-triage` and call it out for Oz instead of guessing.
9. Verify by re-searching GitHub issues and reporting created, deduplicated, skipped, and human-review items.

## Model routing for backlog grooming

Treat backlog grooming as a delegate-first workflow.

- Use `delegate_task` to Qwen3 Coder for bulk classification, duplicate clustering, and task extraction.
- Automatically delegate when feature rows exceed 10 or total records requiring review exceed 20.
- Keep GPT-5.5 for prioritization decisions, roadmap sequencing, and final recommendation quality checks.

## Advisor triage principles

Prioritize features that improve the existing core loop, retention clarity, and reusable solo-dev platform leverage.

Default near-term bias:

1. Core-loop friction and cross-platform access.
2. Reusable goals/reward systems.
3. Clear discovery/progression feedback.
4. Trust-preserving monetization packages.
5. Reusable liveops/event framework after core clarity improves.

Avoid making large/risky ideas the next build merely because they are exciting. Big event/gameplay systems should usually be shaped after reusable frameworks and core-loop clarity are in place.

## Scraplands-specific prioritization lessons from 2026-06-14

Strong next candidates:

- Tasks System v1 — strategic retention/platform feature; reusable for dailies, events, tutorials, achievements, future games.
- Console + Trader/Sell UX Pack — core-loop friction reduction and device coverage.
- Codex unlock rewards — makes discovery feel rewarding and supports mining progression.
- VIP Bundle — direct monetization, but requires careful existing-ownership migration and kid-safe copy.
- More Badges v1 — quick Roblox-native achievement layer that can later connect to tasks/codex.

Defer unless Oz has a strong reason:

- Full Fog/Nightfall Scrap Beast event — large scope and kid-frustration/item-loss risk; prototype as non-punitive event first.
- Auto miner placement after 2nd rebirth — attractive QoL but high persistence/placement/rebirth risk.
- World 3 research point trader — high economy risk; needs deep design.
- Vague premium multipliers — can create confusing stacking/pay-to-win perception.
- Shovel upgrades — needs distinct gameplay role vs pickaxe before building.
