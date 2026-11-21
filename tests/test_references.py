"""Tests for check_references.py. Offline: the lookups answer from synthetic records below.
Every DOI uses the 10.5555 test prefix; no record describes a real article."""

import contextlib
import io
import sys
import tempfile
import unittest
import urllib.error
import urllib.parse
import zipfile
from pathlib import Path

SCRIPTS = Path(__file__).resolve().parents[1] / "scripts"
sys.path.insert(0, str(SCRIPTS))

import check_references as cr  # noqa: E402


def crossref_item(doi, title, family, year, journal, volume="12", page="101-109", **extra):
    item = {"DOI": doi, "title": [title], "author": [{"family": family, "given": "A", "sequence": "first"}],
            "issued": {"date-parts": [[year]]}, "published-print": {"date-parts": [[year, 3]]},
            "container-title": [journal], "volume": volume, "page": page, "type": "journal-article"}
    item.update(extra)
    return item


def pubmed_summary(pmid, doi, title, author, year, source, pubtype=("Journal Article",)):
    return {"uid": pmid, "title": title, "authors": [{"name": author, "authtype": "Author"}],
            "pubdate": f"{year} Mar", "source": source, "fulljournalname": source, "volume": "12",
            "pages": "101-9", "articleids": [{"idtype": "doi", "value": doi}], "pubtype": list(pubtype)}


CROSSREF = {
    "10.5555/trial.1": crossref_item("10.5555/trial.1", "Statins after stroke: a randomized trial", "Okafor", 2021,
                                     "Journal of Test Medicine"),
    "10.5555/cohort.2": crossref_item("10.5555/cohort.2", "Air pollution and asthma in a national cohort", "Lindqvist",
                                      2019, "Journal of Test Medicine"),
    "10.5555/retracted.3": crossref_item(
        "10.5555/retracted.3", "RETRACTED: Vitamin X prevents all colds", "Moreau", 2015, "Journal of Test Medicine",
        **{"updated-by": [{"DOI": "10.5555/notice.3", "type": "retraction", "label": "Retraction",
                           "source": "retraction-watch"}]}),
}
PUBMED = {
    "90000001": pubmed_summary("90000001", "10.5555/trial.1", "Statins after stroke: a randomized trial.", "Okafor A",
                               2021, "J Test Med"),
    "90000003": pubmed_summary("90000003", "10.5555/retracted.3", "Vitamin X prevents all colds.", "Moreau A", 2015,
                               "J Test Med", ("Journal Article", "Retracted Publication")),
}
DATACITE = {"10.5555/data.4": {"titles": [{"title": "Survey data on sleep in adolescents"}],
                               "creators": [{"familyName": "Haddad", "name": "Haddad, R"}],
                               "publicationYear": 2022, "publisher": {"name": "Test Data Repository"}}}
SEARCH = [crossref_item("10.5555/twin.5", "Exercise and mood in older adults", "Novak", 2020, "Test Reports"),
          crossref_item("10.5555/twin.6", "Exercise and mood in older adults", "Novak", 2020, "Test Reports")]


class FakeLookup(cr.Lookup):
    """Answers from the records above; services listed in `down` fail."""

    def __init__(self, down=(), **kwargs):
        super().__init__(**kwargs)
        self.down = set(down)
        self.urls = []

    def fetch_json(self, url):
        self.urls.append(url)
        query = urllib.parse.parse_qs(urllib.parse.urlparse(url).query)
        service = "PubMed" if "eutils" in url else "DataCite" if "datacite" in url else "Crossref"
        if service in self.down:
            raise urllib.error.URLError("connection refused")
        if "esearch" in url:
            term = query["term"][0]
            return {"esearchresult": {"idlist": [p for p, s in PUBMED.items()
                                                 if f'"{s["articleids"][0]["value"]}"[aid]' in term]}}
        if "esummary" in url:
            ids = [i for i in query["id"][0].split(",") if i in PUBMED]
            return {"result": {"uids": ids, **{i: PUBMED[i] for i in ids}}}
        if service == "DataCite":
            doi = urllib.parse.unquote(url.split("/dois/")[1])
            if doi not in DATACITE:
                raise urllib.error.HTTPError(url, 404, "Not Found", None, io.BytesIO())
            return {"data": {"attributes": DATACITE[doi]}}
        if "query.bibliographic" in query:
            return {"message": {"items": SEARCH}}
        wanted = [part[4:] for part in query["filter"][0].split(",") if part.startswith("doi:")]
        return {"message": {"items": [CROSSREF[d] for d in wanted if d in CROSSREF]}}


