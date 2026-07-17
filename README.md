# agent-sop

A human-gated, capability-slotted collaboration workflow (SOP) for coding agents.

[中文说明 →](README.zh.md)

The goal is not to make agents more autonomous — it is to pick the right process weight for each risk level, so that work stays traceable, reviewable, and signable without small tasks drowning in ceremony.

High-risk work follows the full auditable sequence:

```text
research → plan → human approval → implementation → independent review
        → verification → signoff packet → human signoff → deploy
```

Low-risk work runs a deliberately lighter path. Tiers and boundaries are defined in `SKILL.md` §1.1.

## How it works

```mermaid
flowchart TD
  subgraph DISC["🔍 Discovery"]
    direction TB
    A([Task start]) --> B[discover-roster.py --probe]
    B --> C[Slots by condition, not name]
  end

  subgraph TEAM["💜 Team"]
    direction TB
    C --> D[sole-writer: strongest + write]
    C --> E[reviewer: strongest, other vendor]
    C --> F[scouts: cheapest fast tier]
    D & E & F --> G[Roster proposal]
  end

  subgraph PIPE["⚙️ Pipeline"]
    direction TB
    G --> H[[HUMAN: approve / veto roster]]
    H -->|veto| C
    H -->|approve| I[Plan]
    I --> J[[HUMAN: approve plan]]
    J --> K[Sole-writer implements]
    K --> L[Cross-vendor independent review]
    L --> M[Verification]
    M --> N[Signoff packet]
    N --> O[[HUMAN: signoff]]
  end

  subgraph SHIP["🚀 Ship"]
    direction TB
    O --> P[Deploy]
    P --> Q([Agents never self-serve publish or deploy])
  end

  classDef startEnd fill:#0EA5E9,stroke:#0369A1,stroke-width:2px,color:#fff,rx:12,ry:12
  classDef discover fill:#38BDF8,stroke:#0284C7,stroke-width:2px,color:#0C4A6E
  classDef agent fill:#34D399,stroke:#059669,stroke-width:2px,color:#064E3B
  classDef proposal fill:#86EFAC,stroke:#16A34A,stroke-width:2px,color:#14532D
  classDef plan fill:#6EE7B7,stroke:#0D9488,stroke-width:2px,color:#134E4A
  classDef work fill:#4ADE80,stroke:#15803D,stroke-width:2px,color:#14532D
  classDef review fill:#2DD4BF,stroke:#0F766E,stroke-width:2px,color:#fff
  classDef verify fill:#14B8A6,stroke:#0F766E,stroke-width:2px,color:#fff
  classDef packet fill:#5EEAD4,stroke:#0D9488,stroke-width:2px,color:#134E4A
  classDef human fill:#FBBF24,stroke:#C2410C,stroke-width:4px,color:#7C2D12
  classDef deploy fill:#F472B6,stroke:#BE185D,stroke-width:3px,color:#fff
  classDef finale fill:#EC4899,stroke:#9D174D,stroke-width:3px,color:#fff

  class A startEnd
  class B,C discover
  class D,E,F agent
  class G proposal
  class H,J,O human
  class I plan
  class K work
  class L review
  class M verify
  class N packet
  class P deploy
  class Q finale

  style DISC fill:#E0F2FE,stroke:#7DD3FC,stroke-width:2px,color:#0C4A6E
  style TEAM fill:#EDE9FE,stroke:#C4B5FD,stroke-width:2px,color:#5B21B6
  style PIPE fill:#ECFDF5,stroke:#6EE7B7,stroke-width:2px,color:#065F46
  style SHIP fill:#FDF2F8,stroke:#F9A8D4,stroke-width:2px,color:#9D174D
```

## Design principles

- **Agent-first.** Skills are operated by agents, not hand-configured by humans. The skill guides an agent to detect its environment, write its own configuration, and ask the human only for decisions. A step that requires a human to edit files by hand is a design bug.
- **Discovered roster, never a hardcoded one.** At task start the orchestrator runs `scripts/discover-roster.py --probe` to find the coding-agent CLIs actually installed and healthy on the machine, then assigns capability slots **by condition, never by name** (see `references/roster-protocol.md`). Install a new agent CLI and it joins the pool on the next run, with zero skill edits.
- **Capability slots, not fixed roles.** `orchestrator`, `sole-writer`, `reviewer`, `scout` — exactly one writer per repo at a time; reviewers are read-only and, whenever possible, from a **different vendor** than the writer (independence degradation ladder documented and recorded when full independence is unavailable).
- **Humans own decisions; gates are structural.** Publish/deploy/data-write steps are never self-served by an agent. The orchestrator splits dispatched work at every gate; approval is explicit — silence is never approval. Signoff status can only be set to `approved` by a human, and agents recording it must quote the human verbatim.
- **Claims require evidence.** "Tests passed" without commands and captured output is treated as unverified. Reviewers re-run security-relevant checks instead of trusting the writer's summary.

## Files

- `SKILL.md` — the workflow itself (English), written to be loaded by an agent as a skill.
- `references/roster-protocol.md` — roster discovery, condition-based slot assignment, reviewer-independence ladder, `roster.json` schema.
- `references/review-checklist.md` — independent review checklist with a reusable VERDICT/BLOCKING/SUGGESTED/EVIDENCE contract.
- `scripts/discover-roster.py` — agent CLI discovery with optional live health probes (catches expired auth and provider outages *before* work is assigned).
- `templates/signoff-packet.md` — Markdown signoff packet template (Chinese; structure is language-neutral).

## Install

Symlink (or copy) this directory into your agent's skills directory, e.g.:

```bash
ln -s /path/to/agent-sop ~/.claude/skills/sop
```

Any agent runtime that loads Markdown skills works the same way; the workflow itself is agent-agnostic.

## Provenance

This workflow is used in production by its authors, and it was used to produce itself: the roster-discovery redesign and this public release each ran through the full pipeline — plan, sole-writer implementation, cross-vendor independent review, verification, signoff — before shipping.

## License

MIT — see [LICENSE](LICENSE).
