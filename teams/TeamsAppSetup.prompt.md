# Teams App Setup

Generate the artifacts needed to ship a **Microsoft Teams app** that is installed per-resource (meeting, chat, or team) and backed by your own service: a `manifest.json`, a **setup tracking document**, and an **access guide** for the people who will install it.

This prompt is **repository-independent**: every app-, tenant-, and environment-specific value is supplied as an input or gathered by asking the user — nothing about a particular service is baked in.

> **Why this exists:** A Teams app that uses **RSC (Resource-Specific Consent)** grants permission *per installed resource*, not tenant-wide. That makes the manifest only half the job — the other half is knowing who is allowed to install it, how they request that access, and what is still outstanding before the app can ship. This prompt produces all three in one pass so the manifest, the rollout tracker, and the end-user instructions can't drift apart.

## INPUTS

- `AppShortName` (string, required): Short display name shown in Teams (max 30 characters).
- `AppFullName` (string, optional): Full display name (max 100 characters). Defaults to `${input:AppShortName}`.
- `Environment` (string, required): The environment this manifest targets (e.g., `dev`, `staging`, `prod`).
- `Domain` (string, required): The domain that serves the app's tab endpoints for `${input:Environment}` (e.g., `app.contoso.com`). Used in tab URLs, `webApplicationInfo.resource`, and `validDomains`.
- `OutputDir` (string, optional): Directory for the generated documents. Defaults to `docs/teams-app/`; `manifest.json` goes in the app package directory the user names.

Everything else is gathered in Phase 1. Any value the user cannot confirm — a client ID, a group email, an approver — must be written as **TBD — confirm**, never invented.

## PRIMARY DIRECTIVE

Produce three artifacts that stay consistent with each other:

1. **`manifest.json`** — a schema-valid Teams app manifest for one environment.
2. **`{app-name}-setup.md`** — the rollout tracker: what is done, what is pending, who owns it.
3. **`{app-name}-access-guide.md`** — the page handed to an end user who needs to install the app.

Values appear **once** as ground truth and are reused: the manifest is the source of truth for IDs, URLs, and permissions; the setup doc and access guide describe and link to them rather than restating different values.

---

## PHASE 1 — Gather inputs

Ask the user for the following, **one question at a time**, skipping anything already supplied as an input. Offer the defaults noted below so the user can confirm rather than compose.

**App identity**

1. **Short description** — one line, max 80 characters.
2. **Full description** — what the app does and what happens after it is installed, max 4000 characters.
3. **Developer name** — the team or org that owns the app.
4. **Website URL** — used in `developer.websiteUrl`. Defaults to `https://${input:Domain}` if the app has no separate homepage.
5. **App ID (GUID)** — a new GUID for a new app, or the existing ID when updating an app already published. Reusing the existing ID is what makes an upload an *update* rather than a second app.
6. **Version** — semver. **Must** be higher than the currently published version, or Teams will not detect the update.

**Backing identity**

7. **App Registration (service principal) client ID** for `${input:Environment}` — used in `webApplicationInfo.id` and as the last segment of `webApplicationInfo.resource`. Each environment normally has its own registration; confirm you have the right one.
8. **Server-side auth model** — how the backend acquires tokens to call Graph (e.g., workload identity federation / managed identity, certificate, client secret). Record it; it belongs in the access guide's permissions section and determines whether there is a secret to rotate.

**Permissions**

9. **RSC permissions** — name and type (`Application` or `Delegated`) for each. Ask the user to list only what the app actually uses; every extra permission widens the consent granted at install time. Common examples:
   - `OnlineMeetingTranscript.Read.Chat` (Application) — read a meeting transcript
   - `OnlineMeeting.ReadBasic.Chat` (Application) — read basic meeting metadata
   - `ChatMessage.Read.Chat` (Application) — read chat messages
10. **Non-RSC / tenant-wide permissions**, if any — these need admin consent and change the rollout story, so capture them separately.

