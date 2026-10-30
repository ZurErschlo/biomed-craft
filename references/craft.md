# Sentences and paragraphs

How research articles in leading journals build sentences and paragraphs. Rates come from the calibration corpus ([calibration.md](calibration.md)). What to remove is in [register.md](register.md) and [patterns.md](patterns.md); number and abbreviation formats are in [format.md](format.md).

## Paragraphs

- One topic per paragraph, stated in a first sentence a reader could quote on its own. Results paragraphs open with the result and its number; Discussion paragraphs open with a claim.
- Introduction paragraphs run about 60–180 words and discussion paragraphs about 80–250.
- A Results paragraph ends on a fact, a Discussion paragraph on the consequence of its claim; neither ends on a line that restates the paragraph (STR-07).
- Familiar information first, news at the end of the sentence; subject and verb close together.

## Subjects and verbs

- People, groups, data, studies or the trial are the subjects: `Households affected by drug-resistant tuberculosis spent…`, `Most studies measured only hospital costs`. Not abstract nouns (`The concentration in direct medical cost shows…`) and not false agency (`the data tell us`, `the analysis reveals`).
- Figures and studies show, report or include; judgements such as exclude, establish or determine belong to the authors.
- Plain reporting verbs: found, estimated, measured, compared, pooled, enrolled, assigned, were associated with, did not differ, accounted for.
- Write `is`, `are` and `has`; `serves as`, `stands as` and `represents` usually stand in for them (LEX-03).
- The Lancet prefers `We did a…` and `was done` (3·6 per 10 000 words) to `performed` (1·2); other journals use performed and conducted freely.

## Tense, voice and length

- Past tense for what was done and found; present tense for established knowledge, model structure, what a figure shows and interpretation.
- About 36% of sentences in leading-journal research contain a passive (NEJM 46%, BMJ 21%). `We` appears about 8 times per 1000 words (Lancet about 10; JAMA about 5; NEJM about 3, where the trial is usually the subject).
- Median sentence length is 23 words (19 to 27 across papers); about 16% of sentences exceed 35 words and 6% have fewer than 10. Long sentences are normal when they carry compound statistics. A run of short sentences reads as telegraphic and is the usual sign of an over-corrected draft (`share_under_10` in `scan.py --profile`).
- One proposition per sentence where possible; split chains joined with `, and this…`.

## Claims and hedging by design

| Design | Results | Interpretation |
|---|---|---|
| Randomised trial | reduced, increased, resulted in, was non-inferior to | might explain, is likely to reflect |
| Observational study | was associated with, was higher among | might reflect, could be explained by |
| Modelling study | we estimated, would avert, was projected to | depends on, is sensitive to |
| Systematic review and meta-analysis | pooled estimate with interval; GRADE certainty (`moderate-certainty evidence shows`) | consistent with, explained by |
| Diagnostic accuracy | sensitivity was, specificity was | if used as…, would |
| Laboratory study | show (direct observation) | suggest, indicate (mechanism) |

- Hedges go on interpretations; measured results stay unhedged (`Mortality was 12·4%`, not `appeared to be`). One hedge per claim (DEF-02).
- Hedges run at a median of 3·7 per 1000 words, highest in observational studies and systematic reviews and lowest in trials.
- The Lancet uses `might` (13 per 10 000 words) and almost never `may`; NEJM, JAMA and BMJ use `may`.

## Numbers, comparisons and connectives

- Estimate, then interval, then pointer: `Mortality was 12·4% (95% CI 10·1–14·9; figure 2).` Give denominators: `49 (2%) of 2609` (Lancet), `482 of 2104 patients (22.9%)` (NEJM).
- Give the number whenever you describe a size or change (LEX-07). `significant` only with its test or interval in the same sentence (LEX-08). People are counted in whole numbers (FMT-02).
- Compare two named, measured things and give both numbers: `Treatment success was 86% with the new regimen and 79% with the standard regimen.` The usual connectives are `by contrast`, `whereas` and `compared with`.
- Common connectives: `however` (0·6 per 1000 words), `although`, `in addition`, `therefore`. A connective that carries logic cannot simply be deleted; repair the link, for example by opening the next sentence with the term the two share.

## Terms and citations

- One term per concept; no rotating synonyms (patients, participants, subjects). Abbreviate only terms used at least three times; spell terms out in titles. Notation is identical in text, tables and figures.
- Labels used inside an analysis (actual, should, gap, scenario codes) get public names before they reach the manuscript.
- Name earlier work by design and size or trial name (`two trials`, `CRASH-2`); `X et al` is rare in Lancet and NEJM text. Each claim cites the study that supports it.
- Pointers to your own figures and tables go in parentheses at the end of the clause (`(figure 2; table 3)`); opening with `Table 2 shows` is uncommon (META-06).
- Reviews synthesise by theme with counts and pooled estimates, not study by study.
- When compressing, keep the actor, comparator, condition, denominator and time frame; drop low-priority sentences before compressing essential ones.