RIS = """TY  - JOUR
TI  - Statins after stroke: a randomized trial
AU  - Okafor, A
PY  - 2021
JO  - J Test Med
VL  - 12
SP  - 101-109
DO  - https://doi.org/10.5555/TRIAL.1
ER  -
TY  - JOUR
TI  - Air pollution and asthma in a national cohort
AU  - Lindqvist, B
PY  - 2018
JF  - Journal of Test Medicine
VL  - 12
SP  - 101
DO  - 10.5555/cohort.2
ER  -
TY  - JOUR
TI  - Vitamin X prevents all colds
AU  - Moreau, A
PY  - 2015
JO  - J Test Med
DO  - 10.5555/retracted.3
ER  -
TY  - DATA
TI  - Survey data on sleep in adolescents
AU  - Haddad, R
PY  - 2022
T2  - Test Data Repository
DO  - 10.5555/data.4
ER  -
TY  - JOUR
TI  - Exercise and mood in older adults
AU  - Novak, C
PY  - 2020
ER  -
TY  - JOUR
TI  - A trial that was never published
AU  - Petrov, D
PY  - 2023
DO  - 10.5555/missing.7
ER  -
"""

BIBTEX = r"""@article{okafor2021,
  title = {Statins after stroke: {a} randomized trial},
  author = {Okafor, A. and Sato, K.},
  year = 2021,
  journal = {Journal of Test Medicine},
  volume = {12}, pages = {101--109},
  doi = {10.5555/trial.1}
}
@misc{haddad2022, title = "Survey data on sleep in adolescents", author = "Haddad, R", year = {2022},
  doi = {10.5555/data.4}}
"""


def setUpModule():
    global SAVED
    SAVED = (cr.NCBI_PAUSE, cr.CROSSREF_PAUSE, cr.RETRY_PAUSES)
    cr.NCBI_PAUSE = cr.CROSSREF_PAUSE = 0
    cr.RETRY_PAUSES = ()


def tearDownModule():
    cr.NCBI_PAUSE, cr.CROSSREF_PAUSE, cr.RETRY_PAUSES = SAVED


def write(folder: Path, name: str, text: str) -> Path:
    path = folder / name
    path.write_text(text, encoding="utf-8")
    return path


class ReadTest(unittest.TestCase):
    def test_ris_fields(self):
        entries = cr.read_ris(RIS)
        self.assertEqual(len(entries), 6)
        first = entries[0]
        self.assertEqual((first.doi, first.year, first.first_page, first.volume), ("10.5555/trial.1", "2021", "101", "12"))
        self.assertEqual(first.journals, ["J Test Med"])
        self.assertEqual(entries[4].doi, "")

    def test_bibtex_fields(self):
        entries = cr.read_bibtex(BIBTEX)
        self.assertEqual([e.doi for e in entries], ["10.5555/trial.1", "10.5555/data.4"])
        self.assertEqual(entries[0].title, "Statins after stroke: a randomized trial")
        self.assertEqual(entries[0].authors[0], "Okafor, A.")
        self.assertEqual(entries[0].first_page, "101")

    def test_identifier_list(self):
        entries = cr.read_identifiers("doi:10.5555/trial.1\nhttps://doi.org/10.5555/cohort.2\nPMID: 90000003\n")
        self.assertEqual([(e.doi, e.pmid) for e in entries],
                         [("10.5555/trial.1", ""), ("10.5555/cohort.2", ""), ("", "90000003")])


