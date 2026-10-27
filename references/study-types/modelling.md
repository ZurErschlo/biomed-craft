# Disease and epidemiological modelling

Transmission models (compartmental, individual-based, metapopulation), microsimulation and state-transition models of disease, burden estimation and projection, forecasting and nowcasting, and models that estimate what an intervention averted. Report burden estimates to GATHER and forecasts to EPIFORGE 2020; add CHEERS 2022 when costs are modelled. Put the checklist in the appendix.

## Content the paper must contain

1. The decision question, the comparator, and why a model answers it when a trial or an observational study cannot.
2. The model type and structure, with the reason for each: which strata are included and why, which processes are left out, and how each omission is likely to bias the result.
3. The structure in words and in a schematic (usually figure 1). Equations go to the appendix with page pointers. A model published before is cited, with what changed.
4. Each data source with its period, coverage and quality, and how the data were processed (outliers, under-reporting, reporting delay, imputation). Inputs, calibration targets and validation data are kept apart.
5. A parameter table: value, range or prior, and source. Mark values that were assumed or elicited, and which parameters were fitted.
6. Calibration: targets, method (for example Markov chain Monte Carlo, approximate Bayesian computation, maximum likelihood), the likelihood or distance measure, the acceptance or convergence rule, the number of parameter sets kept, and a figure of the fit against the data.
7. Validation against data not used for fitting, and how well the model did.
8. The status quo, the counterfactuals and the scenarios, defined precisely (coverage, timing, scale-up), with the time horizon in years and as a calendar span, and the outcome metrics with their denominators.
9. Uncertainty from parameters, from stochastic runs and, where possible, from model structure. Define how intervals are computed (`1000 draws; 2·5th and 97·5th percentiles`) and use one interval label throughout.
10. Sensitivity analyses of the assumptions that drive the result, including alternative structures, and whether the conclusions change.
11. Comparison with other models and published estimates, with the reasons for differences.
12. Software and versions; code and processed inputs deposited with a DOI; the access route for restricted data.
13. Limitations that name the structural simplifications, where the data are thin, the limits of generalisability and the likely direction of bias. Counterfactual results are described as depending on the model's assumptions.

## What reviewers flag, and the fix

- A model nobody can inspect: a structure paragraph, a schematic, appendix page pointers, and a citation to the earlier validated version.
- Mechanisms included or omitted without reason: justify each, and show that the conclusion holds across structures or across several models.
- Calibration that is opaque or overfitted: name targets and method, show the fit with the data points, and check a feature the model was not fitted to.
- No validation: hold out recent data, cross-validate, freeze projections before trial results are known, or compare with an independent trial, registry or published estimate.
- Uncertainty understated: propagate parameter and stochastic uncertainty, report ranges across models, and never give scenario results as point estimates alone.
- Scenarios chosen arbitrarily: anchor them to real targets or to the best-performing programmes, always include the status quo, and tabulate coverage and timing.
- Counterfactuals over-read: call them illustrative, list their assumptions (no behaviour change, for example), and hedge in the interpretation.
- Sparse data in some settings: show data coverage and quality, validate by leaving one setting out, and flag the settings with little data.
- A result that rests on one assumption: test that assumption explicitly, report the test in the Results, and say which way conservative choices push the estimate.
- Disagreement with other estimates left unexplained: compare and explain the gap by data or structure.
- Results that cannot be reproduced: share versioned code and inputs, and posterior draws where possible.
- Spurious precision: round modelled counts to three significant figures, give rates per capita, and state the rounding rule in table notes.
- Stale real-time estimates: give the data cut-off date and say which new data would change the result.

## Title and abstract

