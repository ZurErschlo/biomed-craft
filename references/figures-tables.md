# Figures and tables

How to choose the figures and tables of a paper, and the conventions for legends, table titles and notes, and the text inside figures, in leading journals and their major sub-journals. The conventions come from page-by-page inspection of figures and a count of every legend and table title in the calibration articles; the choice of display items follows ICMJE and the author's decisions on their own papers. Journal formats are in [journals.md](journals.md).

Legends, table notes and supplementary tables go into the paper as written. They contain only publication text: no plan section numbers, record identifiers, screening rounds, change logs, tool names or file paths.

## Choosing the display items

- Each result appears once: in a figure or a table, in the main text or the supplement. ICMJE asks authors not to duplicate data in graphs and tables, and the EASE guidance says the same. Duplicates include a panel that redraws numbers a table already gives, a supplementary figure that redraws a main figure, a supplementary table that copies the numbers printed on a figure, and columns that restate the same values (a log ratio and its variance next to the ratio and its interval).
- Not duplicates: a table of the values behind a figure that plots points without printing them; the reference row of a sensitivity analysis table; a GRADE evidence profile behind its summary-of-findings table; study-level lists behind summary counts; the pooled diamond of a forest plot whose estimate a table also gives, with statistics the plot cannot hold. Reporting forms are not results, and a systematic review keeps its PRISMA flow diagram.
- A figure when the reader needs a shape: the spread across studies, a comparison between groups, change over time or along a threshold, the relation between two quantities such as cost and effect, geography, gaps in the evidence. A table when the reader needs exact values: many variables or units, several statistics for each result, counts and proportions. A handful of points makes a poor figure; put them in a table.
- Resolve an overlap by planning the set, not by deleting one item of the pair. Go through the Results section by section, give each section the table or figure that carries its finding, and number the items in the order the text first cites them. Then check that the argument still reads in order, that every number the text quotes can be found in a display item, and that each headline finding of the abstract, discussion or conclusion has one in the main text.
- One message per figure. Merge two figures only when the journal's limit forces it. NEJM and JAMA original articles allow five tables and figures in total; check the current instructions before planning the set.
- A stratum the question names (a resistance group, an age group, sex) appears in every main result where it applies, under the paper's term. A table that can hold it holds it.
- Look at the figures themselves in recent articles from leading journals and from sub-journals known for clear figures, beyond the papers the researcher supplied. The test is whether a reviewer gets the result at a glance.

## Legends

- Legends are text, never part of the image: below each figure in the figures file, and also listed after the main text when the journal asks for that. The figure number and title travel with the figure.
- Title: in clinical, epidemiological and modelling journals, a noun phrase saying what is plotted: `Figure 2: Incidence of tuberculosis by WHO region, 2010–2022`. Finding-sentence titles belong to laboratory papers in Cell and, less often, Nature; Science legend titles are mostly noun phrases ending in a full stop.
- Body, in order: panel descriptions (`(A) …; (B) …` or `a, …`), then what each encoding means (points, lines, shading, error bars and the interval type, censoring marks, reference lines), then n, the statistical test and the data source, then abbreviations.
- Present tense for what is shown, past tense for methods: `Error bars show 95% CIs. Estimates were adjusted for age and sex.`
- Define every abbreviation used in the figure, even if the text already defined it.
- What a legend holds: the title, what each panel plots, what markers, lines, shading and intervals mean, n and the test where the journal prints them, and the abbreviations. How a value was computed and the full definitions of categories belong in the Methods. Fewer than one legend in five in Lancet and BMJ papers describes a computation, against two in five in laboratory papers, which also give n and the test in the legend.
- Length follows the journal and the study type. Median words in the library's research articles (interquartile range): BMJ 51 (33–73), Lancet 62 (28–96), JAMA journals 75 (37–112), NEJM about 100 to 130, Nature 106, Science 148, Cell 202. By design: economic evaluations 44, systematic reviews 58, trials, cohorts and models about 90, computational papers 162, laboratory papers 211. In clinical and population research, keep a main-text legend under about 120 words plus its abbreviations.
- A legend does not repeat numbers the figure prints or a table gives.
- Legends describe; the text interprets. No `This figure shows` (META-05) and no conclusions such as `suggesting a decline` (CAP-01). NEJM's `Shown are…` is house style and acceptable.
- Caveats and status notes about a result (for example that a model did not pass validation) go in the legend, never inside the image.

