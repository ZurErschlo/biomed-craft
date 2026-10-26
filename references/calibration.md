# Calibration corpus

The rule levels and the reference ranges in `scan.py` come from research articles published in flagship journals and their major sub-journals. `scripts/calibration.json` holds the statistics and `scripts/corpus.json` lists the articles by DOI. No article text is stored.

## Corpus

- Flagship journals: The Lancet, NEJM, JAMA, BMJ, Annals of Internal Medicine, Nature, Science, Cell.
- Major sub-journals: the Lancet specialty journals (Infectious Diseases, Global Health, Public Health, HIV, Respiratory Medicine, Microbe, Digital Health, Psychiatry, Neurology and others), Nature Medicine, Nature Microbiology, Nature Human Behaviour and the other Nature research journals, the Nature Reviews journals (reviews only), the JAMA specialty journals, Science Translational Medicine.
- Excluded as lower tier for this purpose: Nature Communications, PLOS Medicine, Clinical Infectious Diseases, JAMA Network Open, BMJ Global Health, eClinicalMedicine, Lancet Regional Health, Scientific Reports, BMJ Open and similar.

The first build (October 2026) found 159 unique articles in about 6000 PDFs on the author's computer: 124 research articles (707 782 words of prose) and 33 reviews, comments and other items. Supplements and author manuscripts (31 files) were excluded because journals do not copyedit them.

| Group | Research articles |
|---|---|
| Lancet family | 56 (Lancet Infect Dis 16, Lancet Glob Health 13, Lancet 9, Lancet HIV 5, Lancet Public Health 5, others 8) |
| Nature family | 34 (Nat Med 16, Nature 12, Nat Microbiol 3, other research journals 3) |
| Cell | 10 |
| NEJM | 8 |
| BMJ | 7 |
| JAMA family | 5 |
| Science | 3 |
| Annals | 1 |
| Published before 2023 / 2023 onwards / year unknown | 53 / 63 / 8 |

The corpus leans towards infectious disease, antimicrobial resistance, tuberculosis and modelling, which raises the share of uncertainty intervals and headline-estimate openings. Small groups (NEJM, BMJ, JAMA, Science) give rough ranges only.

## Method

1. Find PDFs; read the first DOI on pages 1–2 (or recover it from the file name) and match it to the journal list in `calibrate.py`.
2. Drop supplements, author manuscripts and duplicates (the largest file per DOI is kept).
3. Extract text with `pdftotext`; remove reference lists, back matter (contributors, funding, interests, data sharing and similar), running heads, captions, panels and superscript citation numbers; keep complete sentences only (five or more words, starting with a capital and ending with a full stop, question mark or exclamation mark).
4. Classify an item as a research article if it has a Methods heading and a Results or Discussion heading; Nature Reviews and similar items are reviews.
5. For each article, compute the style profile (`textstats.profile`) and count every rule that applies to prose.
6. Report per-article quantiles for the profile and pooled rates per 10 000 words for the rules, for the whole corpus, each journal family, and articles published before 2023 and from 2023 onwards.

## Style profile of flagship research articles

10th, 50th and 90th percentiles across articles.

| Metric | 10th | Median | 90th |
|---|---|---|---|
| Median sentence length (words) | 19 | 23 | 27 |
| Sentences over 35 words | 9% | 16% | 27% |
| Sentences under 10 words | 2% | 6% | 12% |
| `we`, `our`, `us` per 1000 words | 2·4 | 8·1 | 16·2 |
| Sentences with a passive | 22% | 36% | 54% |
| Hedges per 1000 words | 1·1 | 3·2 | 6·2 |
| Contrast frames per 1000 words | 0 | 0·33 | 0·80 |
| `Moreover`-type openers per 1000 words | 0 | 0·58 | 1·70 |
| `However,` openers per 1000 words | 0 | 0·57 | 1·31 |
| Em dashes per 1000 words | 0 | 0·28 | 1·41 |
| Semicolons per 1000 words | 1·6 | 4·0 | 10·3 |

Family differences worth knowing: NEJM uses `we` about 2·5 times per 1000 words and almost no contrast frames or signpost openers; BMJ sentences are shorter (median 19 words) with more semicolons; Lancet sentences are the longest (median 25 words).

## How rule levels were set

- Must fix: style rules whose forms appear in at most about 3% of research articles published before 2023 (for single words, each word separately), or text that is internal material by definition (file names, placeholders, seeds). A test (`tests/test_scan.py`) fails if a must-level style rule appears in more than 10% of pre-2023 articles or more than 0·6 times per 10 000 words.
- Review: forms that careful authors use occasionally but that have risen since 2023 or that often stand in for content. Examples: sentence-initial `Notably,` (30% of articles before 2023, 57% from 2023), `-ing` significance tails (9% to 24%), stacked hedges such as `could potentially` (6% to 17%), `pipeline` (4% to 27%).
- Density: forms common in flagship text (`rather than`, `instead of`, `potential`, `key`, `enhance`), reported only as rates compared with the corpus.

Rates before and after 2023 differ partly because the families differ in each period (the earlier set is mostly Lancet, the later set has more Nature), so the period comparison is indicative.

## Rebuilding the calibration

Anyone can recalibrate against their own field's flagship literature:

```bash
python3 scripts/calibrate.py ~/Zotero ~/Papers --out-dir scripts
```

`calibrate.py` needs `pdftotext` (poppler). It writes only statistics and DOI metadata. After a rebuild, run the tests: the guard on must-level rules will fail if a new corpus shows that one of them is common in flagship prose, which means the rule's level should change.
