# PM Prompts

Repository- and data-source-independent GitHub Copilot prompts for recurring program/product-management chores. The value isn't any specific data query — it's the **repeatable structure**. You point each prompt at whatever data and narrative sources you have (a query, a dashboard export, a CSV, or a manual figure), and it produces a consistent artifact every cycle.

## Prompts

| Prompt | Purpose | Primary output |
| ------ | ------- | -------------- |
| [`MonthlyUpdate.prompt.md`](./MonthlyUpdate.prompt.md) | Compile a recurring monthly / milestone update (slide-style) from configured metric sources and narrative inputs. | A paste-ready slide block plus speaker notes, with month-over-month deltas and manual-fallback callouts. |
| [`Newsletter.prompt.md`](./Newsletter.prompt.md) | Draft a recurring team/product newsletter — auto-fill headline metrics, then draft substantive prose from the cycle's **delivery evidence** (merged PRs, completed work items) grouped into 3–6 reader-facing themes, so contributors review a draft instead of facing a blank page. Keeps PR/work-item references in the handoff, never in reader-facing copy. | A dated newsletter **draft** with sourced prose, auto-filled metrics, per-owner ✍️/📸/📊 callouts, and an evidence trail for reviewers. |
| [`ServiceMetricsReport.prompt.md`](./ServiceMetricsReport.prompt.md) | Compute a recurring usage / reliability / quality report for a data-processing pipeline **from its telemetry store**, applying the correctness rules that decide whether the numbers are true: dedup before counting, exact-match status values, honest denominators, and scored-rows-only quality averages. | A paste-ready metrics block with the window stated and every incomplete metric flagged. |

**MonthlyUpdate** assembles the deck; **ServiceMetricsReport** produces the numbers that go in it. If your metrics already exist as a dashboard figure or a CSV, `MonthlyUpdate` alone is enough — reach for `ServiceMetricsReport` when you are computing them from raw pipeline telemetry and need the counting rules to stay identical month over month.

The three cover one reporting cycle end to end: **ServiceMetricsReport** for the numbers, **MonthlyUpdate** for the numbers-and-slides review, and **Newsletter** for the broader written update to your audience.

## Design principles (shared)

- **Data-source-agnostic** — every metric is treated as "value + source"; no specific telemetry stack is assumed.
- **Best-effort with manual fallback** — unreachable sources become clearly-marked manual callouts, not failures.
- **Owner-tagged callouts** — every human-authored block names who writes it.
- **Never overwrite human content** — these produce drafts; a person reviews and sends.

## How to use

1. Copy the prompt file into your repository under `.github/prompts/`.
2. Invoke it with GitHub Copilot (VS Code or the Copilot CLI) and supply the inputs listed at the top — especially your **metric sources** and **narrative inputs**.
3. Confirm the reporting window, then let it assemble the draft.
4. Fill the remaining owner callouts, review, and send.
