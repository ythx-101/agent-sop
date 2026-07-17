# Roster protocol — discover, assign, propose

The roster is **discovered, not declared**. This skill never hardcodes agent
or model names; anyone adopting it has whatever agents they have, and a new
agent installed on the machine must join the pool with zero skill edits.
(Agent-first corollary: configuring the team is mechanical work, so it
belongs to agents; the human only vetoes.)

## 1. Discover

At task start the **orchestrator** — defined as the agent the human is
currently addressing, no election needed — runs:

```bash
python3 <skill>/scripts/discover-roster.py --probe --out <task-dir>/roster.json
```

- Without `--probe`: fast, reports what is installed and versioned.
- With `--probe`: each agent answers a minimal non-interactive call
  (60s timeout). This catches expired auth and provider outages *before*
  work is assigned (an agent whose provider is returning 503/429 shows up
  as `degraded` here instead of stalling a pipeline later).
- Probes run through an interactive shell (`bash -ic`) so they see the
  same profile-provided environment (auth tokens sourced in rc files) that
  a real dispatched pane gets; a bare subprocess can lack that env and
  report false degradation. If a probe still fails while a live
  interactive session of the same CLI is demonstrably working, the
  orchestrator investigates the environment difference before trusting
  either verdict, and may keep the already-alive session in a slot with
  the live session recorded as health evidence.
- The detection list inside the script is an extensible *probe list*, not a
  roster. Add a CLI name + probe recipe there once; it is then discovered
  forever. Do not add per-machine facts to it.

`roster.json` is a per-task artifact. Keep it in the task directory next to
the plan; reference it in the signoff packet so reviewers can see who did
what with which tier.

## 2. Assign slots by condition, never by name

Apply these rules to the `available` agents in roster.json (skip
`degraded` ones; note the skip in the roster proposal):

| Slot | Condition |
| --- | --- |
| orchestrator | The agent the human is addressing. Fixed by construction. |
| sole-writer | Highest-capability healthy agent that has (or is granted) write access to the target repo/config. Prefer `frontier` tier. |
| reviewer | Highest-capability healthy agent from a **different vendor** than the sole-writer. Cross-vendor independence is a hard preference — see the degradation ladder below. |
| scout / parallel workers | Cheapest healthy `fast`-tier agents. Multi-tier CLIs may supply these via model selection (a frontier CLI running its fast model is a valid scout). |

Tie-break deterministically: prefer the agent with the newer version, then
alphabetical. Determinism matters — the human should never be asked to
resolve a coin flip.

### Reviewer independence degradation ladder

When no healthy cross-vendor reviewer exists, degrade in this order and
**record the degradation level in the signoff packet**:

1. Different vendor (full independence) — the default.
2. Same vendor, different model tier (e.g. writer on frontier, reviewer on
   balanced) — partial independence.
3. Same model, fresh session with independent context — weakest; allowed
   only for low/medium-tier tasks, never for data/service/destructive.

## 3. Propose, then proceed (proposal-first gate)

Before any slotted work begins, the orchestrator compresses the outcome
into a 3–6 line roster proposal for the human:

```
roster: <n> found, <m> healthy (skipped: grok — provider 503)
writer:   claude (anthropic, frontier)
reviewer: codex (openai, frontier)  [cross-vendor ✓]
scouts:   pi→fast-provider, claude→fast-model
gates:    publish, deploy  (will return for approval at each)
```

The human replies with a veto or a one-word approval. Silence is not
approval. This replaces the human designing the team; it does not replace
the per-gate approvals in §5 of SKILL.md.

## 4. roster.json schema (per agent)

| Field | Meaning |
| --- | --- |
| `name` / `path` / `version` | The CLI as found on PATH. |
| `vendor` | API provider behind the CLI; `multi` = resolves per-config, orchestrator must read the CLI's own provider config when independence matters. |
| `tier` / `tiers_available` | Coarse capability class of the default model, and the classes reachable via model selection. |
| `health` | `available`, `degraded` (version/probe failure — reason in `notes`), or `unknown` (`--probe` was requested but no non-interactive probe recipe exists — verify manually before assigning). Missing CLIs are simply absent. |
| `probe_ms` | Round-trip of the live probe, when `--probe` was used. |
| `background_recipe` | Known launch mode for unattended panes (see SKILL.md §0 authorization). A human-readable note, not guaranteed-executable argv — the orchestrator adapts it to the pane. `null` = not yet established; establish and add it to the script before backgrounding that agent. |

## 5. Persistent agent memory (optional, Squad-inspired)

For long-running collaborations, an agent slot may keep an append-only
`<task-dir>/crew/<name>-history.md` of project-specific lessons. This is
per-project state, never skill state; the skill stays machine-agnostic.