**Surface**

11. **Tab type and scopes** — configurable or static, and which scopes (`team`, `groupChat`, `personal`). For meeting tabs, also capture context (`meetingChatTab`, `meetingDetailsTab`, `meetingSidePanel`).
12. **Configuration and content URL paths** — e.g., `api/config`, `api/content`. Ask for paths **without** a leading slash; the template prepends `https://${input:Domain}/`.

**Access control**

13. **Availability group** — name and email of the group that controls who may install the app. Mark **pending** if it does not exist yet.
14. **Access-request path** — how a user asks to join that group (e.g., an entitlement-management access package, a manual request to the owning team). Mark **pending** if undecided.
15. **Approvers** — who approves those requests. Mark **pending** if undecided.

---

## PHASE 2 — Output 1: `manifest.json`

Generate a manifest against Teams manifest schema **v1.25** — or the latest schema version the user targets; if they name a different one, use it consistently in both `$schema` and `manifestVersion`. Replace every `{placeholder}` with a Phase 1 answer:

```json
{
  "$schema": "https://developer.microsoft.com/json-schemas/teams/v1.25/MicrosoftTeams.schema.json",
  "manifestVersion": "1.25",
  "version": "{version}",
  "id": "{app_id}",
  "developer": {
    "name": "{developer_name}",
    "websiteUrl": "{website_url}",
    "privacyUrl": "{privacy_url}",
    "termsOfUseUrl": "{terms_of_use_url}"
  },
  "name": {
    "short": "{short_name}",
    "full": "{full_name}"
  },
  "description": {
    "short": "{short_description}",
    "full": "{full_description}"
  },
  "icons": {
    "color": "color-icon.png",
    "outline": "outline-icon.png"
  },
  "accentColor": "{accent_color}",
  "configurableTabs": [
    {
      "configurationUrl": "https://{domain}/{config_path}",
      "canUpdateConfiguration": false,
      "scopes": ["{scope_1}", "{scope_2}"],
      "context": ["{context_1}", "{context_2}"]
    }
  ],
  "webApplicationInfo": {
    "id": "{app_registration_client_id}",
    "resource": "api://{domain}/{app_registration_client_id}"
  },
  "authorization": {
    "permissions": {
      "resourceSpecific": [
        {
          "name": "{permission_1_name}",
          "type": "{permission_1_type}"
        }
      ]
    }
  },
  "validDomains": ["{domain}"]
}
```

### Rules

- **RSC permissions are per-resource.** They are granted when the app is installed on a specific meeting/chat/team — not tenant-wide, and no admin consent is required for them. Say so in the generated docs so users understand they must install per resource.
- **`webApplicationInfo` links the Teams app to an Entra App Registration.** The `resource` value must match an Application ID URI the registration actually exposes, or token audience validation fails at runtime.
- **Privacy and terms URLs are required.** If the app has no dedicated policy, ask which org-level URLs to use rather than inventing one.
- **Icons are required:** `color-icon.png` (192×192 px) and `outline-icon.png` (32×32 px, transparent background), both at the **root** of the package zip — not in a subfolder.
- **Bump `version` on every re-upload.** An unchanged version is silently treated as no update.
- **Static vs configurable tabs:** use `staticTabs` for a fixed page pinned into a scope; use `configurableTabs` when the user adds and configures the tab themselves. Only emit the array the app actually needs.
- Validate that the emitted JSON parses, and that `validDomains`, the tab URLs, and `webApplicationInfo.resource` all reference the **same** `${input:Domain}`.

---

## PHASE 3 — Output 2: `{app-name}-setup.md`

The rollout tracker. Structure it so an owner can tell, at a glance, what still blocks shipping:

