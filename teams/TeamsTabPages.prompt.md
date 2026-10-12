# Teams Tab Pages

Implement and document **authenticated Teams tab pages** using the two-stage *shell + body* pattern: an unauthenticated shell that renders inside the Teams iframe and carries **no product content**, and an authenticated endpoint that returns the real content only after the Teams JS SDK has produced a token.

This prompt is **repository-independent**: it discovers the repository's own web framework, auth middleware, and existing tab endpoints rather than assuming a stack. It is the companion to `TeamsAppSetup.prompt.md` — that one produces the manifest and access story, this one produces the pages the manifest points at.

> **Why this exists:** Teams renders tabs in an iframe, and an iframe cannot follow an interactive login redirect (HTTP 302). The naive fix — excluding the tab route from authentication — leaks product content to anyone who opens the URL directly or views source. The two-stage pattern keeps the *shell* unauthenticated so it can render, while every byte of real content stays behind token validation.

## INPUTS

- `Mode` (enum, optional): `document` (describe the existing implementation in a developer guide) or `add-page` (add a new tab page following the established pattern). Defaults to `document` when no guide exists, otherwise ask.
- `PageName` (string, optional, for `add-page`): Identifier of the new page (e.g., `status`). If omitted in `add-page` mode, ask the user.
- `Domain` (string, optional): The domain serving the tab endpoints; used for example URLs.
- `OutputFile` (string, optional): Path for the developer guide. Defaults to `docs/teams-app/teams-tab-developer-guide.md`.

> Every route, file path, class, and helper named in the output **must** exist in the repository. Do not describe an endpoint the code does not serve — mark anything unverified as **TBD — confirm**.

## PRIMARY DIRECTIVE

Uphold one invariant above all: **the unauthenticated shell never contains product content.**

```text
Teams iframe
  └─► Shell page (unauthenticated, no product content)
        ├─► getAuthToken() via the Teams JS SDK
        └─► fetch(body endpoint) with the token in the Authorization header
              └─► Body endpoint (authenticated) → returns the HTML fragment
```

Anything visible in *View Source* or a plain `curl` of the shell URL must be safe for an anonymous internet caller to see. Product content, customer data, internal names, and configuration values live only behind the authenticated body endpoint.

---

## PHASE 1 — Discover the implementation

Before writing anything, establish from the repository:

- **The web/host framework** and how routes are declared (e.g., HTTP-triggered functions, controllers, minimal APIs).
- **The auth middleware or filter** that protects routes, and the exact mechanism used to *exclude* a route from it. This is the highest-risk detail in the whole pattern — quote the real mechanism, don't paraphrase.
- **Existing tab endpoints** — which routes serve the shell, which serve the body, and which are referenced by `configurationUrl` / `contentUrl` in the app manifest.
- **The shared shell renderer** — the component that emits the HTML skeleton, initializes the Teams JS SDK, acquires the token, and fetches the body.
- **The page registry** — how the body endpoint maps a page identifier to an HTML fragment, and how unknown identifiers are rejected.
- **Token validation** on the body endpoint — issuer, audience, and how the audience relates to `webApplicationInfo.resource` in the manifest.

Record file paths as evidence; the guide cites them. If any piece is missing (for example, there is no allow-list of page identifiers), note it as a gap rather than describing it as if it exists.

---

## PHASE 2 (`document`) — Write the developer guide

Write `${input:OutputFile}` covering:

1. **Overview** — the two-stage architecture and the one-paragraph reason it exists (iframes can't redirect to login).
2. **Endpoints** — a section per endpoint: route, authenticated or not, what it returns, and the file that implements it.
   - **Shell endpoints** (unauthenticated) — the neutral skeleton plus SDK bootstrap.
   - **Body endpoint** (authenticated) — HTML fragments per page, served only after token validation.
   - **Config page specifics** — it is the manifest's `configurationUrl`; if the tab needs no user configuration, note that it calls the SDK's validity-state API immediately so **Save** is enabled, and registers a save handler that sets `contentUrl`, `entityId`, and a suggested display name.
3. **Security model** — a table of `Layer | Mechanism | What it protects`, at minimum:
   - Shell pages → CSP `frame-ancestors` restricted to Teams origins → prevents embedding anywhere else
   - Body endpoint → token validation → product content is never served without auth
   - Webhook/callback routes → their own validation scheme → documented separately from tab auth
   - All other routes → the standard auth path
4. **Theme support** — how the shell maps the Teams theme (default / dark / high contrast) onto CSS custom properties, applied on load from the SDK context and updated by the theme-change handler, so body fragments inherit styling automatically.
5. **Adding a new page** — the ordered steps from Phase 3 below.
6. **Links** — Teams JS SDK reference, tab configuration docs, RSC docs, and the repository's own security documentation.

Keep every code snippet in the repository's actual language, copied or adapted from real code — not invented pseudo-code in a language the repo doesn't use.

---

## PHASE 3 (`add-page`) — Add a tab page

Follow the existing pattern exactly; do not introduce a second way of doing this:

1. **Register the page identifier.** Add the constant and add it to the allow-list of valid pages, so the shell and body endpoint agree on what is servable. An unrecognized identifier must be rejected, not echoed back.
2. **Add the body HTML fragment.** Register it in the body endpoint's page registry, keyed by the identifier. Escape or avoid any interpolated value that could originate from the request.
3. **Create the shell endpoint.** Reuse the shared shell renderer; it returns the neutral skeleton with **no** product content.
4. **Wire authentication.** The shell route must be excluded from the auth middleware; the body route must remain protected. Verify both — an accidentally protected shell breaks the tab silently in Teams, and an accidentally unprotected body leaks content.
5. **Update the manifest if the page is user-visible.** Add an entry to `configurableTabs` (user-added/configured) or `staticTabs` (pinned), and **bump the manifest `version`** or Teams will not pick up the change.
6. **Update the developer guide** with the new endpoint and route.

### Defense in depth

Token validation on the body endpoint is the control that matters, but a second, cheap check is worth adding: have the auth layer stamp a marker (such as a request header or context item) that the body endpoint requires. If someone later mis-configures the route exclusions, the body endpoint fails closed instead of serving content anonymously.

---

## PHASE 4 — Verify

- **Shell leaks nothing.** Fetch each shell route unauthenticated and confirm the response contains no product content, customer data, or internal identifiers — only the skeleton and bootstrap script.
- **Body is protected.** Fetch the body route without a token and confirm it is rejected, not served.
- **Unknown page identifiers are rejected** by the allow-list rather than reflected into the response.
- **CSP `frame-ancestors`** on the shell permits only Teams origins.
- **Audience matches.** The token audience the body endpoint validates matches `webApplicationInfo.resource` in the manifest.
- **Errors don't over-share.** Failure states (auth failed, opened outside Teams) show a neutral message — never a stack trace, internal hostname, or raw exception text.
- **Guide is evidence-true.** Every route, file, and class named in the guide exists; anything unconfirmed is marked **TBD — confirm**.

---

## WORKFLOW SUMMARY

Execute the relevant path; present each phase as a trackable todo:

1. **Discover** → framework, auth middleware and its exclusion mechanism, existing shell/body endpoints, page registry, token validation
2. **Document** → write the developer guide (architecture, endpoints, security model, theming, how to add a page)
   **or** **Add-page** → register identifier, add fragment, create shell endpoint, wire auth, update manifest + guide
3. **Verify** → shell leaks nothing, body rejects anonymous calls, allow-list enforced, CSP and audience correct, errors neutral

The deliverable is a tab implementation where the only thing an anonymous caller can retrieve is an empty shell — and a guide that lets the next engineer add a page without rediscovering the pattern.

## References

- [Teams JS SDK reference](https://learn.microsoft.com/en-us/javascript/api/@microsoft/teams-js/)
- [Create a tab configuration page](https://learn.microsoft.com/en-us/microsoftteams/platform/tabs/how-to/create-tab-pages/configuration-page)
- [Resource-specific consent (RSC)](https://learn.microsoft.com/en-us/microsoftteams/platform/graph-api/rsc/resource-specific-consent)
