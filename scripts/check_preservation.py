#!/usr/bin/env python3
"""Check that an edit kept the facts: numbers, citations, cross-references and links.

Compares an original and a revised file (any format scan.py reads) and lists
numbers, citation keys, figure, table and appendix references, DOIs and URLs
that were dropped or added. Journal number styles are normalized first, so
0·72 and 0.72, or 10 000 and 10,000, count as the same number.

It also lists:
  - sentences that moved from association to effect ("was associated with
    lower mortality" became "reduced mortality"). Causal wording is expected
    in randomized trials, so these are not checked for trials, and for
    meta-analyses of randomized trials unless --journal JAMA is given;
    "predicts" counts only outside prediction studies;
  - for Word files, EndNote and Zotero citation fields that disappeared;
  - for a Word revision with tracked changes, whether rejecting every change
    gives the original text and, with --accepted, whether accepting every
    change gives the intended revision.

Changes in negations and hedges are reported as notes, because removing a
stacked hedge is often the point of the edit.

Examples:
  python3 check_preservation.py draft.docx revised.docx
  python3 check_preservation.py --json before.md after.md
  python3 check_preservation.py --accepted clean.docx original.docx tracked.docx

Exit status: 0 when nothing was lost or added, 1 otherwise, 2 for usage errors.
"""

from __future__ import annotations

import argparse
import base64
import binascii
import difflib
import json
import re
import sys
import xml.etree.ElementTree as ET
import zipfile
from collections import Counter
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import textstats as ts  # noqa: E402

THOUSANDS = re.compile(r"(?<![\d.·])(\d{1,3})(?:(?:,|\u2009|\u202f| )(\d{3}))+(?![\d.·]|,\d)")
NUMBER = re.compile(r"(?<![\w.·])[-−–]?(?:\d+(?:[.·]\d+)?|[.·]\d+)(?:\s?%)?")
CITE_TEX = re.compile(r"\\cite[tp]?\*?(?:\[[^\]]*\])*\{([^}]*)\}")
CITE_PANDOC = re.compile(r"@([A-Za-z][\w:.-]*)")
CITE_NUMERIC = re.compile(r"\[(\d+(?:\s*[,–-]\s*\d+)*)\]")
REF_TEX = re.compile(r"\\(?:ref|eqref|autoref|cref|Cref|label)\{([^}]*)\}")
CROSS_REF = re.compile(
    r"\b(Extended\s+Data\s+(?:Fig\.?|Figure|Table)|Supplementary\s+(?:Fig\.?|Figure|Table|Data|Note)|eFigure|eTable|eAppendix"
    r"|Figure|Figs?\.?|Table|appendix\s+pp?)\s*(S?\d+[A-Za-z]?(?:\s*[,–-]\s*S?\d+[A-Za-z]?)*)",
    re.IGNORECASE,
)
DOI = re.compile(r"\b10\.\d{4,9}/[^\s\"<>,;]+")
URL = re.compile(r"https?://[^\s\"<>]+")
NEGATION = re.compile(r"\b(?:not|no|never|none|neither|nor|without|cannot|n't)\b", re.IGNORECASE)
HEDGE = re.compile(r"\b(?:may|might|could|possibly|probably|likely|perhaps|suggest(?:s|ed)?|appears?)\b", re.IGNORECASE)


# Causal wording, and the association wording it replaces. 'effect' excludes statistical terms
# (fixed effects, effect size, side effects, effect modification).
CAUSAL = re.compile(
    r"\b(?:caus(?:e|es|ed|ing|al(?:ly)?)|(?<!side )(?<!adverse )(?<!fixed )(?<!random )(?<!mixed )(?<!main )"
    r"effects? (?:of|on)|impact(?:s|ed)?|improv(?:e|es|ed|ing)|reduc(?:e|es|ed|ing)|lower(?:s|ed)|rais(?:e|es|ed)"
    r"|increas(?:e|es|ed)|prevent(?:s|ed|ing)?|protect(?:s|ed|ive)|leads? to|led to|result(?:s|ed)? in|efficacy"
    r"|effective(?:ness)?|benefit(?:s|ed)? from|attributable to|due to|driv(?:e|es|en)|contribut(?:e|es|ed) to)\b",
    re.IGNORECASE)
PREDICTIVE = re.compile(r"\bpredict(?:s|ed|ive)?\b", re.IGNORECASE)
ASSOCIATION = re.compile(r"\b(?:associat(?:ed|ion|ions)|linked|correlat(?:ed|ion|es)|related to|was higher|was lower"
                         r"|were higher|were lower|odds|risk of|coincided)\b", re.IGNORECASE)
