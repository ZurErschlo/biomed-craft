#!/usr/bin/env python3
"""Check that a folder of full-text PDFs matches a reference list.

For each record in the reference list (RIS, BibTeX, CSV, or one DOI per line),
the script looks for the PDF that holds that article: the record's title
printed at the top of the first page, or, for records without a title, its DOI
as the first DOI on the page. It reports:

  - records with no matching PDF, including records found only in a
    supplement or in a page that cites them (a patient page, a correction);
  - PDFs that match no record (the wrong article was retrieved);
  - PDFs whose file name points to one record while the content is another;
  - more than one PDF for the same record;
  - supplements, forms and author manuscripts, and PDFs of one or two pages.

It reads the first two pages of each PDF with pdftotext and the page count
with pdfinfo (poppler), and never changes a file.

Examples:
  python3 check_fulltext.py included.ris fulltexts/
  python3 check_fulltext.py --json zotero_export.csv pdfs/
"""

from __future__ import annotations

import argparse
import csv
import json
import re
import shutil
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from calibrate import DOI, MANUSCRIPT_TEXT, SUPPLEMENT_NAME, SUPPLEMENT_START, SUPPLEMENT_TEXT, pdf_text  # noqa: E402

TITLE_COVERAGE = 0.85
HEAD_CHARS = 1500
# Short pages that name an article without being it. A banner such as "Erratum 22 April 2022. See Erratum."
# on a corrected article does not count.
NOT_ARTICLE = re.compile(
    r"^\s*(?:(?:JAMA\s+)?Patient\s+Page|(?:Erratum|Errata|Corrigendum|Correction)\b(?!\s+(?:\d|published|issued))"
    r"|Error\s+in\b|Notice\s+of\s+Retraction|Retraction\s+(?:Note|Notice)|Expression\s+of\s+Concern)",
    re.IGNORECASE | re.MULTILINE,
)


def normalise(text: str) -> str:
    return re.sub(r"\s+", " ", re.sub(r"[^a-z0-9]+", " ", text.lower())).strip()


def clean_doi(doi: str) -> str:
    doi = re.sub(r"^(?:https?://(?:dx\.)?doi\.org/|doi:\s*)", "", doi.strip(), flags=re.IGNORECASE)
    return doi.rstrip(".);,]").lower()


def read_records(path: Path) -> list[dict]:
    text = path.read_text(encoding="utf-8-sig", errors="replace")
    suffix = path.suffix.lower()
    records: list[dict] = []
    if suffix in (".ris", ".nbib") or re.search(r"^TY  - ", text, re.MULTILINE):
        current: dict = {}
        for line in text.splitlines():
            tag, _, value = line.partition("  - ")
            tag, value = tag.strip(), value.strip()
            if tag == "TY":
                current = {"authors": []}
            elif tag in ("TI", "T1") and not current.get("title"):
                current["title"] = value
            elif tag in ("AU", "A1"):
                current["authors"].append(value)
            elif tag in ("PY", "Y1", "DA") and not current.get("year"):
                current["year"] = value[:4]
            elif tag == "DO":
                current["doi"] = value
            elif tag in ("ID", "AN") and not current.get("id"):
                current["id"] = value
            elif tag == "ER":
                records.append(current)
                current = {}
    elif suffix == ".bib":
        for entry in re.finditer(r"@\w+\s*\{\s*([^,]+),(.*?)\n\}", text, re.DOTALL):
            fields = dict((k.lower(), v.strip()) for k, v in
                          re.findall(r"(\w+)\s*=\s*[{\"]((?:[^{}\"]|\{[^{}]*\})*)[}\"]", entry.group(2)))
            records.append({"id": entry.group(1).strip(), "title": fields.get("title", "").replace("{", "").replace("}", ""),
                            "authors": [a.strip() for a in fields.get("author", "").split(" and ") if a.strip()],
                            "year": fields.get("year", "")[:4], "doi": fields.get("doi", "")})
    elif suffix in (".csv", ".tsv"):
        rows = csv.DictReader(text.splitlines(), delimiter="\t" if suffix == ".tsv" else ",")
        for row in rows:
            lower = {k.strip().lower(): (v or "").strip() for k, v in row.items() if k}
            pick = lambda *names: next((lower[n] for n in names if lower.get(n)), "")  # noqa: E731
            records.append({"id": pick("id", "key", "record", "record id", "covidence #"),
                            "title": pick("title", "article title"),
                            "authors": [pick("author", "authors", "first author")],
                            "year": pick("year", "publication year", "py")[:4], "doi": pick("doi")})
    else:
        records = [{"doi": line.strip()} for line in text.splitlines() if DOI.search(line)]
    for number, record in enumerate(records, start=1):
        record.setdefault("id", "")
        record["id"] = record["id"] or f"record {number}"
        record["doi"] = clean_doi(record.get("doi", ""))
        authors = record.get("authors") or [""]
        record["surname"] = re.split(r"[,\s]", authors[0].strip())[0].lower() if authors[0] else ""
    return records


