# Latest feedback → GitHub sync pattern — 2026-06-22

Use when Oz asks to update GitHub after a Google Sheet feedback triage pass and push the repo summary.

## What worked

1. **Search GitHub duplicates before creating issues** using the repo helper, not only `gh`:
   - `gh` may be unauthenticated while `ai/tools/github_issues.py` still works via `~/.hermes/.env`.
   - Example search command:
     ```bash
     python3 ai/tools/github_issues.py search '"Safe Sell"'
     ```
2. **Reopen closed issues when fresh post-fix evidence matches the same root-cause class.**
   - Row 799/800 reopened #39 for save-before-travel failure.
   - Row 797 reopened #9 for pickaxe/backpack inventory-not-added symptoms.
3. **Create one issue per root-cause class, not per row.**
   - Rows 796 + 803 became one currency-HUD/world-travel issue.
   - Row 800 stayed duplicate of row 799/#39.
4. **After creating/reopening issues, update Sheet notes again with canonical GitHub URLs.**
   - Do not leave Sheet notes as local-only triage text once GitHub exists.
5. **Write a repo triage summary under `ai/triage/feedback_triage_<date>.md`.**
   - Include snapshot path, final status counts, reopened issues, created issues, row table, and Project/fallback-label note.
6. **Push the repo summary through the Scraplands ship workflow.**
   - `ship.sh` can print success even when push is rejected; verify with `git status -sb`, `git log -1 --oneline`, and `git ls-remote origin refs/heads/main`.
   - If local commit is clean but remote moved, fetch, inspect `HEAD...origin/main`, rebase the single Alfred summary commit onto `origin/main`, then use `./shellScripts/push.sh`.

## Issue body checklist

Each created/reopened issue should include:

- player evidence: sheet row, version, platform, player display name, quoted report
- priority rationale
- investigation notes / likely systems
- acceptance checks
- Scraplands constraints relevant to the risk class
- `## Model\nModel: auto|medium|premium`
- labels: `priority:*`, `status:*`, `type:bug`, `source:player-feedback`, `area:*`, `model:*`

## Project status caveat

If Projects v2 status movement is unavailable, apply fallback `status:*` labels and say so in the triage summary. Do not block issue creation or Sheet linking on Project API configuration.
