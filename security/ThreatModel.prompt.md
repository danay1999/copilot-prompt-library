# Service Threat Model Generation

Generate a comprehensive threat model for a software service. This prompt is **repository-independent**: it discovers your codebase first, then follows a structured pipeline — enumerate components → build a metamodel → generate data flow diagrams → perform STRIDE analysis → evaluate against your organization's security control catalog.

> **How to use:** Copy this file into your repo under `.github/prompts/` and invoke it with GitHub Copilot. Supply the inputs below. Everything is driven from your repository's real code — there are no hardcoded, service-specific assumptions.

## INPUTS

- `ServiceName` (string, required): The service being modeled (e.g., "MyService").
- `TargetScope` (string, optional): A specific subsystem to focus on (e.g., a named pipeline or subsystem). Defaults to the full service.
- `ControlCatalog` (string, optional): The security control catalog to evaluate against — a path, URL, or name (e.g., your organization's internal security baseline, a compliance tracker, OWASP ASVS, CIS Controls, NIST SP 800-53, or your cloud provider's public security benchmark). If omitted, discover the catalog the repository already tracks against, and otherwise fall back to the control families in Phase 4.
- `OutputDir` (string, optional): Directory to write output artifacts. Defaults to `docs/threat-model/<Month Year>` (e.g., `docs/threat-model/June 2026`).

If no `TargetScope` is provided, analyze the entire service.

> Control IDs and wording differ between organizations, and many catalogs are internal and non-public. Always source them from `${input:ControlCatalog}` — never reproduce a control list from memory, and never paste a non-public catalog into a shared or public repository.

## PRIMARY DIRECTIVE

Produce a threat model that includes:

1. A component enumeration and metamodel
2. Data flow diagrams (Mermaid) showing data movement between components
3. STRIDE threat analysis for each data flow
4. Evaluation against your security control catalog
5. Risk-ranked findings with mitigations

---

## PHASE 1 — Component Enumeration & Baseline Data

Enumerate all deployable units, service roles, hosted processes, and external integrations **in this repository**. Do not assume a particular stack — discover it.

For each, list:

- Every project/module that produces a deployable artifact (services, hosts, class libraries, containers).
- Every distinct hosting process or entry point (HTTP endpoints, timer/cron jobs, queue/event/stream consumers, CLIs, background workers).
- Every external service dependency (databases, REST APIs, message queues/event streams, blob/object storage, AI/LLM endpoints, internal or third-party services).
- Every internal communication mechanism between components (DI-wired services, message passing, pipelines).

### Generic layers to look for

Map your repository onto these layers (rename to match your codebase):

| Layer | What to look for |
| ----- | ---------------- |
| **Host / entry points** | Trigger and endpoint definitions, dependency-injection / service registration, base classes for shared send/receive logic |
| **Orchestration / business logic** | Core workflow layer, AI/LLM orchestration, caching, jobs, domain services |
| **Shared models & telemetry** | Cross-cutting models, telemetry/logging helpers, context abstractions, configuration loading |
| **Authentication** | Credential chains, delegated (on-behalf-of) flows, workload or managed identities, token exchange |
| **Data access** | Database/warehouse clients, parameterized queries, ingestion paths |
| **Integrations** | SDKs/clients for each external system the service talks to |
| **Prompt/template assets** (AI services) | Embedded prompt templates, template engines, prompt routing |

Output the enumeration as a Markdown section in `${input:OutputDir}/1-component-enumeration.md`.

---

## PHASE 2 — Data Flow Diagram (DFD) Generation

Using the component enumeration from Phase 1, create Data Flow Diagrams in Mermaid format.

### Diagram series (progressive depth)

1. **Diagram 1 — System Context (End-to-End)**: Complete core baseline. Every resource must have at least one numbered, grounded connection. No loose or isolated nodes.
2. **Diagram 2 — Runtime Data Flows**: API surfaces, message/event flows, pipeline data movement, prompt/LLM request-response (if applicable), database read/write paths.
3. **Diagram 3 — Authentication & Authorization**: AuthN/AuthZ flows as traceable paths — credential chains, delegated token flows, workload identity, token exchange.
4. **Diagram 4 — Trust Boundaries**: Service components within each trust zone (compute host, data stores, external APIs, AI endpoints) and cross-boundary communication.
5. **Diagram 5 — Data Storage & Retention**: Data at rest in each store, transient storage, caching layers, and data lifecycle (collection → processing → storage → retention → deletion).

### Data elements to track

For each data flow edge, annotate with:

