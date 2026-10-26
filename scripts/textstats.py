"""Shared text handling for the plain-paper scripts.

Reads manuscripts in several formats into segments (prose, captions, table
cells, slide text and text inside figures), splits sentences, applies the rules
in rules.json and computes the style profile used for calibration.
Standard library only.
"""

from __future__ import annotations

import json
import re
import shutil
import statistics
import subprocess
import zipfile
from dataclasses import dataclass
from pathlib import Path
from xml.etree import ElementTree as ET

HERE = Path(__file__).resolve().parent
RULES_PATH = HERE / "rules.json"
CALIBRATION_PATH = HERE / "calibration.json"

SCOPES = ("prose", "caption", "table", "slide", "figure")


@dataclass
class Segment:
    text: str
    line: int
    scope: str
    source: str = "body"


# ---------------------------------------------------------------------------
# Reading files
# ---------------------------------------------------------------------------

CAPTION_START = re.compile(
    r"^\s*(?:\*\*)?(?:Figure|Fig\.?|Table|Extended\s+Data\s+(?:Fig\.?|Figure|Table)|"
    r"Supplementary\s+(?:Figure|Fig\.?|Table)|eFigure|eTable|Appendix\s+(?:Figure|Table)|"
    r"Webfigure|Webtable)\s*S?\d+[A-Za-z]?\s*(?:\*\*)?\s*[:.|]"
)


def is_caption(text: str) -> bool:
    return bool(CAPTION_START.match(text))


def _paragraphs(lines: list[tuple[int, str]]) -> list[tuple[int, str]]:
    """Join consecutive non-blank lines into paragraphs, keeping the first line number."""
    paragraphs: list[tuple[int, str]] = []
    start, buffer = 0, []
    for number, line in lines:
        if line.strip():
            if not buffer:
                start = number
            buffer.append(line.strip())
        elif buffer:
            paragraphs.append((start, " ".join(buffer)))
            buffer = []
    if buffer:
        paragraphs.append((start, " ".join(buffer)))
    return paragraphs


INLINE_CODE = re.compile(r"`[^`\n]*`")
HTML_COMMENT = re.compile(r"<!--.*?-->", re.DOTALL)
MD_IMAGE = re.compile(r"!\[[^\]]*\]\([^)]*\)")
MD_LINK = re.compile(r"\[([^\]]+)\]\([^)]*\)")


def read_markdown(text: str, figure_chunks: bool = False) -> list[Segment]:
    """Markdown, Quarto and R Markdown. Code chunks are skipped, except that
    plotting code inside R or Python chunks is mined for figure text."""
    text = HTML_COMMENT.sub(lambda m: "\n" * m.group(0).count("\n"), text)
    raw_lines = text.splitlines()
    segments: list[Segment] = []
    prose: list[tuple[int, str]] = []
    in_code, fence, chunk_lang, chunk_lines, chunk_start = False, "", "", [], 0
    in_front_matter = bool(raw_lines and raw_lines[0].strip() == "---")
    for index, line in enumerate(raw_lines, start=1):
        if in_front_matter:
            if index > 1 and line.strip() in ("---", "..."):
                in_front_matter = False
            prose.append((index, ""))
            continue
        stripped = line.strip()
        if not in_code and (stripped.startswith("```") or stripped.startswith("~~~")):
            in_code, fence = True, stripped[:3]
            chunk_lang = stripped[3:].strip("{} ").split(",")[0].split()[0].lower() if stripped[3:].strip("{} ") else ""
            chunk_lines, chunk_start = [], index + 1
            prose.append((index, ""))
            continue
        if in_code:
            if stripped.startswith(fence):
                in_code = False
                if figure_chunks and chunk_lang in ("r", "python", "py"):
                    reader = read_r_code if chunk_lang == "r" else read_python_code
                    segments.extend(reader("\n".join(chunk_lines), first_line=chunk_start))
            else:
                chunk_lines.append(line)
            prose.append((index, ""))
            continue
        if stripped.startswith("    ") or line.startswith("\t"):
            prose.append((index, ""))
            continue
        line = INLINE_CODE.sub(" ", line)
        line = MD_IMAGE.sub(" ", line)
        line = MD_LINK.sub(r"\1", line)
        if re.match(r"^\s*\|?\s*:?-{3,}", line):  # table rule
            prose.append((index, ""))
            continue
        item = re.match(r"^\s*(?:[-*+]|\d+[.)])\s+", line)
        if item:  # each list item is its own paragraph
            prose.append((index, ""))
            line = line[item.end():]
        line = re.sub(r"^\s*>\s?", "", line)  # block quotes
        prose.append((index, line))
    for number, paragraph in _paragraphs(prose):
        if paragraph.startswith("|"):
            for cell in [c.strip() for c in paragraph.split("|") if c.strip()]:
                segments.append(Segment(cell, number, "table"))
            continue
        paragraph = re.sub(r"^#{1,6}\s+", "", paragraph)
        scope = "caption" if is_caption(paragraph) else "prose"
        segments.append(Segment(paragraph, number, scope))
    return sorted(segments, key=lambda s: s.line)


