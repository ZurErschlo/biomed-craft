#!/usr/bin/env python3
"""Check that the numbers in a manuscript agree with each other.

Finds these problems, without changing any file:

  - a percentage that does not match its count and denominator
    ("482 of 2104 patients (25.9%)", "49 (2%) of 2609", "13/40 (35%)");
  - a point estimate outside its confidence interval, an interval whose
    bounds are reversed, or a ratio interval that reaches zero or below;
  - a P value that its t, z, χ² or F statistic and degrees of freedom cannot
    give, allowing for rounding ("t(28) = 2.10, P = .21");
  - the arithmetic of a PRISMA 2020 flow diagram written as "label (n = N)";
  - with --grim-items, a mean of integer data (Likert items, counts) that no
    total of n answers can give;
  - a number in the abstract or summary that appears nowhere else in the text.

Notes, which do not count as problems, list ratio intervals that are not
symmetric on the log scale and test statistics that cannot be checked
(one-sided, corrected, exact or resampling tests).

Reads the same formats as scan.py (Markdown, Word, LaTeX, PDF and others).
Lancet mid-dot decimals and space or comma thousands separators are understood.

Examples:
  python3 check_numbers.py manuscript.docx
  python3 check_numbers.py --strict --json draft.md
  python3 check_numbers.py --grim-items 1 survey.docx
"""

from __future__ import annotations

import argparse
import json
import math
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


# ---------------------------------------------------------------------------
# Test statistics and P values
# ---------------------------------------------------------------------------

STAT_NUMBER = r"\d+(?:[.·]\d+)?"
P_VALUE = r"(?P<p>\d(?:[.·]\d+)?\s*(?:[×x]\s*10\s*|[eE])[-−–]\s*\d+|0?[.·]\d+|1(?:[.·]0+)?)(?![\deE])"
STATISTIC = re.compile(
    r"(?<![\w.])(?P<test>t|F|z|Z|χ\s*[²2]|[Cc]hi[- ]?squared?|X\s*²)"
    rf"(?:\s*\(\s*(?P<df1>{STAT_NUMBER})(?:\s*[,;]\s*(?P<df2>{STAT_NUMBER}))?(?:\s*[,;]\s*[Nn]\s*=\s*[\d,]+)?\s*\)"
    r"|_?\{?(?P<sub1>\d+)(?:\s*,\s*(?P<sub2>\d+))?\}?)?"
    rf"\s*=\s*(?P<stat>[-−–]?{STAT_NUMBER})"
    rf"(?:\s*[,;]\s*(?:df|d\.f\.)\s*=\s*(?P<df3>{STAT_NUMBER}))?"
    rf"\s*[,;]?\s*(?:and\s+)?[Pp]\s*(?P<op><=|>=|=|<|>|≤|≥)\s*{P_VALUE}"
)
# These change the P value in ways the statistic and degrees of freedom do not show.
NOT_CHECKABLE = re.compile(
    r"one-sided|one-tailed|Welch|Greenhouse|Huynh|Satterthwaite|Kenward|exact|Fisher|permutation|bootstrap"
    r"|Bonferroni|Holm|Benjamini|adjusted P|corrected P|false discovery", re.IGNORECASE)
FPMIN = 1e-300
MAX_ITERATIONS = 20000  # the series and fractions need about the square root of the larger parameter in steps


def _beta_fraction(a: float, b: float, x: float) -> float:
    """Continued fraction for the incomplete beta function (modified Lentz method); NaN if it does not converge."""
    qab, qap, qam = a + b, a + 1, a - 1
    c, d = 1.0, 1 - qab * x / qap
    d = 1 / (d if abs(d) > FPMIN else FPMIN)
    h = d
    for m in range(1, MAX_ITERATIONS):
        m2 = 2 * m
        for aa in (m * (b - m) * x / ((qam + m2) * (a + m2)), -(a + m) * (qab + m) * x / ((a + m2) * (qap + m2))):
            d = 1 + aa * d
            d = 1 / (d if abs(d) > FPMIN else FPMIN)
            c = 1 + aa / c
            c = c if abs(c) > FPMIN else FPMIN
            h *= d * c
        if abs(d * c - 1) < 1e-14:
            return h
    return math.nan


def incomplete_beta(a: float, b: float, x: float) -> float:
    """Regularized incomplete beta function I_x(a, b)."""
    if x <= 0:
        return 0.0
    if x >= 1:
        return 1.0
    front = math.exp(math.lgamma(a + b) - math.lgamma(a) - math.lgamma(b) + a * math.log(x) + b * math.log1p(-x))
    if x < (a + 1) / (a + b + 2):
        return front * _beta_fraction(a, b, x) / a
    return 1 - front * _beta_fraction(b, a, 1 - x) / b


