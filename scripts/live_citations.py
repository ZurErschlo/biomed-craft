#!/usr/bin/env python3
"""Turn the citations of a Markdown manuscript into live Zotero or EndNote citations in Word.

Pandoc citations ([@smith2020], [@smith2020; @lee2021]) become, in a copy of the
Markdown file:

  zotero   Zotero citation fields, written as raw OpenXML and linked to the items
           of the researcher's Zotero library, and a bibliography field where the
           reference list goes (the ::: {#refs} ::: div, or the end of the file);
  endnote  EndNote temporary citations ({Smith, 2020 #12}) with the record numbers
           of an EndNote XML export of the library that Word will use.

Build the Word file from the copy with the project's own pandoc command, without
--citeproc. For Zotero, write the document preferences (the citation style) into the
Word file with `prefs`, then run Refresh in Word (the ZoteroRefresh macro). For EndNote,
click Update Citations and Bibliography in Word once. `check` then confirms that every
citation in the Word file is a live field.

Zotero items are looked up through Better BibTeX on Zotero's local port
(127.0.0.1:23119): by citation key, then by the DOI and title of the entry in the
bibliography file (CSL JSON; convert BibTeX with `pandoc refs.bib -t csljson -o refs.json`).
Better BibTeX does not search the DOI field, so the title is searched and the DOI compared.
The library is read, never changed. The conversion is all or nothing: an unknown key, a
citation that matches two items, a citation with a locator, prefix or suffix, or a bare
in-text @key stops it; nothing is written, and each one is listed with its line.

Examples:
  python3 live_citations.py zotero manuscript.md --bibliography references.json -o manuscript.zotero.md
  python3 live_citations.py endnote manuscript.md --library library.xml --bibliography references.json -o manuscript.endnote.md
  python3 live_citations.py prefs manuscript.docx --style nature
  python3 live_citations.py check manuscript.docx

Exit status: 0 on success, 1 when the conversion stops or `check` finds citations that are
not live fields, 2 for usage errors, 3 when Zotero does not answer.
"""

from __future__ import annotations

import argparse
import html
import json
import os
import random
import re
import string
import sys
import tempfile
import urllib.error
import urllib.request
import xml.etree.ElementTree as ET
import zipfile
from dataclasses import dataclass, field
from pathlib import Path
from typing import Callable

sys.path.insert(0, str(Path(__file__).resolve().parent))
import check_preservation as cp  # noqa: E402
import check_references as cr  # noqa: E402
import textstats as ts  # noqa: E402

ZOTERO_URL = "http://127.0.0.1:23119"
CSL_SCHEMA = "https://github.com/citation-style-language/schema/raw/master/csl-citation.json"
STYLE_BASE = "http://www.zotero.org/styles/"

# Pandoc citation keys: a letter, digit or _, then word characters and internal punctuation.
KEY = r"\w(?:\w|[:.#$%&+?<>~/-]+(?=\w))*"
CITE_KEY = re.compile(rf"(?<![\w.])-?@({KEY})")
PLAIN_ITEM = re.compile(rf"@({KEY})")
GROUP = re.compile(r"(?<!\\)\[([^\[\]]*)\](?![(\[{:])")
BARE = re.compile(rf"(?<![\w\[@.\\-])@({KEY})")
FENCE = re.compile(r"^ {0,3}(`{3,}|~{3,})")
FRONT_MATTER = re.compile(r"\A---[ \t]*\n.*?\n(?:---|\.\.\.)[ \t]*(?:\n|\Z)", re.DOTALL)
COMMENT = re.compile(r"<!--.*?-->", re.DOTALL)
INLINE_CODE = re.compile(r"(`+)(?!`)(.+?)(?<!`)\1(?!`)")
REFS_DIV = re.compile(r"^(:{3,})[ \t]*\{#refs\b[^}\n]*\}[ \t]*\n(.*?)^\1:*[ \t]*\n?", re.MULTILINE | re.DOTALL)

TEMPORARY = re.compile(r"\{[^{}\n]*#\d+[^{}\n]*\}")
PANDOC_LEFT = re.compile(r"\[[^\[\]\n]*(?<![\w.])-?@\w[^\[\]\n]*\]")

