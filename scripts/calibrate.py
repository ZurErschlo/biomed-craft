#!/usr/bin/env python3
"""Rebuild calibration.json and corpus.json from journal PDFs, saved article texts and Europe PMC.

Finds research articles from leading journals and their major sub-journals by
the DOI printed on the first two pages of each PDF (or in its file name), reads
article texts saved as Markdown with a labelled front matter (--texts), and
reads publisher versions of open-access articles from Europe PMC (JATS XML, by
PMCID). Cleans the text (reference lists, back matter, captions, running heads),
labels the study design, and records how often each rule in rules.json fires in
the prose, together with the style profile used by `scan.py --profile`. Only
statistics and identifiers are written to the repository; saved texts stay in
the git-ignored calibration-texts/ folder. PDFs need pdftotext (poppler).

    python3 calibrate.py ~/Zotero --texts calibration-texts --pmc corpus.json

A saved text starts with a front matter like this, followed by the text that
pdftotext extracts from the publisher PDF:

    ---
    doi: 10.1056/nejmoa0000000
    title: Title of the article
    year: 2021
    type: research
    design: trial
    ---
"""

from __future__ import annotations

import argparse
import concurrent.futures as futures
import datetime as dt
import json
import os
import re
import shutil
import subprocess
import sys
import urllib.error
import urllib.request
import xml.etree.ElementTree as ET
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import textstats as ts  # noqa: E402

# DOI prefix -> (family, journal). Order matters: first match wins.
JOURNALS = [
    (r"10\.1016/s0140-6736", "lancet", "Lancet"),
    (r"10\.1016/s1473-3099", "lancet", "Lancet Infect Dis"),
    (r"10\.1016/s2214-109x", "lancet", "Lancet Glob Health"),
    (r"10\.1016/s2468-2667", "lancet", "Lancet Public Health"),
    (r"10\.1016/s2213-2600", "lancet", "Lancet Respir Med"),
    (r"10\.1016/s2666-5247", "lancet", "Lancet Microbe"),
    (r"10\.1016/s2352-3018", "lancet", "Lancet HIV"),
    (r"10\.1016/s2589-7500", "lancet", "Lancet Digit Health"),
    (r"10\.1016/s1470-2045", "lancet", "Lancet Oncol"),
    (r"10\.1016/s1474-4422", "lancet", "Lancet Neurol"),
    (r"10\.1016/s2215-0366", "lancet", "Lancet Psychiatry"),
    (r"10\.1016/s2213-8587", "lancet", "Lancet Diabetes Endocrinol"),
    (r"10\.1016/s2468-1253", "lancet", "Lancet Gastroenterol Hepatol"),
    (r"10\.1016/s2352-3026", "lancet", "Lancet Haematol"),
    (r"10\.1016/s2665-9913", "lancet", "Lancet Rheumatol"),
    (r"10\.1016/s2352-4642", "lancet", "Lancet Child Adolesc Health"),
    (r"10\.1016/s2542-5196", "lancet", "Lancet Planet Health"),
    (r"10\.1016/s2666-7568", "lancet", "Lancet Healthy Longev"),
    (r"10\.1056/nejm", "nejm", "NEJM"),
    (r"10\.1001/jama\.\d", "jama", "JAMA"),
    (r"10\.1001/jama(?!networkopen|healthforum)[a-z]+", "jama", "JAMA specialty"),
    (r"10\.1136/bmj(?:[.-]|$)", "bmj", "BMJ"),
    (r"10\.7326/", "annals", "Ann Intern Med"),
    (r"10\.1038/s41586|10\.1038/nature\d", "nature", "Nature"),
    (r"10\.1038/s41591", "nature", "Nat Med"),
    (r"10\.1038/s41564", "nature", "Nat Microbiol"),
    (r"10\.1038/s41562", "nature", "Nat Hum Behav"),
    (r"10\.1038/s4158[78]|10\.1038/s4159[0-4]|10\.1038/s4155[6-9]|10\.1038/s4156[0-7]", "nature", "Nature research journal"),
    (r"10\.1038/s4156[8]|10\.1038/s4157\d|10\.1038/s4158[0-6]", "nature", "Nature Reviews"),
    (r"10\.1016/j\.cell\.", "cell", "Cell"),
    (r"10\.1126/scitranslmed", "science", "Sci Transl Med"),
    (r"10\.1126/science", "science", "Science"),
]
JOURNAL_PATTERNS = [(re.compile(p, re.IGNORECASE), f, j) for p, f, j in JOURNALS]
DOI = re.compile(r"10\.\d{4,9}/[^\s\"<>,;]+", re.IGNORECASE)
SKIP_DIRS = ("node_modules", ".git", ".venv", "site-packages", ".app", "__pycache__")
SUPPLEMENT_NAME = re.compile(
    r"mmc\d|_moesm|_esm|-s00\d|suppl|supp\d|supplement|appendix|supporting|_si[_.]|[._]sm[._]|checklist|mdar"
    r"|disclosure|data[-_ ]?sharing|reviewer|response",
    re.IGNORECASE,
)
SUPPLEMENT_START = re.compile(
    r"^\s*(?:Supplementary\s+(?:appendix|information|materials?|methods)|Supplement(?:ary|al)\s+Online\s+Content"
    r"|Supplemental\s+materials?|(?:Web\s*)?appendix\b|Supporting\s+information|Peer\s+Review\s+File"
    r"|Reporting\s+Summary|Data\s+Sharing\s+Statement|ICMJE\b|(?:MDAR\s+)?Reproducibility\s+Checklist)",
    re.IGNORECASE,
)
# Phrases are matched across line breaks, since pdftotext breaks lines inside them.
SUPPLEMENT_TEXT = re.compile(
    r"|".join(r"\s+".join(phrase.split()) for phrase in (
        "This appendix formed part of the original submission", "Supplementary Online Content",
        "Supplemental Online Content", "Supplementary Materials for",
        "provided by the authors to give readers additional information",
        "In the format provided by the authors and unedited", "ICMJE Form for Disclosure")),
    re.IGNORECASE,
)

