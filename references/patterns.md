# AI-style patterns

Sentence shapes, words and formatting that mark text as machine-written, with how often research articles in leading journals use them ([calibration.md](calibration.md)); "papers" means the share of articles using the form at least once. A pattern counts as a tell in proportion to how rarely a careful author would choose it: one `rather than` is ordinary, ten in a discussion are not. Judge clusters and density, and check every rewrite for new tells.

## Contrast frames

The family the author calls `不是…而是`: setting up a position nobody stated in order to knock it down.

- `The central gap is not cost. It is coverage.` (CON-01, must fix); `not only X but also Y` (CON-02; 24% of papers); `The barrier is not cost but access.` (CON-03); clause-final `…because of staffing, not drug prices.` (CON-04).
- `This is not about incidence; it is about value.` (CON-07); `Not a cure. Not a vaccine.` (CON-08); `less about X, more about Y` (CON-09); `not X; instead Y` and sentence-initial `Rather,` (CON-10).
- `rather than` (CON-05; 40% of papers before 2023) and `instead of` (CON-06) are normal in moderation. All contrast frames together run at about 0·3 per 1000 words (90th percentile 0·9); `scan.py` flags density above that.

Fix: write the positive statement. Keep a contrast only between two named, measured things with both numbers, or for a method choice (`We used a Poisson model rather than a negative binomial model because…`).

## Words leading journals rarely print

- Must fix (LEX-01, LEX-02), at most about 3% of papers for each word: `delve`, `tapestry`, `testament`, `realm`, `garner`, `cutting-edge`, `groundbreaking`, `showcase`, `unveil`, `underexplored`, `commendable`, `revolutionise`, `spearhead`, `vibrant`, `endeavour`, `bedrock`, `linchpin`; `a growing body of`, `has attracted increasing attention`, `evolving landscape`, `in the realm of`, `bridge the gap`, `open new avenues`, `valuable insights`, `a testament to`, `navigate the complexities`, `in today's world`, `in an era of`. In narrative reviews LEX-02 is flagged for judgement.
- Must fix in clinical, epidemiological and economic research, judged in context in reviews, laboratory and computational papers (LEX-11): `intriguing`, `myriad`, `plethora`, `unravel`, `intricate`, `invaluable`, `meticulous`, `transformative`.
- Review (LEX-03), uncommon before 2023 and rising: `multifaceted`, `interplay`, `plays a key role`, `taken together`, `remarkable`, `underscore`, `leverage`, `holistic`, `empower`, `novel`, `nuanced`, `landscape`, `insights`, `foster`, `pivotal`, `unprecedented`, `in recent years`, `paramount`, `harness`, `streamline`, `embark`, `bolster`, `noteworthy`, `cornerstone`, `seamless`, `pave the way`, `shed light on`. Keep only when the word carries meaning (`pivotal trial`, `foster care`).
- Density only (LEX-10): `potential`, `key`, `enhance`, `facilitate`, `highlight`, `various`, `diverse`, `particularly`, `additionally`, `furthermore`, `moreover`.
- Sentence-initial `Notably,`, `Importantly,`, `Interestingly,`, `Of note,` (LEX-04): 33% of papers before 2023, 51% from 2023; never two in one paragraph (STR-04).
- Praise adjectives `robust`, `comprehensive`, `crucial`, `critical`, `valuable` (LEX-05): name the property instead; `robust standard errors` and `critically ill` stay.
- Formal substitutes (LEX-06): `utilise`, `elucidate`, `underpin`, `delineate`, `commence`, `thereby`, `markedly`, `impose`, `fundamentally`. Second-opinion models suggest these; keep `use`, `explain`, `support`, `start`.
- Size words without a number (LEX-07); `significant` without a test (LEX-08; the Lancet rarely uses it at all).
- Priority claims (LEX-09): `To our knowledge, this is the first…` appears in 18% of research articles, about 40% in the Lancet journals and a third in the JAMA journals; NEJM does not print it. Keep one, only if a documented search supports it.

Never replace a flagged word with a fancier one: `underscores` becomes `shows` or a number.

## Sentence shapes

- `-ing` tails announcing significance: `…, highlighting the need for scale-up` (STR-03; 7% of papers before 2023, 18% from 2023). End on the fact; move the implication to the Discussion.
- Verdict sentences with no content: `These findings underscore the importance of early diagnosis.` (STR-07).
- Rhetorical questions (STR-05); colon reveals (`The answer: coverage.`) (STR-06); summary openers (`Overall,`, `Taken together,`) outside the final paragraph (STR-08).
- Triads for rhythm where the content has two or four items; every paragraph on one template; synonym cycling; `In other words` restatements; `Studies have shown…` without a citation.

## Punctuation and format

- Dashes that explain or rename what came before: `The main barrier—cost—was not addressed.` Leading-journal research prints about 0·5 dashes per 1000 words: a pair around an aside in a third of papers, a closing dash and explanation in one in ten, and almost never in JAMA. Use a colon, parentheses, commas or a new sentence. Em dashes are flagged for judgement (STR-01); spaced en dashes used as dashes are must-fix outside laboratory methods (STR-02); a dash before a one- or two-word reveal (`…one thing — cost.`) is must-fix (STR-11). En dashes in ranges stay.
- Markdown left in Word or slides (STR-09); emoji (STR-10); bullet lists, decorative bold and Title Case headings in manuscript prose.
- Contractions (FMT-04), `data is` (FMT-03), sentences starting with a numeral (FMT-05), `p=0.000` (FMT-01), fractional people (FMT-02).
- Legends and text inside figures: [figures-tables.md](figures-tables.md) (META-05, CAP-01, FIG-01 to FIG-05).

## Over-correction

Removing tells can create a new signature. Avoid strings of 8–15-word sentences (the median is 23 words), deleting real uncertainty, negation, null results or a contrast that is the finding, telegraphic compression that drops the actor or comparator, swapping one flagged word for another formal word, and forced variety (rotating synonyms, varying sentence length by rule, banning the passive).
