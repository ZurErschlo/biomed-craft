#!/usr/bin/env python3
"""Check that an edit kept the facts: numbers, citations, cross-references and links.

Compares an original and a revised file (any format scan.py reads) and lists
numbers, citation keys, figure, table and appendix references, DOIs and URLs
that were dropped or added. Journal number styles are normalised first, so
0·72 and 0.72, or 10 000 and 10,000, count as the same number. Changes in
negations and hedges are reported as notes, because removing a stacked hedge
is often the point of the edit.

Examples:
  python3 check_preservation.py draft.docx revised.docx
  python3 check_preservation.py --json before.md after.md

Exit status: 0 when nothing was lost or added, 1 otherwise, 2 for usage errors.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
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


def read_text(path: Path) -> str:
    """Raw text for LaTeX and Markdown (citation keys survive); segment text otherwise."""
    if path.suffix.lower() in (".tex", ".md", ".markdown", ".qmd", ".rmd", ".txt"):
        return path.read_text(encoding="utf-8", errors="replace")
    return "\n".join(s.text for s in ts.read_segments(path) if s.scope != "figure")


def normalise_number(token: str) -> str:
    token = token.replace("·", ".").replace("−", "-").replace("–", "-").replace(" ", "")
    if token.startswith("."):
        token = "0" + token
    elif token.startswith("-."):
        token = "-0" + token[1:]
    return token


def numbers(text: str) -> Counter:
    text = THOUSANDS.sub(lambda m: re.sub(r"[,\u2009\u202f ]", "", m.group(0)), text)
    return Counter(normalise_number(m.group(0)) for m in NUMBER.finditer(text))


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


def compare(original: str, revised: str) -> dict:
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
    report["notes"] = {
        "negations": [len(NEGATION.findall(original)), len(NEGATION.findall(revised))],
        "hedges": [len(HEDGE.findall(original)), len(HEDGE.findall(revised))],
    }
    report["ok"] = all(not v["missing"] and not v["added"] for k, v in report.items() if k not in ("notes", "ok"))
    return report


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("original", type=Path)
    parser.add_argument("revised", type=Path)
    parser.add_argument("--json", action="store_true", help="print JSON")
    args = parser.parse_args(argv)
    for path in (args.original, args.revised):
        if not path.exists():
            parser.error(f"no such file: {path}")
    report = compare(read_text(args.original), read_text(args.revised))
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
