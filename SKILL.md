---
name: plain-paper
description: |
  Write, edit and review English academic writing to the standard of flagship journals (Lancet, NEJM, JAMA,
  BMJ, Nature, Science, Cell) and their major sub-journals. Covers every section of a research article,
  supplementary material, figure legends, table notes and text inside figures, plus protocols, response letters,
  consent forms and slides. Removes AI-style patterns such as "not X but Y" contrast frames, stock vocabulary and
  em-dash asides, as well as engineering jargon, defensive hedging and process or metadata narration. Use when
  drafting, polishing, rewriting or proofreading English papers, or when asked to 润色, 优化表达, 去AI味, 改写,
  审校 or 改图注.
license: MIT
metadata:
  version: "1.0.0"
---

# Plain Paper

Write English research prose the way flagship journals print it. Every sentence reports what was studied, how it was studied, what was found, or what it means, in words a reader can check.

The rules come from 124 research articles in flagship journals and their major sub-journals (main text, supplements, figures and tables), the editing decisions of this skill's author, and public skills for removing AI-style writing. Where journals differ, follow the target journal.

## Start here

1. Identify the document and the part being edited (a section, a legend, a table, figure code, a supplement, a response letter, a protocol, slides), the study design, and the target journal. Take these from the user, the file or its reference style. If no journal is named, keep the document's existing conventions; for new text use Lancet style ([journals.md](references/journals.md)).
2. Read the surrounding text and match its register and terms. For protocols, response letters, cover letters, consent forms, slides and grant proposals, also read [documents.md](references/documents.md).
3. Do not ask questions the text answers. Edit, then report what changed.

## Protect

- Numbers, units, denominators, intervals, P values, citations, cross-references and defined terms.
- The strength of each claim: scope conditions, negations, null results and hedges that carry real uncertainty. Narrow an overclaim with numbers; never strengthen a claim.
- LaTeX commands, citation keys, Markdown or Quarto syntax and code chunks.
- Facts: add none, and invent no references, data or quotations. When a sentence needs a number the text does not give, tell the user. Add a cross-reference (`Table S8`, `appendix p 5`) only when its target is certain.

## Modes

- **Draft**: from notes, results or an outline, write the section. Put the content in the order given in [sections.md](references/sections.md) before writing sentences.
- **Optimise** (`润色`, `优化`): diagnose structure first (the order of moves in each section, topic sentences, the chain from burden to gap to aim to design to finding), then sentences ([craft.md](references/craft.md)), then AI-style patterns, then journal style.
- **Review** (`审校`): list problems as a table with columns Original, Revised and Reason, and give each location. No generic advice such as "consider polishing".
- **Check**: run `scripts/scan.py` on the files (Word, Markdown, Quarto, LaTeX, PowerPoint, PDF, SVG, R or Python plotting code) and fix what it reports.

## Order of work

1. Remove process and metadata narration, internal material and chat residue ([register.md](references/register.md)).
2. Replace engineering register with the scientific operation.
3. Cut defensive writing; state each limitation once, with its consequence.
4. Remove AI-style sentence shapes and vocabulary ([patterns.md](references/patterns.md)).
5. Bring each section to flagship form ([sections.md](references/sections.md)), and legends, tables and figure text to [figures-tables.md](references/figures-tables.md).
6. Apply the journal's style ([journals.md](references/journals.md), [format.md](references/format.md)).
7. Check: run the scanner again, run `scripts/check_preservation.py` on the original and the revision, and reread for new tells and choppy sentences.

## Core rules

Sentences:

- Subjects are people, data, studies or the trial. Verbs are plain: found, estimated, compared, were associated with.
- Lead with the result and its number, then the interval, then the pointer in parentheses: `(figure 2)`.
- One hedge per claim, on the interpretation. Match verbs to the design: causal verbs for trials, `associated with` for observational data, `estimated` for models.
- Compare named, measured things and give both numbers. Use contrast frames only for a technical distinction.
- Keep implications and recommendations within the population, setting and design studied. When the input claims more (`across Africa`, `all patients`), narrow it and tell the user.
- Aim for an average of 20–30 words per sentence and avoid runs of short sentences.
- One term per concept; define abbreviations and symbols before use.

Never in a manuscript:

- Revision history, version numbers, dates of writing, status labels, pointers to the project's own logs or plans, previews of what a section will do.
- File names, paths, variable names, scenario codes, seed values, file hashes, placeholders, Chinese characters in English text.
- `It is important to note`, stacked hedges, `we do not claim`, `one might argue`, generic calls for more research.
- Negate-then-assert contrasts (`The gap is not cost. It is coverage.`) and the words and phrases marked must-fix in [patterns.md](references/patterns.md).
- Bullet lists, bold for emphasis, emoji and Markdown markup in manuscript prose.

Figures and tables:

- Legends are text below the figure. They start with a noun phrase saying what is plotted, then describe panels, encodings, n and tests, then define abbreviations. Legends describe; the text interprets.
- Inside the image: panel letters, short panel titles, axis titles with units, keys, direct labels and data annotations. No figure titles, subtitles, sentences, caveats or project labels.
- Tables: group sizes in headers, the statistic format declared once, footnotes in the journal's order, three-line layout.
- Supplements meet the same standard as the main text.

## Keep (do not over-correct)

- `associated with` for observational results; `might` or `probably` on an explanation; intervals and scope conditions.
- Null results with their intervals.
- A contrast that is the finding, with both numbers.
- Passive voice in Methods, and `we` where the journal uses it.
- En dashes in numeric ranges, semicolons, and `rather than` for a method choice.
- Technical terms: `robust standard errors`, `critically ill`, `pivotal trial`, `seamless phase 2–3 design`, accession numbers.
- In response letters, the description of each change and where it is.
- One priority claim (`To our knowledge…`) when a reported search supports it and the journal prints such claims.

## Second opinions

When the user asks for another model's review (for example agy or grok on this machine), send the text for read-only review, check every comment against the text and the evidence, and write the fixes yourself. Reject suggestions that swap plain words for formal ones (`markedly`, `thereby`, `fundamentally`, `imposes`).

## Scripts

Python 3.10 or later, standard library only; PDF input needs `pdftotext`. Paths are relative to this skill's folder.

```bash
python3 scripts/scan.py manuscript.docx                       # findings by rule
python3 scripts/scan.py --profile --journal lancet draft.md   # style profile against flagship ranges
python3 scripts/scan.py --strict legends.md figures/*.R       # exit status 1 on must-fix findings
python3 scripts/scan.py --doc response response_letter.docx   # allows revision narration
python3 scripts/check_preservation.py original.docx revised.docx
python3 scripts/calibrate.py ~/Zotero                         # rebuild reference rates from your own PDFs
```

Findings have three levels. Must: flagship journals almost never print it, or it is internal material. Review: judge in context and rewrite unless the word carries meaning. Density: normal in moderation and compared with flagship rates. The corpus and method are described in [calibration.md](references/calibration.md); worked examples are in [examples.md](references/examples.md); sources are in [sources.md](references/sources.md).

## Output

- Edits: return the revised text, then a short list of the main kinds of change. Keep comments out of the manuscript itself.
- Word files: edit the Word file, with tracked changes if the user wants to see them. Do not convert it to Markdown.
- Reviews: the Original, Revised and Reason table.
- Create no extra files (logs, notes, summaries) unless asked. Apply the recommended edits without asking permission for each one.
