# Changelog

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
