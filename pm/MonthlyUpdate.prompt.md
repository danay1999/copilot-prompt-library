# Monthly Update Slides

Compile a recurring monthly (or milestone) update into a **slide-ready block plus speaker notes**, assembled from whatever data and narrative sources your team has. This prompt is **repository- and data-source-independent**: it does not assume any particular telemetry system — you tell it where the numbers come from (a query, a dashboard export, a CSV, or a manual figure), and it produces a consistent, paste-ready update every cycle.

> **Why this exists:** Every month brings the same chore — re-assemble the same shape of update from scattered numbers and narrative. This prompt turns that into "run it, confirm the window, fill the callouts, paste."

## INPUTS

- `Subject` (string, required): What the update is about (e.g., a team, product, program, or workstream).
- `WindowStart` (date, optional): Start of the reporting window. Defaults to the first day of the previous calendar month (or "last 30 days" if the user says "past month").
- `WindowEnd` (date, optional): End of the window. Defaults to today.
- `Metrics` (list, optional): The metrics to report. For each, note **what** it measures and **where** it comes from (query, dashboard tile, spreadsheet, portal lookup, or manual). If omitted, ask the user for the 3-7 metrics that matter this cycle.
- `NarrativeSources` (list, optional): Evidence for the "what shipped / what's next" story — e.g., merged PRs, closed work items, release notes, a prior update deck. Provide file paths, exports, or links.
- `OutputTarget` (string, optional): Where to write the block. Defaults to inline in the chat (and the session scratch folder). Do **not** write into a tracked file unless the user asks.

Always **confirm the resolved window** with the user before reporting (e.g., "2026-06-01 → 2026-06-30").

## PRINCIPLES

- **Data-source-agnostic.** Treat every metric as "value + source." A source can be a live query, a dashboard export, a CSV, a portal screenshot lookup, or a manually supplied number. Never assume a specific telemetry stack.
- **Best-effort with manual fallback.** If a source can't be reached during the run, emit a clearly-marked `manual — fill in` placeholder for that metric instead of failing the whole update.
- **Show change over time.** Where the prior period's value is available, show the month-over-month (or period-over-period) delta.
- **Only report what's grounded.** Every number must trace to a named source. Flag any metric whose underlying data is incomplete for the window.
- **Deduplicate before counting.** If a source can contain repeated/reprocessed rows, collapse to one row per logical entity before counting, and say so.

## WORKFLOW

Execute sequentially; present each phase as a trackable todo.

### 1. Resolve scope
Confirm `Subject` and the reporting window with the user. List the metrics to be reported and their sources.

### 2. Gather metrics
For each metric, pull the value from its source. For live queries, show the query you ran. For each metric capture: current value, prior-period value (if available), delta, and a one-line source note. If a source is unreachable, mark the metric `manual — fill in (source: …)` and continue.

### 3. Assemble the narrative
From `NarrativeSources`, summarize:
- **What shipped** this period (grouped by workstream/owner).
- **What's coming up** next period.
- **Notable items / risks** worth a callout.
Keep each bullet to one or two sentences and attribute owners where known.

### 4. Emit the slide block
Produce a compact, paste-ready block (see format below) **plus** short speaker notes the presenter can read aloud. State the exact window and flag any incomplete metric.

## OUTPUT FORMAT (slide block)

Emit a block the user can paste into slides — mirror this shape:

```
<Subject> — Monthly Update (<window start> → <window end>)

Metrics:
  <Metric 1>: <value> (<Δ vs prior>)   [source: <source>]
  <Metric 2>: <value> (<Δ vs prior>)   [source: <source>]
  ...

What shipped:
  - <owner/area>: <one-line highlight>
  - ...

What's next:
  - <owner/area>: <one-line plan>
  - ...

Watch / risks:
  - <notable item, if any>

Notes: <exact window; any metric whose data is incomplete or manually filled>
```

Then, under **Speaker notes**, provide 3-6 sentences the presenter can narrate for the slide.

## NOTES / GOTCHAS TO RESTATE EACH CYCLE

- Fixing a data source only affects **future** data; it does not backfill periods already reported.
- Prefer the metric that best reflects real reach; call out when a denominator inflates or deflates a ratio.
- Keep the metric set stable month to month so trends are comparable; note any definition change explicitly.