CP_NS = "http://schemas.openxmlformats.org/officeDocument/2006/custom-properties"
VT_NS = "http://schemas.openxmlformats.org/officeDocument/2006/docPropsVTypes"
FMTID = "{D5CDD505-2E9C-101B-9397-08002B2CF9AE}"
CUSTOM_PART = "docProps/custom.xml"
CUSTOM_TYPE = "application/vnd.openxmlformats-officedocument.custom-properties+xml"
CUSTOM_REL = "http://schemas.openxmlformats.org/officeDocument/2006/relationships/custom-properties"
PREF_LIMIT = 255  # characters in one Word custom property; Zotero splits its preferences into ZOTERO_PREF_1, _2, ...


class ZoteroUnavailable(Exception):
    pass


# ---------------------------------------------------------------------------
# Finding pandoc citations
# ---------------------------------------------------------------------------

@dataclass
class Group:
    start: int
    end: int
    line: int
    text: str
    keys: list[str] = field(default_factory=list)
    problem: str = ""


def protected_spans(text: str) -> list[tuple[int, int]]:
    """Front matter, fenced code, HTML comments and inline code (raw inlines included): never converted."""
    spans: list[tuple[int, int]] = []
    front = FRONT_MATTER.match(text)
    if front:
        spans.append(front.span())
    offset, fence, start = 0, "", 0
    for line in text.splitlines(keepends=True):
        mark = FENCE.match(line)
        if not fence and mark:
            fence, start = mark.group(1), offset
        elif fence and mark and mark.group(1)[0] == fence[0] and len(mark.group(1)) >= len(fence) \
                and not line.strip().strip(fence[0]):
            spans.append((start, offset + len(line)))
            fence = ""
        offset += len(line)
    if fence:
        spans.append((start, len(text)))
    spans.extend(m.span() for m in COMMENT.finditer(text))
    blocks = list(spans)
    spans.extend(m.span() for m in INLINE_CODE.finditer(text) if not _inside(m.start(), blocks))
    return spans


def _inside(position: int, spans: list[tuple[int, int]]) -> bool:
    return any(start <= position < end for start, end in spans)


def _line(text: str, position: int) -> int:
    return text.count("\n", 0, position) + 1


def find_citations(text: str, known: set[str] | None = None) -> tuple[list[Group], list[Group]]:
    """Bracketed citation groups (each with its keys, or a problem), and bare in-text @key citations
    whose key is cited elsewhere or is in the bibliography (`known`)."""
    protected = protected_spans(text)
    groups: list[Group] = []
    for match in GROUP.finditer(text):
        content = match.group(1)
        if _inside(match.start(), protected) or "\n\n" in content or not CITE_KEY.search(content):
            continue
        group = Group(match.start(), match.end(), _line(text, match.start()), match.group(0))
        for part in content.split(";"):
            item = PLAIN_ITEM.fullmatch(part.strip())
            if item:
                group.keys.append(item.group(1))
            elif "-@" in part:
                group.problem = "the author is suppressed (-@key)"
            elif CITE_KEY.search(part):
                group.problem = "a locator, prefix or suffix"
            else:
                group.problem = "text that is not a citation key"
        groups.append(group)
    cited = {key for group in groups for key in group.keys} | (known or set())
    taken = protected + [(g.start, g.end) for g in groups]
    bare = [Group(m.start(), m.end(), _line(text, m.start()), m.group(0), [m.group(1)], "an in-text citation without brackets")
            for m in BARE.finditer(text) if m.group(1) in cited and not _inside(m.start(), taken)]
    return groups, bare


# ---------------------------------------------------------------------------
# Bibliography, Zotero and EndNote
# ---------------------------------------------------------------------------