HEADING_MAIN = {
    "introduction", "background", "methods", "method", "online methods", "materials and methods",
    "methods summary", "results", "discussion", "conclusion", "conclusions", "research in context",
    "summary", "abstract", "starmethods", "star methods", "method details", "experimental procedures",
    "experimental model and subject details", "experimental model and study participant details",
    "quantification and statistical analysis",
}
HEADING_REFERENCES = {"references", "references and notes", "bibliography", "methods references", "notes and references"}
HEADING_BACK = {
    "acknowledgements", "acknowledgments", "contributors", "author contributions", "declaration of interests",
    "competing interests", "data sharing", "data availability", "code availability", "funding",
    "role of the funding source", "ethics declarations", "additional information", "supplementary information",
    "reporting summary", "extended data", "peer review information", "reprints and permissions",
    "publisher's note", "publisher’s note", "open access", "rights and permissions", "article information",
    "conflict of interest disclosures", "funding/support", "role of the funder/sponsor", "group information",
    "data sharing statement", "additional contributions", "supplementary materials", "editor's note",
    "inclusion and ethics", "ethics", "consent for publication", "author information",
    "key resources table", "resource availability", "lead contact", "materials availability",
    "declaration of generative ai and ai-assisted technologies in the writing process",
    "data and code availability", "data and materials availability", "supplementary material",
    "associated data", "references and notes",
}
NOISE_LINE = re.compile(
    r"^(?:www\.|https?://|doi:|DOI|©|Copyright|Downloaded from|Vol\s+\d+|N Engl J Med|JAMA\.|BMJ \d{4}|"
    r"Nature \||Cell \d|Science \d|Articles$|Original Article$|Original Investigation$|RESEARCH$|Article$|"
    r"Published online|Accepted|Received|See Online|See Comment|For the|Correspondence to|\d+$)",
)
EUROPE_PMC = "https://www.ebi.ac.uk/europepmc/webservices/rest/{pmcid}/fullTextXML"
# Abstract types written by the journal or shown as extras, not part of the authors' prose.
SKIP_ABSTRACTS = {"teaser", "key-points", "graphical", "editor", "editor-summary", "web-summary", "toc",
                  "precis", "short", "author-highlights", "highlights", "in-brief"}
