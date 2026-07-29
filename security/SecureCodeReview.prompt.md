# Secure Code Review

Turn a pull-request review into a **high-signal security review**: prioritize the findings that would
actually block approval, suppress the noise that tooling already catches, and treat an established
security control as a repository invariant rather than a one-time task.

This prompt is **repository-independent**: the service, its risk areas, and its control catalog are
inputs or discovered from the repository, and every finding is anchored to a line in the diff.

> **Why this exists:** Reviewer fatigue comes from volume. Twenty style nits bury the one comment that
> matters, so the security regression ships. The other half of the problem is treating security work as
> *done*: once an assessment task is closed, the control it established is easy to weaken in a later PR
> that nobody flags. This prompt fixes both — a small number of high-confidence findings, and an
> explicit rule that a closed control is an invariant, not an optional extra.

## INPUTS

- `ChangeSet` (string, required): The diff to review — a PR number/URL, a branch comparison, or a patch.
- `ControlCatalog` (string, optional): Your organization's security control list (e.g., a secure-development
  control catalog, a compliance tracker, or an assessment status document). When present, **cite the control ID**
  on each security finding so the author can look it up. When absent, name the control in plain language.
- `RiskAreas` (list, optional): Service-specific invariants that a change could quietly break. If not
  supplied, derive them in Phase 1 — do not skip them.
- `ReviewBudget` (number, optional): Maximum findings to emit. Defaults to **5–10**.

## PRIMARY DIRECTIVE

**Prefer three high-confidence findings over twenty speculative ones** — but never let brevity become
partial coverage. Two rules that pull in opposite directions, both mandatory:

- **Review the whole diff in one complete pass.** Enumerate every changed file and inspect every hunk.
  Collect the full set of findings first, then emit them as **one consolidated review** — not two
  comments, then two more, then one. Finding a blocker in one file does not excuse skipping the rest.
- **Completeness is never volume.** Being thorough means not missing a real issue anywhere in the diff.
  It never means inventing low-value comments to look exhaustive. A clean review is a valid result.

When more findings exist than the budget allows, report Critical first, then High, then Medium. Do not
emit low-impact findings when more important ones already exist in the same pull request.

Before writing a finding, check whether a prior review comment already raised it. Do not withhold an
unrelated issue that is visible in the current diff.

---

## PHASE 1 — Establish the service's risk areas

Before reading the diff for defects, establish what this repository considers invariant. Derive from
`${input:RiskAreas}` when supplied, and otherwise from the repository itself:

- **Architecture invariants** — the patterns the codebase states must always hold (a single place where
  services are registered, a base class that owns telemetry and error handling, a required layering).
  Contributing guides, architecture docs, and agent/instruction files usually state these explicitly.
- **Auth and identity paths** — how the service authenticates callers and dependencies, and which role
  or scope checks gate each entry point.
- **Trust boundaries** — where attacker-influenced content enters (request bodies, webhooks, diffs,
  work items, build metadata, uploaded files) and where it is consumed.
- **Configuration model** — whether settings are layered or per-environment, since a setting added to
  one file only is a silent production gap when the files are not layered.
- **Established controls** — anything the `${input:ControlCatalog}` marks as complete. **A closed control
  is established, not optional.** Preserve it and flag any regression, even when its tracking item is Done.

State these back before reviewing. A finding that a change breaks an invariant is only credible if the
invariant was identified first.

---

## PHASE 2 — Prioritize (comment when confidence is high)

- **Correctness and logic bugs** — off-by-one, inverted conditionals, wrong async/await usage, unhandled
  null, swallowed exceptions, incorrect collection or query operations.
- **Security** — auth/authorization gaps, secrets in code or config, injection, unsafe deserialization,
  SSRF, missing input validation on externally reachable endpoints.
- **Concurrency and resource safety** — race conditions, a missing `await`, undisposed resources,
  blocking calls on async paths.
- **Data correctness** — cache-key and identity mistakes, incorrect or unparameterized queries,
  serialization round-trip issues.
- **Observability regressions** — a new execution path with no telemetry, errors without structured
  diagnostics, external calls without enough logging to diagnose a failure, missing correlation
  identifiers, or removal of existing telemetry without justification. **Treat these with the same
  priority as reliability regressions** — an undiagnosable failure in production is a defect.
- **Test gaps** — new public behavior or a bug fix with no corresponding test.
- **Unclear public API naming** — a new public or exposed type, member, or parameter whose name is
  misleading. Analyzers enforce casing but cannot judge whether a name conveys intent.

