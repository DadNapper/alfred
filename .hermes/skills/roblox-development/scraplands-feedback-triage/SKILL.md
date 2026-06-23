---
name: scraplands-feedback-triage
description: >-
  Review, organize, summarize, prioritize, and optionally update Scraplands
  player feedback collected from Google Sheets. Use for new feedback passes,
  status/notes updates, duplicate clustering, and recent player-signal summaries.
---

# Feedback Triage

## Purpose

Review, organize, summarize, and prioritize Scraplands player feedback collected from Google Sheets.

Feedback is categorized as:

- bug
- feedback
- idea

The objective is to help Alfred quickly identify important issues, recurring complaints, feature requests, and high-impact opportunities.

## Model routing

Use **`delegate_task` automatically** for feedback triage/classification workloads. Do not wait for the user to explicitly request delegation.

Subagents run on OpenRouter `qwen/qwen3-coder` per `~/.hermes/config.yaml` → `delegation.*`.

GPT-5.5 remains the orchestrator and should synthesize/finalize results.

Automatically delegate when:

- more than 10 feedback items
- more than 10 bug reports
- more than 10 feature requests
- more than 20 records need review/classification

Also delegate by task type even below thresholds when the work is repetitive/batch (duplicate detection, sentiment analysis, translation passes, bulk summarization, backlog grooming, task extraction).

See `scraplands-hermes/references/model_routing.md`.

---

## Data Source

Google Sheets integration lives at:

```text
/home/alfred/.hermes/integrations/google_sheets.py
```

When running directly from shell, include the integrations path:

```bash
PYTHONPATH=/home/alfred/.hermes/integrations python3 - <<'PY'
from google_sheets import GoogleSheets
sheets = GoogleSheets()
print(len(sheets.get_new_bugs()))
PY
```

Python import:

```python
from google_sheets import GoogleSheets
```

Initialize:

```python
sheets = GoogleSheets()
```

The feedback sheet includes `status` and `notes` columns beyond the core feedback fields; make sure reads include those columns before counting or updating statuses.

---

## Available Functions

### Get All Feedback

```python
sheets.get_player_feedback()
```

Returns all feedback records.

---

### Get Bugs

```python
sheets.get_bugs()
```

Returns records where:

```text
feedbackType = bug
```

---

### Get Feedback

```python
sheets.get_feedback()
```

Returns records where:

```text
feedbackType = feedback
```

---

### Get Ideas

```python
sheets.get_ideas()
```

Returns records where:

```text
feedbackType = idea
```

---

## Status Functions

### Get Items By Status

```python
sheets.get_items_by_status("new")
sheets.get_items_by_status("triaged")
sheets.get_items_by_status("fixed")
```

Valid statuses:

```text
new
triaged
in_progress
fixed
released
wont_fix
```

---

### Dedicated Status Helpers

```python
sheets.get_new_items()
sheets.get_triaged_items()
sheets.get_in_progress_items()
sheets.get_fixed_items()
sheets.get_released_items()
sheets.get_wont_fix_items()
```

---

### New Item Helpers

```python
sheets.get_new_bugs()
sheets.get_new_feedback()
sheets.get_new_ideas()
```

These should be preferred when reviewing new reports.

---

### Flexible Filtering

```python
sheets.filter_feedback(
    feedback_type="bug",
    status="new"
)
```

Examples:

```python
sheets.filter_feedback(
    feedback_type="bug",
    status="new"
)

sheets.filter_feedback(
    feedback_type="idea",
    status="triaged"
)

sheets.filter_feedback(
    feedback_type="feedback",
    status="new"
)
```

---

### Search Feedback

```python
sheets.search_feedback("keyword")
```

Examples:

```python
sheets.search_feedback("drone")
sheets.search_feedback("wagon")
sheets.search_feedback("soccer")
sheets.search_feedback("furnace")
sheets.search_feedback("pet")
sheets.search_feedback("performance")
```

---

### Recent Feedback

```python
sheets.get_recent_feedback(days=7)
```

Returns records submitted within the specified number of days.

---

### Summarize Recent Feedback

```python
sheets.summarize_recent_feedback(days=7)
```

Returns:

- total
- bug_count
- feedback_count
- idea_count
- bugs
- feedback
- ideas

---