def title_words(title: str) -> list[str]:
    return [w for w in normalise(title).split() if len(w) > 3]


def title_coverage(title: str, text: str) -> float:
    words = title_words(title)
    if len(words) < 3:
        return 0.0
    present = set(normalise(text).split())
    return sum(w in present for w in words) / len(words)


def in_order(words: list[str], tokens: list[str]) -> int:
    """Length of the longest common subsequence of two word lists."""
    previous = [0] * (len(tokens) + 1)
    for word in words:
        current = [0]
        for j, token in enumerate(tokens):
            current.append(previous[j] + 1 if word == token else max(previous[j + 1], current[j]))
        previous = current
    return previous[-1]


def title_at_top(title: str, text: str) -> tuple[float, int]:
    """Share of the title's words printed in order and close together near the top of the first page, and where."""
    words = title_words(title)
    if len(words) < 3:
        return 0.0, 0
    tokens = [w for w in normalise(text[:HEAD_CHARS]).split() if len(w) > 3]
    wanted = set(words)
    best, position = 0, 0
    for start, token in enumerate(tokens):
        if token in wanted:
            found = in_order(words, tokens[start:start + 2 * len(words)])
            if found > best:
                best, position = found, start
    return best / len(words), position


def describe(name: str, text: str) -> dict:
    joined = re.sub(r"(10\.\d{4,9}/(?:\S*?[-/(])?)\s*\n\s*", r"\1", text)
    found = [clean_doi(d) for d in DOI.findall(joined)]
    if MANUSCRIPT_TEXT.search(text[:3000]):
        kind = "manuscript"
    elif (SUPPLEMENT_NAME.search(Path(name).name) or SUPPLEMENT_START.search(text[:400])
          or SUPPLEMENT_TEXT.search(text[:3000])):
        kind = "supplement"
    elif NOT_ARTICLE.search(text[:300]):
        kind = "notice"
    else:
        kind = "article"
    # The first DOI on the page is usually the article's own; later ones are often cited references.
    return {"primary": found[0] if found else "", "dois": set(found), "kind": kind}


