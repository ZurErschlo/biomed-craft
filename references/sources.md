# Sources

The rules in this skill come from four places, in this order of priority: the author's own editing decisions on manuscripts, protocols, figures and slides; the published articles described in [calibration.md](calibration.md); public skills for removing AI-style writing; and journal and reporting guidance. All wording in this skill is original. Where a source has no licence or a non-commercial licence, only its ideas were used, and it is credited here.

## Published articles

- Calibration corpus: research articles from leading journals and their major sub-journals, from the author's library and from open-access publisher versions in Europe PMC, listed by DOI in `scripts/corpus.json`.
- Close reading of research articles, reviews and paired supplements across trials, cohort studies, modelling, economic evaluation, systematic reviews, burden studies, diagnostic accuracy, laboratory and computational studies, on topics well beyond infectious disease.
- Page-by-page inspection of figures and tables, and counts of legend and table-note conventions across the calibration articles.

## Public skills and catalogues

| Source | Licence | Used for |
|---|---|---|
| [blader/humanizer](https://github.com/blader/humanizer) | MIT | Strong and weak tells; checking facts after a rewrite; text that describes the document; repository layout (root `SKILL.md`, plugin manifests, issue templates) |
| [op7418/Humanizer-zh](https://github.com/op7418/Humanizer-zh) | MIT | Priority of meaning over style; `keep` counter-examples; rewrite cases with a manual checklist in `tests/` |
| [hardikpandya/stop-slop](https://github.com/hardikpandya/stop-slop) | MIT | False agency, vague declaratives, references kept outside `SKILL.md` |
| [matsuikentaro1/humanizer_academic](https://github.com/matsuikentaro1/humanizer_academic) | see repository | Medical-paper patterns; clarity before compression; repairing cohesion after deleting connectives; checking numbers after a rewrite |
| [AIScientists-Dev/academic-humanizer](https://github.com/AIScientists-Dev/academic-humanizer) | MIT | Academic inflation words; matching verb strength to evidence |
| [Linshan-Ding/SKILLs-Paper-Polish](https://github.com/Linshan-Ding/SKILLs-Paper-Polish) | none stated (ideas only) | One checkable qualifier per conclusion; no arrows or operators standing in for words |
| [stephenturner/skill-deslop](https://github.com/stephenturner/skill-deslop) | MIT | Scientific register for de-slop rules |
| [Imbad0202/academic-research-skills](https://github.com/Imbad0202/academic-research-skills) | CC BY-NC 4.0 (ideas only) | Protected hedges; tracing figure and table claims |
| [HKUSTDial/Supervisor-Skills](https://github.com/HKUSTDial/Supervisor-Skills) | not stated (ideas only) | Section conventions; no chart titles inside figures |
| [K-Dense-AI/claude-scientific-writer](https://github.com/K-Dense-AI/claude-scientific-writer), [K-Dense-AI/scientific-agent-skills](https://github.com/K-Dense-AI/scientific-agent-skills) | MIT | Table note contents; evidence-bound language |
| [Yuan1z0825/nature-skills](https://github.com/Yuan1z0825/nature-skills) | Apache-2.0 | Main-text discipline; legend skeleton; figure legibility checks |
| [conorbronsdon/avoid-ai-writing](https://github.com/conorbronsdon/avoid-ai-writing), [tbhb/vale-ai-tells](https://github.com/tbhb/vale-ai-tells) | MIT | Deterministic checks; word tiers by density; technical-term exceptions |
| [MrGeDiao/shuorenhua](https://github.com/MrGeDiao/shuorenhua) | MIT | Engineer and debugging register as a category |
| [Leey21/awesome-ai-research-writing](https://github.com/Leey21/awesome-ai-research-writing) | none stated (ideas only) | Caption wording; LaTeX safety |
| [sam-paech/slop-forensics](https://github.com/sam-paech/slop-forensics) | MIT | Over-used words measured against a human baseline |
| [Wikipedia: Signs of AI writing](https://en.wikipedia.org/wiki/Wikipedia:Signs_of_AI_writing) | CC BY-SA 4.0 (summarised, not copied) | Taxonomy of tells and their drift over time |

Rules from these sources that do not suit research articles were left out: banning the passive voice, deleting all adverbs, banning en dashes (they are required in ranges), treating `associated with` as vague, writing to the reader as `you`, sentence-length quotas, adding cushioning hedges, and any aim of passing AI detectors.

## Research on LLM vocabulary in scientific writing

- Kobak D, González-Márquez R, Horvát EÁ, Lause J. Delving into LLM-assisted writing in biomedical publications through excess vocabulary. Sci Adv 2025; 11: eadt3813. https://doi.org/10.1126/sciadv.adt3813
- Liang W, Zhang Y, Wu Z, et al. Quantifying large language model usage in scientific papers. Nat Hum Behav 2025. https://doi.org/10.1038/s41562-025-02273-8
- Juzek TS, Ward ZB. Why does ChatGPT "delve" so much? Exploring the sources of lexical overrepresentation in large language models. COLING 2025. https://arxiv.org/abs/2412.11385
- Geng M, Trotta R. Human-LLM coevolution: evidence from academic writing. 2025. https://arxiv.org/abs/2502.09606
- Matsui K. Delving into PubMed records: some terms in medical writing have drastically changed after the arrival of ChatGPT. Perspect Med Educ 2025. https://doi.org/10.5334/pme.1929

## Writing and reporting guidance

- Gopen GD, Swan JA. The science of scientific writing. Am Sci 1990; 78: 550–58. https://www.americanscientist.org/blog/the-long-view/the-science-of-scientific-writing
- International Committee of Medical Journal Editors. Recommendations for the conduct, reporting, editing, and publication of scholarly work in medical journals. https://www.icmje.org/recommendations/
- EQUATOR Network reporting guidelines. https://www.equator-network.org/
- Hopewell S, Chan AW, Collins GS, et al. CONSORT 2025 statement. BMJ 2025. https://doi.org/10.1136/bmj-2024-081123
- Chan AW, Boutron I, Hopewell S, et al. SPIRIT 2025 statement. BMJ 2025. https://doi.org/10.1136/bmj-2024-081477
- Page MJ, McKenzie JE, Bossuyt PM, et al. The PRISMA 2020 statement. BMJ 2021; 372: n71. https://doi.org/10.1136/bmj.n71
- Husereau D, Drummond M, Augustovski F, et al. CHEERS 2022. BMJ 2022; 376: e067975. https://doi.org/10.1136/bmj-2021-067975
- STROBE statement. https://www.strobe-statement.org/
- Bossuyt PM, Reitsma JB, Bruns DE, et al. STARD 2015. BMJ 2015; 351: h5527. https://doi.org/10.1136/bmj.h5527
- Stevens GA, Alkema L, Black RE, et al. GATHER statement. Lancet 2016; 388: e19–23. https://doi.org/10.1016/S0140-6736(16)30388-9

## Research plans, logs and code

- Wilson G, Bryan J, Cranston K, et al. Good enough practices in scientific computing. PLoS Comput Biol 2017; 13: e1005510. https://doi.org/10.1371/journal.pcbi.1005510
- Sandve GK, Nekrutenko A, Taylor J, Hovig E. Ten simple rules for reproducible computational research. PLoS Comput Biol 2013; 9: e1003285. https://doi.org/10.1371/journal.pcbi.1003285
- Noble WS. A quick guide to organizing computational biology projects. PLoS Comput Biol 2009; 5: e1000424. https://doi.org/10.1371/journal.pcbi.1000424
- Bryan J. Project-oriented workflow. https://www.tidyverse.org/blog/2017/12/workflow-vs-script/
- The tidyverse style guide. https://style.tidyverse.org/
- PEP 8, style guide for Python code. https://peps.python.org/pep-0008/
- TIER Protocol 4.0. https://www.projecttier.org/tier-protocol/protocol-4-0/
- The Turing Way, research compendia. https://book.the-turing-way.org/reproducible-research/compendia
- Broman KW, Woo KH. Data organization in spreadsheets. https://kbroman.org/dataorg/
- Gamble C, Krishan A, Stocken D, et al. Guidelines for the content of statistical analysis plans in clinical trials. JAMA 2017; 318: 2337–43. https://doi.org/10.1001/jama.2017.18556
- ICH E9: statistical principles for clinical trials. https://database.ich.org/sites/default/files/E9_Guideline.pdf
- Moher D, Shamseer L, Clarke M, et al. PRISMA-P 2015. Syst Rev 2015; 4: 1. https://doi.org/10.1186/2046-4053-4-1
- Wang SV, Pottegård A, Crown W, et al. HARPER: a harmonized protocol template for real-world evidence studies. Pharmacoepidemiol Drug Saf 2023. https://doi.org/10.1002/pds.5507
- Thorn JC, Davies CF, Brookes ST, et al. Content of health economics analysis plans (HEAPs) for trial-based economic evaluations. Value Health 2021; 24: 699–710. https://doi.org/10.1016/j.jval.2020.10.002
- Pollett S, Johansson MA, Reich NG, et al. EPIFORGE 2020 guidelines for epidemiological forecasting. PLoS Med 2021; 18: e1003793. https://doi.org/10.1371/journal.pmed.1003793
- Keep a Changelog. https://keepachangelog.com/en/1.1.0/
- Social Science Data Editors. Template README for replication packages. https://social-science-data-editors.github.io/template_README/

The plan, log and code references follow the author's own decisions where these sources disagree with them: no run-all script, no shared function file, no unit-test scripts, the local R installation instead of a lockfile, and the history of a plan kept in the execution log instead of an amendment table.

## Journal instructions

- The Lancet: https://www.thelancet.com/lancet/information-for-authors
- NEJM: https://www.nejm.org/author-center/new-manuscripts
- JAMA: https://jamanetwork.com/journals/jama/pages/instructions-for-authors
- BMJ: https://www.bmj.com/about-bmj/resources-authors
- Nature: https://www.nature.com/nature/for-authors/formatting-guide
- Cell Press STAR Methods: https://www.cell.com/star-authors-guide
