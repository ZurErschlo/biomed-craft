#!/usr/bin/env python3
"""Check a reference list against Crossref and PubMed, and a manuscript's numbered citations.

Reads RIS (.ris), BibTeX (.bib) or a plain list with one DOI or PMID per line (.txt). Each
reference is looked up by its DOI in Crossref (DataCite for data and code DOIs) and by DOI or
PMID in PubMed. An entry with neither is searched by title in Crossref and also listed for
checking by hand. Each reference gets one verdict:

  verified       title, first author, year and journal match the record
  fields differ  a record was found but a field differs or is missing; each one is listed
  ambiguous      a title search found two or more records that fit equally well
  not found      no record fits
  query failed   a service did not answer, so the check is incomplete; run it again
  retracted      Crossref or PubMed marks the paper as retracted (both are reported)

Corrections and expressions of concern are listed as notes. A plain DOI list can be checked
only for existence and retraction: the report prints each record so it can be compared.

With --manuscript, numbered citations in the manuscript ([1], [2-4], Word superscripts) are
checked too: every number has an entry, every entry is cited, and the numbers follow the
order of first citation without gaps. The entries counted are those of the manuscript's own
reference list when it has one, otherwise those of the reference file.

No email address or API key is sent. With --offline, or when neither service answers, the
lookups are reported as not done.

Examples:
  python3 check_references.py references.ris
  python3 check_references.py library.bib --manuscript manuscript.docx
  python3 check_references.py --manuscript draft.md
  python3 check_references.py --json dois.txt

Exit status: 0 when every reference is verified and the citations are in order, 1 otherwise,
2 for usage errors, 3 when the lookups could not be done.
"""

from __future__ import annotations

import argparse
import datetime
import difflib
import http.client
import json
import os
import re
import ssl
import sys
import time
import unicodedata
import urllib.error
import urllib.parse
import urllib.request
import zipfile
from dataclasses import asdict, dataclass, field
from pathlib import Path
from xml.etree import ElementTree as ET

sys.path.insert(0, str(Path(__file__).resolve().parent))
import textstats as ts  # noqa: E402

USER_AGENT = "biomed-craft-check-references/2.10"
CROSSREF = "https://api.crossref.org/works"
DATACITE = "https://api.datacite.org/dois/"
EUTILS = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/"
# NCBI allows three E-utilities requests per second without an API key.
NCBI_PAUSE = 0.34
# A short pause keeps a long list well inside Crossref's public rate limit.
CROSSREF_PAUSE = 0.1
TIMEOUT = 20
# Dropped connections are common on the public services; three retries with growing pauses
# recover most of them.
RETRY_PAUSES = (1, 3, 8)
# After this many consecutive network failures a service is treated as down for the run,
# so an offline machine does not wait for a timeout on every reference.
DOWN_AFTER = 3
# Below this similarity two titles are different papers; above it the report shows both
# titles as a near match that still needs a look.
TITLE_NEAR = 0.9
# Identifiers per request: PubMed and Crossref answer lists in one request, and these sizes
# keep each URL well under the length that servers accept.
BATCH = 50
CROSSREF_BATCH = 20
CROSSREF_FIELDS = ("DOI,title,subtitle,author,issued,published-print,published-online,container-title,"
                   "short-container-title,volume,page,article-number,updated-by,update-to,type")

DOI = re.compile(r"10\.\d{4,9}/[^\s\"]+", re.IGNORECASE)
RETRACTED_PREFIX = re.compile(r"^\s*(?:retracted|withdrawn)\s*(?:article)?\s*[:.\-–—]\s*", re.IGNORECASE)
RETRACTION_TYPES = {"retraction", "withdrawal", "removal", "partial_retraction"}
NOTICE_TYPES = {"correction", "erratum", "expression_of_concern", "addendum", "corrigendum"}
STOPWORDS = {"of", "the", "and", "in", "for", "on", "de", "la", "le", "der", "und"}
PARTICLES = re.compile(r"(?:van|von|der|den|de|del|della|di|da|das|dos|du|la|le|ten|ter|op|het|al|el|bin|ibn|st)+")

VERDICTS = ("verified", "fields differ", "ambiguous", "not found", "query failed", "retracted")


@dataclass
class Entry:
    number: int
    key: str = ""
    title: str = ""
    authors: list[str] = field(default_factory=list)
    year: str = ""
    journals: list[str] = field(default_factory=list)
    volume: str = ""
    first_page: str = ""
    doi: str = ""
    pmid: str = ""

    def label(self) -> str:
        author = surname(self.authors[0]) if self.authors else ""
        journal = self.journals[0] if self.journals else ""
        text = " ".join(part for part in (author, self.year, journal) if part)
        return text or (f"doi:{self.doi}" if self.doi else "") or (f"PMID {self.pmid}" if self.pmid else self.key) or \
            f"entry {self.number}"

    def has_fields(self) -> bool:
        return bool(self.title or self.authors or self.year or self.journals)


@dataclass
class Record:
    source: str
    titles: list[str] = field(default_factory=list)
    first_author: str = ""
    years: dict[str, str] = field(default_factory=dict)
    journals: list[str] = field(default_factory=list)
    volume: str = ""
    first_pages: list[str] = field(default_factory=list)
    doi: str = ""
    pmid: str = ""
    retracted: bool = False
    notices: list[str] = field(default_factory=list)
    is_notice: bool = False

    def citation(self) -> str:
        year = next(iter(self.years.values()), "")
        title = self.titles[0] if self.titles else ""
        return f"{self.first_author} {year} {self.journals[0] if self.journals else ''}: {title}".strip()


@dataclass
class Result:
    number: int
    label: str
    verdict: str
    differences: list[str] = field(default_factory=list)
    notes: list[str] = field(default_factory=list)
    record: str = ""
    doi: str = ""
    pmid: str = ""
    by_hand: bool = False


