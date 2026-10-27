# Bioinformatics, genomics and other computational studies

Analyses of public or new omics data (TCGA, GEO, GTEx, CPTAC, single-cell atlases), genome-wide association and polygenic scores, phylogenetics and genomic epidemiology, and machine learning on molecular or imaging data. No single reporting guideline covers them; use REMARK or TRIPOD+AI for prognostic signatures and models, STREGA for genetic association, and the MIAME or MINSEQE metadata standards for deposited data.

## Content the paper must contain

- Each dataset with its repository and accession (GSE numbers, dbGaP study identifiers, TCGA through a named portal), the release (GTEx v8), the download date, and the sample size after exclusions.
- Sample and cell quality control: exclusion rules, doublet and low-quality cell removal, normalisation, and whether raw data were reprocessed uniformly.
- Batch effects: how they were checked and corrected (ComBat, sva, integration methods with their metrics), and each platform processed separately before combination.
- The unit of analysis: the donor or patient, not the cell or the read. Technical and biological replicates are kept apart.
- Multiple testing with Benjamini–Hochberg FDR or Bonferroni over the effective number of tests, with the thresholds stated in advance.
- Splits at the level of the patient (training, validation and test), and validation in independent cohorts. Freeze modules, signatures and thresholds before validation.
- Experimental validation for a mechanistic claim (knockdown, immunohistochemistry, qPCR, spatial methods), or the claim stays at association.
- Software and versions, parameters that are not defaults, and code in a public repository with a DOI.
- New data deposited with an accession number.

## What reviewers flag, and the fix

- Batch effects mistaken for biology: show the correction and a check that the signal survives it.
- Overfitting: patient-level splits, external cohorts, and no tuning on the validation data.
- A signature with no validation: independent datasets, prespecified thresholds, and comparison with established markers.
- Annotation errors in public data: audit sample annotations before analysis.
- Forking paths: fix the analysis choices before looking at the validation data.
- Correlation read as mechanism: keep `drives` and `promotes` for perturbation experiments; otherwise `is associated with` or `predicts`.
- Therapeutic claims from computational results alone: state them as hypotheses for experimental testing.

## Writing conventions

- `we` is used more than in clinical papers, and Results subheadings often state the finding.
- Results open with the aim or the data: `To identify [X], we analysed [dataset] ([n] samples from [k] cancer types; Fig. 1a).`
- Software appears with versions in the Methods (`STAR v2.7.10a`, `Seurat v5.0`); parameter and function names may appear in the Methods of a computational paper.
- Figures: a workflow schematic, then results (enrichment, networks, heatmaps, UMAP, Kaplan–Meier, ROC). Legends name the test, the correction and n for each panel.
- Data and code availability: accessions for every dataset, the repository and DOI for the code, and for Cell Press journals the standard statement that the paper analyses existing public data and reports no original code when that is true.
