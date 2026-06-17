# Scraplands Feature Backlog Tracking

Use this when Oz asks to capture, import, triage, prioritize, or convert feature ideas.

## Canonical repo locations

- `ai/features/README.md` — feature tracking workflow and status definitions
- `ai/features/backlog.md` — lightweight capture list for ideas before implementation
- `ai/features/triage_YYYY_MM_DD.md` — advisor prioritization pass / roadmap recommendation
- `ai/features/<feature_slug>.md` — shaped feature spec when an idea needs product design before implementation
- `ai/tasks/active/<task_slug>.md` — implementation-approved task with Cursor prompt, acceptance criteria, and test plan
- `ai/tasks/published/` — shipped/completed task records

## Recommended flow

```text
Telegram idea
→ ai/features/backlog.md
→ ai/features/triage_YYYY_MM_DD.md when Oz wants advisor prioritization
→ ai/features/<feature_slug>.md for shaping/design
→ ai/tasks/active/<task_slug>.md only when Oz wants Cursor to implement
→ ai/tasks/published/ after shipped
```

## Google Sheets vs repo

Use Google Sheets/CSV for raw player feedback, metrics, sortable triage batches, and external data.

Use the repo as the canonical source for feature intent because Hermes/Cursor can retrieve it directly, it is versioned, and it can link to systems docs and task files.

## Importing feature CSVs

When Oz uploads a CSV backlog:

1. Read the CSV.
2. Decide whether the CSV is additive or authoritative:
   - If Oz says it is the “last/latest CSV,” says he removed unnecessary features, or asks to remove anything not in it, treat that CSV as the authoritative replacement set.
   - In authoritative mode, prune backlog entries from prior imports that are not present in the latest CSV, preserving only items Oz explicitly names as exceptions.
   - In additive mode, merge with `ai/features/backlog.md`; do not blindly duplicate near-identical items.
3. Preserve useful wording from the newer CSV when it changes scope, but do not keep older scope/details that the latest authoritative CSV intentionally removed.
4. Normalize into backlog entries with: Status, Priority, Area, Source, Captured date, Summary, Player value, Next action.
5. Keep items as `idea` unless Oz explicitly approves implementation.
6. If an imported priority is malformed (e.g. `PO`), preserve it and mark for triage instead of guessing.
7. Verify after import/prune with a heading scan (`^### `) and a negative search for removed feature names before reporting completion.

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