- **Data classification** — use the labels from `${input:ControlCatalog}` or your organization's own data-classification scheme. If you have none, a generic scheme works: `[Public]`, `[Internal]`, `[Confidential]`, `[Personal/PII]`, `[CustomerContent]`, `[Credentials]`.
- **Data use** (e.g., `[Analytics]`, `[ServiceOperation]`, `[Caching]`, `[AuditLog]`)

Build a data-element table for **your** service (discover the real elements — the columns below are the shape to fill in, not example data):

| Data Element | Source | Destination | Classification |
| ------------ | ------ | ----------- | -------------- |
| ... | ... | ... | ... |

### Mermaid rendering rules

- Use `flowchart TB` (top-to-bottom vertical layout).
- Every `subgraph` must include `direction TB` immediately after the header.
- Data stores: cylinder shapes `[("label")]`.
- Trust boundaries: `subgraph` blocks with distinct styling.
- All resources must be labeled with a unique ID prefix per type (e.g., `PR1`, `CC2`, `D3`).
- All edges (connections) must be labeled with a separate sequential number (e.g., `1`, `2`, `3`).
- Resource IDs and edge numbers are independent sequences.
- Numbers must be consistent across diagrams (same resource = same ID).
- Example: `PR1 -->|"1. Token Request"| CC2` — `PR1` is the resource ID, `1` is the edge number.
- No `\n` in labels — use `<br/>` for line breaks.
- No `&` multi-target edges — separate lines for each target.
- No emoji, no `/` in labels (use `-` or `and`), no `#` (use `CSharp` or the language name).
- No parentheses in labels inside brackets (except the cylinder syntax `[("label")]` for data stores).
- Subgraph titles: plain ASCII in double quotes.
- Use `classDef` and `class` for a readable color scheme.

### Evidence table

At the bottom of each diagram, include a table:

| #   | Reason for inclusion | Source file(s) |
| --- | -------------------- | -------------- |

Source file references must be actual repository paths.

Output all diagrams in `${input:OutputDir}/2-data-flow-diagrams.md`.

---

## PHASE 3 — STRIDE Threat Analysis

For each data flow identified in Phase 2, perform a STRIDE analysis:

| Threat Category            | Question                                                      |
| -------------------------- | ------------------------------------------------------------- |
| **S**poofing               | Can an attacker impersonate a component or user in this flow? |
| **T**ampering              | Can data in transit or at rest be modified without detection? |
| **R**epudiation            | Can actions be performed without adequate logging/audit?      |
| **I**nformation Disclosure | Can sensitive data leak to unauthorized parties?              |
| **D**enial of Service      | Can this flow be disrupted or overwhelmed?                    |
| **E**levation of Privilege | Can an attacker gain higher permissions through this flow?    |

### Common service-specific threat considerations

Adapt these to your architecture — include the ones that apply and add your own:

- **Prompt injection** (AI services): Can untrusted content (user input, documents, tickets, diffs) manipulate LLM prompts or override system instructions?
- **Token leakage**: Are delegated tokens, workload-identity tokens, or database credentials exposed in logs, messages, or error responses?
- **Input poisoning**: Can crafted external input bias a decision, model output, or downstream processing?
- **Cross-tenant / cross-request data exposure**: Does any shared buffer, cache, or concatenation risk mixing data across requests or tenants?
- **Cache poisoning**: Can cache entries be manipulated or keyed incorrectly?
- **Message replay**: Can replayed queue/event messages cause duplicate processing or stale results?

### Output format

For each finding, provide:

| Field                   | Description                                                 |
| ----------------------- | ----------------------------------------------------------- |
| ID                      | `STRIDE-{category initial}-{number}` (e.g., `STRIDE-S-001`) |
| Threat                  | Description of the threat                                   |
| Affected flow           | Reference to DFD edge number                                |
| Category                | STRIDE category                                             |
| Severity                | Critical / High / Medium / Low                              |
| Likelihood              | High / Medium / Low                                         |
| Risk                    | Severity × Likelihood                                       |
| Existing mitigations    | Controls already in place                                   |
| Recommended mitigations | Additional controls needed                                  |
| Evidence                | Source file references                                      |

Output the STRIDE analysis in `${input:OutputDir}/3-stride-analysis.md`.

---

## PHASE 4 — Security Control Evaluation

Evaluate the service against `${input:ControlCatalog}`. For each control, assess status as: **SUPPORTED**, **PARTIAL**, **GAP**, or **UNKNOWN**.

### Sourcing the controls

