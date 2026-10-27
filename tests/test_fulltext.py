"""Tests for check_fulltext.py, using text in place of PDFs. Offline; standard library only."""

import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import check_fulltext as cf  # noqa: E402

RIS = """TY  - JOUR
ID  - R1
TI  - Trends in tuberculosis notifications in Example Province, 2010-2022
AU  - Smith, Jane
PY  - 2023
DO  - https://doi.org/10.1000/abc.1
ER  - 
TY  - JOUR
ID  - R2
TI  - Cost-effectiveness of screening for hepatitis B infection in adults
AU  - Lee, Kim
PY  - 2021
DO  - 10.1000/abc.2
ER  - 
TY  - JOUR
ID  - R3
TI  - Antibiotic prescribing in primary care after a national awareness campaign
AU  - Garcia, Maria
PY  - 2019
ER  - 
TY  - JOUR
ID  - R4
TI  - Household contact tracing for drug-resistant tuberculosis in urban clinics
AU  - Okafor, Ada
PY  - 2020
ER  - 
"""

R1_TEXT = "Research article\nTrends in tuberculosis notifications in Example Province, 2010-2022\nJane Smith\n2023 doi: 10.1000/abc.1"
R3_TEXT = "Antibiotic prescribing in primary care after a national awareness campaign\nMaria Garcia\nPublished 2019"
DOCUMENTS = {
    "smith2023.pdf": R1_TEXT,
    "lee2021.pdf": "Vaccination coverage in rural districts\nAnna Brown\n2022 doi: 10.1000/xyz.9",
    "garcia2019.pdf": R3_TEXT,
    "garcia2019_supp.pdf": "Supplementary appendix\n" + R3_TEXT,
    "10.1000_abc.2.pdf": R1_TEXT,
}


class FulltextTest(unittest.TestCase):
    def setUp(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "refs.ris"
            path.write_text(RIS, encoding="utf-8")
            self.records = cf.read_records(path)

    def test_reads_ris(self):
        self.assertEqual([r["id"] for r in self.records], ["R1", "R2", "R3", "R4"])
        self.assertEqual(self.records[0]["doi"], "10.1000/abc.1")
        self.assertEqual(self.records[2]["surname"], "garcia")

    def test_reports_every_kind_of_mismatch(self):
        result = cf.match(self.records, DOCUMENTS)
        self.assertEqual(result["missing"], ["R2", "R4"])
        self.assertEqual(result["duplicates"], {"R1": ["smith2023.pdf", "10.1000_abc.2.pdf"]})
        self.assertEqual(result["supplements"], {"R3": ["garcia2019_supp.pdf"]})
        self.assertEqual(result["unmatched_files"], ["lee2021.pdf"])
        problems = {(n["file"], n["problem"]) for n in result["notes"]}
        self.assertIn(("10.1000_abc.2.pdf", "file name points to R2 but the content is R1"), problems)

    def test_a_supplement_or_a_citing_page_is_not_the_article(self):
        title = "Household contact tracing for drug-resistant tuberculosis in urban clinics"
        documents = {
            "okafor_supp1.pdf": f"Supplementary Online Content\nOkafor A, et al. {title}. doi:10.1000/abc.4\neTable 1",
            "patient_page.pdf": ("PATIENT PAGE\nFinding tuberculosis in the family\n" + "Tuberculosis spreads at home. " * 20 +
                                 f"Source: Okafor A. {title}. 2020. doi:10.1000/abc.4"),
        }
        result = cf.match(self.records, documents, {"okafor_supp1.pdf": 6, "patient_page.pdf": 1})
        self.assertIn("R4", result["missing"])
        self.assertEqual(result["supplements"], {"R4": ["okafor_supp1.pdf"]})
        self.assertEqual(result["unmatched_files"], ["patient_page.pdf"])
        self.assertTrue(any(n["file"] == "patient_page.pdf" and "not the article" in n["problem"]
                            for n in result["notes"]))

    def test_corrected_article_and_short_pdf(self):
        documents = {"garcia.pdf": "Erratum 22 April 2022. See Erratum.\nRESEARCH\n" + R3_TEXT,
                     "smith.pdf": R1_TEXT}
        result = cf.match(self.records, documents, {"garcia.pdf": 9, "smith.pdf": 1})
        self.assertEqual(result["matched"], {"R1": ["smith.pdf"], "R3": ["garcia.pdf"]})
        self.assertEqual([n["file"] for n in result["notes"]], ["smith.pdf"])
        self.assertIn("only 1 page", result["notes"][0]["problem"])

    def test_a_cited_doi_does_not_win_over_the_article(self):
        records = [{"id": "A", "title": "Checkpoint blockade in cancer immunotherapy reviewed",
                    "doi": "10.1000/review.a", "surname": "ribas", "year": "2018"},
                   {"id": "B", "title": "Adverse events of checkpoint blockade in cancer immunotherapy",
                    "doi": "10.1000/review.b", "surname": "postow", "year": "2018"}]
        text = ("Checkpoint blockade in cancer immunotherapy reviewed\nAntoni Ribas 2018 doi:10.1000/review.a\n"
                "Adverse events of checkpoint blockade in cancer immunotherapy were reviewed elsewhere "
                "(doi:10.1000/review.b).")
        self.assertEqual(cf.match(records, {"a.pdf": text})["matched"], {"A": ["a.pdf"]})

    def test_title_at_the_top_breaks_a_tie(self):
        records = [{"id": "B", "title": "Adverse events of checkpoint blockade in cancer immunotherapy",
                    "doi": "", "surname": "postow", "year": "2018"},
                   {"id": "A", "title": "Cancer immunotherapy using checkpoint blockade",
                    "doi": "", "surname": "ribas", "year": "2018"}]
        text = ("REVIEW\nCancer immunotherapy using checkpoint blockade\nAntoni Ribas\n" + "x " * 400 +
                "Adverse events of checkpoint blockade in cancer immunotherapy are common. 2018")
        self.assertEqual(cf.match(records, {"a.pdf": text})["matched"], {"A": ["a.pdf"]})

    def test_reads_csv_and_bibtex(self):
        with tempfile.TemporaryDirectory() as directory:
            csv_path = Path(directory) / "refs.csv"
            csv_path.write_text("Key,Title,Author,Publication Year,DOI\nK1,A title of several words here,"
                                "\"Lee, Kim\",2021,10.1000/abc.2\n", encoding="utf-8")
            bib_path = Path(directory) / "refs.bib"
            bib_path.write_text("@article{lee2021,\n  title = {A title of several words here},\n"
                                "  author = {Lee, Kim and Park, Jo},\n  year = {2021},\n  doi = {10.1000/ABC.2}\n}\n",
                                encoding="utf-8")
            for path in (csv_path, bib_path):
                record = cf.read_records(path)[0]
                self.assertEqual((record["doi"], record["year"], record["surname"]), ("10.1000/abc.2", "2021", "lee"))


if __name__ == "__main__":
    unittest.main()