## Text inside figures

Allowed (seen in most figures in leading journals):

- Panel letters, bold, top left, in the journal's case (Nature family lower case; most others upper case; JAMA boxed); upper case while the journal is not settled.
- Short panel or facet titles of a few words (in just over half of the papers inspected).
- Axis titles with the quantity and its unit: `Incidence (per 100 000)`; JAMA uses `Incidence, per 100 000`; NEJM uses Title Case.
- Legend keys with short titles (`Scenario`, `WHO region`) and direct labels on lines.
- Data annotations: an effect estimate with its interval on a Kaplan–Meier plot, numbers at risk, `Favours X | Favours Y` direction labels, labelled threshold or reference lines, period brackets.

Not allowed (no author-drawn figure in the core journals had them):

- A figure title, subtitle or caption inside the image (FIG-01, FIG-02).
- Explanatory sentences, caveats, status labels and footnotes inside the image (FIG-03).
- A table inside a panel. Put the numbers in a table or the legend.
- Project-specific labels: variable names, scenario or arm codes, file names (HYG-03, HYG-08, HYG-01).

Layout and type:

- One font for all text in figures and tables, the manuscript's font: Times New Roman unless the journal asks for another. Check the embedded fonts with `pdffonts`.
- Equal margins, nothing touching the edge, even spacing between panels and aligned panel edges. A crowded figure is redesigned (fewer panels, or two figures), not shrunk.
- Short keys run horizontally above or below the plot. A legend or facet title keeps its unit on the same line: `Deaths (per 100 000)`.
- Stack only the parts of a whole. Quantities that do not add up to a total are not stacked.

Labels:

- One to four words; the same short label for the same category in every figure; full names and definitions in the legend (FIG-04).
- Short does not mean cryptic: a single letter for a category confuses readers (FIG-05).
- Labels use the manuscript's own terms and spelling.
- Check legibility at final size (5–7 pt is the usual minimum), and check that legend titles, tick labels and facet strips do not collide.
- In reviews, summary figures group studies by theme; study-level rows belong in forest plots and tables.
- English figures contain no Chinese characters or full-width punctuation (HYG-06).

## Common result figures

- Kaplan–Meier curves: numbers at risk aligned under the axis; groups labelled directly or with a small key; effect estimate with interval (and P value where the journal prints one) inside the plot.
- Forest plots: numeric columns, a line of no effect, direction labels, log scale for ratios.
- Maps: binned keys with titles, and explicit `No data` and `Not applicable` classes.

## Diagrams drawn by hand

Model structures, intervention pathways, conceptual frameworks and study flow diagrams are drawn in a diagram tool such as draw.io. They are not made by the analysis code, and they have their own requirements.

- The drawing file is the original: edit it, and keep it with its exported images.
- The diagram matches the plan and the code: the same states, flows, symbols and line styles. Redraw it whenever the model or the study design changes.
- Model structures: compartments named in words, with subscripts as notation. Each arrow carries one parameter symbol from the plan, and the full rate expressions go to a transition table. Direction is unambiguous: merged lines keep an arrow on each branch, and there are no junction dots. Flows that leave every compartment, such as background deaths, are not drawn, and the legend says so.
- Study flow (CONSORT, PRISMA): boxes start with the count (`355 were assigned…`); exclusions in side boxes with reasons; symbols resolved in the legend. Exclusion reasons use standard wording (`ineligible`, `declined`, `lost to follow-up`); labels such as `post hoc` do not appear. No internal or unfinished labels, and no boxes repeating counts that a results table gives (studies per analysis belong with the results).
- Layout: boxes aligned and evenly spaced, equal margins, nothing touching the edge, and no text over arrows.
- Legends are short (median 48 words in clinical journals): what the diagram shows, notes on its counts, and the abbreviations. A model structure's legend defines its symbols and points to the transition table.

## Tables

