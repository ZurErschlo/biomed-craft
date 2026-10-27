# Figures and tables

Conventions for figure legends, table titles and notes, and the text inside figures, in leading journals and their major sub-journals, from page-by-page inspection of figures and a count of every legend and table title in the calibration articles. Journal formats are in [journals.md](journals.md).

Legends, table notes and supplementary tables go into the paper as written. They contain only publication text.

## Legends

- In the manuscript file, the legend is text below the figure; the figure number and title travel with the figure.
- Title: in clinical, epidemiological and modelling journals, a noun phrase saying what is plotted: `Figure 2: Incidence of tuberculosis by WHO region, 2010–2022`. Finding-sentence titles belong to laboratory papers in Cell and, less often, Nature; Science legend titles are mostly noun phrases ending in a full stop.
- Body, in order: panel descriptions (`(A) …; (B) …` or `a, …`), then what each encoding means (points, lines, shading, error bars and the interval type, censoring marks, reference lines), then n, the statistical test and the data source, then abbreviations.
- Present tense for what is shown, past tense for methods: `Error bars show 95% CIs. Estimates were adjusted for age and sex.`
- Define every abbreviation used in the figure, even if the text already defined it.
- Length: Lancet and BMJ legends are short (often under 70 words); NEJM 20–60 words; Nature, Cell and Science 100–250 words.
- Legends describe; the text interprets. No `This figure shows` (META-05) and no conclusions such as `suggesting a decline` (CAP-01). NEJM's `Shown are…` is house style and acceptable.
- Caveats and status notes about a result (for example that a model did not pass validation) go in the legend, never inside the image.

## Text inside figures

Allowed (seen in most figures in leading journals):

- Panel letters, bold, top left, in the journal's case (Nature family lower case; most others upper case; JAMA boxed).
- Short panel or facet titles of a few words (in just over half of the papers inspected).
- Axis titles with the quantity and its unit: `Incidence (per 100 000)`; JAMA uses `Incidence, per 100 000`; NEJM uses Title Case.
- Legend keys with short titles (`Scenario`, `WHO region`) and direct labels on lines.
- Data annotations: an effect estimate with its interval on a Kaplan–Meier plot, numbers at risk, `Favours X | Favours Y` direction labels, labelled threshold or reference lines, period brackets.

Not allowed (no author-drawn figure in the core journals had them):

- A figure title, subtitle or caption inside the image (FIG-01, FIG-02).
- Explanatory sentences, caveats, status labels and footnotes inside the image (FIG-03).
- Project-specific labels: variable names, scenario or arm codes, file names (HYG-03, HYG-08, HYG-01).

Labels:

- One to four words; the same short label for the same category in every figure; full names and definitions in the legend (FIG-04).
- Short does not mean cryptic: a single letter for a category confuses readers (FIG-05).
- Labels use the manuscript's own terms and spelling.
- Check legibility at final size (5–7 pt is the usual minimum), and check that legend titles, tick labels and facet strips do not collide.
- In reviews, summary figures group studies by theme; study-level rows belong in forest plots and tables.
- English figures contain no Chinese characters or full-width punctuation (HYG-06).

## Common figure types

- Study flow (CONSORT, PRISMA): boxes start with the count (`355 were assigned…`); exclusions in side boxes with reasons; symbols resolved in the legend. Exclusion reasons use standard wording (`ineligible`, `declined`, `lost to follow-up`); labels such as `post hoc` do not appear.
- Kaplan–Meier curves: numbers at risk aligned under the axis; groups labelled directly or with a small key; effect estimate with interval (and P value where the journal prints one) inside the plot.
- Forest plots: numeric columns, a line of no effect, direction labels, log scale for ratios.
- Maps: binned keys with titles, and explicit `No data` and `Not applicable` classes.
- Model structure diagrams: compartments named in words, with subscripts as notation; arrows show flows and carry no sentences.

## Tables

- Title: a noun phrase (`Table 1: Baseline characteristics`). Placement follows the journal in print (journals.md); in the submission file put it above the table.
- Column headers give group sizes: `Intervention (n=1478)`.
- Declare the statistic format once: `Data are n (%), mean (SD) or median (IQR).` Put units in row labels (`Age, years`).
- Footnotes in this order: general note, abbreviations, then specific notes keyed by *, †, ‡, §, ¶, ||, **, †† or by letters (JAMA, Nature).
- Caveats go in the notes; headers and cells hold only labels and values.
- Distinguish missing from zero; say what `..` or `–` means.
- Keep decimals consistent within a column. No arrows, operators or `(+)/(−)` shorthand in headers; write `lower is better` in a note if needed.
- Three-line layout: rules above and below the header and at the bottom; no vertical rules; no coloured fills.

## Supplementary figures and tables

- Same legend structure as the main text, abbreviations defined again, the journal's numbering (`Table S1`, `eTable 1`, `Extended Data Fig. 1`, `Supplementary Table 1`).
- Parameter tables: Parameter (with time basis or price year), Value, Uncertainty range (95% UI or CrI), Distribution, Source (citation, `Assumption` or `Fitted`), Notes; rows grouped by model component; a footnote saying what the bounds mean.
- Search strategy tables: one per database with date range; numbered lines with full Boolean strings; a final combination line.
- Sensitivity analysis tables: parameter or scenario, range tested, then outcomes (incremental cost, incremental effect, ICER) by setting.
- Checklists (CONSORT, PRISMA, STROBE, CHEERS, GATHER): Section, Item number, Item, Location; update locations to the final version.
- Published supplements often contain code names, arm codes and stale cross-references because journals post them unedited. Do not copy that.
