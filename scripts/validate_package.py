#!/usr/bin/env python3
"""Check plain-paper's package files without external dependencies.

Checks the skill metadata, version numbers, plugin manifests, local links,
rule definitions and their documentation, and the calibration files.
Exit status 0 when everything passes, 1 otherwise.
"""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path
from urllib.parse import unquote, urlsplit

ROOT = Path(__file__).resolve().parent.parent
SEMVER = re.compile(r"^\d+\.\d+\.\d+$")
problems: list[str] = []


def problem(message: str) -> None:
    problems.append(message)


def read(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except OSError as error:
        problem(f"Cannot read {path.relative_to(ROOT)}: {error}")
        return ""


def load_json(path: Path):
    try:
        return json.loads(read(path))
    except json.JSONDecodeError as error:
        problem(f"Fix the JSON in {path.relative_to(ROOT)}: {error}")
        return {}


def check_skill() -> str:
    skill = read(ROOT / "SKILL.md")
    match = re.match(r"\A---\n(.*?)\n---\n", skill, re.DOTALL)
    if not match:
        problem("SKILL.md must begin with YAML front matter")
        return ""
    front = match.group(1)
    name = re.search(r"(?m)^name:\s*(\S+)\s*$", front)
    if not name or name.group(1) != "plain-paper":
        problem("SKILL.md name must be plain-paper")
    description = re.search(r"(?ms)^description:\s*\|?\n?(.*?)(?=^\w[\w-]*:|\Z)", front)
    text = " ".join(line.strip() for line in description.group(1).splitlines()) if description else ""
    if not text or len(text) > 1024:
        problem(f"SKILL.md description must have 1-1024 characters (has {len(text)})")
    for field in ("version:", "compatibility:", "allowed-tools:"):
        if re.search(rf"(?m)^{field}", front):
            problem(f"Move the top-level '{field[:-1]}' field out of the SKILL.md front matter")
    if not re.search(r"(?m)^license:\s*MIT\s*$", front):
        problem("SKILL.md must declare license: MIT")
    version = re.search(r"(?m)^\s+version:\s*[\"']?([0-9.]+)[\"']?\s*$", front)
    if not version or not SEMVER.match(version.group(1)):
        problem("Add metadata.version to SKILL.md as a three-part version")
        return ""
    if len(skill.splitlines()) > 500:
        problem("SKILL.md is longer than 500 lines")
    skill_files = [p.relative_to(ROOT) for p in ROOT.rglob("SKILL.md") if ".git" not in p.parts]
    if skill_files != [Path("SKILL.md")]:
        problem(f"Keep one SKILL.md at the repository root (found {skill_files})")
    return version.group(1)


def check_versions(skill_version: str) -> None:
    plugin = load_json(ROOT / ".claude-plugin" / "plugin.json")
    marketplace = load_json(ROOT / ".claude-plugin" / "marketplace.json")
    rules = load_json(ROOT / "scripts" / "rules.json")
    changelog = re.search(r"(?m)^## (\d+\.\d+\.\d+)\s*$", read(ROOT / "CHANGELOG.md"))
    versions = {
        "SKILL.md": skill_version,
        "CHANGELOG.md": changelog.group(1) if changelog else "",
        "plugin.json": str(plugin.get("version", "")),
        "marketplace.json": str((marketplace.get("plugins") or [{}])[0].get("version", "")),
        "rules.json": str(rules.get("version", "")),
    }
    if len(set(versions.values())) != 1:
        problem(f"Use one version everywhere: {versions}")
    if plugin.get("name") != "plain-paper" or plugin.get("skills") != ["./"]:
        problem("plugin.json must be named plain-paper and point its skills at ['./']")
    entry = (marketplace.get("plugins") or [{}])[0]
    if entry.get("name") != "plain-paper" or entry.get("source") != "./":
        problem("marketplace.json must list plain-paper with source './'")


def check_links() -> None:
    documents = [ROOT / "SKILL.md", ROOT / "README.md", ROOT / "AGENTS.md", ROOT / "tests" / "README.md"]
    documents += sorted((ROOT / "references").glob("*.md"))
    for document in documents:
        text = read(document)
        text = re.sub(r"```.*?```", "", text, flags=re.DOTALL)
        for match in re.finditer(r"\]\(([^)\s]+)\)", text):
            target = match.group(1)
            url = urlsplit(target)
            if url.scheme or not url.path:
                continue
            resolved = (document.parent / unquote(url.path)).resolve()
            if not resolved.exists():
                problem(f"Broken link in {document.relative_to(ROOT)}: {target}")
    skill = read(ROOT / "SKILL.md")
    for reference in sorted((ROOT / "references").glob("*.md")):
        if f"references/{reference.name}" not in skill:
            problem(f"SKILL.md does not link references/{reference.name}")


def check_rules() -> None:
    data = load_json(ROOT / "scripts" / "rules.json")
    rules = data.get("rules", [])
    documented = " ".join(read(p) for p in (ROOT / "references").glob("*.md"))
    seen = set()
    for rule in rules:
        rule_id = rule.get("id", "?")
        if rule_id in seen:
            problem(f"Duplicate rule ID {rule_id}")
        seen.add(rule_id)
        if not re.match(r"^[A-Z]{3,4}-\d{2}$", rule_id):
            problem(f"Badly formed rule ID {rule_id}")
        if rule.get("category") not in data.get("categories", {}):
            problem(f"{rule_id}: unknown category")
        if rule.get("level") not in data.get("levels", {}):
            problem(f"{rule_id}: unknown level")
        if not rule.get("hint"):
            problem(f"{rule_id}: missing hint")
        if not rule.get("examples", {}).get("hit"):
            problem(f"{rule_id}: needs at least one example it matches")
        if rule.get("pattern"):
            try:
                re.compile(rule["pattern"])
            except re.error as error:
                problem(f"{rule_id}: pattern does not compile ({error})")
        elif rule.get("kind") != "builtin":
            problem(f"{rule_id}: needs a pattern or kind 'builtin'")
        if rule_id not in documented:
            problem(f"{rule_id} is not mentioned in references/")


def check_calibration() -> None:
    calibration = load_json(ROOT / "scripts" / "calibration.json")
    corpus = load_json(ROOT / "scripts" / "corpus.json")
    groups = calibration.get("groups", {})
    if "core" not in groups:
        problem("calibration.json has no core group")
        return
    research = [p for p in corpus if p.get("type") == "research"]
    if groups["core"].get("papers") != len(research):
        problem("calibration.json and corpus.json disagree on the number of research articles")
    for paper in corpus:
        if set(paper) - {"doi", "family", "journal", "year", "type", "words", "sentences"}:
            problem(f"corpus.json holds unexpected fields for {paper.get('doi')}")
            break


def main() -> int:
    version = check_skill()
    if version:
        check_versions(version)
    check_links()
    check_rules()
    check_calibration()
    if problems:
        for message in problems:
            print(message, file=sys.stderr)
        return 1
    print("Package checks passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
