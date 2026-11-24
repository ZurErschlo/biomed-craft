"""Tests for live_citations.py. Offline: a fake Better BibTeX search answers from synthetic items below.
Every DOI uses the 10.5555 test prefix; no item describes a real article."""

import contextlib
import io
import json
import random
import re
import shutil
import subprocess
import sys
import tempfile
import unittest
import zipfile
from pathlib import Path

SCRIPTS = Path(__file__).resolve().parents[1] / "scripts"
sys.path.insert(0, str(SCRIPTS))

import live_citations as lc  # noqa: E402

LIBRARY = "http://zotero.org/users/123/items/"
ITEMS = [
    {"id": LIBRARY + "AAAA1111", "citekey": "okafor2021", "citation-key": "okafor2021", "library": "My Library",
     "type": "article-journal", "title": "Statins after stroke: a randomized trial", "DOI": "10.5555/trial.1",
     "author": [{"family": "Okafor", "given": "A"}], "issued": {"date-parts": [[2021]]}, "abstract": "Long text."},
    {"id": LIBRARY + "BBBB2222", "citekey": "lindqvistAirPollution2019", "type": "article-journal",
     "title": "Air pollution and asthma in a national cohort", "DOI": "10.5555/cohort.2",
     "author": [{"family": "Lindqvist", "given": "B"}], "issued": {"date-parts": [[2019]]}},
    {"id": LIBRARY + "CCCC3333", "citekey": "moreau2015", "type": "report",
     "title": "Guidance on `backticks` in reports", "author": [{"literal": "Test Health Agency"}]},
    {"id": LIBRARY + "DDDD4444", "citekey": "dup2020a", "type": "article-journal",
     "title": "Duplicated record in the library", "DOI": "10.5555/dup.4"},
    {"id": LIBRARY + "EEEE5555", "citekey": "dup2020b", "type": "article-journal",
     "title": "Duplicated record in the library", "DOI": "10.5555/DUP.4"},
    {"id": LIBRARY + "FFFF6666", "citekey": "chenBurdenDrugresistant2022", "type": "article-journal",
     "title": "Burden of drug-resistant infection in a test region: a modeling study", "DOI": "10.5555/burden.6"},
]
BIBLIOGRAPHY = {
    "okafor2021": {"id": "okafor2021", "title": "Statins after stroke: a randomized trial", "DOI": "10.5555/trial.1"},
    "lindqvist2019": {"id": "lindqvist2019", "title": "Air pollution and asthma in a national cohort",
                      "DOI": "https://doi.org/10.5555/COHORT.2"},
    "agency2015": {"id": "agency2015", "title": "Guidance on backticks in reports"},
    "dup2020": {"id": "dup2020", "title": "Duplicated record in the library", "DOI": "10.5555/dup.4"},
    "missing2018": {"id": "missing2018", "title": "A study that is not in the library", "DOI": "10.5555/none.9"},
}


def fake_search(terms):
    """Better BibTeX's item.search as observed: the text as one phrase, in the citation key or the title,
    ignoring case, never in the DOI."""
    phrase = terms.lower().strip()
    return [item for item in ITEMS if phrase and (phrase in item["citekey"].lower() or phrase in item["title"].lower())]


def resolve(key, entry):
    return lc.match_zotero(key, entry, fake_search)


def convert_zotero(text, bibliography=None):
    rng = random.Random(1)
    return lc.convert(text, BIBLIOGRAPHY if bibliography is None else bibliography, resolve,
                      lambda items: lc.zotero_citation(items, rng), lc.ZOTERO_BIBLIOGRAPHY)


ENDNOTE_XML = """<?xml version="1.0" encoding="UTF-8"?>
<xml><records>
<record><database name="Test.enl" path="/tmp/Test.enl">Test.enl</database><rec-number>12</rec-number>
 <contributors><authors><author><style face="normal">Okafor, A.</style></author><author>Lee, C.</author></authors></contributors>
 <titles><title><style face="normal">Statins after stroke:</style><style face="normal"> a randomized
 trial</style></title></titles><dates><year><style>2021</style></year></dates>
 <electronic-resource-num><style>10.5555/trial.1</style></electronic-resource-num></record>
<record><rec-number>4</rec-number><contributors><authors><author>Test Health Agency,</author></authors></contributors>
 <titles><title>Guidance on backticks in reports</title></titles></record>
<record><rec-number>7</rec-number><titles><title>Air pollution and asthma in a national cohort</title></titles>
 <dates><year>2019</year></dates><electronic-resource-num>10.5555/cohort.2</electronic-resource-num></record>
</records></xml>
"""