class CompareTest(unittest.TestCase):
    def test_names_journals_and_pages(self):
        self.assertTrue(cr.same_author("van der Berg, J", "van der Berg"))
        self.assertTrue(cr.same_author("A. J. Okafor", "Okafor"))
        self.assertTrue(cr.same_journal(["J Test Med"], ["Journal of Test Medicine"]))
        self.assertFalse(cr.same_journal(["J Test Res"], ["Journal of Test Medicine"]))
        self.assertTrue(cr.same_page("e0123", ["123"]))
        self.assertTrue(cr.same_author("de la Cruz, M", "Cruz"))
        self.assertFalse(cr.same_author("Lee, A", "Atlee"))
        self.assertTrue(cr.same_author("Bland, J M", "Martin Bland"))  # given name stored in the family field

    def test_missing_record_fields_are_not_agreement(self):
        entry = cr.Entry(1, title="T", authors=["Smith, A"], year="2020", journals=["J X"])
        differences = cr.compare(entry, [cr.Record("Crossref", titles=["T"])])
        self.assertEqual(differences, ["first author: not in the record", "year: not in the record",
                                       "journal: not in the record"])

    def test_legacy_doi_keeps_its_brackets(self):
        legacy = "10.5555/(SICI)1098-1128(200005)20:3<203::AID-MED4>3.0.CO;2-3"
        self.assertEqual(cr.clean_doi(legacy), legacy.lower())
        self.assertEqual(cr.clean_doi(f"<https://doi.org/{legacy}>."), legacy.lower())
        self.assertEqual(cr.clean_doi("(doi:10.5555/trial.1)"), "10.5555/trial.1")

    def test_lancet_half_year_volume_matches_running_number(self):
        lancet = cr.Entry(1, year="1986", journals=["Lancet"], volume="1")
        self.assertTrue(cr.same_volume(lancet, {"327"}))
        lancet.volume = "ii"
        self.assertTrue(cr.same_volume(lancet, {"328"}))
        self.assertFalse(cr.same_volume(lancet, {"327"}))
        other = cr.Entry(2, year="1986", journals=["Lancet Oncol"], volume="1")
        self.assertFalse(cr.same_volume(other, {"327"}))

    def test_title_markup_and_case_are_ignored(self):
        self.assertEqual(cr.normalize_title("RETRACTED: <i>Vitamin X</i> prevents all colds."),
                         cr.normalize_title("Vitamin X Prevents All Colds"))


class VerdictTest(unittest.TestCase):
    def setUp(self):
        self.results = {r.number: r for r in cr.check_entries(cr.read_ris(RIS), FakeLookup())}

    def test_verified(self):
        self.assertEqual(self.results[1].verdict, "verified", self.results[1])
        self.assertEqual(self.results[1].pmid, "90000001")

    def test_fields_differ_lists_each_field(self):
        result = self.results[2]
        self.assertEqual(result.verdict, "fields differ")
        self.assertTrue(any(d.startswith("year: entry 2018") for d in result.differences), result.differences)

    def test_retracted_in_both_sources(self):
        result = self.results[3]
        self.assertEqual(result.verdict, "retracted")
        self.assertTrue(any("retraction-watch" in n for n in result.notes))
        self.assertTrue(any("Retracted Publication" in n for n in result.notes))

    def test_datacite_record(self):
        result = self.results[4]
        self.assertEqual(result.verdict, "verified", result)
        self.assertTrue(any("DataCite records carry no retraction status" in n for n in result.notes))

    def test_title_search_tie_is_ambiguous(self):
        result = self.results[5]
        self.assertEqual(result.verdict, "ambiguous")
        self.assertTrue(result.by_hand)
        self.assertEqual(sum(n.startswith("candidate:") for n in result.notes), 2)

    def test_unregistered_doi_is_not_found(self):
        self.assertEqual(self.results[6].verdict, "not found")

    def test_failed_service_is_not_a_verdict(self):
        results = {r.number: r for r in cr.check_entries(cr.read_ris(RIS), FakeLookup(down={"Crossref", "DataCite"}))}
        self.assertEqual(results[2].verdict, "query failed")  # in neither PubMed nor an answering service
        self.assertEqual(results[1].verdict, "query failed")  # PubMed matched, but Crossref may hold a retraction
        self.assertTrue(any("checked in PubMed only" in n for n in results[1].notes))
        self.assertEqual(results[3].verdict, "retracted")  # a retraction found in one source stands

    def test_failed_batch_keeps_the_answered_batches(self):
        class OneBatchDown(FakeLookup):
            def fetch_json(self, url):
                if "filter=" in url and "trial.1" in urllib.parse.unquote(url):
                    raise urllib.error.URLError("timed out")
                return super().fetch_json(url)
        saved = cr.CROSSREF_BATCH
        cr.CROSSREF_BATCH = 1
        try:
            results = {r.number: r for r in cr.check_entries(cr.read_ris(RIS), OneBatchDown(down={"PubMed"}))}
        finally:
            cr.CROSSREF_BATCH = saved
        self.assertEqual(results[3].verdict, "retracted")  # only Crossref marks it here
        self.assertEqual(results[1].verdict, "query failed")

    def test_doi_found_by_title_is_checked_in_pubmed(self):
        unmarked = crossref_item("10.5555/retracted.3", "Vitamin X prevents all colds", "Moreau", 2015,
                                 "Journal of Test Medicine")

        class OneMatch(FakeLookup):
            def crossref_search(self, entry):
                return [cr.crossref_record(unmarked)]
        entry = cr.Entry(1, title="Vitamin X prevents all colds", authors=["Moreau, A"], year="2015",
                         journals=["J Test Med"])
        result = cr.check_entries([entry], OneMatch())[0]
        self.assertEqual(result.verdict, "retracted", result)
        self.assertEqual(result.pmid, "90000003")

    def test_pmid_without_a_record_differs(self):
        entry = cr.Entry(1, title="Statins after stroke: a randomized trial", authors=["Okafor, A"], year="2021",
                         journals=["J Test Med"], doi="10.5555/trial.1", pmid="90000099")
        result = cr.check_entries([entry], FakeLookup())[0]
        self.assertEqual(result.verdict, "fields differ")
        self.assertIn("PMID: PubMed has no record for PMID 90000099", result.differences)

    def test_no_email_is_sent(self):
        lookup = FakeLookup()
        cr.check_entries(cr.read_ris(RIS), lookup)
        self.assertTrue(lookup.urls)
        self.assertFalse(any("email" in url or "mailto" in url or "@" in url for url in lookup.urls))
        self.assertNotIn("@", cr.USER_AGENT)


