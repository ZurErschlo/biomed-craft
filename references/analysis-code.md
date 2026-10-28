# Analysis code and comments

Analysis scripts are written for the researcher to run and read. Each script opens in RStudio and runs section by section, so the results can be checked as they appear.

## Layout

- Few scripts, numbered in the order a person does the analysis: `01_clean.R`, `02_describe.R`, `03_model.R`.
- Each script runs on its own once the scripts before it have run. It reads `data/input` and the files earlier scripts wrote to `data/output`.
- The data-preparation script only cleans: deduplication, imputation and derived variables.
- Figure and table code follows the analysis it shows, in the same script. Each script writes its own figures to `figures/` as PDF and TIFF, the values each figure plots to `data/output/`, and tables to `tables/`, one xlsx file per table. Data files are CSV.
- For a model that takes hours, the drawing section reads the saved results, so a figure can be redrawn without refitting.
- Change a figure or table only through its script; never edit the output by hand.
- No setup, folder-creation, run-all, test or smoke scripts, no JSON manifests, and no shared helper or function file (CODE-06). The exception is a model that takes hours: give it a short trial run first and record that run in `execution_log.md`.
- Watch memory use with large data.

## Reproducibility

- Put an `.Rproj` file at the project root and build every path with `here::here()` (CODE-04).
- Leave out `setwd()` (CODE-01), `rm(list = ls())` (CODE-02), `install.packages()` (CODE-03) and saved workspaces, `save.image()` or `.RData` (CODE-05).
- Load packages at the top with `pacman::p_load()`, one package per line.
- A script that draws random numbers sets one seed at its top (CODE-07).
- Treat input data as read-only; never edit them by hand. Values taken from the literature live in a hand-maintained table with a source for each value, and the code reads them from there.
- Check the assumptions that matter with `stopifnot()` and a message: row counts after a join, unique identifiers, probabilities between 0 and 1.
- Use the current version of R on the machine. Use renv only when a project needs fixed package versions, and say so in the README.

## Comments

- English throughout (HYG-06).
- A header with `# Purpose:`, `# Input:` and `# Output:`, and the heading of the plan section the script carries out.
- Numbered sections in RStudio form, `# 1. Load data ----`, which RStudio lists and folds.
- Comments say why: the assumption behind a step, the source of a constant, a step that is not obvious. They do not restate the code.
- Leave out change history (CODE-08), dates (CODE-09), plan section numbers (CODE-10), to-dos (CODE-11), commented-out code (CODE-12), status marks (PLAN-02), internal codes (PLAN-05) and records of conversations or sessions (META-12).
- Names in `snake_case`: nouns for objects, verbs for functions.

## Example

```r
# Purpose: estimate the trend in notifications (plan: Analysis, trend model)
# Input:   data/output/notifications_clean.csv
# Output:  tables/table2_trend.xlsx, figures/figure2_trend.png

pacman::p_load(
  here,
  MASS,
  writexl
)

# 1. Load data ----
notifications <- read.csv(here::here("data", "output", "notifications_clean.csv"))
stopifnot("duplicate notification IDs" = !anyDuplicated(notifications$id))

# 2. Fit the model ----
# Negative binomial because the counts are overdispersed (deviance ratio above 1.5).
fit <- glm.nb(cases ~ year + offset(log(population)), data = notifications)
```