def upper_gamma(a: float, x: float) -> float:
    """Regularized upper incomplete gamma function Q(a, x); NaN if the series or fraction does not converge."""
    if x <= 0:
        return 1.0
    front = math.exp(-x + a * math.log(x) - math.lgamma(a))
    if x < a + 1:  # series for P(a, x)
        term = total = 1 / a
        denominator = a
        for _ in range(MAX_ITERATIONS):
            denominator += 1
            term *= x / denominator
            total += term
            if abs(term) < abs(total) * 1e-15:
                return max(0.0, 1 - front * total)
        return math.nan
    b, c, d = x + 1 - a, 1 / FPMIN, 1 / (x + 1 - a)  # continued fraction for Q(a, x)
    h = d
    for i in range(1, MAX_ITERATIONS):
        an = -i * (i - a)
        b += 2
        d = an * d + b
        d = 1 / (d if abs(d) > FPMIN else FPMIN)
        c = b + an / c
        c = c if abs(c) > FPMIN else FPMIN
        h *= d * c
        if abs(d * c - 1) < 1e-15:
            return front * h
    return math.nan


def two_sided_p(test: str, value: float, df1: float | None, df2: float | None) -> float | None:
    value = abs(value)
    if test == "z":
        return math.erfc(value / math.sqrt(2))
    if test == "t" and df1:
        return incomplete_beta(df1 / 2, 0.5, df1 / (df1 + value * value))
    if test == "F" and df1 and df2:
        return incomplete_beta(df2 / 2, df1 / 2, df2 / (df2 + df1 * value)) if value > 0 else 1.0
    if test == "chi2" and df1:
        return upper_gamma(df1 / 2, value / 2)
    return None


def _p_number(text: str) -> float:
    scientific = re.match(r"(\d(?:[.·]\d+)?)\s*(?:[×x]\s*10\s*|[eE])[-−–]\s*(\d+)", text)
    if scientific:
        return to_float(scientific.group(1)) * 10 ** -int(scientific.group(2))
    return to_float(text if not text.startswith((".", "·")) else "0" + text)


def _p_step(text: str) -> float:
    """Half the last reported digit of a P value: 0.03 may be anything from 0.025 to 0.035."""
    scientific = re.match(r"(\d(?:[.·](\d+))?)\s*(?:[×x]\s*10\s*|[eE])[-−–]\s*(\d+)", text)
    if scientific:
        return 0.5 * 10 ** -(len(scientific.group(2) or "") + int(scientific.group(3)))
    return 0.5 * 10 ** -decimals(text if not text.startswith((".", "·")) else "0" + text)


def _p_text(p: float) -> str:
    """Two significant figures, in scientific notation below 0.0001."""
    return f"{p:.1e}" if p < 1e-4 else f"{p:.2g}"


