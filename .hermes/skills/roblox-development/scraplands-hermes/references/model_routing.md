# Model Routing (Scraplands Hermes)

Hermes uses a **role-based orchestrator pattern**, not task routing by fallback order.

Fallback providers are only for provider failures: rate limits, 5xxs, connection errors, auth/provider interruptions. They are not a model-selection policy.

## Roles

### Primary Orchestrator

- **Provider:** `openai-codex`
- **Model:** `gpt-5.5`
- **Config:** `~/.hermes/config.yaml` → `model.provider`, `model.default`
- **Responsibility:** project lead, reasoning engine, final reviewer, user-facing synthesis.

Use GPT-5.5 for:

- Product decisions
- Game design
- Economy balancing
- Monetization decisions
- UX/UI decisions
- Roblox architecture and system design
- Planning
- Feature specifications
- Bug triage synthesis
- Changelog generation
- Documentation direction
- Copywriting and localization review
- Roadmapping and prioritization
- Strategic decisions
- Project management
- Final recommendations after delegated work

### Coding Worker

- **Provider:** `openrouter`
- **Model:** `qwen/qwen3-coder`
- **Config:** `~/.hermes/config.yaml` → `delegation.provider`, `delegation.model`
- **Mechanism:** `delegate_task`
- **Responsibility:** primary software engineer for implementation, codebase navigation, static analysis, code review, and root-cause work.

Use Qwen3-Coder for:

- Roblox/Luau implementation
- Refactors
- Multi-file code changes
- Performance optimization
- Static analysis
- Code review
- Root cause analysis
- Test generation
- GitHub issue implementation
- Large codebase navigation
- Roblox/Luau code generation
- Mechanical git/diff analysis when scoped by GPT-5.5
- Bulk feedback/bug/feature classification when the job is analysis-heavy

### Lightweight Worker

- **Provider:** `openai-api` or configured auxiliary provider
- **Model:** `openai/gpt-4.1-mini` / `gpt-4.1-mini`
- **Config:** `~/.hermes/config.yaml` → `auxiliary.*`, selected helper/fallback slots
- **Responsibility:** low-cost utility work.

Use GPT-4.1-mini for:

- Summaries
- Formatting
- Data transformation
- Small helper tasks
- Log cleanup
- Simple documentation generation
- Titles, compression, monitoring summaries, and other auxiliary side jobs

## Automatic delegation rules

Hermes should automatically delegate to Qwen3-Coder when any of these are true:

- More than one file is involved
- Estimated change exceeds 200 lines
- Oz requests implementation
- Oz requests a refactor
- Oz requests a code review
- Oz requests performance optimization
- Oz requests bug investigation
- Oz requests architecture validation with codebase inspection
- Oz requests GitHub issue implementation
- Oz requests Roblox/Luau code generation
- The task requires static analysis across multiple files
- The task requires root-cause analysis in code
- The task requires test generation or validation scripts

Hermes should keep work on GPT-5.5 when the task is primarily:

- Product design discussion
- Game economy balancing
- Monetization decisions
- UX/UI decisions
- Roadmapping
- Feature prioritization
- Changelog writing
- Copywriting
- Localization review
- Strategic decisions
- Final decision-making after delegated implementation/review

## Coding workflow

For coding tasks:

1. GPT-5.5 analyzes the request and project context.
2. GPT-5.5 creates a clear implementation plan and acceptance criteria.
3. Delegate implementation work to Qwen3-Coder with the exact scope, files, commands, and Scraplands constraints.
4. Receive implementation results with file paths, commands run, test/static-analysis output, and any unresolved risks.
5. GPT-5.5 reviews the result for correctness, maintainability, Roblox constraints, product alignment, and rollout safety.
6. Present Oz with the final recommendation, evidence, and next action.

For large coding tasks:

1. Break work into smaller subtasks.
2. Delegate independent subtasks to Qwen3-Coder.
3. Avoid parallel workers touching the same files.
4. Aggregate results.
5. Run or request final verification.
6. GPT-5.5 performs final review and synthesis.

