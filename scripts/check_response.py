#!/usr/bin/env python3
"""Check that the new text quoted in a response letter appears in the revised manuscript.

Finds the passages a response letter gives as new or revised text:

  - text in double quotation marks, eight words or longer, when the words before it mark it
    as new ("we revised", "now reads", "added", "changed to") and not as the original text or
    the reviewer's words;
  - the paragraph after a label such as "Revised text:" or "New text:", or the text after
    "now reads:".

Each sentence of each passage is looked for in the revision, after both are normalized (case,
quotation marks, dashes, spaces, citation markers and Word superscripts are ignored):

  found     it appears word for word
  differs   the closest sentence in the revision is similar but not the same; both are shown
  missing   nothing in the revision comes close

The place the letter names is compared with where the sentence was found. Sections, tables
and figures are checked; pages and lines depend on the layout and are reported as not checked.
Quotations that nothing marks as new are listed, so that none is skipped without a word.

Word files are read with tracked changes accepted: inserted text is kept, deleted text dropped.
Give the supplement after the manuscript when the letter quotes text from it.

Examples:
  python3 check_response.py response.docx revised.docx
  python3 check_response.py response.docx revised.docx supplement.docx
  python3 check_response.py --json response.md revised.md

Exit status: 0 when every quoted sentence is found at the place named, 1 otherwise, 2 for
usage errors.
"""

from __future__ import annotations

import argparse
import difflib
import json
import re
import sys
import unicodedata
import xml.etree.ElementTree as ET
import zipfile
from dataclasses import asdict, dataclass, field
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import textstats as ts  # noqa: E402

# Quotations shorter than this are usually terms, phrases or the reviewer's words.
MIN_WORDS = 8
# Shorter pieces, such as "(Table 2)", are not checked on their own.
MIN_SENTENCE_WORDS = 4
# At or above this similarity the closest sentence is the same sentence edited after the letter
# was written; below it, it is usually a different sentence.
SIMILAR = 0.8
# Candidates sharing fewer of the quoted sentence's words than this are not compared at all.
SHARED_WORDS = 0.5
# How far before a quotation the words marking it as new or original are looked for.
CONTEXT = 300

W = ts.W
QUOTE = re.compile(r"[“\"]([^”\"]+)[”\"]")
NEW_MARK = re.compile(
    r"\b(?:revis\w*|added|add|now\s+reads?|now\s+states?|reads\s+as\s+follows|as\s+follows|changed|amended|"
    r"inserted|rewritten|rephrased|reworded|expanded|clarified|updated|new\s+(?:text|sentence|paragraph)|"
    r"we\s+(?:now\s+)?(?:write|state|report|say))\b", re.IGNORECASE)
OLD_MARK = re.compile(
    r"\b(?:original(?:ly)?|previous(?:ly)?|old|former(?:ly)?|first\s+version|reviewer|referee|"
    r"you\s+(?:wrote|state|suggest|mention)|comment|deleted|removed|used\s+to\s+read)\b", re.IGNORECASE)
LABEL = re.compile(
    r"^\W*(?:(?:revised|new|added|amended|changed|updated|modified)\s+(?:text|sentences?|paragraphs?|wording|"
    r"version|passage)|changes?\s+(?:made\s+)?in\s+the\s+manuscript|text\s+added)\b[^:]{0,80}:\s*", re.IGNORECASE)
INLINE = re.compile(
    r"(?:now\s+reads?|reads\s+as\s+follows|(?:was|has\s+been)\s+(?:changed|revised)\s+to|we\s+now\s+write)"
    r"[^:“\"]{0,60}:\s*(?=[^\s“\"])", re.IGNORECASE)
REVIEWER = re.compile(r"^\W*((?:reviewer|referee)\s*#?\s*\d+|editor)\b", re.IGNORECASE)
COMMENT = re.compile(r"^\W*(R\d+[.\-]\d+|E\d+|(?:comment|point|query)\s*#?\s*[\d.]*\d)\b", re.IGNORECASE)
SECTIONS = {
    "abstract": "abstract", "summary": "abstract", "introduction": "introduction", "background": "introduction",
    "method": "methods", "methods": "methods", "materials and methods": "methods", "result": "results",
    "results": "results", "discussion": "discussion", "conclusion": "conclusions", "conclusions": "conclusions",
    "limitations": "discussion", "research in context": "research in context",
}
SECTION_WORD = re.compile(r"\b(" + "|".join(sorted(SECTIONS, key=len, reverse=True)) + r")\b", re.IGNORECASE)
DISPLAY = re.compile(
    r"\b(?:(supplementary|extended\s+data|appendix)\s+)?(e|web)?(table|figure|fig\.?)\s*(s?\d+)", re.IGNORECASE)
