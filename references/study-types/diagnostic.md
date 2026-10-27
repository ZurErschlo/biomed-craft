# Diagnostic accuracy studies

Studies of the accuracy of a test, a reader or an AI tool against a reference standard. Report to STARD 2015 (STARD for Abstracts for the abstract) and STARD-AI for AI tools, CLAIM for AI in medical imaging, and TRIPOD+AI when the test is a multivariable model. Reviewers judge bias and applicability with QUADAS-3, or QUADAS-C for comparative accuracy.

## Content the paper must contain

1. The intended use and role of the test (triage, add-on or replacement), the target condition and the clinical setting, and the minimum acceptable accuracy set in advance.
2. A consecutive or random series from the intended-use population (a single-gate design), with eligibility, setting and dates. A case-control (two-gate) design is explained.
3. The index test described so that it can be repeated: technique, operator or reader expertise, and positivity thresholds, said to be prespecified or derived from the data.
4. The reference standard, why it is the best available, whether everyone received it, the interval between the tests and any treatment in between.
5. Who was masked to what: readers of each test and the clinical information available to them.
6. The sample size, justified by the precision needed for sensitivity and specificity.
7. Indeterminate, inconclusive and missing results, and how they were handled.
8. The flow diagram, and the 2×2 table of index test against reference standard, overall and by subgroup; the spread of severity and of alternative diagnoses.
9. Sensitivity, specificity and likelihood ratios with 95% CIs; predictive values with the prevalence they assume; the AUC only beside metrics at clinically relevant thresholds.
10. Variation across subgroups, readers and sites, and any harm from testing.
11. Comparative accuracy from paired or randomised comparisons.
12. Where the test sits in the clinical pathway; registration and protocol.
13. For AI tools: splits at the patient level, an external test set, how reference labels were produced, an analysis of failures, and how clinicians used the tool.

## What reviewers flag, and the fix

- Spectrum bias from severe cases against healthy controls: a single-gate consecutive design.
- Partial or differential verification: verify everyone, or correct for it.
- Incorporation bias: keep the index test out of the reference standard.
- Thresholds chosen on the same data: prespecify them, or validate them in new data.
- Indeterminate results excluded: report and analyse them.
- The AUC as the only metric: give sensitivity, specificity and likelihood ratios at the thresholds that matter.
- Clinical usefulness claimed without a defined pathway: describe the decision the test changes.
- Predictive values without prevalence.
- Generalisation from retrospective data from one site.

## Writing conventions

- Results open with the flow: `Of 2140 patients assessed, 1876 were enrolled and 1802 had both tests (figure 1); 412 (22·9%) had the target condition.`
- Main figures and tables: the STARD flow diagram; 2×2 tables; an accuracy table with CIs at prespecified thresholds; the ROC curve with the operating points marked; the distribution of index-test results by reference status. AI studies add a diagram of data partitioning and examples of failures.
- JAMA asks for prevalence whenever predictive values are given; the Lancet adds Research in context; the BMJ adds patient and public involvement.