TEX_COMMENT = re.compile(r"(?<!\\)%.*$", re.MULTILINE)
TEX_MATH = re.compile(r"\$\$.*?\$\$|\$[^$]*\$|\\\[.*?\\\]|\\\(.*?\\\)", re.DOTALL)
TEX_ENV_SKIP = re.compile(
    r"\\begin\{(equation|align|gather|multline|tikzpicture|verbatim|lstlisting)\*?\}.*?\\end\{\1\*?\}",
    re.DOTALL,
)
TEX_REF = re.compile(r"\\(?:cite[tp]?|citep|citet|ref|eqref|autoref|cref|Cref|label)\*?(?:\[[^\]]*\])?\{[^}]*\}")


def read_tex(text: str) -> list[Segment]:
    text = TEX_COMMENT.sub("", text)
    text = TEX_ENV_SKIP.sub(lambda m: "\n" * m.group(0).count("\n"), text)
    text = TEX_MATH.sub(lambda m: " MATH " + "\n" * m.group(0).count("\n"), text)
    segments: list[Segment] = []
    for match in re.finditer(r"\\caption\{((?:[^{}]|\{[^{}]*\})*)\}", text):
        line = text.count("\n", 0, match.start()) + 1
        caption = TEX_REF.sub(" ", match.group(1))
        caption = re.sub(r"\\[a-zA-Z]+\*?(?:\[[^\]]*\])?", " ", caption).replace("{", "").replace("}", "")
        segments.append(Segment(re.sub(r"\s+", " ", caption).strip(), line, "caption", "\\caption"))
    body = re.sub(r"\\caption\{((?:[^{}]|\{[^{}]*\})*)\}", lambda m: "\n" * m.group(0).count("\n"), text)
    body = TEX_REF.sub(" ", body)
    body = re.sub(r"\\(?:begin|end)\{[^}]*\}", " ", body)
    body = re.sub(r"\\(?:section|subsection|subsubsection|paragraph)\*?\{([^}]*)\}", r"\1.", body)
    body = re.sub(r"\\(?:textbf|textit|emph|underline|textsc|mathrm|text)\{([^}]*)\}", r"\1", body)
    body = re.sub(r"\\[a-zA-Z]+\*?(?:\[[^\]]*\])?(?:\{[^}]*\})?", " ", body)
    lines = [(i, l) for i, l in enumerate(body.splitlines(), start=1)]
    for number, paragraph in _paragraphs(lines):
        segments.append(Segment(paragraph.replace("~", " "), number, "prose"))
    return sorted(segments, key=lambda s: s.line)


W = "{http://schemas.openxmlformats.org/wordprocessingml/2006/main}"
A = "{http://schemas.openxmlformats.org/drawingml/2006/main}"


def _docx_paragraph_text(paragraph: ET.Element) -> str:
    parts = []
    for node in paragraph.iter():
        if node.tag == W + "t" and node.text:
            parts.append(node.text)
        elif node.tag in (W + "tab", W + "br"):
            parts.append(" ")
    return "".join(parts).strip()


def _docx_style(paragraph: ET.Element) -> str:
    style = paragraph.find(f"{W}pPr/{W}pStyle")
    return (style.get(W + "val") or "") if style is not None else ""