# ---------------------------------------------------------------------------
# Reading reference files
# ---------------------------------------------------------------------------

def clean_doi(text: str) -> str:
    """The DOI in a field or a line of text. Legacy SICI DOIs contain brackets
    (10.1002/(SICI)...<203::AID-MED4>3.0.CO;2-3), so a closing mark at the end is dropped only when
    nothing in the DOI opens it."""
    match = DOI.search(urllib.parse.unquote(text or ""))
    if not match:
        return ""
    doi = match.group(0)
    while doi:
        last = doi[-1]
        pair = {")": "(", ">": "<", "]": "[", "}": "{"}.get(last)
        if last in ".,;'" or (pair and doi.count(pair) < doi.count(last)):
            doi = doi[:-1]
        else:
            break
    return doi.lower()


def read_ris(text: str) -> list[Entry]:
    entries, current = [], None
    for line in text.splitlines():
        match = re.match(r"^([A-Z][A-Z0-9])\s{1,2}-\s?(.*)$", line.strip("\ufeff"))
        if not match:
            continue
        tag, value = match[1], match[2].strip()
        if tag == "TY":
            current = Entry(len(entries) + 1)
            continue
        if current is None:
            continue
        if tag == "ER":
            entries.append(current)
            current = None
        elif tag in ("TI", "T1") and not current.title:
            current.title = value
        elif tag in ("AU", "A1"):
            current.authors.append(value)
        elif tag in ("PY", "Y1", "DA") and not current.year:
            year = re.search(r"\b(1[89]\d\d|20\d\d)\b", value)
            current.year = year.group(1) if year else ""
        elif tag in ("JF", "T2", "JO", "JA", "J2") and value and value not in current.journals:
            current.journals.append(value)
        elif tag == "VL":
            current.volume = value
        elif tag == "SP":
            current.first_page = re.split(r"[-–]", value)[0].strip()
        elif tag in ("DO", "UR", "L3") and not current.doi:
            current.doi = clean_doi(value)
        elif tag == "AN" and re.fullmatch(r"\d{1,8}", value):
            current.pmid = value
        elif not current.pmid:
            pmid = re.search(r"\bPMID:?\s*(\d{1,8})\b", value)
            if pmid:
                current.pmid = pmid.group(1)
    return entries


BIB_FIELD = re.compile(r"\s*([A-Za-z][\w-]*)\s*=\s*")
BIB_BARE = re.compile(r"[^,}\s]+")
BIB_COMMA = re.compile(r"\s*,?")
BIB_END = re.compile(r"\s*[})]")


def _bibtex_value(text: str, i: int) -> tuple[str, int]:
    if text[i] == "{":
        depth, start = 0, i
        while i < len(text):
            depth += {"{": 1, "}": -1}.get(text[i], 0)
            i += 1
            if depth == 0:
                return text[start + 1:i - 1], i
        return text[start + 1:], i
    if text[i] == '"':
        end = i + 1
        while end < len(text) and (text[end] != '"' or text[end - 1] == "\\"):
            end += 1
        return text[i + 1:end], end + 1
    match = BIB_BARE.match(text, i)
    return (match.group(0), match.end()) if match else ("", i)


def _latex_plain(text: str) -> str:
    text = re.sub(r"\\[a-zA-Z]+\s*", "", text)
    return re.sub(r"\s+", " ", text.replace("{", "").replace("}", "").replace("\\", "")).strip()


def read_bibtex(text: str) -> list[Entry]:
    entries = []
    for match in re.finditer(r"@(\w+)\s*[{(]\s*([^,\s]*)\s*,", text):
        if match[1].lower() in ("comment", "string", "preamble"):
            continue
        fields, i = {}, match.end()
        while i < len(text):
            name = BIB_FIELD.match(text, i)
            if not name:
                break
            value, i = _bibtex_value(text, name.end())
            fields[name[1].lower()] = value
            i = BIB_COMMA.match(text, i).end()
            if BIB_END.match(text, i):
                break
        entry = Entry(len(entries) + 1, key=match[2])
        entry.title = _latex_plain(fields.get("title", ""))
        entry.authors = [_latex_plain(a) for a in re.split(r"\s+and\s+", fields.get("author", "")) if a.strip()]
        year = re.search(r"(1[89]\d\d|20\d\d)", fields.get("year", "") or fields.get("date", ""))
        entry.year = year.group(1) if year else ""
        entry.journals = [_latex_plain(fields[k]) for k in ("journal", "journaltitle", "shortjournal") if fields.get(k)]
        entry.volume = fields.get("volume", "").strip()
        entry.first_page = re.split(r"[-–]", fields.get("pages", ""))[0].strip()
        entry.doi = clean_doi(fields.get("doi", "") or fields.get("url", ""))
        pmid = fields.get("pmid", "") or (fields.get("eprint", "") if fields.get("eprinttype", "").lower() == "pubmed" else "")
        entry.pmid = pmid.strip() if re.fullmatch(r"\s*\d{1,8}\s*", pmid or "") else ""
        entries.append(entry)
    return entries


def read_identifiers(text: str) -> list[Entry]:
    entries = []
    for line in text.splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        entry = Entry(len(entries) + 1)
        pmid = re.fullmatch(r"(?:PMID:?\s*)?(\d{1,8})", line, re.IGNORECASE)
        if pmid:
            entry.pmid = pmid.group(1)
        else:
            entry.doi = clean_doi(line)
        if entry.doi or entry.pmid:
            entries.append(entry)
    return entries


