# Guide for agents

How to change plain-paper without breaking the package or the skill.

## What this repository is

An agent skill for English academic writing. `SKILL.md` at the root is the only skill file; agents read it first and load files from `references/` when needed. The scripts in `scripts/` use only the Python standard library. There is no build step.

Keep the skill portable: no instructions that only one agent product can follow.

## Key files

- `SKILL.md`: workflow, protected content, core rules, modes and output. Keep it under about 150 lines.
- `references/`: the detailed guidance. Each file covers one topic; `SKILL.md` links to all of them.
- `scripts/rules.json`: every rule with ID, category, level, scopes, pattern, hint and examples.
- `scripts/textstats.py`: shared reading, sentence splitting, rule matching and style profile.
- `scripts/scan.py`, `scripts/check_preservation.py`, `scripts/calibrate.py`: command-line tools.
- `scripts/calibration.json`, `scripts/corpus.json`: statistics and DOI list from the calibration corpus. Never add article text.
- `scripts/validate_package.py`: package checks run in CI.
- `tests/`: unit tests and `fixtures/cases.json` for rewrite evaluation.
- `.claude-plugin/`, `agents/openai.yaml`: install metadata for Claude Code and OpenAI-compatible agents.

## Rules for changes

- Every rule needs a unique ID (`CAT-NN`), a category and level from `rules.json`, scopes, a hint written as an instruction, at least one example it must match and, where it makes sense, examples it must not match. Mention the ID in at least one file in `references/`.
- A must-level style rule has to be rare in flagship prose. After changing one, rebuild the calibration if the PDF corpus is available (`python3 scripts/calibrate.py <folders>`); the test guard in `tests/test_scan.py` must pass.
- Examples are synthetic. Do not copy text from published articles or unpublished manuscripts, and do not name the author's projects.
- Keep one version number in `SKILL.md` (`metadata.version`), `CHANGELOG.md`, `.claude-plugin/plugin.json`, `.claude-plugin/marketplace.json` and `scripts/rules.json`.
- Write in the style the skill teaches. `python3 scripts/scan.py --strict SKILL.md references/` must report no must-fix findings outside `references/sources.md`.

## Checks before committing

```bash
python3 scripts/validate_package.py
python3 -m unittest discover -s tests -v
python3 scripts/scan.py --strict --level must SKILL.md references/craft.md references/sections.md
```
