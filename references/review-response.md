# Peer review and responses

Two jobs: reviewing a manuscript before submission (the researcher's own, or a colleague's on request), and answering the reviewers after a decision.

## Reviewing before submission

- Work from one fixed version of the manuscript and its supplement.
- When several reviews are wanted, run them separately (other models or isolated sessions), each with a different emphasis: methods and statistics, the clinical or biological claim, presentation. Freeze each report before comparing them.
- Review methods in a fixed order: estimand; design and unit of analysis; allocation and masking; sample size; missing data and attrition; fit between analysis and design; multiplicity and prespecification; estimates and denominators; generalisability. Then check the content list of the study type ([study-types.md](study-types.md)).
- Write each concern with an identifier, the claim it challenges, where the evidence is, why it matters and what would resolve it. Call a concern blocking only when the central claim cannot stand without it; there is no quota of concerns.
- Separately, audit the numbers: recompute percentages, check intervals and totals, compare text with tables and figures (`scripts/check_numbers.py`), and reproduce the headline numbers from the analysis output before suggesting new analyses.
- Leave out criticisms that would not survive an editor: requests for a different study, for the reviewer's own work to be cited, or for analyses the design cannot support.
- Verify every concern raised by another model against the manuscript before passing it on, and say which ones did not hold and why.

## Answering reviewers

- Ask the researcher what the decision was (major or minor revision, reject and resubmit); do not infer it from the tone of the letter.
- Number every comment (`E1` for the editor, `R1.1` for the first comment of the first report) and give each a category, a severity, a proposed action and what the researcher needs to supply.
- Keep one internal table of all comments and their status; write one response per reviewer.
- For each comment: thank the reviewer once at the top of the letter, not in every reply; quote or summarise the comment; say what was done and where (page, line, figure, table); give the new text when it is short.
- When a reviewer missed something that is in the paper, treat it as a presentation problem: point to it and make it easier to find.
- When a request cannot be met (an impossible experiment, data that do not exist), say so plainly, give the reason, and add the limitation to the paper.
- When reviewers disagree, follow the evidence and explain the choice to both.
- Statistical requests are answered with the test, the unit, n, the correction, the effect size and its interval.
- Mark each change as verified in the revised files or as still to do. Do not report a change as done until it is in the manuscript.
- After every edit, rerun the number and consistency checks (`scripts/check_preservation.py`, `scripts/check_numbers.py`). A revision does not make a claim stronger than the evidence allows; check the abstract and conclusions against the first version.
- Every addition prompts a search for something to delete, so the paper does not grow past the word limit.
