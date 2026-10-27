# AI-style patterns

Sentence shapes, words and formatting that mark text as machine-written, with how often research articles in leading journals use them ([calibration.md](calibration.md)); "papers" means the share of articles using the form at least once. Rule IDs refer to `scripts/rules.json`.

A pattern counts as a tell in proportion to how rarely a careful author would choose it. One `rather than` is ordinary; ten in a discussion are not. Judge clusters and density, and always check the rewrite for new tells.

## Contrast frames

The family the author calls `不是…而是` in Chinese: setting up a position nobody stated in order to knock it down.

- `The central gap is not cost. It is coverage.`: negate, then assert, across two sentences (CON-01, must fix).
- `not only X but also Y` (CON-02; 24% of papers, 0·06 per 1000 words).
- `The barrier is not cost but access.` (CON-03).
- Clause-final correction: `…because of staffing, not drug prices.` (CON-04).
- `This is not about incidence; it is about value.` (CON-07); `Not a cure. Not a vaccine.` (CON-08); `less about X, more about Y` (CON-09); `not X; instead Y` and sentence-initial `Rather,` (CON-10).
- `rather than` (CON-05; 40% of papers before 2023) and `instead of` (CON-06) are normal in moderation; they count towards density.

All contrast frames together occur about 0·3 times per 1000 words in leading-journal research (90th percentile 0·9). `scan.py` reports the density and flags anything above the 90th percentile.

Fix: write the positive statement. Keep a contrast only when it compares two named, measured things and both numbers are given, or when it marks a method choice (`We used a Poisson model rather than a negative binomial model because…`).

## Words leading journals rarely print

Four tiers, set by how often each word appears in research articles in leading journals before and after 2023, and by study design:

- Must fix (LEX-01, LEX-02): absent or nearly absent from research articles (at most about 3% of papers for each word). `delve`, `tapestry`, `testament`, `realm`, `garner`, `cutting-edge`, `groundbreaking`, `showcase`, `unveil`, `underexplored`, `commendable`, `revolutionise`, `spearhead`, `vibrant`, `endeavour`, `bedrock`, `linchpin`; and the phrases `a growing body of`, `has attracted increasing attention`, `evolving landscape`, `in the realm of`, `bridge the gap`, `open new avenues`, `valuable insights`, `a testament to`, `navigate the complexities`, `in today's world`, `in an era of`. Narrative reviews print the LEX-02 phrases more often, so in a review they are flagged for judgement.
- Must fix in clinical, epidemiological and economic research; judge in context in reviews, laboratory and computational papers (LEX-11): `intriguing`, `myriad`, `plethora`, `unravel`, `intricate`, `invaluable`, `meticulous`, `transformative`. Cell, Science and the review articles of every journal print these; clinical research articles almost never do.
- Review (LEX-03): uncommon before 2023 and rising since: `multifaceted`, `interplay`, `plays a key role`, `taken together`, `remarkable`, `underscore`, `leverage`, `holistic`, `empower`, `novel`, `nuanced`, `landscape`, `insights`, `foster`, `pivotal`, `unprecedented`, `fundamentally`, `in recent years`, `paramount`, `harness`, `streamline`, `embark`, `bolster`, `noteworthy`, `cornerstone`, `seamless`, `pave the way`, `shed light on`. Keep only when the word carries meaning (`pivotal trial`, `foster care`, `seamless phase 2–3 design`).
- Density only (LEX-10): `potential`, `key`, `enhance`, `facilitate`, `highlight`, `various`, `diverse`, `particularly`, `additionally`, `furthermore`, `moreover`. Common in leading-journal text; a problem only when stacked.

Related checks:

- Sentence-initial signposts `Notably,`, `Importantly,`, `Interestingly,`, `Of note,` (LEX-04): 33% of papers before 2023, 51% from 2023.
- Praise adjectives `robust`, `comprehensive`, `crucial`, `critical`, `valuable` (LEX-05): replace with the property that earns the word. `robust standard errors`, `robust to alternative priors`, `critically ill` and `critical care` are technical and stay.
- Formal substitutes (LEX-06): `utilise`, `elucidate`, `underpin`, `delineate`, `commence`, `thereby`, `markedly`, `impose`, `fundamentally`. Second-opinion models tend to suggest these; prefer `use`, `explain`, `support`, `start`.
- Size words without a number (LEX-07): `substantial`, `substantially`, `considerable`, `dramatically`.
- `significant` without a statistical test (LEX-08). The Lancet rarely uses `significant` at all.
- Priority claims (LEX-09): `To our knowledge, this is the first…` appears in 18% of research articles, before and after 2023 alike: about 40% in the Lancet journals (often in Research in context) and a third in the JAMA journals; NEJM does not print it. Keep one, only if a documented search supports it and the journal prints such claims.

Do not replace a flagged word with a fancier one. `Underscores` becomes `shows` or a number, not `accentuates`.

## Sentence shapes

- `-ing` tails that announce significance: `…, highlighting the need for scale-up` (STR-03; 7% of papers before 2023, 18% from 2023). End the sentence on the fact; move the implication to the Discussion and make it specific.
- Verdict sentences with no content: `These findings underscore the importance of early diagnosis.`, `This is a noteworthy finding.` (STR-07). Delete, or state the implication with its scope.
- Two signposts opening sentences in one paragraph (STR-04).
- Rhetorical questions (STR-05) and colon reveals (`The answer: coverage.`) (STR-06).
- Summary openers (`In summary,`, `Overall,`, `Taken together,`) outside the final paragraph (STR-08).
- Triads used for rhythm: three abstract nouns or three parallel clauses where the content has two or four items. Use the number of items the content has.
- Every paragraph built on the same template (claim, three supports, summary line).
- Synonym cycling and `In other words` restatements.
- Vague attribution: `Studies have shown…` with no citation, `experts suggest`.

## Punctuation and format

- Em dashes (STR-01): about 0·5 per 1000 words in leading-journal research (53% of papers use at least one). Use a comma, parentheses or a new sentence for an aside. En dashes in numeric ranges stay (JAMA uses hyphens in ranges).
- Spaced en dashes used as dashes (STR-02).
- Markdown left in Word or slides: `**bold**`, `#` headings (STR-09); emoji (STR-10).
- Bullet lists in manuscript prose, decorative bold, Title Case headings where the journal uses sentence case.
- Contractions (FMT-04), `data is` (FMT-03), sentences starting with a numeral (FMT-05), `p=0.000` (FMT-01), fractional people (FMT-02).

## Legends and figure text

- Legends that describe themselves (META-05) or interpret (CAP-01).
- Figure-level titles, subtitles or captions inside the image (FIG-01); plot titles in code that are longer than a panel title (FIG-02); sentences inside the image (FIG-03); long labels (FIG-04); single-letter category labels (FIG-05).

## Over-correction

Removing tells can create a new signature. Avoid:

- Strings of 8–15-word sentences with commas and full stops everywhere. The median sentence length in leading journals is 23 words; check `share_under_10` with `scan.py --profile`.
- Deleting real uncertainty, real negation, a null result or a contrast that is the finding.
- Deleting connectives that carry logic, leaving disconnected sentences.
- Telegraphic, jargon-dense compression that drops the actor, comparator or time frame.
- Swapping one flagged word for another formal word.
- Forcing variety: rotating synonyms, varying sentence length by rule, or banning the passive voice.
