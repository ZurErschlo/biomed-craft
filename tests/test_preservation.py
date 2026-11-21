"""Tests for check_preservation.py. Offline; standard library only."""

import json
import subprocess
import sys
import tempfile
import unittest
import zipfile
from pathlib import Path
from xml.sax.saxutils import escape

SCRIPTS = Path(__file__).resolve().parents[1] / "scripts"
sys.path.insert(0, str(SCRIPTS))

import check_preservation as cp  # noqa: E402

NS = 'xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main"'


def write_docx(path: Path, body: str) -> Path:
    with zipfile.ZipFile(path, "w") as archive:
        archive.writestr("word/document.xml", f'<?xml version="1.0" encoding="UTF-8"?><w:document {NS}><w:body>'
                                              f'{body}</w:body></w:document>')
    return path


def run(text: str) -> str:
    return f'<w:r><w:t xml:space="preserve">{escape(text)}</w:t></w:r>'


def field(instruction: str, shown: str) -> str:
    return ('<w:r><w:fldChar w:fldCharType="begin"/></w:r>'
            f'<w:r><w:instrText xml:space="preserve">{escape(instruction)}</w:instrText></w:r>'
            '<w:r><w:fldChar w:fldCharType="separate"/></w:r>' + run(shown) + '<w:r><w:fldChar w:fldCharType="end"/></w:r>')


ENDNOTE = field("ADDIN EN.CITE <EndNote><Cite><Author>Doe</Author><Year>2020</Year><RecNum>12</RecNum></Cite></EndNote>",
                "[1]")
ZOTERO = field('ADDIN ZOTERO_ITEM CSL_CITATION {"citationID":"x1","citationItems":[{"id":4},{"id":9}]}', "[2,3]")


def tracked(author: str, deleted: str, inserted: str) -> str:
    return (f'<w:del w:id="1" w:author="{author}"><w:r><w:delText xml:space="preserve">{deleted}</w:delText></w:r></w:del>'
            f'<w:ins w:id="2" w:author="{author}">{run(inserted)}</w:ins>')


ORIGINAL = ("Mortality was 12·4% (95% CI 10·1–14·9) among 10 344 adults [12]. It is important to note that "
            "costs could potentially rise (figure 2; appendix p 7). See https://doi.org/10.1016/S0140-6736(19)31288-7 "
            "and \\cite{smith2020,lee2021}.")


class CompareTest(unittest.TestCase):
    def test_journal_style_changes_are_not_losses(self):
        revised = ("Mortality was 12.4% (95% CI 10.1-14.9) among 10,344 adults [12]. Costs might rise "
                   "(figure 2; appendix p 7). See https://doi.org/10.1016/S0140-6736(19)31288-7 and \\cite{smith2020,lee2021}.")
        report = cp.compare(ORIGINAL, revised)
        self.assertTrue(report["ok"], report)

    def test_lost_and_changed_items_are_reported(self):
        revised = "Mortality was 12.4% among 10,344 adults. Costs might rise (figure 3). See \\cite{smith2020}."
        report = cp.compare(ORIGINAL, revised)
        self.assertFalse(report["ok"])
        self.assertIn("14.9", report["numbers"]["missing"])
        self.assertIn("lee2021", report["citations"]["missing"])
        self.assertIn("[12]", report["citations"]["missing"])
        self.assertIn("fig 2", report["cross_references"]["missing"])
        self.assertIn("fig 3", report["cross_references"]["added"])
        self.assertIn("10.1016/s0140-6736(19)31288-7", report["links"]["missing"])

    def test_leading_decimal_p_values(self):
        self.assertEqual(cp.numbers("P < .001"), cp.numbers("P < 0.001"))

    def test_hedges_and_negations_are_counted(self):
        report = cp.compare("This may not reduce costs.", "This reduces costs.")
        self.assertEqual(report["notes"]["hedges"], [1, 0])
        self.assertEqual(report["notes"]["negations"], [1, 0])