SKIP_ELEMENTS = {"table-wrap", "fig", "disp-formula", "inline-formula", "supplementary-material", "boxed-text",
                 "fn", "fn-group", "table", "graphic", "media", "disp-quote", "ref-list", "caption", "label"}
BACK_SEC_TYPES = {"supplementary-material", "supplementary-materials", "data-availability",
                  "data-availability-statement", "coi-statement", "funding-information", "author-contributions",
                  "ack", "ethics-statement", "display-objects", "associated-data", "history", "ref-list"}
MANUSCRIPT_TEXT = re.compile(r"Author\s+[Mm]anuscript|HHS\s+Public\s+Access|Europe\s+PMC\s+Funders\s+Group")
MIN_GROUP = 10
LIGATURES = {"ﬁ": "fi", "ﬂ": "fl", "ﬀ": "ff", "ﬃ": "ffi", "ﬄ": "ffl", "­": ""}


def find_pdfs(roots: list[Path]) -> list[Path]:
    found = []
    for root in roots:
        for directory, dirnames, filenames in os.walk(root):
            dirnames[:] = [d for d in dirnames if not any(s in d for s in SKIP_DIRS)]
            for name in filenames:
                if name.lower().endswith(".pdf"):
                    found.append(Path(directory) / name)
    return found


def pdf_text(path: Path, first: int | None = None, last: int | None = None) -> str:
    command = ["pdftotext", "-q"]
    if first:
        command += ["-f", str(first)]
    if last:
        command += ["-l", str(last)]
    try:
        result = subprocess.run(command + [str(path), "-"], capture_output=True, text=True, timeout=120)
    except (subprocess.TimeoutExpired, OSError):
        return ""
    text = result.stdout
    for old, new in LIGATURES.items():
        text = text.replace(old, new)
    return text


def doi_from_name(name: str) -> str:
    decoded = name.replace("%2528", "(").replace("%2529", ")").replace("%28", "(").replace("%29", ")")
    for pattern, prefix in (
        (r"(s4\d{4}-\d{3}-\d{5}-[\dx])", "10.1038/"),
        (r"(NEJM[a-z]{1,3}\d{5,8})", "10.1056/"),
        (r"(S\d{4}-\d{3}[\dX]\(\d{2}\)\d{5}-[\dX])", "10.1016/"),
        (r"((?:science|scitranslmed)\.[a-z]{1,4}\d{3,5})", "10.1126/"),
    ):
        match = re.search(pattern, decoded, re.IGNORECASE)
        if match:
            return (prefix + match.group(1)).lower()
    return ""


def identify(path: Path) -> dict | None:
    head = pdf_text(path, 1, 2)
    joined = re.sub(r"(10\.\d{4,9}/(?:\S*?[-/(])?)\s*\n\s*", r"\1", head)
    candidates = [d.rstrip(".)]") for d in DOI.findall(joined)]
    # A DOI-shaped file name names the article itself; the first DOI on the page can be a related article's
    # (Science prints its own DOI only at the end).
    from_name = doi_from_name(path.name)
    if from_name:
        candidates.insert(0, from_name)
    for doi in candidates:
        doi = doi.lower()
        for pattern, family, journal in JOURNAL_PATTERNS:
            if pattern.match(doi):
                supplement = (bool(SUPPLEMENT_NAME.search(path.name)) or bool(SUPPLEMENT_START.search(head[:400]))
                              or bool(SUPPLEMENT_TEXT.search(head[:3000])) or bool(MANUSCRIPT_TEXT.search(head[:3000])))
                return {"doi": doi, "family": family, "journal": journal, "path": str(path),
                        "supplement": supplement, "head": head}
    return None


