# Numbers, units and mechanics

Journal-specific forms are in [journals.md](journals.md). Whatever the journal, be consistent within the document.

## Numbers

- Report estimates with their interval: `1·60 (95% CI 1·40–1·83)`; for pooled estimates add the prediction interval and heterogeneity where relevant: `(95% PI 0·80–3·20; I²=94%; k=33)`.
- Give proportions with denominators: `144 (71%) of 204` (Lancet), `144 of 204 patients (70.6%)` (NEJM). In a table, a denominator shared by a row or a block is given once, in its label.
- Use the journal's decimal mark (Lancet mid-line point `0·5`; others `0.5`) and thousands separator (Lancet thin space for five or more digits, `10 000`; NEJM and Nature comma, `10,000`; JAMA thin space).
- Ranges: en dash (`2010–2020`, `1·2–3·4`) in most journals; hyphen in JAMA intervals; `to` when a range includes a negative number, and in NEJM and BMJ intervals.
- Write `from 2010 to 2020` or `2010–2020`, never `from 2010–2020`.
- Year ranges follow the target journal: the Lancet journals mostly print `2010–19`; JAMA, NEJM and Science print `2010–2019`. When a paper uses both, check whether the journal's own rule explains it before changing anything.
- Do not start a sentence with a numeral (FMT-05). Many journals spell out numbers below 10 except with units; follow the journal.
- People are counted in whole numbers; averages are labeled as averages (FMT-02).
- Keep the same number of decimals for the same quantity across text, tables and figures, and check that numbers in the abstract, text, tables and figures agree.

## P values and statistics

- Use the journal's form: Lancet `p=0·03`, `p<0·0001`; NEJM `P = 0.03`, `P<0.001`; JAMA `P = .03`, `P < .001`; BMJ `P=0.03`.
- Never `p=0.000` (FMT-01). Report P values to two significant figures unless the journal says otherwise.
- `Significant` refers to a statistical test (LEX-08). Non-significance is not evidence of no effect; report the estimate and interval.
- Name the uncertainty measure every time it appears in a figure or table (SD, SE, 95% CI, IQR, UI, CrI).
- Italicize statistical symbols if the journal does (n, P, t, F).

## Units and symbols

- SI units with a space between number and unit (`5 mg`, `37 °C`); no space before `%`.
- State the currency and price year: `2025 US$` or `2025 international dollars (Int$)`.
- Define each symbol before its first use and keep subscripts identical in text, equations, tables and figures (write `g_R` everywhere; mixing `g = R` and `R` confuses readers).

## Abbreviations

- No abbreviation before its full term. Define it at first use in the abstract, again in the main text, and in each legend, table note and supplement. A protocol, consent form, cover letter or slide deck (speaker notes included) is read on its own and defines its own.
- Abbreviate only terms used at least three times. Titles spell terms out; a trial acronym goes in a title only where the journal's title style puts one (`… (ACRONYM): a randomized controlled trial`).
- Terms readers of the journal know need no definition (CI, SD, IQR, DNA, HIV, WHO and the like; the journal's own list wins). Instruments, trials, databases and software keep their published names, introduced at first use with the full name where one exists (`the EuroQol five-dimension five-level questionnaire (EQ-5D-5L)`) or with what they are.
- Do not abbreviate everyday words to save space.
- `scan.py` flags an abbreviation used before its definition or never defined (FMT-06). The abstract and the main text share one list of definitions in the script, so check the definitions in the main text by eye.

## Spelling and grammar

- American spelling throughout, whatever the journal (FMT-07); the journal's copy editors apply its house spelling. A style file may set `Spelling: British` (-ise and -our) or `Spelling: Oxford` (-ize and -our) instead ([personal-style.md](personal-style.md)). Proper names, quotations and the titles of references keep their own spelling. What the journals print: the Lancet family and the BMJ use British -ise forms; the Nature journals use -ize, with -our and `modelling` in Nature and Nature Human Behaviour; Nature Medicine, NEJM, JAMA, Cell and Science use American spelling.
- `Data` takes a plural verb (`data are`; FMT-03).
- No contractions (FMT-04).
- Hyphenate compound modifiers before a noun (`drug-resistant tuberculosis`) but not after (`the strain was drug resistant`), unless the journal style says otherwise.
- Sentence-case headings unless the journal uses Title Case (NEJM figure and table titles, JAMA titles).

## Files

- Word manuscripts: edit in Word, keep the document's styles, and use tracked changes when the user asks to see edits. Do not convert a Word manuscript to Markdown for delivery.
- A section that holds only a placeholder is deleted before the file goes to co-authors or a journal, heading included (HYG-05). After any change of layout, update the page numbers in the contents and in the reporting checklist.
- LaTeX: keep `\cite{}`, `\ref{}`, `\label{}`, maths and comments intact; escape `%`, `_` and `&` in text; do not add formatting commands such as `\textbf{}` for emphasis.
- Markdown or Quarto: keep citation keys (`[@smith2020]`), cross-reference labels and code chunks intact.
- After editing, run `scripts/check_preservation.py original revised` to confirm that numbers, citations, cross-references and links survived.
- Word files with reference-manager fields (EndNote, Zotero): count the citation fields before and after editing and list any that disappeared (`check_preservation.py` counts both kinds). Never change text inside a field by hand, and remind the researcher to update the fields in Word afterwards. To turn the citation keys of a Markdown draft into live fields, see [citations.md](citations.md).
- Tracked changes mark only the words that changed. Before handing a file back, check both ways: rejecting every change gives the original text, and accepting every change gives the revision (`check_preservation.py` does this for Word files). Changes made by other people keep their author.
- Every citation in the text has an entry in the reference list, and every entry is cited; numbered references follow the order of first citation with no gaps (`scripts/check_references.py refs.ris --manuscript ms.docx`).
- Count words by the target journal's own rule (which parts are left out), on the final file. When the rule is unclear, take the higher count.
