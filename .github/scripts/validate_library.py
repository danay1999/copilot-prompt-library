#!/usr/bin/env python3
"""Validate the structure and repository-independence of the Copilot prompt library.

Enforces the rules documented in CONTRIBUTING.md:

* prompts and agents live in a category folder, never at the repository root
* files are named ``PascalCaseName.prompt.md`` / ``PascalCaseName.agent.md``
* every category folder has a README.md, and every file is listed in it
* every category folder is listed in the root README category table
* every prompt declares an ``## INPUTS`` section
* relative links resolve to something that exists
* prompt and agent bodies contain no service-specific names, IDs, emails, or hosts

Run from anywhere::

    python .github/scripts/validate_library.py

Exit code 0 means the library is clean; 1 means at least one violation was found.
"""

from __future__ import annotations

import re
import sys
from dataclasses import dataclass
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
LINT_DIR = REPO_ROOT / ".github" / "prompt-lint"
DENYLIST_FILE = LINT_DIR / "denylist.txt"
ALLOWLIST_FILE = LINT_DIR / "allowlist.txt"

PROMPT_SUFFIX = ".prompt.md"
AGENT_SUFFIX = ".agent.md"

# Top-level directories that are infrastructure rather than prompt categories.
NON_CATEGORY_DIRS = {".git", ".github", ".vscode"}

PASCAL_CASE = re.compile(r"^[A-Z][A-Za-z0-9]*$")
INPUTS_HEADING = re.compile(r"^##\s+INPUTS\s*$", re.MULTILINE)
MARKDOWN_LINK = re.compile(r"\[[^\]]*\]\(([^)]+)\)")
FENCED_BLOCK = re.compile(r"```.*?```", re.DOTALL)