1. **Header** — app name, environment, domain, app registration client ID, manifest version, last-updated date.
2. **App overview** — what the app does, tab type, permissions requested, server-side auth model.
3. **Access control status** — availability group, access-request path, approvers; each marked done/pending with an owner.
4. **Pending to-dos** — a table of `Item | Status | Notes` covering at minimum:
   - Create the availability group (if not done)
   - Create the access-request path / access package with an approval policy (if not done)
   - Align on approvers
   - Register the app for distribution with the availability group
   - Upload the manifest to the Teams Developer Portal
   - Verify permissions end to end against a real resource
   - Per-environment items still outstanding (e.g., a `prod` manifest whose domain is not final)
5. **Deployment checklist** — manifest generated, icons present and correctly sized, package zipped, uploaded, availability group assigned, end-to-end test passed.
6. **Links** — Teams Developer Portal, the access-request portal, manifest file location.

Mark items done/pending strictly from what the user reported. Never mark something done because it "should" be.

---

## PHASE 4 — Output 3: `{app-name}-access-guide.md`

The page handed to a user who needs to install the app. Write it for someone who does not know the service internals:

1. **What this app is** — plain-language purpose, and what happens after install.
2. **How it works** — the short chain from "user installs app on a resource" to "the service does X". A small text diagram is enough.
3. **How to get access** — prerequisites (membership in the availability group), the request path, and expected approval turnaround. If the request path is still pending, say so explicitly instead of describing a flow that does not exist yet.
4. **How to install the app on a resource** — click by click, ending with what the user should see when it worked.
5. **Permissions** — a table of each RSC permission and, in one line, what it is used for; plus a statement of scope ("granted only for the resource where the app is installed") and how the backend authenticates.
6. **FAQ** — at minimum: must I install it on every resource (yes, for RSC), what happens if I remove it, where do results appear, what do I check when nothing happens.
7. **Pending to-dos** — mirror the tracker's table so a reader is never told to use a path that is not live yet.
8. **Links** — Developer Portal, access-request portal, deeper docs.

### Packaging snippet to include

```powershell
Compress-Archive -Path .\app\* -DestinationPath {app-name}.zip -Force
```

Note alongside it that the three files (`manifest.json`, `color-icon.png`, `outline-icon.png`) must sit at the **root** of the zip.

---

## PHASE 5 — Verify

Before finishing, check:

- **No invented values.** Every GUID, client ID, group email, domain, and approver is either user-supplied or written **TBD — confirm**.
- **No secrets.** Client secrets, tokens, and connection strings never appear in the manifest or the docs — reference the store they live in.
- **Least privilege.** Every permission in the manifest maps to a use the user actually described; flag any that does not.
- **Consistency.** App name, version, client ID, domain, and permission list match across all three artifacts.
- **Schema validity.** The manifest parses as JSON and respects the documented length limits (short name ≤ 30, full name ≤ 100, short description ≤ 80, full description ≤ 4000).
- **Environment scoping.** The manifest is valid for `${input:Environment}` only; if other environments exist, the tracker lists them as separate outstanding manifests.

---

## WORKFLOW SUMMARY

Execute in order; present each phase as a trackable todo:

1. **Gather inputs** → app identity, backing registration, permissions, tab surface, access control
2. **Emit `manifest.json`** → schema-valid, single-environment, least-privilege
3. **Emit `{app-name}-setup.md`** → rollout tracker with honest done/pending state
4. **Emit `{app-name}-access-guide.md`** → end-user access and install instructions
5. **Verify** → no invented values, no secrets, consistent across artifacts

Finish by reminding the user to place `manifest.json` in the app package directory, add both icons at the package root, zip it, and upload via the [Teams Developer Portal](https://dev.teams.microsoft.com/home).

## References

- [Teams app manifest schema](https://learn.microsoft.com/en-us/microsoftteams/platform/resources/schema/manifest-schema)
- [Resource-specific consent (RSC)](https://learn.microsoft.com/en-us/microsoftteams/platform/graph-api/rsc/resource-specific-consent)
- [Teams Developer Portal](https://dev.teams.microsoft.com/home)
