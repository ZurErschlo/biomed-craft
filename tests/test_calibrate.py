"""Tests for calibrate.py, using synthetic text in place of PDFs. Offline; standard library only."""

import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import calibrate as cb  # noqa: E402
import textstats as ts  # noqa: E402

_, RULES = ts.load_rules()
PROSE_RULES = [r for r in RULES if r.kind == "regex" and "prose" in r.scopes and not r.formats and not r.docs]
SENTENCE = ("Patients in the intervention group had fewer admissions than patients in the control group during "
            "the first year of follow-up. ")


class CalibrateTest(unittest.TestCase):
    def test_saved_text_keeps_its_labels(self):
        text = ("---\ndoi: 10.1056/NEJMoa0000001\ntitle: A synthetic trial\nyear: 2019\ntype: research\n"
                "design: trial\n---\n\nMethods\n\n" + SENTENCE * 40 + "\n\nResults\n\n" + SENTENCE * 40 + "\n")
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "10.1056_nejmoa0000001.md"
            path.write_text(text, encoding="utf-8")
            article = cb.analyse_text(cb.read_text(path), PROSE_RULES)
        self.assertEqual((article["doi"], article["journal"], article["year"], article["type"], article["design"]),
                         ("10.1056/nejmoa0000001", "NEJM", 2019, "research", "trial"))
        self.assertNotIn("title", article)

    def test_only_real_headings_switch_text_off(self):
        text = ("SUPPLEMENTARY MATERIALS\nMaterials and Methods\nReferences (31-33)\n\n" + SENTENCE * 10 +
                "\nMethods are described in the\nsupplementary materials.\n\n" + SENTENCE * 10 +
                "\n\nREFERENCES AND NOTES\n\n1. A. Author, A cited title. J. Synth. 1, 1 (2020).\n")
        paragraphs, _ = cb.clean_article(text)
        joined = " ".join(paragraphs)
        self.assertEqual(joined.count("first year of follow-up"), 20)
        self.assertNotIn("cited title", joined)

    def test_file_names_and_supplements(self):
        self.assertEqual(cb.doi_from_name("science.abc1234.pdf"), "10.1126/science.abc1234")
        self.assertEqual(cb.doi_from_name("scitranslmed.abc1234.pdf"), "10.1126/scitranslmed.abc1234")
        for name in ("joi990001supp1_prod.pdf", "nejmoa0000001_disclosures.pdf", "nejmoa0000001_data-sharing.pdf",
                     "author.sm.pdf", "abc1234_mdar_reproducibility_checklist.pdf"):
            self.assertTrue(cb.SUPPLEMENT_NAME.search(name), name)
        for name in ("science.abc1234.pdf", "joi990001.pdf", "NEJMoa0000001.pdf"):
            self.assertFalse(cb.SUPPLEMENT_NAME.search(name), name)
        self.assertTrue(cb.SUPPLEMENT_TEXT.search("This trial protocol has been provided by the authors to give\n"
                                                  "readers additional information about their work."))


if __name__ == "__main__":
    unittest.main()