- Lancet family: topic, scope and period, then the design, with no result: `…, 1990–2021, with forecasts to 2050: a systematic analysis for the Global Burden of Disease Study 2021`, `…: a mathematical modelling study`, `…: a combined analysis of eleven mathematical models`.
- BMJ: `…: modelling study`, `…: microsimulation modelling study`, without an article. JAMA: Title Case and no design label in JAMA itself. Nature journals and Science: a short phrase (`Estimated deaths averted by …`). American spelling `modeling` outside the Lancet family and the BMJ.
- Lancet Methods name the model type, setting, data, calibration, scenarios and horizon. Findings open with the headline estimate: `We estimated that [X] averted [N] million (95% uncertainty interval [UI] a–b) deaths in [place, period].` Then the scenario contrast: `Under [scenario], [outcome] would fall by x% (a–b) compared with the status quo.` Interpretation gives one hedged sentence of meaning and one of action.
- BMJ intervals read `95% uncertainty interval a to b`; conclusions are conditional on the assumptions.
- JAMA: Key Points; the first interval `(95% uncertainty interval [UI], a to b)`, later `(95% UI, a-b)`; comparative models give the mean across models and the range.

## Methods

- Lancet transmission or intervention models: Model structure, Data, Calibration, Intervention scenarios, Sensitivity analysis, Role of the funding source. Burden estimation: an overview with a GATHER sentence, input data, estimation tools, forecasting, uncertainty. JAMA: Model Description; Data, Model Parameterization, and Validation; Model Analyses and Scenarios; Model Outcomes; Sensitivity Analysis and Uncertainty. BMJ adds patient and public involvement.
- The main text gives one or two paragraphs on the model: deterministic or stochastic, compartmental or individual-based, the strata, the states named in words, the transitions in words, and what was fitted. The parameter table sits in the main text in the BMJ and JAMA, in the appendix in the Lancet and Nature journals.
- Denominators that fit the outcome: per 100 000 for burden; per 10 000 people or per 10 000 vaccinations for deaths averted; per 1000 screened for screening; number needed to vaccinate for comparing strategies.

## Results

- Fit first: `The model reproduced [targets] (figure 2).`
- Past estimates in the past tense: `We estimated that N (a–b) [outcome] occurred in [year].`
- Projections: `[Outcome] is projected to rise from N (a–b) in [year] to N (a–b) in [year] at the status quo.`
- Counterfactuals: `Without [X], an estimated N (a–b) additional deaths would have occurred.` or `[X] averted N (a–b) deaths, x per 10 000 population.`
- Ensembles: `mean x (range across models y–z)`.
- Sensitivity: `When [X] was varied, [outcome] changed to N; the ranking of strategies did not change (appendix p n).`
- Results are attributed (`we estimated`, `the model projects`) and stated without hedges; `would` carries the counterfactual meaning. Hedges belong in the interpretation and Discussion, on explanations, extrapolation to settings without data, and policy implications.
- Name each scenario the same way in the text, the legends and the tables.

## Figures and tables

- Usual order: schematic or input coverage; fit to data; projections by scenario with uncertainty ribbons; averted outcomes or scenario comparisons; maps; decomposition of forecasts. Sensitivity results go to the appendix.
- Lancet legends: a title phrase, then what lines, points and shading show, panel letters, and abbreviations (`UI=uncertainty interval.`). Lancet table notes: `Data are n (95% UI).`, then the rounding rule (counts to three significant figures, rates to one decimal place), then symbols. Real-time analyses date their estimates in the legend.

## Discussion

- Restate the main estimate, then compare it with other estimates (WHO, UNAIDS, IHME, IDF and others) and explain the gap.
- Limitations: `Our study has several limitations. First, …`. Burden studies point to the general limitations published elsewhere and add their own.
- Close with the decision the results inform. Lancet papers carry a Research in context panel that describes the literature search.

## Numbers

- Lancet: `12·3 million (95% UI 10·1–14·6)`, thin-space thousands from five digits, `per 100 000`, `to` when a bound is negative. BMJ: point decimals and `a to b`. JAMA: hyphenated ranges. Nature: comma thousands and en-dash ranges.
- Modelling papers run longer sentences and more `we` than other research articles; that is the genre, and it stays.

## Supplement and availability

The full model description and equations, parameter tables with sources and priors, calibration targets, diagnostics and fits by setting, validation, further scenarios and sensitivity analyses, results by setting, the GATHER or CHEERS checklist, and data sources. State availability in this order of preference: data and code in a repository with a DOI; sources listed in the appendix and in a public data catalogue; restricted data with the custodian named; on request.
