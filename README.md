# biomed-craft

English | [中文](README.zh-CN.md)

[![Check package](https://github.com/ZurErschlo/biomed-craft/actions/workflows/validate.yml/badge.svg)](https://github.com/ZurErschlo/biomed-craft/actions/workflows/validate.yml)

An agent skill for biomedical research, from the research question to the published paper and the reply to reviewers. It starts from writing and goes beyond it: study design, research plans and execution logs, data and evidence, analysis code, figures and tables, manuscripts, reporting checklists and peer review.

The researcher stays the author. The researcher decides the question, the design, the values that drive the result, the interpretation and what is submitted; the agent prepares the evidence for each decision, does the groundwork (finding and verifying literature and data, checking that numbers agree, drafting and polishing), stops at defined confirmation points, and ends every task by reporting what was done, what was not done and why, what went wrong, and what the researcher needs to decide. Nothing rests on guesses or numbers recalled from memory.

The skill uses the [Agent Skills](https://agentskills.io) format and works with Claude Code, Codex and other agents that read `SKILL.md`.

## What it covers

- **Writing to the standard of leading journals** (Lancet, NEJM, JAMA, BMJ, Nature, Science, Cell and their major sub-journals): every section, supplements, figure legends, table notes and text inside figures, without AI-style patterns, engineering register, defensive hedging or narration about the process.
- **Three layers**: a general standard for wording and shared conventions; the target journal's structure and format; the conventions and required content of the study type.
- **Thirteen study types**: randomised trials, observational and database studies, Mendelian randomisation, systematic reviews and meta-analyses, narrative reviews, health economic evaluations, diagnostic accuracy, clinical prediction models, disease and epidemiological modelling, laboratory and mechanistic studies, computational and omics studies, qualitative and mixed-methods studies. Each file lists the content a paper must contain, what reviewers flag and how strong papers avoid it, and the writing conventions of leading journals.
- **The rest of a project**: research plans written as a specification someone else could follow, execution logs, analysis scripts that run section by section in RStudio, comments, and project folders.
- **Evidence and consistency**: a source for every claim and value, the newest official data, numbers checked against their source, retrieved full texts checked against the reference list, and one story told the same way in the plan, the code, the tables and the text.

## Installation

With the skills CLI:

```bash
npx skills add ZurErschlo/biomed-craft
```

As a Claude Code plugin:

```text
/plugin marketplace add ZurErschlo/biomed-craft
/plugin install biomed-craft@biomed-craft
```

Or clone it into your agent's skills folder:

```bash
git clone https://github.com/ZurErschlo/biomed-craft.git ~/.claude/skills/biomed-craft
```

For Codex use `~/.codex/skills/biomed-craft`.

## Usage

- "Draft the Results of this cohort study from tables 1–3 for JAMA Internal Medicine."
- "Polish this Discussion; the target journal is not decided yet."
- "Review this meta-analysis against the systematic-review checklist and list what is missing."
- "Check research_plan.md and the scripts in analysis/."
- "Check that these 120 PDFs are the articles in included.ris before we screen them."
- "Help me answer the reviewers; here are the comments and the manuscript."

The scripts run on their own (Python 3.10 or later, standard library only; PDF input needs `pdftotext`):

```bash
python3 scripts/scan.py manuscript.docx
python3 scripts/scan.py --type prediction --profile draft.md
python3 scripts/scan.py --doc code analysis/
python3 scripts/check_numbers.py manuscript.docx
python3 scripts/check_fulltext.py included.ris fulltexts/
python3 scripts/check_preservation.py original.docx revised.docx
```

`scan.py` reads Word, Markdown, Quarto, LaTeX, PowerPoint, PDF, SVG and R or Python code, guesses the study type, and reports findings by rule, with levels that follow the study type and journal. `check_numbers.py` finds percentages that do not match their counts, estimates outside their intervals and abstract numbers that appear nowhere else. `check_fulltext.py` lists retrieved PDFs that are the wrong article, a supplement or a duplicate, and records with no PDF. `check_preservation.py` confirms that an edit kept every number, citation and cross-reference.

## How it is built

- `SKILL.md`: principles, start-up checks, where to look, core writing rules and output.
- `references/`: one topic per file, loaded when needed: working with the researcher stage by stage, evidence and data, study types, sections, sentences, journals, figures and tables, register, AI-style patterns, research plans, logs, code, folders, peer review, documents, numbers, calibration, examples and sources.
- `scripts/rules.json`: the wording rules, each with examples it must and must not match. A word is must-fix only when research articles in leading journals almost never print it, checked separately for each journal family and study design.
- `scripts/calibrate.py`: rebuilds the reference rates from PDFs and from open-access publisher versions in Europe PMC.

## Sources

Built from research articles in leading journals and their supplements, the current reporting guidelines (CONSORT 2025, SPIRIT 2025, PRISMA 2020, STROBE, CHEERS 2022, STARD, TRIPOD+AI and others), the author's own projects and editing decisions, and public skills including [blader/humanizer](https://github.com/blader/humanizer), [K-Dense-AI/scientific-agent-skills](https://github.com/K-Dense-AI/scientific-agent-skills), [Yuan1z0825/nature-skills](https://github.com/Yuan1z0825/nature-skills) and [Imbad0202/academic-research-skills](https://github.com/Imbad0202/academic-research-skills) (ideas only). The full list is in [references/sources.md](references/sources.md).

## Version history

See [CHANGELOG.md](CHANGELOG.md).

## License

[MIT](LICENSE)
