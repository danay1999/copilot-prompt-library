# Eval Prompts

Repository-independent GitHub Copilot prompts for evaluating AI/LLM behavior. Each prompt discovers *your* service's request contract, payload source, and endpoints first, then grounds the workflow in real traffic — nothing here is tied to a specific service or stack.

## Prompts

| Prompt | Purpose | Primary output |
| ------ | ------- | -------------- |
| [`ModelComparison.prompt.md`](./ModelComparison.prompt.md) | Before a model upgrade, replay real recent request payloads against the current and candidate models (cache bypassed), then use an LLM-as-judge to compare outputs on an explicit rubric. | A runnable, CI-safe comparison harness plus a verdict report (upgrade / hold / investigate) — with raw responses kept as a local-only artifact. |

## How to use

1. Copy the prompt file into your own repository under `.github/prompts/`.
2. In an editor with GitHub Copilot (e.g., VS Code) or the Copilot CLI, invoke the prompt by name and supply the inputs listed at the top of the file (e.g., `ServiceName`, `ModelB`, and optionally the judge model and prompt types).
3. The agent executes the phases sequentially — source payloads, replay A vs. B, judge, report — writing artifacts to the path described.
4. Review the verdict report, keep the harness opt-in (never on by default in CI), and re-disable it after a run.


