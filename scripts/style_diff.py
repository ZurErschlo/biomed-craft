#!/usr/bin/env python3
"""Compare the agent's draft with the researcher's revision and list style habits.

Reads two versions (any format scan.py reads), or one Word file with tracked
changes, aligns paragraphs and then words, and reports what the researcher
changed: replaced words and phrases with counts, frequent deletions and
insertions, rule findings removed or introduced, and shifts in the style
profile. Edits that changed numbers or citations are set aside as content.
The end of the report lists candidate entries for the personal style file
(references/personal-style.md), each with a suggested scope. Nothing is written
to the style file: the researcher confirms entries first.

Examples:
  python3 style_diff.py draft.docx revised.docx
  python3 style_diff.py --doc legends draft_legends.md revised_legends.md
  python3 style_diff.py --tracked revised_with_track_changes.docx --type modelling
  python3 style_diff.py --json draft.md revised.md
"""

from __future__ import annotations

import argparse
import difflib
import json
import re
import sys
import zipfile
from collections import Counter
from pathlib import Path
from xml.etree import ElementTree as ET

sys.path.insert(0, str(Path(__file__).resolve().parent))
import check_preservation as cp  # noqa: E402
import textstats as ts  # noqa: E402

W = "{http://schemas.openxmlformats.org/wordprocessingml/2006/main}"
TOKEN = re.compile(r"[A-Za-z0-9]+(?:['’.·-][A-Za-z0-9]+)*|[^\sA-Za-z0-9]")
BRITISH = re.compile(r"\b\w+(?:is(?:e|ed|es|ing|ation)|our|yse|ysed|tre)\b", re.IGNORECASE)
AMERICAN = re.compile(r"\b\w+(?:iz(?:e|ed|es|ing|ation)|or|yze|yzed|ter)\b", re.IGNORECASE)
PROFILE_SHIFTS = (("sentence_median", "median sentence length", 3.0), ("we_per_1000", "`we` per 1000 words", 3.0),
                  ("passive_share", "share of sentences with a passive", 0.1),
                  ("dashes_per_1000", "dashes per 1000 words", 1.0), ("semicolons_per_1000", "semicolons per 1000 words", 1.0))
MIN_REPEAT = 2
# Profile shifts are noise in short texts.
MIN_PROFILE_WORDS = 300


def tracked_versions(path: Path) -> tuple[str, str]:
    """Text before and after the tracked changes of a Word file."""
    with zipfile.ZipFile(path) as archive:
        root = ET.fromstring(archive.read("word/document.xml"))
    before, after = [], []

    def walk(node: ET.Element, inserted: bool, out: tuple[list, list]) -> None:
        for child in node:
            if child.tag == W + "t":
                if not inserted:
                    out[0].append(child.text or "")
                out[1].append(child.text or "")
            elif child.tag == W + "delText":
                out[0].append(child.text or "")
            elif child.tag in (W + "tab", W + "br"):
                out[0].append(" "), out[1].append(" ")
            else:
                walk(child, inserted or child.tag == W + "ins", out)

    for paragraph in root.iter(W + "p"):
        pieces: tuple[list, list] = ([], [])
        walk(paragraph, False, pieces)
        before.append("".join(pieces[0]).strip())
        after.append("".join(pieces[1]).strip())
    return "\n\n".join(p for p in before if p), "\n\n".join(p for p in after if p)


def paragraphs(text: str) -> list[str]:
    return [re.sub(r"\s+", " ", p).strip() for p in re.split(r"\n\s*\n|\n(?=#)", text) if p.strip()]


def join_tokens(tokens: list[str]) -> str:
    return re.sub(r"\s+([,.;:)\]])", r"\1", " ".join(tokens)).replace("( ", "(")


def is_content(old: str, new: str) -> bool:
    """An edit that changes numbers or citations is content, not style."""
    return cp.numbers(old) != cp.numbers(new) or cp.citations(old) != cp.citations(new)