- Title: a noun phrase (`Table 1: Baseline characteristics`). Placement follows the journal in print (journals.md); in the submission file put it above the table.
- Column headers give group sizes: `Intervention (n=1478)`.
- Declare the statistic format once: `Data are n (%), mean (SD) or median (IQR).` Put units in row labels (`Age, years`).
- Footnotes in this order: general note, abbreviations, then specific notes keyed by *, †, ‡, §, ¶, ||, **, †† or by letters (JAMA, Nature).
- Notes give what a reader needs to read the table: the statistic format, abbreviations, symbols, the meaning of `..`, and definitions of scales or categories in keyed notes. How estimates were computed belongs in the Methods. Length follows the journal: Science and Cell tables carry almost no notes; Lancet and BMJ about 60 words; JAMA about 140, mostly abbreviations; NEJM about 260, with definitions keyed to symbols.
- Caveats go in the notes; headers and cells hold only labels and values.
- Distinguish missing from zero; say what `..` or `–` means.
- Keep decimals consistent within a column, and give the same quantity the same decimals in every table. An interval stays on one line; set column widths so it does not wrap.
- No arrows, operators or `(+)/(−)` shorthand in headers; write `lower is better` in a note if needed.
- Three-line layout: rules above and below the header and at the bottom; no vertical rules; no coloured fills.
- Main and supplementary tables use the same group order and terms. Studies with the same first author and year carry letters (2022a, 2022b).

## Supplementary figures and tables

- Every supplementary item is cited in the main text and numbered in the order of first citation. Supplements hold detail and source data (study-level data, the values behind plotted points), not repeats of main-text items; the number of items matters less than whether each is cited and adds something.
- Very long tables, such as study lists and study-level extracted data, go to a separate spreadsheet of supplementary data, cited like any other item.
- Same legend structure as the main text, abbreviations defined again, the journal's numbering (`Table S1`, `eTable 1`, `Extended Data Fig. 1`, `Supplementary Table 1`).
- Parameter tables: Parameter (with time basis or price year), Value, Uncertainty range (95% UI or CrI), Distribution, Source (citation, `Assumption` or `Fitted`), Notes; rows grouped by model component; a footnote saying what the bounds mean.
- Search strategy tables: one per database with date range; numbered lines with full Boolean strings; a final combination line.
- Sensitivity analysis tables: parameter or scenario, range tested, then outcomes (incremental cost, incremental effect, ICER) by setting.
- Checklists (CONSORT, PRISMA, STROBE, CHEERS, GATHER): Section, Item number, Item, Location; update locations to the final version.
- Published supplements often contain code names, arm codes and stale cross-references because journals post them unedited. Do not copy that.

## Result figures and tables made by code

- Change a figure or table only through the script that makes it, never by editing the output. After a change that should not touch values (labels, fonts, layout), confirm that the computed results are unchanged.
- The scripts write each figure to `figures/` as PDF and TIFF. The manuscript package carries one format of each, since `figures/` keeps the originals. The values each figure plots go to `data/output/`, not `figures/` ([analysis-code.md](analysis-code.md)).
## Assembling and changing the set

- For submission, one Word file of main figures and one of main tables, each item followed by its title and its legend or notes; the supplement carries its own figures and tables.
- After any change to the set: renumber; update the citations in the text, the legends, the supplement's cross-references, the reporting checklist (locations and page numbers), the scripts, the README and the plan; search the whole package for old numbers (`Figure 6`, `Figures 1–6`); rebuild the package; and show the researcher any new design before calling the change done.

## Working through figures with the researcher

- Brief one figure at a time: why it exists and its one message, each panel, and how to read it.
- Show each proposed change as a rendered figure. An idea that sounds better can look worse once drawn (offset error bars, for example); keep the earlier version when it reads better.
- Have someone other than the maker check the final set: another agent or a co-author.

## Checks before submission

- Every rendered page: numbering and order, every title, legend and note present, wide tables fitted (landscape if needed), no row split across pages, nothing cut off, one font, no stray blank space.
- Counts in legends match the current data after any rerun.
- A figure plots the statistic the text and tables use: a frontier chosen on means is drawn at means. Totals and differences are computed draw by draw and then summarised, never summed from medians.
- A share names its base when two are possible, such as all costs or attributable costs.
- Labels say what was done: a fit to the whole period is not labelled held-out.
- Axis limits clip no interval or point; facet labels do not reuse the panel letters; a table uses one currency and price year, and each column one unit.