def read_bibliography(path: Path) -> dict[str, dict]:
    """CSL JSON entries by citation key."""
    if path.suffix.lower() in (".bib", ".bibtex", ".ris", ".yaml", ".yml"):
        raise ValueError(f"{path.name}: give the bibliography as CSL JSON, for example "
                         f"pandoc {path.name} -t csljson -o references.json")
    data = json.loads(path.read_text(encoding="utf-8"))
    if isinstance(data, dict):
        data = data.get("items") or data.get("references") or []
    return {str(entry["id"]): entry for entry in data if isinstance(entry, dict) and entry.get("id")}


class Zotero:
    """Better BibTeX's JSON-RPC on Zotero's local port; read only."""

    def __init__(self, base: str = ZOTERO_URL):
        self.base = base.rstrip("/")
        self.opener = urllib.request.build_opener(urllib.request.ProxyHandler({}))
        self.cache: dict[str, list[dict]] = {}

    def search(self, terms: str) -> list[dict]:
        if terms not in self.cache:
            body = json.dumps({"jsonrpc": "2.0", "method": "item.search", "params": [terms], "id": 1}).encode()
            request = urllib.request.Request(self.base + "/better-bibtex/json-rpc", data=body,
                                             headers={"Content-Type": "application/json"})
            try:
                with self.opener.open(request, timeout=60) as response:
                    data = json.load(response)
            except (urllib.error.URLError, OSError, ValueError) as error:
                raise ZoteroUnavailable(str(error)) from error
            if data.get("error"):
                raise ZoteroUnavailable(str(data["error"].get("message") or data["error"]))
            self.cache[terms] = data.get("result") or []
        return self.cache[terms]

    def version(self) -> str:
        try:
            with self.opener.open(self.base + "/connector/ping", timeout=5) as response:
                return response.headers.get("X-Zotero-Version", "")
        except (urllib.error.URLError, OSError) as error:
            raise ZoteroUnavailable(str(error)) from error


@dataclass
class Match:
    key: str
    how: str  # key, DOI, title, ambiguous, not found
    found: list = field(default_factory=list)
    note: str = ""


def title_queries(title: str) -> list[str]:
    """Phrases to search for: Better BibTeX matches the search text as one phrase, so each query is a run of
    words as they stand in the title. The first is the start of the title, up to a colon, question mark or
    semicolon; the second is the longest run of plain words, which survives a dash or quote written
    differently in the library."""
    words = re.sub(r"<[^>]+>", "", title or "").split()
    start = []
    for word in words[:6]:
        start.append(word.rstrip(":;?!.,"))
        if word[-1:] in ":;?!":
            break
    runs, run = [], []
    for word in words + [""]:
        core = word.rstrip(":;?!.,")
        if core and re.fullmatch(r"[^\W_]+", core):
            run.append(core)
            if core == word:
                continue
        runs.append(run)
        run = []
    plain = max(runs, key=len, default=[])[:6]
    queries = [" ".join(w for w in start if w), " ".join(plain) if len(plain) > 1 else "",
               " ".join(start[:2]) if len(start) > 2 else ""]  # last resort: many items, filtered by DOI and title
    return [q for q in dict.fromkeys(queries) if q]


def _citekey(item: dict) -> str:
    return str(item.get("citekey") or item.get("citation-key") or item.get("citationKey") or "")


def _pick(key: str, entry: dict | None, candidates: list, doi_of: Callable, title_of: Callable) -> Match:
    """Match a bibliography entry to library items: the same DOI, or the same title when one side has no DOI."""
    if entry is None:
        return Match(key, "not found", note="not a citation key in the library, and not in the bibliography file")
    doi = cr.clean_doi(str(entry.get("DOI") or ""))
    title = cr.normalize_title(str(entry.get("title") or ""))
    by_doi = [c for c in candidates if doi and doi_of(c) == doi]
    by_title = [c for c in candidates if title and cr.normalize_title(title_of(c)) == title and not (doi and doi_of(c))]
    for how, found in (("DOI", by_doi), ("title", by_title)):
        if len(found) == 1:
            return Match(key, how, found)
        if found:
            return Match(key, "ambiguous", found, f"{len(found)} library items have this {how}; merge the duplicates")
    if not title:
        return Match(key, "not found", note="the bibliography entry has no title to search for")
    return Match(key, "not found", note="no library item has this DOI or title")