def docx(path, body, custom=None, extra_parts=None):
    """A minimal Word file; `body` is the inner XML of w:body."""
    w = 'xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main"'
    types = ('<?xml version="1.0" encoding="UTF-8"?><Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">'
             '<Default Extension="xml" ContentType="application/xml"/>'
             '<Override PartName="/word/document.xml" ContentType="application/vnd.openxmlformats-officedocument.'
             'wordprocessingml.document.main+xml"/></Types>')
    rels = ('<?xml version="1.0" encoding="UTF-8"?><Relationships xmlns="http://schemas.openxmlformats.org/package/2006/'
            'relationships"><Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/'
            'relationships/officeDocument" Target="word/document.xml"/></Relationships>')
    with zipfile.ZipFile(path, "w") as archive:
        archive.writestr("[Content_Types].xml", types)
        archive.writestr("_rels/.rels", rels)
        archive.writestr("word/document.xml", f'<w:document {w}><w:body>{body}</w:body></w:document>')
        if custom is not None:
            archive.writestr("docProps/custom.xml", custom)
        for name, data in (extra_parts or {}).items():
            archive.writestr(name, data)
    return path


def field_xml(instruction, shown):
    return ('<w:r><w:fldChar w:fldCharType="begin"/></w:r>'
            f'<w:r><w:instrText xml:space="preserve"> {instruction} </w:instrText></w:r>'
            '<w:r><w:fldChar w:fldCharType="separate"/></w:r>'
            f'<w:r><w:t>{shown}</w:t></w:r><w:r><w:fldChar w:fldCharType="end"/></w:r>')


def run(argv):
    out, err = io.StringIO(), io.StringIO()
    with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
        try:
            code = lc.main(argv)
        except SystemExit as exit_:
            code = exit_.code
    return code, out.getvalue(), err.getvalue()


class FindCitations(unittest.TestCase):
    def test_groups_and_keys(self):
        groups, bare = lc.find_citations("One [@okafor2021]. Two [@a2020; @b:2021-x].\n")
        self.assertEqual([g.keys for g in groups], [["okafor2021"], ["a2020", "b:2021-x"]])
        self.assertFalse(any(g.problem for g in groups))
        self.assertEqual(bare, [])

    def test_skips_code_comments_and_front_matter(self):
        text = ("---\ntitle: \"See [@yaml2020]\"\n---\n\nText `[@inline2020]` and <!-- [@comment2020] -->.\n\n"
                "```r\n# [@fenced2020]\n```\n\n~~~~\n[@tilde2020]\n~~~~\n\nReal [@real2020].\n")
        groups, _ = lc.find_citations(text)
        self.assertEqual([k for g in groups for k in g.keys], ["real2020"])

    def test_links_emails_and_escapes_are_not_citations(self):
        text = "Write to [a@b.org](mailto:a@b.org), see [@ref](#x), \\[@notacite2020] and [text]{.class}.\n"
        groups, bare = lc.find_citations(text)
        self.assertEqual(groups, [])
        self.assertEqual(bare, [])

    def test_problems_block(self):
        groups, _ = lc.find_citations("A [@a2020, p. 4]. B [see @b2020]. C [-@c2020]. D [@d2020; and more].\n")
        problems = [g.problem for g in groups]
        self.assertEqual(problems[:3], ["a locator, prefix or suffix"] * 2 + ["the author is suppressed (-@key)"])
        self.assertEqual(problems[3], "text that is not a citation key")

    def test_bare_key_only_when_known(self):
        text = "As @okafor2021 showed [@okafor2021]. Mail me@site.org or @someone on social media.\n"
        _, bare = lc.find_citations(text)
        self.assertEqual([(b.keys, b.line) for b in bare], [(["okafor2021"], 1)])
        _, bare = lc.find_citations("As @lindqvist2019 showed.\n", known={"lindqvist2019"})
        self.assertEqual(len(bare), 1)

    def test_line_numbers(self):
        groups, _ = lc.find_citations("Line one.\n\nLine three [@x2020].\n")
        self.assertEqual(groups[0].line, 3)