def read_references(path: Path) -> list[Entry]:
    text = path.read_text(encoding="utf-8-sig", errors="replace")
    suffix = path.suffix.lower()
    if suffix == ".ris":
        return read_ris(text)
    if suffix in (".bib", ".bibtex"):
        return read_bibtex(text)
    if re.search(r"^TY\s{1,2}-", text, re.MULTILINE):
        return read_ris(text)
    if re.search(r"@\w+\s*\{", text):
        return read_bibtex(text)
    return read_identifiers(text)


# ---------------------------------------------------------------------------
# Comparing fields
# ---------------------------------------------------------------------------

def _fold(text: str) -> str:
    text = unicodedata.normalize("NFKD", text)
    return "".join(c for c in text if not unicodedata.combining(c)).casefold()


def normalize_title(text: str) -> str:
    text = re.sub(r"<[^>]+>", "", text or "")
    text = RETRACTED_PREFIX.sub("", unicodedata.normalize("NFKC", text))
    text = _fold(text).replace("&", " and ")
    return re.sub(r"\s+", " ", re.sub(r"[^\w\s]|_", " ", text)).strip()


def surname(name: str) -> str:
    name = re.sub(r"\s+", " ", (name or "").strip())
    if "," in name:
        return name.split(",")[0].strip()
    parts = name.split(" ")
    if len(parts) > 1 and re.fullmatch(r"[A-Z]{1,3}|(?:[A-Z]\.\s?){1,3}", parts[-1]):
        return " ".join(parts[:-1])  # Vancouver form: Smith AJ
    if len(parts) > 1 and all(re.fullmatch(r"[A-Z]\.?(?:-[A-Z]\.?)?", p) for p in parts[:-1]):
        return parts[-1]  # A. J. Smith
    return parts[-1] if len(parts) > 1 and parts[0][:1].isupper() and not parts[-1][:1].isdigit() else name


def _letters(text: str) -> str:
    return re.sub(r"[^a-z0-9]", "", _fold(text))


def _word_tails(name: str) -> set[str]:
    """The name's last word, last two words and so on: Martin Bland gives bland and martinbland."""
    words = [w for w in (_letters(part) for part in re.split(r"[\s\-‐]+", name)) if w]
    return {"".join(words[i:]) for i in range(len(words))}


def same_author(entry_name: str, record_name: str) -> bool:
    entry_surname = surname(entry_name)
    a, b = _letters(entry_surname), _letters(record_name)
    if not a or not b:
        return False
    if a == b or a in _word_tails(record_name) or b in _word_tails(entry_surname):
        return True  # whole trailing words: van der Berg and Berg; Martin Bland and Bland
    short, long = sorted((a, b), key=len)
    if len(short) >= 3 and long.endswith(short) and PARTICLES.fullmatch(long[:-len(short)]):
        return True  # particles written as one word: Vanderberg and Berg
    whole = _letters(entry_name)
    return len(b) >= 6 and (b in whole or whole in b)  # group authors


def _journal_words(name: str) -> list[str]:
    name = re.sub(r"\([^)]*\)", " ", name)
    name = _fold(unicodedata.normalize("NFKC", name)).replace("&", " and ")
    return [w for w in re.split(r"[^\w]+", name) if w and w not in STOPWORDS]


def same_journal(entry_names: list[str], record_names: list[str]) -> bool:
    for a in entry_names:
        for b in record_names:
            wa, wb = _journal_words(a), _journal_words(b)
            if not wa or not wb:
                continue
            if wa == wb:
                return True
            # An abbreviation matches when each of its words starts the word in the same place.
            if len(wa) == len(wb) and all(x.startswith(y) or y.startswith(x) for x, y in zip(wa, wb)):
                return True
    return False


def same_volume(entry: Entry, record_volumes: set[str]) -> bool:
    """The Lancet has published two volumes a year since 1823. Older citations give the half
    year (1986; 1: 307), while Crossref and PubMed give the running number (327), so volume 1
    or 2 of year Y matches (Y - 1823) * 2 + 1 or + 2. Only an exact running number counts."""
    mine = entry.volume.strip()
    if mine in record_volumes:
        return True
    half = {"1": 1, "i": 1, "2": 2, "ii": 2}.get(mine.lower())
    if not half or not entry.year.isdigit() or not any(_journal_words(j) == ["lancet"] for j in entry.journals):
        return False
    return str((int(entry.year) - 1823) * 2 + half) in record_volumes


def _page(text: str) -> str:
    """e073725 and e73725 are the same article number."""
    return re.sub(r"^([a-z]?)0+(\d)", r"\1\2", (text or "").strip().lower())


def same_page(entry_page: str, record_pages: list[str]) -> bool:
    a = _page(entry_page)
    return any(a == _page(p) or a.lstrip("e") == _page(p).lstrip("e") for p in record_pages if p)