def match(records: list[dict], documents: dict[str, str], pages: dict[str, int] | None = None) -> dict:
    """Match records to documents given as {file name: text of the first pages}, with optional page counts."""
    pages = pages or {}
    articles: dict[str, list[str]] = {r["id"]: [] for r in records}
    supplements: dict[str, list[str]] = {r["id"]: [] for r in records}
    owner: dict[str, str] = {}
    notes: list[dict] = []
    for name, text in documents.items():
        info = describe(name, text)
        if info["kind"] == "notice" and pages.get(name, 0) > 3:
            info["kind"] = "article"
        best, best_key, cited = None, None, None
        for record in records:
            top, position = title_at_top(record.get("title", ""), text)
            primary = bool(record["doi"]) and record["doi"] == info["primary"]
            titled = len(title_words(record.get("title", ""))) >= 3
            if top >= TITLE_COVERAGE or (primary and not titled):
                key = (primary, top, -position)
                if best_key is None or key > best_key:
                    best, best_key = record, key
            elif cited is None and ((record["doi"] and record["doi"] in info["dois"])
                                    or title_coverage(record.get("title", ""), text[:6000]) >= TITLE_COVERAGE):
                cited = record
        if best is None:
            if cited is not None and info["kind"] != "supplement":
                notes.append({"file": name, "record": cited["id"],
                              "problem": "names this record but is not the article: its title is not at the top"})
            elif cited is not None:
                supplements[cited["id"]].append(name)
                owner[name] = cited["id"]
            elif info["kind"] == "supplement":
                notes.append({"file": name, "record": "", "problem": "a supplement or form of no listed record"})
            continue
        if info["kind"] == "supplement":
            supplements[best["id"]].append(name)
            owner[name] = best["id"]
            continue
        if info["kind"] == "notice":
            notes.append({"file": name, "record": best["id"],
                          "problem": "a correction, retraction notice or patient page, not the article"})
            continue
        articles[best["id"]].append(name)
        owner[name] = best["id"]
        if info["kind"] == "manuscript":
            notes.append({"file": name, "record": best["id"], "problem": "an author manuscript, not the published version"})
        if 0 < pages.get(name, 0) <= 2:
            notes.append({"file": name, "record": best["id"],
                          "problem": f"only {pages[name]} page(s): check that this is the full text, not an abstract or a "
                                     "first-page preview"})
        if best["doi"] != info["primary"]:
            lowered = text[:6000].lower()
            if best["surname"] and best["surname"] not in lowered:
                notes.append({"file": name, "record": best["id"],
                              "problem": "title matches but the first author is not on the first pages"})
            elif best.get("year") and best["year"] not in text[:6000]:
                notes.append({"file": name, "record": best["id"],
                              "problem": "title matches but the year is not on the first pages"})
    for name in documents:
        stem = normalise(Path(name).stem)
        for record in records:
            tokens = [t for t in (record["doi"].replace("/", " "), normalise(record["id"])) if len(t) > 4]
            if any(normalise(t) in stem for t in tokens) and owner.get(name) not in (None, record["id"]):
                notes.append({"file": name, "record": record["id"],
                              "problem": f"file name points to {record['id']} but the content is {owner[name]}"})
    return {
        "missing": [rid for rid, files in articles.items() if not files],
        "duplicates": {rid: files for rid, files in articles.items() if len(files) > 1},
        "unmatched_files": sorted(name for name in documents if name not in owner),
        "notes": notes,
        "matched": {rid: files for rid, files in articles.items() if len(files) == 1},
        "supplements": {rid: files for rid, files in supplements.items() if files},
    }


def page_count(path: Path) -> int:
    """Pages in a PDF, or 0 when pdfinfo is not available."""
    if not shutil.which("pdfinfo"):
        return 0
    try:
        output = subprocess.run(["pdfinfo", str(path)], capture_output=True, text=True, timeout=60).stdout
    except (subprocess.TimeoutExpired, OSError):
        return 0
    found = re.search(r"^Pages:\s+(\d+)", output, re.MULTILINE)
    return int(found.group(1)) if found else 0


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("references", type=Path, help="RIS, BibTeX, CSV or a list of DOIs")
    parser.add_argument("folder", type=Path, help="folder of PDFs (searched recursively)")
    parser.add_argument("--json", action="store_true", help="print JSON")
    parser.add_argument("--strict", action="store_true", help="exit with status 1 unless every record has one matching PDF")
    args = parser.parse_args(argv)
    if not shutil.which("pdftotext"):
        parser.error("pdftotext (poppler) is required")
    records = read_records(args.references)
    paths = {str(p.relative_to(args.folder)): p for p in sorted(args.folder.rglob("*.pdf"))}
    documents = {name: pdf_text(path, 1, 2) for name, path in paths.items()}
    result = match(records, documents, {name: page_count(path) for name, path in paths.items()})
    problems = len(result["missing"]) + len(result["duplicates"]) + len(result["unmatched_files"]) + len(result["notes"])
    if args.json:
        json.dump({"records": len(records), "files": len(documents), **result}, sys.stdout, ensure_ascii=False, indent=1)
        print()
    else:
        supplements = sum(len(files) for files in result["supplements"].values())
        print(f"{len(records)} records, {len(documents)} PDFs: {len(result['matched'])} matched one to one, "
              f"{len(result['missing'])} missing, {supplements} supplements or forms, {len(result['notes'])} to check.")
        for rid in result["missing"]:
            print(f"  missing       {rid}")
        for rid, files in result["duplicates"].items():
            print(f"  duplicate     {rid}: {', '.join(files)}")
        for name in result["unmatched_files"]:
            print(f"  no record     {name}")
        for note in result["notes"]:
            print(f"  check         {note['file']}: {note['problem']}")
    return 1 if (args.strict and problems) else 0


if __name__ == "__main__":
    for stream in (sys.stdout, sys.stderr):
        if hasattr(stream, "reconfigure"):
            stream.reconfigure(encoding="utf-8")
    raise SystemExit(main())