def match_zotero(key: str, entry: dict | None, search: Callable[[str], list[dict]]) -> Match:
    by_key = [item for item in search(key) if _citekey(item) == key]
    if len(by_key) == 1:
        return Match(key, "key", by_key)
    def pick(candidates):
        return _pick(key, entry, list(candidates.values()), lambda c: cr.clean_doi(str(c.get("DOI") or "")),
                     lambda c: str(c.get("title") or ""))

    candidates: dict[str, dict] = {}
    for query in title_queries(str(entry.get("title") or "")) if entry else []:
        for item in search(query):
            candidates.setdefault(str(item.get("id")), item)
        match = pick(candidates)
        if match.how != "not found":
            return match
    return pick(candidates)


@dataclass
class Record:
    number: str
    author: str
    year: str
    title: str
    doi: str
    database: str = ""


def _text(element: ET.Element | None) -> str:
    return re.sub(r"\s+", " ", "".join(element.itertext())).strip() if element is not None else ""


def read_endnote(path: Path) -> list[Record]:
    """Records of an EndNote XML export (File > Export, XML), text inside <style> elements included."""
    records = []
    for record in ET.parse(path).getroot().iter("record"):
        authors = record.findall("contributors/authors/author") or record.findall("contributors/*/author")
        database = record.find("database")
        records.append(Record(_text(record.find("rec-number")), _text(authors[0]) if authors else "",
                              _text(record.find("dates/year")), _text(record.find("titles/title")),
                              cr.clean_doi(_text(record.find("electronic-resource-num"))),
                              database.get("name", "") if database is not None else ""))
    return [r for r in records if r.number]


def match_endnote(key: str, entry: dict | None, records: list[Record]) -> Match:
    return _pick(key, entry, records, lambda r: r.doi, lambda r: r.title)


# ---------------------------------------------------------------------------
# Writing citations
# ---------------------------------------------------------------------------

def _id(rng: random.Random) -> str:
    return "".join(rng.choice(string.ascii_letters) for _ in range(8))


def openxml_field(instruction: str, shown: str) -> str:
    """A Word field as a pandoc raw OpenXML inline."""
    return ('`<w:r><w:fldChar w:fldCharType="begin"/></w:r>'
            f'<w:r><w:instrText xml:space="preserve"> {html.escape(instruction, quote=False)} </w:instrText></w:r>'
            '<w:r><w:fldChar w:fldCharType="separate"/></w:r>'
            f'<w:r><w:t>{html.escape(shown, quote=False)}</w:t></w:r>'
            '<w:r><w:fldChar w:fldCharType="end"/></w:r>`{=openxml}')


ZOTERO_BIBLIOGRAPHY = openxml_field('ADDIN ZOTERO_BIBL {"uncited":[],"omitted":[],"custom":[]} CSL_BIBLIOGRAPHY',
                                    "{Bibliography}")


def zotero_citation(items: list[dict], rng: random.Random) -> str:
    """One citation field for library items as Better BibTeX returns them (CSL JSON, id = item URI)."""
    entries = []
    for item in items:
        uri = str(item["id"])
        data = {k: v for k, v in item.items() if k not in ("citekey", "citation-key", "citationKey", "library", "abstract")}
        data["id"] = uri  # Refresh finds the item by its URI
        entries.append({"id": uri, "uris": [uri], "itemData": data})
    citation = {"citationID": _id(rng),
                "properties": {"formattedCitation": "{Citation}", "plainCitation": "{Citation}", "noteIndex": 0},
                "citationItems": entries, "schema": CSL_SCHEMA}
    # A backtick would end pandoc's raw inline early; ` is the same character in JSON.
    text = json.dumps(citation, ensure_ascii=False).replace("`", "\\u0060")
    return openxml_field("ADDIN ZOTERO_ITEM CSL_CITATION " + text, "{Citation}")


def _markdown_escape(text: str) -> str:
    return re.sub(r"([\\`*_\[\]<>{}#])", r"\\\1", text)