class Matching(unittest.TestCase):
    def test_by_key(self):
        match = resolve("okafor2021", None)
        self.assertEqual((match.how, match.found[0]["id"]), ("key", LIBRARY + "AAAA1111"))

    def test_by_doi_when_key_differs(self):
        match = resolve("lindqvist2019", BIBLIOGRAPHY["lindqvist2019"])
        self.assertEqual((match.how, match.found[0]["citekey"]), ("DOI", "lindqvistAirPollution2019"))

    def test_by_title_without_doi(self):
        match = resolve("agency2015", BIBLIOGRAPHY["agency2015"])
        self.assertEqual((match.how, match.found[0]["citekey"]), ("title", "moreau2015"))

    def test_title_queries_are_phrases_from_the_title(self):
        self.assertEqual(lc.title_queries("Burden of drug–resistant infection in a test region: a modeling study"),
                         ["Burden of drug–resistant infection in a", "infection in a test region", "Burden of"])
        self.assertEqual(lc.title_queries("Short: title"), ["Short"])
        self.assertEqual(lc.title_queries(""), [])

    def test_by_doi_when_the_dash_differs(self):
        entry = {"title": "Burden of drug–resistant infection in a test region: a modeling study",
                 "DOI": "10.5555/burden.6"}
        match = resolve("chen2022", entry)
        self.assertEqual((match.how, match.found[0]["citekey"]), ("DOI", "chenBurdenDrugresistant2022"))

    def test_same_title_different_doi_is_not_a_match(self):
        entry = {"title": "Statins after stroke: a randomized trial", "DOI": "10.5555/other.8"}
        self.assertEqual(resolve("x", entry).how, "not found")

    def test_duplicates_are_ambiguous(self):
        match = resolve("dup2020", BIBLIOGRAPHY["dup2020"])
        self.assertEqual((match.how, len(match.found)), ("ambiguous", 2))

    def test_unknown_key(self):
        self.assertEqual(resolve("nobody1999", None).how, "not found")
        self.assertEqual(resolve("missing2018", BIBLIOGRAPHY["missing2018"]).how, "not found")


class ZoteroConversion(unittest.TestCase):
    def test_fields_and_bibliography(self):
        text = "Statins [@okafor2021; @lindqvist2019].\n\n# References\n\n::: {#refs}\n:::\n"
        result = convert_zotero(text)
        self.assertEqual(result.problems, [])
        self.assertEqual(result.text.count("ADDIN ZOTERO_ITEM CSL_CITATION"), 1)
        self.assertEqual(result.text.count("ADDIN ZOTERO_BIBL"), 1)
        self.assertNotIn("{#refs}", result.text)
        self.assertIn("# References", result.text)
        instruction = re.search(r"CSL_CITATION (\{.*?\}) </w:instrText>", result.text).group(1)
        citation = json.loads(instruction.replace("&lt;", "<").replace("&gt;", ">").replace("&amp;", "&"))
        items = citation["citationItems"]
        self.assertEqual([i["uris"] for i in items], [[LIBRARY + "AAAA1111"], [LIBRARY + "BBBB2222"]])
        self.assertEqual(items[0]["id"], LIBRARY + "AAAA1111")
        self.assertEqual(items[0]["itemData"]["id"], LIBRARY + "AAAA1111")
        for dropped in ("citekey", "citation-key", "library", "abstract"):
            self.assertNotIn(dropped, items[0]["itemData"])

    def test_bibliography_appended_without_refs_div(self):
        result = convert_zotero("Text [@okafor2021].\n")
        self.assertTrue(result.text.rstrip().endswith("`{=openxml}"))
        self.assertEqual(result.text.count("ZOTERO_BIBL"), 1)

    def test_backticks_escaped_in_json(self):
        result = convert_zotero("Guidance [@moreau2015].\n")
        field = re.search(r"`(<w:r>.*?)`\{=openxml\}", result.text).group(1)
        self.assertNotIn("`", field)
        self.assertIn("\\u0060backticks\\u0060", field)

    def test_all_or_nothing(self):
        text = "A [@okafor2021].\nB [@dup2020].\nC [@nobody1999].\nD [@okafor2021, p. 3].\nE @okafor2021 said.\n"
        result = convert_zotero(text)
        self.assertEqual(result.text, "")
        self.assertEqual(sorted(p["line"] for p in result.problems), [2, 3, 4, 5])
        self.assertTrue(any(p["problem"].startswith("ambiguous") for p in result.problems))

    def test_nocite_note(self):
        result = convert_zotero("---\nnocite: |\n  @lindqvist2019\n---\n\nText [@okafor2021].\n")
        self.assertTrue(any("nocite" in n for n in result.notes))

    def test_command_writes_nothing_when_stopped(self):
        with tempfile.TemporaryDirectory() as folder:
            manuscript, output = Path(folder, "ms.md"), Path(folder, "out.md")
            manuscript.write_text("Text [@nobody1999].\n", encoding="utf-8")
            original = lc.Zotero.search
            lc.Zotero.search = lambda self, terms: fake_search(terms)
            try:
                code, out, _ = run(["zotero", str(manuscript), "-o", str(output)])
            finally:
                lc.Zotero.search = original
            self.assertEqual(code, 1)
            self.assertFalse(output.exists())
            self.assertIn("line 1", out)

    def test_command_refuses_to_overwrite_manuscript(self):
        with tempfile.TemporaryDirectory() as folder:
            manuscript = Path(folder, "ms.md")
            manuscript.write_text("Text [@okafor2021].\n", encoding="utf-8")
            code, _, err = run(["zotero", str(manuscript), "-o", str(manuscript)])
            self.assertEqual(code, 2)
            self.assertIn("another file", err)

    def test_zotero_closed(self):
        with tempfile.TemporaryDirectory() as folder:
            manuscript = Path(folder, "ms.md")
            manuscript.write_text("Text [@okafor2021].\n", encoding="utf-8")
            code, _, err = run(["zotero", str(manuscript), "-o", str(Path(folder, "out.md")),
                                "--zotero", "http://127.0.0.1:9"])
            self.assertEqual(code, 3)
            self.assertIn("does not answer", err)

    def test_bibtex_bibliography_refused(self):
        with tempfile.TemporaryDirectory() as folder:
            with self.assertRaises(ValueError):
                lc.read_bibliography(Path(folder, "refs.bib"))