def statistic_problems(text: str, line: int) -> tuple[list[Problem], list[Problem]]:
    """P values recomputed from t, z, χ² and F with their degrees of freedom (two-sided for t and z). A reported statistic
    stands for a range (2.3 for anything from 2.25 to 2.35), so a P value is flagged only when no value in
    that range gives it."""
    problems, notes = [], []
    spans = ts.sentence_spans(text)
    for match in STATISTIC.finditer(text):
        raw = match["test"]
        test = "chi2" if raw[0] in "χCcX" else raw.lower() if raw in ("z", "Z") else raw
        df1 = match["df1"] or match["sub1"] or match["df3"]
        df2 = match["df2"] or match["sub2"]
        df1 = to_float(df1) if df1 else None
        df2 = to_float(df2) if df2 else None
        sentence = ts.sentence_at(text, spans, match.start())
        method = NOT_CHECKABLE.search(sentence)
        if method:
            notes.append(Problem("statistic", line, match.group(0),
                                 f"not checked: the sentence names {method.group(0)!r}, and one-sided, corrected, "
                                 "exact and resampling tests or adjusted degrees of freedom change the P value"))
            continue
        statistic = to_float(match["stat"])
        if statistic < 0 and test in ("chi2", "F"):
            label = "a χ²" if test == "chi2" else "an F"
            problems.append(Problem("statistic", line, match.group(0), f"{label} statistic cannot be negative"))
            continue
        step = 0.5 * 10 ** -decimals(match["stat"])
        high = two_sided_p(test, max(abs(statistic) - step, 0), df1, df2)
        low = two_sided_p(test, abs(statistic) + step, df1, df2)
        if high is None or low is None:
            continue
        if math.isnan(high) or math.isnan(low):
            notes.append(Problem("statistic", line, match.group(0),
                                 "not checked: the P value could not be computed to full precision for these degrees "
                                 "of freedom"))
            continue
        reported, op = _p_number(match["p"]), match["op"]
        if op in ("=",):
            margin = _p_step(match["p"])
            agrees = low <= reported + margin and high >= reported - margin
            one_sided = low / 2 <= reported + margin and high / 2 >= reported - margin
        elif op in ("<", "<=", "≤"):
            agrees, one_sided = low <= reported, low / 2 <= reported
        else:
            agrees, one_sided = high >= reported, high / 2 >= reported
        if agrees:
            continue
        one_sided = one_sided and test in ("t", "z")  # χ² and F tests already use one tail
        df = f"{df1:g}, {df2:g}" if df2 else f"{df1:g}" if df1 else ""
        label = {"chi2": "χ²", "z": "z"}.get(test, test) + (f"({df})" if df else "")
        low_text, high_text = _p_text(low), _p_text(high)
        span = f"of about {low_text}" if low_text == high_text else f"between {low_text} and {high_text}"
        sides = "a two-sided P" if test in ("t", "z") else "P"
        message = f"{label} = {match['stat']} gives {sides} {span}, not P {op} {match['p']}"
        if one_sided:
            message += "; the reported P fits a one-sided test, so say so or report the two-sided value"
        problems.append(Problem("statistic", line, match.group(0), message))
    return problems, notes


# ---------------------------------------------------------------------------
# Ratio intervals on the log scale
# ---------------------------------------------------------------------------

ASYMMETRIC_INTERVAL = re.compile(r"\b(?:UI|uncertainty|CrI|credible|Bayesian|posterior|profile|exact|bootstrap"
                                 r"|Clopper|Wilson|mid-p)\b", re.IGNORECASE)
SYMMETRY_SLACK = 0.1  # share of the half-width on the log scale; profile-likelihood intervals of large studies fall within it


def symmetry_notes(text: str, line: int) -> list[Problem]:
    """A Wald interval for a ratio is symmetric about the estimate on the log scale. Flag estimates that sit
    off-center by more than rounding allows, as a prompt to check the numbers or name the method."""
    notes = []
    spans = ts.sentence_spans(text)
    for match in INTERVAL.finditer(text):
        if not match["label"]:
            continue
        before = text[max(0, match.start() - 80):match.end()]
        if ASYMMETRIC_INTERVAL.search(before) or ASYMMETRIC_INTERVAL.search(ts.sentence_at(text, spans, match.start())):
            continue
        try:
            values = [match["est"], match["low"], match["high"]]
            estimate, low, high = (to_float(v) for v in values)
        except ValueError:
            continue
        if not 0 < low < estimate < high:
            continue
        steps = [0.5 * 10 ** -decimals(v) for v in values]
        if low - steps[1] <= 0:
            continue
        center_low = (math.log(low - steps[1]) + math.log(high - steps[2])) / 2
        center_high = (math.log(low + steps[1]) + math.log(high + steps[2])) / 2
        estimate_low, estimate_high = math.log(estimate - steps[0]), math.log(estimate + steps[0])
        slack = SYMMETRY_SLACK * (math.log(high) - math.log(low)) / 2
        if estimate_high + slack < center_low or estimate_low - slack > center_high:
            center = math.exp((math.log(low) + math.log(high)) / 2)
            notes.append(Problem("symmetry", line, match.group(0),
                                 f"on the log scale the interval centers on {center:.3g}, not {match['est']}; check the "
                                 "numbers, or name the method if the interval is not a Wald interval"))
    return notes


# ---------------------------------------------------------------------------
# GRIM: means of integer data
# ---------------------------------------------------------------------------

MEAN = re.compile(r"\b(?:mean|M|average)\b(?:\s+(?:score|value))?\s*(?:[=:]|was|of|,)?\s*(?P<mean>\d+[.·]\d+)")
SAMPLE = re.compile(r"\b[nN]\s*=\s*(?P<n>\d{1,3}(?:,\d{3})*|\d+)\b")


