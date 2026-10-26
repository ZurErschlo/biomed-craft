# plain-paper

English | [中文](README.zh-CN.md)

[![Check package](https://github.com/ZurErschlo/plain-paper/actions/workflows/validate.yml/badge.svg)](https://github.com/ZurErschlo/plain-paper/actions/workflows/validate.yml)

An agent skill for writing, editing and reviewing English academic text to the standard of flagship journals (Lancet, NEJM, JAMA, BMJ, Nature, Science, Cell) and their major sub-journals. It also removes AI-style patterns, engineering jargon, defensive hedging and narration about the writing process. It covers every section of a research article, supplementary material, figure legends, table notes and text inside figures, as well as protocols, response letters, consent forms and slides.

The rules come from four sources, in this order of priority: the author's own editing decisions on manuscripts, protocols, figures and slides; 124 research articles from flagship journals and their major sub-journals (main text, supplements, figures and tables); public skills for removing AI-style writing; and journal instructions and reporting guidelines. The skill uses the [Agent Skills](https://agentskills.io) format and works with Claude Code, Codex and other agents that read `SKILL.md`.

## The five most common problems

```text
Contrast frame          The central gap is not cost. It is coverage.
Process narration       In the revised version, we reran the pipeline (see 02_model.R).
Engineering register    Our pipeline cleaned and merged the records with seed = 2024.
Defensive writing       It is important to note that these estimates could potentially change.
Internal legend text    Figure 2: This figure shows incidence from amr_rate_v2, suggesting a decline.
```

After editing:

```text
Coverage was the main constraint: uptake fell from 64% to 41% in districts that lost nurses.
We linked notification and laboratory records by national identifier and removed duplicates.
The estimates depend on the assumed duration of infectiousness (appendix p 9).
Figure 2: Incidence of drug-resistant tuberculosis by WHO region, 2010–2022
```

## Installation

With the skills CLI (recommended; it links the skill to the agents installed on your machine):

```bash
npx skills add ZurErschlo/plain-paper
```

As a Claude Code plugin:

```text
/plugin marketplace add ZurErschlo/plain-paper
/plugin install plain-paper@plain-paper
```

Or clone it into your agent's skills folder:

```bash
git clone https://github.com/ZurErschlo/plain-paper.git ~/.claude/skills/plain-paper
```

For Codex use `~/.codex/skills/plain-paper`. For other agents, put the folder in their skills directory or point them to `SKILL.md` at the repository root.

## Usage

Ask for what you need; the agent loads the skill and the references it requires:

- Draft: "Use plain-paper to write the Results from these tables for The Lancet Infectious Diseases."
- Optimise: "Polish this Discussion and remove the AI-style and defensive wording."
- Review: "Review this Methods section item by item, with columns Original, Revised and Reason."
- Check: "Check the R plotting code in figures/ and the legends for variable names, file names and other project-only labels."

The checking scripts run on their own (Python 3.10 or later, standard library only; PDF input needs `pdftotext`):

```bash
python3 scripts/scan.py manuscript.docx
python3 scripts/scan.py --profile --journal lancet draft.md
python3 scripts/scan.py --strict legends.md figures/*.R
python3 scripts/check_preservation.py original.docx revised.docx
python3 scripts/calibrate.py ~/Zotero
```

`scan.py` reads Word, Markdown, Quarto, LaTeX, PowerPoint, PDF, SVG, and R or Python plotting code. It lists findings by rule ID and compares sentence length, hedges, connectives and contrast frames with the ranges found in flagship journals. `check_preservation.py` compares the numbers, citations, figure, table and appendix references, and links before and after an edit, so you can confirm that no fact was lost or added. `calibrate.py` rebuilds the reference rates from a folder of flagship-journal PDFs in your own field.

## How it works

- `SKILL.md` sets the workflow: identify the document, section, study design and target journal; then deal with process narration, engineering register, defensive writing, AI-style sentence shapes and vocabulary, section conventions and journal style, in that order; then check the result.
- `references/` holds the detail, loaded when needed: sentences and paragraphs, sections, journal styles, figures and tables, the kinds of text that do not belong in a paper, AI-style patterns and word lists, other document types, numbers and format, the calibration corpus, worked examples and sources.
- `scripts/rules.json` holds 83 rules at three levels: must (flagship journals almost never print it, or it is internal material), review (judge in context) and density (common in flagship journals; reported only as a rate). Every rule comes with examples it must match and examples it must not match.
- Levels follow the corpus: a word or construction is must-fix only if it appears in about 3% or fewer of research articles published in flagship journals before 2023.

| Category | Covers | Rules |
|---|---|---|
| CON | Contrast frames ("not X but Y" and relatives) | 10 |
| DEF | Defensive hedging and disclaimers | 11 |
| META | Process and metadata narration | 11 |
| ENG | Engineering and software register | 9 |
| LEX | Words flagship journals rarely print | 10 |
| STR | Sentence shapes and punctuation | 10 |
| HYG | Internal material (file names, variable names, placeholders) | 11 |
| FMT | Numbers, grammar and format | 5 |
| CAP | Figure legends and table notes | 1 |
| FIG | Text inside figures | 5 |

## Verification

```bash
python3 scripts/validate_package.py
python3 -m unittest discover -s tests -v
```

The tests cover every rule's examples, each input format, the command-line options and exit codes, a flagship-style passage with no findings, and a guard that keeps must-level style rules rare in pre-2023 flagship articles. CI runs them on Linux, macOS and Windows with Python 3.10 and 3.13, and checks the skills CLI discovery and the Claude Code plugin manifest. `tests/fixtures/cases.json` holds rewrite cases for testing an agent with the skill; [tests/README.md](tests/README.md) explains how to score them.

The corpus leans towards infectious disease, antimicrobial resistance and modelling, and the NEJM, BMJ, JAMA and Science groups are small, so their reference ranges are rough.

## Sources

The full list is in [references/sources.md](references/sources.md). The main public sources are [blader/humanizer](https://github.com/blader/humanizer), [op7418/Humanizer-zh](https://github.com/op7418/Humanizer-zh), [hardikpandya/stop-slop](https://github.com/hardikpandya/stop-slop) and [matsuikentaro1/humanizer_academic](https://github.com/matsuikentaro1/humanizer_academic), together with research on the vocabulary of language models in scientific writing by Kobak and colleagues (Science Advances 2025) and Liang and colleagues (Nature Human Behaviour 2025). All wording in this repository is original; repositories without a licence or with a non-commercial licence contributed ideas only and are credited.

## Version history

See [CHANGELOG.md](CHANGELOG.md).

## License

[MIT](LICENSE)