PAGE_LINE = re.compile(r"\b(?:pages?|pp?\.)\s*\d+(?:\s*[–-]\s*\d+)?|\blines?\s*\d+(?:\s*[–-]\s*\d+)?", re.IGNORECASE)
CITATION = re.compile(r"\[\s*\d+(?:\s*[,–-]\s*\d+)*\s*\]")
SUPERSCRIPT = re.compile(r"<sup>(.*?)</sup>|\^([^^\s]+)\^|([⁰¹²³⁴-⁹⁻⁺]+)")
SUPERSCRIPT_DIGITS = str.maketrans("⁰¹²³⁴⁵⁶⁷⁸⁹⁻⁺−", "0123456789-+-")
# A superscript is a power, not a citation, after a 10 (10⁶, ×10⁹) or after a unit (m², s⁻¹, kg/m²).
POWER_OF_TEN = re.compile(r"(?<![\d.,])10$")
UNIT = re.compile(r"(?:\b(?:[kcmdµμn]?m|[mµμn]?[gLl]|mol|min|s|h|ft|in)|/m)$")


def is_power(before: str, superscript: str) -> bool:
    """Whether a superscript after the text `before` is an exponent: two digits at most after 10,
    one digit after a unit; a citation number otherwise."""
    content = superscript.translate(SUPERSCRIPT_DIGITS).strip()
    if POWER_OF_TEN.search(before.rstrip("×x ")) and re.fullmatch(r"-?\d{1,2}", content):
        return True
    return bool(UNIT.search(before) and re.fullmatch(r"-?\d", content))


def mark_powers(text: str) -> str:
    """Citation superscripts dropped; powers written as ^6, ^2 or ^-1 so that 10⁶ and 10³ differ."""
    out, last = [], 0
    for match in SUPERSCRIPT.finditer(text):
        content = match[1] or match[2] or match[3] or ""
        out.append(text[last:match.start()])
        before = "".join(out)
        out.append("^" + content.translate(SUPERSCRIPT_DIGITS).strip() if is_power(before, content) else " ")
        last = match.end()
    out.append(text[last:])
    return "".join(out)


@dataclass
class Sentence:
    text: str
    status: str
    found_at: str = ""
    closest: str = ""
    similarity: float = 0.0


@dataclass
class Passage:
    letter_location: str
    comment: str
    named_place: str
    sentences: list[Sentence] = field(default_factory=list)
    place_check: str = ""


@dataclass
class Unit:
    """A paragraph of the revision, with the section and the table or figure it belongs to."""
    text: str
    location: str
    section: str
    display: str
    normalized: str = ""


# ---------------------------------------------------------------------------
# Reading
# ---------------------------------------------------------------------------

def _docx_text(paragraph: ET.Element) -> str:
    """Paragraph text with changes accepted and citation superscripts left out; a superscript power
    (10⁶, m²) is kept as ^6 or ^2."""
    parts = []
    for run in (n for n in ts.docx_accepted(paragraph) if n.tag == W + "r"):
        align = run.find(f"{W}rPr/{W}vertAlign")
        if align is not None and align.get(W + "val") == "superscript":
            text = "".join(n.text or "" for n in run if n.tag == W + "t")
            if text and is_power("".join(parts), text):
                parts.append("^" + text.translate(SUPERSCRIPT_DIGITS).strip())
            continue
        for node in run:
            if node.tag == W + "t" and node.text:
                parts.append(node.text)
            elif node.tag in (W + "tab", W + "br"):
                parts.append(" ")
    return "".join(parts).strip()


