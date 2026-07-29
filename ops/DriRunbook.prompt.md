# DRI / On-Call Runbook

Generate an evidence-backed **DRI (Directly Responsible Individual) / on-call runbook** for a service. This prompt is **repository-independent**: it discovers *your* service's endpoints, dashboards, alerts, dependencies, and failure modes from the codebase and configuration, then produces a runbook a new on-call engineer can actually follow — grounded in real telemetry queries and real triggers, not generic advice.

> **Why this exists:** Every on-called service needs the same thing — a single page that says *what you own, how to check health, what the alerts mean, and what to do when common things break*. Reconstructing that from scratch each rotation is wasteful. This prompt turns it into a discover-once, fill-the-runbook workflow that stays specific to your service.

## INPUTS

- `ServiceName` (string, required): The service on-call covers.
- `Environments` (list, optional): Deployed environments and their monitoring targets (dashboards, App Insights / telemetry resources, hosts). If omitted, discover from config and mark unknowns **TBD — confirm**.
- `DashboardUrl` / `IcmUrl` (string, optional): Links to the health dashboard and the incident-management queue. If omitted, leave a **TBD — confirm** placeholder rather than inventing a URL.
- `OutputFile` (string, optional): Path for the runbook. Defaults to `docs/dri/dri-runbook.md`.

> Every URL, dashboard GUID, subscription ID, cluster, or resource name in the output **must** come from a provided input or discovered evidence. Never emit a real-looking link or ID you have not confirmed — mark it **TBD — confirm**.

## PRIMARY DIRECTIVE

Produce **one** runbook (`${input:OutputFile}`) that a new DRI can follow end-to-end:

1. **What you own** — the DRI's responsibilities and SLAs.
2. **Access & prerequisites** — every portal, dashboard, cluster, and permission needed, with how to request it.
3. **Daily health check** — a concrete, ordered walkthrough with normal-range thresholds and known-noise to ignore.
4. **Alert investigation** — what each configured alert means and the first steps when it fires.
5. **Common scenarios** — the recurring failure modes and their triage steps.
6. **Escalation & useful queries** — severity ladder plus ready-to-run telemetry queries.

Ground each section in real evidence: endpoints from route definitions, alerts from alert config, dependencies from the service's clients, failure modes from error-handling and prior incidents.

---

## PHASE 1 — Ownership & access

- **What you own** — list the DRI's duties: acknowledge/triage incidents within SLA, monitor the dashboard for reliability/error/exception anomalies, coordinate with dependent teams across service boundaries, perform rollbacks on bad deployments, and maintain the TSG.
- **Access & prerequisites** — a table of every resource the DRI needs (incident portal, metrics dashboard, telemetry store read access, cluster access, repo) with **how to get access** for each. Discover the real resources from config; mark any unknown link **TBD — confirm**.

---

## PHASE 2 — Daily health check

Write an **ordered** walkthrough the DRI performs each shift. For each dashboard page / view, give the concrete signal to read, the **normal range/threshold**, and the action if it deviates. Critically, capture **known noise to ignore** (e.g., transient throttling messages, a known-benign upstream exception) so the DRI doesn't chase false positives — discover these from prior incidents/TSG where available, and mark others **TBD — confirm**.

Include a real-time view (live metrics) link if one exists. End with the general rule: *anything not already documented as a known issue gets raised immediately.*

---

## PHASE 3 — Alert investigation

List the service's configured alerts (discover them from alert-rule config / infra). For each: **what it detects**, its **severity**, and the **first investigation steps** (which dashboard to cross-reference, how to confirm scope, how to spot a false positive and adjust thresholds). If the platform offers AI-assisted / one-click investigation, note it.

---

## PHASE 4 — Common scenarios

Document the recurring failure modes as short numbered playbooks. Derive them from the service's real dependencies and error paths (upstream API failures, data-store connectivity, event-processing lag, deployment failures/rollback, auth/permission revocation, rate limiting, model/LLM or other external-service outages). For each scenario, give the ordered checks and the resolution, including the exact user-visible error string where the code produces one.

---

## PHASE 5 — Escalation & useful queries

- **Escalation ladder** — a severity → action table (page secondary/lead for Sev1–2, business-hours investigation for Sev3, next-sprint triage for Sev4) aligned to your org's SLA.
- **Useful queries** — ready-to-run telemetry queries against the service's real store (recent exceptions by problem/message, request latency percentiles, error-rate by endpoint). Use the actual role/cloud names discovered in code; keep them copy-paste runnable.
- **Sub-pipeline monitoring** — if the service has a distinct secondary pipeline (e.g., an event/stream processor) with its own dashboard and alerts, give it its own triage subsection (per-alert first steps, stuck/lag handling, manual re-queue guidance).

---

## PHASE 6 — Assemble & verify

Write the runbook to `${input:OutputFile}` covering Phases 1–5 in order, with a header noting the service and last-updated date. Keep it scannable — tables for access/escalation, numbered steps for scenarios, fenced blocks for queries.

After writing, **verify**: every dashboard/portal link and ID is a provided input or **TBD — confirm** (no invented URLs or GUIDs); every alert and scenario maps to a real config/dependency in the codebase; every query uses real role/store names and runs as written; known-noise items are captured so the DRI won't chase false positives.

---

## WORKFLOW SUMMARY

Execute sequentially; present each phase as a trackable todo and finish each before moving on:

1. **Ownership & access** → duties + access table with how-to-request
2. **Daily health check** → ordered walkthrough with thresholds and known-noise to ignore
3. **Alert investigation** → per-alert meaning + first steps
4. **Common scenarios** → dependency/error-driven triage playbooks with real error strings
5. **Escalation & queries** → severity ladder + copy-paste telemetry queries (+ sub-pipeline)
6. **Assemble & verify** → the runbook file, every link/ID/query grounded or TBD

The final deliverable is a single runbook a fresh on-call engineer can execute from cold — specific to your service, with no invented links and no generic filler.
