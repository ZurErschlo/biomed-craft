# Sources

The rules in this skill come from four places, in this order of priority: the author's own editing decisions on manuscripts, protocols, figures and slides; the published articles described in [calibration.md](calibration.md); public skills for removing AI-style writing; and journal and reporting guidance. All wording in this skill is original. Where a source has no licence or a non-commercial licence, only its ideas were used, and it is credited here.

## Published articles

- Calibration corpus: 124 research articles from flagship journals and their major sub-journals, listed by DOI in `scripts/corpus.json`.
- Close reading of 45 research articles, 4 reviews and 16 paired supplements across trials, cohort studies, modelling, economic evaluation, systematic reviews, burden studies, diagnostic accuracy and laboratory studies, including open-access articles from PubMed Central on topics outside infectious disease.
- Figure and table inspection of 28 articles page by page, plus legends and table notes from 15 more.

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

## Journal instructions

- The Lancet: https://www.thelancet.com/lancet/information-for-authors
- NEJM: https://www.nejm.org/author-center/new-manuscripts
- JAMA: https://jamanetwork.com/journals/jama/pages/instructions-for-authors
- BMJ: https://www.bmj.com/about-bmj/resources-authors
- Nature: https://www.nature.com/nature/for-authors/formatting-guide
- Cell Press STAR Methods: https://www.cell.com/star-authors-guide
