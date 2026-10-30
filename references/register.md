# Process narration, engineering register, defensive writing and internal material

Four kinds of text that do not belong in a research paper. Rule IDs refer to `scripts/rules.json`. The test for every sentence: does it report the research (what was studied, how, what was found, what it means), or the writing, the software or the authors' worries? Only the first kind stays. What to keep is in the Keep list of `SKILL.md`.

## Process and metadata narration

Cues:

- Version history and revisions: `In the revised version…`, `the earlier version of this protocol` (META-01); `As requested by the reviewer…` (META-02).
- Status, dates and provenance: `provisional estimates`, `Last updated 13 October 2026`, `This document supersedes…` (META-08); `Course proposal only`, `Supply is not yet confirmed` (DEF-11).
- Previews: `In this section, we describe…` (META-03); `In this paper, we present…` (META-04). Self-description: `This figure shows…` (META-05); `Table 2 shows…` (META-06).
- Working history: `We initially tried…`, `After several iterations…`, `We reran the analysis…` (META-10).
- Writing rules leaking into text: `These labels must remain consistent across…` (META-11).
- Pointers to the project's own files (`execution log`, `research plan`, source tags such as `N12`) (META-09); chat residue (`Certainly!`, `Here is the revised abstract`) (META-07).

Rewrite: describe the study as it stands; replace pointers to own files with published or supplementary items (`appendix p 5`) and source tags with references; start sections with content. A changed outcome is reported once, where the journal asks for protocol changes. In a reply to reviewers, describing the change and its location is the content (`scan.py --doc response`).

## Engineering register

Cues:

- Software nouns: `pipeline`, `module`, `workflow`, `architecture`, `evidence streams`, `decision family` (ENG-01, ENG-06, ENG-08).
- Code operations: `ran the script`, `stored in a file`, `executed`, `debugged` (ENG-02).
- Implementation details in summaries and results: `in 10 000 simulated trials`, `1000 model runs` (ENG-03); seeds, file hashes, commit identifiers (ENG-04).
- Slang: `sanity check`, `source of truth`, `out of the box`, `deep dive` (ENG-05).
- Symbols and code tokens as words: arrows, `↑`, `3x higher`, `w/`, `data$age`, `TRUE` (ENG-07, ENG-09).
- Results that narrate procedure: `records were indexed`, `values were filled`, `then… then…` fallback chains (ENG-08).

Rewrite: name the scientific operation (linkage, imputation, calibration, inclusion criteria): `Our pipeline cleaned and merged the records` becomes `We linked notification and laboratory records by national identifier and removed duplicates.` Methodological quantities stay in Methods, written as methods (`We drew 1000 parameter sets from the prior distributions`). Software is cited with its version in Methods; code goes in the availability statement; seeds and hashes stay in the repository. Established technical terms (calibration, bootstrap, robust standard errors, a named published tool) stay.

## Defensive writing

Cues:

- Throat-clearing: `It should be noted that` (DEF-01). Stacked hedges: `could potentially`, `may possibly` (DEF-02). Uncheckable qualifiers: `to some extent`, `arguably` (DEF-03).
- Disclaimer tails: `should be interpreted with caution`, `does not establish causality` (DEF-04). Narrated candour: `We are upfront about…`, `Admittedly…` (DEF-05). Status hedges: `indicative only`, `for illustrative purposes` (DEF-06).
- Generic calls for research (DEF-07). Pre-empting misreadings: `We do not claim that…` (DEF-08). An absent opponent: `One might argue that…` (DEF-09). Softening formulas: `Despite these limitations, our findings provide…` (DEF-10).
- The same caveat repeated across sections or slides.

Rewrite: bound the claim with facts (who, how, how long). Each limitation appears once, as problem, consequence and direction of bias: `Outcomes came from routine registers, which might miss deaths after transfer; this would bias the estimate towards the null.` Risks become plans with milestones; future research becomes specific (`A trial in children is needed to set the dose`). Critical appraisal of other studies stays.

## Internal material

Anything that only makes sense inside the project. Legends, table notes, supplementary tables and data files are held to the same standard.

Cues:

- File names and paths (HYG-01, HYG-02); `snake_case`, `camelCase` and `CODE_LABEL` identifiers (HYG-03, HYG-04, HYG-08); version tags such as `_v3`, `_final` (HYG-07).
- Placeholders: `[TODO]`, `[citation needed]`, `{{n_total}}` (HYG-05). Chinese characters or full-width punctuation in English text (HYG-06).
- AI tool names (HYG-09) and tracking residue in links (`utm_source=chatgpt.com`) (HYG-10). Status tags: `(simulated)`, `(post hoc)` (HYG-11).
- Labels only the project uses (`actual`, `should`, `gap`) and material from other projects.

Rewrite: use the public name of every variable, group and scenario; refer to items by their published labels (`Table S8`). Before submission, scan the exported Word files and figure PDFs, not only the source: `python3 scripts/scan.py --strict manuscript.docx figures/*.pdf`. Accession numbers, native-script author names the journal allows, and an AI-use disclosure the authors wrote stay.