def temporary_citation(records: list[Record]) -> str:
    """EndNote temporary citation, braces escaped for pandoc: \\{Smith, 2020 #12;Lee, 2021 #4\\}."""
    parts = []
    for record in records:
        name = record.author.split(",")[0].strip() if "," in record.author else record.author.strip()
        name = name or " ".join(record.title.split()[:3]) or "Anonymous"
        parts.append(_markdown_escape(f"{name}, {record.year}".rstrip() if record.year else f"{name},") + f" #{record.number}")
    return "\\{" + ";".join(parts) + "\\}"


# ---------------------------------------------------------------------------
# Converting a manuscript
# ---------------------------------------------------------------------------

@dataclass
class Conversion:
    text: str = ""
    groups: int = 0
    keys: int = 0
    matches: dict[str, Match] = field(default_factory=dict)
    problems: list[dict] = field(default_factory=list)
    notes: list[str] = field(default_factory=list)


def convert(text: str, bibliography: dict[str, dict], resolve: Callable[[str, dict | None], Match],
            write_group: Callable[[list], str], bibliography_block: str | None) -> Conversion:
    """Replace every citation group; `bibliography_block` replaces the refs div (None removes it, as for EndNote)."""
    result = Conversion()
    groups, bare = find_citations(text, set(bibliography))
    result.groups = len(groups)
    result.keys = sum(len(g.keys) for g in groups)
    for group in groups + bare:
        if group.problem:
            result.problems.append({"line": group.line, "citation": group.text, "problem": group.problem})
    for key in dict.fromkeys(k for g in groups if not g.problem for k in g.keys):
        match = resolve(key, bibliography.get(key))
        result.matches[key] = match
        if match.how in ("ambiguous", "not found"):
            line = next(g.line for g in groups if key in g.keys)
            found = "; ".join(_describe(f) for f in match.found)
            result.problems.append({"line": line, "citation": "@" + key,
                                    "problem": f"{match.how}: {match.note}" + (f" ({found})" if found else "")})
    front = FRONT_MATTER.match(text)
    if front and re.search(r"(?m)^nocite:", front.group(0)):
        result.notes.append("nocite entries are not converted; cite them in the text or add them in Word")
    if result.problems:
        return result
    pieces, last = [], 0
    for group in sorted(groups, key=lambda g: g.start):
        pieces += [text[last:group.start], write_group([result.matches[k].found[0] for k in group.keys])]
        last = group.end
    converted = "".join(pieces) + text[last:]
    refs = REFS_DIV.search(converted)
    if refs and refs.group(2).strip():
        result.notes.append("the refs div held text, which was replaced")
    block = "" if bibliography_block is None else bibliography_block + "\n"
    if refs:
        converted = converted[:refs.start()] + block + converted[refs.end():]
    elif bibliography_block is not None:
        converted = converted.rstrip("\n") + "\n\n" + bibliography_block + "\n"
    result.text = converted
    return result


def _describe(found) -> str:
    if isinstance(found, Record):
        return f"record {found.number}"
    return f"{_citekey(found) or '?'} {found.get('id', '')}".strip()


# ---------------------------------------------------------------------------
# Word files: document preferences and the final check
# ---------------------------------------------------------------------------

def zotero_preferences(style: str, version: str, rng: random.Random) -> str:
    style_id = style if style.startswith("http") else STYLE_BASE + style
    return (f'<data data-version="3" zotero-version="{html.escape(version)}"><session id="{_id(rng)}"/>'
            f'<style id="{html.escape(style_id)}" hasBibliography="1" bibliographyStyleHasBeenSet="0"/>'
            '<prefs><pref name="fieldType" value="Field"/></prefs></data>')