def year_of(doi: str, text: str) -> int | None:
    match = re.search(r"s\d{4}-\d{3}[\dx]\((\d{2})\)", doi)
    if match:
        return 2000 + int(match.group(1))
    match = re.search(r"/s4\d{4}-0(\d{2})-", doi)
    if match:
        return 2000 + int(match.group(1))
    for pattern in (
        r"Published online[^0-9]{0,40}\d{1,2},?\s+((?:19|20)\d{2})",
        r"Published:\s*\d{1,2}\s+\w+\s+((?:19|20)\d{2})",
        r"©\s*((?:19|20)\d{2})", r"Copyright\s*©?\s*((?:19|20)\d{2})",
        r"N Engl J Med\s+((?:19|20)\d{2})", r"JAMA\.\s*((?:19|20)\d{2})", r"BMJ\s+((?:19|20)\d{2})",
        r"Science\s+\d+,\s*[\w–-]+\s*\(((?:19|20)\d{2})\)", r"\b\d{1,2}\s+[A-Z]{3,9}\s+((?:19|20)\d{2})\s+•\s+VOL", r"Sci\.\s*Transl\.\s*Med\.\s*\d+,\s*\w+\s*\(((?:19|20)\d{2})\)",
        r"Lancet[^\n]{0,40}?((?:19|20)\d{2})", r"Accepted[^0-9]{0,20}\d{1,2}\s+\w+\s+((?:19|20)\d{2})",
    ):
        match = re.search(pattern, text[:6000])
        if match:
            year = int(match.group(1))
            if 1990 <= year <= dt.date.today().year + 1:
                return year
    return None


def normalise_heading(line: str) -> str:
    return re.sub(r"[^a-z/’' ]", "", line.lower()).strip()


def clean_article(text: str) -> tuple[list[str], set[str]]:
    """Return prose paragraphs and the set of main headings seen."""
    lines = text.splitlines()
    kept: list[str] = []
    headings: set[str] = set()
    skipping = False
    for raw in lines:
        line = raw.strip()
        if not line:
            kept.append("")
            continue
        heading = normalise_heading(line)
        # A heading starts with a capital and has no digits or final full stop, apart from a section number;
        # "References (36-38)" in a list of supplementary materials and sentence ends are not headings.
        core = re.sub(r"^\d+(?:\.\d+)*\.?\s+", "", line)
        if not core[:1].isupper() or core.endswith(".") or re.search(r"\d", core):
            heading = ""
        if len(line) < 70 and heading in HEADING_REFERENCES:
            skipping = True
            kept.append("")
            continue
        if len(line) < 120 and heading in HEADING_BACK:
            skipping = True
            kept.append("")
            continue
        if len(line) < 70 and heading in HEADING_MAIN:
            headings.add(heading)
            skipping = False
            kept.append("")
            continue
        if skipping or NOISE_LINE.match(line):
            continue
        kept.append(line)
    paragraphs = []
    for _, paragraph in ts._paragraphs(list(enumerate(kept))):
        if ts.is_caption(paragraph) or re.match(r"^(?:Panel|Box)\s*\d*[:.]", paragraph):
            continue
        paragraph = re.sub(r"(?<=[a-z)\]%])\d{1,3}(?:[,–-]\d{1,3})*(?=[\s.,;:)])", "", paragraph)
        paragraph = re.sub(r"(?<=[a-z][.,;:])\d{1,3}(?:[,–-]\d{1,3})*(?=\s+[A-Z])", "", paragraph)
        paragraphs.append(paragraph)
    return paragraphs, headings


