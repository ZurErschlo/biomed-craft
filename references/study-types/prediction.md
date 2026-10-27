# Clinical prediction models

Development, validation and updating of diagnostic and prognostic prediction models, including machine learning. Report to TRIPOD+AI (2024) and judge risk of bias with PROBAST, or PROBAST+AI for machine-learning models. Put the checklist in the supplement.

## Settle before any data are touched

- The intended use: who uses the prediction, for whom, at what moment, and what decision it informs.
- The type of study: development, internal validation, external validation or updating. A random split of one dataset is internal validation. Only temporally or geographically separate data are external.
- The outcome: a validated measure with a reference, and its timing. A screening cut-off is not a diagnosis; a model of a positive screen predicts the risk of screening positive, and the title says so.
- Predictors: only information available at the moment of prediction, measured before the outcome. A predictor that is part of the outcome's definition, or of an index the outcome is built from, is excluded.
- Cross-sectional data support a diagnostic or concurrent model, never a risk prediction model.
- Sample size from the Riley criteria (the `pmsampsize` package), with the number of outcome events and candidate predictor parameters stated. When events are too few, simplify the model or stop.
- Comparators that measure the same outcome (a steatosis index for steatosis, not a fibrosis score).
- Continuous outcomes stay continuous unless a cut-off has clinical support.

## Building the model

- Split before any processing. Every step (imputation, scaling, univariable screening, variable selection, tuning, resampling, nomogram fitting) is fitted on the training data only and then applied unchanged.
- Prefer prespecified predictors or penalised regression to univariable p-value screening followed by stepwise selection.
- Multiple imputation for missing predictors, fitted within the training data; report the amount of missing data for each variable and the handling. Complete-case analysis is a weakness to state.
- Machine learning: tune with cross-validation inside the training data; apply SMOTE or other resampling only inside training folds, and recalibrate afterwards, because resampling distorts predicted probabilities.
- Choose the model, the threshold, the feature set and any ensemble members from cross-validated training results only, and lock the choice before the test set is opened. Ranking candidates on test performance is selection on the test set.
- Fix the classification threshold during development and carry it unchanged to the test and external sets.
- Use models whose output is a probability. A score that is not a probability is recalibrated before calibration plots or decision curves.

## Performance and validation

- Discrimination: the C statistic with its 95% CI.
- Calibration: calibration slope, calibration-in-the-large or intercept, observed-to-expected ratio, and a smoothed calibration plot.
- Clinical utility: net benefit in a decision curve over a stated range of thresholds.
- Internal validation by bootstrap or cross-validation, with optimism-corrected performance.
- External validation with the published model unchanged: no proxy predictors, no outcome set to zero when missing, and the missing-data handling reported.
- Classification metrics at the fixed threshold with 95% CIs; likelihood ratios computed from sensitivity and specificity; totals that agree across rows and categories.
- Performance in subgroups (sex, age, ethnicity, site) to show where the model may fail.
- Incremental value of a new marker: a likelihood-ratio test between nested models fitted to the same data, and the change in C statistic with its CI as a size. The DeLong test is not used for nested models on the same data; continuous net reclassification is avoided.
- SHAP and other importance measures describe the model; they carry no inferential intervals and do not show cause.

## What reviewers flag, and the fix

- Predictors measured at the same time as, or after, the outcome: give the time of each measurement, and call them predictive factors, never risk factors.
- An outcome measured with a screening tool: reframe as the risk of screening positive and add the limitation.
- No independent test set, or leakage: state when the split happened and which steps were fitted on which data.
- A feature-selection rule with no reason: justify the rule, or replace it with a penalised model.
- Too little detail to reproduce: give imputation, tuning, cross-validation and software with versions, and share the code.
- Performance figures that disagree with the tables: recompute both from the same output.
- A single-centre sample: state the limits of representativeness and plan external validation in other centres and populations.
- Metrics without clinical meaning: show what a given sensitivity and specificity mean for the intended use.
- Inclusion and exclusion criteria mixed together: list them separately, and give a reference for every scale.
- A method in the text that differs from the code (test names, thresholds, the number of selection methods): make the text describe what the code did.

## Writing it up

- Title: `Development and validation of a model to predict [outcome] in [population]: a [design] study`, or `External validation of [model] in [population]`.
- Abstract: the population and setting, the outcome and horizon, the candidate predictors, the modelling method, the type of validation, and the C statistic, calibration and net benefit with their intervals.
- Present the final model so that others can use it: the full equation with the intercept, a nomogram, or shared code.
- Main figures: the calibration plot and the decision curve; a ROC curve adds little next to the C statistic. Main tables: participant characteristics by development and validation set, and the predictors with their coefficients or odds ratios.
- Baseline tables give medians with quartiles or means with SDs consistently, and no significance tests between the development and validation sets.