def compare(entry: Entry, records: list[Record]) -> list[str]:
    """Each field that differs or is missing from the entry, judged against all records for it."""
    differences = []
    titles = [t for r in records for t in r.titles]
    if not entry.title:
        differences.append("title: not in the entry")
    else:
        mine = normalize_title(entry.title)
        theirs = [normalize_title(t) for t in titles]
        if mine not in theirs:
            best = max(theirs, key=lambda t: difflib.SequenceMatcher(None, mine, t).ratio(), default="")
            ratio = difflib.SequenceMatcher(None, mine, best).ratio() if best else 0
            shown = titles[theirs.index(best)] if best else ""
            kind = "differs slightly" if ratio >= TITLE_NEAR else "differs"
            differences.append(f"title {kind}: entry {entry.title!r}; record {shown!r}")
    authors = [r.first_author for r in records if r.first_author]
    if not entry.authors:
        differences.append("first author: not in the entry")
    elif not authors:
        differences.append("first author: not in the record")
    elif not any(same_author(entry.authors[0], a) for a in authors):
        differences.append(f"first author: entry {surname(entry.authors[0])}; record {authors[0]}")
    years = {f"{y} ({k})" for r in records for k, y in r.years.items()}
    if not entry.year:
        differences.append("year: not in the entry")
    elif not years:
        differences.append("year: not in the record")
    elif entry.year not in {y.split()[0] for y in years}:
        differences.append(f"year: entry {entry.year}; record {', '.join(sorted(years))}")
    journals = [j for r in records for j in r.journals]
    if not entry.journals:
        differences.append("journal: not in the entry")
    elif not journals:
        differences.append("journal: not in the record")
    elif not same_journal(entry.journals, journals):
        differences.append(f"journal: entry {entry.journals[0]}; record {journals[0]}")
    volumes = {r.volume for r in records if r.volume}
    if entry.volume and volumes and not same_volume(entry, volumes):
        differences.append(f"volume: entry {entry.volume}; record {', '.join(sorted(volumes))}")
    pages = [p for r in records for p in r.first_pages]
    if entry.first_page and pages and not same_page(entry.first_page, pages):
        differences.append(f"first page: entry {entry.first_page}; record {', '.join(dict.fromkeys(pages))}")
    return differences


# ---------------------------------------------------------------------------
# Looking up records
# ---------------------------------------------------------------------------

class QueryFailed(Exception):
    pass


class NotFound(Exception):
    pass


def ssl_context() -> ssl.SSLContext:
    """Certificates are always verified. Python from the python.org installer on macOS ships
    without a certificate bundle until 'Install Certificates.command' is run; the system
    bundle is used then instead."""
    paths = ssl.get_default_verify_paths()
    if not (os.environ.get("SSL_CERT_FILE") or paths.cafile or (paths.capath and os.listdir(paths.capath))
            or os.path.exists(paths.openssl_cafile)) and os.path.exists("/etc/ssl/cert.pem"):
        return ssl.create_default_context(cafile="/etc/ssl/cert.pem")
    return ssl.create_default_context()


class Lookup:
    """HTTP access to Crossref, DataCite and PubMed. Tests replace fetch_json."""

    def __init__(self, offline: bool = False):
        self.offline = offline
        self.failures: dict[str, int] = {}
        self.answered: set[str] = set()
        self.last_call: dict[str, float] = {}
        self.errors: dict[str, str] = {}
        self.context = None

    def fetch_json(self, url: str) -> dict:
        if self.context is None:
            self.context = ssl_context()
        request = urllib.request.Request(url, headers={"User-Agent": USER_AGENT, "Accept": "application/json"})
        with urllib.request.urlopen(request, timeout=TIMEOUT, context=self.context) as response:
            return json.loads(response.read().decode("utf-8"))

    def get(self, service: str, url: str, pause: float) -> dict:
        if self.offline or self.failures.get(service, 0) >= DOWN_AFTER:
            raise QueryFailed(service)
        for attempt in range(len(RETRY_PAUSES) + 1):
            wait = pause - (time.monotonic() - self.last_call.get(service, 0))
            if wait > 0:
                time.sleep(wait)
            self.last_call[service] = time.monotonic()
            try:
                data = self.fetch_json(url)
                self.failures[service] = 0
                self.errors.pop(service, None)
                self.answered.add(service)
                return data
            except urllib.error.HTTPError as error:
                error.close()  # the error holds the open response
                if error.code == 404:
                    self.answered.add(service)
                    raise NotFound(url) from error
                if error.code not in (429, 500, 502, 503, 504):
                    self.answered.add(service)
                    raise QueryFailed(f"{service}: HTTP {error.code}") from error
            except (urllib.error.URLError, http.client.HTTPException, TimeoutError, OSError, ValueError) as error:
                reason = getattr(error, "reason", error)
                self.errors[service] = str(reason)
                if isinstance(reason, ssl.SSLCertVerificationError):
                    self.failures[service] = DOWN_AFTER
                    self.errors[service] = ("the HTTPS certificate could not be verified; on macOS run "
                                            "'Install Certificates.command' in the Python folder, or set SSL_CERT_FILE")
                    raise QueryFailed(service) from error
            if attempt < len(RETRY_PAUSES):
                time.sleep(RETRY_PAUSES[attempt])
        self.failures[service] = self.failures.get(service, 0) + 1
        raise QueryFailed(service)

    # Crossref and DataCite -------------------------------------------------

    def crossref_dois(self, dois: list[str]) -> tuple[dict[str, Record], set[str]]:
        """Records for many DOIs, several per request, and the DOIs whose request failed. A DOI
        missing from an answer is not in Crossref."""
        found: dict[str, Record] = {}
        unanswered: set[str] = set()
        plain = [d for d in dict.fromkeys(dois) if "," not in d and "<" not in d]
        for start in range(0, len(plain), CROSSREF_BATCH):
            chunk = plain[start:start + CROSSREF_BATCH]
            filters = ",".join(f"doi:{d}" for d in chunk)
            url = (f"{CROSSREF}?rows={len(chunk)}&select={CROSSREF_FIELDS}"
                   f"&filter={urllib.parse.quote(filters, safe=':/(),')}")
            try:
                items = self.get("Crossref", url, CROSSREF_PAUSE).get("message", {}).get("items", [])
            except QueryFailed:
                unanswered.update(chunk)
                continue
            for item in items:
                record = crossref_record(item)
                found[record.doi] = record
        for doi in (d for d in dict.fromkeys(dois) if d not in plain):
            try:
                url = f"{CROSSREF}/{urllib.parse.quote(doi, safe='/()')}"
                found[doi] = crossref_record(self.get("Crossref", url, CROSSREF_PAUSE).get("message", {}))
            except NotFound:
                pass
            except QueryFailed:
                unanswered.add(doi)
        return found, unanswered

    def crossref_search(self, entry: Entry) -> list[Record]:
        query = " ".join(p for p in (entry.title, surname(entry.authors[0]) if entry.authors else "", entry.year) if p)
        url = f"{CROSSREF}?rows=5&select={CROSSREF_FIELDS}&query.bibliographic={urllib.parse.quote(query)}"
        data = self.get("Crossref", url, CROSSREF_PAUSE)
        return [crossref_record(item) for item in data.get("message", {}).get("items", [])]

    def datacite_doi(self, doi: str) -> Record:
        data = self.get("DataCite", DATACITE + urllib.parse.quote(doi, safe="/()"), CROSSREF_PAUSE)
        return datacite_record(data.get("data", {}).get("attributes", {}), doi)

    # PubMed ------------------------------------------------------------------

    def pubmed_ids_for_dois(self, dois: list[str]) -> dict[str, str]:
        found: dict[str, str] = {}
        for start in range(0, len(dois), BATCH):
            chunk = dois[start:start + BATCH]
            term = " OR ".join(f'"{d}"[aid]' for d in chunk)
            url = f"{EUTILS}esearch.fcgi?db=pubmed&retmode=json&retmax={4 * len(chunk)}&term={urllib.parse.quote(term)}"
            ids = self.get("PubMed", url, NCBI_PAUSE).get("esearchresult", {}).get("idlist", [])
            for record in self.pubmed_summaries(ids).values():
                if record.doi in chunk:
                    found[record.doi] = record.pmid
        return found

    def pubmed_summaries(self, pmids: list[str]) -> dict[str, Record]:
        records: dict[str, Record] = {}
        for start in range(0, len(pmids), BATCH):
            chunk = pmids[start:start + BATCH]
            if not chunk:
                continue
            url = f"{EUTILS}esummary.fcgi?db=pubmed&retmode=json&id={','.join(chunk)}"
            result = self.get("PubMed", url, NCBI_PAUSE).get("result", {})
            for pmid in result.get("uids", []):
                if "error" not in result.get(pmid, {}):
                    records[pmid] = pubmed_record(result[pmid])
        return records