def custom_properties(existing: bytes | None, preferences: str) -> bytes:
    """docProps/custom.xml with ZOTERO_PREF_1, _2, ... holding the preferences; other properties kept."""
    ET.register_namespace("", CP_NS)
    ET.register_namespace("vt", VT_NS)
    root = ET.fromstring(existing) if existing else ET.Element(f"{{{CP_NS}}}Properties")
    for prop in list(root):
        if (prop.get("name") or "").startswith("ZOTERO_PREF_"):
            root.remove(prop)
    pid = max((int(p.get("pid")) for p in root if (p.get("pid") or "").isdigit()), default=1) + 1
    chunks = [preferences[i:i + PREF_LIMIT] for i in range(0, len(preferences), PREF_LIMIT)]
    for number, chunk in enumerate(chunks, 1):
        prop = ET.SubElement(root, f"{{{CP_NS}}}property", {"fmtid": FMTID, "pid": str(pid), "name": f"ZOTERO_PREF_{number}"})
        ET.SubElement(prop, f"{{{VT_NS}}}lpwstr").text = chunk
        pid += 1
    return ('<?xml version="1.0" encoding="UTF-8" standalone="yes"?>\n' + ET.tostring(root, encoding="unicode")).encode()


def write_preferences(path: Path, preferences: str) -> None:
    with zipfile.ZipFile(path) as archive:
        entries = [(info, archive.read(info.filename)) for info in archive.infolist()]
    parts = {info.filename: data for info, data in entries}
    replaced = {CUSTOM_PART: custom_properties(parts.get(CUSTOM_PART), preferences)}
    types = parts["[Content_Types].xml"].decode("utf-8")
    if "/" + CUSTOM_PART not in types:
        replaced["[Content_Types].xml"] = types.replace(
            "</Types>", f'<Override PartName="/{CUSTOM_PART}" ContentType="{CUSTOM_TYPE}"/></Types>').encode()
    rels = parts["_rels/.rels"].decode("utf-8")
    if CUSTOM_PART not in rels:
        number = max((int(n) for n in re.findall(r'Id="rId(\d+)"', rels)), default=0) + 1
        replaced["_rels/.rels"] = rels.replace(
            "</Relationships>", f'<Relationship Id="rId{number}" Type="{CUSTOM_REL}" Target="{CUSTOM_PART}"/></Relationships>').encode()
    handle, temporary = tempfile.mkstemp(suffix=".docx", dir=path.parent)
    os.close(handle)
    try:
        with zipfile.ZipFile(temporary, "w", zipfile.ZIP_DEFLATED) as archive:
            for info, data in entries:
                archive.writestr(info, replaced.pop(info.filename, data))
            for name, data in replaced.items():
                archive.writestr(name, data)
        os.replace(temporary, path)
    finally:
        if os.path.exists(temporary):
            os.remove(temporary)


def fields(path: Path) -> list[tuple[str, str]]:
    """(instruction, displayed text) of every field in the accepted text, footnotes and endnotes included."""
    found: list[tuple[str, str]] = []
    stack: list[dict] = []

    def walk(node: ET.Element) -> None:
        if node.tag in cp.DELETED:
            return
        if node.tag == cp.W + "fldChar":
            kind = node.get(cp.W + "fldCharType")
            if kind == "begin":
                stack.append({"instruction": [], "shown": [], "result": False})
            elif kind == "separate" and stack:
                stack[-1]["result"] = True
            elif kind == "end" and stack:
                item = stack.pop()
                found.append(("".join(item["instruction"]).strip(), "".join(item["shown"]).strip()))
        elif node.tag == cp.W + "instrText" and stack and not stack[-1]["result"]:
            stack[-1]["instruction"].append(node.text or "")
        elif node.tag == cp.W + "t":
            for item in stack:
                if item["result"]:
                    item["shown"].append(node.text or "")
        elif node.tag == cp.W + "fldSimple":
            found.append(((node.get(cp.W + "instr") or "").strip(), "".join(node.itertext()).strip()))
        for child in node:
            walk(child)

    for part in cp._parts(path):
        walk(part)
    return found