## Scraplands implementation guardrails

When delegating Scraplands coding work, include these constraints in the Qwen context:

- Repo: `~/projects/scraplands`
- Read `AGENTS.md`, `ai/README.md`, relevant workflows, and feature docs first.
- No Rojo; Script Sync workflow only.
- New scripts go under service `Scripts/` folders.
- Suffixes: `.legacy.luau` for server scripts, `.local.luau` for client scripts, `.luau` for modules.
- StreamingEnabled is always enabled.
- All persistent writes go through DataService / PlayerData_v2 patterns.
- Avoid DataStore write pressure and duplicate leave-time saves.
- Do not enable live-ops/tester gates server-wide based on any tester online; keep eligibility per-player unless explicitly isolated to private-server-owner testing.
- Never force push, rebase, reset hard, delete branches, or ship without Oz's approval.
- Never leave `DEBUG_ENABLED = true`.
- Run targeted Selene/StyLua/Luau analysis when applicable and report real output.

## Responsibility → model

| Responsibility | Model | How it is enforced |
|---|---|---|
| Project lead / reasoning | GPT-5.5 | `model.provider=openai-codex`, `model.default=gpt-5.5` |
| Product / design / economy / UX | GPT-5.5 | main session stays on GPT-5.5 |
| Architecture / planning / specifications | GPT-5.5 | main session, with Qwen codebase inspection when needed |
| Roblox/Luau implementation | Qwen3-Coder | `delegate_task` → `delegation.*` |
| Refactors / multi-file edits | Qwen3-Coder | automatic delegation trigger |
| Code review / RCA / static analysis | Qwen3-Coder | automatic delegation trigger, GPT-5.5 final synthesis |
| GitHub issue implementation | Qwen3-Coder | delegate implementation worker |
| Summaries / formatting / simple transforms | GPT-4.1-mini | `auxiliary.*` or explicit lightweight helper |
| Provider failure | fallback chain | only when provider/model call fails |

## Runtime config map

| Layer | Location | Read by Hermes? |
|---|---|---|
| Runtime config | `~/.hermes/config.yaml` | **Yes** — `model`, `delegation`, `auxiliary`, `fallback_providers` |
| Agent playbook | This file | **Yes** — when `scraplands-hermes` loads this reference |
| Human YAML index | `~/.hermes/model_routing.yml` | No — quick map for humans only |
| Per-skill hints | Scraplands skills | Yes — short delegate reminders |

Rule: when routing changes, edit `config.yaml` first, then update this file and `model_routing.yml`. Never put API keys in skills.

## Fallback policy

Fallbacks are provider-failure recovery only. They should not be used as task routing.

Preferred fallback order when GPT-5.5 via OpenAI Codex is unavailable:

1. `openrouter` / `openai/gpt-5.5` — preserve orchestrator quality if possible.
2. `openrouter` / `qwen/qwen3-coder` — capable coding/reasoning backup.
3. `openai-api` / `gpt-4.1-mini` — low-cost emergency continuation.
4. `openrouter` / `openai/gpt-4.1-mini` — final backup.

Primary should restore on the next normal turn when available.

## Verification

Static checks:

```bash
hermes fallback list
hermes config check
hermes doctor
```

Live OpenRouter / Qwen smoke test:

```bash
hermes chat -q "Reply with exactly: qwen-ok" --provider openrouter -m qwen/qwen3-coder
```

Delegation smoke test:

> Use `delegate_task` to run `echo delegation-test` and report the output.

Then confirm the delegated worker used `provider=openrouter` and `model=qwen/qwen3-coder` in Hermes logs if needed.

After changing `config.yaml`, restart the gateway so new Telegram sessions pick up routing:

```bash
hermes gateway restart
```

Existing sessions may need `/new`, `/reset`, or a fresh `hermes` invocation.
