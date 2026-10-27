# Laboratory and mechanistic studies

Cell, animal, structural, molecular and device work. Report animal studies to ARRIVE 2.0 and life-science work to the MDAR framework (required by the Science journals); qPCR to MIQE 2.0; sex and gender to SAGER; check cell lines against the ICLAC register and identify reagents with RRIDs.

## Content the paper must contain

1. The hypothesis and the experimental unit (animal, litter, culture, patient-derived line).
2. The exact n per group as numbers, and whether n counts biological replicates, technical replicates or independent experiments.
3. The justification of the sample size.
4. Randomised allocation and order, and masking of allocation, conduct, outcome assessment and analysis.
5. Inclusion and exclusion criteria set in advance, and every exclusion and loss with its reason.
6. Animals: species, strain, sex, age, weight and source; housing, husbandry and welfare; humane end points; ethics approval.
7. Cells: source and catalogue number, authentication method and date, mycoplasma testing, passage number, and the check against the ICLAC list.
8. Reagents and tools: antibodies (clone, dilution, validation), constructs and software, with RRIDs or catalogue numbers.
9. Protocols in enough detail to repeat (doses, timing, routes, instrument settings), deposited step by step where possible.
10. Statistics: the test and whether it is one-sided or two-sided, checks of assumptions, corrections for multiple comparisons, mixed models for nested data, exact P values, and effect sizes with CIs.
11. Individual data points in the figures, with the centre and the error bars defined (SD, SEM or CI).
12. Positive and negative controls, and key claims tested by independent methods (two siRNAs and a rescue; genetic and pharmacological approaches).
13. Image acquisition and processing, representative images chosen by a stated rule and quantified across all samples, and uncropped blots and raw images supplied.
14. For qPCR: RNA quality, reverse transcription, primer sequences and efficiency, validated reference genes, and how Cq values were converted.
15. Both sexes, or the reason for one, and the sex of animals and cells reported.
16. The number of independent repeats, and data, code and materials made available.

## What reviewers flag, and the fix

- Pseudo-replication (cells, wells or fields counted as n): analyse at the level of the experimental unit, or use mixed models.
- n of three with SEM bars and t-tests on data that are not independent.
- Bar charts that hide the distribution: dot plots, with lines joining paired values.
- No randomisation or masking, and exclusions not reported.
- One cell line or one model only.
- Off-target effects not addressed.
- Correlation presented as mechanism (`required for`, `drives`): test necessity and sufficiency and add rescue experiments.
- Selectively chosen or manipulated images.
- Unvalidated antibodies, or one unvalidated reference gene.
- Many tests without correction.
- Findings in mice, or in one sex, generalised to people.
- No dose-response, or only supraphysiological doses.
- n in a legend that differs from n in the Methods.

## Writing conventions

- Result sentences state the observation; the inference sits at the end of the paragraph (`These data suggest that X acts through Y.`). `We propose` and `we speculate` belong in the last paragraph of the Discussion.
- In Cell, Results subheadings and legend titles state findings; in Science, legend titles are mostly noun phrases ([journals.md](../journals.md)).
- Legends give, for each panel, what is shown, n and what it counts, the test, and what the bars show. Cell adds `See also Figure S1`; Nature journals require the Reporting Summary, answered item by item; Cell requires STAR Methods with the Key resources table.
- Main figures: a schematic of the design and timeline, dot plots of individual values, representative images with scale bars and their quantification, dose-response and time-course curves, survival curves with numbers at risk. A supplementary table gives the test, n and exact P for every panel.
