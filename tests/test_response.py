"""Tests for check_response.py. Offline; standard library only; synthetic text."""

import contextlib
import io
import sys
import tempfile
import unittest
import zipfile
from pathlib import Path

SCRIPTS = Path(__file__).resolve().parents[1] / "scripts"
sys.path.insert(0, str(SCRIPTS))

import check_response as cr  # noqa: E402

REVISION = """# Methods

We enrolled adults aged 18 years or older from 12 hospitals between 2019 and 2022 [4].
Missing covariate data were handled by multiple imputation with 20 imputed datasets, and estimates were combined with Rubin's rules.

# Results

The hazard ratio for death was 0·82 (95% CI 0·71–0·94) in the adjusted model.

Table 2: Characteristics of participants by exposure group

| Variable | Exposed | Unexposed |
|---|---|---|
| Age in years is given as the median with the interquartile range | 64 (55–72) | 62 (53–70) |

# Discussion

Our estimate is smaller than that of earlier cohort studies, which did not adjust for frailty.
"""

LETTER = """Reviewer 1

Comment 1. Explain how missing data were handled. Originally you wrote "missing data were simply excluded from all of the analyses".

Response: We have revised the Methods (page 6, lines 101–104), which now read: "Missing covariate data were handled by multiple imputation with 20 imputed datasets, and estimates were combined with Rubin's rules."

Comment 2. Report the adjusted estimate.

Response: We added the adjusted estimate to the Results: "The hazard ratio for death was 0.82 (95% CI 0.71-0.94) in the adjusted model."

Comment 3. Compare with earlier studies.

Revised text (Discussion):

"Our estimate is smaller than that of earlier cohort studies, which did not adjust for age or frailty."

Comment 4. The table should say how age is summarized.

Response: We added a row to Table 2: "Age in years is given as the median with the interquartile range."

Comment 5. Give the period of enrollment.

Response: We revised the Results so that it reads "We enrolled adults aged 18 years or older from 12 hospitals between 2019 and 2022." We also added "Follow-up ended at death, emigration or the end of 2023, whichever came first."
"""


def write(folder: Path, name: str, text: str) -> Path:
    path = folder / name
    path.write_text(text, encoding="utf-8")
    return path


def write_docx(path: Path, body: str) -> None:
    xml = ('<?xml version="1.0" encoding="UTF-8"?><w:document xmlns:w="http://schemas.openxmlformats.org/'
           f'wordprocessingml/2006/main"><w:body>{body}</w:body></w:document>')
    with zipfile.ZipFile(path, "w") as archive:
        archive.writestr("word/document.xml", xml)


def run(text: str, superscript: bool = False) -> str:
    props = '<w:rPr><w:vertAlign w:val="superscript"/></w:rPr>' if superscript else ""
    return f'<w:r>{props}<w:t xml:space="preserve">{text}</w:t></w:r>'


class MarkdownTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        with tempfile.TemporaryDirectory() as folder:
            folder = Path(folder)
            cls.report = cr.check(write(folder, "letter.md", LETTER), [write(folder, "revised.md", REVISION)])
        cls.sentences = [(p, s) for p in cls.report["passages"] for s in p["sentences"]]

    def status(self, start: str) -> tuple[dict, dict]:
        for passage, sentence in self.sentences:
            if sentence["text"].startswith(start):
                return passage, sentence
        self.fail(f"no sentence starting {start!r}")

    def test_found_despite_decimal_dash_and_citation_styles(self):
        self.assertEqual(self.status("The hazard ratio")[1]["status"], "found")
        self.assertEqual(self.status("Missing covariate")[1]["status"], "found")

    def test_edited_sentence_differs_and_shows_the_revision(self):
        _, sentence = self.status("Our estimate")
        self.assertEqual(sentence["status"], "differs")
        self.assertIn("did not adjust for frailty", sentence["closest"])

    def test_missing_sentence(self):
        self.assertEqual(self.status("Follow-up ended")[1]["status"], "missing")

    def test_table_text_is_found_in_the_table(self):
        passage, sentence = self.status("Age in years")
        self.assertEqual(sentence["status"], "found")
        self.assertEqual(passage["named_place"], "table 2")
        self.assertEqual(passage["place_check"], "matches")

    def test_wrong_section_is_reported(self):
        passage, _ = self.status("We enrolled")
        self.assertEqual(passage["named_place"], "results")
        self.assertIn("found in methods, not results", passage["place_check"])

    def test_pages_and_lines_are_not_checked(self):
        passage, _ = self.status("Missing covariate")
        self.assertIn("not checked", passage["place_check"])

    def test_original_text_is_not_treated_as_new(self):
        self.assertFalse(any(s["text"].startswith("missing data were simply") for _, s in self.sentences))
        self.assertTrue(any("missing data were simply" in item for item in self.report["not_marked_as_new"]))

    def test_comment_labels(self):
        passage, _ = self.status("Our estimate")
        self.assertEqual(passage["comment"], "Reviewer 1, Comment 3")


