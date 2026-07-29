# Ops / On-Call Prompts

Repository-independent GitHub Copilot prompts for operational readiness and on-call workflows. Each prompt discovers *your* service's endpoints, dashboards, alerts, and dependencies first, then grounds every step in real evidence — nothing here is tied to a specific service or stack.

## Prompts

| Prompt | Purpose | Primary output |
| ------ | ------- | -------------- |
| [`DriRunbook.prompt.md`](./DriRunbook.prompt.md) | Generate a DRI / on-call runbook: what you own, access & prerequisites, an ordered daily health check with thresholds and known-noise, alert investigation, common failure scenarios, and escalation + ready-to-run telemetry queries. | A `dri-runbook.md` a fresh on-call engineer can follow from cold. |

**DriRunbook** is the standing "how to operate the service" page: what to check each shift, what normal looks like, which signals are known noise, and who to escalate to. Keep its *known-noise-to-ignore* list cross-linked with whatever troubleshooting guide your team maintains, so a known-benign signal is never re-investigated.

## How to use

1. Copy the prompt file into your own repository under `.github/prompts/`.
2. In an editor with GitHub Copilot (e.g., VS Code) or the Copilot CLI, invoke the prompt by name and supply the inputs listed at the top of the file (e.g., `ServiceName`, and optional dashboard/incident-tracker links).
3. The agent executes the phases sequentially, discovering endpoints/alerts/dependencies from your codebase and writing outputs to the paths described.
4. Review, replace any **TBD — confirm** placeholders with your real links/IDs, and commit.


