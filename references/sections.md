# Sections of a research article

What each part of a research article does in leading journals and their major sub-journals, with templates, from close reading of research articles, reviews and supplements across study designs. Journal-specific formats are in [journals.md](journals.md).

## Title

- Name the topic, population and setting. Add place, period or scale where it matters: `in 120 countries`, `1990–2021`.
- Lancet family: topic, colon, design label with an article: `…: a randomised, placebo-controlled trial`, `…: a modelling study`. BMJ: the same without the article: `…: prospective cohort study`. NEJM: a short noun phrase with no design label. JAMA: often `Association of X With Y Among Z`.
- Clinical titles in Lancet, NEJM, BMJ and JAMA do not state the result. NEJM rewrote one author's result-stating title into a neutral one before publication.
- Titles avoid questions, puns, `novel`, `first`, `insights` and abbreviations other than trial acronyms.

## Abstract or Summary

- Follow the journal's structure exactly (journals.md).
- Background: two to four sentences: burden with a number, the gap, then the aim (`We aimed to…`).
- Methods: open with the design, setting and period (`We did a… at [N] sites in [countries] between [date] and [date]`), then eligibility, allocation, the primary outcome and the analysis population. End with registration where required.
- Findings or Results: trials open with dates and counts enrolled; reviews with records screened; models with the headline estimate. Give estimates with intervals.
- Interpretation or Conclusions: one to three sentences. The verb matches the design (craft.md). Lancet Interpretation may give a recommendation; NEJM Conclusions restate the effect with population and comparator and do not recommend.
- Abstract methods and results must match the main text exactly.

## Panels

- Lancet Research in context: Evidence before this study (search: databases, dates, terms; what it found), Added value of this study (what was done and the key result; a priority claim such as `To our knowledge, this is the first…` is common here and only here, when the search supports it), Implications of all the available evidence.
- BMJ What is already known on this topic / What this study adds: two or three short declarative bullets each, without references.
- JAMA Key Points: Question (one sentence); Findings (`In this [design] of [N] [people], …` with the key number); Meaning (usually `These findings suggest…`).

## Introduction

Two to five paragraphs. The order is almost universal:

1. Burden or scale, with a number, year and source: `In 2023, an estimated 10·8 million people developed tuberculosis.`
2. What is known: earlier evidence named by design and size or by trial name.
3. The gap, made specific: the missing estimate, comparison, population or design, ideally with a number. Vague gaps (`poorly understood`, `remains unclear`) appear only when attached to a concrete object.
4. Why now: a guideline, a target or a decision that depends on the answer.
5. The aim, in one sentence: `We aimed to…` (Lancet), `Here, we report…` (NEJM), `To address this gap, we…` (JAMA), `Here we show…` (Nature, Cell).

Introductions do not list contributions and rarely state hypotheses (laboratory and behavioural studies are the exception). Opening with a general statement of importance (`In recent years, X has attracted increasing attention`) is absent from the corpus (LEX-02).

## Methods

- Open with one sentence giving design, setting and period. Then follow the journal's subheadings for the design:
  - Lancet trials: Study design and participants; Randomisation and masking; Procedures; Outcomes; Statistical analysis; Role of the funding source.
  - NEJM trials: Trial Design and Oversight; Randomization; Procedures; Outcome Measures; Statistical Analysis.
  - Lancet systematic reviews: Search strategy and selection criteria; Data analysis; Role of the funding source.
  - Modelling studies: model structure; data and parameters; fitting; scenarios; uncertainty analysis.
  - Diagnostic accuracy: Index test; Comparator tests; Reference standard.
  - BMJ adds Patient and public involvement. Nature journals put Methods after the Discussion; Cell uses STAR Methods.
- Define the primary outcome in one sentence (`The primary outcome was…`) and list secondary outcomes in the next.
- Statistical analysis follows this order: sample size and power; analysis population; model; prespecified subgroup and sensitivity analyses; multiplicity and sidedness; statistical analysis plan; software with version (`Analyses were done with R, version 4.4.1`).
- Modelling: state where the model comes from, what it was fitted to, the counterfactual, how uncertainty was propagated (uncertainty intervals or credible intervals) and the scenarios. Equations and parameter tables go to the appendix with page pointers.
- Economic evaluation: perspective, currency and price year, outcome (DALYs or QALYs), discount rate, threshold, probabilistic sensitivity analysis, and the CHEERS 2022 statement.
- Methods describe what was done, in the order a reader needs it. Precedent goes in as a short citation; limits go in the Discussion; next steps do not appear.
- Methods describe the methods as they were carried out and give the registration number. When the registration was amended, the amendment is answered in the reporting checklist (PRISMA 2020 item 24c) or in one line of the supplement. A decision made after the data were seen is never called prespecified, and a statement that the primary outcome or eligibility changed stays in.
- Methods describe the analysis in scientific terms. Software steps, file names, seeds and version histories stay out ([register.md](register.md)).
- Name the reporting guideline in one sentence: `The trial is reported according to CONSORT 2025.`
- Ethics approval and consent sit with participants (Lancet, NEJM) or in back matter (JAMA, BMJ). The Lancet ends Methods with a fixed role-of-funder sentence.