---

## PHASE 3 — Security control families

Treat a change that introduces or weakens any of these as **Critical/High**, and cite the control ID from
`${input:ControlCatalog}` when one exists.

### Injection and input validation

- **Query injection** — flag any query built by string concatenation or interpolation of user- or
  build-controlled data. Queries must use parameterized execution, never string building.
- **Input validation** — user, request, build, and config input must be validated or filtered before use.
  Flag externally reachable endpoints that trust request bodies or query parameters without validation.
- **Command injection** — flag user-controlled data reaching a shell or process invocation without strict
  validation.
- **SSRF** — flag outbound requests whose URL or host derives from user input without an allow-list. Any
  service that parses URLs out of incoming data must validate them against expected hosts.

### Secrets, certificates, and cryptography

- **No secrets in code or config** — flag hardcoded keys, tokens, connection strings, or passwords in
  source or settings files. Secrets belong in a managed secret store or a managed identity flow.
- **Approved algorithms only** — hashing must be SHA-256 or stronger. Flag MD5, SHA-1, and other weak or
  deprecated algorithms. Keys must be single-purpose; flag reuse across algorithms or purposes.
- **Transport security** — flag disabled certificate validation or downgraded TLS.
- **Token handling** — bearer tokens belong in the `Authorization` header only, never in cookies or URLs.

### Identity, authorization, and least privilege

- **Approved non-people identities** — new service-to-service auth should use managed identity or the
  service's established credential provider; flag ad-hoc credential patterns.
- **Preserve the auth path** — flag changes that broaden access, bypass a role or scope check, or blur the
  distinction between acting as the calling user and acting as the application.
- **Least privilege** — flag new permissions, scopes, or role grants broader than the change requires.

### Error disclosure

- Responses must not leak stack traces, exception detail, internal hostnames, or debugging interfaces.
  Flag returning a raw exception message to a caller.
- Flag dangling or unvalidated DNS references that could enable takeover.

### AI and LLM security

- **Prompt-injection resistance** — model inputs are attacker-influenced (user text, diffs, documents,
  work items). Flag prompt construction that lets untrusted content override system instructions.
- **Sensitive-data protection** — flag AI paths that log, cache, or persist secrets, tokens, or sensitive
  customer data. Do not persist fully rendered prompts.
- **AI telemetry** — security-relevant AI operations should be logged with sensitive values scrubbed.
  Flag both missing logging and over-sharing logging on model calls.

### Dependency and scanning hygiene

- Flag a new vulnerable or unpinned dependency, and code matching a pattern the repository's scanners
  already flag elsewhere. Do not add to an existing alert backlog.
- Prefer fixing forward: when a change touches code near an existing alert, note the chance to remediate
  rather than propagate the pattern.

---

## PHASE 4 — Suppress the noise

Do **not** comment on:

- Style, formatting, indentation, or mechanical naming/casing — linters and analyzers enforce these, and
  many repositories fail the build on them already. (Exception: a genuinely misleading **public** API name.)
- Documentation-comment presence on internal or private members, when the repository only requires it on
  public surface.
- Dependency versions when the repository uses central version management.
- Subjective preferences, restating what the code obviously does, or praise-only comments.
- Pre-existing issues in code the change does not touch.

---

## PHASE 5 — Write the review

- **Anchor** each comment to the specific line, and state the **concrete fix**, not just the problem.
- **Assign a severity** — Critical / High / Medium — so the author can triage instantly.
- **Cite the evidence**: the control ID, the invariant from Phase 1, or the exact code path that makes it
  a defect. A finding without evidence is a guess.
- If the change is safe, say so in a brief overall summary. **Do not manufacture line comments to appear
  thorough.**

---

## WORKFLOW SUMMARY

Execute in order; present each phase as a trackable todo:

1. **Risk areas** → derive the repository's invariants, auth paths, trust boundaries, and established controls
2. **Prioritize** → correctness, security, concurrency, data, observability, test gaps, public naming
3. **Security families** → injection/validation, secrets/crypto, identity/least privilege, error disclosure, AI, dependencies
4. **Suppress** → drop anything tooling already enforces or that restates the obvious
5. **Write** → one consolidated review, line-anchored, severity-tagged, evidence-cited, within budget

The deliverable is a review a human would have written on their best day: complete over the diff, short
on the page, and impossible to dismiss as noise.
