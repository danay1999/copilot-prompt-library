# Service Threat Model Generation

Generate a comprehensive threat model for a software service. This prompt is **repository-independent**: it discovers your codebase first, then follows a structured pipeline — enumerate components → build a metamodel → generate data flow diagrams → perform STRIDE analysis → evaluate against your organization's security control catalog.

> **How to use:** Copy this file into your repo under `.github/prompts/` and invoke it with GitHub Copilot. Supply the inputs below. Everything is driven from your repository's real code — there are no hardcoded, service-specific assumptions.

## INPUTS

- `ServiceName` (string, required): The service being modeled (e.g., "MyService").
- `TargetScope` (string, optional): A specific subsystem to focus on (e.g., a named pipeline or subsystem). Defaults to the full service.
- `ControlCatalog` (string, optional): The security control catalog to evaluate against — a path, URL, or name (e.g., your organization's internal security baseline, a compliance tracker, CIS Controls, NIST SP 800-53, or the public [Microsoft Cloud Security Benchmark](https://learn.microsoft.com/en-us/security/benchmark/azure/overview)). If omitted, discover the catalog the repository already tracks against, and otherwise fall back to the control families in Phase 4.
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
| **Authentication** | Credential chains, on-behalf-of (OBO) flows, managed identity, token exchange |
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
3. **Diagram 3 — Authentication & Authorization**: AuthN/AuthZ flows as traceable paths — credential chains, OBO token flow, managed identity, token exchange.
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
- **Token leakage**: Are OBO tokens, managed identity tokens, or database credentials exposed in logs, messages, or error responses?
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

> **Do not copy a non-public control catalog into generated artifacts that will be shared publicly.** Cite controls by ID and link to the catalog instead of restating its contents. If the threat model itself is destined for a public repository, reference a public benchmark such as the [Microsoft Cloud Security Benchmark](https://learn.microsoft.com/en-us/security/benchmark/azure/overview), CIS Controls, or NIST SP 800-53.

### Control families to cover

Whatever catalog you use, make sure the evaluation spans at least these families — map each to the catalog's own IDs:

| Family                     | What to assess                                                                       |
| -------------------------- | ------------------------------------------------------------------------------------ |
| **Isolation**              | Untrusted code and workloads isolated from the host platform and from each other      |
| **Network security**       | Baseline firewall/segmentation policy; private connectivity to privileged resources   |
| **Authentication**         | Service-to-service authentication; delegated vs. application identity; managed identity |
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
2. **Risk register** — All findings from STRIDE and principles evaluation, ranked by risk (Critical → High → Medium → Low).
3. **Top 5 recommendations** — Highest-impact mitigations the team should prioritize.
4. **Appendix** — Links to all generated artifacts.

Output the summary in `${input:OutputDir}/5-threat-model-summary.md`.

---

## PHASE 6 — Microsoft Threat Modeling Tool File (.tm7)

Generate a `.tm7` file for the [Microsoft Threat Modeling Tool](https://learn.microsoft.com/en-us/azure/security/develop/threat-modeling-tool).

> **Important:** The `.tm7` format uses .NET `DataContractSerializer` with an embedded `KnowledgeBase` that cannot be hand-crafted. Generation requires a **baseline `.tm7` file** — a blank model saved from TMT against a chosen `.tb7` template. Automate the injection with a small script (see below).

### One-time baseline setup

1. Download a `.tb7` template (e.g., from [PatrickGallucci/threat-model-templates](https://github.com/PatrickGallucci/threat-model-templates)).
2. Open Microsoft Threat Modeling Tool → **File → Create A Model** → select the `.tb7`.
3. Save the empty model as `docs/threat-model/baseline.tm7`.

### Automated generation

Create/use a generation script (e.g., `docs/threat-model/New-ServiceThreatModel.ps1`) that injects your components into the baseline:

```powershell
.\docs\threat-model\New-ServiceThreatModel.ps1 -BaselineTm7 docs\threat-model\baseline.tm7
```

By default target a subfolder named after the current month and year (e.g., `docs/threat-model/June 2026`). To target a specific period, pass an explicit `-OutputDir`.

The script should read the Markdown artifacts from Phase 1 (component enumeration) and:

- Replace the `DrawingSurfaceList` with your components (trust boundaries, processes, data stores, external interactors) laid out in a grid.
- Clear `ThreatInstances` for manual review in TMT (auto-generated threats from the template's STRIDE rules regenerate on open).
- Update `MetaInformation` with your service-specific title, description, and assumptions.

Output: `${input:OutputDir}/<ServiceName>-ThreatModel.tm7`

---

## PHASE 7 — Threat Modeling Tool Walkthrough Guide

Generate a step-by-step guide for completing the threat model review in the Microsoft Threat Modeling Tool. This guide bridges the gap between the generated `.tm7` file and a finished, reviewed threat model.

Output the guide as `${input:OutputDir}/6-tmt-walkthrough.md` with the following sections:

### 1. Opening the Model

- Exact file path to open
- What template (`.tb7`) was used
- What you should see on the canvas (count of shapes, boundary boxes)

### 2. Understanding the Shapes

Explain the visual language with a reference table (examples are generic — substitute your own components):

| Shape          | TMT Type                    | Meaning                         | Examples                                |
| -------------- | --------------------------- | ------------------------------- | --------------------------------------- |
| Circle/Ellipse | Process (GE.P)              | Code that runs                  | HTTP endpoint, worker, processor        |
| Rectangle      | External Interactor (GE.EI) | Outside system or user          | End user, third-party API               |
| Parallel Lines | Data Store (GE.DS)          | Persistent or transient storage | Database, queue, cache, Key Vault       |
| Dashed Box     | Trust Boundary (GE.TB.B)    | Security perimeter              | Compute host, external APIs             |

### 3. Arranging the Diagram

For each trust boundary, list:

- The boundary name
- Which components belong inside it (pulled from Phase 1)
- Drag instructions: "Move [component] inside the [boundary] box"

### 4. Drawing Data Flows

For each data flow from Phase 2 Diagram 2, provide a checklist entry:

```
[ ] Source: [component name] → Target: [component name]
    Label: [description]
    Data Classification: [your scheme's label — see Phase 2]
    How: Right-click on source shape → drag arrow to target → set properties
```

Group the checklist by trust boundary crossing (flows within a boundary vs. flows crossing boundaries — the latter generate STRIDE threats).

### 5. Reviewing Auto-Generated Threats

Explain:

- Click the **magnifying glass icon** (Analysis View) in the toolbar.
- TMT auto-generates threats for every data flow that crosses a trust boundary.
- For each auto-generated threat, set the status:
  - **Mitigated** — if the control exists (reference Phase 3 `ExistingMitigations` column).
  - **Not Started** — if it needs work (reference Phase 3 `Recommended Mitigations`).
  - **Not Applicable** — if the threat doesn't apply to this architecture.

### 6. Adding Custom Threats

List each STRIDE finding from Phase 3 that TMT won't auto-generate (service-specific threats like prompt injection, query injection, token leakage). For each:

```
Threat ID: STRIDE-T-001
Title: <short title>
Category: <STRIDE category>
Priority: <Critical/High/Medium/Low>
Affected flow: <source> → <target>
How to add: Click "Add Threat" in Analysis View → fill in Title, Category, Description, Priority
```

### 7. Saving and Exporting

- **Save** the model (File → Save) — this preserves diagram + threats in the `.tm7`.
- **Export report** (Reports → Create Full Report → Save Report) — generates an HTML summary for stakeholders.
- Commit both the `.tm7` and the HTML report to the dated subfolder.

---

## WORKFLOW SUMMARY

Execute phases sequentially. Each phase builds on the prior phase's output:

1. **Component Enumeration** → `1-component-enumeration.md`
2. **Data Flow Diagrams** → `2-data-flow-diagrams.md`
3. **STRIDE Analysis** → `3-stride-analysis.md`
4. **Security Principles** → `4-security-principles-evaluation.md`
5. **Summary & Risk Register** → `5-threat-model-summary.md`
6. **Threat Modeling Tool File** → `<ServiceName>-ThreatModel.tm7`
7. **TMT Walkthrough Guide** → `6-tmt-walkthrough.md`

Present each phase as a trackable todo. Complete each phase fully before proceeding to the next.
