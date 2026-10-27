# Sentences and paragraphs

How research articles in leading journals build sentences and paragraphs. Rates come from the calibration corpus ([calibration.md](calibration.md)); structural observations come from close reading of articles across study designs.

## Paragraphs

- One topic per paragraph. The first sentence states it, and a reader could quote that sentence on its own.
- Results paragraphs open with the result and its number. Discussion paragraphs open with a claim.
- Introduction paragraphs run about 60–180 words and discussion paragraphs about 80–250.
- A Results paragraph ends on a fact. A Discussion paragraph ends on the consequence of its claim. Neither ends on a line that restates the paragraph (STR-07).
- After adding a sentence, look for the sentence it made redundant and delete that one. Drafts grow by accretion; edits should shrink them.

## Information order

- Put familiar information first and new information last. The subject links back to the previous sentence; the end of the sentence carries the news.
- Keep subject and verb close together. Move long qualifiers after the verb.

## Subjects

- Make people, groups, data, studies or the trial the subject: `Households affected by drug-resistant tuberculosis spent…`, `The trial enrolled…`, `Most studies measured only hospital costs`.
- Avoid abstract nouns as subjects: `The concentration in direct medical cost shows…` becomes `Most studies measured only direct medical costs`.
- Avoid false agency: `the data tell us`, `the analysis reveals`, `the decision emerges`. Write `We found…` or state the finding.
- Figures and studies can show, report or include. Judgements such as exclude, establish or determine belong to the authors.

## Verbs

- Plain reporting verbs do most of the work: found, estimated, measured, compared, pooled, enrolled, assigned, were associated with, did not differ, increased, decreased, accounted for.
- The Lancet prefers `We did a…` and `was done` (3·6 per 10 000 words) to `performed` (1·2). Other journals use performed and conducted freely.
- Write `is`, `are` and `has`. `Serves as`, `stands as` and `represents` usually stand in for them (LEX-03).
- Formal substitutes such as `utilise`, `elucidate`, `underpin`, `delineate`, `commence`, `thereby`, `markedly`, `impose` and `fundamentally` make prose sound edited by a machine. Second-opinion models often propose them; keep the plain word (LEX-06).

## Tense and voice

- Past tense for what was done and found. Present tense for established knowledge, model structure, what a figure shows, and interpretation.
- Passives are normal, especially in Methods: about 36% of sentences in research articles in leading journals contain one (NEJM 46%, BMJ 21%).
- `We` appears about 8 times per 1000 words (Lancet about 10; NEJM about 2·5, where the trial is usually the subject).

## Sentence length

- Median sentence length is 23 words (papers range from 19 to 27 at the 10th and 90th percentiles). About 16% of sentences exceed 35 words and 6% have fewer than 10.
- Long sentences are normal when they carry compound statistics. A run of short sentences reads as telegraphic; it is also the usual sign of an over-corrected draft (check `share_under_10` with `scan.py --profile`).
- One proposition per sentence where possible. Split clause chains joined with `, and this…`.

## Claims and hedging by design

| Design | Results | Interpretation |
|---|---|---|
| Randomised trial | reduced, increased, resulted in, was non-inferior to | might explain, is likely to reflect |
| Observational study | was associated with, was higher among | might reflect, could be explained by |
| Modelling study | we estimated, would avert, was projected to | depends on, is sensitive to |
| Systematic review and meta-analysis | pooled estimate with interval; GRADE certainty (`moderate-certainty evidence shows`) | consistent with, explained by |
| Diagnostic accuracy | sensitivity was, specificity was | if used as…, would |
| Laboratory study | show (direct observation) | suggest, indicate (mechanism) |

- Put hedges on interpretations and leave measured results unhedged: `Mortality was 12·4%` (`Mortality appeared to be 12·4%` hedges a measurement).
- One hedge per claim (DEF-02). Hedges run at a median of 3·2 per 1000 words in leading-journal research, highest in cohort studies and economic evaluations and lowest in trials.
- Keep hedges that carry real uncertainty: association wording for observational data, scope conditions, the interval, `probably` on an explanation. Deleting them changes the claim.
- The Lancet uses `might` (13 per 10 000 words) and almost never `may`. NEJM, JAMA and BMJ use `may`.

## Numbers in sentences

- Lead with the estimate, then the interval, then the pointer: `Mortality was 12·4% (95% CI 10·1–14·9; figure 2).`
- Give denominators: `49 (2%) of 2609` (Lancet) or `482 of 2104 patients (22.9%)` (NEJM).
- Give the number whenever you describe a size or change (LEX-07).
- Reserve `significant` for statistical significance with the test or interval in the same sentence (LEX-08).
- People are counted in whole numbers. Write `an average of 1·5 participants per site` (FMT-02).

## Comparisons and contrasts

- Compare two named, measured things and give both numbers: `Treatment success was 86% with the new regimen and 79% with the standard regimen.`
- The usual connectives are `by contrast`, `whereas` and `compared with`.
- Contrast frames (`rather than`, `not … but`, `not only`, a clause-final `, not X`, `instead of`) occur about 0·3 times per 1000 words in leading-journal research (90th percentile 0·8). They mark technical distinctions, such as a method choice or a definition. They never open an argument (CON rules).

## Connectives

- The common connectives are `however` (0·6 per 1000 words), `although`, `in addition` and `therefore`.
- Sentence-initial `Notably`, `Importantly` and `Interestingly` were used by 30% of papers before 2023 and by 57% after (LEX-04). Use them rarely and never twice in one paragraph (STR-04).
- A connective that carries logic cannot simply be deleted. Repair the link instead, for example by starting the next sentence with the term the two sentences share.

## Terms and abbreviations

- One term per concept throughout. Do not rotate synonyms (patients, participants, subjects) for variety.
- Define an abbreviation at first use in the abstract and again in the main text, and again in each figure legend and table note ([figures-tables.md](figures-tables.md)).
- Abbreviate only terms used at least three times. Spell terms out in titles.
- Define symbols before first use and keep notation identical in text, tables and figures.
- Labels used inside an analysis (actual, should, gap, scenario codes) get public names before they reach the manuscript.

## Citing earlier work

- Name earlier work by design and size or by trial name: `two trials`, `CRASH-2`. `X et al` is rare in Lancet and NEJM text.
- Each claim cites the study that supports it. Five references for one point need a reason for each.
- Pointers to your own figures and tables go in parentheses at the end of the clause: `(figure 2; table 3)`. Opening with `Table 2 shows` is uncommon (META-06).
- In reviews and meta-analyses, synthesise by theme with counts and pooled estimates. Do not walk through studies one by one.

## Concision without loss

- Cut words that add nothing: `in order to` becomes `to`; delete `it was found that`.
- Clarity comes before compression. Keep the actor, comparator, condition, denominator and time frame.
- When a text must shrink, drop low-priority sentences before compressing essential ones.