def _year(parts: dict | None) -> str:
    try:
        return str(parts["date-parts"][0][0])
    except (KeyError, IndexError, TypeError):
        return ""


def crossref_record(message: dict) -> Record:
    record = Record("Crossref", doi=(message.get("DOI") or "").lower())
    title = " ".join(message.get("title") or [])
    subtitle = " ".join(message.get("subtitle") or [])
    record.titles = [t for t in (title, f"{title} {subtitle}".strip() if subtitle else "") if t]
    if RETRACTED_PREFIX.match(title):
        record.retracted = True
        record.notices.append("Crossref: the title is marked as retracted or withdrawn")
    authors = message.get("author") or []
    first = next((a for a in authors if a.get("sequence") == "first"), authors[0] if authors else {})
    record.first_author = first.get("family") or first.get("name") or ""
    for label, key in (("print", "published-print"), ("online", "published-online"), ("issued", "issued")):
        year = _year(message.get(key))
        if year and year not in record.years.values():
            record.years[label] = year
    record.journals = [j for j in (message.get("container-title") or []) + (message.get("short-container-title") or []) if j]
    record.volume = (message.get("volume") or "").strip()
    page = (message.get("page") or "").strip()
    record.first_pages = [p for p in (re.split(r"[-–]", page)[0] if page else "", message.get("article-number") or "") if p]
    for update in message.get("updated-by") or []:
        kind = (update.get("type") or "").lower().replace("-", "_")
        notice = f"Crossref: {update.get('label') or kind} {update.get('DOI', '')} (source: {update.get('source', 'publisher')})"
        if kind in RETRACTION_TYPES:
            record.retracted = True
            record.notices.append(notice)
        elif kind:
            record.notices.append(notice)
    if message.get("update-to"):
        record.is_notice = True
    return record


def datacite_record(attributes: dict, doi: str) -> Record:
    record = Record("DataCite", doi=doi.lower())
    record.titles = [t.get("title", "") for t in attributes.get("titles") or [] if t.get("title")]
    creators = attributes.get("creators") or []
    if creators:
        record.first_author = creators[0].get("familyName") or surname(creators[0].get("name", ""))
    if attributes.get("publicationYear"):
        record.years["published"] = str(attributes["publicationYear"])
    publisher = attributes.get("publisher")
    publisher = publisher.get("name", "") if isinstance(publisher, dict) else (publisher or "")
    container = (attributes.get("container") or {}).get("title", "")
    record.journals = [j for j in (container, publisher) if j]
    return record


def pubmed_record(summary: dict) -> Record:
    record = Record("PubMed", pmid=str(summary.get("uid", "")))
    record.titles = [summary.get("title", "")]
    authors = [a for a in summary.get("authors") or [] if a.get("authtype", "Author") == "Author"]
    record.first_author = surname(authors[0]["name"]) if authors else (summary.get("lastauthor") or "")
    for label, key in (("print", "pubdate"), ("online", "epubdate")):
        year = re.search(r"(1[89]\d\d|20\d\d)", summary.get(key) or "")
        if year and year.group(1) not in record.years.values():
            record.years[label] = year.group(1)
    record.journals = [j for j in (summary.get("source"), summary.get("fulljournalname")) if j]
    record.volume = (summary.get("volume") or "").strip()
    pages = (summary.get("pages") or "").strip()
    elocation = re.sub(r"^(?:doi|pii):\s*\S+\s*", "", summary.get("elocationid") or "").strip()
    record.first_pages = [p for p in (re.split(r"[-–]", pages)[0] if pages else "", elocation) if p]
    for article_id in summary.get("articleids") or []:
        if article_id.get("idtype") == "doi":
            record.doi = article_id.get("value", "").lower()
    types = summary.get("pubtype") or []
    if "Retracted Publication" in types:
        record.retracted = True
        record.notices.append("PubMed: publication type Retracted Publication")
    if any(t in types for t in ("Retraction of Publication", "Published Erratum", "Expression of Concern")):
        record.is_notice = True
    return record


