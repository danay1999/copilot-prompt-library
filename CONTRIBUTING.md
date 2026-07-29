# Contributing

Thanks for helping grow this Copilot prompt library. The bar for a good contribution is simple: a prompt that someone else can copy into their own repo and run without editing out your project's details.

## The golden rule: keep prompts repository-independent

Every prompt must work in **any** repository, not just the one it was born in.

- **No hardcoded specifics.** No service names, work-item IDs, cluster or data-store URLs, project/module names, or environment names baked into the prompt body.
- **Expose them as inputs instead.** Put anything project-specific in a documented `INPUTS` section at the top of the prompt (e.g., `ServiceName`, `OutputDir`) and reference it via `${input:...}` placeholders.
- **Drive from discovery.** Prefer instructing the agent to *discover* the repository (entry points, dependencies, data flows) over describing a specific architecture.
- **Examples are fine — label them.** If you include an illustrative table or value, mark it clearly as an example and provide an empty template shape for the reader to fill in.

If you're genericizing a prompt that started life in a specific repo, a quick check: search the text for your project's name and any ID patterns and confirm there are zero matches in the prompt body.

## The second rule: only publish work that is yours to publish

A prompt here is often a genericized version of something written elsewhere. **Port only what you wrote**, and only what you have the right to publish. Someone else's prompt is their contribution to its original project, not yours to republish — even if you later edited, reformatted, or genericized it.

Before opening a PR that ports something, check the authorship of the **source** artifact:

```bash
git log --follow --format='%an' -- path/to/source.md | sort -u
git blame --line-porcelain path/to/source.md | grep '^author ' | sort | uniq -c | sort -rn
```

If the substance is someone else's, don't port it. If it's genuinely co-authored and you wrote the substance, port it and say so in the PR with the blame counts.

> The validator cannot check this. `validate_library.py` enforces structure and repository-independence; provenance is a human judgment, made once, at PR time.

## The third rule: never reproduce a non-public catalog

Authorship is not the only provenance question. A prompt may be entirely your own writing and still carry content that isn't public — a security control catalog, a compliance rubric, a data-classification taxonomy, a bug bar, or a review checklist that originates in an internal document.

**Take the catalog as an input; cite it by ID and link. Never paste its contents into a prompt body.**

```markdown
- `ControlCatalog` (string, optional): The control catalog to evaluate against — a path, URL, or name.
```

This is also better prompt design: a hardcoded catalog is by definition organization-specific, so it breaks the golden rule *and* it goes stale the moment the source is revised. Public standards (Microsoft Cloud Security Benchmark, CIS Controls, NIST SP 800-53, OWASP) are fine to name, quote, and link.

> Also a human judgment. The denylist can't catch this — and must not be used to try, since [`denylist.txt`](./.github/prompt-lint/denylist.txt) is itself public, so listing a confidential term there discloses it.

## Repository layout

```
<category>/
  README.md            # table listing the prompts in this category + how to use them
  Something.prompt.md  # one prompt per file
```

- Group prompts by purpose in a **category folder** (e.g., `security/`).
- Name prompt files `PascalCaseName.prompt.md`.
- When you add a prompt, add a row for it in that category's `README.md` table.
- To start a new category, create the folder with its own `README.md` and link it from the root `README.md` category table.

## Automated checks

[`.github/scripts/validate_library.py`](./.github/scripts/validate_library.py) enforces the rules below. It needs nothing but Python 3:

```bash
python .github/scripts/validate_library.py
```

It runs in CI on every pull request. To catch problems before you push, enable the pre-commit hook once per clone:

```bash
git config core.hooksPath .githooks
```

| Check | Rule enforced |
| ----- | ------------- |
| Layout | No prompt file at the repository root; every category folder has a `README.md`. |
| Naming | Files are `PascalCaseName.prompt.md`. |
| Indexing | Every prompt is listed in its category `README.md`; every category is listed in the root `README.md` table. |
| Inputs | Every `*.prompt.md` declares an `## INPUTS` section. |
| Links | Relative markdown links resolve (placeholder targets like `[<id>](<url>)` are ignored). |
| Independence | Prompt bodies contain no term from [`denylist.txt`](./.github/prompt-lint/denylist.txt), and no hardcoded GUID, work-item reference, email address, cluster host, or organization URL. |

Two config files tune the last check:

- **`.github/prompt-lint/denylist.txt`** — project/product names that must never appear in a prompt body. Add a term the first time it leaks.
- **`.github/prompt-lint/allowlist.txt`** — values that look project-specific but are genuinely universal. Add an entry only when every consumer uses that exact value — never to silence a leak of your own project's resources.

Category `README.md` files are exempt from the independence check.

## Submitting changes

1. Create a branch: `git checkout -b <short-description>`.
2. Make your change (add/update a prompt, update the relevant READMEs).
3. Run `python .github/scripts/validate_library.py` locally (or let the pre-commit hook run it).
4. Open a PR.

Keep PRs focused — one prompt or one logical change per PR is easiest to review.
