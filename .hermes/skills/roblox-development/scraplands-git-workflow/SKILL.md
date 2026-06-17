---
name: scraplands-git-workflow
description: >-
  Alfred/Hermes git workflow for Scraplands on VPS. Use for sync, commits, ship,
  branch safety, or any git operation on ~/projects/scraplands.
---

# Scraplands Git Workflow (Alfred)

Full doc: repo `shellScripts/README.md`.

## Model routing

Multi-step git batches (sync + inspect + ship prep across many files) should use **`delegate_task`** when the work is mechanical. Subagents run on OpenRouter `qwen/qwen3-coder`; keep the main GPT-5.5 session for judgment calls and Oz-facing summaries. See `scraplands-hermes/references/model_routing.md`.

## Repo path

```text
~/projects/scraplands
```

## Every task sequence

1. **Sync** — `scrapupdate` (before starting any work)
2. **Work** — edit files; do not pull/rebase/merge mid-task
3. **Pre-ship scope check** — before running `ship.sh`, inspect `git status --short`, `git diff --stat`, and `git diff --name-only`. The ship script runs `git add .`, so **any untracked or unrelated file will be committed** unless removed/stashed first.
4. **Ship** — when Oz says "ready to ship", follow repo `ai/workflows/ready_to_ship.md`, then use `./shellScripts/ship.sh "commit message"` when commit/push is approved

## Never

- Random ad-hoc git commands
- Force push unless Oz explicitly instructs
- Rebase or merge during an active task
- Commit with ad-hoc messages outside `ship.sh` workflow
- Destructive git without explicit instruction

## Commit identity

```bash
git config --global user.name "Alfred"
git config --global user.email "alfred@scraplands.dev"  # or project email
```

## Pre-commit checks

- `DEBUG_ENABLED` must be `false` in all modified scripts
- README changelogs updated for feature/fix commits
- Localization CSV updated in repo if player-facing strings changed (Oz uploads to Studio)

## Ship script push-rejection pitfall

`./shellScripts/ship.sh` may still print `Shipped successfully.` even when `git push` is rejected because remote `main` moved. Do not trust the final echo alone. Always verify after ship with `git status -sb` and `git log -1 --oneline`.

If the commit was created but push was rejected with `fetch first`:

1. Run `git fetch origin` and inspect `git status -sb` plus `git log --oneline --decorate --left-right HEAD...origin/main`.
2. If local branch is exactly one Alfred commit ahead and only behind new remote commits, rebase that local commit onto `origin/main` (`git rebase origin/main`).
3. Push using `./shellScripts/push.sh`.
4. Re-verify clean tracking state and latest commit SHA before telling Oz it shipped.

Do **not** force-push or reset to recover from this; escalate if the rebase conflicts.

## Hermes vs Cursor on git

- **Cursor** may prep commits when Oz asks
- **Hermes/Alfred** uses `ship.sh` on VPS after human validation
- Never assume auto-commit or auto-push

## Agent ops topic

Report git failures clearly: command run, error output, suggested fix. Keep infra chatter in 🤖 Agent Ops topic, not Active Dev.
