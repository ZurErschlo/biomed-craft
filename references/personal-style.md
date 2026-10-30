# Personal style

The skill brings the standard; the researcher brings the style. Each researcher keeps a style file that records how they write, so that two people using this skill end up with work that is equally sound and recognisably their own. The file is personal: it stays on the researcher's computer and is never part of this repository.

## The file

- `~/.biomed-craft/style.md`, or `style.md` in the folder named by `BIOMED_CRAFT_HOME`. Plain Markdown that any agent can read and the researcher can edit.
- Create it from the template below the first time a style entry is confirmed. If the agent cannot write outside the project, ask once for permission; if writing stays blocked, show the exact lines and ask the researcher to paste them in.
- Style only: no numbers, data, project names, people or content. About 150 lines at most.

## Reading it

At the start of every writing, polishing, figure or code task, read the file if it exists. Apply the `General` entries and every section whose scope matches the task: the document, the study type, the journal, and figures and tables. A scoped entry wins over a general one.

Order of precedence:

1. Facts, numbers, sources and the Protect list in `SKILL.md`. No style entry changes them.
2. The target journal's requirements.
3. The style file, over the skill's style defaults and over review- and density-level rules.
4. A must-level style rule: say once that leading journals rarely print the form, then follow the researcher if they confirm.

`scan.py` reads the file too. Findings for rules named in `Allow [ID]` entries are listed apart, as allowed by the style file, never for rules on internal material (HYG).

## Adding to it

- An explicit instruction ("always write it this way", "I never use this word") is saved at once, with the date.
- When the researcher revises a draft, compare the draft and the revision with `scripts/style_diff.py` (two files, or one Word file with tracked changes). Edits that changed numbers, citations or claims are content, not style, and the script sets them aside.
- A pattern noticed in revisions goes to `Pending` with a count and the date. When it has appeared three times across at least two documents, propose it as an entry. Show the evidence and one before-and-after example on a passage the researcher did not touch, so the rule does not become a caricature. Save it only when the researcher agrees.
- One edit is not a style. Many edits answer a word limit, a co-author or a reviewer.
- File a new entry under the narrowest scope its evidence supports (a habit seen only in legends goes under legends). Propose moving it to `General` once it shows up in several kinds of document.
- When the researcher rejects a version, record what and why under `Not me`.

## Keeping it short

- The newest entry wins; delete the one it replaces. Merge duplicates.
- Drop a `Pending` item not seen again within 90 days.
- Each time the file changes, tell the researcher what was added, changed or removed.

## Template

```markdown
# Personal style

Read by biomed-craft before writing. One entry per line: the rule, then
(said by the researcher, YYYY-MM-DD) or (seen N times, last YYYY-MM-DD).
`Allow [RULE-ID]` lets a rule the skill flags stand where this section applies.

## General

## Document: manuscript
## Document: abstract
## Document: legends and table notes
## Document: plan
## Document: log
## Document: code
## Document: response
## Document: slides

## Study type: systematic-review

## Journal: lancet

## Figures and tables

## Not me

## Pending
```

Use the skill's own names for study types (`references/study-types.md`) and journals (`lancet`, `nejm`, `jama`, `bmj`, `nature`, `science`, `cell`). Delete sections that stay empty.