### Status Counts

```python
sheets.get_status_counts()
```

Example output:

```json
{
  "new": 132,
  "triaged": 41,
  "in_progress": 12,
  "fixed": 38,
  "released": 420,
  "wont_fix": 17
}
```

---

## Write Functions

### Update Status

```python
sheets.update_status(row_number, status)
```

Example:

```python
sheets.update_status(42, "triaged")
```

### Update Notes

```python
sheets.update_notes(row_number, notes)
```

Example:

```python
sheets.update_notes(
    42,
    "Duplicate of wagon ownership issue"
)
```

### Workflow Helpers

```python
sheets.mark_triaged(row_number, notes="")
sheets.mark_in_progress(row_number, notes="")
sheets.mark_fixed(row_number, notes="")
sheets.mark_released(row_number, notes="")
sheets.mark_wont_fix(row_number, notes="")
```

Examples:

```python
sheets.mark_triaged(
    42,
    notes="Needs investigation"
)

sheets.mark_fixed(
    42,
    notes="Fixed by wagon ownership rewrite"
)
```

---

## Status Meanings

| Status | Meaning |
|----------|----------|
| new | Not reviewed |
| triaged | Reviewed and categorized |
| in_progress | Actively being worked on |
| fixed | Solution implemented |
| released | Included in a published game update |
| wont_fix | Intentionally not being addressed |

---

## Review Rules

1. Prioritize bugs over feedback and ideas.
2. Prioritize status = new.
3. Ignore released items unless explicitly requested.
4. Ignore wont_fix items unless explicitly requested.
5. Identify duplicate reports whenever possible.
6. Group similar reports together.
7. Focus on root causes rather than individual reports.
8. Look for patterns and trends.
9. Recommend status changes when appropriate.
10. Hermes may update status and notes fields when performing triage work explicitly requested by Oz.
11. When changing status, always add a note explaining the reasoning when possible.
12. Prefer triaged before in_progress, and fixed before released.

---

## Language Handling

Feedback may be submitted in any language.

When feedback is not in English:

1. Preserve the original `feedbackText`.
2. Translate the feedback into English.
3. Add the translation at the beginning of `notes`.
4. Prefix translations with:

   ```text
   🌐 Translation:
   ```

5. Leave a blank line after the translation.
6. Append all triage notes below the translation.
7. Use the translated text for triage.
8. Never overwrite the original `feedbackText`.
9. Do not mark feedback as `wont_fix` solely because it is not English.

Example:

```text
🌐 Translation: I cannot sell gold.

Likely issue with Gold Trader interaction.
```

---

## Non-Actionable Feedback

Some feedback contains frustration, insults, or opinions but does not provide enough information to investigate or act on.

Examples:

- "this game sucks"
- "trash"
- "bad game"
- "boring"
- "worst game ever"
- profanity without context

When feedback contains no actionable information:

```text
status = wont_fix
```

Notes should include:

```text
Non-actionable feedback
```

Do not spend time investigating these reports.

### Important Exception

Do not classify feedback as non-actionable if it contains:

- A bug description
- A symptom
- A complaint tied to a specific system
- A feature request
- A suggestion
- A gameplay concern

Examples of actionable feedback (triage normally):

- "this game sucks because drones keep getting stuck"
- "boring after level 20"
- "soccer balls spawn too slowly"
- "can't trade stickers"
- "wagon disappeared"

---

## Duplicate Reports

When a report describes an issue already tracked elsewhere:

```text
status = wont_fix
```

Notes should include:

```text
Duplicate of issue: <description>
```

Example:

```text
Duplicate of drone pathfinding issue.
```

Reference the primary issue whenever possible.

---

## Recommended Triage Workflow

For new bugs:

new → triaged → in_progress → fixed → released

For rejected issues:

new → triaged → wont_fix

