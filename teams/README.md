# Teams App Prompts

Repository-independent GitHub Copilot prompts for building and shipping a **Microsoft Teams app** backed by your own service. Each prompt discovers *your* domain, app registration, permissions, and endpoints first — nothing here is tied to a specific service or stack.

## Prompts

| Prompt | Purpose | Primary output |
| ------ | ------- | -------------- |
| [`TeamsAppSetup.prompt.md`](./TeamsAppSetup.prompt.md) | Produce everything needed to ship a Teams app installed per-resource via **RSC (Resource-Specific Consent)**: a schema-valid manifest for one environment, a rollout tracker with honest done/pending state, and an end-user access guide. Enforces least-privilege permissions, no invented IDs, and no secrets. | `manifest.json`, `{app-name}-setup.md`, and `{app-name}-access-guide.md`. |
| [`TeamsTabPages.prompt.md`](./TeamsTabPages.prompt.md) | Implement and document **authenticated tab pages** using the two-stage *shell + body* pattern — an unauthenticated shell with no product content, and an authenticated endpoint that returns the real HTML only after the Teams JS SDK produces a token. Supports `document` and `add-page` modes. | A `teams-tab-developer-guide.md`, plus the new endpoint wiring in `add-page` mode. |

The two are complementary: **TeamsAppSetup** produces the manifest and the access story around it; **TeamsTabPages** produces the pages that manifest points at. Keep the manifest's `configurationUrl` / `contentUrl` and the developer guide's endpoint list cross-checked — when one changes, the other usually must too.

## Why the tab pattern matters

Teams renders tabs in an iframe, and an iframe cannot follow an interactive login redirect. The tempting shortcut — excluding the tab route from authentication — publishes your product content to anyone who opens the URL or views source. `TeamsTabPages.prompt.md` exists to make the safe pattern the easy one: the shell is public but empty, and every byte of real content stays behind token validation.

## How to use

1. Copy the prompt file into your own repository under `.github/prompts/`.
2. In an editor with GitHub Copilot (e.g., VS Code) or the Copilot CLI, invoke the prompt by name and supply the inputs listed at the top of the file (e.g., `AppShortName`, `Environment`, `Domain`).
3. The agent executes the phases sequentially, asking for the values it cannot discover and writing outputs to the paths described.
4. Review, replace any **TBD — confirm** placeholders with your real IDs, group emails, and approvers, and commit.

> Both prompts refuse to invent GUIDs, client IDs, group emails, or approvers — unconfirmed values come back as **TBD — confirm** on purpose. Resolve them before shipping the manifest.