Read the control IDs, titles, and wording from `${input:ControlCatalog}` itself — do not reproduce them from memory, and do not substitute a catalog from a different organization. If no catalog is supplied, discover the one the repository already tracks against (a compliance doc, an assessment tracker, or a security README); if there is none, evaluate against the generic control families below and say plainly that no authoritative catalog was used.

> **Do not copy a non-public control catalog into generated artifacts that will be shared publicly.** Cite controls by ID and link to the catalog instead of restating its contents. If the threat model itself is destined for a public repository, reference a public standard such as OWASP ASVS, CIS Controls, NIST SP 800-53, or your cloud provider's public security benchmark.

### Control families to cover

Whatever catalog you use, make sure the evaluation spans at least these families — map each to the catalog's own IDs:

| Family                     | What to assess                                                                       |
| -------------------------- | ------------------------------------------------------------------------------------ |
| **Isolation**              | Untrusted code and workloads isolated from the host platform and from each other      |
| **Network security**       | Baseline firewall/segmentation policy; private connectivity to privileged resources   |
| **Authentication**         | Service-to-service authentication; delegated vs. application identity; workload identity |
| **Authorization**          | Explicit permission checks on privileged operations; least privilege                  |
| **Data protection**        | Integrity protection, encryption in transit and at rest, key management               |
| **Secrets management**     | Secrets held in an approved store, never hardcoded, rotated, inventoried              |
| **Secure operations**      | Operator access path, production access tooling, pre-prod/production isolation        |
| **Logging & monitoring**   | Security-relevant events logged, retained, and alertable                              |

### Evidence rigor

- Perform targeted evidence collection for each control family.
- Use both code evidence and architecture evidence.
- Prefer PARTIAL when controls exist but full compliance proof is incomplete.
- Use UNKNOWN only when evidence is genuinely absent after targeted search.
- For each control, state whether the limiting factor is a **discovery gap** (missing evidence) or a **control gap** (missing implementation).

### Overall status rules

- **GAP** if one or more controls are GAP.
- **PARTIAL** if no GAP and one or more are PARTIAL.
- **UNKNOWN** if all are UNKNOWN.
- **SUPPORTED** only if all are SUPPORTED.

Output the evaluation in `${input:OutputDir}/4-security-controls-evaluation.md`.

---

## PHASE 5 — Summary & Risk Register

Compile a final summary:

1. **Executive summary** — Overall security posture in 3-5 sentences.
2. **Risk register** — All findings from the STRIDE analysis and control evaluation, ranked by risk (Critical → High → Medium → Low).
3. **Top 5 recommendations** — Highest-impact mitigations the team should prioritize.
4. **Appendix** — Links to all generated artifacts.

Output the summary in `${input:OutputDir}/5-threat-model-summary.md`.

---

## PHASE 6 — Review Walkthrough

Generate a guide for the team's threat-model review, so the generated artifacts become a reviewed threat model with owners rather than a document nobody checks.

Output the guide as `${input:OutputDir}/6-review-walkthrough.md` with these sections:

1. **Scope and assumptions** — what is in and out of scope, and every assumption the analysis relied on (e.g., "the gateway enforces authentication"), each marked for the owning team to confirm or reject.
2. **Diagram check** — for each trust boundary in Diagram 4, the components inside it and the flows that cross it, so reviewers can confirm the diagrams match the deployed system.
3. **Threat triage** — one row per STRIDE finding with a proposed status (**Mitigated**, **Needs work**, **Not applicable**, or **Accepted**), the evidence from Phase 3, and an empty owner column to fill in during the review.
4. **Open questions** — every UNKNOWN control and discovery gap from Phase 4, phrased as a question for the role that can answer it (service owner, platform team, security reviewer).
5. **Optional tool import** — if the team keeps threat models in a modeling tool (OWASP Threat Dragon, the Microsoft Threat Modeling Tool, or similar), a checklist mapping the Phase 1 components and Phase 2 flows onto that tool's element types. Do not hand-craft the tool's file format: list what to draw, and compare any threats the tool generates against Phase 3.

---

## WORKFLOW SUMMARY

Execute phases sequentially. Each phase builds on the prior phase's output:

1. **Component Enumeration** → `1-component-enumeration.md`
2. **Data Flow Diagrams** → `2-data-flow-diagrams.md`
3. **STRIDE Analysis** → `3-stride-analysis.md`
4. **Security Control Evaluation** → `4-security-controls-evaluation.md`
5. **Summary & Risk Register** → `5-threat-model-summary.md`
6. **Review Walkthrough** → `6-review-walkthrough.md`

Present each phase as a trackable todo. Complete each phase fully before proceeding to the next.