## Results

- First sentence by design:
  - Trials: `Between [date] and [date], [N] patients were screened, of whom [N] were enrolled (figure 1).`
  - Systematic reviews: `We identified [N] records, of which [N] studies were included.`
  - Modelling and burden studies: the headline estimate (`In 2021, we estimated [N] (95% UI …) deaths…`).
  - Laboratory studies: a purpose clause is acceptable (`To test whether…, we…`).
- Each paragraph opens with its result and a number. Give denominators and intervals.
- Pointers go in parentheses after the number they support. About 1% of Results sections open with `Table 1 shows`.
- Clinical journals keep interpretation out of Results. Laboratory papers interpret briefly (`suggesting that…`).
- Results in reviews are organised by outcome or theme, never study by study.
- Subheadings: NEJM uses Patients, Primary Outcome, Secondary Outcomes, Safety; Nature uses descriptive or declarative subheadings; Lancet trials often use none.

## Discussion

1. First paragraph: the principal finding with design, population and key estimate (87% of papers): `In this [design] of [population], [finding with number].`
2. Comparison with earlier work: one to five named studies, each with its estimate, and one reason for any difference (design, population, period).
3. Explanation: hedged once (`might reflect`, `probably because`), with supporting evidence where possible.
4. Implications for practice or policy, proportionate to the design.
5. Strengths and limitations: one block (Lancet), subheadings (BMJ, JAMA) or brief (NEJM). Open plainly (`Our study has several limitations.`). Each limitation names its consequence: the direction of bias, what was done about it, or why it is unlikely to change the conclusion. Use `First,… Second,…` for three or more.
6. Future research: specific design, population or outcome, tied to a stated limitation. Bare calls for more research do not occur in the corpus (DEF-07).
7. Final paragraph: the main finding and a proportionate implication. `In conclusion` opens it in about a third of papers; BMJ and JAMA use a Conclusions heading instead.

## Declarations

- Contributors (CRediT roles where required), declaration of interests, data sharing, funding and role of the funder, acknowledgments, ethics.
- Write them as public statements. Data and code availability names the repository or the access route; internal file names, script names and folder paths do not appear.
- Data availability says which data, where (repository and accession number, or the access route and its conditions) and from when. Code availability names a repository that issues a DOI (Zenodo, for example) and the licence. Formats: a Code availability section after Data availability (Nature journals); bullets under Data and code availability (Cell); Data and materials availability with the acknowledgements (Science); a data sharing statement for trials (ICMJE, required by NEJM, JAMA, BMJ and The Lancet).
- Do not draft an AI-use statement for the authors. Keep one the authors wrote if the journal requires it.

## Supplementary material

- A contents list with page numbers comes first. Number items in the journal's style (journals.md).
- Supplements hold full search strings for each database, equations, parameter tables with a source column, calibration targets, scenario and sensitivity analyses, additional results and reporting checklists.
- Same register as the main text, but more procedural and list-like; protocol wording (`will be`) may survive in appended protocols.
- Journals post supplements as supplied, without copyediting. Published supplements show code variable names, arm codes, stale cross-references and placeholders. Bring supplements to main-text standard: same legend structure, abbreviations defined again, public labels, no placeholders, checklist locations updated to the final version.
- Main-text pointers are exact: `(appendix pp 14–17)`, `(Table S1 in the Supplementary Appendix)`, `(eTable 3 in Supplement 1)`, `(Supplementary Table 3)`, `(Extended Data Fig. 2a)`.

## Review articles

- Abstract ends on scope (`In this Review, we describe…`). Nature Reviews adds five Key points.
- A one-sentence roadmap may close the introduction of a review; research articles do not have one.
- Synthesise by theme. Rhetoric, if any, belongs only in the final section on future directions.
