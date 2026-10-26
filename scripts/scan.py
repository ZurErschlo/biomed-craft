#!/usr/bin/env python3
"""Check English academic text for AI tells, internal material and style drift.

Reads Markdown, Quarto, R Markdown, LaTeX, Word (.docx), PowerPoint (.pptx),
PDF (with pdftotext), SVG, and R or Python plotting code, and reports findings
by rule. It never edits files. Rules live in rules.json; reference rates from
flagship-journal research articles live in calibration.json.

Examples:
  python3 scan.py manuscript.docx
  python3 scan.py --profile --journal lancet draft.md
  python3 scan.py --strict figures/*.R legends.md
  python3 scan.py --doc response response_letter.docx
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

SUFFIXES = {".md", ".markdown", ".txt", ".text", ".qmd", ".rmd", ".tex", ".docx", ".pptx", ".pdf", ".svg", ".r", ".py"}
DOC_TYPES = ("manuscript", "response", "protocol", "slides")
LEVELS = ("must", "review", "density")
STACK_OPENER = re.compile(
    r"^(?:Moreover|Furthermore|Additionally|In addition|Notably|Importantly|Interestingly|Crucially|Collectively|Remarkably),"
)
FIGURE_LEVEL_ROLES = {"subtitle", "caption", "sub"}
FIGURE_LEVEL_FUNCTIONS = {"plot_annotation", "suptitle"}
TITLE_ROLES = {"title", "main"}
TITLE_FUNCTIONS = {"ggtitle", "set_title", "title"}
DENSITY_LABELS = {
    "contrast_per_1000": "Contrast frames (rather than, not … but, instead of)",
    "ai_signposts_per_1000": "Openers such as Moreover, Notably, Importantly",
    "em_dash_per_1000": "Em dashes",
    "hedges_per_1000": "Hedges (may, might, could, likely, suggest)",
}
PROFILE_LABELS = {
    "sentence_median": "Median sentence length (words)",
    "share_over_35": "Share of sentences over 35 words",
    "share_under_10": "Share of sentences under 10 words",
    "we_per_1000": "we/our/us per 1000 words",
    "passive_share": "Share of sentences with a passive",
    "hedges_per_1000": "Hedges per 1000 words",
    "contrast_per_1000": "Contrast frames per 1000 words",
    "ai_signposts_per_1000": "Moreover/Notably-type openers per 1000 words",
    "however_per_1000": "'However,' openers per 1000 words",
    "em_dash_per_1000": "Em dashes per 1000 words",
    "semicolons_per_1000": "Semicolons per 1000 words",
}


@dataclass
class Finding:
    rule: str
    level: str
    category: str
    file: str
    line: int
    scope: str
    source: str
    match: str
    context: str
    hint: str
    count: int = 1


def _excerpt(text: str, limit: int = 160) -> str:
    text = re.sub(r"\s+", " ", text).strip()
    return text if len(text) <= limit else text[: limit - 1] + "…"


def _figure_role(source: str) -> tuple[str, str]:
    match = re.match(r"([\w.]+)\((.*)\)", source)
    return (match.group(1), match.group(2)) if match else (source, "")


def figure_findings(segment: ts.Segment, rules_by_id: dict[str, ts.Rule], label: str) -> list[Finding]:
    text = segment.text.strip()
    function, role = _figure_role(segment.source)
    n_words = len(ts.words(text))
    found = []

    def add(rule_id: str):
        rule = rules_by_id[rule_id]
        found.append(Finding(rule_id, rule.level, rule.category, label, segment.line, segment.scope,
                             segment.source, text, _excerpt(text), rule.hint))

    if role in FIGURE_LEVEL_ROLES or function in FIGURE_LEVEL_FUNCTIONS:
        add("FIG-01")
    elif role in TITLE_ROLES or (function in TITLE_FUNCTIONS and role in (function, "label", "positional")):
        add("FIG-02")
    if n_words >= 9 or (text.endswith(".") and n_words >= 5):
        add("FIG-03")
    elif len(text) > 40:
        add("FIG-04")
    if len(text) == 1 and text.isalpha() and (role in ("labels", "legend") or function.startswith("scale_")):
        add("FIG-05")
    return found


def scan_segments(segments: list[ts.Segment], rules: list[ts.Rule], label: str, file_format: str,
                  doc_type: str) -> tuple[list[Finding], list[str]]:
    rules_by_id = {r.id: r for r in rules}
    active = [r for r in ts.regex_rules(rules) if doc_type not in r.skip_docs
              and (not r.formats or file_format in r.formats)]
    findings: list[Finding] = []
    prose_sentences: list[str] = []
    for segment in segments:
        text = segment.text
        spans = ts.sentence_spans(text)
        sentences = [text[a:b] for a, b in spans]
        if segment.scope == "prose":
            prose_sentences.extend(sentences)
        grouped: dict[tuple[str, str], Finding] = {}
        for rule in active:
            if segment.scope not in rule.scopes:
                continue
            for match in ts.rule_matches(rule, text, spans):
                context = _excerpt(ts.sentence_at(text, spans, match.start()))
                key = (rule.id, context)
                if key in grouped:  # one finding per rule and sentence
                    found = grouped[key]
                    found.count += 1
                    if match.group(0) not in found.match.split(" | "):
                        found.match += " | " + match.group(0)
                    continue
                grouped[key] = Finding(rule.id, rule.level, rule.category, label, segment.line, segment.scope,
                                       segment.source, match.group(0), context, rule.hint)
                findings.append(grouped[key])
        if segment.scope in ("prose", "caption", "slide"):
            openers = [s for s in sentences if STACK_OPENER.match(s.strip())]
            if len(openers) >= 2:
                rule = rules_by_id["STR-04"]
                findings.append(Finding("STR-04", rule.level, rule.category, label, segment.line, segment.scope,
                                        segment.source, " / ".join(o.split(",")[0] for o in openers),
                                        _excerpt(openers[0]), rule.hint))
        if segment.scope == "prose" and doc_type != "slides":
            for sentence in sentences:
                stripped = sentence.strip()
                if stripped.endswith("?") and not re.search(r"[\"“”']", stripped) and len(ts.words(stripped)) > 3:
                    rule = rules_by_id["STR-05"]
                    findings.append(Finding("STR-05", rule.level, rule.category, label, segment.line,
                                            segment.scope, segment.source, stripped, _excerpt(stripped), rule.hint))
        if segment.scope == "figure":
            findings.extend(figure_findings(segment, rules_by_id, label))
    return findings, prose_sentences


def density_report(profile: dict, findings: list[Finding], words: int, group: dict | None) -> list[dict]:
    rows = []
    for metric, label in DENSITY_LABELS.items():
        if metric not in profile:
            continue
        reference = (group or {}).get("metrics", {}).get(metric, {})
        value = profile[metric]
        high = bool(reference) and value > reference.get("p90", float("inf"))
        rows.append({"metric": metric, "label": label, "value": round(value, 2),
                     "reference_median": reference.get("p50"), "reference_p90": reference.get("p90"), "high": high})
    counts: dict[str, int] = {}
    for f in findings:
        if f.level in ("review", "density") and f.scope in ("prose", "caption", "slide"):
            counts[f.rule] = counts.get(f.rule, 0) + f.count
    for rule_id in sorted(counts):
        count = counts[rule_id]
        reference = (group or {}).get("rules", {}).get(rule_id)
        if reference is None or (count < 2 and rule_id not in ("CON-05", "CON-06", "LEX-10")):
            continue
        value = count * 1000 / words if words else 0.0
        ref_per_1000 = reference["per_10k_words"] / 10
        rows.append({"metric": rule_id, "label": f"{rule_id} ({count} hits)", "value": round(value, 2),
                     "reference_median": round(ref_per_1000, 2), "reference_p90": None,
                     "high": value > max(3 * ref_per_1000, 0.2)})
    return rows


def profile_report(profile: dict, group: dict | None) -> list[dict]:
    rows = []
    for metric in ts.PROFILE_METRICS:
        if metric not in profile:
            continue
        reference = (group or {}).get("metrics", {}).get(metric, {})
        value = profile[metric]
        note = ""
        if reference:
            if value > reference["p90"]:
                note = "above typical range"
            elif value < reference["p10"]:
                note = "below typical range"
        rows.append({"metric": metric, "label": PROFILE_LABELS[metric], "value": round(value, 3),
                     "p10": reference.get("p10"), "p50": reference.get("p50"), "p90": reference.get("p90"),
                     "note": note})
    return rows


def collect_paths(paths: list[str]) -> list[Path]:
    collected = []
    for item in paths:
        path = Path(item)
        if path.is_dir():
            collected.extend(sorted(p for p in path.rglob("*") if p.suffix.lower() in SUFFIXES and p.is_file()))
        else:
            collected.append(path)
    return collected


def format_number(value) -> str:
    if value is None:
        return "–"
    if isinstance(value, float) and value < 1 and value != 0:
        return f"{value:.2f}"
    return f"{value:.1f}" if isinstance(value, float) else str(value)


def print_report(result: dict, show_levels: set[str], show_profile: bool, out) -> None:
    findings = [f for f in result["findings"] if f["level"] in show_levels]
    print(f"\n{result['file']}: {result['words']:,} words of prose, {result['sentences']:,} sentences", file=out)
    for level in ("must", "review", "density"):
        items = [f for f in findings if f["level"] == level]
        if not items:
            continue
        heading = {"must": "MUST FIX", "review": "REVIEW", "density": "DENSITY TERMS"}[level]
        print(f"\n{heading} ({len(items)})", file=out)
        for f in sorted(items, key=lambda x: (x["line"], x["rule"])):
            where = f"{f['scope']} {f['line']}" if f["scope"] != "figure" else f"line {f['line']} {f['source']}"
            times = f" (x{f['count']})" if f.get("count", 1) > 1 else ""
            print(f"  {where}  [{f['rule']}]{times} \"{f['context']}\"", file=out)
            print(f"      {f['hint']}", file=out)
    if result["density"]:
        print("\nDENSITY per 1000 words (flagship research median / 90th percentile)", file=out)
        for row in result["density"]:
            flag = "  HIGH" if row["high"] else ""
            ref = f"{format_number(row['reference_median'])} / {format_number(row['reference_p90'])}"
            print(f"  {row['label']:<52} {format_number(row['value']):>6}   ({ref}){flag}", file=out)
    if show_profile and result.get("profile"):
        print(f"\nSTYLE PROFILE (reference group: {result['reference_group']}; typical range = 10th–90th percentile)",
              file=out)
        for row in result["profile"]:
            ref = f"{format_number(row['p10'])}–{format_number(row['p90'])}" if row["p10"] is not None else "–"
            print(f"  {row['label']:<46} {format_number(row['value']):>6}   {ref:<12} {row['note']}", file=out)


def scan_file(path: Path, rules: list[ts.Rule], doc_type: str, scope: str | None, group: dict | None,
              label: str | None = None, text: str | None = None) -> dict:
    if text is not None:
        segments = ts.read_markdown(text)
        if scope:
            for segment in segments:
                segment.scope = scope
        file_format = "md"
    else:
        segments = ts.read_segments(path, scope)
        file_format = path.suffix.lower().lstrip(".")
    label = label or str(path)
    findings, prose_sentences = scan_segments(segments, rules, label, file_format, doc_type)
    profile = ts.profile(prose_sentences)
    words = profile.get("words", 0)
    return {
        "file": label,
        "words": words,
        "sentences": profile.get("sentences", 0),
        "findings": [asdict(f) for f in findings],
        "density": density_report(profile, findings, words, group) if words >= 200 else [],
        "profile": profile_report(profile, group) if words >= 200 else [],
        "reference_group": None,
    }


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("paths", nargs="+", help="files or folders to check; '-' reads text from stdin")
    parser.add_argument("--doc", choices=DOC_TYPES, default="manuscript",
                        help="document type; 'response' allows revision narration")
    parser.add_argument("--journal", default="core",
                        help="reference group for density and profile: core, lancet, nejm, jama, bmj, nature, cell, science")
    parser.add_argument("--scope", choices=ts.SCOPES, help="treat all text in the inputs as this scope (e.g. figure)")
    parser.add_argument("--level", choices=("must", "review", "all"), default="review",
                        help="lowest level to list (default: review)")
    parser.add_argument("--profile", action="store_true", help="compare the style profile with flagship journals")
    parser.add_argument("--json", action="store_true", help="print JSON")
    parser.add_argument("--strict", action="store_true", help="exit with status 1 if any must-fix finding is present")
    args = parser.parse_args(argv)

    _, rules = ts.load_rules()
    group = None
    try:
        calibration = ts.load_calibration()
        group = calibration["groups"].get(args.journal)
        if group is None:
            parser.error(f"unknown reference group '{args.journal}'; choose from {', '.join(calibration['groups'])}")
    except FileNotFoundError:
        calibration = None

    results = []
    for item in args.paths:
        if item == "-":
            results.append(scan_file(Path("stdin"), rules, args.doc, args.scope, group, "stdin", sys.stdin.read()))
            continue
        for path in collect_paths([item]):
            if not path.exists():
                parser.error(f"no such file: {path}")
            try:
                result = scan_file(path, rules, args.doc, args.scope, group)
            except (OSError, RuntimeError, KeyError, ValueError) as error:
                print(f"{path}: cannot read ({error})", file=sys.stderr)
                continue
            results.append(result)
    for result in results:
        result["reference_group"] = args.journal if group else None

    show = {"must"} if args.level == "must" else ({"must", "review"} if args.level == "review" else set(LEVELS))
    must_total = sum(1 for r in results for f in r["findings"] if f["level"] == "must")
    review_total = sum(1 for r in results for f in r["findings"] if f["level"] == "review")
    if args.json:
        payload = {"files": results, "summary": {"must": must_total, "review": review_total}}
        if not args.profile:
            for r in payload["files"]:
                r.pop("profile", None)
        json.dump(payload, sys.stdout, ensure_ascii=False, indent=1)
        print()
    else:
        for result in results:
            print_report(result, show, args.profile, sys.stdout)
        print(f"\n{must_total} must-fix, {review_total} to review across {len(results)} file(s).")
    return 1 if (args.strict and must_total) else 0


if __name__ == "__main__":
    for stream in (sys.stdout, sys.stderr):
        if hasattr(stream, "reconfigure"):
            stream.reconfigure(encoding="utf-8")
    raise SystemExit(main())
