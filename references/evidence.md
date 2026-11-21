# Evidence, data and consistency

The groundwork behind every sentence: a source for each claim and each value, data from the best available origin, numbers checked against that origin, and one story told the same way in the plan, the code, the tables, the figures and the text. The agent does this work and reports what it found; the researcher decides what the evidence means.

## Real work, no guessing

- Every aim, direction, method, value and number rests on a source that can be checked or on this study's own data. Nothing rests on assumption or memory.
- Do each task completely. When a step cannot be finished, stop at that step and report it; do not fill the gap with a guess.
- When the agent has no access (a paywalled full text, a database behind a login, data released only on request), it says so and hands the step to the researcher with what is needed: the citation, the link and where to request it.
- At the end of every task, report four lists: done; not done, with the reason; done wrong or found wrong; and what the researcher needs to decide. Nothing is left out of these lists because it looks minor.

## A source for every claim

- Each statement that this study did not produce needs a citation. Cite the primary source; cite a review only for a summary judgment.
- Each method choice cites its precedent and gives its reason: `We used a negative binomial model because the counts were overdispersed, as in [citation].`
- Each parameter, threshold and assumed value has a source, recorded with the page or table it came from.
- Search beyond the local library: PubMed or MEDLINE, Europe PMC, Embase where available, trial registries (ClinicalTrials.gov, WHO ICTRP), guidelines (WHO, NICE, CDC, national bodies) and regulatory documents (FDA, EMA). Label a preprint as a preprint.
- Prefer the newest authoritative source: the current guideline, the latest systematic review, the latest round of a burden study.
- Check every reference before it goes in: it is the paper the record describes, it says what the sentence claims, the version cited is the version of record, and it has not been retracted (the next three sections).
- Never cite from memory and never invent a reference. In a draft, mark a missing source as missing (HYG-05 catches the placeholder) and find it before submission.
- Before screening full texts, check that each file is the article it is filed as: DOI, title, first author, year and journal against the record. Retrieval often returns the wrong article, a supplement, a disclosure form or a page that only cites the article: a commentary, a correction, a patient page. `scripts/check_fulltext.py` compares a folder of PDFs with the reference list. It accepts a PDF as the article only when the record's title is printed at the top of the first page, and it lists missing articles, wrong files, duplicates, supplements and PDFs of one or two pages.

## Does the source support the sentence

- Split the sentence into its claims: whether the effect exists, its direction, its size, the population and setting, the period, and how causal the wording is. Check each claim against the source.
- Record how far the source was read: full text, abstract only or not obtained. Only the full text can support a number, a subgroup or a population.
- Give each claim one of six verdicts: supported; overstated (the source says less, or says it with more caution); wrong number or denominator; wrong population, setting or period; not supported; cannot be checked, for the researcher to decide.
- A supported claim carries its locator: the page, table or figure, or a short quotation. Without a locator the claim is not verified.
- Check the version cited. A preprint, a conference abstract and the published article can report different numbers.
- Keep three kinds of unverified apart: not searched; searched and not found; not reported in the paper. A search that finds nothing does not show that no study exists: write `we found no study of X in [databases, dates]`, not `no study has examined X`.

## Checking references

- A reference is verified only when its title, first author, year and journal match the bibliographic record. A DOI that resolves is not enough, because it can resolve to another paper. List each field that differs.
- When two or more records fit equally well, mark the reference ambiguous and ask the researcher which is meant.
- A failed query is not a verdict. Run it again, and report the check as not done if it still fails.
- Give each reference its DOI or PMID where one exists, and list the references without one for checking by hand.
- `scripts/check_references.py` checks a RIS, BibTeX or DOI list against Crossref and PubMed and gives each reference one verdict: verified, fields differ, ambiguous, not found, query failed or retracted. With `--manuscript` it also checks that every numbered citation has an entry, every entry is cited, and the numbers follow the order of first citation without gaps. Use search tools (PubMed, Europe PMC, Crossref, OpenAlex) to find a paper or to check one or two; for a whole list use the script, which returns one table instead of a long record for each reference.

## Retracted and corrected articles