def check(path: Path) -> dict:
    all_fields = fields(path)
    zotero = [shown for instruction, shown in all_fields if instruction.startswith("ADDIN ZOTERO_ITEM")]
    endnote = [shown for instruction, shown in all_fields
               if instruction.startswith("ADDIN EN.CITE") and not instruction.startswith("ADDIN EN.CITE.DATA")]
    zotero_bib = [shown for instruction, shown in all_fields if instruction.startswith("ADDIN ZOTERO_BIBL")]
    endnote_bib = [shown for instruction, shown in all_fields if instruction.startswith("ADDIN EN.REFLIST")]
    text = "\n".join(ts._docx_paragraph_text(p) for part in cp._parts(path) for p in part.iter(cp.W + "p"))
    problems = []
    unrefreshed = sum(1 for shown in zotero if shown == "{Citation}") + sum(1 for shown in zotero_bib if shown == "{Bibliography}")
    if unrefreshed:
        problems.append(f"{unrefreshed} Zotero fields still show their placeholder: run Refresh in Word with Zotero open")
    temporary = TEMPORARY.findall(text)
    if temporary:
        problems.append(f"{len(temporary)} EndNote temporary citations are left ({', '.join(temporary[:3])}): update the "
                        "citations in Word with the library open; a citation that stays has no record in that library")
    pandoc = PANDOC_LEFT.findall(text)
    if pandoc:
        problems.append(f"{len(pandoc)} pandoc citations are left as text ({', '.join(pandoc[:3])})")
    if zotero and endnote:
        problems.append("the file has both Zotero and EndNote fields: use one reference manager per document")
    if zotero and not zotero_bib:
        problems.append("Zotero citations but no Zotero bibliography field")
    if endnote and not endnote_bib:
        problems.append("EndNote citations but no EndNote reference list: update the citations in Word")
    if not zotero and not endnote and not problems:
        problems.append("no Zotero or EndNote citation fields")
    return {"file": str(path), "zotero_citations": len(zotero), "zotero_bibliography": len(zotero_bib),
            "endnote_citations": len(endnote), "endnote_reference_list": len(endnote_bib),
            "problems": problems, "ok": not problems}


# ---------------------------------------------------------------------------
# Command line
# ---------------------------------------------------------------------------