class ClaimTest(unittest.TestCase):
    OBSERVATIONAL = "In this cohort, statin use was associated with lower mortality (HR 0.82)."

    def test_association_becoming_effect_is_reported(self):
        changes = cp.claim_changes(self.OBSERVATIONAL, "In this cohort, statin use reduced mortality (HR 0.82).")
        self.assertEqual([c["terms"] for c in changes], [["reduced"]])
        self.assertFalse(cp.compare(self.OBSERVATIONAL, "In this cohort, statin use reduced mortality (HR 0.82).")["ok"])

    def test_dropping_the_association_before_a_causal_word_is_reported(self):
        changes = cp.claim_changes("Statin use was associated with reduced mortality.", "Statin use reduced mortality.")
        self.assertEqual([c["terms"] for c in changes], [["reduced"]])

    def test_wording_that_keeps_the_association_passes(self):
        self.assertEqual(cp.claim_changes(self.OBSERVATIONAL, "In this cohort, statin use was associated with reduced "
                                                              "mortality (HR 0.82)."), [])
        self.assertEqual(cp.claim_changes("Fixed effects were associated with the outcome.",
                                          "Fixed effects of site were included."), [])

    def test_design_decides(self):
        revised = "In this cohort, statin use reduced mortality (HR 0.82)."
        self.assertEqual(cp.claim_changes(self.OBSERVATIONAL, revised, "trial"), [])
        predicted = ("Higher scores were associated with readmission.", "Higher scores predicted readmission.")
        self.assertEqual(len(cp.claim_changes(*predicted)), 1)
        self.assertEqual(cp.claim_changes(*predicted, "prediction"), [])
        pooled = "We pooled 12 randomized controlled trials. Treatment was associated with lower mortality."
        rewritten = "We pooled 12 randomized controlled trials. Treatment reduced mortality."
        self.assertEqual(cp.claim_changes(pooled, rewritten, "systematic-review"), [])
        self.assertEqual(len(cp.claim_changes(pooled, rewritten, "systematic-review", "JAMA")), 1)


