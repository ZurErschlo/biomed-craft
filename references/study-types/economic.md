# Health economic evaluations

Cost-effectiveness, cost-utility, cost-benefit and budget impact analyses, built on a model or alongside a trial. Report to CHEERS 2022 and put the completed checklist in the supplement. For a trial-based analysis, write a health economic analysis plan (HEAP) before the data are unblinded and cite it.

## Content the paper must contain

- The decision: who decides, for which population and jurisdiction, and what the choice is (adopt, scale up, set a price).
- Every realistic comparator, current practice included. Justify a do-nothing arm and any option left out.
- The perspective and the cost categories it implies. A societal perspective includes productivity losses and out-of-pocket costs.
- A time horizon justified by the natural history of the condition and the duration of effect. If the analysis stops at trial follow-up, say why that is long enough.
- Discount rates for costs and outcomes, the guideline they come from, and a test of other rates.
- The primary outcome (cost per QALY gained, per DALY averted, net monetary benefit or benefit–cost ratio), with the utility instrument and value set or the source of disability weights.
- Resource use, unit-cost sources, currency, price year, inflation index and conversion method. Include start-up, training and supervision costs.
- For a model: its type and why it fits the question (a transmission-dynamic model when herd effects matter), the structure as a diagram, key assumptions, cycle length and software.
- Every input in a table: value, range or distribution, and source. Gamma distributions for costs, beta for probabilities and utilities, lognormal for relative risks are the usual choices; name the ones used.
- Validation: face validity, verification of the code, calibration targets and fit, and external validation.
- For a model built on a trial: show that it reproduces the trial over the trial period, state how long the effect is assumed to last after the trial, and test waning as a scenario. Explain any gap between the clinical result and the economic result.
- For a trial-based analysis: multiple imputation for missing costs and outcomes, seemingly unrelated regression or bootstrapping for the correlation between costs and QALYs, multilevel models for clustering, adjustment for baseline utility, and the intention-to-treat population.
- Uncertainty in full: probabilistic analysis with named distributions and the number of draws, a cost-effectiveness acceptability curve or the probability of being cost-effective at each stated threshold, one-way analyses of the main drivers, structural scenarios, price thresholds for a new product, and value-of-information analysis when the decision is still uncertain.
- Results by prespecified subgroup and setting, and distributional (equity) results where they bear on the decision.
- Complete results: mean costs and outcomes per arm, incremental values with uncertainty, sequential ICERs with dominated options removed, and net monetary benefit.
- A budget impact analysis, if any, reported separately: undiscounted, from the budget holder's perspective, over one to five years.
- A threshold for every claim that something is cost-effective or cost saving, with its justification and the probability attached.

## What reviewers flag, and the fix

- Comparators that are too few or unrealistic: model all realistic strategies and run a full incremental analysis with dominance checked first.
- Costs that do not match the stated perspective: build costs from the perspective (NHS and Personal Social Services for NICE; measured out-of-pocket costs for a societal view).
- A horizon too short for the benefits: extrapolate with explicit post-trial assumptions and show alternatives.
- A model nobody can inspect: publish the parameter table with sources and distributions, and share the code.
- No validation: report calibration targets, fit and external validation.
- A threshold chosen for convenience: justify it, show results across a range, add opportunity-cost thresholds in low-income and middle-income settings, and give price targets.
- Thin uncertainty analysis: combine probabilistic, one-way and structural analyses. When the effect straddles zero, report net monetary benefit; an interval around the ICER cannot be read.
- Overclaiming: give point estimates with intervals and probabilities. A saving whose interval crosses zero is a possible saving.
- Weak trial-based methods: a prespecified plan, multiple imputation, bootstrapping or seemingly unrelated regression, and multilevel models.
- Utilities of unclear origin: name the instrument, value set and any mapping algorithm, and test another value set.
- Programme costs left out: micro-cost delivery by activity.
- Generalisability asserted without support: name comparable settings and show results by country or setting.
- Budget impact mixed with cost-effectiveness: keep the two analyses apart.
- A conclusion that serves no decision: end with the price, budget or scale-up decision the analysis supports.

## Title and abstract

- Lancet family: `Cost-effectiveness of [X] versus [Y] for [Z] in [country]: a modelling study`. Other labels in use: `an economic evaluation`, `a cost-effectiveness analysis of the [ACRONYM] trial`, `an extended cost-effectiveness analysis`, `a cost–benefit analysis` (en dash).
- BMJ: `… : pragmatic randomised controlled trial and economic evaluation`, or `… : cost effectiveness analysis based on [model]`. BMJ writes `cost effectiveness` without a hyphen and drops the article before the design.
- JAMA: Title Case, `Cost-Effectiveness of X for Y in Z`; trials add a subtitle such as `A Randomized Clinical Trial`. The design line of the abstract reads `This economic evaluation, from a [health care sector] perspective, used a [microsimulation] model with a [lifetime] horizon…`.
- NEJM: `Cost-Effectiveness of X versus Y`, with no design label.
- Abstract results give the incremental outcome with its interval, the ICER with its unit, and the threshold. Lancet abstracts usually add the probability of being cost-effective; JAMA abstracts add the time horizon.