def _report(result: Conversion, manager: str, output: Path, as_json: bool) -> int:
    ok = not result.problems
    if as_json:
        json.dump({"ok": ok, "groups": result.groups, "keys": result.keys,
                   "matches": {k: m.how for k, m in result.matches.items()}, "problems": result.problems,
                   "notes": result.notes, "output": str(output) if ok else None}, sys.stdout, ensure_ascii=False, indent=1)
        print()
        return 0 if ok else 1
    counts: dict[str, int] = {}
    for match in result.matches.values():
        counts[match.how] = counts.get(match.how, 0) + 1
    found = ", ".join(f"{n} by {how}" for how, n in counts.items() if how not in ("ambiguous", "not found"))
    print(f"Citations: {result.groups} groups, {result.keys} keys, {len(result.matches)} distinct references.")
    if found:
        print(f"Matched in {manager}: {found}.")
    for note in result.notes:
        print(f"Note: {note}.")
    if not ok:
        print("Stopped; nothing written:")
        for item in sorted(result.problems, key=lambda p: p["line"]):
            print(f"  line {item['line']}: {item['citation']}: {item['problem']}")
        return 1
    print(f"Wrote {output}. Build the Word file from it without --citeproc.")
    if manager == "Zotero":
        print("Then: live_citations.py prefs FILE.docx --style STYLE, open the file in Word and run Zotero Refresh.")
    else:
        print("Then open the file in Word with the same EndNote library open and click Update Citations and Bibliography.")
    return 0


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    commands = parser.add_subparsers(dest="command", required=True)
    zotero = commands.add_parser("zotero", help="Markdown with Zotero citation fields")
    zotero.add_argument("manuscript", type=Path)
    zotero.add_argument("-o", "--output", type=Path, required=True)
    zotero.add_argument("--bibliography", type=Path, help="CSL JSON, for keys that are not Better BibTeX citation keys")
    zotero.add_argument("--zotero", default=ZOTERO_URL, help=f"Zotero's local address (default {ZOTERO_URL})")
    endnote = commands.add_parser("endnote", help="Markdown with EndNote temporary citations")
    endnote.add_argument("manuscript", type=Path)
    endnote.add_argument("-o", "--output", type=Path, required=True)
    endnote.add_argument("--library", type=Path, required=True, help="EndNote XML export of the library Word will use")
    endnote.add_argument("--bibliography", type=Path, required=True, help="CSL JSON with each key's DOI and title")
    prefs = commands.add_parser("prefs", help="write Zotero document preferences into a Word file")
    prefs.add_argument("docx", type=Path)
    prefs.add_argument("--style", required=True, help="Zotero style id, e.g. nature, vancouver, american-medical-association")
    prefs.add_argument("--zotero-version", help="installed Zotero version (default: asked from Zotero)")
    prefs.add_argument("--zotero", default=ZOTERO_URL)
    checking = commands.add_parser("check", help="confirm that every citation in a Word file is a live field")
    checking.add_argument("docx", type=Path)
    for command in (zotero, endnote, prefs, checking):
        command.add_argument("--json", action="store_true", help="print JSON")
    args = parser.parse_args(argv)

    if args.command in ("zotero", "endnote"):
        if not args.manuscript.exists():
            parser.error(f"no such file: {args.manuscript}")
        if args.output.resolve() == args.manuscript.resolve():
            parser.error("write the converted copy to another file; the manuscript itself stays as it is")
        try:
            bibliography = read_bibliography(args.bibliography) if args.bibliography else {}
        except (OSError, ValueError, KeyError) as error:
            parser.error(f"cannot read the bibliography: {error}")
        text = args.manuscript.read_text(encoding="utf-8")
        rng = random.Random()
        if args.command == "zotero":
            library = Zotero(args.zotero)
            try:
                result = convert(text, bibliography, lambda k, e: match_zotero(k, e, library.search),
                                 lambda items: zotero_citation(items, rng), ZOTERO_BIBLIOGRAPHY)
            except ZoteroUnavailable as error:
                print(f"Zotero does not answer at {args.zotero} ({error}). Open Zotero with Better BibTeX installed, "
                      "and let this process reach local ports.", file=sys.stderr)
                return 3
            manager = "Zotero"
        else:
            try:
                records = read_endnote(args.library)
            except (OSError, ET.ParseError) as error:
                parser.error(f"cannot read the EndNote export: {error}")
            result = convert(text, bibliography, lambda k, e: match_endnote(k, e, records), temporary_citation, None)
            databases = sorted({r.database for r in records if r.database})
            if databases:
                result.notes.append(f"record numbers belong to {', '.join(databases)}; open that library before updating")
            manager = "EndNote"
        if not result.problems:
            args.output.write_text(result.text, encoding="utf-8")
        return _report(result, manager, args.output, args.json)

    if not args.docx.exists() or not zipfile.is_zipfile(args.docx):
        parser.error(f"not a Word file: {args.docx}")
    if args.command == "prefs":
        version = args.zotero_version
        if not version:
            try:
                version = Zotero(args.zotero).version()
            except ZoteroUnavailable as error:
                print(f"Zotero does not answer at {args.zotero} ({error}); give --zotero-version.", file=sys.stderr)
                return 3
        preferences = zotero_preferences(args.style, version or "7.0", random.Random())
        write_preferences(args.docx, preferences)
        has_fields = any(i.startswith("ADDIN ZOTERO_ITEM") for i, _ in fields(args.docx))
        report = {"file": str(args.docx), "style": args.style, "zotero_version": version, "zotero_fields": has_fields}
        if args.json:
            print(json.dumps(report))
        else:
            print(f"Zotero document preferences written to {args.docx}: style {args.style}.")
            if not has_fields:
                print("The file has no Zotero citation fields.")
        return 0

    report = check(args.docx)
    if args.json:
        json.dump(report, sys.stdout, ensure_ascii=False, indent=1)
        print()
    else:
        print(f"Zotero: {report['zotero_citations']} citation fields, {report['zotero_bibliography']} bibliography fields.")
        print(f"EndNote: {report['endnote_citations']} citation fields, {report['endnote_reference_list']} reference lists.")
        for problem in report["problems"]:
            print(f"  {problem}")
        print("All citations are live fields." if report["ok"] else "Not every citation is a live field.")
    return 0 if report["ok"] else 1


if __name__ == "__main__":
    sys.exit(main())
