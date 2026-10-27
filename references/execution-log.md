# Execution logs

The log (`execution_log.md`) records what was done, what came out and what was decided, in date order. It sits beside the research plan ([research-plan.md](research-plan.md)) and never repeats it. Write it in English, in Markdown.

## Layout

- A short status block at the top: aim, done, not done, next. Update it in place.
- Below it, one entry per working session, appended at the end and headed by the date as YYYY-MM-DD. Do not rewrite old entries; close an open item in a later entry.

## Each entry

- What was done, the result with its numbers and the output file, problems met, and decisions with their reasons.
- A design decision takes one line: the date, the decision and the heading of the plan section it changed. The plan carries the content.
- Record a problem before rerunning anything. Keep failed attempts and the results that did not work out.
- For the run that produces the final results, record the R version and the versions of the packages used. The Methods cite the same versions.
- When the method departs from the registration, amend the registration and record the change here.

## Allowed here and not in a paper

Dates, run records, the names of scripts and output files, and plan section headings.

## What stays out

- Records of how an assistant, a session or a conversation worked, such as `subagent`, `main session`, `the assistant decided` or `the user chose` (META-12). Write what was done to the research and why.
- Engineering detail that the code already shows, and defensive wording.
- Dates written any way other than YYYY-MM-DD (LOG-01) and relative dates such as yesterday (LOG-02).
- Internal codes that need a key (PLAN-05).
- Content copied from the plan.

## Example

```text
2026-05-12
- Fitted the Poisson model of monthly notifications (analysis/03_model.R). The deviance ratio was 2.8, so the
  negative binomial rule in the plan applies; output in data/output/model_nb.rds.
- Problem: 41 duplicate notification IDs after linkage; recorded, not yet fixed.
- Decision: deduplicate on ID and date of diagnosis before linkage (plan: Data, linkage).
Next: refit after deduplication.
```