def read_docx(path: Path) -> list[Segment]:
    with zipfile.ZipFile(path) as archive:
        root = ET.fromstring(archive.read("word/document.xml"))
    body = root.find(W + "body")
    segments: list[Segment] = []
    index = 0
    for child in list(body) if body is not None else []:
        if child.tag == W + "p":
            index += 1
            text = _docx_paragraph_text(child)
            if text:
                style = _docx_style(child).lower()
                scope = "caption" if ("caption" in style or is_caption(text)) else "prose"
                segments.append(Segment(text, index, scope, f"paragraph {index}"))
        elif child.tag == W + "tbl":
            for cell_paragraph in child.iter(W + "p"):
                index += 1
                text = _docx_paragraph_text(cell_paragraph)
                if text:
                    segments.append(Segment(text, index, "table", f"table paragraph {index}"))
    return segments


def read_pptx(path: Path) -> list[Segment]:
    segments: list[Segment] = []
    with zipfile.ZipFile(path) as archive:
        slides = sorted(
            (n for n in archive.namelist() if re.match(r"ppt/slides/slide\d+\.xml$", n)),
            key=lambda n: int(re.search(r"(\d+)\.xml$", n).group(1)),
        )
        for name in slides:
            number = int(re.search(r"(\d+)\.xml$", name).group(1))
            root = ET.fromstring(archive.read(name))
            for paragraph in root.iter(A + "p"):
                text = "".join(t.text or "" for t in paragraph.iter(A + "t")).strip()
                if text:
                    segments.append(Segment(text, number, "slide", f"slide {number}"))
    return segments


def read_svg(text: str) -> list[Segment]:
    segments: list[Segment] = []
    try:
        root = ET.fromstring(text)
    except ET.ParseError:
        return segments
    for node in root.iter():
        if node.tag.split("}")[-1] == "text":
            content = re.sub(r"\s+", " ", "".join(node.itertext())).strip()
            if content:
                segments.append(Segment(content, 0, "figure", "svg text"))
    return segments


def read_pdf(path: Path) -> list[Segment]:
    if not shutil.which("pdftotext"):
        raise RuntimeError("Reading PDF needs pdftotext (poppler) on PATH")
    text = subprocess.run(["pdftotext", "-q", str(path), "-"], capture_output=True, text=True).stdout
    lines = [(i, l) for i, l in enumerate(text.splitlines(), start=1)]
    return [
        Segment(p, n, "caption" if is_caption(p) else "prose")
        for n, p in _paragraphs(lines)
    ]


# --- figure text inside plotting code ---------------------------------------

R_FUNCTIONS = {
    "labs", "ggtitle", "xlab", "ylab", "annotate", "geom_text", "geom_label", "plot_annotation",
    "plot", "title", "legend", "text", "mtext", "barplot", "hist", "boxplot",
}
PY_FUNCTIONS = {
    "set_title", "title", "suptitle", "set_xlabel", "set_ylabel", "xlabel", "ylabel", "text",
    "annotate", "legend", "set_xticklabels", "set_yticklabels", "set", "labs", "ggtitle",
}
STRING = re.compile(r"""(?P<q>["'])(?P<s>(?:\\.|(?!(?P=q)).)*)(?P=q)""", re.DOTALL)
NAMED_ARG = re.compile(r"(?P<name>[A-Za-z_.][\w.]*)\s*=\s*$")


def _call_arguments(code: str, open_index: int) -> tuple[str, int]:
    """Return the text between the parenthesis at open_index and its partner."""
    depth, i, quote = 0, open_index, ""
    while i < len(code):
        char = code[i]
        if quote:
            if char == "\\":
                i += 2
                continue
            if char == quote:
                quote = ""
        elif char in "\"'":
            quote = char
        elif char == "(":
            depth += 1
        elif char == ")":
            depth -= 1
            if depth == 0:
                return code[open_index + 1:i], i
        i += 1
    return code[open_index + 1:], len(code)


def _strings_with_roles(arguments: str, function: str) -> list[tuple[str, str, int]]:
    """Find string literals in an argument list with the argument name they belong to."""
    found: list[tuple[str, str, int]] = []
    depth = 0
    for match in STRING.finditer(arguments):
        before = arguments[:match.start()]
        depth = before.count("(") - before.count(")")
        # name of the closest argument at the top level of this call
        top = before
        if depth > 0:
            # inside c(...) or list(...): use the argument that opened it
            cut = before.rfind("(")
            while cut > 0 and before[:cut].count("(") - before[:cut].count(")") > 0:
                cut = before.rfind("(", 0, cut)
            top = before[:cut]
            top = re.sub(r"[\w.]+\s*$", "", top)
        name_match = NAMED_ARG.search(top.rstrip())
        role = name_match.group("name") if name_match else "positional"
        found.append((match.group("s"), role, match.start()))
    return found