class WordTest(unittest.TestCase):
    def test_changes_accepted_and_superscripts_ignored(self):
        revision = (
            '<w:p><w:pPr><w:pStyle w:val="Heading1"/></w:pPr>' + run("Methods") + "</w:p>"
            "<w:p>" + run("Participants were followed for a median of ")
            + '<w:del w:id="1" w:author="A"><w:r><w:delText>four</w:delText></w:r></w:del>'
            + '<w:ins w:id="2" w:author="A">' + run("five") + "</w:ins>"
            + run(" years after the index admission") + run("12,13", superscript=True) + run(".") + "</w:p>"
        )
        letter = ("<w:p>" + run("R1.2 Response: We changed the Methods, which now read: “Participants were followed "
                                "for a median of five years after the index admission.”") + "</w:p>"
                  "<w:p>" + run("We also revised it to say “Participants were followed for a median of four years "
                                "after the index admission.”") + "</w:p>")
        with tempfile.TemporaryDirectory() as folder:
            folder = Path(folder)
            write_docx(folder / "revised.docx", revision)
            write_docx(folder / "letter.docx", letter)
            report = cr.check(folder / "letter.docx", [folder / "revised.docx"])
        statuses = [s["status"] for p in report["passages"] for s in p["sentences"]]
        self.assertEqual(statuses, ["found", "differs"])

    def test_moved_text_is_read_at_its_new_place_only(self):
        revision = (
            '<w:p><w:pPr><w:pStyle w:val="Heading1"/></w:pPr>' + run("Methods") + "</w:p>"
            '<w:p><w:moveFrom w:id="1" w:author="A">' + run("Results were similar in women and in men overall.")
            + "</w:moveFrom></w:p>"
            '<w:p><w:pPr><w:pStyle w:val="Heading1"/></w:pPr>' + run("Discussion") + "</w:p>"
            '<w:p><w:moveTo w:id="2" w:author="A">' + run("Results were similar in women and in men overall.")
            + "</w:moveTo></w:p>")
        letter = "<w:p>" + run("Response: The Methods now read: “Results were similar in women and in men overall.”") + "</w:p>"
        with tempfile.TemporaryDirectory() as folder:
            folder = Path(folder)
            write_docx(folder / "revised.docx", revision)
            write_docx(folder / "letter.docx", letter)
            report = cr.check(folder / "letter.docx", [folder / "revised.docx"])
        self.assertIn("found in discussion, not methods", report["passages"][0]["place_check"])

    def test_word_superscript_powers_are_kept(self):
        revision = ("<w:p>" + run("The assay detected 10") + run("6", superscript=True)
                    + run(" viable cells in each blood sample.") + "</w:p>")
        statuses = []
        for power in ("10⁶", "10³"):
            letter = "<w:p>" + run(f"Response: The text now reads: “The assay detected {power} viable cells in each blood sample.”") + "</w:p>"
            with tempfile.TemporaryDirectory() as folder:
                folder = Path(folder)
                write_docx(folder / "revised.docx", revision)
                write_docx(folder / "letter.docx", letter)
                report = cr.check(folder / "letter.docx", [folder / "revised.docx"])
            statuses.append(report["passages"][0]["sentences"][0]["status"])
        self.assertEqual(statuses[0], "found")
        self.assertNotEqual(statuses[1], "found")


class NormalizeTest(unittest.TestCase):
    def found(self, quoted: str, revised: str) -> str:
        revision = cr.Revision([cr.Unit(revised, "line 1", "results", "", cr.normalize(revised))])
        return revision.find(quoted)[0].status

    def test_comparison_signs_are_kept(self):
        self.assertNotEqual(cr.normalize("only patients with a baseline P < 0.05"),
                            cr.normalize("only patients with a baseline P > 0.05"))
        self.assertEqual(cr.normalize("P<0.05"), cr.normalize("P < 0.05"))

    def test_a_number_is_not_found_inside_a_longer_one(self):
        self.assertNotEqual(self.found("The adjusted hazard ratio for death was 0.8.",
                                       "The adjusted hazard ratio for death was 0.82."), "found")

    def test_powers_are_kept_and_citations_dropped(self):
        self.assertNotEqual(cr.normalize("The assay detected 10⁶ cells"), cr.normalize("The assay detected 10³ cells"))
        self.assertEqual(cr.normalize("The assay detected 10⁶ cells"), cr.normalize("The assay detected 10<sup>6</sup> cells"))
        self.assertEqual(cr.normalize("Rates rose in 2019¹²."), cr.normalize("Rates rose in 2019 [12]."))


class CommandLineTest(unittest.TestCase):
    def test_exit_codes(self):
        with tempfile.TemporaryDirectory() as folder:
            folder = Path(folder)
            revised = write(folder, "revised.md", REVISION)
            good = write(folder, "good.md", "Response: The Discussion now reads: “Our estimate is smaller than that "
                                            "of earlier cohort studies, which did not adjust for frailty.”\n")
            bad = write(folder, "bad.md", LETTER)
            with contextlib.redirect_stdout(io.StringIO()):
                self.assertEqual(cr.main([str(good), str(revised)]), 0)
                self.assertEqual(cr.main([str(bad), str(revised)]), 1)
            with contextlib.redirect_stderr(io.StringIO()), self.assertRaises(SystemExit) as raised:
                cr.main([str(good), str(folder / "absent.md")])
            self.assertEqual(raised.exception.code, 2)


if __name__ == "__main__":
    unittest.main()