RCT_EVIDENCE = re.compile(r"\b(?:randomi[sz]ed (?:controlled |clinical )?trials|RCTs)\b", re.IGNORECASE)
NON_RANDOMIZED = re.compile(r"\b(?:observational|cohort|case-control|cross-sectional|non-?randomi[sz]ed)\b", re.IGNORECASE)
# 'associated with reduced mortality': the causal word is qualified by the association, so dropping the
# association strengthens the claim even though 'reduced' was already in the sentence.
QUALIFIED = re.compile(f"({ASSOCIATION.pattern})((?:\\W+\\w+){{0,3}}?\\W+)({CAUSAL.pattern})", re.IGNORECASE)
MATCH_RATIO = 0.6  # overlap of the other words above which a revised sentence counts as the rewrite of an original one


def causal_allowed(original: str, design: str, journal: str) -> bool:
    """Randomized trials may use causal language. JAMA asks meta-analyses of randomized trials for associational
    language too; other journals accept causal wording there."""
    if design == "trial":
        return True
    if design == "systematic-review" and journal.lower() != "jama":
        return bool(RCT_EVIDENCE.search(original)) and not NON_RANDOMIZED.search(original)
    return False


FILLER = re.compile(r"\b(?:was|were|is|are|has|have|been|with|the|a|an|to|of)\b", re.IGNORECASE)


def _sentences(text: str) -> list[str]:
    return [re.sub(r"\s+", " ", text[a:b]).strip() for a, b in ts.sentence_spans(text)]


def _core_words(sentence: str) -> list[str]:
    """The words left once the claim wording is taken out, so a rewrite of a short sentence still matches."""
    return FILLER.sub(" ", PREDICTIVE.sub(" ", CAUSAL.sub(" ", ASSOCIATION.sub(" ", sentence)))).lower().split()


def claim_changes(original: str, revised: str, design: str = "", journal: str = "") -> list[dict]:
    """Revised sentences that gained causal wording while losing the association wording of the sentence they
    rewrite. 'predicts' counts as a stronger claim except in prediction studies."""
    if causal_allowed(original, design, journal):
        return []
    patterns = [CAUSAL] + ([] if design == "prediction" else [PREDICTIVE])
    candidates = [(s, _core_words(s)) for s in _sentences(original) if ASSOCIATION.search(s)]
    changes = []
    for sentence in _sentences(revised):
        terms = [m.group(0).lower() for pattern in patterns for m in pattern.finditer(sentence)]
        if not terms or not candidates:
            continue
        matcher = difflib.SequenceMatcher(None, _core_words(sentence), autojunk=False)
        best, best_ratio = None, MATCH_RATIO
        for source, source_words in candidates:
            matcher.set_seq2(source_words)
            if matcher.real_quick_ratio() > best_ratio and matcher.quick_ratio() > best_ratio:
                ratio = matcher.ratio()
                if ratio > best_ratio:
                    best, best_ratio = source, ratio
        if best is None:
            continue
        unqualified = QUALIFIED.sub(lambda m: m.group(1) + m.group(2), best).lower()
        gained = [term for term in terms if term not in unqualified]
        if gained and len(ASSOCIATION.findall(sentence)) < len(ASSOCIATION.findall(best)):
            changes.append({"original": best, "revised": sentence, "terms": sorted(set(gained))})
    return changes


# ---------------------------------------------------------------------------
# Word files: citation fields and tracked changes
# ---------------------------------------------------------------------------

W = "{http://schemas.openxmlformats.org/wordprocessingml/2006/main}"
INSERTED, DELETED = (W + "ins", W + "moveTo"), (W + "del", W + "moveFrom")
REC_NUM = re.compile(r"<RecNum>(\d+)</RecNum>")
ZOTERO_JSON = re.compile(r"CSL_CITATION\s*(\{.*\})\s*$", re.DOTALL)


def _document(path: Path) -> ET.Element:
    with zipfile.ZipFile(path) as archive:
        return ET.fromstring(archive.read("word/document.xml"))


def _parts(path: Path) -> list[ET.Element]:
    """The body, then the footnotes and endnotes, which hold citation fields too."""
    with zipfile.ZipFile(path) as archive:
        names = set(archive.namelist())
        return [ET.fromstring(archive.read(name)) for name in
                ("word/document.xml", "word/footnotes.xml", "word/endnotes.xml") if name in names]