def _figure_segments(code: str, functions: set[str], first_line: int, comment: str) -> list[Segment]:
    code_no_comments = re.sub(rf"(?m){re.escape(comment)}.*$", lambda m: " " * len(m.group(0)), code)
    segments: list[Segment] = []
    pattern = re.compile(r"(?:\b|\.)(?P<f>[A-Za-z_][\w]*)\s*\(")
    for match in pattern.finditer(code_no_comments):
        function = match.group("f")
        is_scale = function.startswith("scale_")
        if function not in functions and not is_scale:
            continue
        arguments, _ = _call_arguments(code_no_comments, match.end() - 1)
        base_offset = match.end()
        for value, role, offset in _strings_with_roles(arguments, function):
            if function in ("annotate",) and value in ("text", "label", "segment", "rect", "point"):
                continue
            if role in ("family", "fontface", "hjust", "vjust", "color", "colour", "fill", "position",
                        "stat", "method", "linetype", "shape", "size", "alpha", "fontfamily", "loc",
                        "ha", "va", "fontsize", "fontweight", "weight", "palette", "na.value",
                        "values", "breaks", "limits", "trans", "transform", "guide", "c", "fmt",
                        "marker", "style", "bbox", "arrowprops", "xycoords", "textcoords", "pch", "col",
                        "lty", "lwd", "cex", "font", "adj", "pos", "side", "line", "las", "bty", "type",
                        "data", "mapping", "aes", "geom", "x", "y") and not (
                function in ("labs", "set", "plot", "title") and role in ("x", "y")
            ):
                continue
            if is_scale and role not in ("name", "labels", "positional"):
                continue
            line = first_line + code_no_comments.count("\n", 0, base_offset + offset)
            label_role = role if role != "positional" else function
            segments.append(Segment(value.replace("\\n", " "), line, "figure", f"{function}({label_role})"))
    return segments


def read_r_code(code: str, first_line: int = 1) -> list[Segment]:
    return _figure_segments(code, R_FUNCTIONS, first_line, "#")


def read_python_code(code: str, first_line: int = 1) -> list[Segment]:
    return _figure_segments(code, PY_FUNCTIONS, first_line, "#")


TEXT_SUFFIXES = {".md", ".markdown", ".txt", ".text"}


def read_segments(path: Path, scope: str | None = None) -> list[Segment]:
    suffix = path.suffix.lower()
    if suffix == ".docx":
        segments = read_docx(path)
    elif suffix == ".pptx":
        segments = read_pptx(path)
    elif suffix == ".pdf":
        segments = read_pdf(path)
    else:
        text = path.read_text(encoding="utf-8", errors="replace")
        if suffix in (".qmd", ".rmd"):
            segments = read_markdown(text, figure_chunks=True)
        elif suffix == ".tex":
            segments = read_tex(text)
        elif suffix == ".svg":
            segments = read_svg(text)
        elif suffix == ".r":
            segments = read_r_code(text)
        elif suffix == ".py":
            segments = read_python_code(text)
        else:
            segments = read_markdown(text)
    if scope:
        for segment in segments:
            segment.scope = scope
    return segments


# ---------------------------------------------------------------------------
# Sentences and words
# ---------------------------------------------------------------------------

ABBREVIATIONS = (
    "et al", "e.g", "i.e", "Fig", "Figs", "vs", "No", "Nos", "approx", "ca", "cf", "Dr", "Prof",
    "Eq", "Eqs", "Ref", "Refs", "Suppl", "Vol", "pp", "p", "Inc", "Ltd", "Co", "St", "Mt", "Jr",
    "Jan", "Feb", "Mar", "Apr", "Jun", "Jul", "Aug", "Sep", "Sept", "Oct", "Nov", "Dec",
    "U.S", "U.K", "Ph.D", "M.D", "min", "max", "sp", "spp", "var", "resp", "incl", "est",
)
_ABBREV = re.compile(r"\b(" + "|".join(re.escape(a) for a in ABBREVIATIONS) + r")\.", re.IGNORECASE)
_SPLIT = re.compile(r"(?<=[.!?])[\"'”’)\]]*\s+(?=[A-Z(\[“\"‘'])")
WORD = re.compile(r"[A-Za-z]+(?:['’-][A-Za-z]+)*")