# ---------------------------------------------------------------------------
# Verdicts
# ---------------------------------------------------------------------------

def _score(entry: Entry, record: Record) -> int:
    mine = normalize_title(entry.title)
    score = 3 if mine in [normalize_title(t) for t in record.titles] else 0
    if not score and any(difflib.SequenceMatcher(None, mine, normalize_title(t)).ratio() >= TITLE_NEAR for t in record.titles):
        score = 2
    if entry.authors and record.first_author and same_author(entry.authors[0], record.first_author):
        score += 1
    if entry.year and entry.year in record.years.values():
        score += 1
    if entry.journals and same_journal(entry.journals, record.journals):
        score += 1
    return score


def _title_search(entry: Entry, result: Result, lookup: Lookup) -> list[Record] | None:
    """Records found by title for an entry without identifiers; None when the verdict is settled."""
    result.by_hand = True
    result.notes.append("no DOI or PMID in the entry: searched by title in Crossref; check by hand")
    if not entry.title:
        result.verdict = "not found"
        return None
    try:
        candidates = [r for r in lookup.crossref_search(entry) if _score(entry, r) >= 2]
    except (QueryFailed, NotFound):
        result.verdict = "query failed"
        return None
    candidates = [r for r in candidates if not r.is_notice] or candidates
    best = max((_score(entry, r) for r in candidates), default=0)
    top = [r for r in candidates if _score(entry, r) == best]
    if len(top) > 1:
        result.verdict = "ambiguous"
        result.notes += [f"candidate: {r.citation()} (doi:{r.doi})" for r in top]
        return None
    if top:
        result.doi = top[0].doi
        result.notes.append(f"record found by title: doi:{top[0].doi}")
    return top


def judge(entry: Entry, records: list[Record], failed: list[str], pmid: str, lookup: Lookup) -> Result:
    result = Result(entry.number, entry.label(), "", doi=entry.doi, pmid=pmid)
    if not entry.doi and not entry.pmid:
        found = _title_search(entry, result, lookup)
        if found is None:
            return result
        records = found
        if records and records[0].doi:
            failed = list(failed)
            try:
                pmid = lookup.pubmed_ids_for_dois([records[0].doi]).get(records[0].doi, "")
                if pmid:
                    records = records + list(lookup.pubmed_summaries([pmid]).values())
                    result.pmid = pmid
            except QueryFailed:
                failed.append("PubMed")
    if not records:
        result.verdict = "query failed" if failed else "not found"
        if failed:
            result.notes.append(f"no answer from {', '.join(failed)}")
        elif entry.doi:
            result.notes.append("the DOI is not registered with Crossref or DataCite")
        return result
    pubmed = next((r for r in records if r.source == "PubMed"), None)
    if entry.pmid and not pubmed and "PubMed" not in failed:
        result.differences.append(f"PMID: PubMed has no record for PMID {entry.pmid}")
    if entry.doi and entry.pmid and pubmed and pubmed.doi and pubmed.doi != entry.doi:
        result.differences.append(f"identifiers: the PMID's record has doi:{pubmed.doi}, the entry doi:{entry.doi}")
    if entry.has_fields():
        result.differences += compare(entry, records)
    else:
        result.differences.append("the entry gives only an identifier; compare the record with the citation")
    result.record = records[0].citation()
    for record in records:
        result.notes += record.notices
        if record.is_notice:
            result.notes.append(f"{record.source}: the record is a notice (retraction, erratum or concern), not the article")
    marked = {r.source: r.retracted for r in records if r.source != "DataCite"}
    if any(marked.values()):
        result.verdict = "retracted"
        if len(set(marked.values())) > 1:
            result.notes.append("Crossref and PubMed disagree: " + "; ".join(
                f"{k} {'retracted' if v else 'not marked as retracted'}" for k, v in marked.items()))
    elif failed:
        result.verdict = "query failed"  # the unanswered service may hold a retraction
    else:
        result.verdict = "fields differ" if result.differences else "verified"
    if failed:
        result.notes.append(f"no answer from {', '.join(failed)}; checked in {', '.join(r.source for r in records)} only")
    if not marked:
        result.notes.append("DataCite records carry no retraction status")
    return result


def check_entries(entries: list[Entry], lookup: Lookup) -> list[Result]:
    failed: dict[int, list[str]] = {e.number: [] for e in entries}
    # PubMed first, in batches: the PMID of each entry that gives only a DOI, then the summaries.
    pmids = {e.number: e.pmid for e in entries if e.pmid}
    pubmed: dict[str, Record] = {}
    try:
        dois = [e.doi for e in entries if e.doi and not e.pmid]
        by_doi = lookup.pubmed_ids_for_dois(dois) if dois else {}
        for entry in entries:
            if not entry.pmid and entry.doi in by_doi:
                pmids[entry.number] = by_doi[entry.doi]
        pubmed = lookup.pubmed_summaries(list(dict.fromkeys(pmids.values())))
    except QueryFailed:
        for entry in entries:
            if entry.doi or entry.pmid:
                failed[entry.number].append("PubMed")
    # Crossref by DOI, the entry's own or the one PubMed gives; DataCite for DOIs Crossref does not hold.
    wanted: dict[int, str] = {}
    for entry in entries:
        record = pubmed.get(pmids.get(entry.number, ""))
        doi = entry.doi or (record.doi if record else "")
        if doi:
            wanted[entry.number] = doi
    crossref, unanswered = lookup.crossref_dois(list(wanted.values()))
    other: dict[int, Record] = {}
    for number, doi in wanted.items():
        if doi in unanswered:
            failed[number].append("Crossref")
        elif doi in crossref:
            other[number] = crossref[doi]
        else:
            try:
                other[number] = lookup.datacite_doi(doi)
            except NotFound:
                pass
            except QueryFailed:
                failed[number].append("DataCite")
    results = []
    for entry in entries:
        pmid = pmids.get(entry.number, "")
        records = [r for r in (other.get(entry.number), pubmed.get(pmid)) if r]
        results.append(judge(entry, records, failed[entry.number], pmid, lookup))
    return results


