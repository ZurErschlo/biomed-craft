# Systematic reviews and meta-analyses

Intervention reviews, meta-analyses of proportions and prevalence, reviews of costs and economic evaluations, and scoping and bibliometric reviews. Report to PRISMA 2020, with PRISMA-S for the searches, PRISMA-P for the protocol, SWiM for synthesis without meta-analysis and PRISMA-ScR for scoping reviews.

## Before the search

- Register the protocol (PROSPERO for health outcomes) before the formal search. Fill every field and keep it consistent with the manuscript. When the criteria change, amend the registration and record the change in `execution_log.md`.
- Define the outcome as a construct that can be coded: acceptance, intention, willingness and uptake are different outcomes. Record each study's own wording so that construct-restricted analyses are possible.
- Use guideline definitions for populations and places (WHO regions, World Bank income groups for a stated year, the populations named in global guidance) and keep them identical in the title, text, tables and figures.
- Search the databases the question needs, with exact dates (`from 1 January 2003 to 15 April 2026`; `inception` only when it is true). Give the full strategy for each database in the supplement, and state grey literature and reference-list searches, or the reason for none. State any language limit once, the same way everywhere.

## Screening and extraction

- Two reviewers screen titles, abstracts and full texts independently, and a third resolves disagreements. Report agreement.
- Give each excluded full text one primary reason, chosen in a preset order, and map every reason to a criterion in the registration.
- Before screening full texts, check that each retrieved file is the article it is filed as (`scripts/check_fulltext.py`). Count articles that could not be obtained, and files that turned out to be the wrong article, as not retrieved.
- Keep records, reports and studies apart: map reports to studies, merge reports that share participants, and remove secondary compilations that repeat primary studies.
- Extract with a piloted form, in duplicate. Retrieve the supplement of every included study. The second extractor checks against the source without seeing the first values.
- Keep values taken from papers in a hand-maintained workbook, with the page or table for each value. Log every edit (old value, new value, reason, page). Analysis scripts read the workbook and never write to it. The workbook holds only values taken from the included studies; screening counts for the flow diagram are kept elsewhere.
- Freeze the included set before analysis. Reconcile every count in the abstract, flow diagram, text, tables and appendix from the lists of identifiers, overlapping subsets included.

## Synthesis

- Decide for each outcome, after extraction, whether pooling makes sense.
- Random effects: name the estimator (REML), use Hartung–Knapp intervals, report τ² and I², and give a 95% prediction interval with every pooled estimate from three or more studies, noting that it is imprecise below five. When heterogeneity is high, phrase the conclusion around the prediction interval.
- Proportions: a generalised linear mixed model on the logit scale as the main analysis, with exact or Wilson intervals; the Freeman–Tukey transformation only as a sensitivity analysis, because its back-transformation can mislead. If the main model can fall back to another, say which model produced each estimate.
- Zero events: the mixed model needs no continuity correction. Do not drop studies with no events in either arm by default, and do not use a fixed 0·5 correction as the main analysis.
- Several estimates from one sample: choose one by a stated rule and show the rule in a selection table, or model the dependence (multilevel models with t-based inference).
- Take the point estimate and its variance from the same quantity on the same scale. Never build an interval from medians of interval ends, and never combine fields from different rows of the source into one summary row.
- Convert medians to means with an established method and state its assumption; do not convert zero-inflated distributions.
- Costs: back-convert to local currency, inflate with a named index, convert with a stated method (for example Turner and colleagues, 2019), and keep one currency unit within each range or figure.
- Pool nothing when the variance is derived from the estimate itself or the studies share their inputs; describe the results instead.
- Meta-regression and small-study tests need at least ten studies. Study-level covariates give associations across studies, not causal effects. A funnel plot of single proportions does not show publication bias.
- Without meta-analysis: follow SWiM, count votes by the direction of effect and never by statistical significance, and tabulate the results.
- Sensitivity analyses: restriction by risk of bias, other estimators, leave-one-out, and restriction to one outcome construct. Report the sensitivity analyses that were run, not the ones that were planned.

## Appraisal and certainty

- Match the tool to the design: RoB 2 for each result of a trial; ROBINS-I, with its version stated; QUADAS-2 for diagnostic accuracy; QUIPS for prognostic factors; PROBAST for prediction models; JBI checklists for prevalence studies. Report item-level judgements; give no total score or band unless the tool defines one.
- Grade the certainty of each pooled outcome with GRADE, or say why GRADE is not used and give a credibility summary instead: number of studies and participants, estimate, prediction interval, I², weight from studies with critical flaws, small-study test and the range across sensitivity analyses. A pooled estimate that a forest plot shows may appear again in this table, beside what the plot cannot hold; otherwise each number appears in one place ([figures-tables.md](../figures-tables.md)).
- Scoping reviews: appraisal is optional and is never called risk of bias. GRADE-CERQual rates confidence in review findings, not in individual studies.

## Reporting

- Results open with the search: `We identified 4210 records; after removing duplicates, 2876 were screened and 214 full texts assessed; 58 studies (63 reports) were included (figure 1).`
- A table of study characteristics, with place, setting and context, and a full list of included studies in the supplement.
- Risk of bias and small-study results go in the Results, as well as the appendix.
- Pooled single-arm rates are descriptive and never stand in for a treatment effect. Say why single arms were taken from trials.
- Limitations state the language limits, grey literature, the search date and the definition of scope, and the scope reads the same in every section.
- Methods describe what was done. A claim to be the first review is checked against a fresh search before it goes in.
- A search more than about twelve months old at submission is updated; journals reject reviews for stale searches.
- Comments raised by co-authors are tracked and closed before submission. Declarations match the submission history, and any AI help with screening, extraction or appraisal is disclosed.

## Journal formats

- Lancet: Research in context describes the search (databases, dates, terms, language limits). JAMA abstracts use Data Sources, Study Selection, Data Extraction and Synthesis; BMJ abstracts use Data sources, Eligibility criteria for selecting studies, Data extraction and synthesis.
- The PRISMA flow diagram labels each stage and its numbers add up. Forest plots show weights, the estimator and the prediction interval. Maps use one sequential palette with bins that do not overlap, and grey for no data.

## Bibliometric reviews

Give the full query string and the search date, justify the choice of database, refresh the data when more than a year has passed, and read trends against milestones in the field.
