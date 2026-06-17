# Hermes Skills for Scraplands

Copy the **skill folders** inside this directory into your Hermes skills folder.

## Install

```bash
cp -R hermes/scraplands-* ~/.hermes/skills/
```

Or copy individual skills as needed. Each subfolder (`scraplands-*`) is one skill with a `SKILL.md`.

---

# Skills

| Folder | Use when | Model Tier |
|----------|----------|----------|
| `scraplands-hermes` | Always load. Project orchestrator, memory, planning, routing. | GPT-5.5 |
| `solo-dev-advisor` | Product strategy, roadmap, prioritization, monetization, growth decisions. | GPT-5.5 |
| `scraplands-cursor-handoff` | Writing implementation prompts and transferring context to Cursor. | Qwen3 Coder |
| `scraplands-bug-triage` | QA, bugs, player feedback, regressions, issue analysis. | Qwen3 Coder |
| `scraplands-git-workflow` | Commits, sync, releases, Alfred VPS git operations. | Qwen3 Coder |
| `scraplands-telegram-topics` | Telegram notifications, summaries, reporting. | GPT-4.1 Mini |

---

# Model Routing

Hermes follows an **orchestrator pattern**.

The primary session runs on GPT-5.5.

Cheap, repeatable, and administrative work should be delegated whenever possible.

| Document | Purpose |
|-----------|---------|
| `scraplands-hermes/references/model_routing.md` | Canonical routing playbook |
| `~/.hermes/model_routing.yml` | Human-readable routing index |
| `~/.hermes/config.yaml` | Runtime enforcement (models, delegation, fallbacks) |

Load `scraplands-hermes` before making model-routing decisions.

---

# Routing Precedence

When determining which model should perform a task:

1. `config.yaml` (runtime enforcement)
2. `model_routing.md`
3. Skill instructions
4. User request

If guidance conflicts, `config.yaml` wins.

---

# Cost Philosophy

Default to the cheapest model capable of successfully completing the task.

Use GPT-5.5 only when reasoning quality materially impacts the outcome.

Prefer OpenRouter models whenever the task is primarily:

- Classification
- Categorization
- Summarization
- Formatting
- Documentation
- Reporting
- Administrative work

Premium reasoning should be reserved for:

- Game design
- Product strategy
- System architecture
- Complex debugging
- Major implementation decisions
- Economy balancing
- Monetization
- Roadmap planning

---

# Never Delegate

The following work must remain on GPT-5.5.

## Product & Design

- Feature prioritization
- Roadmap planning
- Product strategy
- Retention design
- Monetization decisions
- Economy balancing
- Progression balancing
- Event design
- New world design
- Reward structure design

## Technical

- Architecture reviews
- System design
- Major refactors
- Cross-system impact analysis
- Security-sensitive changes
- Production launch decisions

## Business

- Growth strategy
- Live-ops strategy
- Advertising strategy
- Long-term project direction

---

# Safe To Delegate

The following work should be delegated whenever practical.

## Qwen3 Coder

- Bug triage
- Feedback categorization
- Spreadsheet updates
- Commit summaries
- Changelog generation
- Session handoffs
- Documentation cleanup
- Issue reproduction analysis
- Git workflow assistance
- Project organization

## GPT-4.1 Mini

- Telegram summaries
- Daily reports
- Status updates
- Notifications
- Meeting summaries
- Progress digests

---

# Repo Is Source Of Truth

These skills are a routing layer.

Project knowledge lives in:

```text
~/projects/scraplands/ai/
```

Always refresh project documentation before beginning work:

```bash
scrapupdate
```

or

```bash
git pull
```

Do not duplicate project knowledge into skills.

Skills contain:

- Routing
- Workflow guidance
- Non-negotiables
- Operational procedures

Project knowledge belongs in the repository.

---

# Validation Checklist

Before completing a task:

- [ ] Correct skill loaded
- [ ] Correct model selected
- [ ] Delegation appropriate
- [ ] Project documentation refreshed
- [ ] No duplicated project knowledge created
- [ ] Changes consistent with current project state
- [ ] Output quality appropriate for chosen model

---

# Updating

When `ai/` or `AGENTS.md` changes:

1. Update repository documentation first.
2. Update skills only if routing or operational guidance changed.
3. Re-copy skills into Hermes.
4. Validate model routing behavior.

When model routing changes:

1. Update `config.yaml`
2. Update `model_routing.md`
3. Update this README if responsibilities changed

Keep all three synchronized.