def _field_data(begin: ET.Element) -> str:
    """The text EndNote stores, base64-encoded, in w:fldData at the start of a field. A citation of several
    references, or one with a long record, keeps its record numbers there and only `ADDIN EN.CITE` in the
    instruction."""
    data = begin.find(W + "fldData")
    if data is None or not (data.text or "").strip():
        return ""
    try:
        raw = base64.b64decode(re.sub(r"\s+", "", data.text), validate=True)
    except (binascii.Error, ValueError):
        return ""
    if raw[:2] in (b"\xff\xfe", b"\xfe\xff"):
        return raw.decode("utf-16", errors="replace")
    return raw.decode("utf-8", errors="replace")


def _field_key(instruction: str, data: str = "") -> str | None:
    """'EndNote 12,30' or 'Zotero 4,9' from a citation field's instruction and stored data; None for other fields."""
    instruction = instruction.strip()
    if instruction.startswith("ADDIN EN.CITE") and not instruction.startswith("ADDIN EN.CITE.DATA"):
        records = list(dict.fromkeys(REC_NUM.findall(instruction) + REC_NUM.findall(data)))
        return "EndNote " + (",".join(records) if records else "(no record number)")
    if instruction.startswith("ADDIN ZOTERO_ITEM"):
        found = ZOTERO_JSON.search(instruction)
        try:
            data = json.loads(found.group(1)) if found else {}
        except json.JSONDecodeError:
            data = {}
        items = [str(item.get("id") or (item.get("uris") or ["?"])[0]) for item in data.get("citationItems", [])]
        return "Zotero " + (",".join(items) if items else data.get("citationID", "(no item)"))
    return None


def citation_fields(path: Path) -> list[tuple[str, str]]:
    """(key, displayed text) for every EndNote and Zotero citation field in the accepted text of a Word file,
    footnotes and endnotes included."""
    fields: list[tuple[str, str]] = []
    stack: list[dict] = []

    def walk(node: ET.Element) -> None:
        if node.tag in DELETED:
            return
        if node.tag == W + "fldChar":
            kind = node.get(W + "fldCharType")
            if kind == "begin":
                stack.append({"instruction": [], "shown": [], "result": False, "data": _field_data(node)})
            elif kind == "separate" and stack:
                stack[-1]["result"] = True
            elif kind == "end" and stack:
                field = stack.pop()
                key = _field_key("".join(field["instruction"]), field["data"])
                if key:
                    fields.append((key, "".join(field["shown"]).strip()))
        elif node.tag == W + "instrText" and stack and not stack[-1]["result"]:
            stack[-1]["instruction"].append(node.text or "")
        elif node.tag == W + "t":
            for field in stack:
                if field["result"]:
                    field["shown"].append(node.text or "")
        elif node.tag == W + "fldSimple":
            key = _field_key(node.get(W + "instr") or "")
            if key:
                fields.append((key, "".join(t.text or "" for t in node.iter(W + "t")).strip()))
            return
        for child in node:
            walk(child)

    for part in _parts(path):
        walk(part)
    return fields


def compare_fields(original: Path, revised: Path) -> dict:
    before, after = citation_fields(original), citation_fields(revised)
    lost = Counter(key for key, _ in before) - Counter(key for key, _ in after)
    added = Counter(key for key, _ in after) - Counter(key for key, _ in before)
    shown = dict(before + after)
    describe = lambda key: f"{key} (shown as {shown[key]!r})" if shown.get(key) else key
    return {"counts": [len(before), len(after)], "missing": sorted(describe(k) for k in lost.elements()),
            "added": sorted(describe(k) for k in added.elements())}


def tracked_views(path: Path) -> dict:
    """The text with every tracked change accepted and with every change rejected, and who made the changes."""
    accepted: list[str] = []
    rejected: list[str] = []
    authors: Counter = Counter()

    def walk(node: ET.Element, inserted: bool, deleted: bool) -> None:
        if node.tag in INSERTED + DELETED:
            authors[node.get(W + "author") or "(unknown)"] += 1
            inserted = inserted or node.tag in INSERTED
            deleted = deleted or node.tag in DELETED
        if node.tag in (W + "t", W + "delText") and node.text:
            if not deleted:
                accepted.append(node.text)
            if not inserted:
                rejected.append(node.text)
        elif node.tag in (W + "tab", W + "br", W + "p"):
            accepted.append(" ")
            rejected.append(" ")
        for child in node:
            walk(child, inserted, deleted)

    walk(_document(path), False, False)
    squash = lambda parts: re.sub(r"\s+", " ", "".join(parts)).strip()
    return {"accepted": squash(accepted), "rejected": squash(rejected), "authors": authors}