def word_edits(draft: str, revised: str) -> dict:
    replaced, deleted, inserted, content = Counter(), Counter(), Counter(), 0
    old_paras, new_paras = paragraphs(draft), paragraphs(revised)
    matcher = difflib.SequenceMatcher(None, old_paras, new_paras, autojunk=False)
    pairs = []
    for op, a0, a1, b0, b1 in matcher.get_opcodes():
        if op == "equal":
            continue
        for old in old_paras[a0:a1]:
            best = max(new_paras[b0:b1], key=lambda new: difflib.SequenceMatcher(None, old, new).ratio(), default=None)
            if best is not None and difflib.SequenceMatcher(None, old, best).ratio() >= 0.4:
                pairs.append((old, best))
    for old, new in pairs:
        a, b = TOKEN.findall(old), TOKEN.findall(new)
        aligned = difflib.SequenceMatcher(None, [x.lower() for x in a], [x.lower() for x in b], autojunk=False)
        for op, a0, a1, b0, b1 in aligned.get_opcodes():
            before, after = join_tokens(a[a0:a1]), join_tokens(b[b0:b1])
            if op == "equal" or (a1 - a0) > 6 or (b1 - b0) > 6:
                continue
            if is_content(before, after):
                content += 1
            elif op == "replace":
                replaced[(before.lower(), after.lower())] += 1
            elif op == "delete":
                deleted[before.lower()] += 1
            elif op == "insert":
                inserted[after.lower()] += 1
    return {"replaced": replaced, "deleted": deleted, "inserted": inserted, "content_edits": content,
            "paragraphs_changed": len(pairs)}


def rule_counts(text: str, rules: list[ts.Rule]) -> Counter:
    counts = Counter()
    for rule in rules:
        if rule.kind == "regex" and "prose" in rule.scopes and not rule.docs:
            hits = len(ts.rule_matches(rule, text))
            if hits:
                counts[rule.id] = hits
    return counts


def style_profile(text: str) -> dict:
    sentences = [s for p in paragraphs(text) for s in ts.split_sentences(p) if len(s.split()) >= 4]
    profile = ts.profile(sentences)
    profile["british"] = len(BRITISH.findall(text))
    profile["american"] = len(AMERICAN.findall(text))
    return profile