# High-signal patterns that usually mean a service-specific value leaked into a
# prompt. Anything legitimately shared (an org-wide scanner, a central reporting
# cluster) belongs in allowlist.txt rather than being silently permitted here.
LEAK_PATTERNS = [
    (
        "GUID",
        re.compile(r"\b[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}\b"),
    ),
    ("work item reference", re.compile(r"\b[A-Z]{2,6}#\d+\b")),
    ("email address", re.compile(r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b")),
    ("Kusto cluster host", re.compile(r"\b[A-Za-z0-9-]+(?:\.[A-Za-z0-9-]+)*\.kusto\.windows\.net\b")),
    ("Azure DevOps organization URL", re.compile(r"\bdev\.azure\.com/[A-Za-z0-9._-]+")),
]


@dataclass
class Violation:
    """A single rule breach, reported with the file that caused it."""

    path: str
    message: str

    def __str__(self) -> str:
        return f"{self.path}: {self.message}"


def load_list(path: Path) -> list[str]:
    """Read a config file of one entry per line, ignoring blanks and # comments."""
    if not path.is_file():
        return []
    entries = []
    for raw in path.read_text(encoding="utf-8").splitlines():
        line = raw.split("#", 1)[0].strip()
        if line:
            entries.append(line)
    return entries


def category_dirs() -> list[Path]:
    return sorted(
        p
        for p in REPO_ROOT.iterdir()
        if p.is_dir() and p.name not in NON_CATEGORY_DIRS and not p.name.startswith(".")
    )


def library_files(directory: Path) -> list[Path]:
    return sorted(
        p
        for p in directory.rglob("*")
        if p.is_file() and (p.name.endswith(PROMPT_SUFFIX) or p.name.endswith(AGENT_SUFFIX))
    )


def rel(path: Path) -> str:
    return path.relative_to(REPO_ROOT).as_posix()


def base_name(path: Path) -> str:
    suffix = PROMPT_SUFFIX if path.name.endswith(PROMPT_SUFFIX) else AGENT_SUFFIX
    return path.name[: -len(suffix)]


def check_layout(violations: list[Violation]) -> None:
    """Prompts and agents must live in a category folder and be named PascalCase."""
    for path in REPO_ROOT.iterdir():
        if path.is_file() and (path.name.endswith(PROMPT_SUFFIX) or path.name.endswith(AGENT_SUFFIX)):
            violations.append(
                Violation(rel(path), "lives at the repository root; move it into a category folder")
            )

    for directory in category_dirs():
        files = library_files(directory)
        if not files:
            continue
        if not (directory / "README.md").is_file():
            violations.append(Violation(f"{directory.name}/", "category folder has no README.md"))
        for path in files:
            name = base_name(path)
            if not PASCAL_CASE.match(name):
                violations.append(
                    Violation(
                        rel(path),
                        f"'{name}' is not PascalCase; rename to PascalCaseName{PROMPT_SUFFIX}",
                    )
                )


def check_indexing(violations: list[Violation]) -> None:
    """Every file is listed in its category README; every category in the root README."""
    root_readme = REPO_ROOT / "README.md"
    root_text = root_readme.read_text(encoding="utf-8") if root_readme.is_file() else ""
    if not root_text:
        violations.append(Violation("README.md", "root README.md is missing or empty"))

    for directory in category_dirs():
        files = library_files(directory)
        if not files:
            continue
        if f"./{directory.name}" not in root_text:
            violations.append(
                Violation(
                    "README.md",
                    f"category '{directory.name}/' is not listed in the root category table",
                )
            )
        readme = directory / "README.md"
        if not readme.is_file():
            continue
        readme_text = readme.read_text(encoding="utf-8")
        for path in files:
            if path.name not in readme_text:
                violations.append(Violation(rel(readme), f"does not list '{path.name}' in its table"))


def check_prompt_contents(violations: list[Violation]) -> None:
    """Every prompt declares its inputs, so consumers know what to supply."""
    for directory in category_dirs():
        for path in library_files(directory):
            if not path.name.endswith(PROMPT_SUFFIX):
                continue
            if not INPUTS_HEADING.search(path.read_text(encoding="utf-8")):
                violations.append(Violation(rel(path), "has no '## INPUTS' section"))


def check_links(violations: list[Violation]) -> None:
    """Relative markdown links must resolve to a file that exists."""
    for path in sorted(REPO_ROOT.rglob("*.md")):
        parts = path.relative_to(REPO_ROOT).parts
        if any(part in NON_CATEGORY_DIRS for part in parts[:-1]):
            continue
        for target in MARKDOWN_LINK.findall(path.read_text(encoding="utf-8")):
            target = target.split()[0].strip()
            if target.startswith(("http://", "https://", "mailto:", "#")):
                continue
            # Skip placeholder targets in illustrative output shapes, e.g.
            # `[<TicketId>](<tracker url>)` or `[report](${input:OutputFile})`.
            if any(ch in target for ch in "<>{}$"):
                continue
            resolved = (path.parent / target.split("#", 1)[0]).resolve()
            if not resolved.exists():
                violations.append(Violation(rel(path), f"broken relative link '{target}'"))


def check_independence(violations: list[Violation], denylist: list[str], allowlist: list[str]) -> None:
    """Prompt and agent bodies must not name a specific service, tenant, or resource."""
    for directory in category_dirs():
        for path in library_files(directory):
            text = path.read_text(encoding="utf-8")
            for term in denylist:
                if re.search(rf"\b{re.escape(term)}\b", text, re.IGNORECASE):
                    violations.append(
                        Violation(
                            rel(path),
                            f"contains service-specific term '{term}'; expose it as an input instead",
                        )
                    )
            # Blank out fenced blocks so illustrative snippets keep their line
            # numbers but do not trip the leak patterns.
            scrubbed = FENCED_BLOCK.sub(lambda m: "\n" * m.group(0).count("\n"), text)
            for label, pattern in LEAK_PATTERNS:
                for match in pattern.finditer(scrubbed):
                    value = match.group(0)
                    if any(allowed in value or value in allowed for allowed in allowlist):
                        continue
                    violations.append(
                        Violation(
                            rel(path),
                            f"contains a hardcoded {label} ('{value}'); make it an input, or add it "
                            "to .github/prompt-lint/allowlist.txt if it is genuinely org-wide",
                        )
                    )


def main() -> int:
    violations: list[Violation] = []
    denylist = load_list(DENYLIST_FILE)
    allowlist = load_list(ALLOWLIST_FILE)

    check_layout(violations)
    check_indexing(violations)
    check_prompt_contents(violations)
    check_links(violations)
    check_independence(violations, denylist, allowlist)

    categories = [d.name for d in category_dirs() if library_files(d)]
    total = sum(len(library_files(d)) for d in category_dirs())
    print(f"Checked {total} prompt/agent files across {len(categories)} categories: {', '.join(categories)}")

    if violations:
        print(f"\n{len(violations)} violation(s) found:\n", file=sys.stderr)
        for violation in violations:
            print(f"  - {violation}", file=sys.stderr)
        print("\nSee CONTRIBUTING.md for the rules these checks enforce.", file=sys.stderr)
        return 1

    print("No violations found.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