def grim_problems(text: str, line: int, items: int) -> list[Problem]:
    """GRIM (Brown and Heathers 2017): n people, each scored as the average of k integer items, give means that
    are multiples of 1/(n × k); a summed score is one integer, so k = 1. A mean with d decimals can be tested only when n × k < 10^d; beyond that, consecutive multiples
    lie closer together than the rounding step, so every reported value is possible. The condition follows
    from the arithmetic. Means and sample sizes are paired only when they alternate within a sentence."""
    problems = []
    for start, end in ts.sentence_spans(text):
        sentence = text[start:end]
        marks = sorted([(m.start(), "mean", m) for m in MEAN.finditer(sentence)]
                       + [(m.start(), "n", m) for m in SAMPLE.finditer(sentence)], key=lambda item: item[0])
        kinds = [kind for _, kind, _ in marks]
        if not marks or kinds.count("mean") != kinds.count("n") or any(a == b for a, b in zip(kinds, kinds[1:])):
            continue
        for first, second in zip(marks[::2], marks[1::2]):
            mean_match = first[2] if first[1] == "mean" else second[2]
            n_match = second[2] if first[1] == "mean" else first[2]
            reported, places = to_float(mean_match["mean"]), decimals(mean_match["mean"])
            units = int(n_match["n"].replace(",", "")) * items
            if units <= 0 or units >= 10 ** places:
                continue
            step = 0.5 * 10 ** -places + 1e-9
            closest = round(reported * units)
            if not any(abs(k / units - reported) <= step for k in (closest - 1, closest, closest + 1)):
                problems.append(Problem("grim", line, f"{mean_match.group(0)} … {n_match.group(0)}",
                                        f"no total of {units} integer answers gives a mean of {mean_match['mean']}"
                                        f" (n = {n_match['n']}, {items} item(s) each)"))
    return problems


# ---------------------------------------------------------------------------
# PRISMA 2020 flow diagram
# ---------------------------------------------------------------------------

FLOW_COUNT = re.compile(rf"(?P<label>[A-Za-z][^()\n]{{2,90}}?)\s*\(\s*[nN]\s*=\s*(?P<n>{NUMBER})\s*\)")
FLOW_STEPS = (  # checked in this order: 'reports of included studies' before 'included studies'
    ("duplicates", r"duplicate"),
    ("automation", r"automation"),
    ("other_removed", r"removed for other reasons"),
    ("screened", r"records screened"),
    ("records_excluded", r"records excluded"),
    ("sought", r"sought for retrieval"),
    ("not_retrieved", r"not retrieved"),
    ("assessed", r"assessed for eligibility"),
    ("reports_excluded", r"reports excluded\s*$"),
    ("included_reports", r"reports of (?:new )?included studies"),
    ("studies", r"studies included|included studies"),
    ("identified_part", r"\bdatabases?\b|\bregisters?\b"),
    ("identified", r"records identified\b(?!\s*(?:from|through|via))"),
)
REASONS_START = re.compile(r"reports excluded\s*:\s*\S")
BEFORE_SCREENING = ("duplicates", "automation", "other_removed")


