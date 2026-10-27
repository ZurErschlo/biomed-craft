# biomed-craft

[English](README.md) | 中文

[![Check package](https://github.com/ZurErschlo/biomed-craft/actions/workflows/validate.yml/badge.svg)](https://github.com/ZurErschlo/biomed-craft/actions/workflows/validate.yml)

一个面向生物医学研究的 agent skill，覆盖从提出研究问题到论文发表、回复审稿意见的全过程。它从写作出发，但不止于写作：研究设计、研究方案和执行记录、数据与文献依据、分析代码、图表、论文、报告规范清单和同行评审。

研究者始终是作者。研究问题、设计、决定结果的关键数值、结果解读和投稿内容由研究者决定；AI 为每个决定准备依据，完成底层工作（查找并核实文献和数据、检查数字前后一致、起草和润色），在约定的确认点停下来，并在每项任务结束时说明：做了什么，什么没做及原因，哪里做错了，哪些需要研究者决定。任何内容都不建立在猜测或凭记忆的数字上。

skill 采用 [Agent Skills](https://agentskills.io) 格式，可用于 Claude Code、Codex 以及其他读取 `SKILL.md` 的 agent。

## 覆盖内容

- **按高水平期刊的标准写作**（Lancet、NEJM、JAMA、BMJ、Nature、Science、Cell 及其主要子刊）：论文各部分、补充材料、图注、表注和图中文字；去掉 AI 腔、工程化表达、防御性表达和过程性叙述。
- **三层标准**：通用标准管用语和各刊共同做法；目标期刊层管结构和格式；研究类型层管该类研究必须交代的内容和写法。
- **13 类研究**：随机对照试验、观察性与数据库研究、孟德尔随机化、系统综述与 Meta 分析、叙述性综述、卫生经济学评价、诊断准确性研究、临床预测模型、疾病与流行病学建模、实验室与机制研究、计算与组学研究、定性与混合方法研究。每类都写明论文必须包含的内容、审稿人常挑的问题和高质量论文的应对办法，以及高水平期刊的写法。
- **研究的其他部分**：别人照着就能复现的研究方案、执行记录、在 RStudio 里能逐节运行的分析代码、代码注释和项目文件夹。
- **依据与一致性**：每个论断和数值都有出处，数据用最新、最权威的来源，数字回头核对原始来源，下载的全文与文献记录逐一核对，研究方案、代码、图表和正文说的是同一件事。

## 安装

用 skills CLI：

```bash
npx skills add ZurErschlo/biomed-craft
```

作为 Claude Code 插件：

```text
/plugin marketplace add ZurErschlo/biomed-craft
/plugin install biomed-craft@biomed-craft
```

或直接克隆到 agent 的 skills 文件夹：

```bash
git clone https://github.com/ZurErschlo/biomed-craft.git ~/.claude/skills/biomed-craft
```

Codex 用 `~/.codex/skills/biomed-craft`。

## 使用

- “根据表 1–3 写这个队列研究的 Results，目标期刊 JAMA Internal Medicine。”
- “润色这段 Discussion，目标期刊还没定。”
- “按系统综述的清单审一下这篇 Meta 分析，列出缺了什么。”
- “检查 research_plan.md 和 analysis/ 里的脚本。”
- “筛选之前，核对这 120 个 PDF 是不是 included.ris 里对应的文章。”
- “帮我回复审稿意见，这是意见和稿件。”

脚本可以单独运行（Python 3.10 及以上，只用标准库；读 PDF 需要 `pdftotext`）：

```bash
python3 scripts/scan.py manuscript.docx
python3 scripts/scan.py --type prediction --profile draft.md
python3 scripts/scan.py --doc code analysis/
python3 scripts/check_numbers.py manuscript.docx
python3 scripts/check_fulltext.py included.ris fulltexts/
python3 scripts/check_preservation.py original.docx revised.docx
```

`scan.py` 读取 Word、Markdown、Quarto、LaTeX、PowerPoint、PDF、SVG 以及 R 和 Python 代码，自动判断研究类型，按规则列出问题，规则级别随研究类型和期刊调整。`check_numbers.py` 找出与人数对不上的百分比、落在置信区间外的点估计，以及摘要里有、正文里找不到的数字。`check_fulltext.py` 列出下错的文章、补充材料、只是引用了该文的页面（评论、更正、患者须知等）、重复文件，以及没有对应 PDF 的记录。`check_preservation.py` 确认修改前后数字、引用和交叉引用没有丢失或增加。

## 结构

- `SKILL.md`：原则、开始前的识别、到哪里找规范、核心写作规则和输出要求。
- `references/`：每个文件一个主题，按需读取：分阶段与研究者协作、依据与数据、研究类型、论文各部分、句子、期刊格式、图表、表达层次、AI 腔、研究方案、执行记录、代码、文件夹、同行评审、其他文书、数字格式、语料、示例和来源。
- `scripts/rules.json`：用词规则，每条都带必须命中和不得命中的例句。只有高水平期刊研究论文几乎从不使用的写法才列为必须改，并且按期刊和研究类型分别核对。
- `scripts/calibrate.py`：用 PDF、本地保存的文章文本和 Europe PMC 上的开放获取出版社版本重建参考数据。

## 来源

依据高水平期刊的研究论文及其补充材料、现行报告规范（CONSORT 2025、SPIRIT 2025、PRISMA 2020、STROBE、CHEERS 2022、STARD、TRIPOD+AI 等）、作者本人的研究项目和修改决定，以及 [blader/humanizer](https://github.com/blader/humanizer)、[K-Dense-AI/scientific-agent-skills](https://github.com/K-Dense-AI/scientific-agent-skills)、[Yuan1z0825/nature-skills](https://github.com/Yuan1z0825/nature-skills)、[Imbad0202/academic-research-skills](https://github.com/Imbad0202/academic-research-skills)（只借鉴思路）等公开 skill。完整清单见 [references/sources.md](references/sources.md)。

## 版本记录

见 [CHANGELOG.md](CHANGELOG.md)。

## 许可

[MIT](LICENSE)
