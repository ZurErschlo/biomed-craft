# Research plans

A research plan (`research_plan.md`) is the working specification of a study. Someone outside the project could repeat the study from it alone. Write it in English and in the future tense, and let it state the current method only: it reads like the skeleton of the Methods and Results of the paper.

## Contents, in order

1. Title, registration number if there is one, and one sentence of aim.
2. Objectives, primary then secondary.
3. Data, early: each source with its version or release, access date and route, and the inclusion and exclusion criteria. Point to the data dictionary.
4. Definitions concrete enough to code: population, exposure or intervention, comparator, outcome, time zero, follow-up and covariates, each with units and the algorithm that derives it.
5. Analysis, step by step: models, formulas written as rendered equations, parameters with values and sources, and software. Label each analysis primary, secondary or sensitivity.
6. Decision rules fixed in advance, written as definite conditions: `If the model does not converge, we will remove the random slope.`
7. For a model: structure, assumptions with their sources, a parameter table (value, distribution, source), calibration targets and method, validation and uncertainty. An economic evaluation adds perspective, time horizon, discount rates and threshold (CHEERS 2022).
8. Limitations known in advance.
9. Outputs, last: every figure and table, with what each one shows.

Explain every variable and abbreviation where it first appears. Write each method choice as a choice with its reason and precedent: `We will use a negative binomial model because the counts are overdispersed, as in [citation].` Take values from sources, never from memory; when a value has no source yet, find one before writing it down.

## Before freezing the plan

- Name the primary outcome and the quantity to be estimated. A trial states its estimand (ICH E9(R1)): population, treatment conditions, variable, the handling of intercurrent events and the summary measure. Other designs name the quantity in plain words; reporting guidelines ask about the estimand framework only when it was used.
- Intercurrent events, such as stopping or switching treatment, are handled in the estimand. Missing data are a separate matter: withdrawal from the study, administrative censoring and data that the chosen strategy needed but that were not collected are handled in the analysis.
- Each decision rule is a definite condition (item 6), never `if appropriate` or `where necessary`. A diagnostic test such as a test of normality changes the method only through a rule written in advance with its threshold and its alternative model, as in the example below.
- Multiplicity: define the families of comparisons and how the type I error is controlled. When there is no adjustment, say so and read the results as exploratory.
- Each hypothesis has one outcome and one primary analysis. List the sensitivity and subgroup analyses in advance and label each one secondary or sensitivity, so that none is added or dropped after the results are seen.
- Name the software defaults that affect the results, with their values and the software version (the default importance measure in feature selection, for example).
- A trial's statistical analysis plan is final before unblinding, and the paper marks each departure made after unblinding.

## What stays out

- Unsettled items and to-dos (PLAN-01). Decide, or move the item to the to-do list in `execution_log.md`.
- Status labels, ticks and progress marks (PLAN-02).
- Dates, version numbers, change notes and notes on what replaced what (PLAN-03). A trial's statistical analysis plan is the exception: it keeps each amendment with its version, reason and timing (Gamble and colleagues 2017, items 4a–4c). Other plans record their changes in the log.
- Pointers to the log, meeting notes or chats (PLAN-04).
- Internal codes that need a key, such as `N12` or `R1–R22` (PLAN-05).
- Run details: threads, environment variables, profiling, runtime (PLAN-06).
- Undecided options: `we may also explore` (PLAN-07).
- Records of how an assistant or a session worked (META-12).
- Comparisons with an anchor paper, exploratory appendices and discussion of the registered protocol.

Keep one plan per project. When the plan changes, edit it in place and record the change in the log ([execution-log.md](execution-log.md)).

## Changes and the registration

- When the method departs from the registration, amend the registration (PROSPERO keeps every version with its date) and record the change in the log.
- In the paper, Methods describe the methods as they were done and give the registration number. A decision made after the data were seen is never called prespecified.
- Reporting checklists ask about amendments (PRISMA 2020 item 24c). Answer there, or in one line of the supplement.

## Example

```text
Before
Model: Poisson for now (TBD, maybe NB if overdispersed; see log 12/05). Status: in progress (N7).

After
We will fit a Poisson regression of monthly notifications on calendar year, with the population as an offset.
If the ratio of residual deviance to degrees of freedom exceeds 1.5, we will fit a negative binomial model.
```
