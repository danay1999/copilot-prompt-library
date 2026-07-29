# Model-Upgrade Comparison (LLM-as-Judge)

Generate a **model-upgrade comparison** workflow for an AI service: before switching to a new model, replay *real* request payloads against both the current and the candidate model, then use an LLM judge to compare the outputs. This prompt is **repository-independent**: it discovers *your* service's request contract, payload source, and endpoints from the codebase, then produces a runnable comparison harness and a verdict report — so a model upgrade is a measured decision, not a leap of faith.

> **Why this exists:** Every AI service eventually faces a model upgrade (a new GPT/Claude/Gemini version, a cheaper deployment, a region move). "It looks fine in a couple of manual tests" is not evidence. This prompt turns model-upgrade validation into a repeatable *replay real payloads → compare A vs. B → judge → report* workflow you can run before every upgrade.

## INPUTS

- `ServiceName` (string, required): The AI service whose model is being upgraded.
- `ModelA` (label + endpoint, optional): The **current/baseline** model (e.g., `GPT-5.4 (INT)` → its endpoint). If omitted, discover the current endpoint from config.
- `ModelB` (label + endpoint, optional): The **candidate** model (e.g., `GPT-4.1 (Staging)` → its endpoint). If omitted, ask the user.
- `JudgeModel` (endpoint + deployment, optional): The LLM used as judge. If omitted, discover an available deployment and confirm.
- `PromptTypes` (list, optional): The request/prompt types to sample across (e.g., code-risk, summary, comments). If omitted, discover them from the request contract.
- `SampleSize` (int, optional): Payloads per prompt type (default 3).
- `OutputDir` (string, optional): Where results/report are written. Defaults to a timestamped local test-artifact directory.

> Every endpoint, deployment, cluster, or table in the output **must** come from a provided input or discovered evidence. Never invent an endpoint or deployment name — mark unknowns **TBD — confirm**. Model version labels drift; treat them as inputs, not constants.

## PRIMARY DIRECTIVE

Produce a **comparison harness + report** that:

1. Sources **real, recent request payloads** (not synthetic) representative of production traffic.
2. Sends **each payload to Model A and Model B** under identical conditions, **bypassing any cache**.
3. Uses an **LLM-as-judge** to compare the two responses on defined criteria and emit a verdict per payload.
4. Writes a **results artifact** (raw responses) and a **report** (verdicts + metadata, no raw responses), treated as **local artifacts** — never committed with production data.
5. Never runs by accident in CI (guard the harness so it's opt-in only).

Ground the harness in the service's real request/response contract so payloads round-trip through the actual pipeline.

---

## PHASE 1 — Source representative payloads

Pull the **most recent successful** request payloads from where the service records them (its telemetry/result store), then **sample down** to `SampleSize` payloads per prompt type across `PromptTypes`, so every prompt path is represented. Prefer a recent window (e.g., last 7 days) to reflect current traffic.

Discover the payload store/table and the request-contract shape from code. If payloads contain sensitive data, treat the results as local-only artifacts (see Phase 4) and do not commit them.

---

## PHASE 2 — Replay against both models

For each payload, call **Model A** and **Model B** with the **same** request body, concurrently. Critically:

- **Bypass the cache** — set the appropriate no-cache directive so you compare *fresh* generations, not a stored result.
- Use the correct **auth** for each endpoint (discover the credential the service/tests use; some endpoints reject certain credential types).
- Record latency per call so the report can flag large performance regressions.

---

## PHASE 3 — Judge the outputs

Send each `(payload, responseA, responseB)` triple to the **judge model** with a rubric. Define explicit, service-relevant criteria — e.g., correctness/faithfulness to the input, completeness, adherence to the required output schema, and absence of hallucinated or leaked content. Have the judge emit a **structured verdict** per payload: which response is better (or tie), per-criterion scores, and a short justification.

Keep the judge prompt itself in the harness so the rubric is reviewable and stable across runs.

---

## PHASE 4 — Report & guardrails

Write two artifacts to `${input:OutputDir}`:

- **Results (JSON)** — raw Model A / Model B responses per payload. *Local test artifact; may contain production-derived data — do not commit.*
- **Report (Markdown)** — per-payload verdicts, per-criterion aggregates, latency summary, and an overall recommendation (upgrade / hold / investigate). Contains verdicts + metadata, **no raw responses**.

Guardrails to bake in:

- **Opt-in only** — the harness must not run in CI by default (e.g., an ignore/skip attribute or an env-gate). Document how to enable it and to re-disable it after.
- **Prerequisites** — list what a run needs (auth/login, network/VPN to reach the endpoints, judge-model access).
- **Cost/runtime note** — state the rough runtime and that each payload incurs A + B + judge calls.

---

## PHASE 5 — Verify

Before finishing, verify: payloads are **real and sampled across all prompt types**; both models receive identical bodies with cache bypassed; the judge rubric is explicit and stored in the harness; results vs. report separation is correct (no raw responses in the committed report); the harness is CI-safe (opt-in); every endpoint/deployment/store is a provided input or **TBD — confirm** (nothing invented).

---

## WORKFLOW SUMMARY

Execute sequentially; present each phase as a trackable todo and finish each before moving on:

1. **Source payloads** → recent real requests, sampled N per prompt type
2. **Replay A vs. B** → identical body, cache bypassed, correct auth, latency captured
3. **Judge** → structured per-payload verdict against an explicit rubric
4. **Report & guardrails** → local results JSON + committed verdict report, opt-in/CI-safe, prereqs + cost noted
5. **Verify** → real payloads, fair comparison, rubric stored, artifacts separated, nothing invented

The final deliverable is a repeatable comparison you can run before any model upgrade to decide — with evidence from real traffic and a documented rubric — whether the new model is a safe, better, or worse choice than the current one.
