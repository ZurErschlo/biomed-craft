# Mendelian randomisation

Two-sample and one-sample Mendelian randomisation, drug-target and cis-MR with protein or expression quantitative trait loci, multivariable and mediation MR, and bidirectional designs. Report to STROBE-MR.

## Content the paper must contain

- The estimand: the effect of lifelong, genetically proxied differences in the exposure. It is not the effect of a short-term intervention, and the conclusion stays within that.
- Each GWAS source: consortium or cohort, release (FinnGen R8, for example), sample size, ancestry, genome build, and the download date. A table serves best.
- The three instrumental-variable assumptions, stated: relevance, independence and exclusion restriction, with what was done to probe each.
- Instrument selection: the significance threshold (P<5×10⁻⁸), the cis window for drug-target MR (for example ±200 kb), clumping (r², window, reference panel), F statistics, removal of palindromic variants or the harmonisation rule, and Steiger filtering where used.
- Sample overlap between exposure and outcome GWAS, and how it was handled.
- The primary estimator (inverse-variance weighted, or the Wald ratio for a single variant) and a sensitivity battery chosen for the pleiotropy model: MR-Egger (when instrument strength allows), weighted median and mode, MR-PRESSO or an outlier method, and multivariable MR for related traits.
- Heterogeneity (Cochran's Q) and pleiotropy (the Egger intercept), with what was concluded.
- Colocalisation for cis-MR and protein or expression targets, reverse MR with independent instruments, and replication in an independent outcome GWAS.
- Multiplicity: the number of tests and the corrected threshold (`P<0·05/90`), stated once in the Methods.
- Ethics for summary data (public data, approvals held by the contributing studies) and the UK Biobank application number when individual data were used.
- Code in a public repository.

## What reviewers flag, and the fix

- Causal language beyond the evidence: say `evidence of a causal effect` only when the sensitivity analyses, colocalisation and replication agree, and never `proved` or `verified`.
- Weak instruments: report F statistics and drop or flag weak ones.
- Horizontal pleiotropy: cis instruments, the sensitivity battery, colocalisation, and a discussion of known pleiotropic pathways.
- Reverse causation: Steiger filtering and reverse MR.
- Winner's curse and overlap: weights from independent data, or methods that allow overlap.
- Population stratification and limited ancestry: state the ancestry of every sample and the limits it sets.
- Collider bias in analyses of disease progression: name it and use designs that address it.
- Too little detail in the main text: instrument criteria, the tests of assumptions and the correction belong in the Methods, with the full variant lists in the supplement.
- Treatment recommendations from MR alone: a drug-target finding nominates a target; it does not show that a drug works.

## Writing conventions

- Titles put the design in the title or subtitle: `…: a two-sample Mendelian randomisation study`, `… identified with proteomics and drug-target Mendelian randomisation`.
- Results: `Genetically predicted [exposure] was associated with [outcome] (OR per SD 1·21, 95% CI 1·10–1·33).` For screens: `Of 90 proteins, six were associated with heart failure at P<0·05/90 (figure 2).` Results that fail correction are `nominally associated` or `suggestive`, in the supplement.
- Figures: a schematic of the design and the three assumptions, forest plots per SD with the estimator named, and exposure-by-outcome heatmaps. Scatter, funnel and leave-one-out plots go to the supplement.