def read_docx(path: Path) -> list[ts.Segment]:
    """Body paragraphs, content controls and table cells, in order, with changes accepted:
    deleted text sits in w:delText, which is not read."""
    with zipfile.ZipFile(path) as archive:
        root = ET.fromstring(archive.read("word/document.xml"))
    body = root.find(W + "body")
    segments, index = [], 0

    def add(paragraph: ET.Element, scope: str) -> None:
        nonlocal index
        index += 1
        text = _docx_text(paragraph)
        if not text:
            return
        style = paragraph.find(f"{W}pPr/{W}pStyle")
        name = (style.get(W + "val") or "").lower() if style is not None else ""
        if scope == "prose" and ("caption" in name or ts.is_caption(text)):
            scope = "caption"
        where = f"table paragraph {index}" if scope == "table" else f"paragraph {index}"
        segments.append(ts.Segment(text, index, scope, where))

    for child in list(body) if body is not None else []:
        if child.tag == W + "p":
            add(child, "prose")
        elif child.tag == W + "tbl":
            for paragraph in child.iter(W + "p"):
                add(paragraph, "table")
        elif child.tag == W + "sdt":
            for paragraph in child.iter(W + "p"):
                add(paragraph, "prose")
    return segments


def read(path: Path) -> list[ts.Segment]:
    segments = read_docx(path) if path.suffix.lower() == ".docx" else ts.read_segments(path)
    return [s for s in segments if s.scope in ("prose", "caption", "table")]


def _where(segment: ts.Segment) -> str:
    return f"line {segment.line}" if segment.source == "body" else segment.source


def normalize(text: str) -> str:
    text = unicodedata.normalize("NFKC", mark_powers(CITATION.sub(" ", text))).casefold()
    text = text.replace("·", ".").replace("−", "-").replace("–", "-").replace("—", "-")
    text = re.sub(r"(?<=\d)\.(?=\d)", "․", text)  # keep decimal points
    text = re.sub(r"(?<=[^\W\d_])-|-(?=[^\W\d_])|(?<=\d)-(?=\d)", " ", text)  # hyphens and ranges; minus stays
    text = re.sub(r"\s*([<>=≤≥±^])\s*", r" \1 ", text)  # P < 0.05 and P > 0.05 stay apart
    text = re.sub(r"[^\w\s%․<>=≤≥±^-]|_", " ", text).replace("․", ".")
    return re.sub(r"\s+", " ", text).strip()


def _display_label(match: re.Match) -> str:
    """'table 2', 'figure 3', 'supplementary table s1', 'extended data figure 4'."""
    prefix = re.sub(r"\s+", " ", (match[1] or match[2] or "").lower())
    if prefix in ("e", "web", "appendix"):
        prefix = "supplementary"
    kind = "figure" if match[3].lower().startswith("fig") else "table"
    return f"{prefix + ' ' if prefix else ''}{kind} {match[4].lower()}"


def _heading(text: str) -> str:
    """The section a short heading opens, or '' for any other paragraph."""
    plain = re.sub(r"^[\d.\s]+", "", text).strip().strip("*_ ").rstrip(":")
    if len(plain.split()) > 4 or plain.endswith("."):
        return ""
    return SECTIONS.get(plain.casefold(), "")


def revision_units(paths: list[Path]) -> list[Unit]:
    units = []
    for path in paths:
        section, display = "", ""
        prefix = f"{path.name}, " if len(paths) > 1 else ""
        for segment in read(path):
            heading = _heading(segment.text)
            if heading:
                section, display = heading, ""
                continue
            if segment.scope == "caption":
                match = DISPLAY.match(segment.text.strip("*_ "))
                display = _display_label(match) if match else ""
            elif segment.scope == "prose":
                display = ""
            units.append(Unit(segment.text, prefix + _where(segment), section,
                              display if segment.scope != "prose" else "", normalize(segment.text)))
    return units


# ---------------------------------------------------------------------------
# The letter
# ---------------------------------------------------------------------------

def place_named(text: str) -> str:
    """The section, table or figure, and the page or line, that a piece of the letter names."""
    parts = []
    displays = list(DISPLAY.finditer(text))
    if displays:
        parts.append(_display_label(displays[-1]))
    sections = list(SECTION_WORD.finditer(text))
    if sections:
        parts.append(SECTIONS[sections[-1].group(1).lower()])
    pages = [re.sub(r"\s+", " ", p) for p in PAGE_LINE.findall(text)]
    if pages:
        parts.append(", ".join(pages))
    return "; ".join(parts)


