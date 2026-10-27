# Evidence, data and consistency

The groundwork behind every sentence: a source for each claim and each value, data from the best available origin, numbers checked against that origin, and one story told the same way in the plan, the code, the tables, the figures and the text. The agent does this work and reports what it found; the researcher decides what the evidence means.

## Real work, no guessing

- Every aim, direction, method, value and number rests on a source that can be checked or on this study's own data. Nothing rests on assumption or memory.
- Do each task completely. When a step cannot be finished, stop at that step and report it; do not fill the gap with a guess.
- When the agent has no access (a paywalled full text, a database behind a login, data released only on request), it says so and hands the step to the researcher with what is needed: the citation, the link and where to request it.
- At the end of every task, report four lists: done; not done, with the reason; done wrong or found wrong; and what the researcher needs to decide. Nothing is left out of these lists because it looks minor.

## A source for every claim

- Each statement that this study did not produce needs a citation. Cite the primary source; cite a review only for a summary judgement.
- Each method choice cites its precedent and gives its reason: `We used a negative binomial model because the counts were overdispersed, as in [citation].`
- Each parameter, threshold and assumed value has a source, recorded with the page or table it came from.
- Search beyond the local library: PubMed or MEDLINE, Europe PMC, Embase where available, trial registries (ClinicalTrials.gov, WHO ICTRP), guidelines (WHO, NICE, CDC, national bodies) and regulatory documents (FDA, EMA). Label a preprint as a preprint.
- Prefer the newest authoritative source: the current guideline, the latest systematic review, the latest round of a burden study.
- Check every reference before it goes in: the DOI resolves, the paper says what the sentence claims, the version cited is the version of record, and it has not been retracted.
- Never cite from memory and never invent a reference. In a draft, mark a missing source as missing (HYG-05 catches the placeholder) and find it before submission.
- Before screening full texts, check that each file is the article it is filed as: DOI, title, first author, year and journal against the record. Retrieval often returns the wrong article, a supplement, a disclosure form or a page that only cites the article: a commentary, a correction, a patient page. `scripts/check_fulltext.py` compares a folder of PDFs with the reference list. It accepts a PDF as the article only when the record's title is printed at the top of the first page, and it lists missing articles, wrong files, duplicates, supplements and PDFs of one or two pages.

## Finding data

- Order of preference: official statistics and surveillance (WHO, national agencies); registries; curated databases (Global Burden of Disease, UN World Population Prospects, World Bank indicators, DHS); deposited datasets (Dryad, Zenodo, Figshare); the supplements of published papers; values read off published figures, as a last resort, naming the digitising tool.
- Take the newest release and the most complete, official source. When another source is used, say why.
- Record for each source: name, release or version, access date, URL or DOI, licence and any processing. The record lives in the data section of the research plan and in the data dictionary ([research-plan.md](research-plan.md)).

## Verifying data

- Compare imported data with the source: totals, a random sample of rows, ranges, units, denominators and missing-value codes. Reconcile with published figures such as national totals.
- In a systematic review, two people extract the data independently; check extracted numbers against the tables of each paper and report agreement.
- Keep values entered by hand in a table that gives, for each value, the source and the page or table.
- When two places disagree, correct a value only when the right one can be checked (by arithmetic, or against the analysis output or the source table). Otherwise list both locations and ask which is right; do not choose for the author.
- After each analysis, check the main numbers against an independent calculation or the previous run. Record a discrepancy in `execution_log.md` before fixing it ([execution-log.md](execution-log.md)).

## Logical consistency

- Abstract, main text, tables, figures and supplement report the same numbers. `scripts/check_numbers.py` finds percentages that do not match their counts, estimates outside their intervals and abstract numbers that appear nowhere else.
- Plan, code and paper describe the same method: the same definitions, covariates, model and outcomes.
- Counts add up: subgroups sum to totals, and the numbers in the flow diagram match the text.
- Each claim in the Discussion follows from a result in the paper. Causal wording needs a causal design, and implications stay within the population, setting and design studied.
- One name for each outcome, exposure and group throughout; abbreviations defined once and used the same way.
- Each figure shows what its legend says, with the axes and units the text uses.
- Results that did not work out are reported with the rest.

## Who does what

- The agent searches, retrieves, extracts, cross-checks, formats citations and lists every discrepancy with its location.
- The researcher chooses the sources when they conflict, judges whether a discrepancy matters, and decides what the evidence supports.