# ---------------------------------------------------------------------------
# Numbered citations in a manuscript
# ---------------------------------------------------------------------------

W = "{http://schemas.openxmlformats.org/wordprocessingml/2006/main}"
SUP_OPEN, SUP_CLOSE = "\x01", "\x02"
REFERENCE_HEADING = re.compile(r"^\W*(?:references?|reference list|bibliography|literature cited|works cited)\W*$", re.IGNORECASE)
AFTER_REFERENCES = re.compile(r"^\W*(?:tables?\b|figures?\b|figure legends|supplementary|appendix|acknowledg|"
                              r"extended data)", re.IGNORECASE)
BRACKET_GROUP = re.compile(r"\[(\d{1,3}(?:\s*[,–\-‒—]\s*\d{1,3})*)\]")
SUP_GROUP = re.compile(SUP_OPEN + r"([^" + SUP_CLOSE + r"]*)" + SUP_CLOSE)
HTML_SUP = re.compile(r"<sup>([\d,\s–\-‒—]+)</sup>|\^([\d,\s–\-‒—]+)\^")
SUPERSCRIPT_DIGITS = str.maketrans("⁰¹²³⁴⁵⁶⁷⁸⁹⁻", "0123456789-")
UNICODE_SUP = re.compile(r"[⁰¹²³⁴⁵⁶⁷⁸⁹][⁰¹²³⁴⁵⁶⁷⁸⁹,⁻–\-]*")
ENTRY_NUMBER = re.compile(r"^\s*\[?(\d{1,3})[\].)]?(?:\s|$)")


def manuscript_paragraphs(path: Path) -> list[tuple[str, str]]:
    """(location, text) in reading order, with Word superscripts wrapped in markers."""
    suffix = path.suffix.lower()
    if suffix in (".md", ".markdown", ".qmd", ".rmd", ".txt", ".tex"):
        lines, fenced = [], False
        for number, line in enumerate(path.read_text(encoding="utf-8", errors="replace").splitlines(), start=1):
            if line.strip().startswith(("```", "~~~")):
                fenced = not fenced
            elif not fenced and line.strip():
                lines.append((f"line {number}", line.strip()))
        return lines
    if suffix != ".docx":
        return [(f"line {s.line}", s.text) for s in ts.read_segments(path) if s.scope in ("prose", "caption", "table")]
    with zipfile.ZipFile(path) as archive:
        root = ET.fromstring(archive.read("word/document.xml"))
    paragraphs = []
    for index, paragraph in enumerate(root.iter(W + "p"), start=1):
        parts, superscript = [], False
        for run in paragraph.iter(W + "r"):
            align = run.find(f"{W}rPr/{W}vertAlign")
            is_sup = align is not None and align.get(W + "val") == "superscript"
            text = "".join(t.text or "" for t in run.iter(W + "t"))
            if not text:
                continue
            if is_sup != superscript:
                parts.append(SUP_OPEN if is_sup else SUP_CLOSE)
                superscript = is_sup
            parts.append(text)
        if superscript:
            parts.append(SUP_CLOSE)
        text = "".join(parts).strip()
        if text:
            paragraphs.append((f"paragraph {index}", text))
    return paragraphs


def expand(group: str) -> list[int]:
    numbers = []
    for part in re.split(r"\s*,\s*", group.strip()):
        bounds = [int(n) for n in re.split(r"\s*[–\-‒—]\s*", part) if n.isdigit()]
        if len(bounds) == 2 and bounds[0] < bounds[1] <= bounds[0] + 200:
            numbers += range(bounds[0], bounds[1] + 1)
        elif bounds:
            numbers.append(bounds[0])
    return numbers


def _is_exponent(before: str) -> bool:
    """A superscript after a digit or a short symbol (10⁶, m², χ², I²) is not a citation."""
    if before[-1:].isdigit():
        return True
    token = re.search(r"([^\W\d_]+)$", before)
    return bool(token) and len(token.group(1)) <= 2


def citation_groups(text: str) -> list[list[int]]:
    groups = []
    plain = text.replace(SUP_OPEN, " ").replace(SUP_CLOSE, " ")
    for match in BRACKET_GROUP.finditer(plain):
        groups.append((match.start(), expand(match[1])))
    for match in SUP_GROUP.finditer(text):
        inner = match[1].strip()
        if re.fullmatch(r"[\d,\s–\-‒—]+", inner) and not _is_exponent(text[:match.start()].rstrip(SUP_CLOSE)):
            groups.append((match.start(), expand(inner)))
    for match in HTML_SUP.finditer(plain):
        if not _is_exponent(plain[:match.start()]):
            groups.append((match.start(), expand(match[1] or match[2])))
    for match in UNICODE_SUP.finditer(plain):
        if not _is_exponent(plain[:match.start()]):
            groups.append((match.start(), expand(match.group(0).translate(SUPERSCRIPT_DIGITS))))
    return [numbers for _, numbers in sorted(groups) if numbers]


