# Privacy & Data Inventory

Generate an evidence-backed **privacy & data inventory** for a feature or service that collects, processes, stores, or shares data. This prompt is **repository-independent**: it discovers *your* feature's data elements from the codebase — every source, in-memory transform, permanent store, and outbound share — classifies each, and produces the inventory a privacy review (e.g., a data-use request or privacy impact assessment) needs. Every row is grounded in real code, not a generic template.

> **Why this exists:** A privacy review asks for a complete inventory of *every* data element a feature touches: where it comes from, how it's classified, whether it's persisted, and who it's shared with. Reconstructing that by hand is slow and error-prone. This prompt turns it into a discover-once, trace-each-element workflow that stays honest by citing the source code for every row.

## INPUTS

- `FeatureName` (string, required): The feature or service whose data is being inventoried.
- `ClassificationTaxonomy` (string, optional): The classification scheme to use (e.g., *customer content*, *account & identity data*, *service-generated data*, *support data*; or your organization's own scheme). If omitted, use that four-bucket default and note that it can be swapped for whichever taxonomy your privacy reviewers expect.
- `WorkItemUrl` (string, optional): The privacy-review / Data-Use-Request tracking item to cite at the top.
- `OutputFile` (string, optional): Path for the inventory. Defaults to `docs/privacy-data-inventory.md`.

> Every service ID, cluster, table, resource ID, or endpoint in the output **must** come from discovered evidence. Never emit a real-looking identifier you have not confirmed in code/config — mark unknowns **TBD — confirm** and cite where the authoritative value lives.

## PRIMARY DIRECTIVE

Produce **one** inventory document (`${input:OutputFile}`) that accounts for **every** data element the feature touches across its lifecycle:

1. Data **collected from external/upstream sources** (APIs, event notifications, upstream stores).
2. Data **processed in-memory** only (never persisted as raw).
3. Data **stored permanently** (databases, tables, blobs, caches) with retention.
4. Data **shared or transferred** outbound (to a model, another service, a downstream store).
5. A top-level **classification summary**, the **data subjects**, and the **data-use** purpose.

Every data element gets a **classification** and a **source-code citation** (the file/handler/query where it enters, moves, or lands). An element you cannot trace to code does not belong in the inventory — find it or mark it **TBD — confirm**.

---

## PHASE 1 — Classification summary & scope

At the top, produce:

- A **classification summary** table: for each classification category in the taxonomy, the sub-category, whether it is input/output, and the representative data elements.
- **Data subjects** (e.g., employees, end users, customers) and the **data-use** purpose (why the feature processes the data).

This orients the reviewer before the element-by-element detail.

---

## PHASE 2 — Data collected from external / upstream sources

For each upstream source (external API, webhook/event notification, upstream telemetry store), record the source's identity (service name/ID if applicable, permissions/scopes used) and a table of data elements: **data element**, **source mechanism** (the exact call/route/field or query), **classification**, and **resource ID** (the ID type that keys it).

Cite the **source code** for each source (the handler, the client/service, the query, the notification model). Note any field that is *received but not forwarded/stored/used* — these are common and worth calling out explicitly to shrink the privacy surface.

---

## PHASE 3 — Data processed in-memory only

List data elements that live only for the duration of execution and are **never persisted as raw**: raw inputs held in memory, redaction/pseudonymization maps, redacted derivatives, transient counts, assembled context. For each: **processing**, **lifetime**, **classification**.

If the feature performs **redaction/anonymization**, include a table of the categories redacted (e.g., names, emails, phone numbers, IPs, name variants), the **technique**, and any notes/ordering subtleties. Name the redaction framework and any size guards. Cite the redaction component.

---

## PHASE 4 — Data stored permanently

For each permanent store (table, blob, cache), record: **cluster/store**, **database/container**, **table/name**, any **ingestion mapping**, and **retention** (or **TBD — confirm**). Then a column-by-column table: **column**, **type**, **classification**, **description** — flagging which stored fields are redacted vs. raw. Cite the repository/model source code for each store.

Pay attention to keys and IDs: dedupe keys, hashes, and foreign IDs are usually Non-Personal but should still be listed and classified.

---

## PHASE 5 — Data shared / transferred outbound

Document every outbound flow: data sent to a **model/LLM**, to **another service**, or to a **downstream store/consumer**. For each: what is sent, in what form (raw vs. redacted), to whom, and the guarantee that applies (e.g., no-training/tenant-isolation for a model platform; contractual terms for a partner service). Explicitly confirm which sensitive elements are **not** sent (e.g., an internal identifier queried but never forwarded).

---

## PHASE 6 — Assemble & verify

Write the inventory to `${input:OutputFile}` with: the classification summary + subjects + data-use (Phase 1), the four lifecycle sections (Phases 2–5), and a short **source-code map** listing the cited files. Keep the taxonomy consistent throughout.

After writing, **verify**: every data element has a classification **and** a source-code citation; every store lists retention or **TBD — confirm**; every service ID / cluster / table / resource ID is discovered or **TBD — confirm** (no invented identifiers); "received but not stored/used" and "queried but not sent" notes are present where true; nothing sensitive is silently omitted.

---

## WORKFLOW SUMMARY

Execute sequentially; present each phase as a trackable todo and finish each before moving on:

1. **Classification summary & scope** → summary table + data subjects + data-use
2. **External/upstream sources** → per-source element tables with source-mechanism + citations
3. **In-memory only** → transient elements + redaction/anonymization table
4. **Stored permanently** → per-store column tables with classification + retention
5. **Shared / transferred** → outbound flows + platform/partner guarantees + "not sent" notes
6. **Assemble & verify** → the inventory file, every element traced to code, no invented IDs

The final deliverable is a single, complete data inventory a privacy reviewer can trust because every element points at the code that collects, transforms, stores, or shares it.