def _marked_new(before: str) -> bool:
    new = list(NEW_MARK.finditer(before))
    if not new:
        return False
    old = list(OLD_MARK.finditer(before))
    return not old or old[-1].start() < new[-1].start()


def letter_passages(path: Path) -> tuple[list[tuple[str, str, str, str]], list[str]]:
    """(letter location, comment, place named, passage) for each passage of new text, and the
    quotations that nothing marks as new."""
    found, skipped = [], []
    reviewer = comment = label = previous = ""
    for segment in read(path):
        text, where = segment.text.strip(), _where(segment)
        head = REVIEWER.match(text)
        if head:
            reviewer = comment = re.sub(r"\s+", " ", head.group(1))
        mark = COMMENT.match(text)
        if mark:
            number = re.sub(r"\s+", " ", mark.group(1))
            comment = f"{reviewer}, {number}" if reviewer and not re.match(r"[RE]\d", number) else number
        if label:  # the paragraph after a label line is the new text
            found.append((where, comment, place_named(label), text.strip("“”\" ")))
            label, previous = "", text
            continue
        labeled = LABEL.match(text)
        if labeled:
            rest = text[labeled.end():].strip()
            if rest:
                found.append((where, comment, place_named(text[:labeled.end()]), rest.strip("“”\" ")))
            else:
                label = text
            previous = text
            continue
        inline = INLINE.search(text)
        if inline and not QUOTE.search(text[inline.end():]):
            found.append((where, comment, place_named(text[:inline.start()]), text[inline.end():].strip()))
            previous = text
            continue
        for quote in QUOTE.finditer(text):
            passage = quote.group(1).strip()
            if len(ts.words(passage)) < MIN_WORDS:
                continue
            before = QUOTE.sub(" ", previous[-200:] + " " + text[:quote.start()])[-CONTEXT:]
            if not _marked_new(before):
                skipped.append(f"{where}: {passage[:70]}…")
                continue
            after = re.match(r"\s*\(([^)]*)\)", text[quote.end():])
            named = place_named(QUOTE.sub(" ", text[:quote.start()]) + " " + (after.group(1) if after else ""))
            found.append((where, comment, named or place_named(QUOTE.sub(" ", previous)), passage))
        previous = text
    return found, skipped


# ---------------------------------------------------------------------------
# Matching
# ---------------------------------------------------------------------------

def _fragments(passage: str) -> list[str]:
    """The sentences of a passage; an ellipsis splits it into pieces checked separately."""
    sentences = []
    for piece in re.split(r"\s*(?:\[\s*(?:\.\.\.|…)\s*\]|\.\.\.|…)\s*", passage):
        sentences += ts.split_sentences(piece)
    return [s for s in sentences if len(ts.words(s)) >= MIN_SENTENCE_WORDS]


class Revision:
    def __init__(self, units: list[Unit]):
        self.units = units
        self.sentences = []
        for unit in units:
            for sentence in ts.split_sentences(unit.text):
                normal = normalize(sentence)
                if normal:
                    self.sentences.append((sentence, normal, set(normal.split()), unit))

    def find(self, sentence: str) -> tuple[Sentence, list[Unit]]:
        target = normalize(sentence)
        bounded = re.compile(r"(?<![\w.])" + re.escape(target) + r"(?![\w]|\.\d)") if target else None
        hits = [u for u in self.units if bounded and bounded.search(u.normalized)]
        if hits:
            return Sentence(sentence, "found", hits[0].location, similarity=1.0), hits
        words = set(target.split())
        best, best_unit, best_ratio = "", None, 0.0
        for candidate, normal, candidate_words, unit in self.sentences:
            if len(words & candidate_words) < SHARED_WORDS * max(len(words), 1):
                continue
            ratio = difflib.SequenceMatcher(None, target, normal, autojunk=False).ratio()
            if ratio > best_ratio:
                best, best_unit, best_ratio = candidate, unit, ratio
        if best_unit is not None and best_ratio >= SIMILAR:
            return Sentence(sentence, "differs", best_unit.location, best, round(best_ratio, 2)), [best_unit]
        return Sentence(sentence, "missing", closest=best, similarity=round(best_ratio, 2)), []


