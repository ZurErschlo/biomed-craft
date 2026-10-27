# Calibration corpus

The rule levels and the reference ranges in `scan.py` come from research articles published in leading journals and their major sub-journals. `scripts/calibration.json` holds the statistics and `scripts/corpus.json` lists the articles by DOI (and PMCID where they came from Europe PMC), with the journal, year, article type and study design. The repository stores no article text.

## Corpus

- Leading journals: The Lancet, NEJM, JAMA, BMJ, Annals of Internal Medicine, Nature, Science, Cell.
- Major sub-journals: the Lancet specialty journals, Nature Medicine and the other Nature research journals, the Nature Reviews journals (reviews only), the JAMA specialty journals, Science Translational Medicine.
- Excluded for this purpose: Nature Communications, PLOS Medicine, JAMA Network Open, JAMA Health Forum, BMJ Global Health, BMJ Open, eClinicalMedicine, Lancet Regional Health, Scientific Reports and similar journals. Guidance on public-database studies also draws on journals with an impact factor of 10 or more; those articles inform the study-type files but not the statistics.
- Three sources: PDFs on the author's computer; publisher PDFs chosen to fill gaps, whose text is kept on the author's computer in `calibration-texts/` (ignored by git); and open-access publisher versions read as full-text XML from Europe PMC, chosen to spread journals, study designs and topics. Author manuscripts and supplements are excluded because journals do not copyedit them.
- Study designs: trials, observational and database studies, economic evaluations, systematic reviews, diagnostic accuracy, modelling, laboratory and computational studies, and narrative reviews, each with its own reference group once it has enough articles.
- Topic balance: the author's own library leans towards infectious disease, antimicrobial resistance and modelling. The open-access articles from JAMA journals, the BMJ, Cell and the economic and database studies cover many other fields. The open-access publisher versions of NEJM, Science and Science Translational Medicine are mostly from the COVID-19 period, so publisher PDFs of articles from 2016 to 2024 on other topics were added for these journals and for JAMA: trials, cohorts, diagnostic, economic, laboratory and computational studies, and reviews.

## Method

1. PDFs: take the DOI from the file name when it has one, otherwise the first DOI on pages 1–2, and match it to the journal list in `calibrate.py`. Saved texts: read the DOI and labels from the front matter. Europe PMC: fetch the JATS XML by PMCID and keep only publisher versions.
2. Drop supplements, disclosure and data-sharing forms, author manuscripts and duplicates.
3. Keep the abstract and body prose; remove reference lists, back matter, running heads, captions, tables, boxes and citation markers; keep complete sentences only (five or more words, starting with a capital and ending with a full stop, question mark or exclamation mark).
4. Label the study design: by hand for Europe PMC articles and saved texts, and with `textstats.detect_design` for other PDFs. An unlabelled item is a research article if it has a Methods heading and a Results or Discussion heading. The automatic guess is a starting point: on the hand-labelled publisher PDFs it was wrong for about one article in four, mostly reviews and translational laboratory papers, so state the type with `--type` when it is known.
5. For each article, compute the style profile (`textstats.profile`) and count every rule that applies to prose.
6. Report per-article quantiles for the profile and pooled rates per 10 000 words for the rules: for all research articles, each journal family, each study design, and articles published before 2023 and from 2023 onwards.

## Style profile of research articles in leading journals

10th, 50th and 90th percentiles across articles.

| Metric | 10th | Median | 90th |
|---|---|---|---|
| Median sentence length (words) | 20 | 24 | 28 |
| Sentences over 35 words | 10% | 18% | 30% |
| Sentences under 10 words | 2% | 5% | 10% |
| `we`, `our`, `us` per 1000 words | 2·1 | 8·1 | 16 |
| Sentences with a passive | 23% | 38% | 52% |
| Hedges per 1000 words | 1·5 | 3·7 | 6·9 |
| Contrast frames per 1000 words | 0 | 0·30 | 0·90 |
| `Moreover`-type openers per 1000 words | 0 | 0·54 | 1·63 |
| `However,` openers per 1000 words | 0 | 0·59 | 1·45 |
| Em dashes per 1000 words | 0 | 0·16 | 1·44 |
| Semicolons outside brackets per 1000 words | 0·3 | 1·7 | 5·5 |

Differences worth knowing: NEJM uses `we` about three times per 1000 words and JAMA about five, against eight or nine in the BMJ and ten to twelve in the Lancet, Cell and modelling and computational studies; reviews use `we` least and hedge most; modelling studies run the longest sentences; laboratory papers and Cell use the fewest semicolons. Semicolons inside brackets are left out because JAMA and NEJM use them to separate statistics.

## How rule levels were set

- Must fix: style rules whose forms appear in at most about 3% of research articles published before 2023 (for single words, each word separately), or text that is internal material by definition (file names, placeholders, seeds). Tests in `tests/test_scan.py` fail if a must-level style rule appears in more than 10% of pre-2023 articles or more than 0·6 times per 10 000 words, or in more than 15% of the articles of any journal family or study design with enough articles.
- Per-design and per-journal levels: when a form is common in one design or journal (`intriguing` in reviews, laboratory papers and Cell; parameter names in computational methods) and rare elsewhere, the rule carries a lower level for that design or journal instead of a lower level everywhere.
- Review: forms that careful authors use occasionally but that have risen since 2023 or that often stand in for content, such as sentence-initial `Notably,`, `-ing` significance tails and stacked hedges.
- Density: forms common in leading-journal text (`rather than`, `instead of`, `potential`, `key`, `enhance`), reported only as rates compared with the reference group.

## Rebuilding the calibration

```bash
python3 scripts/calibrate.py ~/Zotero ~/Papers --texts calibration-texts --pmc scripts/corpus.json
python3 scripts/calibrate.py --pmc new_articles.txt ~/Zotero          # add articles: one "PMCID design" per line
```

PDFs need `pdftotext` (poppler); Europe PMC articles need network access. A saved text is the `pdftotext` output of a publisher PDF under a short front matter (DOI, title, year, type, design; see the top of `calibrate.py`). Saved texts stay in `calibration-texts/`, which git ignores, because they are under the publishers' copyright; `validate_package.py` fails if one is committed. The script writes only statistics and identifiers to the repository. After a rebuild, run the tests: the guards fail if the new corpus shows that a must-level rule is common in some journal or design, which means its level should change.