def check_manuscript(path: Path, entries: list[Entry] | None) -> dict:
    paragraphs = manuscript_paragraphs(path)
    cited: list[tuple[int, str]] = []
    listed: list[int] = []
    in_references = False
    for location, text in paragraphs:
        plain = text.replace(SUP_OPEN, "").replace(SUP_CLOSE, "")
        heading = plain.strip().strip("#").strip()
        if REFERENCE_HEADING.match(heading):
            in_references = True
            continue
        if in_references:
            if AFTER_REFERENCES.match(heading) or ts.is_caption(plain):
                in_references = False
            else:
                number = ENTRY_NUMBER.match(plain)
                listed.append(int(number.group(1)) if number else len(listed) + 1)
                continue
        for group in citation_groups(text):
            cited += [(n, location) for n in group]
    report = {"file": str(path), "citations": len(cited), "problems": []}
    if listed:
        report["entries"], report["entries_from"] = len(listed), "the manuscript's reference list"
        if listed != list(range(1, len(listed) + 1)):
            report["problems"].append("the reference list is not numbered 1 to N without gaps or repeats")
        if entries is not None and len(entries) != len(listed):
            report["problems"].append(f"the reference file has {len(entries)} entries and the manuscript's list {len(listed)}")
    elif entries is not None:
        report["entries"], report["entries_from"] = len(entries), "the reference file"
    else:
        report["entries"], report["entries_from"] = None, "nowhere: no reference list was found"
        report["problems"].append("no reference list was found, so citations could not be matched to entries")
    if not cited:
        report["problems"].append("no numbered citations were found")
        return report
    first: dict[int, str] = {}
    order: list[int] = []
    for number, location in cited:
        if number not in first:
            first[number] = location
            order.append(number)
    total = report["entries"]
    if total is not None:
        for number in sorted(n for n in first if n > total or n < 1):
            report["problems"].append(f"reference {number} is cited ({first[number]}) but has no entry")
        for number in range(1, total + 1):
            if number not in first:
                report["problems"].append(f"entry {number} is never cited")
    else:
        for number in range(1, max(first) + 1):
            if number not in first:
                report["problems"].append(f"reference {number} is never cited, though higher numbers are")
    for previous, number in zip(order, order[1:]):
        if number < previous:
            report["problems"].append(f"reference {number} is first cited ({first[number]}) after reference "
                                      f"{previous} ({first[previous]})")
    return report


# ---------------------------------------------------------------------------
# Report
# ---------------------------------------------------------------------------

def print_report(results: list[Result], manuscript: dict | None, path: Path | None, lookups_done: bool,
                 errors: dict[str, str], out) -> None:
    if path is not None:
        print(f"\n{path}: {len(results)} reference(s), checked {datetime.date.today().isoformat()}", file=out)
        if not lookups_done:
            print("  Not done: neither Crossref nor PubMed answered (or --offline was given). "
                  "No reference has been checked.", file=out)
            for service, error in errors.items():
                print(f"  {service}: {error}", file=out)
        else:
            for r in results:
                print(f"  {r.number:>3}  {r.verdict:<13}  {r.label}", file=out)
                for line in r.differences:
                    print(f"         - {line}", file=out)
                for line in r.notes:
                    print(f"         note: {line}", file=out)
                if r.record and r.verdict != "verified":
                    print(f"         record: {r.record}", file=out)
            counts = {v: sum(r.verdict == v for r in results) for v in VERDICTS}
            print("  " + ", ".join(f"{v} {n}" for v, n in counts.items()), file=out)
        manual = [str(r.number) for r in results if r.by_hand]
        if manual:
            print(f"  Without DOI or PMID, to check by hand: {', '.join(manual)}", file=out)
    if manuscript:
        entries = manuscript["entries"]
        print(f"\n{manuscript['file']}: {manuscript['citations']} numbered citation(s); "
              f"{entries if entries is not None else 'unknown number of'} entries, from {manuscript['entries_from']}",
              file=out)
        for problem in manuscript["problems"]:
            print(f"  - {problem}", file=out)
        if not manuscript["problems"]:
            print("  Citations and entries match, in order of first citation.", file=out)


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("references", nargs="?", type=Path, help="RIS, BibTeX or a list of DOIs or PMIDs")
    parser.add_argument("--manuscript", type=Path, help="manuscript to check for numbered citations (docx, md, tex)")
    parser.add_argument("--offline", action="store_true", help="skip the lookups; check only the citations")
    parser.add_argument("--json", action="store_true", help="print JSON")
    args = parser.parse_args(argv)
    if not args.references and not args.manuscript:
        parser.error("give a reference file, --manuscript, or both")
    for path in (args.references, args.manuscript):
        if path is not None and not path.exists():
            parser.error(f"no such file: {path}")
    entries = read_references(args.references) if args.references else None
    if args.references and not entries:
        parser.error(f"no references could be read from {args.references}")
    results: list[Result] = []
    lookup = Lookup(offline=args.offline)
    if entries:
        results = check_entries(entries, lookup)
    lookups_done = bool(lookup.answered)
    manuscript = check_manuscript(args.manuscript, entries) if args.manuscript else None
    if args.json:
        json.dump({"references": str(args.references) if args.references else None,
                   "lookups_done": lookups_done if entries else None,
                   "errors": lookup.errors,
                   "results": [asdict(r) for r in results] if lookups_done else [],
                   "manuscript": manuscript}, sys.stdout, ensure_ascii=False, indent=1)
        print()
    else:
        print_report(results, manuscript, args.references, lookups_done, lookup.errors, sys.stdout)
    if entries and not lookups_done:
        return 3
    bad = any(r.verdict != "verified" for r in results) or bool(manuscript and manuscript["problems"])
    return 1 if bad else 0


if __name__ == "__main__":
    for stream in (sys.stdout, sys.stderr):
        if hasattr(stream, "reconfigure"):
            stream.reconfigure(encoding="utf-8")
    raise SystemExit(main())