class EndNote(unittest.TestCase):
    def setUp(self):
        self.folder = tempfile.TemporaryDirectory()
        self.library = Path(self.folder.name, "library.xml")
        self.library.write_text(ENDNOTE_XML, encoding="utf-8")
        self.records = lc.read_endnote(self.library)

    def tearDown(self):
        self.folder.cleanup()

    def test_read_export(self):
        first = self.records[0]
        self.assertEqual((first.number, first.author, first.year, first.doi, first.database),
                         ("12", "Okafor, A.", "2021", "10.5555/trial.1", "Test.enl"))
        self.assertEqual(first.title, "Statins after stroke: a randomized trial")

    def test_temporary_citations(self):
        self.assertEqual(lc.temporary_citation(self.records[:1]), "\\{Okafor, 2021 #12\\}")
        self.assertEqual(lc.temporary_citation(self.records[1:2]), "\\{Test Health Agency, #4\\}")
        self.assertEqual(lc.temporary_citation(self.records[2:3]), "\\{Air pollution and, 2019 #7\\}")
        self.assertEqual(lc.temporary_citation(self.records[:2]), "\\{Okafor, 2021 #12;Test Health Agency, #4\\}")

    def test_convert(self):
        text = "Statins [@okafor2021; @agency2015]. Air [@lindqvist2019].\n\n::: {#refs}\n:::\n"
        result = lc.convert(text, BIBLIOGRAPHY, lambda k, e: lc.match_endnote(k, e, self.records),
                            lc.temporary_citation, None)
        self.assertEqual(result.problems, [])
        self.assertIn("\\{Okafor, 2021 #12;Test Health Agency, #4\\}", result.text)
        self.assertIn("\\{Air pollution and, 2019 #7\\}", result.text)
        self.assertNotIn("refs", result.text)

    def test_command(self):
        manuscript, output = Path(self.folder.name, "ms.md"), Path(self.folder.name, "out.md")
        bibliography = Path(self.folder.name, "refs.json")
        manuscript.write_text("Statins [@okafor2021].\n", encoding="utf-8")
        bibliography.write_text(json.dumps(list(BIBLIOGRAPHY.values())), encoding="utf-8")
        code, out, _ = run(["endnote", str(manuscript), "--library", str(self.library),
                            "--bibliography", str(bibliography), "-o", str(output)])
        self.assertEqual(code, 0, out)
        self.assertIn("#12", output.read_text(encoding="utf-8"))
        self.assertIn("Test.enl", out)


