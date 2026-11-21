# Sources

The rules in this skill come from four places, in this order of priority: the author's own editing decisions on manuscripts, protocols, figures and slides; the published articles described in [calibration.md](calibration.md); public skills for removing AI-style writing and for research work; and journal and reporting guidance. All wording in this skill is original. Where a source has no license or a non-commercial license, only its ideas were used, and it is credited here.

Contents: Published articles; Public skills and catalogs; Research on LLM vocabulary in scientific writing; Writing and reporting guidance; Methods guidance; Research plans, logs and code; Journal instructions.

## Published articles

- Calibration corpus: research articles from leading journals and their major sub-journals, from the author's library and from open-access publisher versions in Europe PMC, listed by DOI in `scripts/corpus.json`.
- Close reading of research articles, reviews and paired supplements across trials, cohort studies, modeling, economic evaluation, systematic reviews, burden studies, diagnostic accuracy, laboratory and computational studies, on topics well beyond infectious disease.
- Page-by-page inspection of figures and tables, and counts of legend and table-note conventions across the calibration articles.

## Public skills and catalogs

| Source | License | Used for |
|---|---|---|
| [blader/humanizer](https://github.com/blader/humanizer) | MIT | Strong and weak tells; checking facts after a rewrite; text that describes the document; repository layout (root `SKILL.md`, plugin manifests, issue templates) |
| [op7418/Humanizer-zh](https://github.com/op7418/Humanizer-zh) | MIT | Priority of meaning over style; `keep` counter-examples; rewrite cases with a manual checklist in `tests/` |
| [hardikpandya/stop-slop](https://github.com/hardikpandya/stop-slop) | MIT | False agency, vague declaratives, references kept outside `SKILL.md` |
| [matsuikentaro1/humanizer_academic](https://github.com/matsuikentaro1/humanizer_academic) | see repository | Medical-paper patterns; clarity before compression; repairing cohesion after deleting connectives; checking numbers after a rewrite |
| [AIScientists-Dev/academic-humanizer](https://github.com/AIScientists-Dev/academic-humanizer) | MIT | Academic inflation words; matching verb strength to evidence |
| [Linshan-Ding/SKILLs-Paper-Polish](https://github.com/Linshan-Ding/SKILLs-Paper-Polish) | none stated (ideas only) | One checkable qualifier per conclusion; no arrows or operators standing in for words |
| [stephenturner/skill-deslop](https://github.com/stephenturner/skill-deslop) | MIT | Scientific register for de-slop rules |
| [Imbad0202/academic-research-skills](https://github.com/Imbad0202/academic-research-skills) | CC BY-NC 4.0 (ideas only) | Protected hedges; tracing figure and table claims; four states for every check; judging the design from the Methods before choosing a guideline; splitting compound review comments; checking Methods and Results both ways; a location for the evidence behind each claim; checking retractions again before submission; counting words as the journal does; reporting the use of AI in systematic reviews |
| [HKUSTDial/Supervisor-Skills](https://github.com/HKUSTDial/Supervisor-Skills) | not stated (ideas only) | Section conventions; no chart titles inside figures |
| [K-Dense-AI/claude-scientific-writer](https://github.com/K-Dense-AI/claude-scientific-writer), [K-Dense-AI/scientific-agent-skills](https://github.com/K-Dense-AI/scientific-agent-skills) | MIT | Table note contents; evidence-bound language; citations and the reference list checked both ways; counting reference-manager fields in Word; confidentiality of peer review; time-to-event prediction models; enrichment background and differential-expression input; Bayesian priors; harms reporting; sample size; agreement studies; software versions; result figures in slides kept as made |
| [Yuan1z0825/nature-skills](https://github.com/Yuan1z0825/nature-skills) | Apache-2.0 | Main-text discipline; legend skeleton; figure legibility checks |
| [conorbronsdon/avoid-ai-writing](https://github.com/conorbronsdon/avoid-ai-writing), [tbhb/vale-ai-tells](https://github.com/tbhb/vale-ai-tells) | MIT | Deterministic checks; word tiers by density; technical-term exceptions |
| [MrGeDiao/shuorenhua](https://github.com/MrGeDiao/shuorenhua) | MIT | Engineer and debugging register as a category |
| [Leey21/awesome-ai-research-writing](https://github.com/Leey21/awesome-ai-research-writing) | none stated (ideas only) | Caption wording; LaTeX safety |
| [sam-paech/slop-forensics](https://github.com/sam-paech/slop-forensics) | MIT | Over-used words measured against a human baseline |
| [WUBING2023/PaperSpine](https://github.com/WUBING2023/PaperSpine) | MIT | The strongest reading each result supports and its likely over-reading; three states for each declaration |
| [zLanqing/codex-claude-academic-skills](https://github.com/zLanqing/codex-claude-academic-skills) | MIT | Round trip of tracked changes |
| [Haojae/scipilot-figure-skill](https://github.com/Haojae/scipilot-figure-skill) | MIT | Axes and chart types; canvas set to the final width; raw points for small samples; significance stars |
| [917Dhj/DeepPaperNote](https://github.com/917Dhj/DeepPaperNote) | MIT | `ambiguous` when several records fit a reference equally well |
| [Spark-To-Paper-Skills/paperjury](https://github.com/Spark-To-Paper-Skills/paperjury) | MIT | Quoting and locating each concern; checking whether the paper already answers it; three groups of concerns; key sentences followed through a revision |
| [claesbackman/AI-research-feedback](https://github.com/claesbackman/AI-research-feedback) | MIT | Searching the full text, supplement and protocol before calling something missing; checks before a plan is frozen |
| [fcakyon/labrat](https://github.com/fcakyon/labrat) | MIT | Comparing published estimates only when they are comparable; software defaults recorded as choices |
| [Noi1r/beamer-skill](https://github.com/Noi1r/beamer-skill) | MIT | Asking the length and audience of a talk |
| [joshzyj/open-scholar-skill](https://github.com/joshzyj/open-scholar-skill) | academic use only (ideas only) | Whether a source supports the sentence that cites it |
| [gaasher/Agent-Loop-Skills](https://github.com/gaasher/Agent-Loop-Skills) | MIT | Causes of a disagreement listed before a number changes; one change per rerun; figures spot-checked against plotted values; a checking pass where no other agent can run |
| [KalarisLabs/research-agent-skills](https://github.com/KalarisLabs/research-agent-skills), [yilunzhao/bib-audit](https://github.com/yilunzhao/bib-audit) | see repository; none stated (ideas only) | Verdicts for reference checks |
| [flonat/flonat-research](https://github.com/flonat/flonat-research) | MIT | Strictness by stage; changes judged from the revised files; numbers read from output files; citation checks by an agent that did not write the text |
| [cLin-c/paper-skill](https://github.com/cLin-c/paper-skill) | MIT | New text quoted in a response letter found word for word in the revision |
| [MrGeDiao/paper-reading-zh](https://github.com/MrGeDiao/paper-reading-zh) | MIT | Splitting a sentence into the claims it makes |
| [xf686/Meet-Reviewer-2](https://github.com/xf686/Meet-Reviewer-2) | MIT | Criticisms to leave out of a review, narrowed to those COPE and journal reviewer guides reject |
| [Eliot5566/JEV-Paper-Radar](https://github.com/Eliot5566/JEV-Paper-Radar) | MIT | Screening criteria piloted first; records awaiting assessment kept out of final counts |
| [Agent Skills specification](https://agentskills.io/specification), [Anthropic skill-authoring best practices](https://docs.claude.com/en/docs/agents-and-tools/agent-skills/best-practices), [OpenAI skill-creator](https://github.com/openai/skills) | guidance | Main uses and trigger words first in the description; a contents line in long reference files; reference files one level below `SKILL.md`; checks that apply to every round of edits |
| [Wikipedia: Signs of AI writing](https://en.wikipedia.org/wiki/Wikipedia:Signs_of_AI_writing) | CC BY-SA 4.0 (summarized, not copied) | Taxonomy of tells and their drift over time |

Rules from these sources that do not suit research articles were left out: banning the passive voice, deleting all adverbs, banning en dashes (they are required in ranges), treating `associated with` as vague, writing to the reader as `you`, sentence-length quotas, adding cushioning hedges, and any aim of passing AI detectors. Also left out from the research skills: minimum numbers of figures or references, APA format and Cohen's conventions for effect sizes, writing the introduction last, sampling citations for checks, systematic-review methods below the Cochrane standard, jury votes and simulated acceptance decisions, claim markers inside the manuscript, and the automatic choice of tests or imputation methods.

## Research on LLM vocabulary in scientific writing

- Kobak D, González-Márquez R, Horvát EÁ, Lause J. Delving into LLM-assisted writing in biomedical publications through excess vocabulary. Sci Adv 2025; 11: eadt3813. https://doi.org/10.1126/sciadv.adt3813
- Liang W, Zhang Y, Wu Z, et al. Quantifying large language model usage in scientific papers. Nat Hum Behav 2025. https://doi.org/10.1038/s41562-025-02273-8
- Juzek TS, Ward ZB. Why does ChatGPT "delve" so much? Exploring the sources of lexical overrepresentation in large language models. COLING 2025. https://arxiv.org/abs/2412.11385
- Geng M, Trotta R. Human-LLM coevolution: evidence from academic writing. 2025. https://arxiv.org/abs/2502.09606
- Matsui K. Delving into PubMed records: some terms in medical writing have drastically changed after the arrival of ChatGPT. Perspect Med Educ 2025. https://doi.org/10.5334/pme.1929

## Writing and reporting guidance

- Gopen GD, Swan JA. The science of scientific writing. Am Sci 1990; 78: 550–58. https://www.americanscientist.org/blog/the-long-view/the-science-of-scientific-writing
- International Committee of Medical Journal Editors. Recommendations for the conduct, reporting, editing, and publication of scholarly work in medical journals. https://www.icmje.org/recommendations/
- International Committee of Medical Journal Editors. AI use by reviewers. https://www.icmje.org/recommendations/browse/artificial-intelligence/ai-use-by-reviewers.html
- International Committee of Medical Journal Editors. AI use by authors. https://www.icmje.org/recommendations/browse/artificial-intelligence/ai-use-by-authors.html
- COPE Council. Ethical guidelines for peer reviewers, version 1. Committee on Publication Ethics, 2013. https://car.ca/wp-content/uploads/2025/04/Ethical_guidelines_for_peer_reviewers.pdf
- Communications Biology. A brief guide for referees. https://www.nature.com/documents/commsbio-referee-brief-guide.pdf
- EQUATOR Network reporting guidelines. https://www.equator-network.org/
- European Association of Science Editors. Author toolkit: figures and tables. https://ease.org.uk/learning-hub/author-toolkit-1/revising-your-draft-and-adding-details/figures-and-tables/
- Gelman A, Pasarica C, Dodhia R. Let's practice what we preach: turning tables into graphs. Am Stat 2002; 56: 121–30. https://doi.org/10.1198/000313002317572790
- Hopewell S, Chan AW, Collins GS, et al. CONSORT 2025 statement. BMJ 2025. https://doi.org/10.1136/bmj-2024-081123
- Hopewell S, Chan AW, Collins GS, et al. CONSORT 2025 explanation and elaboration. BMJ 2025; 389: e081124. https://doi.org/10.1136/bmj-2024-081124
- Junqueira DR, Zorzela L, Golder S, et al. CONSORT Harms 2022 statement, explanation, and elaboration. BMJ 2023; 381: e073725. https://doi.org/10.1136/bmj-2022-073725
- Chan AW, Boutron I, Hopewell S, et al. SPIRIT 2025 statement. BMJ 2025. https://doi.org/10.1136/bmj-2024-081477
- Page MJ, McKenzie JE, Bossuyt PM, et al. The PRISMA 2020 statement. BMJ 2021; 372: n71. https://doi.org/10.1136/bmj.n71
- Page MJ, Moher D, Bossuyt PM, et al. PRISMA 2020 explanation and elaboration. BMJ 2021; 372: n160. https://doi.org/10.1136/bmj.n160
- Husereau D, Drummond M, Augustovski F, et al. CHEERS 2022. BMJ 2022; 376: e067975. https://doi.org/10.1136/bmj-2021-067975
- STROBE statement. https://www.strobe-statement.org/
- Bossuyt PM, Reitsma JB, Bruns DE, et al. STARD 2015. BMJ 2015; 351: h5527. https://doi.org/10.1136/bmj.h5527
- Collins GS, Moons KGM, Dhiman P, et al. TRIPOD+AI statement. BMJ 2024; 385: e078378. https://doi.org/10.1136/bmj-2023-078378
- Kottner J, Audigé L, Brorson S, et al. Guidelines for reporting reliability and agreement studies (GRRAS) were proposed. J Clin Epidemiol 2011; 64: 96–106. https://doi.org/10.1016/j.jclinepi.2010.03.002
- Kruschke JK. Bayesian analysis reporting guidelines. Nat Hum Behav 2021; 5: 1282–91. https://doi.org/10.1038/s41562-021-01177-7
- Stevens GA, Alkema L, Black RE, et al. GATHER statement. Lancet 2016; 388: e19–23. https://doi.org/10.1016/S0140-6736(16)30388-9

## Methods guidance

- Lefebvre C, Glanville J, Briscoe S, et al. Chapter 4: searching for and selecting studies, with the MECIR standards it quotes. In: Higgins JPT, Thomas J, Chandler J, et al, eds. Cochrane Handbook for Systematic Reviews of Interventions, version 6.5.1. Cochrane, 2025. https://www.cochrane.org/authors/handbooks-and-manuals/handbook/current/chapter-04
- Deeks JJ, Higgins JPT, Altman DG, et al. Chapter 10: analysing data and undertaking meta-analyses. In: Higgins JPT, Thomas J, Chandler J, et al, eds. Cochrane Handbook for Systematic Reviews of Interventions, version 6.5.1. Cochrane, 2026. https://www.cochrane.org/handbook
- Flemyng E, Noel-Storr A, Macura B, et al. Position statement on artificial intelligence (AI) use in evidence synthesis across Cochrane, the Campbell Collaboration, JBI and the Collaboration for Environmental Evidence 2025. Cochrane Database Syst Rev 2025: ED000178. https://doi.org/10.1002/14651858.ED000178
- Bland JM, Altman DG. Statistical methods for assessing agreement between two methods of clinical measurement. Lancet 1986; 1: 307–10. https://doi.org/10.1016/S0140-6736(86)90837-8
- Austin PC, Lee DS, Fine JP. Introduction to the analysis of survival data in the presence of competing risks. Circulation 2016; 133: 601–09. https://doi.org/10.1161/CIRCULATIONAHA.115.017719
- Brown NJL, Heathers JAJ. The GRIM test: a simple technique detects numerous anomalies in the reporting of results in psychology. Soc Psychol Personal Sci 2017; 8: 363–69. https://doi.org/10.1177/1948550616673876
- Vehtari A, Gelman A, Simpson D, Carpenter B, Bürkner PC. Rank-normalization, folding, and localization: an improved R-hat for assessing convergence of MCMC. Bayesian Anal 2021; 16: 667–718. https://doi.org/10.1214/20-BA1221
- Self SG, Liang KY. Asymptotic properties of maximum likelihood estimators and likelihood ratio tests under nonstandard conditions. J Am Stat Assoc 1987; 82: 605–10. https://doi.org/10.1080/01621459.1987.10478472
- Prince T, Bommert A, Rahnenführer J, Schmid M. On the estimation of inverse-probability-of-censoring weights for the evaluation of survival prediction error. PLoS One 2025; 20: e0318349. https://doi.org/10.1371/journal.pone.0318349
- Love MI, Anders S, Huber W. Analyzing RNA-seq data with DESeq2. Bioconductor vignette, DESeq2 version 1.52.0. https://bioconductor.org/packages/release/bioc/vignettes/DESeq2/inst/doc/DESeq2.html
- Timmons JA, Szkop KJ, Gallagher IJ. Multiple sources of bias confound functional enrichment analysis of global -omics data. Genome Biol 2015; 16: 186. https://doi.org/10.1186/s13059-015-0761-7
- Bender R, Friede T, Koch A, et al. Methods for evidence synthesis in the case of very few studies. Res Synth Methods 2018; 9: 382–92. https://doi.org/10.1002/jrsm.1297
- Röver C, Bender R, Dias S, et al. On weakly informative prior distributions for the heterogeneity parameter in Bayesian random-effects meta-analysis. Res Synth Methods 2021; 12: 448–74. https://doi.org/10.1002/jrsm.1475
- Röver C. Bayesian random-effects meta-analysis using the bayesmeta R package. J Stat Softw 2020; 93 (6). https://doi.org/10.18637/jss.v093.i06
- Gomersall JS, Jadotte YT, Xue Y, et al. Conducting systematic reviews of economic evaluations. Int J Evid Based Healthc 2015; 13: 170–78. https://doi.org/10.1097/XEB.0000000000000063
- Schnitzler L, Roberts TE, Jackson LJ, et al. A consensus-based checklist for the critical appraisal of cost-of-illness (COI) studies. Int J Technol Assess Health Care 2023; 39: e34. https://doi.org/10.1017/S0266462323000193
- Turner HC, Lauer JA, Tran BX, et al. Adjusting for inflation and currency changes within health economic studies. Value Health 2019; 22: 1026–32. https://doi.org/10.1016/j.jval.2019.03.021
- Robinson LA, Hammitt JK, O'Keeffe L. Valuing mortality risk reductions in global benefit-cost analysis. J Benefit Cost Anal 2019; 10 (suppl 1): 15–50. https://doi.org/10.1017/bca.2018.26
- Sanders GD, Neumann PJ, Basu A, et al. Recommendations for conduct, methodological practices, and reporting of cost-effectiveness analyses: Second Panel on Cost-Effectiveness in Health and Medicine. JAMA 2016; 316: 1093–103. https://doi.org/10.1001/jama.2016.12195
- Briggs AH, Weinstein MC, Fenwick EAL, et al. Model parameter estimation and uncertainty analysis: ISPOR-SMDM Modeling Good Research Practices Task Force-6. Med Decis Making 2012; 32: 722–32. https://doi.org/10.1177/0272989X12458348
- Eddy DM, Hollingworth W, Caro JJ, et al. Model transparency and validation: ISPOR-SMDM Modeling Good Research Practices Task Force-7. Med Decis Making 2012; 32: 733–43. https://doi.org/10.1177/0272989X12454579

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
- ICH E9(R1): addendum on estimands and sensitivity analysis in clinical trials. 2019. https://database.ich.org/sites/default/files/E9-R1_Step4_Guideline_2019_1203.pdf
- Moher D, Shamseer L, Clarke M, et al. PRISMA-P 2015. Syst Rev 2015; 4: 1. https://doi.org/10.1186/2046-4053-4-1
- Wang SV, Pottegård A, Crown W, et al. HARPER: a harmonized protocol template for real-world evidence studies. Pharmacoepidemiol Drug Saf 2023. https://doi.org/10.1002/pds.5507
- Thorn JC, Davies CF, Brookes ST, et al. Content of health economics analysis plans (HEAPs) for trial-based economic evaluations. Value Health 2021; 24: 699–710. https://doi.org/10.1016/j.jval.2020.10.002
- Pollett S, Johansson MA, Reich NG, et al. EPIFORGE 2020 guidelines for epidemiological forecasting. PLoS Med 2021; 18: e1003793. https://doi.org/10.1371/journal.pmed.1003793
- Keep a Changelog. https://keepachangelog.com/en/1.1.0/
- Social Science Data Editors. Template README for replication packages. https://social-science-data-editors.github.io/template_README/

The plan, log and code references follow the author's own decisions where these sources disagree with them: no run-all script, no shared function or style file (the style sits at the top of each figure and table script), no unit-test scripts, the local R installation instead of a lockfile, and the history of a plan kept in the execution log instead of an amendment table, except a trial's statistical analysis plan, which keeps its versions, reasons and dates as Gamble and colleagues ask.

## Journal instructions

- The Lancet: https://www.thelancet.com/lancet/information-for-authors
- NEJM: https://www.nejm.org/author-center/new-manuscripts
- JAMA: https://jamanetwork.com/journals/jama/pages/instructions-for-authors
- BMJ: https://www.bmj.com/about-bmj/resources-authors
- Nature: https://www.nature.com/nature/for-authors/formatting-guide
- Nature figures: https://research-figure-guide.nature.com/figures/preparing-figures-our-specifications/ and https://research-figure-guide.nature.com/figures/building-and-exporting-figure-panels/
- Communications Biology formatting guidelines: https://www.nature.com/commsbio/submit/formatting-guidelines
- Nature code and software submission checklist: https://media.nature.com/full/nature-cms/documents/GuidelinesCodePublication.pdf
- Springer Nature, accessibility of figures and images (alt text): https://www.springernature.com/gp/policies/accessibility-figures-images
- BMJ journals, formatting your paper: https://authors.bmj.com/writing-and-formatting/formatting-your-paper/
- Cell Press STAR Methods: https://www.cell.com/star-authors-guide
- W3C. Web Content Accessibility Guidelines 2.2, success criterion 1.4.11 (non-text contrast): https://www.w3.org/TR/WCAG22/#non-text-contrast
- GB/T 3101-1993. General principles concerning quantities, units and symbols. Standardization Administration of China: https://openstd.samr.gov.cn/
