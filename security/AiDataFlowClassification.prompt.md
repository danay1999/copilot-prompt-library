# AI Data-Flow & Sensitive-Data Classification

Generate an evidence-backed **AI data-flow and sensitive-data assessment** for a service that sends data to an LLM. This prompt is **repository-independent**: it traces *your* service's data from collection → prompt construction → model call → response/storage, classifies every input, and verifies that no sensitive data leaks through prompts, responses, logs, or caches — all grounded in real code, not assumptions.

> **Why this exists:** Security, privacy, and Responsible-AI reviews all ask the same thing of an AI feature: *what exactly does the model see, where does it go afterwards, and can anything sensitive escape?* This prompt turns that into a discover-once, trace-the-flow workflow. It pairs with `RaiCompliance.prompt.md`.

## INPUTS

- `ServiceName` (string, required): The AI service being assessed.
- `Feature` (string, optional): Scope the assessment to one AI feature/path (e.g., a specific endpoint) if the service has several. If omitted, cover every model-calling path.
- `OutputFile` (string, optional): Path for the assessment. Defaults to `docs/security/ai-data-flow-security.md`.

> Every host, cluster, table, endpoint, or component name in the output **must** come from discovered evidence. Never emit a real-looking value you have not confirmed in code/config — mark unknowns **TBD — confirm** and cite where the authoritative value lives.

## PRIMARY DIRECTIVE

Produce **one** assessment document (`${input:OutputFile}`) that:

1. Draws the **end-to-end data flow** — source data → collection/signals → assembly → model call → response handling → storage/cache — with the real component names.
2. **Classifies every input** the model receives (data category, source, sensitivity) and justifies the classification.
3. Documents the **platform data-processing guarantees** (training use, tenant isolation, encryption, abuse-monitoring retention) for the model in use.
4. Traces **response handling**: what is returned to callers, what is logged server-side, and what is persisted/cached — proving prompts and sensitive inputs do **not** leak.
5. Lists **sensitive-data controls** (secrets, PII), the **residual risks** honestly, and a **verification checklist** with evidence.

Ground every claim in a file path, config key, or query. An unverified boundary is a **residual risk**, not a control.

---

## PHASE 1 — Map the data flow & entry points

Enumerate the AI-calling entry points (HTTP/timer/event triggers) and draw the pipeline from source data through to response and storage. Produce:

- An **entry-point table** (function/handler, trigger, use case).
- A compact ASCII **data-flow diagram**: `source data → collect → assemble → model call → platform → response → storage/cache`.

Use the real component names discovered in code (the collector/"signal" layer, the assembler/chunker, the model processor, the response post-processors, the cache). Do not invent stages.

---

## PHASE 2 — Classify every input the model receives

For each distinct input the model sees, record: **input name**, **data collected**, **source** (source control, work-tracking API, telemetry store, cache, user upload…), and a **classification** (e.g., General / org-internal, Personal/PII, Customer/End-User Content, Confidential).

Then justify the classification and state the **boundary**: is any customer-provided or end-user data collected, or only org-authored engineering artifacts? Call out **free-form fields** (descriptions, comments, work-item text, transcripts) as a residual risk when they are **not** redacted — an author can paste arbitrary content, including secrets or personal data.

Produce a signal/input classification table plus a short justification.

---

## PHASE 3 — Prompt construction & platform guarantees

- **Prompt construction** — describe how collected inputs are assembled into the model request (chunking/templating), and confirm the **identity** used to call the model (managed identity vs. keys — cite it). Note any assembly behavior that matters for safety (e.g., whether untrusted content is delimited/labelled vs. concatenated).
- **Platform data-processing guarantees** — for the model platform in use, document: not used for training, not shared with other tenants/customers, encryption at rest and in transit (TLS version), and **abuse-monitoring retention** (how long prompts/completions may be stored, and whether opt-out applies). Cite the platform's data-privacy documentation.
- **Content filtering** — note whether platform content filtering provides an additional layer against prompt injection via malicious input.

---

## PHASE 4 — Response handling: return / log / persist

Prove that prompts and sensitive inputs do not escape. Produce a response-pipeline table (stage → component → action) and document three boundaries explicitly:

- **What is returned to callers** — structured results only? Confirm **no raw prompt or input data is echoed back**.
- **What is logged server-side** — metrics/metadata (token counts, sizes, correlation IDs) vs. content. Confirm **raw prompt/response content is NOT logged** in deployed environments. Flag any **development-only** tracer that writes raw content locally, and state the exact condition under which it is active (so it's clearly not on in production).
- **What is persisted / cached** — where model outputs are stored, the cache key, and the retention policy (or **TBD — confirm** if unknown). Note whether stored outputs are redacted.

Cite the file for each boundary (response builder, logger, cache/repository).

---

## PHASE 5 — Sensitive-data controls, residual risk & verification

- **Secrets** — is there pre-send secrets scanning on inputs? If not, state the compensating factors (inputs already in source control, upstream credential scanning, platform no-train guarantee) and the honest residual risk.
- **PII** — how is personal data handled per path? Where redaction exists, name the component and the categories it covers; where it does not, say so.
- **Error disclosure** — confirm caller-facing errors do **not** leak exception type/message, stack traces, or internal hostnames; cite the error-handling path. Recommend a regression test that asserts this if one is missing.
- **Verification checklist** — a table of requirements (inputs classified, no customer data collected, no training use, auth via managed identity, responses don't leak prompts, errors scrubbed) each with **Status + Evidence** (a real file path or config key).
- **Recommendations** — concrete, defense-in-depth follow-ups (e.g., pre-send secret check, confirm cache retention, monitor content-filter triggers, add an error-scrub regression test).

---

## PHASE 6 — Assemble & verify

Write the assessment to `${input:OutputFile}` with: the data-flow overview + entry points (Phase 1), input classification (Phase 2), prompt construction + platform guarantees (Phase 3), response handling (Phase 4), sensitive-data controls + residual risk + verification checklist (Phase 5), and a **Source References** table mapping each component to its file path.

After writing, **verify**: every stage/component name is real (discovered in code); every input has a classification and justification; every "does not leak" claim cites the enforcing file; every cluster/host/table value is discovered or **TBD — confirm**; residual risks are stated honestly rather than hidden.

---

## WORKFLOW SUMMARY

Execute sequentially; present each phase as a trackable todo and finish each before moving on:

1. **Map the flow** → entry-point table + data-flow diagram (real component names)
2. **Classify inputs** → per-input classification table + free-form-field residual-risk note
3. **Prompt construction & platform guarantees** → assembly, identity, no-train/isolation/encryption/abuse-monitoring
4. **Response handling** → returned / logged / persisted boundaries, each proven against code
5. **Controls, residual risk & verification** → secrets/PII/errors + evidence-backed checklist
6. **Assemble & verify** → the assessment file, every claim grounded, no invented names

The final deliverable is a single assessment that lets a reviewer see exactly what the model receives, where it goes, and why nothing sensitive escapes — with every boundary traced to code.
