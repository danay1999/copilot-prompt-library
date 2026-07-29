# Responsible AI (RAI) Security & Compliance Posture

Generate an evidence-backed **Responsible AI (RAI) security & compliance posture** document for a service that uses an LLM / generative-AI model. This prompt is **repository-independent**: it discovers *your* service's AI usage, controls, and identity from the codebase and configuration, then produces a service-specific posture doc grounded in real evidence — not a generic checklist.

> **Why this exists:** Security and Responsible-AI reviews ask the same questions of every AI service — what does the model see, what stops it producing harmful or leaking content, how is access controlled, and how do you turn it off in an incident. This prompt turns that into a discover-once, ground-in-code workflow.

## INPUTS

- `ServiceName` (string, required): The AI service being assessed.
- `AiPlatform` (string, optional): The model host/platform (e.g., Azure OpenAI, OpenAI, Bedrock, a self-hosted model). If omitted, discover it from the AI client configuration in code/config.
- `WorkItemUrl` (string, optional): The tracking item for the Responsible-AI requirement, to cite at the top.
- `OutputFile` (string, optional): Path for the posture doc. Defaults to `docs/security/rai-compliance.md`.

> Any host, endpoint, deployment name, content-filter threshold, or role name in the output **must** be substituted from discovered evidence. Never emit a real-looking value you have not confirmed in code/config — mark it **TBD — confirm** and cite where the authoritative value lives (e.g., `appsettings.{env}.json`).

## PRIMARY DIRECTIVE

Produce **one** posture document (`${input:OutputFile}`) that:

1. Enumerates the service's **AI use cases** (model, input, output) from code — one row per distinct LLM/embedding call site.
2. Documents the **layered RAI controls** actually in place (platform content filtering, application constraints, data protection, access control), each grounded in a file path.
3. Assesses residual **risks** with an honest status (mitigated / partial / accepted), not aspirational claims.
4. Documents the **incident response** path and a concrete **kill switch** (how to stop AI processing, including cached responses).
5. States the **AI bug bar** used to triage AI-specific issues and a **compliance action list** (done / pending).

Ground every claim in evidence. A control you cannot point to in code or config is **not** a control — record it as a gap, not a mitigation.

---

## PHASE 1 — Enumerate AI use cases

Find every place the service calls a model (chat/completion and embeddings). For each, record: **use case**, **model/deployment** (from config, not guessed), **input** (what data is sent), and **output** (what comes back, and whether it is consumed as structured data or surfaced verbatim).

Produce an "AI Use Cases" table. Note that authoritative model/deployment IDs live in per-environment config — cite the config key rather than pinning a version that will drift.

---

## PHASE 2 — Document the layered controls (grounded in code)

For each layer, state what is enforced and **cite the file/config**. Do not claim a layer exists because the platform *could* provide it — confirm it.

- **Layer 1 — Platform content filtering.** Are the AI platform's built-in harm filters (violence/hate/sexual/self-harm), jailbreak/prompt-shield, and protected-material filters enabled? At what severity? Is abuse monitoring on or opted-out? Cite where this is verified (platform config / portal export). Produce a filter table with the verified thresholds.
- **Layer 2 — Application-level constraints.** Is model output consumed as **structured** data (schema/JSON) rather than surfaced free-form? Are safety/instruction snippets injected into prompts? Be precise about **which** prompt paths inject them and which do **not** — a partially-covered control is a partial control.
- **Layer 3 — Data protection.** Is there input/output redaction (PII, secrets)? To **which** feature/path does it apply, and which paths have **none**? Name the redaction component and the data classification of each input.
- **Layer 4 — Access control.** How is the AI endpoint authenticated/authorized (in code, not just at the host/gateway layer)? What identity does the service use to reach the model (managed identity vs. keys)? Call out any endpoints that are anonymous-in-code even if a gateway sits in front, and cross-reference the threat model if one exists.

---

## PHASE 3 — Risk assessment

Produce a risk table: **Risk → Mitigation → Status**. Cover at minimum: harmful-content generation, PII/secret leakage in AI outputs, prompt injection via attacker-influenced input (PR text, diffs, work items, transcripts), unauthorized AI access, training-data exposure, and model hallucination. Use honest statuses:

- ✅ **Mitigated** — a control you cited in Phase 2 fully addresses it.
- ⚠️ **Partial / Accepted** — platform-only coverage, an un-redacted path, or an inherent LLM risk. Say *why* and reference the tracking item / threat-model entry.

Do not upgrade a partial control to "mitigated." Reviewers trust an honest ⚠️ far more than an unsupported ✅.

---

## PHASE 4 — Incident response & kill switch

Document:

- **Incident response** — your standard incident-management and severity process, plus the **AI-specific triggers** that warrant an incident (content-filter bypass, prompt injection that manipulates outputs, unexpected prompt/response exposure, anomalous model usage/cost).
- **Kill switch** — the concrete way(s) to stop AI processing, ranked by completeness. Distinguish stopping **new** model calls (disable the deployment / revoke the identity's role) from stopping **all** AI responses including **cached** ones (stop the host app or purge the cache). If there is no application-level "AI off" flag, say so and note it as optional hardening.

---

## PHASE 5 — AI bug bar & compliance actions

- **AI bug bar** — state how AI-specific issues are triaged (the Microsoft AI severity classification / your org's equivalent) and where they are tracked (threat model, security backlog).
- **Compliance actions** — a checklist split into **Completed** (each with evidence: a file, workflow, or merged PR), **Pending — resolvable by documentation**, and **Pending — requires team/process decision** (external actions like OneRAI registration or APIM onboarding). Be explicit about which pending items are *not* solvable in this document.

---

## PHASE 6 — Assemble & verify

Write the posture doc to `${input:OutputFile}` with: a short overview, the use-case table (Phase 1), the layered controls (Phase 2), the risk table (Phase 3), incident response + kill switch (Phase 4), AI bug bar + compliance actions (Phase 5), a compact **data-flow** sketch (source → optional redaction → prompt construction → model → structured consumption → response), and a **References** section listing the cited source files.

Add a **source-of-truth caveat** near the top: where the doc cites specific configuration (deployments, endpoints, filter thresholds, auth levels), the authoritative source is the referenced code/config and threat model, and the doc may lag — verify against the cited sources.

After writing, **verify**: every control traces to a file/config path or is marked as a gap; every model/host/deployment value is discovered or **TBD — confirm**; no invented endpoints, IDs, or thresholds remain; every ✅ has cited evidence.

---

## WORKFLOW SUMMARY

Execute sequentially; present each phase as a trackable todo and finish each before moving on:

1. **Enumerate AI use cases** → use-case table (model/input/output, from config)
2. **Layered controls** → platform filtering, app constraints, data protection, access control — each cited
3. **Risk assessment** → honest mitigated / partial / accepted table
4. **Incident response & kill switch** → triggers + a concrete way to stop new *and* cached AI responses
5. **AI bug bar & compliance actions** → triage process + completed/pending checklist
6. **Assemble & verify** → the posture file, evidence-grounded, no invented values

The final deliverable is a single, honest RAI posture document a reviewer can trust because every claim points at real code, config, or an explicitly-tracked gap.