def fetch_jats(pmcid: str) -> str:
    """Europe PMC full text for one PMCID; falls back to curl when Python cannot verify TLS."""
    url = EUROPE_PMC.format(pmcid=pmcid)
    try:
        with urllib.request.urlopen(url, timeout=60) as response:
            return response.read().decode("utf-8", "replace")
    except (urllib.error.URLError, OSError, ValueError):
        pass
    if shutil.which("curl"):
        try:
            result = subprocess.run(["curl", "-sfL", "--max-time", "60", url], capture_output=True, timeout=90)
        except (subprocess.TimeoutExpired, OSError):
            return ""
        if result.returncode == 0:
            return result.stdout.decode("utf-8", "replace")
    return ""


def is_manuscript(front: ET.Element) -> bool:
    """True for author manuscripts, which have not been copyedited by the journal."""
    if front.find(".//article-id[@pub-id-type='manuscript']") is not None:
        return True
    for journal_id in front.iter("journal-id"):
        if (journal_id.text or "").strip().lower() in {"nihpa", "gatesmanu", "ukpmcpa", "wtpa"}:
            return True
    for meta in front.iter("custom-meta"):
        if (meta.findtext("meta-name") or "").strip() == "is-manuscript":
            return (meta.findtext("meta-value") or "").strip().lower() == "yes"
    return bool(MANUSCRIPT_TEXT.search(" ".join(front.itertext())))


def _element_text(element: ET.Element) -> str:
    parts: list[str] = []

    def visit(node: ET.Element) -> None:
        skip = node.tag in SKIP_ELEMENTS or (node.tag == "xref" and node.get("ref-type") in {"bibr", "fn"})
        if not skip:
            parts.append(node.text or "")
            for child in node:
                visit(child)
        parts.append(node.tail or "")

    parts.append(element.text or "")
    for child in element:
        visit(child)
    text = re.sub(r"\s+", " ", "".join(parts)).strip()
    text = re.sub(r"\s*[\[(]\s*(?:[,;–-]\s*)*[\])]", "", text)
    return re.sub(r"\s+([.,;:])", r"\1", text)


def jats_article(xml: str) -> dict | None:
    """DOI, year, headings and prose paragraphs of a publisher-version JATS article."""
    try:
        root = ET.fromstring(xml)
    except ET.ParseError:
        return None
    front = root.find("front")
    if front is None or is_manuscript(front):
        return None
    doi = (front.findtext(".//article-meta/article-id[@pub-id-type='doi']") or "").strip().lower()
    years = [int(y) for y in (d.findtext("year") for d in front.iter("pub-date")) if y and y.strip().isdigit()]
    paragraphs: list[str] = []
    headings: set[str] = set()
    for abstract in front.iter("abstract"):
        if abstract.get("abstract-type", "") not in SKIP_ABSTRACTS:
            paragraphs.extend(_element_text(p) for p in abstract.iter("p"))

    def walk(node: ET.Element) -> None:
        for child in node:
            if child.tag in SKIP_ELEMENTS:
                continue
            if child.tag == "sec":
                title = normalise_heading(child.findtext("title") or "")
                if (child.get("sec-type", "").lower() in BACK_SEC_TYPES or title in HEADING_BACK
                        or title in HEADING_REFERENCES):
                    continue
                if title in HEADING_MAIN:
                    headings.add(title)
                walk(child)
            elif child.tag == "p":
                paragraphs.append(_element_text(child))
            else:
                walk(child)

    body = root.find("body")
    if body is not None:
        walk(body)
    return {"doi": doi, "year": min(years) if years else None, "headings": headings,
            "article_type": root.get("article-type", ""), "paragraphs": [p for p in paragraphs if p]}


def read_pmc_list(path: Path) -> list[tuple[str, str]]:
    """PMCIDs with design labels, from corpus.json or from a text file of 'PMCID design' lines."""
    text = path.read_text(encoding="utf-8")
    if path.suffix == ".json":
        return [(p["pmcid"], p.get("design", "")) for p in json.loads(text) if p.get("pmcid")]
    items = []
    for line in text.splitlines():
        fields = line.split("#", 1)[0].split()
        if fields and re.match(r"PMC\d+$", fields[0]):
            items.append((fields[0], fields[1] if len(fields) > 1 else ""))
    return items