def split_sentences(text: str) -> list[str]:
    protected = _ABBREV.sub(lambda m: m.group(1).replace(".", "\u2024") + "\u2024", text)
    protected = re.sub(r"(?<=\b[A-Z])\.(?=\s?[A-Z]\.)", "\u2024", protected)  # initials
    pieces = _SPLIT.split(protected)
    return [p.replace("\u2024", ".").strip() for p in pieces if p.strip()]


def words(text: str) -> list[str]:
    return WORD.findall(text)


# ---------------------------------------------------------------------------
# Rules
# ---------------------------------------------------------------------------

@dataclass
class Rule:
    id: str
    category: str
    level: str
    scopes: tuple[str, ...]
    hint: str
    pattern: re.Pattern | None
    kind: str = "regex"
    unless: str = ""
    formats: tuple[str, ...] = ()
    skip_docs: tuple[str, ...] = ()
    skip_urls: bool = False


def load_rules(path: Path = RULES_PATH) -> tuple[dict, list[Rule]]:
    data = json.loads(path.read_text(encoding="utf-8"))
    rules = []
    for item in data["rules"]:
        flags = re.IGNORECASE if "i" in item.get("flags", "") else 0
        flags |= re.MULTILINE
        pattern = re.compile(item["pattern"], flags) if item.get("pattern") else None
        rules.append(Rule(
            id=item["id"],
            category=item["category"],
            level=item["level"],
            scopes=tuple(item.get("scopes", SCOPES)),
            hint=item["hint"],
            pattern=pattern,
            kind=item.get("kind", "regex"),
            unless=item.get("unless", ""),
            formats=tuple(item.get("formats", ())),
            skip_docs=tuple(item.get("skip_docs", ())),
            skip_urls=bool(item.get("skip_urls", False)),
        ))
    return data, rules


def regex_rules(rules: list[Rule]) -> list[Rule]:
    return [r for r in rules if r.kind == "regex" and r.pattern is not None]


STATISTICS = re.compile(
    r"\b[Pp]\s*[=<>≤≥]|\bCI\b|confidence\s+interval|\d\s?%|statistic|\btest(?:s|ed|ing)?\b|χ|chi-?squared?"
    r"|odds\s+ratio|hazard\s+ratio|risk\s+ratio|\b(?:OR|HR|RR|aOR|aHR|IRR)\b|regression|α"
)
AVERAGE = re.compile(r"\b(?:average|mean|median|rate|ratio)\b|\bper\s+(?:\d|1000|100|10\s?000)", re.IGNORECASE)
UNLESS = {
    "number": re.compile(r"\d"),
    "statistics": STATISTICS,
    "average": AVERAGE,
    "quote": re.compile(r"[\"“”]"),
}
URL = re.compile(r"https?://\S+|www\.\S+|\bdoi:\s*\S+|\b10\.\d{4,9}/\S+|[\w.+-]+@[\w-]+\.[\w.]+")


def sentence_spans(text: str) -> list[tuple[int, int]]:
    spans, cursor = [], 0
    for sentence in split_sentences(text):
        start = text.find(sentence[:20], cursor)
        if start < 0:
            start = cursor
        end = start + len(sentence)
        spans.append((start, end))
        cursor = end
    return spans or [(0, len(text))]


def sentence_at(text: str, spans: list[tuple[int, int]], index: int) -> str:
    for start, end in spans:
        if start <= index < max(end, start + 1):
            return text[start:end]
    return text


def rule_matches(rule: Rule, text: str, spans: list[tuple[int, int]] | None = None) -> list[re.Match]:
    """Regex matches of a rule in a segment, after applying its 'unless' condition."""
    if rule.pattern is None:
        return []
    matches = list(rule.pattern.finditer(text))
    if matches and rule.skip_urls:
        links = [m.span() for m in URL.finditer(text)]
        matches = [m for m in matches if not any(a <= m.start() < b for a, b in links)]
    if not matches or not rule.unless:
        return matches
    spans = spans if spans is not None else sentence_spans(text)
    condition = UNLESS[rule.unless]
    return [m for m in matches if not condition.search(sentence_at(text, spans, m.start()))]


