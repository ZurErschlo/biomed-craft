"""Tests for style_diff.py and the personal style file. Offline; standard library only."""

import os
import sys
import tempfile
import unittest
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
os.environ["BIOMED_CRAFT_HOME"] = tempfile.mkdtemp()

import scan  # noqa: E402
import style_diff as sd  # noqa: E402
import textstats as ts  # noqa: E402

PROFILE = ROOT / "tests" / "fixtures" / "style_profile.md"
DRAFT = ("In this cohort we performed the main analysis in 1204 patients. Notably, mortality was higher with resistance.\n\n"
         "We performed sensitivity analyses to utilize all available data. Notably, the estimates did not change.\n\n"
         "Costs were 4500 dollars per patient (Smith 2020).")
REVISED = ("In this cohort we did the main analysis in 1204 patients. Mortality was higher with resistance.\n\n"
           "We did sensitivity analyses to use all available data. The estimates did not change.\n\n"
           "Costs were 4800 dollars per patient (Smith 2020).")
DOCUMENT_XML = (
    '<w:document xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main"><w:body><w:p>'
    '<w:r><w:t xml:space="preserve">We </w:t></w:r>'
    '<w:del w:id="1" w:author="R"><w:r><w:delText>performed</w:delText></w:r></w:del>'
    '<w:ins w:id="2" w:author="R"><w:r><w:t>did</w:t></w:r></w:ins>'
    '<w:r><w:t xml:space="preserve"> the analysis.</w:t></w:r></w:p></w:body></w:document>'
)


class StyleDiffTest(unittest.TestCase):
    def test_counts_substitutions_and_sets_content_aside(self):
        result = sd.compare(DRAFT, REVISED)
        replaced = {(r["from"], r["to"]): r["count"] for r in result["replaced"]}
        self.assertEqual(replaced[("performed", "did")], 2)
        self.assertEqual(result["content_edits_set_aside"], 1)
        self.assertNotIn(("4500", "4800"), replaced)
        self.assertEqual(result["rules_removed"]["LEX-04"], {"before": 2, "after": 0})
        entries = [c["entry"] for c in result["candidates"]]
        self.assertIn("Prefer 'did' to 'performed'.", entries)
        self.assertTrue(all(c["scope"] == "Document: manuscript" for c in result["candidates"]))

    def test_reads_tracked_changes(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "tracked.docx"
            with zipfile.ZipFile(path, "w") as archive:
                archive.writestr("word/document.xml", DOCUMENT_XML)
            before, after = sd.tracked_versions(path)
        self.assertEqual((before, after), ("We performed the analysis.", "We did the analysis."))


class StyleFileTest(unittest.TestCase):
    def setUp(self):
        self.entries = ts.read_style(PROFILE)

    def test_scopes_apply_only_where_they_match(self):
        allowed = lambda doc, design, scope="prose": ts.style_allowed_rules(self.entries, doc, design, "core", scope)  # noqa: E731
        self.assertEqual(allowed("manuscript", "trial"), {"STR-01"})
        self.assertEqual(allowed("manuscript", "laboratory"), {"STR-01", "LEX-04"})
        self.assertEqual(allowed("plan", "trial"), set())
        self.assertNotIn("HYG-06", allowed("manuscript", "trial"))
        self.assertNotIn("CON-01", allowed("manuscript", "laboratory"))

    def test_scan_lists_allowed_findings_apart(self):
        _, rules = ts.load_rules()
        text = "The effect—small but real—persisted in the cohort. Notably, mortality fell in every group we studied."
        lab = scan.scan_file(Path("x.md"), rules, "manuscript", None, None, text=text, design="laboratory",
                             style=self.entries)
        trial = scan.scan_file(Path("x.md"), rules, "manuscript", None, None, text=text, design="trial",
                               style=self.entries)
        self.assertEqual(set(lab["allowed"]), {"STR-01", "LEX-04"})
        self.assertNotIn("STR-01", {f["rule"] for f in lab["findings"]})
        self.assertIn("LEX-04", {f["rule"] for f in trial["findings"]})


if __name__ == "__main__":
    unittest.main()