Template for a Lancet Findings section: `[X] would avert [N] DALYs (95% UI a–b) at an incremental cost of US$[C], an ICER of $[Y] per DALY averted; the probability of being cost-effective at [threshold] was [P]%.`

## Methods

- Lancet models run Study design, Model structure, Scenarios, Data or inputs, Costs, Outcomes, Cost-effectiveness analysis, Sensitivity analysis, Model validation. Trial-based papers add a health economic subsection to the trial methods.
- Perspective: `We took a [health-system] perspective, including [cost categories]; a societal perspective was a scenario.`
- Horizon: `Costs and outcomes were estimated over [lifetime or N years] to capture [reason].`
- Discounting: 3% (United States, WHO-CHOICE, many low-income and middle-income analyses), 3·5% (United Kingdom), 5% (Australia and some others), with 1·5% as a United Kingdom scenario. Budget impact analyses are not discounted.
- Currency: `Costs are in [year] [currency], inflated with [index] and converted with [purchasing power parity or exchange rate].`
- Threshold: NICE £20 000–30 000 per QALY; US$50 000, $100 000 or $150 000 per QALY in the United States, sometimes as value bands; opportunity-cost thresholds or GDP-based ranges elsewhere. New products often get a price-threshold analysis instead.
- Name the model and its version when it has one (`Policy1-Cervix`, `CVD Policy Model`).
- The parameter table sits in the main text in JAMA and in some Lancet papers; otherwise in the appendix, with columns for parameter, base-case value, range or distribution, and source.

## Results

- Order: health outcomes, disaggregated costs, incremental results and ICER or net monetary benefit, probabilistic results, one-way and scenario analyses, subgroups or settings, budget impact or price thresholds, value of information.
- Units: `per QALY gained`, `per DALY averted`.
- ICER: `Compared with [Y], [X] cost £[C] more (95% CI …) and gained [Q] QALYs (95% CI …), giving £[R] per QALY gained.`
- Dominance: name the quadrant (`cost saving`, `dominant`, `dominated`, `extendedly dominated`) and do not compute an ICER for a dominated strategy.
- Probabilistic results: `At £[threshold] per QALY gained, the probability that [X] is cost-effective was [P]% ([N] simulations).`
- One-way results: `ICERs ranged from [a] to [b]; results were most sensitive to [parameters].`
- Price thresholds: `cost-effective at an annual price of $[P] or less; cost saving at $[Q] or less.`

## Figures and tables

- Main figures: the cost-effectiveness acceptability curve, the cost-effectiveness plane, the model diagram and a tornado plot; trial-based papers also show the CONSORT flow.
- Main tables: costs by category and the cost-effectiveness results table.
- Lancet and BMJ notes define abbreviations as `ICER=incremental cost-effectiveness ratio.` and state the currency and interval type: `Currency is AUS$.`, `Values in parentheses are 95% uncertainty intervals.` JAMA notes open with `Abbreviations: ICER, incremental cost-effectiveness ratio; …`.

## Discussion

- Open with the result at the level of the decision, then compare with earlier evaluations.
- Give each limitation with the direction in which it would move the result.
- Say which settings the result applies to and what it implies for price, budget or scale-up.
- Lancet papers carry a Research in context panel that describes the literature search (databases, dates, terms, language limits). BMJ papers carry the two boxes, What is already known on this topic and What this study adds. JAMA ends the Discussion with Limitations and adds a Conclusions section.

## Numbers and wording

- Round ICERs to whole currency units or about three significant figures (£45 200); keep thresholds round; give QALY differences to two to four decimals.
- First use `US$`, then `$`; international dollars as `I$`.
- Economic evaluations run longer sentences than other research articles, because a result carries an estimate, its interval and a threshold. Split a sentence only when it holds two results.
- `utilisation` is a costing term and `robust to` describes a sensitivity result; both stay.

## Supplement

The CHEERS checklist, full parameter tables with distributions and sources, model structure and equations, calibration targets and fit, validation, further sensitivity analyses and cost-effectiveness planes, results by country or subgroup, unit costs, and the HEAP or statistical analysis plan. Share model code in a public repository and cite it.