def read_text(path: Path) -> tuple[dict, str] | None:
    """Front matter and body of an article text saved as Markdown."""
    text = path.read_text(encoding="utf-8", errors="replace")
    found = re.match(r"---\n(.*?)\n---\n", text, re.DOTALL)
    if not found:
        return None
    meta = {}
    for line in found.group(1).splitlines():
        key, _, value = line.partition(":")
        meta[key.strip()] = value.strip()
    return (meta, text[found.end():]) if meta.get("doi") else None


def good_sentence(sentence: str) -> bool:
    tokens = sentence.split()
    if len(tokens) < 5 or not re.match(r"^[A-Z(\[“\"]", sentence) or not re.search(r"[.!?][\"”')\]]?$", sentence):
        return False
    alpha = sum(bool(re.search(r"[A-Za-z]{2,}", t)) for t in tokens)
    return alpha / len(tokens) >= 0.6


def measure(paragraphs: list[str], rules: list[ts.Rule]) -> dict | None:
    """Sentences, words, rule hits and style profile of a list of prose paragraphs."""
    sentences, prose = [], []
    for paragraph in paragraphs:
        kept = [s for s in ts.split_sentences(paragraph) if good_sentence(s)]
        if kept:
            sentences.extend(kept)
            prose.append(" ".join(kept))
    words = len(ts.words(" ".join(sentences)))
    if words < 800:
        return None
    hits = {}
    for rule in rules:
        if "prose" not in rule.scopes or rule.formats:
            continue
        count = 0
        for paragraph in prose:
            count += len(ts.rule_matches(rule, paragraph))
        if count:
            hits[rule.id] = count
    return {"words": words, "sentences": len(sentences), "profile": ts.profile(sentences), "hits": hits,
            "opening": " ".join(prose)[:60000]}


METHODS_HEADINGS = {"methods", "online methods", "materials and methods", "methods summary", "starmethods",
                    "star methods", "method details", "experimental procedures"}


def is_research_article(headings: set[str]) -> bool:
    return bool(headings & METHODS_HEADINGS) and ("results" in headings or "discussion" in headings)


def finish(base: dict, measured: dict, kind: str, design: str) -> dict:
    if kind == "research" and not design:
        design = ts.detect_design(measured["opening"])[0]
    elif kind == "review":
        design = "review"
    measured = {k: v for k, v in measured.items() if k != "opening"}
    return {**base, "type": kind, "design": design if kind != "other" else "", **measured}


def analyse(record: dict, rules: list[ts.Rule]) -> dict | None:
    text = pdf_text(Path(record["path"]))
    paragraphs, headings = clean_article(text)
    measured = measure(paragraphs, rules)
    if measured is None:
        return None
    is_review = record["journal"] == "Nature Reviews" or bool(
        re.search(r"^\s*(?:Review|Review Article|Seminar|Series|Clinical Review|Perspective|Comment)\s*$",
                  record["head"][:600], re.MULTILINE))
    kind = "research" if is_research_article(headings) and not is_review else ("review" if is_review else "other")
    base = {"doi": record["doi"], "family": record["family"], "journal": record["journal"],
            "year": year_of(record["doi"], record["head"] + text[:4000])}
    return finish(base, measured, kind, "")


def analyse_text(item: tuple[dict, str], rules: list[ts.Rule]) -> dict | None:
    meta, body = item
    doi = meta["doi"].lower()
    match = next(((f, j) for pattern, f, j in JOURNAL_PATTERNS if pattern.match(doi)), None)
    if match is None:
        return None
    paragraphs, headings = clean_article(body)
    measured = measure(paragraphs, rules)
    if measured is None:
        return None
    design = meta.get("design", "")
    kind = meta.get("type", "")
    if not kind:
        kind = "review" if design == "review" else ("research" if design or is_research_article(headings) else "other")
    year = int(meta["year"]) if meta.get("year", "").isdigit() else year_of(doi, body[:6000])
    base = {"doi": doi, "family": match[0], "journal": match[1], "year": year}
    return finish(base, measured, kind, design)


