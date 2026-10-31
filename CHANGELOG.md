# Changelog

## 2.6.0

Released 2026-11-01.

- New check FMT-06 in `scan.py`: an abbreviation used before its full term or never defined. The running text keeps one list of definitions and every legend and table note its own; reference lists, back matter, registry numbers and terms readers know (CI, SD, HIV, WHO and the like) are skipped. Review level, density level in laboratory and computational papers, where gene and cell-line names fill the text.
- Core rules in `SKILL.md`: professional and direct wording (the field's standard term or the plain word, no shorthand coined during the work), and no abbreviation before its full term in each part and each separate document. `references/craft.md` shows how; `references/format.md` covers trial acronyms in titles and published names of instruments and databases.
- `references/study-types/trial.md`: a sample size fixes power and α and solves for the minimum number, takes the standard deviation of the analysed outcome from its source (never a standard error), matches the design, and states α the same way everywhere.
- `references/workflow.md`: a finished plan, analysis or document gets an independent review by another model or agent where one is available; co-authors' current copy, wording and comments are respected; the abstract, text, tables, supplement, registration and letters are checked against each other before submission.
- Saved Word files must open without repair or field-update prompts.

## 2.5.2

Released 2026-10-30.

- The three wording files and the examples are a third shorter (4716 to 3162 words), with every rule ID and corpus figure kept. Each point now sits in one file: formal substitutes, contrast-frame rates and sentence-initial signposts in `references/patterns.md`, abbreviations in `references/format.md`, legend and figure rules in `references/figures-tables.md`, and what to keep in the Keep list of `SKILL.md`. General writing advice the model already follows is gone.
- `references/examples.md` keeps the eight examples no other file shows, and a short list of sentences to leave alone.

## 2.5.1

Released 2026-10-30.

- Leaner `SKILL.md`, checked against Anthropic's skill authoring guidance: each rule stated once (the four lists, second opinions now only in `references/workflow.md`), study-type files linked directly so every reference is one level from `SKILL.md`, and maintainer-only files marked as such.
- Contents lines at the top of the reference files longer than 100 lines; the figure-diagram layout and the LEX-04 rates stated in one place each.

## 2.5.0

Released 2026-10-30.

- Why craft: the name stands for a craftsman's care, exacting in every detail, never satisfied with almost right, and carrying the maker's own hand. It is now principle 7 in `SKILL.md` and a section of both READMEs.
- Personal style file (`references/personal-style.md`): each researcher keeps `~/.biomed-craft/style.md` on their own computer. It is read before every task, with general entries kept apart from entries for particular documents, study types, journals, and figures and tables. Explicit instructions are saved at once. Habits seen in revisions wait in Pending until they recur three times across two documents and the researcher confirms them.
- `scripts/style_diff.py`: compares a draft with the researcher's revision, or reads one Word file with tracked changes. It lists replaced words, deletions, rule findings removed or introduced and profile shifts, sets aside edits to numbers and citations, and proposes scoped candidate entries.
- `scan.py` reads the style file (`--style`, `--no-style`). Rules permitted by `Allow [ID]` entries in the matching scope are listed apart; internal-material rules are never allowed.

## 2.4.2

Released 2026-10-28.

- Each project may have one shared file, `analysis/style.R`, with the fonts and the table format only; analysis, data and plotting code stay in the scripts (`references/analysis-code.md`, CODE-06).

## 2.4.1

Released 2026-10-28.

- Figure files, corrected: the scripts write each figure as PDF and TIFF to `figures/`, and the manuscript package carries one format, because `figures/` keeps the originals.
- Diagrams drawn by hand are separated from result figures made by code (`references/figures-tables.md`). A diagram's drawing file is the original. The diagram matches the plan and the code and is redrawn when the model changes. It follows model-structure and flow-diagram conventions and has a short legend.
- Legends and table notes, measured in the library's open-access research articles. Medians run from about 50 words (BMJ, Lancet) to 200 (Cell), and from 44 (economic evaluations) to 211 (laboratory papers). Method details appear in fewer than one legend in five in Lancet and BMJ papers. A legend holds what a reader needs to read the figure, and computation and definitions go to the Methods; main-text legends in clinical and population research stay under about 120 words plus abbreviations, and legends do not repeat numbers the figure or a table gives. Table notes hold the statistic format, abbreviations, symbols and keyed definitions, with lengths by journal. The NEJM legend length was wrong (20–60 words) and is now about 100 to 130.
- Briefing a supervisor (`references/workflow.md`): what to cover for each figure and each table.

## 2.4.0

Released 2026-10-28. From the author's recent work on figures and tables across five papers, chiefly their checks for figures and tables that show the same information.

- Choosing the display items (`references/figures-tables.md`). Each result appears once, in a figure or a table, in the main text or the supplement (ICMJE, EASE). The section lists what does not count as duplication: source data behind plotted points, reference rows, a GRADE profile behind its summary table, study lists, forest-plot diamonds and reporting forms; a systematic review keeps its PRISMA diagram. A figure shows a shape and a table gives exact values (Gelman et al.). An overlap is resolved by planning the set along the Results, never by deleting one item of the pair. One message per figure; named strata in every main result; figures benchmarked against real figures in leading journals.
- Layout and type. All text in figures and tables uses the manuscript's font (Times New Roman unless the journal asks for another; check with `pdffonts`). Equal margins, even spacing and aligned panels; a crowded figure is redesigned, not shrunk. Horizontal keys with the unit on the title line; no table inside a panel; stack only parts of a whole. In model diagrams, one parameter symbol per arrow, rates in a transition table, no junction dots and no background deaths, and the diagram is redrawn when the model changes.
- Making, changing and checking. Outputs change only through their scripts, and values are confirmed unchanged after a cosmetic edit. One file per figure, with the plotted values in `data/output/`; Word files of main figures and main tables. After any change, renumber and update every pointer. Figures are briefed one at a time and changes shown rendered, and someone other than the maker checks the set. Rendered pages are checked; legends match the current data; figure and text use the same statistic, with totals summed draw by draw.
- Supplements: every item is cited in the main text in order of first citation and adds something; very long tables go in a separate spreadsheet; `figures/` and `tables/` are flat. `references/study-types/systematic-review.md` says when the credibility table may repeat a forest-plot estimate, and keeps screening counts out of the extraction workbook.

## 2.3.1

Released 2026-10-27.

- The JAMA narrative review that was missing from the publisher PDFs is now in the calibration. Its structure corrected the JAMA line in `references/study-types/review.md`: the Methods name the databases, search dates and selection, and the body sits under Discussion and Observations.
- The study type comes from the researcher and goes to `scan.py --type`; the guess is a fallback (`SKILL.md`, `references/study-types.md`).

## 2.3.0

Released 2026-10-27.

- Study-type detection is right for about seven in eight hand-labelled articles from leading journals, up from four in five. Reviews are recognised from what they say about themselves in their first 1000 words, unless systematic-review methods appear. A Mendelian randomisation study has to name itself. Early-phase trials count as trials (phase 1 and 2, first-in-human, dose escalation, open-label). Emulated target trials are observational. Polygenic risk scores are not prediction models. Trial terms can no longer be outweighed by a few diagnostic or prediction terms. Modelling terms now include averted outcomes, forecasts, microsimulation and uncertainty intervals, and modelling terms no longer outweigh an economic evaluation. `calibrate.py` never types a research article as a review.
- Dashes. `SKILL.md` tells the agent not to use a dash to explain or rename what came before. Spaced en dashes used as dashes are must-fix outside laboratory methods (STR-02). A dash before a one- or two-word reveal at the end of a sentence is must-fix (STR-11, new). The em dash hint names the habit (STR-01), and the style profile now counts spaced en dashes with em dashes. Measured in leading-journal research: about 0·5 dashes per 1000 words; a third of papers use a pair around an aside, and one in ten ends a sentence with a dash and a short explanation.
- Journal formats checked on the PDFs themselves (`references/journals.md`). Science Research Articles open with unheaded introductory paragraphs. In 2026 issues they print Materials and methods after the Discussion and label data availability `Data, code, and materials availability:`. NEJM writes `P=0.03`, and its print edition adds thin spaces around the sign.
- A rewrite case for explanatory dashes (`tests/fixtures/cases.json`).

## 2.2.0

Released 2026-10-27.

- `check_fulltext.py` accepts a PDF as an article only when the record's title is printed at the top of its first page. A page that only cites the article (a patient page, a correction, a commentary) no longer counts, and the record is reported missing. Supplements, disclosure and data-sharing forms and reproducibility checklists are listed with their record instead of being counted as the article. PDFs of one or two pages are flagged, while corrected articles with an erratum banner still count. These were all found on a real set of downloads.
- Publisher PDFs of NEJM, JAMA, Science and Science Translational Medicine articles from 2016 to 2024, outside COVID-19, are now part of the calibration. Their texts stay on the author's computer in `calibration-texts/`, which git ignores; `calibrate.py --texts` reads them with hand-checked labels; `validate_package.py` fails if one is committed.
- `calibrate.py`: DOI-shaped file names come first (Science prints its own DOI only at the end of the article), including Science file names; NEJM protocols, disclosure forms and JAMA online supplements are skipped; and lines such as `References (36-38)` in a list of supplementary materials no longer hide the rest of the text. The year is now read from Science footers.
- Journal formats checked against the new articles (`references/journals.md`). NEJM and JAMA close up four-digit numbers. Recent NEJM papers point to `available at NEJM.org`. JAMA trials put the protocol and the analysis plan in Supplement 1. JAMA itself prints the reporting-guideline sentence mainly in trials and reviews. The design line in JAMA names the design. Science and Science Translational Medicine figure titles often state the finding in laboratory papers.
- Rates quoted in `references/patterns.md`, `references/craft.md` and `references/calibration.md` match the current calibration again (some dated from the first corpus).

## 2.1.0

Released 2026-10-27.

- Formal protocols and statistical analysis plans: SPIRIT 2025 content, the separate analysis plan, and what ethics committees and reviewers flag (`references/documents.md`).
- Checks before submission for every study type: the gap behind the aim, the abstract against the text, numbers that reconcile, and the statements leading journals expect (`references/sections.md`).
- Rewrite cases for research plans, execution logs, code comments, a post hoc exclusion, a prediction-model review and a number check (`tests/fixtures/cases.json`).
- After a blind test on ten cases: `check_numbers.py` now reads `Of N, n (p%)`, compares an inline `Abstract:` paragraph with the text, and no longer misreads a bare interval; DEF-12 flags repeated thanks and self-praise in replies to reviewers; META-13 flags a decision made after screening or unblinding that is called prespecified; values that disagree are corrected only when the right one can be checked.

## 2.0.0

Released 2026-10-27. The skill is now biomed-craft (formerly plain-paper): end-to-end help with biomedical research, starting from writing.

- Principles and confirmation points for working with the researcher, from the research question to the reply to reviewers (`references/workflow.md`), and the rule that every task ends with what was done, not done, done wrong and still to decide.
- Content and conventions for thirteen study types (`references/study-types/`), built from leading-journal articles, the current reporting guidelines and the author's own projects and reviews.
- Three layers: a general standard, the journal's structure and format, and the study type. `scan.py --type` sets or guesses the study type; rule levels and reference groups follow it.
- Research plans, execution logs, analysis code, comments and project folders (`--doc plan`, `--doc log`, `--doc code`), and evidence, data and consistency (`references/evidence.md`).
- New checks: `check_numbers.py` (percentages, intervals, abstract against text) and `check_fulltext.py` (retrieved PDFs against the reference list).
- A larger calibration corpus: open-access publisher versions from Europe PMC (NEJM, JAMA journals, BMJ, Science, Sci Transl Med, Cell, Lancet journals, Nature Medicine) read as JATS XML, with study designs labelled and per-design groups; rules corrected for the false positives the new articles showed.
- Leading journals instead of flagship journals throughout; no article counts in the skill text; peer review and replies to reviewers (`references/review-response.md`).

## 1.0.0

Released 2026-10-26.

- `SKILL.md` with modes for drafting, optimising, reviewing and checking English academic writing.
- Eleven reference files: sentence craft, sections, journal styles, figures and tables, process and engineering register and defensive writing, AI-style patterns, other documents, numbers and format, calibration, examples, sources.
- `scan.py` with 83 rules in ten categories, reading Word, Markdown, Quarto, LaTeX, PowerPoint, PDF, SVG and R or Python plotting code, with a style profile against leading journals.
- `check_preservation.py` for numbers, citations, cross-references and links after an edit.
- `calibrate.py`, and a calibration built from research articles in leading journals and their major sub-journals.
- Unit tests, rewrite cases for agent evaluation, package validation and CI.