- Deal with every retracted reference: remove it, replace it with a valid source, or say in the text that it was retracted when the retraction is the point. Take them in order of what they support. A reference behind a main conclusion comes first: tell the researcher at once, because the analysis may need to be redone. Supporting and background citations follow.
- Check again just before submission and before each revision, because papers are retracted while manuscripts are under review.
- PubMed is the reference for retraction status. When Crossref and PubMed disagree, report both.
- Report corrections and expressions of concern too, and check whether a correction changes the number cited.

## Finding data

- Order of preference: official statistics and surveillance (WHO, national agencies); registries; curated databases (Global Burden of Disease, UN World Population Prospects, World Bank indicators, DHS); deposited datasets (Dryad, Zenodo, Figshare); the supplements of published papers; values read off published figures, as a last resort, naming the digitizing tool.
- Take the newest release and the most complete, official source. When another source is used, say why.
- Search beyond papers: national statistics offices, national plans, insurance payment standards and price lists. When a source needs registration to download, list it for the researcher in order of importance, with the page or table to look at.
- When a source issues a new release that revises earlier years, replace the whole series with the new release and record which release it is. List the places checked that needed no change, and the sources confirmed to have no newer release.
- A number that cannot be verified is not used. Go back to the last verified value and label it an assumption.
- Record for each source: name, release or version, access date, URL or DOI, license and any processing. The record lives in the data section of the research plan and in the data dictionary ([research-plan.md](research-plan.md)).

## Verifying data

- Compare imported data with the source: totals, a random sample of rows, ranges, units, denominators and missing-value codes. Reconcile with published figures such as national totals.
- In a systematic review, two people extract the data independently; check extracted numbers against the tables of each paper and report agreement.
- Keep values entered by hand in a table that gives, for each value, the source and the page or table.
- When two numbers disagree, list the possible causes first (a new release that revised earlier years, a changed definition, a different denominator, rounding, a change in composition, a data error), then run the check that best tells them apart. When the causes cannot be separated, report them together and say what data would separate them.
- Compare a result with a published estimate only when the population, period, definition and denominator are the same. Otherwise write that the two are not comparable, and why.
- When two places disagree, correct a value only when the right one can be checked (by arithmetic, or against the analysis output or the source table). Otherwise list both locations and ask which is right; do not choose for the author.
- After each analysis, check the main numbers against an independent calculation or the previous run. Record a discrepancy in `execution_log.md` before fixing it ([execution-log.md](execution-log.md)).

## Logical consistency

- Abstract, main text, tables, figures and supplement report the same numbers. `scripts/check_numbers.py` finds percentages that do not match their counts, estimates outside their intervals, abstract numbers that appear nowhere else, and P values that their t, z, χ² or F statistic and degrees of freedom cannot give. It notes ratio intervals that are off-center on the log scale and tests it cannot recompute (one-sided, corrected, exact or resampling). For means of integer data (Likert items, counts), `--grim-items` adds the GRIM test (Brown and Heathers 2017): with n people each scored as the average of k integer items, a mean is a multiple of 1/(n × k), which can be tested when n × k is below 10 to the power of the decimals reported; a summed score counts as one item.
- Plan, code and paper describe the same method: the same definitions, covariates, model and outcomes.
- Methods and Results match both ways. List each analysis the Methods describe but the Results do not report, and each one reported but not described, and check that every departure from the registered protocol is disclosed (for systematic reviews, PRISMA 2020 item 24c).
- Counts add up: subgroups sum to totals, and the numbers in the flow diagram match the text.
- Each claim in the Discussion follows from a result in the paper. Causal wording needs a causal design, and implications stay within the population, setting and design studied.
- One name for each outcome, exposure and group throughout; abbreviations defined once and used the same way.
- Each figure shows what its legend says, with the axes and units the text uses.
- Results that did not work out are reported with the rest.

## Who does what

- The agent searches, retrieves, extracts, cross-checks, formats citations and lists every discrepancy with its location.
- The researcher chooses the sources when they conflict, judges whether a discrepancy matters, and decides what the evidence supports.