class WordTest(unittest.TestCase):
    def test_citation_fields(self):
        with tempfile.TemporaryDirectory() as folder:
            folder = Path(folder)
            before = write_docx(folder / "a.docx", "<w:p>" + run("Rates rose ") + ENDNOTE + run(" and fell ") + ZOTERO
                                + "</w:p>")
            after = write_docx(folder / "b.docx", "<w:p>" + run("Rates rose ") + ENDNOTE + run(" and fell [2,3]") + "</w:p>")
            self.assertEqual(cp.citation_fields(before), [("EndNote 12", "[1]"), ("Zotero 4,9", "[2,3]")])
            report = cp.compare_fields(before, after)
        self.assertEqual(report["counts"], [2, 1])
        self.assertEqual(report["missing"], ["Zotero 4,9 (shown as '[2,3]')"])

    def test_citation_fields_in_footnotes_are_counted(self):
        with tempfile.TemporaryDirectory() as folder:
            folder = Path(folder)
            before = write_docx(folder / "a.docx", "<w:p>" + run("Rates rose.") + "</w:p>")
            after = write_docx(folder / "b.docx", "<w:p>" + run("Rates rose.") + "</w:p>")
            for path, note in ((before, ENDNOTE), (after, run("[1]"))):
                with zipfile.ZipFile(path, "a") as archive:
                    archive.writestr("word/footnotes.xml", f'<w:footnotes {NS}><w:footnote w:id="1"><w:p>'
                                                           f'{run("See ")}{note}</w:p></w:footnote></w:footnotes>')
            report = cp.compare_fields(before, after)
        self.assertEqual(report["counts"], [1, 0])
        self.assertEqual(report["missing"], ["EndNote 12 (shown as '[1]')"])

    def test_intended_revision_is_compared_without_tracked_changes(self):
        with tempfile.TemporaryDirectory() as folder:
            folder = Path(folder)
            original = write_docx(folder / "original.docx", "<w:p>" + run("Participants were followed for four years.")
                                  + "</w:p>")
            clean = write_docx(folder / "clean.docx", "<w:p>" + run("Participants were followed for five years.") + "</w:p>")
            report = cp.compare_tracked(original, original, clean)
        self.assertEqual(report["changes"], 0)
        self.assertFalse(report["accept_all_gives_revision"])

    def test_tracked_changes_round_trip(self):
        with tempfile.TemporaryDirectory() as folder:
            folder = Path(folder)
            original = write_docx(folder / "original.docx", "<w:p>" + run("Participants were followed for four years.")
                                  + "</w:p>")
            good = write_docx(folder / "good.docx", "<w:p>" + run("Participants were followed for ")
                              + tracked("Editor", "four", "five") + run(" years.") + "</w:p>")
            silent = write_docx(folder / "silent.docx", "<w:p>" + run("People were followed for ")
                                + tracked("Editor", "four", "five") + run(" years.") + "</w:p>")
            clean = write_docx(folder / "clean.docx", "<w:p>" + run("Participants were followed for five years.") + "</w:p>")
            self.assertIsNone(cp.compare_tracked(original, original))
            report = cp.compare_tracked(original, good, clean)
            self.assertTrue(report["reject_all_gives_original"])
            self.assertTrue(report["accept_all_gives_revision"])
            report = cp.compare_tracked(original, silent, clean)
            self.assertFalse(report["reject_all_gives_original"])
            self.assertIn("Participants", report["difference"])
            self.assertFalse(report["accept_all_gives_revision"])

    def test_other_authors_keep_their_changes(self):
        with tempfile.TemporaryDirectory() as folder:
            folder = Path(folder)
            original = write_docx(folder / "original.docx", "<w:p>" + run("We enrolled ") + tracked("Coauthor", "80", "84")
                                  + run(" adults.") + "</w:p>")
            kept = write_docx(folder / "kept.docx", "<w:p>" + tracked("Editor", "We", "The team") + run(" enrolled ")
                              + tracked("Coauthor", "80", "84") + run(" adults.") + "</w:p>")
            merged = write_docx(folder / "merged.docx", "<w:p>" + run("We enrolled 84 adults.") + "</w:p>")
            self.assertEqual(cp.compare_tracked(original, kept)["authors_with_fewer_changes"], [])
            self.assertTrue(cp.compare_tracked(original, kept)["reject_all_gives_original"])
            self.assertIsNone(cp.compare_tracked(original, merged))


class CommandLineTest(unittest.TestCase):
    def test_exit_status(self):
        with tempfile.TemporaryDirectory() as directory:
            before, same, changed = (Path(directory) / n for n in ("a.md", "b.md", "c.md"))
            before.write_text(ORIGINAL, encoding="utf-8")
            same.write_text(ORIGINAL.replace("·", "."), encoding="utf-8")
            changed.write_text(ORIGINAL.replace("12·4", "13·4"), encoding="utf-8")
            run = lambda b: subprocess.run([sys.executable, str(SCRIPTS / "check_preservation.py"), str(before), str(b)],
                                           capture_output=True, text=True, encoding="utf-8", cwd=directory)
            self.assertEqual(run(same).returncode, 0)
            self.assertEqual(run(changed).returncode, 1)

    def test_word_files(self):
        with tempfile.TemporaryDirectory() as folder:
            folder = Path(folder)
            original = write_docx(folder / "original.docx", "<w:p>" + run("Participants were followed for four years ")
                                  + ENDNOTE + run(".") + "</w:p>")
            revised = write_docx(folder / "revised.docx", "<w:p>" + run("People were followed for ")
                                 + tracked("Editor", "four", "five") + run(" years [1].") + "</w:p>")
            result = subprocess.run([sys.executable, str(SCRIPTS / "check_preservation.py"), "--json", str(original),
                                     str(revised)], capture_output=True, text=True, encoding="utf-8")
        report = json.loads(result.stdout)
        self.assertEqual(result.returncode, 1)
        self.assertEqual(report["citation_fields"]["missing"], ["EndNote 12 (shown as '[1]')"])
        self.assertFalse(report["tracked_changes"]["reject_all_gives_original"])


if __name__ == "__main__":
    unittest.main()
