# Team Newsletter Draft

Generate a **draft** of a recurring team/product newsletter so contributors only have to add screenshots and prose instead of hand-compiling numbers and re-deriving the format. This prompt is **repository- and data-source-independent**: metrics come from whatever sources you configure (a query, a dashboard export, a CSV, or a manual figure), and everything else is an owner-tagged "fill this in" callout.

> **Why this exists:** A newsletter is the same structure every cycle — headline metrics, what shipped, what's coming, tips — filled with fresh content. This prompt auto-fills what can be automated and clearly flags what a human must write, with an owner on each item.
>
> **A draft that is mostly empty callouts is not a successful draft.** The tedious part is not the template — it is gathering the real numbers and turning a cycle's delivery evidence into prose a reader cares about. When that evidence is available, this prompt writes a substantive first pass and makes each contributor a **reviewer** rather than a blank-page author.

## INPUTS

- `Audience` (string, required): Who the newsletter is for (e.g., a product's users, a partner team, leadership).
- `PeriodLabel` (string, optional): The issue label (e.g., "June 2026"). Defaults to the current month.
- `Template` (path, optional): A newsletter skeleton with `{{PLACEHOLDER}}` tokens for auto-filled metrics and `REPLACE` callouts for owner-authored sections. If none is provided, generate a reasonable skeleton from the sections below and offer it back for reuse.
- `Sections` (list, optional): The section → owner map for this issue (e.g., "Reliability → @alice"). Defaults to the sections from the prior issue if `PriorIssue` is supplied.
- `Metrics` (list, optional): Headline metrics to auto-fill. For each, note **what** it measures and **where** it comes from (query, dashboard tile, spreadsheet, portal lookup, or manual).
- `PriorIssue` (path, optional): The previous issue — used for style reference, section roster, and prior-period metric values (for deltas).
- `NarrativeSources` (list, optional): The cycle's **delivery evidence** — merged PRs and completed work items for the period (for "what shipped"), plus open PRs and active/planned work items updated during the period (for "what's coming up"). Paths, exports, or a query the agent can run with your own credentials. When present, use them to draft first-pass prose for each contributor section, clearly marked as a draft to be reviewed.
- `ReviewHandoff` (enum, optional): How the draft reaches its reviewers — `inline` (default), `note` (a summary of outstanding items), or `pull-request` (open a **draft** PR containing only the new newsletter file). Never publish or complete the PR.
- `OutputTarget` (path, optional): Where to write the dated draft (e.g., `newsletters/generated/<period>-newsletter.md`). Never write to the canonical/published file directly — always produce a draft for review.

## CONVENTIONS (callout legend)

Use these markers so contributors instantly see what each block needs:

- ✍️ **owner action** — write/update this section (remove it if nothing to report this cycle).
- 📸 **screenshot needed** — paste an image here.
- 📊 **metric needed** — fill in the number (source noted in the callout).
- 🤖 **auto-filled** — review the numbers; don't hand-type them.

## PRINCIPLES

- **Auto-fill what you can; flag what you can't.** Fill every metric with a reachable source; for anything unreachable, leave a 📊 `manual — fill in (source: …)` callout rather than failing.
- **Never invent a number.** No estimating, extrapolating, or "roughly" — if a metric could not be retrieved, the manual callout stays. If a metric has no queryable source at all, remove the metric bullet **and** its manual callout together as one unit, so the draft never carries half a metric.
- **Draft from evidence, not from titles.** A PR or work-item title is not enough to support a customer-facing claim — read the description before writing about it. Every drafted claim must trace to a specific PR, work item, or queried metric.
- **Shipped means shipped.** Merged PRs and completed work items feed "what shipped"; open PRs and active/planned items feed "what's coming up". Never present an open PR as delivered, or a suggested focus as a committed roadmap.
- **Keep delivery references out of customer-facing copy.** PR numbers, PR links, and work-item links are drafting evidence — record them in the handoff (PR body or note) so reviewers can validate claims, not in the newsletter a reader receives.
- **Separate observation from interpretation.** Interpretation beside a metric is welcome, but label it: state what was observed, then what you think it means. Never imply causation from correlation.
- **Verify every link.** Add a link only when it leads to authoritative documentation, and confirm the URL resolves before writing it into the draft.
- **Every manual block has an owner.** No section should be ambiguous about who writes it — attach an owner to each ✍️ callout.
- **Deltas where available.** Show month-over-month change for numeric metrics when the prior issue provides a baseline.
- **Never overwrite human content.** Produce a dated **draft**; the canonical/sent issue is edited and sent by a human. Preserve any existing prose and images, and never modify the template, a prior issue, or any file other than the new draft.
- **Data-source-agnostic.** A metric's source may be a live query, a dashboard export, a CSV, or a manual figure — treat them uniformly as "value + source."

## WORKFLOW

Execute sequentially; present each phase as a trackable todo.

### 1. Resolve issue scope
Confirm `Audience`, `PeriodLabel`, and the section → owner roster (seed from `PriorIssue` if given). Resolve the reporting window for metrics and confirm it with the user.

### 2. Auto-fill metrics
For each metric, pull its value from the configured source and compute the delta vs. the prior issue where possible. Replace the matching `{{PLACEHOLDER}}` tokens. For unreachable sources, insert a 📊 manual callout naming the exact lookup steps or query.

### 3. Gather delivery evidence
If `NarrativeSources` is available, collect the period's evidence with your own credentials and tools — **never guess**:

- **Shipped** — PRs merged and work items completed within the window.
- **Coming up** — PRs still open and work items active/planned that were updated within the window.

Read the **description**, not just the title, of the most consequential items. A title is not enough evidence for a customer-facing claim. Keep a running list of which item supports which claim; it becomes the evidence trail in step 6.

### 4. Theme the evidence
Group what you gathered into **3–6 reader-facing themes based on outcomes**, not a commit dump. A theme is something a reader would recognize as affecting them ("faster failure diagnosis", "fewer manual steps at review time"), not an implementation detail. Items that don't ladder into a theme are usually not newsletter material.

### 5. Draft the sections
Write concise prose for the shipped and upcoming sections from the themed evidence, in the style of `PriorIssue`. Prefer customer impact and operational meaning over implementation detail. Where the prior issue gives comparable context, include the change.

Then rewrite each ✍️ callout so its action is **"review and edit the sourced draft below, and add any notable cases"** — not "write this section". Preserve 📸 screenshot callouts and any applicable 📊 manual-metric callouts untouched.

**Write the intro last**, once every other section is drafted, so it accurately summarizes the strongest 2–4 themes and says why they matter to this audience.

### 6. Emit the draft and hand it off
Fill the template (or generated skeleton) and write it to `OutputTarget` as a dated draft — exactly one new file. Then hand off per `ReviewHandoff`, listing:

- the remaining owner action items (each ✍️/📸/📊 callout, with its owner),
- any metric left manual because its source wasn't reachable,
- which numbers came from which source and should be spot-checked before sending,
- the **evidence trail** — the PRs and work items behind each drafted claim, so a reviewer can validate them without those references appearing in the newsletter itself.

For `pull-request`, open a **draft** PR containing only the new newsletter file; never publish or complete it.

## DEFAULT SKELETON (when no `Template` is provided)

```markdown
# <Audience> Newsletter — {{PERIOD_LABEL}}

## <Intro>
> ✍️ **Intro prose (owner: <compiler>)** — written last, once the other sections are drafted: 1-2 paragraphs on the strongest 2-4 themes of this issue and why they matter to this audience.

## Metrics
> 🤖 **Auto-filled (best-effort)** — falls back to a manual note if a source isn't reachable. Shows change vs. prior issue where available.
- **<Metric name>:** {{METRIC_1}}
- **<Metric name>:** {{METRIC_2}}

## ✅ What's shipped
### <Workstream> — owner: <@owner>
> ✍️ **<@owner>** — review and edit the sourced draft below, and add any notable cases (or remove if nothing to report). Left empty only when no delivery evidence was available.
[SCREENSHOT_HERE] — 📸 <what the screenshot should show>

## 🚧 What's coming up
### <Workstream> — owner: <@owner>
> ✍️ **<@owner>** — review and edit the sourced draft below; confirm nothing here is a commitment the team hasn't made (or remove if nothing to report).

## 💡 Tips and reminders
> ✍️ **Review the evergreen tips** — keep, update, or remove for this issue.

<sub>Metrics sourced from <named sources> for <date range>. All other sections are contributor-authored.</sub>
```

## NOTES

- Any `{{PLACEHOLDER}}` in a custom `Template` must map to a metric you can fill; unmatched placeholders should be surfaced (not silently left in the draft).
- When a metric has no queryable source at all, remove its bullet **and** its 📊 manual callout as one unit — leaving either half behind produces a draft that asks someone to fill in a number nobody can get.
- Keep the section roster in sync with the work — add, rename, or remove sections as the team's workstreams change cycle to cycle.
- Delivery references (PR numbers, PR links, work-item links) belong in the handoff, never in the issue a reader receives. The evidence trail is for reviewers validating claims.
- The final send is always a human step; this prompt's job is to eliminate the mechanical assembly and the blank page, not to auto-publish.