def compare(draft: str, revised: str, doc: str = "manuscript", design: str = "") -> dict:
    _, rules = ts.load_rules()
    edits = word_edits(draft, revised)
    before_rules, after_rules = rule_counts(draft, rules), rule_counts(revised, rules)
    hints = {r.id: r.hint for r in rules}
    removed = {r: (before_rules[r], after_rules.get(r, 0)) for r in before_rules if after_rules.get(r, 0) < before_rules[r]}
    introduced = {r: (before_rules.get(r, 0), after_rules[r]) for r in after_rules if after_rules[r] > before_rules.get(r, 0)}
    p_before, p_after = style_profile(draft), style_profile(revised)
    shifts = []
    short = min(p_before.get("words", 0), p_after.get("words", 0)) < MIN_PROFILE_WORDS
    for key, label, threshold in ([] if short else PROFILE_SHIFTS):
        if key in p_before and key in p_after and abs(p_after[key] - p_before[key]) >= threshold:
            shifts.append({"metric": label, "before": round(p_before[key], 2), "after": round(p_after[key], 2)})
    scope = f"Document: {doc}" + (f" (study type: {design})" if design else "")
    candidates = []
    for (old, new), n in edits["replaced"].most_common():
        if n >= MIN_REPEAT:
            candidates.append({"entry": f"Prefer '{new}' to '{old}'.", "evidence": f"replaced {n} times", "scope": scope})
    for phrase, n in edits["deleted"].most_common():
        if n >= MIN_REPEAT and re.search(r"[A-Za-z]{3}", phrase):
            candidates.append({"entry": f"Avoid '{phrase}'.", "evidence": f"deleted {n} times", "scope": scope})
    for rule_id, (b, a) in sorted(removed.items()):
        if a == 0 and b >= MIN_REPEAT:
            candidates.append({"entry": f"Avoid [{rule_id}]: {hints[rule_id]}", "evidence": f"removed all {b}",
                               "scope": scope})
    for rule_id, (b, a) in sorted(introduced.items()):
        if a - b >= MIN_REPEAT:
            candidates.append({"entry": f"Allow [{rule_id}] where the researcher writes it.",
                               "evidence": f"added {a - b} although the skill flags it", "scope": scope})
    for shift in shifts:
        candidates.append({"entry": f"Aim for a {shift['metric']} near {shift['after']}.",
                           "evidence": f"changed from {shift['before']} to {shift['after']}", "scope": scope})
    if p_after["british"] - p_before["british"] >= MIN_REPEAT and p_after["american"] <= p_before["american"]:
        candidates.append({"entry": "British spelling.", "evidence": "British forms added", "scope": "General"})
    elif p_after["american"] - p_before["american"] >= MIN_REPEAT and p_after["british"] <= p_before["british"]:
        candidates.append({"entry": "American spelling.", "evidence": "American forms added", "scope": "General"})
    return {
        "paragraphs_changed": edits["paragraphs_changed"],
        "content_edits_set_aside": edits["content_edits"],
        "replaced": [{"from": o, "to": n, "count": c} for (o, n), c in edits["replaced"].most_common(30)],
        "deleted": [{"text": t, "count": c} for t, c in edits["deleted"].most_common(20)],
        "inserted": [{"text": t, "count": c} for t, c in edits["inserted"].most_common(20)],
        "rules_removed": {r: {"before": b, "after": a} for r, (b, a) in sorted(removed.items())},
        "rules_introduced": {r: {"before": b, "after": a} for r, (b, a) in sorted(introduced.items())},
        "profile_shifts": shifts,
        "candidates": candidates,
    }


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("files", nargs="*", type=Path, help="the agent's draft and the researcher's revision")
    parser.add_argument("--tracked", type=Path, help="one Word file with tracked changes, instead of two files")
    parser.add_argument("--doc", default="manuscript",
                        help="document the text belongs to (manuscript, abstract, legends, plan, log, code, response, slides)")
    parser.add_argument("--type", dest="design", default="", choices=("",) + ts.DESIGNS, help="study type, for the scope")
    parser.add_argument("--json", action="store_true", help="print JSON")
    args = parser.parse_args(argv)
    if args.tracked:
        draft, revised = tracked_versions(args.tracked)
    elif len(args.files) == 2:
        draft, revised = (cp.read_text(p) for p in args.files)
    else:
        parser.error("give the draft and the revision, or --tracked FILE.docx")
    result = compare(draft, revised, args.doc, args.design)
    if args.json:
        json.dump(result, sys.stdout, ensure_ascii=False, indent=1)
        print()
        return 0
    print(f"{result['paragraphs_changed']} paragraphs changed; {result['content_edits_set_aside']} edits to numbers "
          "or citations set aside as content.")
    for title, key, fmt in (("Replaced", "replaced", lambda x: f"'{x['from']}' -> '{x['to']}'"),
                            ("Deleted", "deleted", lambda x: f"'{x['text']}'"),
                            ("Inserted", "inserted", lambda x: f"'{x['text']}'")):
        if result[key]:
            print(f"\n{title}:")
            for item in result[key][:15]:
                print(f"  {fmt(item)} x{item['count']}")
    for title, key in (("Rule findings the researcher removed", "rules_removed"),
                       ("Rule findings the researcher introduced", "rules_introduced")):
        if result[key]:
            print(f"\n{title}:")
            for rule_id, counts in result[key].items():
                print(f"  {rule_id}: {counts['before']} -> {counts['after']}")
    if result["profile_shifts"]:
        print("\nStyle profile:")
        for shift in result["profile_shifts"]:
            print(f"  {shift['metric']}: {shift['before']} -> {shift['after']}")
    print("\nCandidate entries (add to Pending; propose once seen three times across two documents):")
    for item in result["candidates"] or [{"entry": "none", "evidence": "", "scope": ""}]:
        print(f"  - {item['entry']} ({item['evidence']}) [{item['scope']}]" if item["evidence"] else "  - none")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