def first_difference(expected: str, actual: str) -> str:
    """The first place two texts part, with a little context on each side."""
    matcher = difflib.SequenceMatcher(None, expected, actual, autojunk=False)
    for tag, a1, a2, b1, b2 in matcher.get_opcodes():
        if tag != "equal":
            return (f"expected {expected[max(0, a1 - 30):a2 + 30]!r}, found {actual[max(0, b1 - 30):b2 + 30]!r}")
    return ""


def compare_tracked(original: Path, revised: Path, accepted: Path | None = None) -> dict | None:
    """Rejecting every change in the revision gives the original (its own tracked changes rejected too);
    accepting every change gives the intended revision. None when the revision has no tracked changes and no
    intended revision is given; with one, a revision without tracked changes is still compared."""
    after = tracked_views(revised)
    if not after["authors"] and accepted is None:
        return None
    before = tracked_views(original)
    report = {"changes": sum(after["authors"].values()), "reject_all_gives_original": after["rejected"] == before["rejected"],
              "difference": first_difference(before["rejected"], after["rejected"])}
    if accepted is not None:
        clean = (tracked_views(accepted)["accepted"] if accepted.suffix.lower() == ".docx"
                 else re.sub(r"\s+", " ", read_text(accepted)).strip())
        report["accept_all_gives_revision"] = after["accepted"] == clean
        report["accept_difference"] = first_difference(clean, after["accepted"])
    report["authors_with_fewer_changes"] = sorted(a for a, n in before["authors"].items() if after["authors"][a] < n)
    return report


def read_text(path: Path) -> str:
    """Raw text for LaTeX and Markdown (citation keys survive); segment text otherwise."""
    if path.suffix.lower() in (".tex", ".md", ".markdown", ".qmd", ".rmd", ".txt"):
        return path.read_text(encoding="utf-8", errors="replace")
    return "\n".join(s.text for s in ts.read_segments(path) if s.scope != "figure")


def normalize_number(token: str) -> str:
    token = token.replace("·", ".").replace("−", "-").replace("–", "-").replace(" ", "")
    if token.startswith("."):
        token = "0" + token
    elif token.startswith("-."):
        token = "-0" + token[1:]
    return token


def numbers(text: str) -> Counter:
    text = THOUSANDS.sub(lambda m: re.sub(r"[,\u2009\u202f ]", "", m.group(0)), text)
    return Counter(normalize_number(m.group(0)) for m in NUMBER.finditer(text))


def citations(text: str) -> Counter:
    keys: list[str] = []
    for match in CITE_TEX.finditer(text):
        keys.extend(k.strip() for k in match.group(1).split(","))
    keys.extend(m.group(1) for m in CITE_PANDOC.finditer(text) if "." not in m.group(1)[-1:])
    keys.extend("[" + re.sub(r"\s+", "", m.group(1)) + "]" for m in CITE_NUMERIC.finditer(text))
    return Counter(keys)


def cross_references(text: str) -> Counter:
    items = [m.group(1) for m in REF_TEX.finditer(text)]
    for match in CROSS_REF.finditer(text):
        label = re.sub(r"\s+", " ", match.group(1).lower()).replace("figs", "fig").replace("figure", "fig").rstrip(".")
        number = re.sub(r"\s+", "", match.group(2)).upper()
        items.append(f"{label} {number}")
    return Counter(items)


def _trim_link(link: str) -> str:
    link = link.rstrip(".,;:")
    while link.endswith(")") and link.count(")") > link.count("("):
        link = link[:-1].rstrip(".,;:")
    return link.lower()


def links(text: str) -> Counter:
    return Counter([_trim_link(d) for d in DOI.findall(text)] + [_trim_link(u) for u in URL.findall(text)])


def without_links(text: str) -> str:
    """Drop links and bracketed citation numbers so their digits are not read as data."""
    return CITE_NUMERIC.sub(" ", DOI.sub(" ", URL.sub(" ", text)))


