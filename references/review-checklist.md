# Independent Review Checklist

Use this checklist for an independent read-only review in a new session.

Return:

`VERDICT: PASS | NEEDS_CHANGES | BLOCKED`

`BLOCKING: <required fixes with paths/lines, or none>`

`SUGGESTED: <non-blocking improvements, or none>`

`EVIDENCE: <files, lines, commands, logs, or URLs checked>`

## Evidence

- [ ] The approved plan and acceptance criteria were read completely.
- [ ] Baseline Git status and changed paths are known.
- [ ] Every important claim has a file, line, command, log, or URL evidence.
- [ ] Unknowns and assumptions are named.
- [ ] If a prior session exceeded 60% context, its evidence and status were persisted before review continued in this fresh session.

## Scope and correctness

- [ ] Every required behavior is implemented.
- [ ] Out-of-scope features were not added.
- [ ] Empty, invalid, duplicate, retry, and failure cases are handled.
- [ ] Existing data and API contracts remain compatible.
- [ ] An optimization change includes quantified evidence for both its benefit and its cost or regression side; one-sided improvement claims are not accepted.

## Safety and privacy

- [ ] No secrets, tokens, private URLs, or personal raw data entered source control.
- [ ] Authentication and authorization are preserved.
- [ ] User-supplied paths, Markdown, and URLs are constrained safely.
- [ ] Signoff packets and previews are Markdown-only in v1; HTML remains disabled until a sandboxed iframe and an isolated origin both exist.
- [ ] Private content systems remain private; public exports whitelist only deliberately publishable content.

## Ownership and signoff

- [ ] The task record declares capability assignments plus `writer=<agent> repo=<path>`.
- [ ] The control-plane pane label (when a pane-based control plane is used) matches the declared task, slot, and `writer/ro` mode.
- [ ] Exactly one writer owns each repository, worktree, or production configuration.
- [ ] Signoff data is stored separately, never in a production database or a public export.
- [ ] Agents initialized signoff status only as `pending`.
- [ ] Any recorded status transition is explicitly human-authorized and includes the human's verbatim signoff statement; no agent-authored decision is present.

## Operations

- [ ] Writers and readers have clear ownership.
- [ ] Locks prevent overlapping jobs where needed.
- [ ] Failure leaves a recoverable state.
- [ ] Backup and rollback steps are documented.
- [ ] Service changes followed backup → config test → separate §4 approval → deploy/restart → health check → log confirmation → report.
- [ ] A failed deployment stopped further rollout and completed or clearly reported rollback checks.

## Verification

- [ ] Syntax/build/type/lint checks appropriate to the project pass.
- [ ] Focused tests pass.
- [ ] API/UI smoke checks pass.
- [ ] Database and receipt invariants are checked.
- [ ] Remaining risks are explicit.
