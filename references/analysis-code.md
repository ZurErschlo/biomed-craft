# Analysis code and comments

Analysis scripts are written for the researcher to run and read. Each script opens in RStudio and runs section by section, so the results can be checked as they appear. The agent still reruns a script itself after every change ([workflow.md](workflow.md)).

## Layout

- Few scripts, numbered in the order a person does the analysis: `01_clean.R`, `02_describe.R`, `03_model.R`.
- Each script runs on its own once the scripts before it have run. It reads `data/input` and the files earlier scripts wrote to `data/output`.
- The data-preparation script only cleans: deduplication, imputation and derived variables.
- Figures and tables have their own scripts, numbered after the analysis (`09_figures.R`, `10_tables.R`). The analysis scripts write every value a figure or table shows to `data/output/`: summaries, predictions, confidence bands and, when needed, the fitted model objects as rds files. The plotting and table scripts read only `data/output/`, and the cleaned data for plots of raw points; they never refit a model. A figure is then redrawn in seconds, however long the model took.
- The plotting scripts write figures to `figures/` as PDF and TIFF; the table scripts write tables to `tables/`, one xlsx file per table. Data files are CSV.
- The style sits at the top of each plotting and table script: the font (Times New Roman unless the journal asks for another), the three-line table format and the canvas width. A project that also draws in Python sets the same values at the top of its Python plotting script.
- Change a figure or table only through its script; never edit the output by hand. After a change to an analysis script, rerun the plotting and table scripts that read its output ([workflow.md](workflow.md)).
- No setup, folder-creation, run-all, test or smoke scripts, no JSON manifests, and no shared helper, function or style file (CODE-06). The exception is a model that takes hours: give it a short trial run first and record that run in `execution_log.md`.
- Watch memory use with large data.

## Reproducibility

- Put an `.Rproj` file at the project root and build every path with `here::here()` (CODE-04).
- Leave out `setwd()` (CODE-01), `rm(list = ls())` (CODE-02), `install.packages()` (CODE-03) and saved workspaces, `save.image()` or `.RData` (CODE-05).
- Load packages at the top with `pacman::p_load()`, one package per line.
- A script that draws random numbers sets one seed at its top (CODE-07).
- Treat input data as read-only; never edit them by hand. Values taken from the literature live in a hand-maintained table with a source for each value, and the code reads them from there.
- Check the assumptions that matter with `stopifnot()` and a message: row counts after a join, unique identifiers, probabilities between 0 and 1.
- Use the current version of R on the machine. Use renv only when a project needs fixed package versions, and say so in the README.
- When the software version that produced the results differs from the one the Methods give, rerun under the stated version, or rerun and change the stated version. The version number alone is never edited.
- Numbers in the text are read from the output files, never copied from the console.
- Python notebooks: the first code cell lists the packages and versions used and checks each one, printing the install command for any that is missing; it installs nothing itself. Each section opens with a heading cell, and the cells run in order, one by one.

## Comments

- English by default (CODE-13). A researcher who wants comments in their own language allows CODE-13 in the style file ([personal-style.md](personal-style.md)); comments, section headings, check messages and printed output then use that language, while object, function, column and file names stay in English.
- A header with `# Purpose:`, `# Input:` and `# Output:`, and the heading of the plan section the script carries out.
- Numbered sections in RStudio form, `# 1. Load data ----`, which RStudio lists and folds.
- Comments say why: the assumption behind a step, the source of a constant, a step that is not obvious. They do not restate the code.
- Leave out change history (CODE-08), dates (CODE-09), plan section numbers (CODE-10), to-dos (CODE-11), commented-out code (CODE-12), status marks (PLAN-02), internal codes (PLAN-05) and records of conversations or sessions (META-12).
- Names in `snake_case`: nouns for objects, verbs for functions.

## Example

```r
# Purpose: estimate the trend in notifications (plan: Analysis, trend model)
# Input:   data/output/notifications_clean.csv
# Output:  data/output/trend_fit.rds, data/output/trend_predictions.csv

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

A plotting script opens the same way:

```r
# Purpose: draw the trend in notifications (plan: Outputs, figure 2)
# Input:   data/output/trend_predictions.csv
# Output:  figures/figure2_trend.pdf, figures/figure2_trend.tiff

pacman::p_load(
  here,
  ggplot2
)

# 1. Style ----
# Single-column width of the target journal, in millimeters.
figure_width <- 89
theme_set(theme_classic(base_family = "Times New Roman", base_size = 7))
```