def compare(original: str, revised: str, design: str = "", journal: str = "") -> dict:
    report = {}
    for name, extractor in (("numbers", numbers), ("citations", citations),
                            ("cross_references", cross_references), ("links", links)):
        source_before = without_links(original) if name == "numbers" else original
        source_after = without_links(revised) if name == "numbers" else revised
        before, after = extractor(source_before), extractor(source_after)
        report[name] = {
            "missing": sorted((before - after).elements()),
            "added": sorted((after - before).elements()),
        }
    report["claims"] = claim_changes(original, revised, design, journal)
    report["notes"] = {
        "negations": [len(NEGATION.findall(original)), len(NEGATION.findall(revised))],
        "hedges": [len(HEDGE.findall(original)), len(HEDGE.findall(revised))],
    }
    report["ok"] = not report["claims"] and all(
        not report[k]["missing"] and not report[k]["added"] for k in ("numbers", "citations", "cross_references", "links"))
    return report


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("original", type=Path)
    parser.add_argument("revised", type=Path)
    parser.add_argument("--json", action="store_true", help="print JSON")
    parser.add_argument("--design", choices=ts.DESIGNS, help="study design (default: detected from the original)")
    parser.add_argument("--journal", default="", help="target journal; JAMA also checks meta-analyses of trials")
    parser.add_argument("--accepted", type=Path, metavar="FILE",
                        help="the intended revision, to compare with the tracked revision once every change is accepted")
    args = parser.parse_args(argv)
    for path in (args.original, args.revised) + ((args.accepted,) if args.accepted else ()):
        if not path.exists():
            parser.error(f"no such file: {path}")
    original_text = read_text(args.original)
    design = args.design or ts.detect_design(original_text)[0]
    report = compare(original_text, read_text(args.revised), design, args.journal)
    report["design"] = design
    word = args.original.suffix.lower() == ".docx" and args.revised.suffix.lower() == ".docx"
    if word:
        report["citation_fields"] = compare_fields(args.original, args.revised)
        report["tracked_changes"] = compare_tracked(args.original, args.revised, args.accepted)
        fields, tracked = report["citation_fields"], report["tracked_changes"]
        if fields["missing"] or fields["added"]:
            report["ok"] = False
        if tracked and (not tracked["reject_all_gives_original"] or tracked.get("accept_all_gives_revision") is False):
            report["ok"] = False
    elif args.accepted:
        parser.error("--accepted needs Word files for the original and the revision")
    if args.json:
        json.dump(report, sys.stdout, ensure_ascii=False, indent=1)
        print()
    else:
        labels = {"numbers": "Numbers", "citations": "Citations", "cross_references": "Figure, table and appendix references",
                  "links": "DOIs and URLs"}
        for key, label in labels.items():
            missing, added = report[key]["missing"], report[key]["added"]
            if missing or added:
                print(f"{label}:")
                if missing:
                    print(f"  missing in revision: {', '.join(missing)}")
                if added:
                    print(f"  new in revision:     {', '.join(added)}")
        if report["claims"]:
            print("Claims moved from association to effect (check that the design supports them):")
            for claim in report["claims"]:
                print(f"  was: {claim['original']}\n  now: {claim['revised']}  [{', '.join(claim['terms'])}]")
        fields = report.get("citation_fields")
        if fields:
            print(f"Citation fields: {fields['counts'][0]} -> {fields['counts'][1]}")
            for key, label in (("missing", "missing in revision"), ("added", "new in revision")):
                if fields[key]:
                    print(f"  {label}: {'; '.join(fields[key])}")
        tracked = report.get("tracked_changes")
        if tracked:
            print(f"Tracked changes: {tracked['changes']}; rejecting all gives the original: "
                  f"{'yes' if tracked['reject_all_gives_original'] else 'no, ' + tracked['difference']}")
            if "accept_all_gives_revision" in tracked:
                print("  accepting all gives the revision: "
                      f"{'yes' if tracked['accept_all_gives_revision'] else 'no, ' + tracked['accept_difference']}")
            if tracked["authors_with_fewer_changes"]:
                print(f"  fewer tracked changes than before by: {', '.join(tracked['authors_with_fewer_changes'])}")
        negations, hedges = report["notes"]["negations"], report["notes"]["hedges"]
        print(f"Negations: {negations[0]} -> {negations[1]}; hedges: {hedges[0]} -> {hedges[1]} "
              "(check that no real uncertainty or negation was lost)")
        print("Facts preserved." if report["ok"] else "Check the items above before accepting the revision.")
    return 0 if report["ok"] else 1


if __name__ == "__main__":
    for stream in (sys.stdout, sys.stderr):
        if hasattr(stream, "reconfigure"):
            stream.reconfigure(encoding="utf-8")
    raise SystemExit(main())
