# Process narration, engineering register, defensive writing and internal material

Four kinds of text that do not belong in a research paper. Each section lists the cues, how to rewrite, and what to keep. Rule IDs refer to `scripts/rules.json`.

The test for every sentence: does it report the research (what was studied, how, what was found, what it means), or does it report the writing, the software, or the authors' worries? Only the first kind stays.

## Process and metadata narration

Text about the document, its history or its production.

Cues:

- Version history and revisions: `In the revised version…`, `the earlier version of this protocol`, `(the earlier win-probability outcome)` (META-01); `As requested by the reviewer…` (META-02).
- Status, dates and provenance: `provisional estimates`, `Last updated 13 October 2026`, `This document supersedes…` (META-08); status disclaimers such as `Course proposal only` or `Supply is not yet confirmed` (DEF-11).
- Previews and roadmaps: `In this section, we describe…`, `The remainder of this paper…` (META-03); `In this paper, we present…` (META-04).
- Self-description: a legend that says `This figure shows…` (META-05); a Results sentence that opens `Table 2 shows…` (META-06); sentences explaining how a chart was built or what a table groups.
- Working history: `We initially tried…`, `After several iterations…`, `We reran the analysis…` (META-10).
- Writing rules leaking into text: `These labels must remain consistent across…`, `Original reports take precedence over summaries` (META-11).
- Pointers to the project's own files: `execution log`, `research plan`, `working notes`, source tags such as `N12`, other projects (META-09).
- Chat residue: `Certainly!`, `Here is the revised abstract`, `I hope this helps` (META-07).

Rewrite:

- Describe the study as it stands. Report a changed outcome once, where the journal asks for protocol changes (for example in Methods or the trial registry).
- Replace pointers to the project's own files with published or supplementary items (`appendix p 5`), or delete them.
- Replace source tags with formal references.
- Start sections with content. A research article needs no roadmap.

Keep:

- In a response to reviewers, describing the change and its location is the content (`We added a sensitivity analysis excluding…; see Methods, lines 120–128`). Use `scan.py --doc response`.
- Protocol amendments and registration changes that the journal requires, stated as facts with dates.
- A one-sentence roadmap at the end of a review's introduction.

## Engineering register

Software and data-processing language used for research procedures.

Cues:

- Software nouns: `pipeline`, `module`, `workflow`, `architecture`, `evidence streams`, `decision family`, `analytical unit` (ENG-01, ENG-06, ENG-08).
- Code operations: `ran the script`, `stored in a file`, `executed`, `deployed`, `debugged` (ENG-02).
- Implementation details in summaries and results: `in 10 000 simulated trials`, `1000 model runs` (ENG-03); `seed = 2024`, file hashes, commit identifiers (ENG-04).
- Slang: `sanity check`, `source of truth`, `drop-in`, `out of the box`, `deep dive` (ENG-05).
- Symbols and code tokens as words: arrows, `↑`, `3x higher`, `w/`, `num/den`, `data$age`, `TRUE` (ENG-07, ENG-09).
- Results that narrate procedure: `records were indexed`, `values were filled`, `remained distinct`, `then… then… then…` fallback chains (ENG-08).
- Reproducibility sections listing script names, file names, package versions, seed values and file hashes.

Rewrite:

- Name the scientific operation: linkage, imputation, calibration, cleaning rules, inclusion criteria. `Our pipeline cleaned and merged the records` becomes `We linked notification and laboratory records by national identifier and removed duplicates.`
- Keep methodological quantities in Methods, written as methods: `We drew 1000 parameter sets from the prior distributions.` Remove them from the abstract, results text and slides.
- Cite software with name and version in Methods (`R, version 4.4.1`). Put code and data access in the availability statement (`Code is available at https://github.com/…`). Leave seed values and file hashes in the repository.
- Replace chains of procedure with the rule the reader needs: `When national data were missing, we used the narrowest region with data.`

Keep:

- Established technical terms of the field: calibration, simulation, bootstrap, robust standard errors, a named published tool (`nf-core/sarek`), model compartments.

## Defensive writing

Sentences written to guard the authors against objections. They add nothing about the research.

Cues:

- Throat-clearing: `It should be noted that`, `It is important to note that` (DEF-01).
- Stacked hedges: `could potentially`, `may possibly`, `it is possible that… might` (DEF-02).
- Uncheckable qualifiers: `to some extent`, `in some cases`, `somewhat`, `arguably` (DEF-03).
- Disclaimer tails: `should be interpreted with caution`, `does not establish causality`, `remains conditional on`, `rather than a universal estimate` (DEF-04).
- Narrated candour: `We are upfront about…`, `We acknowledge that…`, `Admittedly…` (DEF-05).
- Status hedges: `indicative only`, `for illustrative purposes` (DEF-06).
- Generic calls for research: `Further research is needed.` (DEF-07; absent from the 124 flagship articles).
- Pre-empting misreadings nobody made: `We do not claim that…`, `This does not mean that…`, `This is not a cost-effectiveness claim` (DEF-08).
- Arguing with an absent opponent: `One might argue that…` (DEF-09).
- Softening formulas: `Despite these limitations, our findings provide…` (DEF-10).
- The same caveat repeated across sections or slides.

Rewrite:

- State the finding with its interval and the design. The boundary of a claim comes from facts: who was studied, how, for how long.
- Put each limitation in one place (the limitations paragraph, or where the estimate is reported) and write it as problem, consequence, and direction of bias or mitigation: `Outcomes came from routine registers, which might miss deaths after transfer; this would bias the estimate towards the null.`
- State risks as plans with milestones: `Supply agreements will be signed by month 6; if not, the trial will use the alternative supplier.`
- Make future research specific: `A trial in children is needed to set the dose.`

Keep:

- Hedges that carry real uncertainty (association wording for observational data; `probably` on an explanation; scope conditions; intervals).
- Accurate null results: `did not differ` is a finding; do not turn it into `had no effect`, and do not delete it.
- Critical appraisal of other studies (`their design does not establish causality`).
- A contrast that is itself the finding, with both numbers.

## Internal material

Anything that only makes sense inside the authors' project. Legends, table notes, supplementary tables and data files go into the paper as written, so they are held to the same standard.

Cues:

- File names and paths (HYG-01, HYG-02); `snake_case`, `camelCase` and `CODE_LABEL` identifiers (HYG-03, HYG-04, HYG-08); version tags such as `_v3`, `_final`, `v1.1` (HYG-07).
- Placeholders: `[TODO]`, `[citation needed]`, `{{n_total}}`, `XXX` (HYG-05).
- Chinese characters or full-width punctuation in an English document (HYG-06).
- AI tool names (HYG-09) and chat or tracking residue in links (`utm_source=chatgpt.com`) (HYG-10).
- Status tags in parentheses: `(simulated)`, `(appendix)`, `(post hoc)` (HYG-11).
- Labels for groups or scenarios that only the project uses (`actual`, `should`, `gap`), and material from other projects.

Rewrite:

- Use the public name of every variable, group and scenario, and define it once.
- Refer to items by their published labels (`Table S8`, `Supplementary Data 1`).
- Before submission, scan the exported Word files and the figure PDFs, not only the source text: `python3 scripts/scan.py --strict manuscript.docx figures/*.pdf`.

Keep:

- Accession numbers, locus tags and repository identifiers in genomic methods (`NC_000962.3`).
- Native-script author names where the journal allows them.
- A disclosure of AI use that the journal requires and the authors wrote. Do not write one for them.