For non-actionable feedback and duplicate reports, see [Non-Actionable Feedback](#non-actionable-feedback) and [Duplicate Reports](#duplicate-reports).

Always leave enough context in notes so future reviews can understand why a status was changed.

---

## P0 Fix Extraction From Bug Lists

When Oz asks for P0 fixes based on a bug list, keep the P0 set intentionally narrow. Escalate to P0 when the cluster can:

- lose or roll back player progress, purchases, miners, world unlocks, rebirth state, or high-value items
- corrupt economy state or copy one world's balance into another
- block the core loop of mine → collect → sell → progress
- force rejoin/reset as the only recovery path
- hard-lock movement, UI, selling, or interaction after reset/death/world travel

Usually **not P0 by default** unless tied to the above: generic lag, pet pathing delay, UI truncation, tutorial confusion, car controls, or isolated QoL requests.

Recommended output shape:

1. Name the P0 cluster as a root-cause class, not an individual row.
2. Include representative row/version evidence.
3. Explain why it is P0 in one sentence.
4. State likely fix direction and acceptance checks.
5. Recommend creating or updating a GitHub issue for each root-cause class.

---

## Second-Pass Backlog Cleanup Workflow

Use this after the bug pass when many non-bug `new` rows remain.

1. Snapshot the sheet before mutating it.
2. Process remaining `new` rows across `Feedback`, `Idea`, and blank/unknown feedback types.
3. Preserve original `feedbackText`; never overwrite it.
4. For non-English feedback, add `🌐 Translation: <English translation>` at the top of notes, then a blank line, then triage notes.
   - Classify using the English translation, not only the original text. A translated feature request should stay `triaged`; do not accidentally mark it `wont_fix` because keyword rules could not read the source language.
5. Mark `wont_fix` for:
   - positive-only feedback with no task
   - spam/gibberish/profanity with no useful context
   - requests for Robux/account grants/personal freebies
   - duplicate rows already represented by a bug/feedback cluster
6. Mark `triaged` for actionable product/design signals, even if rough or translated: tutorial confusion, economy pacing, feature requests, accessibility/platform asks, control issues, content ideas, etc.
7. For duplicate rows, notes should name the primary cluster rather than re-investigating the row.
8. Re-read the sheet after writing and verify: `new` count, status counts, and missing-note count.

Useful duplicate-note pattern:

```text
Duplicate of issue: performance/lag cluster already captured in bug triage; keep one cluster open rather than separate duplicate rows. Original type: feedback; original report v6329.
```

---

## New-Item Triage After Recent Publishes

Use this when Oz asks whether new Google Sheet rows can be combined with existing triaged tasks after a publish.

1. Snapshot the sheet before mutating it.
2. Read all `status = new` rows, then map each row to one of:
   - existing open GitHub issue
   - recently published GitHub issue that may need reopening/regression verification
   - existing backlog/feature/UX cluster in GitHub
   - genuinely new issue candidate
3. Update sheet `status` + `notes`, but **do not silently stop there**. After writing notes, explicitly summarize:
   - which rows mapped to open GitHub issues
   - which rows map to published issues as post-fix regression signals
   - which rows are P0/P1 candidates
   - whether any GitHub issue should be updated or reopened
4. Treat fresh post-publish reports as stronger signal than older backlog rows. A row newer than the shipped fix should usually stay `triaged`/open, not `fixed`, even if it overlaps the same cluster.
5. Escalate to **P0** when a new row indicates high-value item loss, progress rollback, world-travel persistence loss, economy corruption, hard-lock/session-ending state, or paid/Robux-value loss. Example: gold nuggets/conveyor/furnace contents disappearing across world travel is P0 until disproven because it combines high-value item loss + world travel persistence + furnace lifecycle risk.
6. If you only updated the sheet and not GitHub issues, say that plainly. If a new row materially changes an issue’s evidence or acceptance criteria, update/comment on the GitHub issue when Oz asks.
7. If Oz follows up with “create tickets,” “create GitHub issues,” or “ship it,” create or update GitHub issues for **each actionable root-cause class**, not just P0s. The GitHub issue is canonical; do not create local `ai/tasks/` files.
8. For each GitHub issue: search duplicates first, include row/version evidence, likely scripts, required readings, investigation plan, acceptance criteria, priority rationale, a body model hint (`## Model\nModel: auto|medium|premium`), and labels (`priority:*`, `type:*`, `area:*`, `source:player-feedback`, `status:ready` or `status:backlog`, `model:*`). Add the issue to the GitHub Project / status field when API scopes allow it.
9. For docs-only issue/task creation, no README changelog or localization CSV is needed. Still run the ready-to-ship checks and use the Scraplands ship workflow once Oz explicitly asks to ship.

See `references/feedback-to-github-issues-2026-06-17.md` for a compact example of turning a small post-publish feedback batch into GitHub issues.

See `references/latest-feedback-to-github-issue-2026-06-21.md` for a small two-row pass: snapshot, duplicate search, one new GitHub issue, one non-actionable `wont_fix`, sheet verification, and fallback `status:*` labels when Projects v2 movement is unavailable.

See `references/latest-feedback-github-sync-2026-06-22.md` for the follow-up pattern when Oz says “update GitHub issues and push”: use the repo GitHub helper even if `gh` is unauthenticated, reopen closed issues for fresh post-fix regression evidence, create one issue per root-cause class, update Sheet notes with canonical GitHub URLs, write `ai/triage/feedback_triage_<date>.md`, then ship/push the summary with verified remote state.

See `references/automated-feedback-triage-cron.md` for the daily cron pattern: run an LLM-driven job each morning, no-op cleanly when there are no new rows, create/update GitHub issues when rows exist, write an `ai/triage/*_auto.md` summary, and only commit/push intended triage summary files when the working tree has no unrelated changes.

### Small latest-feedback batch checklist

When only a few `status = new` rows exist, do not skip the workflow just because the batch is small:

1. Snapshot the sheet before mutating it.
2. Search GitHub for duplicates using root-cause/system terms, not only the exact feedback wording.
3. Create or update one issue per actionable root-cause class; mark noise/non-actionable rows `wont_fix` with a note.
4. Include row/version/platform evidence, likely scripts/docs, acceptance checks, constraints, labels, and `## Model` in any new GitHub issue.
5. Update sheet status/notes with the GitHub issue URL or non-actionable rationale.
6. Re-read and verify `new` count, status counts, and row notes after writes.
7. If Projects v2 status movement is unavailable, apply fallback `status:*` labels and say that Project status was not moved; do not block issue creation on Project API/config.
8. Write a concise `ai/triage/feedback_triage_<date>.md` summary when GitHub issues or meaningful sheet statuses changed.

## Large First-Pass Bug Triage Workflow

Use this when the sheet has many old `new` bugs and Oz wants status/notes backfilled from git history.

Reference: `references/post-publish-fixed-status-update-2026-06-15.md` captures a concrete post-publish fixed-status update pattern, including sheet snapshotting, published task inspection, batch status/notes updates, and verification.

1. Snapshot the sheet before mutating it. Save local artifacts outside the Scraplands repo unless Oz explicitly wants repo artifacts.
2. Focus on `feedbackType = Bug` first; leave feedback/ideas alone unless requested.
3. Cluster by symptom/root cause before searching git history. Do not process row-by-row as the primary strategy.
4. Search git history by cluster terms and affected systems. Prefer high-confidence commit matches over broad keyword matches.
5. Mark `fixed` only when the report predates a specific likely fix and the symptom matches the commit(s). Put commit IDs directly in `notes`.
6. Mark `triaged` when the report is still useful context but not high-confidence fixed, especially persistence/data-loss, performance, mobile input, post-hotfix regressions, or vague reports.
7. Treat newer reports after a candidate fix as regression/new signal; keep them `triaged`, not `fixed`.
8. Batch-update only `status` and `notes` for the target rows, then re-read the sheet and verify counts plus missing-note count.
9. Clean up temp scripts and keep the repo git status clean unless Oz asked for repo files.

Recommended note style:

```text
Fixed: money/sell/world-currency rollback cluster. Relevant commits: bfd845cb fixed world-travel money/rebirth display; b3c94322 prevented duplicate deposits; 11a50dda added ore-selling stuck-state recovery. Original report v6329.
```

```text
Triaged: possible persistence/progress-loss report. Related hardening exists (8b6fe0c1 leave-save hardening, fbac6e0d DataService bootstrap, 9fcbf909 datastore guardrails), but not safe to mark fixed without exact repro match. Original report v6329.
```

---

## Output Style

Be concise.

Group similar reports together.

Prefer summaries over raw lists.

Example:

Good:

"12 players reported drones getting stuck while delivering ore."

Avoid:

Listing 12 nearly identical reports individually.

Focus on:

- Severity
- Frequency
- Root causes
- Recommended actions
- Impact on players
