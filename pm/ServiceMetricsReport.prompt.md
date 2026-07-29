# Service Metrics Report

Compile a recurring **usage / reliability / quality** report for a data-processing pipeline directly from
its telemetry store, and emit a slide-ready block. The value is not any one query — it is the set of
**correctness rules** that decide whether the numbers you present are true: deduplication, exact-match
status values, honest denominators, and partially-populated columns.

This prompt is **repository- and platform-independent**: the stores, tables, and field names are
established as constants at the start of each run, and the worked examples use KQL only as the most
common case.

> **Why this exists:** Pipeline metrics are easy to compute and easy to get quietly wrong. Reprocessed
> records double-count. A status filter that loose-matches `"published"` silently includes failures. A
> coverage denominator that counts work the pipeline was never eligible for makes a healthy service look
> broken. Quality scores averaged over rows that predate a schema fix produce a number that means
> nothing. This prompt runs the same checks every cycle so month-over-month comparisons stay comparable.

## INPUTS

- `ServiceName` (string, required): The service or pipeline being reported on.
- `WindowStart` (date, optional): Start of the reporting window. Defaults to the first day of the previous
  calendar month — or, for a first report, the service's GA / rollout-completion date.
- `WindowEnd` (date, optional): End of the window. Defaults to today.
- `QueryLibrary` (string, optional): Path to the repository's canonical, parameterized query definitions.
  When present, pull the queries from there instead of composing new ones, and keep the two in sync.
- `OutputTarget` (string, optional): Where the report goes. Defaults to **inline in the conversation**.

**Always confirm the resolved window with the user before reporting** (e.g., "2026-05-29 → 2026-06-24").
An unstated window makes every number in the block unfalsifiable.

> By default, do **not** write the output into a tracked file in the repository. A metrics snapshot goes
> stale immediately and turns into a source of contradicted numbers. Emit it inline, or to a scratch
> location, unless the user explicitly asks for a tracked file.

## PRIMARY DIRECTIVE

Report only what the data supports. Every number in the final block must be traceable to a query that was
actually run over the confirmed window. If a metric's underlying data is incomplete, **say so next to the
number** rather than presenting it as clean. Never estimate a figure to fill a slot — mark it
**TBD — confirm** and state what would be needed to get it.

---

## PHASE 1 — Establish the constants

Before running anything, fill in this table for `${input:ServiceName}` and confirm it with the user.
Discover the values from the repository (persistence code, ingestion mappings, `${input:QueryLibrary}`)
rather than assuming them:

| Thing | Value |
|---|---|
| Primary store (cluster / workspace) | |
| Primary database | |
| Primary table + record model | |
| Reference/secondary store (for denominators) | |
| Reference table + the fields joined on | |
| Timestamp field used for the window filter | |
| Processing timestamp field (for dedup) | |
| Dedup key field | |
| Terminal-state / event-type field | |
| Error-message field | |
| Segment field(s) (e.g., version or tenant split) | |
| Quality-score fields | |
| Downstream publish-status field | |
| Exact value meaning "published successfully" | |

Getting the **exact** success value matters: statuses are usually case-sensitive strings with several
near-miss siblings (`Skipped`, `Failed`, blank for non-eligible records). Filter on equality with the real
value; never pattern-match on "success" or "published".

---

## PHASE 2 — Correctness rules

Apply these to every count, in every cycle. They are the difference between a report and a guess.

- **Deduplicate before counting.** If records can be reprocessed, the store holds several rows per logical
  item. Collapse to the latest per key before any aggregation:
  `| summarize arg_max(<ProcessedAt>, *) by <DedupeKey>`.
- **Beware shared identifiers.** Recurring or templated entities often reuse a single ID across all
  occurrences, so a distinct count of that ID collapses to 1. Count the meaningful unit (a name or series
  field from the reference store) instead, and state which one you used.
- **Split legacy and current formats.** If identifiers changed shape across a migration, the format itself
  is the segment (e.g., a dotted legacy ID vs a plain numeric one). Report the split; a shifting mix
  explains trends that otherwise look like regressions.
- **Use honest denominators.** A coverage ratio computed over everything in the reference store includes
  work the pipeline was never eligible for, which understates reach. Lead with coverage over the **in-scope**
  subset, and report the raw ratio separately with its caveat.