def write_docx(path: Path, paragraphs: list[list[tuple[str, bool]]]) -> None:
    """Paragraphs of (text, superscript) runs."""
    body = ""
    for runs in paragraphs:
        body += "<w:p>" + "".join(
            "<w:r>" + ('<w:rPr><w:vertAlign w:val="superscript"/></w:rPr>' if sup else "")
            + f'<w:t xml:space="preserve">{text}</w:t></w:r>' for text, sup in runs) + "</w:p>"
    xml = ('<?xml version="1.0" encoding="UTF-8"?><w:document xmlns:w="http://schemas.openxmlformats.org/'
           f'wordprocessingml/2006/main"><w:body>{body}</w:body></w:document>')
    with zipfile.ZipFile(path, "w") as archive:
        archive.writestr("word/document.xml", xml)


class ManuscriptTest(unittest.TestCase):
    def test_markdown_order_and_unused_entries(self):
        with tempfile.TemporaryDirectory() as folder:
            path = write(Path(folder), "ms.md",
                         "# Introduction\n\nRates rose [1,2] and fell [5].\n\nCells grew 10⁶-fold (R² 0.9) in this¹ study.\n\n"
                         "Later work [3–4] agreed.\n\n# References\n\n1. A\n2. B\n3. C\n4. D\n5. E\n6. F\n")
            report = cr.check_manuscript(path, None)
        self.assertEqual(report["entries"], 6)
        self.assertIn("entry 6 is never cited", report["problems"])
        self.assertTrue(any(p.startswith("reference 3 is first cited") for p in report["problems"]), report)
        self.assertFalse(any("reference 6 " in p or "reference 2 is first" in p for p in report["problems"]))

    def test_citations_without_a_reference_list_are_not_matched(self):
        with tempfile.TemporaryDirectory() as folder:
            report = cr.check_manuscript(write(Path(folder), "ms.md", "Rates rose [1].\n"), None)
        self.assertTrue(any("no reference list was found" in p for p in report["problems"]), report)

    def test_word_superscripts_are_citations(self):
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / "ms.docx"
            write_docx(path, [[("Rates rose", False), ("1,2", True), (" and fell", False), ("3", True), (".", False)],
                              [("A volume of 10", False), ("6", True), (" cells.", False)],
                              [("References", False)], [("1. A", False)], [("2. B", False)], [("3. C", False)]])
            report = cr.check_manuscript(path, None)
        self.assertEqual(report["citations"], 3)
        self.assertEqual(report["problems"], [])

    def test_offline_reports_not_done(self):
        with tempfile.TemporaryDirectory() as folder:
            path = write(Path(folder), "refs.ris", RIS)
            with contextlib.redirect_stdout(io.StringIO()) as out:
                code = cr.main([str(path), "--offline"])
        self.assertEqual(code, 3)
        self.assertIn("Not done", out.getvalue())


if __name__ == "__main__":
    unittest.main()
