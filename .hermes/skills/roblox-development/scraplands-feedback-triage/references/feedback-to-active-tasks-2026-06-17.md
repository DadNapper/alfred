# Feedback → Active Task Specs Pattern (2026-06-17)

Use when a small batch of fresh Google Sheet feedback has already been triaged and Oz asks to create active task files and ship them.

## Pattern

1. Start from the triaged sheet rows and existing published/active tasks; do not re-triage from scratch.
2. Create one `ai/tasks/active/` spec per actionable root-cause class, including non-P0 QoL/UX work if Oz asked for active tasks broadly.
3. Filename convention:
   - `p0-<root-cause>(model:premium).md` for data loss, high-value item loss, core-loop inventory/economy regressions, or multi-system race bugs.
   - `p1-<root-cause>(model:premium).md` for session-ending UI/control softlocks without confirmed data loss.
   - `p2-<root-cause>(model:auto).md` for QoL or visual/progression clarity issues.
4. Task file structure:
   - `Status: ready_for_cursor`
   - task metadata: ID, created date, priority, owner, implementation/review, topic, model, source rows, related published tasks
   - Goal, Why priority, Player Evidence, Hypothesis/Product Direction
   - Non-negotiable constraints
   - Required readings / Cursor attachments
   - likely scripts/files to inspect
   - investigation plan
   - acceptance criteria
   - out-of-scope guardrails
   - Cursor prompt block
5. For docs-only active-task creation:
   - no README changelog is required
   - no localization CSV is required
   - still run ship-prep checks (`git diff --check`, debug flag grep, status/diff review)
   - use `./shellScripts/ship.sh "Add active feedback triage tasks"` only after Oz explicitly says ship.

## Concrete split from the session

Rows `767`–`768` became one P0 task: gold furnace/conveyor/carry jam regression.

Row `769` became one P0 task: pickaxe + pet nearby inventory not added regression.

Row `766` became one P1 task: respawn menus break and require rejoin.

Rows `765` and `770` became P2 tasks: stable pickaxe hotbar slot and Meadows research maxed/star display mismatch.

## Pitfall

Do not create only the P0 files when Oz says “active task files” for the whole triaged batch. Include actionable P1/P2 tasks too, but make their priority/model hints clear so Cursor starts with the P0s.
