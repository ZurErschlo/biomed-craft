# Peer review and responses

Three jobs: reviewing a manuscript before submission (the researcher's own, or a colleague's on request), reviewing someone else's manuscript for a journal, and answering the reviewers after a decision.

## Reviewing before submission

- Work from one fixed version of the manuscript and its supplement.
- Match the strictness to the stage: in an early draft, look at the structure and the design; close to submission, report only definite errors.
- When several reviews of the researcher's own manuscript are wanted, run them separately (other models or isolated sessions), each with a different emphasis: methods and statistics, the clinical or biological claim, presentation. Freeze each report before comparing them. Someone else's unpublished manuscript never goes to an outside model.
- Review methods in a fixed order: estimand; design and unit of analysis; allocation and masking; sample size; missing data and attrition; fit between analysis and design; multiplicity and prespecification; estimates and denominators; generalizability. Then check the content list of the study type ([study-types.md](study-types.md)).
- Quote the passage each concern is about and give its location. Before calling something missing, search the full text, the supplement and the registered protocol; before raising a concern, check whether the paper already answers it.
- Write each concern with an identifier, the claim it challenges, where the evidence is, why it matters and what would resolve it. Call a concern blocking only when the central claim cannot stand without it; there is no quota of concerns.
- Separately, audit the numbers: recompute percentages, check intervals and totals, compare text with tables and figures (`scripts/check_numbers.py`), and reproduce the headline numbers from the analysis output before suggesting new analyses.
- Leave out criticisms that would not survive an editor, or turn them into suggestions that leave the conclusions alone:
  - a new study unrelated to the stated conclusions (an analysis the conclusions need stays in);
  - analyses the design cannot support;
  - citations of the reviewer's own work without a scholarly reason;
  - a reversal of the conclusions without new evidence;
  - a limitation the paper already states in proportion to its conclusions (one that undermines the main conclusion stays in);
  - a different method only because the reviewer prefers it, when the method used suits the design;
  - `not novel` without a reference to the earlier work;
  - remarks on the authors or on their English;
  - judging the data by the quality of the writing.

  Mark as optional any addition that would only make the paper more impressive.
- Once the concerns are checked, sort them into three groups:
  - fixable by wording alone: write one sentence on what the revised text must achieve, with no new data, numbers or citations;
  - needs the researcher: a new analysis, new data, a new citation or the authors' intent;
  - does not hold: give the reason and list it under "done wrong or found wrong" in the closing report, so that no concern disappears without a word.
- Verify every concern raised by another model against the manuscript before passing it on, and say which ones did not hold and why.

## Reviewing for a journal

- Before handling someone else's unpublished manuscript, ask the researcher whether the journal's policy allows AI tools in peer review, or whether the journal has given permission. If neither, do not process the manuscript.
- When it is allowed, keep the manuscript local: do not upload it where confidentiality cannot be guaranteed and do not send it to other models. Remind the researcher to tell the journal that AI was used.
- Write the comments to the authors and the confidential comments to the editor separately. Conflicts of interest, integrity concerns and the recommendation go only to the editor.
- The method of the section above applies: quotations and locations, the list of criticisms to leave out, and the three groups.

## Answering reviewers

- Ask the researcher what the decision was (major or minor revision, reject and resubmit); do not infer it from the tone of the letter.
- Number every comment (`E1` for the editor, `R1.1` for the first comment of the first report) and give each a category, a severity, a proposed action and what the researcher needs to supply.
- Split a compound comment into its separate requests and answer each one. A request is required only when the editor says so; neither its severity nor the number of reviewers who raise it makes it required.
- Keep one internal table of all comments and their status; write one response per reviewer.
- For each comment: thank the reviewer once at the top of the letter, not in every reply; quote or summarize the comment; say what was done and where (page, line, figure, table); give the new text when it is short.
- When a reviewer missed something that is in the paper, treat it as a presentation problem: point to it and make it easier to find.
- When a request cannot be met (an impossible experiment, data that do not exist), say so plainly, give the reason, and add the limitation to the paper.
- When reviewers disagree, follow the evidence and explain the choice to both.
- Statistical requests are answered with the test, the unit, n, the correction, the effect size and its interval.
- Mark each change done, partly done or not done, judged from the revised files and not from the letter. New text quoted in the letter appears word for word at the place it names in the revision (`scripts/check_response.py response.docx revised.docx`).
- Before revising, agree with the researcher on up to seven key sentences: the main finding, the main numbers, the main limitation and the conclusion. After each round of changes, mark each one still supported, weakened, contradicted or left without support.
- After every edit, rerun the number and consistency checks (`scripts/check_preservation.py`, `scripts/check_numbers.py`). A revision does not make a claim stronger than the evidence allows: check the abstract and conclusions against the first version, and look at every sentence that `check_preservation.py` reports as moving from association to effect.
- Every addition prompts a search for something to delete, so the paper does not grow past the word limit.