- **Exclude unscored rows from quality averages.** If a scoring column only started populating after a
  schema or mapping fix, averaging over all rows silently mixes "scored 0" with "never scored". Report
  "scores available from `<date>`", average only over scored rows, and state the scored percentage.
- **Aggregate correctly for the platform.** In KQL, distinct counts belong inside `summarize`
  (`| summarize dcount(col)`), not inside a bare `toscalar(... | dcount(...))`. Cross-cluster references
  must be issued against the primary cluster using its `cluster(...).database(...)` syntax.

---

## PHASE 3 — Run the queries

Pull parameterized queries from `${input:QueryLibrary}` when it exists; otherwise compose them from the
Phase 1 constants and offer to save them there afterwards. Substitute the confirmed window as explicit
datetime literals.

Run at minimum:

1. **Activity headline** — items received, completed, completion %, pending/failed.
2. **Reliability by terminal state** — counts per terminal state / error message. Bucket non-completions
   into *causes*, not codes: expected no-ops (nothing to do for this input), upstream gaps (dependency had
   no data in window), and genuine failures (retries exhausted, unhandled errors). Source the state list
   from the pipeline's own code so no terminal state is missed.
3. **Volume and segment split** — total records, unique logical items, split by the Phase 1 segment field.
4. **Trend** — daily produced vs. daily eligible, as a comparison series. This is what shows a regression
   that a single window total hides.
5. **Reach** — unique downstream entities covered.
6. **In-scope coverage** — coverage % over the in-scope subset, per series/entity.
7. **Quality scores** — averages per score dimension over the window, plus the percentage of rows scored.
8. **Downstream publish rate** — % of outputs that reached the downstream system, filtered on the exact
   success value from Phase 1.

Show the user the resolved queries before or alongside the results, so a surprising number can be traced
immediately.

---

## PHASE 4 — Emit the block

Produce a compact, paste-ready block — not prose, and by default not a tracked file:

```text
Window: <start> → <end>
Rollout:
  <GA / flag / milestone events that landed in the window>
Usage:
  <received> received -> <produced> produced (<pct>%)
  <total> total (<segment A>, <segment B>) covering <unique> unique items across <series> series
Reliability:
  <completion>% completion; <n> non-completions: <bucketed causes>
Coverage:
  In-scope coverage ~<pct>% (best <slice> up to <pct>%)
Quality:
  Scores (avg): <dimension> <x>, <dimension> <x>, ... (<pct>% of rows scored, available from <date>)
  Downstream publish rate: <pct>%
```

State the exact window in the block itself, and flag every metric whose underlying data is incomplete.

---

## PHASE 5 — Restate the standing caveats

Repeat these each cycle; they are the ones people forget between reports:

- **Append-only stores do not backfill.** Fixing an ingestion mapping or schema only affects *future*
  writes. Historical rows keep their gaps until the pipeline reprocesses them or a backfill job runs — so
  a metric can be "fixed" and still look broken for months.
- **A reprocess changes history.** If reprocessing is how gaps get filled, past windows can shift between
  reports. Note when a previously-reported number has moved and why.
- **Comparisons need identical rules.** Month-over-month deltas are only meaningful if the same dedup,
  denominator, and exclusion rules were applied. If a rule changed, say so and, where cheap, restate the
  prior month under the new rule.

---

## WORKFLOW SUMMARY

Execute in order; present each phase as a trackable todo:

1. **Constants** → establish and confirm stores, fields, dedup key, exact status values
2. **Correctness rules** → dedup, shared-ID handling, segment split, honest denominators, scored-rows-only
3. **Run** → activity, reliability, volume/segment, trend, reach, in-scope coverage, quality, publish rate
4. **Emit** → paste-ready block with the window stated and incomplete metrics flagged
5. **Caveats** → append-only backfill behavior, shifting history, comparison-rule parity

The deliverable is a block of numbers that survives being questioned — every figure traceable to a query
over a stated window, with its known weaknesses labelled rather than smoothed over.

## Related

Feed the emitted block into [`MonthlyUpdate.prompt.md`](./MonthlyUpdate.prompt.md), which assembles the
slide deck and month-over-month deltas around these numbers.
