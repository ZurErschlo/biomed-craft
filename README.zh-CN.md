# plain-paper

[English](README.md) | 中文

[![Check package](https://github.com/ZurErschlo/plain-paper/actions/workflows/validate.yml/badge.svg)](https://github.com/ZurErschlo/plain-paper/actions/workflows/validate.yml)

按正刊和大子刊的写法，写作、优化和审校英文学术文本；同时去掉 AI 腔、工程化表达、防御性表达和与研究本身无关的过程性表述。覆盖论文每一部分、补充材料、图注、表注和图内文字，也适用于研究方案、回复审稿信、知情同意书和汇报幻灯片。

规则来自四处，按优先级：作者本人在稿件、方案、图表和幻灯片上的修改决定；124 篇正刊和大子刊研究论文（正文、补充材料和图表）；GitHub 上的同类 skill；期刊作者指南和报告规范。采用 [Agent Skills](https://agentskills.io) 格式，可用于 Claude Code、Codex 和其他支持 SKILL.md 的代理。

## 最常见的五类问题

```text
对照框架      The central gap is not cost. It is coverage.
过程叙述      In the revised version, we reran the pipeline (see 02_model.R).
工程化表达    Our pipeline cleaned and merged the records with seed = 2024.
防御性表达    It is important to note that these estimates could potentially change.
图注内部信息  Figure 2: This figure shows incidence from amr_rate_v2, suggesting a decline.
```

改写后：

```text
Coverage was the main constraint: uptake fell from 64% to 41% in districts that lost nurses.
We linked notification and laboratory records by national identifier and removed duplicates.
The estimates depend on the assumed duration of infectiousness (appendix p 9).
Figure 2: Incidence of drug-resistant tuberculosis by WHO region, 2010–2022
```

## 安装

用 skills CLI（推荐，自动链接到本机已装的代理）：

```bash
npx skills add ZurErschlo/plain-paper
```

在 Claude Code 里作为插件安装：

```text
/plugin marketplace add ZurErschlo/plain-paper
/plugin install plain-paper@plain-paper
```

或直接克隆到代理的 skills 目录：

```bash
git clone https://github.com/ZurErschlo/plain-paper.git ~/.claude/skills/plain-paper
```

Codex 用 `~/.codex/skills/plain-paper`；其他代理放到各自的 skills 目录，或让代理读取仓库根目录的 `SKILL.md`。

## 使用

直接说要做什么，代理会按需加载：

- 起草：“用 plain-paper 根据这些结果写 Results，目标期刊 Lancet Infectious Diseases。”
- 优化：“润色这段 Discussion，去掉 AI 腔和防御性表达。”
- 审校：“逐条审校这份 Methods，用原文、改为、原因三栏给出。”
- 检查：“检查 figures/ 里的 R 绘图代码和图注有没有内部信息。”

也可以直接运行检查脚本（Python 3.10 以上，只用标准库；读取 PDF 需要 pdftotext）：

```bash
python3 scripts/scan.py manuscript.docx
python3 scripts/scan.py --profile --journal lancet draft.md
python3 scripts/scan.py --strict legends.md figures/*.R
python3 scripts/check_preservation.py original.docx revised.docx
```

`scan.py` 读取 Word、Markdown、Quarto、LaTeX、PowerPoint、PDF、SVG 以及 R 和 Python 绘图代码，按规则编号列出问题，并把句长、限定语、连接词、对照框架等频率与正刊的参考范围对比。`check_preservation.py` 对比改前改后的数字、引用、图表与附录编号和链接，确认改写没有丢失或新增事实。

## 工作原理

- `SKILL.md` 给出流程：先判断文档类型、所在部分、研究设计和目标期刊，再按顺序处理过程叙述、工程化、防御性、AI 句式和词汇、章节写法、期刊体例，最后复查。
- `references/` 按需读取：句子与段落、各部分写法、各刊体例、图表、四类不该出现的表达、AI 句式与词表、其他文件类型、数字与格式、语料说明、示例和来源。
- `scripts/rules.json` 有 83 条规则，分三级：must（正刊几乎不印，或属于内部信息）、review（结合上下文判断）、density（正刊常见，只看频率）。每条规则都附有必须命中和不得命中的例句。
- 分级依据语料：一个词或句式在 2023 年前的正刊研究论文里出现的比例不超过约 3%，才列为 must。`scripts/calibrate.py` 可用你自己领域的正刊 PDF 重新校准。

| 类别 | 内容 | 条数 |
|---|---|---|
| CON | 对照框架（not X but Y 等） | 10 |
| DEF | 防御性表达 | 11 |
| META | 过程和元数据叙述 | 11 |
| ENG | 工程化表达 | 9 |
| LEX | 正刊少用的词 | 10 |
| STR | 句式与标点 | 10 |
| HYG | 内部信息（文件名、变量名、占位符等） | 11 |
| FMT | 数字、语法与格式 | 5 |
| CAP | 图注与表注 | 1 |
| FIG | 图内文字 | 5 |

## 验证

```bash
python3 scripts/validate_package.py
python3 -m unittest discover -s tests -v
```

测试覆盖：每条规则的例句；各种文件格式的读取；命令行退出码；正刊风格段落零误报；must 级规则在 2023 年前正刊论文中的出现比例不超过 10%。`tests/fixtures/cases.json` 是给代理做改写测试的案例，核对方法见 [tests/README.md](tests/README.md)。

语料偏重感染病、耐药和建模研究，NEJM、BMJ、JAMA、Science 的样本较小，相应的参考范围只是粗略值。

## 来源

完整清单见 [references/sources.md](references/sources.md)。主要参考了 [blader/humanizer](https://github.com/blader/humanizer)、[op7418/Humanizer-zh](https://github.com/op7418/Humanizer-zh)、[hardikpandya/stop-slop](https://github.com/hardikpandya/stop-slop)、[matsuikentaro1/humanizer_academic](https://github.com/matsuikentaro1/humanizer_academic) 等仓库，以及 Kobak 等（Science Advances 2025）和 Liang 等（Nature Human Behaviour 2025）关于科研写作中大模型用词的研究。所有文字为本仓库原创；无许可或非商业许可的仓库只借鉴思路并注明出处。

## 版本

见 [CHANGELOG.md](CHANGELOG.md)。

## 许可

[MIT](LICENSE)

