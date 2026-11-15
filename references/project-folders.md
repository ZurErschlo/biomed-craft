# Project folders

A project folder the researcher can read at a glance: few layers, plain names and no stage numbers.

```text
project/
  00 folder        papers by other people, nothing else
  protocol/        registered protocol, research_plan.md, execution_log.md
  data/input/      collected and hand-entered data, read-only, with a dictionary for each table
  data/output/     everything the scripts rebuild
  analysis/        numbered scripts, and style.R for fonts and table format
  figures/         each figure as PDF and TIFF, written by the scripts
  tables/
  manuscript/      main text, supplement, main figures and main tables as Word files, dated YYYYMMDD
  archive/         files no longer used, in subfolders named by date and content
```

- `figures/` and `tables/` are flat and in number order, with no main or supplement subfolders.
- No nested projects and no `results/` folder. Files that are no longer used move to the single `archive/` folder; nothing is deleted without the researcher's approval. Before sheets or rows leave a workbook, a copy of the version that holds them goes to `archive/`.
- Scripts used once (to build or repair a workbook) and reference material stay out of the data and analysis folders: figures from other papers go with those papers, and a one-off script goes to `archive/` once it has run.
- Data files are CSV. Result tables are xlsx, one file per table. No table is kept in two formats. Figures are kept as PDF and TIFF in `figures/`; the manuscript folder holds one format of each.
- Dates in file names (YYYYMMDD) instead of version labels such as `v2` or `final`. The data extraction workbook carries its date.
- Each clean table has a data dictionary: variable name, meaning, unit, allowed values or range, missing-value code and source.
- No stray README, AGENTS.md or notes files. A single README at the root only when the code is shared or deposited, giving the script order, the inputs and outputs of each script, software versions and data sources.
- Nothing copied from other projects.
- The manuscript is written in Word once the analysis is done.
