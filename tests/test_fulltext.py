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
        self.assertEqual(result["duplicates"], {"R1": ["smith2023.pdf", "10.1000_abc.2.pdf"],
                                                "R3": ["garcia2019.pdf", "garcia2019_supp.pdf"]})
        self.assertEqual(result["unmatched_files"], ["lee2021.pdf"])
        problems = {(n["file"], n["problem"]) for n in result["notes"]}
        self.assertIn(("garcia2019_supp.pdf", "looks like a supplement or an author manuscript"), problems)
        self.assertIn(("10.1000_abc.2.pdf", "file name points to R2 but the content is R1"), problems)

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
