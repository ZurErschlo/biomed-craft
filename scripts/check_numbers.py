#!/usr/bin/env python3
"""Check that the numbers in a manuscript agree with each other.

Finds three kinds of problem, without changing any file:

  - a percentage that does not match its count and denominator
    ("482 of 2104 patients (25.9%)", "49 (2%) of 2609", "13/40 (35%)");
  - a point estimate outside its confidence interval, an interval whose
    bounds are reversed, or a ratio interval that reaches zero or below;
  - a number in the abstract or summary that appears nowhere else in the text.

Reads the same formats as scan.py (Markdown, Word, LaTeX, PDF and others).
Lancet mid-dot decimals and space or comma thousands separators are understood.

Examples:
  python3 check_numbers.py manuscript.docx
  python3 check_numbers.py --strict --json draft.md
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from dataclasses import asdict, dataclass
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import textstats as ts  # noqa: E402

NUMBER = r"\d{1,3}(?:[,   ]\d{3})+(?![\d·.])|\d+(?:[.·]\d+)?"
COUNT_OF = re.compile(
    rf"(?P<n>{NUMBER})\s*(?:/|of)\s*(?P<N>{NUMBER})\b(?:\s+[A-Za-z-]+){{0,3}}\s*\(\s*(?P<p>\d+(?:[.·]\d+)?)\s*%\s*[),;]"
)
COUNT_PCT_OF = re.compile(
    rf"(?P<n>{NUMBER})\s*\(\s*(?P<p>\d+(?:[.·]\d+)?)\s*%\s*\)\s*of\s+(?:the\s+)?(?P<N>{NUMBER})\b"
)
OF_TOTAL = re.compile(
    rf"\b[Oo]f\s+(?:the\s+)?(?P<N>{NUMBER})(?:\s+[A-Za-z-]+){{0,3}},\s+(?P<n>{NUMBER})(?:\s+[A-Za-z-]+){{0,2}}"
    rf"\s*\(\s*(?P<p>\d+(?:[.·]\d+)?)\s*%\s*\)"
)
INTERVAL = re.compile(
    rf"(?P<label>\b(?:[AaIi]?(?:OR|HR|RR|IRR|SHR)|odds ratio|hazard ratio|risk ratio|rate ratio|ratio)\b"
    rf"(?:\s+(?:was|were|is|of))?[\s,:=]*)?"
    rf"(?P<est>-?{NUMBER})(?![\d·.])\s*[,;]?\s*\(?\s*(?:95%\s*(?:CI|confidence interval|UI|uncertainty interval|CrI|credible interval)"
    rf"\s*(?:\[\w+\])?[\s,:]*)?(?P<low>[-−–]?{NUMBER})\s*(?:to|–|-(?=\d))\s*(?P<high>[-−–]?{NUMBER})\s*\)"
)
ABSTRACT_HEADING = re.compile(r"^(?:abstract|summary)$", re.IGNORECASE)
ABSTRACT_LABEL = re.compile(r"^\s*(?:abstract|summary)\s*[:.]\s*", re.IGNORECASE)
TRIVIAL = re.compile(r"^(?:\d|1\d|95|100|19\d\d|20\d\d)$")


@dataclass
class Problem:
    kind: str
    line: int
    match: str
    message: str


def to_float(text: str) -> float:
    text = text.replace("−", "-").replace("–", "-").replace("·", ".")
    return float(re.sub(r"[,   ]", "", text))


def decimals(text: str) -> int:
    text = text.replace("·", ".")
    return len(text.split(".")[1]) if "." in text else 0


def percentage_problems(text: str, line: int) -> list[Problem]:
    found = []
    for pattern in (COUNT_OF, COUNT_PCT_OF, OF_TOTAL):
        for match in pattern.finditer(text):
            n, total, shown = to_float(match["n"]), to_float(match["N"]), to_float(match["p"])
            if total <= 0 or n > total:
                continue
            exact = 100 * n / total
            tolerance = 0.5 * 10 ** -decimals(match["p"]) + 1e-9
            if abs(exact - shown) > tolerance:
                found.append(Problem("percentage", line, match.group(0),
                                     f"{match['n']} of {match['N']} is {exact:.{max(decimals(match['p']), 1)}f}%, "
                                     f"not {match['p']}%"))
    return found


def interval_problems(text: str, line: int) -> list[Problem]:
    found = []
    for match in INTERVAL.finditer(text):
        try:
            estimate, low, high = to_float(match["est"]), to_float(match["low"]), to_float(match["high"])
        except ValueError:
            continue
        if low > high:
            found.append(Problem("interval", line, match.group(0), "the lower bound is above the upper bound"))
        elif not low <= estimate <= high:
            found.append(Problem("interval", line, match.group(0), "the estimate lies outside its interval"))
        elif match["label"] and low <= 0:
            found.append(Problem("interval", line, match.group(0), "a ratio interval cannot reach zero"))
    return found


def numbers_in(text: str) -> set[str]:
    return {to_float(n).__repr__() for n in re.findall(NUMBER, text) if not TRIVIAL.match(n)}


def abstract_problems(segments: list[ts.Segment]) -> list[Problem]:
    """Numbers in the abstract that appear nowhere else in the document."""
    abstract, rest, inside = [], [], False
    for segment in segments:
        heading = segment.text.strip().strip("#").strip()
        if len(heading) < 30 and ABSTRACT_HEADING.match(heading):
            inside = True
            continue
        if ABSTRACT_LABEL.match(segment.text):  # an inline "Abstract:" paragraph
            abstract.append(segment)
            inside = False
            continue
        if inside and len(heading) < 60 and not heading.endswith(".") and len(heading.split()) <= 6:
            inside = False
        (abstract if inside else rest).append(segment)
    if not abstract or not rest:
        return []
    elsewhere = set()
    for segment in rest:
        elsewhere |= numbers_in(segment.text)
    found = []
    for segment in abstract:
        for raw in re.findall(NUMBER, segment.text):
            if TRIVIAL.match(raw) or to_float(raw).__repr__() in elsewhere:
                continue
            found.append(Problem("abstract", segment.line, raw, "appears in the abstract but nowhere else"))
    return found


def check_file(path: Path) -> dict:
    segments = ts.read_segments(path)
    problems: list[Problem] = []
    for segment in segments:
        if segment.scope in ("prose", "caption", "table", "slide"):
            problems += percentage_problems(segment.text, segment.line)
            problems += interval_problems(segment.text, segment.line)
    problems += abstract_problems([s for s in segments if s.scope in ("prose", "caption", "table")])
    return {"file": str(path), "problems": [asdict(p) for p in problems]}


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("paths", nargs="+", type=Path, help="manuscript files")
    parser.add_argument("--json", action="store_true", help="print JSON")
    parser.add_argument("--strict", action="store_true", help="exit with status 1 if any problem is found")
    args = parser.parse_args(argv)
    results = []
    for path in args.paths:
        if not path.exists():
            parser.error(f"no such file: {path}")
        results.append(check_file(path))
    total = sum(len(r["problems"]) for r in results)
    if args.json:
        json.dump({"files": results, "problems": total}, sys.stdout, ensure_ascii=False, indent=1)
        print()
    else:
        for result in results:
            print(f"\n{result['file']}")
            for p in result["problems"]:
                print(f"  {p['kind']:<10} line {p['line']}: {p['match']!r}: {p['message']}")
        print(f"\n{total} number problem(s) across {len(results)} file(s).")
    return 1 if (args.strict and total) else 0


if __name__ == "__main__":
    for stream in (sys.stdout, sys.stderr):
        if hasattr(stream, "reconfigure"):
            stream.reconfigure(encoding="utf-8")
    raise SystemExit(main())
