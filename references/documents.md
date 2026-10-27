# Other academic documents

Research articles are the main target. These documents share most of the rules, with the differences below.

## Research protocols and statistical analysis plans

Formal protocols go to ethics committees, registries and journals; the internal working plan of a project is covered in [research-plan.md](research-plan.md). Follow SPIRIT 2025 for trials (with the schedule of enrolment, interventions and assessments, and extensions such as SPIRIT-PRO, SPIRIT-AI and SPIRIT-C for participants up to 19 years), PRISMA-P for systematic-review protocols, the Gamble guideline for statistical analysis plans (the DEBATE extension for observational studies), and a health economic analysis plan for trial-based economic evaluations.

Content:

1. Administrative and open-science items on the title page: a title that names the design, version and date, registration (registry, number, date) before the first participant, where the protocol and analysis plan will be available, the data-sharing plan, funding and the roles of sponsor and funder, conflicts of interest, committees and their roles, and the dissemination plan. Amendments go to the ethics committee and the registry as SPIRIT 2025 asks; the body of the protocol states the current method.
2. Background built on a systematic review of existing evidence, the justification of the comparator, and objectives that cover benefits and harms.
3. Design, framework and allocation ratio, with a justified non-inferiority margin where relevant; plans for patient and public involvement.
4. Eligibility of participants, sites and the people delivering the interventions; interventions in TIDieR detail, with criteria for modifying them, adherence strategies and concomitant care.
5. Each outcome defined by its measurement, metric, aggregation and time point; harms defined, with how they will be collected.
6. The estimand for the primary outcome and key secondary outcomes (population, treatments, end point, summary measure, intercurrent-event strategies), with the main estimator and its sensitivity analyses (ICH E9(R1)).
7. Sample size with sourced assumptions, power, alpha and the allowance for attrition, and the recruitment plan.
8. Randomisation (sequence generation, restriction, stratification), concealment and implementation; masking and the procedure for unmasking.
9. Data collection, management and retention.
10. Statistical analysis: analysis populations, prespecified models and covariates, missing-data assumptions with methods and sensitivity analyses, the multiplicity strategy, a few subgroups each with a hypothesised direction, and interim analyses with stopping rules.
11. Monitoring (data monitoring committee and trial monitoring), ethics, consent (including consent for later use of data and specimens), confidentiality and post-trial care.

The statistical analysis plan is a separate document, finalised before unmasking. It gives outcome derivations, CI levels and sidedness, handling of protocol deviations, methods detailed enough to replicate, shell tables and software.

What reviewers and ethics committees flag: a vague primary outcome; several primary outcomes with no multiplicity plan; no estimand and no plan for intercurrent events; missing-data assumptions not stated; sample-size assumptions with no evidence behind them; an unjustified non-inferiority margin; too many subgroups; `appropriate statistical methods will be used`; a protocol and an analysis plan that disagree; registration after enrolment began or an analysis plan finalised after unmasking; no plan for harms; data sharing left undecided; pilot and feasibility protocols that test efficacy.

Writing: definite future tense (`Participants will be randomly assigned…`); no options left open (`we could also…`, `if feasible`); no status labels (`implemented`, `to do`, `checked`); and no pointers to the project's own working record (META-08, META-09). Known limitations go in a limitations section, stated once with their consequences. Main figures and tables: the SPIRIT schedule, a trial-flow schematic, an estimand table, outcome definitions, the sample-size table, and for systematic-review protocols the draft search strategy.

## Responses to reviewers

- One block per comment: the comment (quoted or summarised), the answer, the change and its location (`Methods, paragraph 3; lines 120–128`).
- Thank the reviewers once at the start. Repeating `We thank the reviewer for this insightful comment` before every answer is boilerplate.
- Answer directly. If you disagree, say so and give the evidence.
- Describing what was changed is the content of this document, so revision narration is fine here (`scan.py --doc response` turns those rules off).
- Avoid procedural self-praise: `we carefully revised`, `we ensured`, `while preserving` (DEF-12 flags these and repeated thanks).

## Cover letters

- One page: what was found (with the key number), why it matters to this journal's readers, and the required statements (originality, conflicts, preprint, suggested reviewers if asked).
- No hype words (LEX-01, LEX-02) and no priority claims that the paper does not support.

## Participant information and consent forms

- Second person and plain language throughout (`You will be asked to…`); no sudden switch to third-person regulatory wording.
- Concrete descriptions of procedures, time, risks and compensation.
- No unfilled placeholders or administrative fields that do not apply (HYG-05). If the document is coursework, leave out sponsor, contact and approval fields that do not exist, and leave out status disclaimers.

## Slides and pitch decks

- One message per slide, about 25–40 words of text; prefer a chart or table to text where possible.
- Sources in the speaker notes, citing external sources only (not the team's own report or synopsis); no backup or source slides unless asked.
- State each caveat once, on the slide where it matters; repeating the same caveat across slides reads as defensive.
- State risks as plans with milestones (`supply agreement by month 6`).
- Avoid layouts that look generated: large text cards, pill badges, numbered tags such as `01` and `02`, the same line-label-title block on every slide, coloured table fills.
- The same rules for internal material apply (no file names, codes, simulation counts or versions on slides).

## Grant proposals

- Ambitious aims are acceptable when the feasibility evidence is given next to them.
- Aims should not depend on each other in a way that makes the whole project fail if aim 1 fails.
- Avoid anaphora (`We will… We will… We will…`) and generic broader-impact statements; give the specific population, setting and outcome.