def check_place(named: str, located: list[list[Unit]]) -> str:
    """Compare the section, table or figure named with where the sentences were found."""
    located = [units for units in located if units]
    if not named or not located:
        return ""
    notes, unchecked = [], []
    for part in named.split("; "):
        if re.search(r"(?:table|figure) s?\d+$", part):
            away = sum(not any(u.display == part for u in units) for units in located)
            if away:
                notes.append(f"{away} of {len(located)} sentence(s) found outside {part}")
        elif part in SECTIONS.values():
            away = [units for units in located if not any(u.section == part for u in units)]
            if away:
                where = sorted({u.section or "no section" for units in away for u in units})
                notes.append(f"{len(away)} of {len(located)} sentence(s) found in {', '.join(where)}, not {part}")
        else:
            unchecked.append(part)
    if unchecked:
        notes.append(f"{', '.join(unchecked)}: not checked, as pages and lines depend on the layout")
    return "; ".join(notes) if notes else "matches"


def check(letter: Path, revisions: list[Path]) -> dict:
    revision = Revision(revision_units(revisions))
    passages, skipped = letter_passages(letter)
    results = []
    for where, comment, named, text in passages:
        passage, located = Passage(where, comment, named), []
        for sentence in _fragments(text):
            result, units = revision.find(sentence)
            passage.sentences.append(result)
            located.append(units)
        if passage.sentences:
            passage.place_check = check_place(named, located)
            results.append(passage)
    counts = {status: sum(s.status == status for p in results for s in p.sentences)
              for status in ("found", "differs", "missing")}
    misplaced = sum(" found " in p.place_check for p in results)
    return {"letter": str(letter), "revision": [str(p) for p in revisions], "passages": [asdict(p) for p in results],
            "counts": counts, "misplaced": misplaced, "not_marked_as_new": skipped}


def print_report(report: dict, out) -> None:
    print(f"\n{report['letter']} against {', '.join(report['revision'])}", file=out)
    for passage in report["passages"]:
        head = f"  {passage['letter_location']}"
        if passage["comment"]:
            head += f" ({passage['comment']})"
        if passage["named_place"]:
            head += f", names {passage['named_place']}"
        print(head, file=out)
        for s in passage["sentences"]:
            where = f" at {s['found_at']}" if s["found_at"] else ""
            print(f"    {s['status']:<8} “{s['text'][:110]}”{where}", file=out)
            if s["status"] != "found" and s["closest"]:
                print(f"             closest ({s['similarity']}): “{s['closest'][:110]}”", file=out)
        if passage["place_check"] and passage["place_check"] != "matches":
            print(f"    place: {passage['place_check']}", file=out)
    if report["not_marked_as_new"]:
        print("  Quotations not marked as new text, so not checked:", file=out)
        for item in report["not_marked_as_new"]:
            print(f"    {item}", file=out)
    c = report["counts"]
    if not report["passages"]:
        print("\nNo passage of new text was found in the letter.", file=out)
        return
    print(f"\n{c['found']} sentence(s) found, {c['differs']} differ, {c['missing']} missing; "
          f"{report['misplaced']} passage(s) found away from the place named.", file=out)


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("letter", type=Path, help="response letter")
    parser.add_argument("revision", type=Path, nargs="+", help="revised manuscript, then any supplement")
    parser.add_argument("--json", action="store_true", help="print JSON")
    args = parser.parse_args(argv)
    for path in (args.letter, *args.revision):
        if not path.exists():
            parser.error(f"no such file: {path}")
    report = check(args.letter, args.revision)
    if args.json:
        json.dump(report, sys.stdout, ensure_ascii=False, indent=1)
        print()
    else:
        print_report(report, sys.stdout)
    c = report["counts"]
    return 1 if c["differs"] or c["missing"] or report["misplaced"] else 0


if __name__ == "__main__":
    for stream in (sys.stdout, sys.stderr):
        if hasattr(stream, "reconfigure"):
            stream.reconfigure(encoding="utf-8")
    raise SystemExit(main())