class Preferences(unittest.TestCase):
    def test_new_custom_part(self):
        with tempfile.TemporaryDirectory() as folder:
            path = docx(Path(folder, "a.docx"), "<w:p/>")
            lc.write_preferences(path, lc.zotero_preferences("nature", "7.0.1", random.Random(1)))
            with zipfile.ZipFile(path) as archive:
                custom = archive.read("docProps/custom.xml").decode()
                types = archive.read("[Content_Types].xml").decode()
                rels = archive.read("_rels/.rels").decode()
            self.assertIn('name="ZOTERO_PREF_1"', custom)
            self.assertIn("http://www.zotero.org/styles/nature", custom.replace("&quot;", '"'))
            self.assertIn("/docProps/custom.xml", types)
            self.assertIn('Id="rId2"', rels)
            self.assertIn("custom-properties", rels)

    def test_existing_properties_kept_and_long_value_split(self):
        custom = ('<?xml version="1.0" encoding="UTF-8"?><Properties xmlns="http://schemas.openxmlformats.org/'
                  'officeDocument/2006/custom-properties" xmlns:vt="http://schemas.openxmlformats.org/officeDocument/'
                  '2006/docPropsVTypes"><property fmtid="{D5CDD505-2E9C-101B-9397-08002B2CF9AE}" pid="2" name="Owner">'
                  '<vt:lpwstr>Lab</vt:lpwstr></property><property fmtid="{D5CDD505-2E9C-101B-9397-08002B2CF9AE}" '
                  'pid="3" name="ZOTERO_PREF_1"><vt:lpwstr>old</vt:lpwstr></property></Properties>')
        with tempfile.TemporaryDirectory() as folder:
            path = docx(Path(folder, "b.docx"), "<w:p/>", custom=custom)
            style = "http://www.zotero.org/styles/" + "x" * 300
            preferences = lc.zotero_preferences(style, "7.0.1", random.Random(1))
            lc.write_preferences(path, preferences)
            with zipfile.ZipFile(path) as archive:
                names = archive.namelist()
                written = archive.read("docProps/custom.xml").decode()
            self.assertEqual(names.count("docProps/custom.xml"), 1)
            self.assertIn('name="Owner"', written)
            self.assertNotIn(">old<", written)
            values = re.findall(r'name="ZOTERO_PREF_\d"[^>]*><vt:lpwstr>(.*?)</vt:lpwstr>', written)
            self.assertEqual(len(values), -(-len(preferences) // lc.PREF_LIMIT))
            self.assertGreater(len(values), 1)
            self.assertTrue(all(len(lc.html.unescape(v)) <= lc.PREF_LIMIT for v in values))
            self.assertEqual("".join(lc.html.unescape(v) for v in values), preferences)
            pids = re.findall(r'pid="(\d+)"', written)
            self.assertEqual(len(pids), len(set(pids)))


class Check(unittest.TestCase):
    def check(self, body, **parts):
        with tempfile.TemporaryDirectory() as folder:
            return lc.check(docx(Path(folder, "c.docx"), body, **parts))

    def test_refreshed_zotero(self):
        body = (f'<w:p>{field_xml("ADDIN ZOTERO_ITEM CSL_CITATION {}", "1,2")}</w:p>'
                f'<w:p>{field_xml("ADDIN ZOTERO_BIBL {} CSL_BIBLIOGRAPHY", "1. Okafor A.")}</w:p>')
        report = self.check(body)
        self.assertTrue(report["ok"], report)
        self.assertEqual((report["zotero_citations"], report["zotero_bibliography"]), (1, 1))

    def test_placeholders_left(self):
        body = (f'<w:p>{field_xml("ADDIN ZOTERO_ITEM CSL_CITATION {}", "{Citation}")}</w:p>'
                f'<w:p>{field_xml("ADDIN ZOTERO_BIBL {} CSL_BIBLIOGRAPHY", "{Bibliography}")}</w:p>')
        report = self.check(body)
        self.assertFalse(report["ok"])
        self.assertIn("placeholder", report["problems"][0])

    def test_endnote_with_temporary_citation_in_footnote(self):
        footnotes = ('<w:footnotes xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main"><w:footnote>'
                     '<w:p><w:r><w:t>{Lee, 2020 #9}</w:t></w:r></w:p></w:footnote></w:footnotes>')
        body = (f'<w:p>{field_xml("ADDIN EN.CITE &lt;EndNote&gt;&lt;RecNum&gt;12&lt;/RecNum&gt;&lt;/EndNote&gt;", "1")}'
                f'{field_xml("ADDIN EN.CITE.DATA xyz", "")}</w:p><w:p>{field_xml("ADDIN EN.REFLIST", "1. Okafor A.")}</w:p>')
        report = self.check(body, extra_parts={"word/footnotes.xml": footnotes})
        self.assertEqual(report["endnote_citations"], 1)
        self.assertEqual(report["endnote_reference_list"], 1)
        self.assertFalse(report["ok"])
        self.assertTrue(any("{Lee, 2020 #9}" in p for p in report["problems"]))

    def test_pandoc_citation_left_but_email_ignored(self):
        body = ('<w:p><w:r><w:t>Statins [@okafor2021] reduce risk; write to [a@b.org].</w:t></w:r></w:p>'
                f'<w:p>{field_xml("ADDIN ZOTERO_ITEM CSL_CITATION {}", "1")}</w:p>'
                f'<w:p>{field_xml("ADDIN ZOTERO_BIBL {} CSL_BIBLIOGRAPHY", "1. A.")}</w:p>')
        report = self.check(body)
        self.assertEqual(len(report["problems"]), 1)
        self.assertIn("[@okafor2021]", report["problems"][0])

    def test_no_fields_exit_code(self):
        with tempfile.TemporaryDirectory() as folder:
            path = docx(Path(folder, "d.docx"), "<w:p><w:r><w:t>Plain text.</w:t></w:r></w:p>")
            code, out, _ = run(["check", str(path)])
        self.assertEqual(code, 1)
        self.assertIn("no Zotero or EndNote citation fields", out)

    def test_deleted_field_not_counted(self):
        body = (f'<w:p><w:del w:id="1" w:author="A">{field_xml("ADDIN ZOTERO_ITEM CSL_CITATION {}", "1")}</w:del>'
                f'{field_xml("ADDIN ZOTERO_ITEM CSL_CITATION {}", "2")}</w:p>'
                f'<w:p>{field_xml("ADDIN ZOTERO_BIBL {} CSL_BIBLIOGRAPHY", "1. A.")}</w:p>')
        self.assertEqual(self.check(body)["zotero_citations"], 1)


@unittest.skipUnless(shutil.which("pandoc"), "pandoc is not installed")
class PandocRoundTrip(unittest.TestCase):
    def test_zotero_fields_survive_pandoc(self):
        text = ("---\ntitle: Test\n---\n\nStatins [@okafor2021; @lindqvist2019]. Guidance [@moreau2015].\n\n"
                "# References\n\n::: {#refs}\n:::\n")
        result = convert_zotero(text)
        self.assertEqual(result.problems, [])
        with tempfile.TemporaryDirectory() as folder:
            source, output = Path(folder, "ms.md"), Path(folder, "ms.docx")
            source.write_text(result.text, encoding="utf-8")
            subprocess.run(["pandoc", str(source), "-o", str(output)], check=True, capture_output=True)
            lc.write_preferences(output, lc.zotero_preferences("nature", "7.0.1", random.Random(1)))
            report = lc.check(output)
            self.assertEqual((report["zotero_citations"], report["zotero_bibliography"]), (2, 1))
            self.assertTrue(any("placeholder" in p for p in report["problems"]))
            fields = [i for i, _ in lc.fields(output) if i.startswith("ADDIN ZOTERO_ITEM")]
            citation = json.loads(fields[1].split("CSL_CITATION", 1)[1])
            self.assertIn("`backticks`", citation["citationItems"][0]["itemData"]["title"])

    def test_endnote_braces_survive_pandoc(self):
        records = [lc.Record("12", "Okafor, A.", "2021", "", ""), lc.Record("4", "Lee, C.", "2019", "", "")]
        with tempfile.TemporaryDirectory() as folder:
            source, output = Path(folder, "ms.md"), Path(folder, "ms.docx")
            source.write_text(f"Statins {lc.temporary_citation(records)}.\n", encoding="utf-8")
            subprocess.run(["pandoc", str(source), "-o", str(output)], check=True, capture_output=True)
            report = lc.check(output)
            self.assertTrue(any("{Okafor, 2021 #12;Lee, 2019 #4}" in p for p in report["problems"]), report)


if __name__ == "__main__":
    unittest.main()
