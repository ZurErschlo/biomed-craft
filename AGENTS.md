# Guide for agents

How to change biomed-craft without breaking the package or the skill, and how to fold in what a new research project teaches.

## What this repository is

An agent skill for biomedical research, from the research question to the published paper and the response to reviewers. It starts from writing and covers the content and methods of each study type, research plans, execution logs, analysis code, evidence and data checks. `SKILL.md` at the root is the only skill file; agents read it first and load files from `references/` when needed. The scripts in `scripts/` use only the Python standard library. There is no build step.

Keep the skill portable: no instructions that only one agent product can follow.

## Key files

- `SKILL.md`: principles, stages and confirmation points, routing by document and study type, core rules and output. Keep it under about 150 lines.
- `references/`: the detailed guidance, one topic per file. `SKILL.md` links every top-level file; `references/study-types.md` links every file in `references/study-types/`.
- `scripts/rules.json`: every rule with ID, category, level, per-design levels, scopes, document types, pattern, hint and examples.
- `scripts/textstats.py`: shared reading (documents and code), sentence splitting, rule matching, style profile and study-design detection.
- `scripts/scan.py`, `scripts/check_numbers.py`, `scripts/check_fulltext.py`, `scripts/check_preservation.py`, `scripts/calibrate.py`: command-line tools.
- `scripts/calibration.json`, `scripts/corpus.json`: statistics and identifiers (DOI, PMCID) from the calibration corpus. Never add article text.
- `calibration-texts/`: local only and ignored by git. Texts of publisher PDFs, read by `calibrate.py --texts`. They are under the publishers' copyright: never commit them, and `validate_package.py` fails if one is tracked.
- `scripts/validate_package.py`: package checks run in CI.
- `tests/`: unit tests, fixtures and `fixtures/cases.json` for rewrite evaluation.
- `.claude-plugin/`, `agents/openai.yaml`: install metadata for Claude Code and OpenAI-compatible agents.

## Rules for changes

- Every rule needs a unique ID (`CAT-NN`), a category and level from `rules.json`, scopes, a hint written as an instruction, at least one example it must match and, where it makes sense, examples it must not match. Mention the ID in at least one file in `references/`.
- A must-level style rule has to be rare in the research articles of every journal family and study design with enough articles. When it is common in one design (reviews, laboratory work), give it a per-design level in `levels` instead of weakening it everywhere. After changing one, rebuild the calibration (`python3 scripts/calibrate.py <folders> --texts calibration-texts --pmc scripts/corpus.json`); the test guard in `tests/test_scan.py` must pass.
- Examples are synthetic. Do not copy text from published articles or unpublished manuscripts, and do not name the author's projects.
- Keep one version number in `SKILL.md` (`metadata.version`), `CHANGELOG.md`, `.claude-plugin/plugin.json`, `.claude-plugin/marketplace.json` and `scripts/rules.json`.
- Write in the style the skill teaches. `python3 scripts/scan.py --strict SKILL.md references/` must report no must-fix findings outside `references/sources.md`.

## Folding in a new research project

When the author asks the agent to learn from a finished or ongoing project:

1. Read the project's protocol or registration, research plan, execution log, code headers, manuscript and supplement, and above all the reviewer comments and response letters.
2. Record, by study type: the methods used and the reasons given; decisions the author made or corrected; problems that recurred in the log; what reviewers asked for; gaps the drafts show.
3. Add each lesson where it belongs: content and reviewer concerns to `references/study-types/<type>.md`; wording to a rule in `rules.json` with synthetic examples; plan, log, code and folder practice to the matching reference; evidence and data practice to `references/evidence.md`.
4. Write every lesson as a general instruction. Do not name the project, its people or its data, and do not copy its text.
5. Run the checks below, add a line to `CHANGELOG.md`, and list for the author what was added, what was left out and why.

## Adding publisher PDFs to the calibration

1. List the articles with DOI, title, year and study design, chosen to fill a gap in journals, designs or topics. The author downloads the PDFs.
2. Run `python3 scripts/check_fulltext.py list.csv <folder>`. Every record needs its own article, not a supplement, a form or a page that cites it. Report wrong and missing files to the author before going on.
3. Save each article as `calibration-texts/<DOI with / replaced by _>.md`: the front matter described at the top of `scripts/calibrate.py` (doi, title, year, type, design), then the text that `pdftotext` extracts from the PDF.
4. Rebuild with `--texts calibration-texts`, run the tests, and update the corpus description in `references/calibration.md`. The PDFs are then no longer needed; the texts serve later rebuilds.

## Checks before committing

```bash
python3 scripts/validate_package.py
python3 -m unittest discover -s tests -v
python3 scripts/scan.py --strict --level must SKILL.md $(ls references/*.md references/*/*.md | grep -v sources.md)
```