# ---------------------------------------------------------------------------
# Style profile
# ---------------------------------------------------------------------------

PASSIVE = re.compile(
    r"\b(?:is|are|was|were|be|been|being)\s+(?:\w+ly\s+)?"
    r"(?:\w+ed|made|done|given|shown|seen|found|known|taken|held|kept|left|built|sent|set|put|"
    r"thought|brought|sought|run|begun|chosen|drawn|driven|written|grown|withdrawn|undertaken|"
    r"spent|paid|lost|met|led|read|identified|split|cut|hit|bound)\b",
    re.IGNORECASE,
)
HEDGE = re.compile(
    r"\b(?:may|might|could|likely|possibly|perhaps|suggest(?:s|ed|ing)?|appears?\s+to|appeared\s+to)\b",
    re.IGNORECASE,
)
WE = re.compile(r"\b(?:we|our|us)\b", re.IGNORECASE)
CONTRAST = re.compile(
    r"\brather\s+than\b|\binstead\s+of\b|\bnot\s+only\b|\bnot\b[^.;!?]{1,60}?\bbut\b|,\s+not\s+[a-z]|^Instead,",
    re.IGNORECASE,
)
SIGNPOST_AI = re.compile(
    r"^(?:Moreover|Furthermore|Additionally|Notably|Importantly|Interestingly|Crucially|Critically|Collectively|Taken together),",
)
HOWEVER = re.compile(r"^However,")
EM_DASH = re.compile("\u2014")
SEMICOLON = re.compile(";")


def _quantile(values: list[float], q: float) -> float:
    if not values:
        return 0.0
    ordered = sorted(values)
    position = (len(ordered) - 1) * q
    low = int(position)
    high = min(low + 1, len(ordered) - 1)
    return ordered[low] + (ordered[high] - ordered[low]) * (position - low)


def sentence_stats(sentences: list[str]) -> dict:
    lengths = [len(words(s)) for s in sentences]
    lengths = [n for n in lengths if n >= 3]
    if not lengths:
        return {"sentences": 0}
    return {
        "sentences": len(lengths),
        "sentence_median": statistics.median(lengths),
        "sentence_p25": _quantile(lengths, 0.25),
        "sentence_p75": _quantile(lengths, 0.75),
        "share_over_35": sum(n > 35 for n in lengths) / len(lengths),
        "share_over_50": sum(n > 50 for n in lengths) / len(lengths),
        "share_under_10": sum(n < 10 for n in lengths) / len(lengths),
    }


PROFILE_METRICS = (
    "sentence_median", "share_over_35", "share_under_10", "we_per_1000", "passive_share",
    "hedges_per_1000", "contrast_per_1000", "ai_signposts_per_1000", "however_per_1000",
    "em_dash_per_1000", "semicolons_per_1000",
)


def profile(sentences: list[str]) -> dict:
    """Style metrics for a list of prose sentences."""
    text = " ".join(sentences)
    total_words = len(words(text))
    result = {"words": total_words}
    result.update(sentence_stats(sentences))
    if total_words == 0 or not sentences:
        return result
    per_1000 = 1000.0 / total_words
    result.update({
        "we_per_1000": len(WE.findall(text)) * per_1000,
        "passive_share": sum(bool(PASSIVE.search(s)) for s in sentences) / len(sentences),
        "hedges_per_1000": len(HEDGE.findall(text)) * per_1000,
        "contrast_per_1000": sum(bool(CONTRAST.search(s)) for s in sentences) * per_1000,
        "ai_signposts_per_1000": sum(bool(SIGNPOST_AI.match(s)) for s in sentences) * per_1000,
        "however_per_1000": sum(bool(HOWEVER.match(s)) for s in sentences) * per_1000,
        "em_dash_per_1000": len(EM_DASH.findall(text)) * per_1000,
        "semicolons_per_1000": len(SEMICOLON.findall(text)) * per_1000,
    })
    return result


def load_calibration(path: Path = CALIBRATION_PATH) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))
