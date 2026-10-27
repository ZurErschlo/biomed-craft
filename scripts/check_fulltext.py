#!/usr/bin/env python3
"""Check that a folder of full-text PDFs matches a reference list.

For each record in the reference list (RIS, BibTeX, CSV, or one DOI per line),
the script looks for the PDF that holds that article, by DOI first and then by
title, and reports:

  - records with no matching PDF;
  - PDFs that match no record (the wrong article was retrieved);
  - PDFs whose file name points to one record while the content is another;
  - more than one PDF for the same record;
  - supplements and author manuscripts filed as the article.

It reads the first two pages of each PDF with pdftotext (poppler) and never
changes a file.

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
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from calibrate import DOI, SUPPLEMENT_START, SUPPLEMENT_TEXT, pdf_text  # noqa: E402

TITLE_COVERAGE = 0.85


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


def title_coverage(title: str, text: str) -> float:
    words = [w for w in normalise(title).split() if len(w) > 3]
    if len(words) < 3:
        return 0.0
    present = set(normalise(text).split())
    return sum(w in present for w in words) / len(words)


def describe(text: str) -> dict:
    joined = re.sub(r"(10\.\d{4,9}/(?:\S*?[-/(])?)\s*\n\s*", r"\1", text)
    return {"dois": {clean_doi(d) for d in DOI.findall(joined)}, "text": text,
            "supplement": bool(SUPPLEMENT_START.search(text[:400]) or SUPPLEMENT_TEXT.search(text[:3000]))}


def match(records: list[dict], documents: dict[str, str]) -> dict:
    """Match records to documents given as {file name: text of the first pages}."""
    described = {name: describe(text) for name, text in documents.items()}
    by_record: dict[str, list[str]] = {r["id"]: [] for r in records}
    by_document: dict[str, str] = {}
    notes: list[dict] = []
    for name, info in described.items():
        best, score = None, 0.0
        for record in records:
            if record["doi"] and record["doi"] in info["dois"]:
                best, score = record, 2.0
                break
            coverage = title_coverage(record.get("title", ""), info["text"][:6000])
            if coverage > score:
                best, score = record, coverage
        if best is not None and score >= TITLE_COVERAGE:
            by_record[best["id"]].append(name)
            by_document[name] = best["id"]
            if score < 2.0:
                lowered = info["text"][:6000].lower()
                if best["surname"] and best["surname"] not in lowered:
                    notes.append({"file": name, "record": best["id"],
                                  "problem": "title matches but the first author is not on the first pages"})
                elif best.get("year") and best["year"] not in info["text"][:6000]:
                    notes.append({"file": name, "record": best["id"],
                                  "problem": "title matches but the year is not on the first pages"})
        if info["supplement"]:
            notes.append({"file": name, "record": by_document.get(name, ""),
                          "problem": "looks like a supplement or an author manuscript"})
        stem = normalise(Path(name).stem)
        for record in records:
            tokens = [t for t in (record["doi"].replace("/", " "), normalise(record["id"])) if len(t) > 4]
            if any(normalise(t) in stem for t in tokens) and by_document.get(name) not in (None, record["id"]):
                notes.append({"file": name, "record": record["id"],
                              "problem": f"file name points to {record['id']} but the content is {by_document[name]}"})
    return {
        "missing": [rid for rid, files in by_record.items() if not files],
        "duplicates": {rid: files for rid, files in by_record.items() if len(files) > 1},
        "unmatched_files": sorted(name for name in described if name not in by_document),
        "notes": notes,
        "matched": {rid: files for rid, files in by_record.items() if len(files) == 1},
    }


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
    documents = {str(p.relative_to(args.folder)): pdf_text(p, 1, 2) for p in sorted(args.folder.rglob("*.pdf"))}
    result = match(records, documents)
    problems = len(result["missing"]) + len(result["duplicates"]) + len(result["unmatched_files"]) + len(result["notes"])
    if args.json:
        json.dump({"records": len(records), "files": len(documents), **result}, sys.stdout, ensure_ascii=False, indent=1)
        print()
    else:
        print(f"{len(records)} records, {len(documents)} PDFs, {len(result['matched'])} matched one to one.")
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
