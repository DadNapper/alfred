# Model Routing (Scraplands Hermes)

Hermes uses an **orchestrator pattern**: the main session stays on premium GPT-5.5 (OpenAI Codex). Cheap or batch work goes to OpenRouter via subagents and auxiliary slots.

## Documentation layers

| Layer | Location | Read by Hermes? |
|-------|----------|-----------------|
| Runtime config | `~/.hermes/config.yaml` | **Yes** — `model`, `delegation`, `auxiliary`, `fallback_providers` |
| Agent playbook | This file | **Yes** — when `scraplands-hermes` loads this reference |
| Human YAML index | `~/.hermes/model_routing.yml` | No — quick map for humans only |
| Per-skill hints | `scraplands-feedback-triage`, `scraplands-git-workflow`, `scraplands-cursor-handoff` | Yes — short delegate reminders |

**Rule:** When routing changes, edit `config.yaml` first, then update this file and `model_routing.yml`. Never put API keys in skills.

## Responsibility → model

| Responsibility | Model | How it is enforced |
|----------------|-------|-------------------|
| Roblox implementation | GPT-5.5 (Cursor) | Cursor implements; Hermes orchestrates |
| Product / design / advisor | GPT-5.5 | `model.provider` / `model.default` |
| Feedback triage (bulk) | Qwen3 Coder | `delegate_task` → `delegation.*` |
| Git workflow (mechanical) | Qwen3 Coder | `delegate_task` → `delegation.*` |
| Cursor handoff drafts | Qwen3 Coder | `delegate_task` → `delegation.*` |
| Telegram summaries / admin PM | GPT-4.1 Mini | `auxiliary.*` (compression, titles, web extract, …) |
| Codex unavailable / rate limited | OpenRouter chain | `fallback_providers` (per turn) |

Premium skills that stay on the main agent: `scraplands-hermes`, `solo-dev-advisor`.

## Main agent (orchestrator)

- **Provider:** `openai-codex`
- **Model:** `gpt-5.5`
- **Use for:** product/design decisions, Roblox architecture, feature design, advisor reasoning
- **Config:** `~/.hermes/config.yaml` → `model.default` / `model.provider`

Roblox **implementation** is Cursor's job, not the main Hermes loop.

## Subagents (`delegate_task`)

- **Provider:** `openrouter`
- **Model:** `qwen/qwen3-coder`
- **Use for:** feedback triage batches, git workflow steps, Cursor handoff prompt drafting
- **Config:** `~/.hermes/config.yaml` → `delegation.provider` / `delegation.model`

**Rule:** Do not burn GPT-5.5 on bulk triage, git batches, or long handoff drafts. Delegate first; synthesize results on the main agent.

## Auxiliary side jobs

| Task | Model | Typical use |
|------|-------|-------------|
| `compression`, `title_generation`, `web_extract`, `approval`, `monitor`, `skills_hub`, `mcp`, `kanban_decomposer`, `profile_describer` | `openai/gpt-4.1-mini` | Telegram summaries, admin/PM, context compression |
| `triage_specifier`, `curator` | `qwen/qwen3-coder` | Kanban triage, skill curation |
| `vision`, `tts_audio_tags` | `auto` (main model) | Leave on main unless vision needs a dedicated model |

Configured under `~/.hermes/config.yaml` → `auxiliary.*`.

## Fallback when Codex is unavailable

Order (per turn; primary restored on the next user message):

1. `openrouter` / `openai/gpt-5.5`
2. `openrouter` / `qwen/qwen3-coder`
3. `openrouter` / `openai/gpt-4.1-mini`

**Config:** `~/.hermes/config.yaml` → `fallback_providers`

Requires `OPENROUTER_API_KEY` in `~/.hermes/.env`.

## Verification

Static checks:

```bash
hermes fallback list
hermes config check
hermes doctor
```

Live OpenRouter / Qwen smoke test:

```bash
hermes -z "Reply with exactly: qwen-ok" --provider openrouter -m qwen/qwen3-coder
```

Delegation smoke test (CLI or Telegram):

> Use delegate_task to run `echo delegation-test` and report the output.

Then confirm `provider=openrouter` and `model=qwen/qwen3-coder` in `~/.hermes/logs/agent.log`.

After changing `config.yaml`, restart the gateway so new Telegram sessions pick up routing:

```bash
sudo hermes gateway restart
```

Existing topic sessions may need `/new` or idle reset.

## Human-readable map

See `~/.hermes/model_routing.yml` for the same mapping in YAML (documentation only).
