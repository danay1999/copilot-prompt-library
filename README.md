# copilot-prompt-library

A library of reusable [GitHub Copilot](https://github.com/features/copilot) prompt files. Each prompt is a saved, structured instruction set that runs a repeatable, multi-phase workflow — so you stop re-explaining the same task every time you need it done.

Every prompt is **repository-independent**: copy the `.prompt.md` file into your own repo under `.github/prompts/`, supply the inputs listed at the top, and run it. Nothing is hardcoded to the codebase it was written against.

## Categories

| Folder | Contents |
| ------ | -------- |
| [`security/`](./security) | Security & compliance workflows — STRIDE threat modeling, Responsible-AI compliance posture, AI data-flow classification, privacy data inventory, and high-signal secure code review. |
| [`pm/`](./pm) | Program/product-management chores — pipeline usage/reliability/quality metrics, monthly update slides, and team newsletter drafts. |
| [`teams/`](./teams) | Microsoft Teams app workflows — RSC app manifest, rollout tracker and access guide, plus the two-stage authenticated tab-page pattern. |
| [`ops/`](./ops) | Operational readiness & on-call workflows — a runbook grounded in your service's real dashboards, alerts, and dependencies. |
| [`eval/`](./eval) | AI/LLM evaluation workflows — model-upgrade comparison via real-payload replay and LLM-as-judge. |

More categories can be added over time (each in its own folder with a README).

## Why these are more than a saved chat message

- **Multi-phase and ordered.** Each prompt runs as a sequence of phases with a defined artifact at the end, not a single question.
- **Evidence-first.** Prompts discover your repository and ground findings in real code. Where a value can't be confirmed they emit `TBD — confirm` rather than inventing one.
- **Genuinely portable.** A validator enforces it: no hardcoded service names, GUIDs, work-item IDs, emails, cluster hosts, or organization URLs in any prompt body.
- **Structurally consistent.** Every prompt declares its `INPUTS`, lives in a category folder, and is indexed in that folder's README — all machine-checked.

## How to use a prompt

1. Copy the `.prompt.md` file into your repository under `.github/prompts/`.
2. In an editor with GitHub Copilot (e.g., VS Code) or the Copilot CLI, invoke the prompt by name and provide the inputs listed at the top of the file.
3. The agent runs the phases in order and writes the described output artifacts.
4. Review, replace any `TBD — confirm` placeholders with your real values, and commit.

## Working in this repository

Prompts are validated by [`.github/scripts/validate_library.py`](./.github/scripts/validate_library.py), which checks layout, naming, README indexing, the `INPUTS` section, relative links, and repository-independence. Enable it locally as a pre-commit hook:

```bash
git config core.hooksPath .githooks
```

## Contributing

Add new prompts in the relevant category folder (or create a new folder with its own `README.md`). Keep prompts repository-independent — drive everything from inputs and repository discovery rather than hardcoded, service-specific assumptions. See [CONTRIBUTING.md](./CONTRIBUTING.md).

## License

[MIT](./LICENSE).
