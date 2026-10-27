# Observational studies and database analyses

Cohort, case-control and cross-sectional studies, including analyses of routine records, registries, claims, surveys and public databases (NHANES, UK Biobank, SEER, MIMIC, CPRD, national registers, DHS and others). Report to STROBE, with RECORD for routinely collected data and RECORD-PE for pharmacoepidemiology.

## Content the paper must contain

- The question as a contrast with an estimand: population, exposure and comparator, outcome, time zero and follow-up. For a causal question, write down the target trial the study emulates (eligibility, strategies, assignment, time zero, outcome, follow-up, causal contrast) and map each element to a measured variable.
- Time zero as the single moment when eligibility is met, exposure is assigned and follow-up starts. Eligibility uses only information available at time zero; any use of later information is justified and checked for selection bias.
- The data source: name, custodian, design and coverage, years, version or release (MIMIC-IV v2.2, GBD 2021, a named NHANES cycle), linkage, and the approval or application number.
- The ethics basis for public data, stated plainly: de-identified public data exempt from review, reliance on the original study's approval, a national-law exemption, or the data controller's governance route.
- The cohort flow with counts at every step, in a figure (STROBE flow diagram) or in the first paragraph of the Results.
- Variable definitions with their coding systems (ICD with version transitions, ATC, Read or SNOMED codes, field identifiers, validated algorithms with their positive predictive values), and the code lists shared.
- Look-back, washout, lag and landmark windows, and the matching ratio.
- Confounders chosen from a causal diagram (DAG), with no adjustment for variables affected by the exposure.
- Missing data: the amount for each variable, the assumed mechanism and the method (multiple imputation, a missing category or complete cases), and how much estimates move across methods. Completer results are never the main finding.
- Absolute as well as relative measures: risks or rates in each group and their difference, beside hazard or odds ratios.
- Multiplicity control when many outcomes or features are scanned (Bonferroni or Benjamini–Hochberg); a single prespecified question needs none.
- Sensitivity analyses aimed at the threats that matter: alternative definitions, exposure lags, removal of early events, extra adjustment, competing-risk models, negative-control outcomes, and an E-value or quantitative bias analysis.
- Survey weights for survey data, and the weighted estimates.
- Data and code availability that names the access route (public link, application, credentialed access) and the repository for the code.

## What reviewers flag, and the fix

- Immortal time: align eligibility, exposure assignment and the start of follow-up; use landmark or cloning, censoring and weighting designs for strategies that start later.
- Confounding by indication: an active comparator, a new-user design, propensity scores with balance shown, or self-matched designs.
- Reverse causation and protopathic bias: lag windows, exclusion of prevalent disease, and results by time since exposure.
- Selection and representativeness: weights, a description of who is missing, and a statement of the healthy-volunteer effect where it applies.
- Misclassification: validated algorithms, alternative definitions, and the positive predictive value of the codes.
- Adjusting for mediators or colliders (and reading every coefficient in the adjusted model as an effect, the table 2 fallacy): build the adjustment set from the DAG and report only the exposure effect.
- Positivity: show overlap of propensity scores and the effective sample size after weighting.
- Data dredging in large public databases: a prespecified question, correction for multiple outcomes, and a phenome-wide scan labelled as hypothesis-generating. A single-factor analysis of an open database needs a reason to exist beyond the data being available.
- Overclaiming: association wording, and a limitation that says what the design cannot show.
- Missing data handled by dropping cases: report how much was missing and how the estimate changes with imputation.

## Writing conventions

- Titles: JAMA family `Association of [Exposure] With [Outcome] Among [Population]`; BMJ and Lancet `[Exposure] and risk of [outcome]: [design] in [setting or database]`.
- Results open with the cohort: `Of 412 380 adults in the database, 98 214 met the criteria (figure 1); the median age was 61 years (IQR 52–70) and 54% were women; 3120 events occurred over 412 000 person-years.` Not with a pointer such as `Baseline characteristics are shown in table 1.`
- Wording follows the design: `[Exposure] was associated with a higher risk of [outcome] (HR 1·32, 95% CI 1·15–1·51)`; comparative-effectiveness designs with an active comparator may say `lower risk than [comparator]`. Keep `causal` for the limitations unless the design supports it.
- Name the results that do and do not survive correction: `Five of 214 disease groups remained associated after Bonferroni correction (P<0·00023).`
- Figures: the flow diagram, cumulative incidence curves, dose–response curves (restricted cubic splines with a shaded 95% CI), forest plots by subgroup, maps. Legends name the adjustment set and what the shading shows.
- BMJ papers include patient and public involvement; JAMA papers point to a data sharing statement in the supplement.

## Burden estimates from aggregate data (secondary analyses of the Global Burden of Disease)

- Report to GATHER, carry the published 95% uncertainty intervals into every figure and trend estimate, and attach no P values to modelled estimates as if they were samples.
- Joinpoint and age–period–cohort analyses state their limits (few age groups, modelled inputs). Forecasts use rolling-origin validation and carry uncertainty forward; prefer established methods (Bayesian age–period–cohort models or the published reference forecasts) to machine learning on a few dozen annual points, and do not pick a different forecasting model for each outcome.
- State the increment over named earlier analyses of the same data, give the data release and download date, and show bar charts or tables beside maps.