def analyse_pmc(item: tuple[str, str], rules: list[ts.Rule]) -> dict | None:
    pmcid, design = item
    article = jats_article(fetch_jats(pmcid))
    if not article or not article["doi"]:
        return None
    match = next(((f, j) for pattern, f, j in JOURNAL_PATTERNS if pattern.match(article["doi"])), None)
    if match is None:
        return None
    measured = measure(article["paragraphs"], rules)
    if measured is None:
        return None
    if design:
        kind = "review" if design == "review" else "research"
    else:
        is_review = article["article_type"] in {"review-article", "systematic-review"} and \
            not is_research_article(article["headings"])
        kind = "review" if is_review else ("research" if is_research_article(article["headings"]) else "other")
    base = {"doi": article["doi"], "pmcid": pmcid, "family": match[0], "journal": match[1], "year": article["year"]}
    return finish(base, measured, kind, design)


def summarise(papers: list[dict], rule_ids: list[str]) -> dict:
    words = sum(p["words"] for p in papers)
    summary = {"papers": len(papers), "words": words, "metrics": {}}
    for metric in ts.PROFILE_METRICS:
        values = [p["profile"][metric] for p in papers if metric in p["profile"]]
        if values:
            summary["metrics"][metric] = {
                q: round(ts._quantile(values, v), 3)
                for q, v in (("p10", 0.10), ("p25", 0.25), ("p50", 0.50), ("p75", 0.75), ("p90", 0.90))
            }
    summary["rules"] = {}
    for rule_id in rule_ids:
        total = sum(p["hits"].get(rule_id, 0) for p in papers)
        with_hit = sum(1 for p in papers if p["hits"].get(rule_id))
        summary["rules"][rule_id] = {
            "per_10k_words": round(total * 10000 / words, 3) if words else 0.0,
            "paper_share": round(with_hit / len(papers), 3) if papers else 0.0,
        }
    return summary


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("roots", nargs="*", type=Path, help="folders to search for PDFs")
    parser.add_argument("--texts", type=Path, action="append", default=[],
                        help="folders of article texts saved as Markdown with a front matter (doi, year, type, design)")
    parser.add_argument("--pmc", type=Path, action="append", default=[],
                        help="Europe PMC articles to add: corpus.json, or a text file of 'PMCID design' lines")
    parser.add_argument("--out-dir", type=Path, default=Path(__file__).resolve().parent,
                        help="where to write calibration.json and corpus.json (default: this folder)")
    parser.add_argument("--workers", type=int, default=8)
    args = parser.parse_args(argv)
    if not args.roots and not args.pmc and not args.texts:
        parser.error("give folders of PDFs, --texts, --pmc, or a combination")
    if args.roots and not shutil.which("pdftotext"):
        parser.error("pdftotext (poppler) is required for PDFs")

    _, rules = ts.load_rules()
    prose_rules = [r for r in rules if r.kind == "regex" and "prose" in r.scopes and not r.formats and not r.docs]
    rule_ids = [r.id for r in prose_rules]
    texts = [item for folder in args.texts for item in map(read_text, sorted(folder.expanduser().glob("*.md")))
             if item]
    with futures.ThreadPoolExecutor(args.workers) as pool:
        analysed = [a for a in pool.map(lambda i: analyse_text(i, prose_rules), texts) if a]
    if texts:
        print(f"{len(analysed)} of {len(texts)} saved texts kept", file=sys.stderr)
    known = {p["doi"] for p in analysed}
    pdfs = find_pdfs([r.expanduser() for r in args.roots])
    print(f"Scanning {len(pdfs)} PDFs for journal DOIs", file=sys.stderr)
    with futures.ThreadPoolExecutor(args.workers) as pool:
        identified = [r for r in pool.map(identify, pdfs) if r]
    articles: dict[str, dict] = {}
    supplements = 0
    for record in identified:
        if record["doi"] in known:
            continue
        if record["supplement"]:
            supplements += 1
            continue
        current = articles.get(record["doi"])
        if current is None or os.path.getsize(record["path"]) > os.path.getsize(current["path"]):
            articles[record["doi"]] = record
    print(f"{len(articles)} unique articles ({supplements} supplements or author manuscripts skipped)", file=sys.stderr)
    with futures.ThreadPoolExecutor(args.workers) as pool:
        analysed += [a for a in pool.map(lambda r: analyse(r, prose_rules), articles.values()) if a]
    pmc_items = list(dict.fromkeys(item for path in args.pmc for item in read_pmc_list(path)))
    if pmc_items:
        print(f"Reading {len(pmc_items)} Europe PMC articles", file=sys.stderr)
        known = {p["doi"] for p in analysed}
        with futures.ThreadPoolExecutor(args.workers) as pool:
            from_pmc = [a for a in pool.map(lambda i: analyse_pmc(i, prose_rules), pmc_items) if a]
        skipped = len(pmc_items) - len(from_pmc)
        for article in from_pmc:
            if article["doi"] not in known:
                analysed.append(article)
                known.add(article["doi"])
        print(f"{len(from_pmc)} Europe PMC articles kept ({skipped} author manuscripts, other journals or "
              f"unreadable)", file=sys.stderr)

    research = [p for p in analysed if p["type"] == "research"]
    groups = {"core": research}
    for family in sorted({p["family"] for p in research}):
        groups[family] = [p for p in research if p["family"] == family]
    for design in ts.DESIGNS:
        members = [p for p in analysed if p["design"] == design]
        if len(members) >= MIN_GROUP:
            groups[design] = members
    groups["core_before_2023"] = [p for p in research if p["year"] and p["year"] < 2023]
    groups["core_2023_on"] = [p for p in research if p["year"] and p["year"] >= 2023]
    groups["reviews_and_other"] = [p for p in analysed if p["type"] != "research"]

    calibration = {
        "version": 1,
        "generated": dt.date.today().isoformat(),
        "description": "Rule rates and style profile of research articles in leading journals and their major "
                       "sub-journals. Built by calibrate.py; statistics only.",
        "method": {
            "selection": "PDFs: first DOI on pages 1-2 (or in the file name) matched to the journal list in "
                         "calibrate.py. Saved texts: publisher PDFs converted to text, labelled by hand, kept "
                         "outside git. Europe PMC: publisher versions of open-access articles, by PMCID. "
                         "Supplements, author manuscripts and duplicates removed.",
            "cleaning": "PDFs through pdftotext, JATS XML through its structure; reference lists, back matter, "
                        "running heads, captions, tables, boxes and citation markers removed; only complete "
                        "sentences kept.",
            "research_article": "Has a Methods heading and a Results or Discussion heading; reviews excluded.",
            "design": "Labelled when the article was selected, otherwise guessed by textstats.detect_design; "
                      "design groups with fewer than 10 articles are not written.",
            "metrics": "Per-paper values; quantiles across papers. Rule rates are pooled per 10 000 words.",
        },
        "groups": {name: summarise(papers, rule_ids) for name, papers in groups.items() if papers},
    }
    fields = ("doi", "pmcid", "family", "journal", "year", "type", "design", "words", "sentences")
    corpus = [
        {k: p[k] for k in fields if k in p}
        for p in sorted(analysed, key=lambda p: (p["family"], p["year"] or 0, p["doi"]))
    ]
    args.out_dir.mkdir(parents=True, exist_ok=True)
    (args.out_dir / "calibration.json").write_text(json.dumps(calibration, indent=1) + "\n", encoding="utf-8")
    (args.out_dir / "corpus.json").write_text(json.dumps(corpus, indent=1) + "\n", encoding="utf-8")
    print(f"{len(research)} research articles, {len(analysed) - len(research)} other items; wrote "
          f"{args.out_dir / 'calibration.json'}", file=sys.stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