def flow_problems(segments: list[ts.Segment]) -> list[Problem]:
    """Arithmetic of a PRISMA 2020 flow diagram written as 'label (n = N)': records identified minus those
    removed before screening equals records screened; screened minus excluded equals reports sought;
    sought minus not retrieved equals reports assessed; assessed minus reports excluded equals the reports
    of included studies, and the reasons for exclusion add up to the reports excluded. Studies and reports
    are counted apart and not compared: a study can have several reports, and one report can describe several
    studies. A step whose label appears twice (another branch of the diagram) is left unchecked."""
    counts: dict[str, list[tuple[int, int]]] = {}
    reason_blocks: list[list[int]] = []
    reasons_open = False
    for segment in segments:
        for match in FLOW_COUNT.finditer(segment.text):
            label = match["label"].lower().strip(" :;,.–—-*†‡")
            n = int(to_float(match["n"]))
            if REASONS_START.search(label):  # 'Reports excluded: wrong population (n = 30)'
                reason_blocks.append([n])
                reasons_open = True
                continue
            step = next((name for name, pattern in FLOW_STEPS if re.search(pattern, label)), None)
            if reasons_open and step in BEFORE_SCREENING:  # 'Duplicate population (n = 20)' is a reason
                step = None
            if step is None:
                if reasons_open:
                    reason_blocks[-1].append(n)
                continue
            counts.setdefault(step, []).append((n, segment.line))
            reasons_open = step == "reports_excluded"
            if reasons_open:
                reason_blocks.append([])
    if "screened" not in counts:
        return []

    def one(step: str) -> int | None:
        values = counts.get(step, [])
        return values[0][0] if len(values) == 1 else None

    def line_of(step: str) -> int:
        return counts[step][0][1]

    problems = []
    parts = [n for n, _ in counts.get("identified_part", [])]
    identified = sum(parts) if parts else one("identified")
    if parts and one("identified") is not None and sum(parts) != one("identified"):
        problems.append(Problem("flow", line_of("identified"), f"records identified (n = {one('identified')})",
                                f"the databases and registers add up to {sum(parts)}"))
    removed = [one(step) for step in ("duplicates", "automation", "other_removed")]
    if identified and one("screened") is not None and any(r is not None for r in removed):
        expected = identified - sum(r or 0 for r in removed)
        if expected != one("screened"):
            problems.append(Problem("flow", line_of("screened"), f"records screened (n = {one('screened')})",
                                    f"{identified} identified minus {sum(r or 0 for r in removed)} removed before "
                                    f"screening is {expected}"))
    excluded_reports = one("reports_excluded")
    blocks = [block for block in reason_blocks if block]
    if len(reason_blocks) == 1 and blocks:
        if excluded_reports is None and "reports_excluded" not in counts:
            excluded_reports = sum(blocks[0])
        elif excluded_reports is not None and sum(blocks[0]) != excluded_reports:
            problems.append(Problem("flow", line_of("reports_excluded"), f"reports excluded (n = {excluded_reports})",
                                    f"the reasons add up to {sum(blocks[0])}"))
    chain = (("screened", "records_excluded", "sought", "reports sought for retrieval"),
             ("sought", "not_retrieved", "assessed", "reports assessed for eligibility"),
             ("assessed", None, "included_reports", "reports of included studies"))
    for first_step, minus, result, name in chain:
        first, second = one(first_step), excluded_reports if minus is None else one(minus)
        target = one(result)
        if None in (first, second, target):
            continue
        if first - second != target:
            problems.append(Problem("flow", line_of(result), f"{name} (n = {target})",
                                    f"{first} minus {second} is {first - second}"))
    return problems


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


def check_file(path: Path, grim_items: int = 0) -> dict:
    segments = ts.read_segments(path)
    problems: list[Problem] = []
    notes: list[Problem] = []
    for segment in segments:
        if segment.scope in ("prose", "caption", "table", "slide", "figure"):
            problems += percentage_problems(segment.text, segment.line)
            problems += interval_problems(segment.text, segment.line)
            found, unchecked = statistic_problems(segment.text, segment.line)
            problems += found
            notes += unchecked + symmetry_notes(segment.text, segment.line)
            if grim_items:
                problems += grim_problems(segment.text, segment.line, grim_items)
    problems += abstract_problems([s for s in segments if s.scope in ("prose", "caption", "table")])
    problems += flow_problems([s for s in segments if s.scope in ("prose", "caption", "table", "slide", "figure")])
    return {"file": str(path), "problems": [asdict(p) for p in problems], "notes": [asdict(n) for n in notes]}


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("paths", nargs="+", type=Path, help="manuscript files")
    parser.add_argument("--json", action="store_true", help="print JSON")
    parser.add_argument("--strict", action="store_true", help="exit with status 1 if any problem is found")
    parser.add_argument("--grim-items", type=int, default=0, metavar="K",
                        help="check means of integer data, each person's score the average of K integer items "
                             "(1 for a single Likert item, a count or a summed score); off by default")
    args = parser.parse_args(argv)
    if args.grim_items < 0:
        parser.error("--grim-items must be 1 or more")
    results = []
    for path in args.paths:
        if not path.exists():
            parser.error(f"no such file: {path}")
        results.append(check_file(path, args.grim_items))
    total = sum(len(r["problems"]) for r in results)
    if args.json:
        json.dump({"files": results, "problems": total}, sys.stdout, ensure_ascii=False, indent=1)
        print()
    else:
        for result in results:
            print(f"\n{result['file']}")
            for p in result["problems"]:
                print(f"  {p['kind']:<10} line {p['line']}: {p['match']!r}: {p['message']}")
            for p in result["notes"]:
                print(f"  note       line {p['line']}: {p['match']!r}: {p['message']}")
        print(f"\n{total} number problem(s) across {len(results)} file(s).")
    return 1 if (args.strict and total) else 0


if __name__ == "__main__":
    for stream in (sys.stdout, sys.stderr):
        if hasattr(stream, "reconfigure"):
            stream.reconfigure(encoding="utf-8")
    raise SystemExit(main())
