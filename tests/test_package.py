"""Package-level checks: metadata, the skill's own prose and the rewrite cases. Offline."""

import json
import subprocess
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "scripts"
sys.path.insert(0, str(SCRIPTS))

import scan  # noqa: E402
import textstats as ts  # noqa: E402

_, RULES = ts.load_rules()


class PackageTest(unittest.TestCase):
    def test_validate_package_passes(self):
        result = subprocess.run([sys.executable, str(SCRIPTS / "validate_package.py")], capture_output=True, text=True,
                                encoding="utf-8")
        self.assertEqual(result.returncode, 0, result.stderr)

    def test_skill_prose_passes_its_own_scanner(self):
        documents = [ROOT / "SKILL.md"] + sorted(p for p in (ROOT / "references").glob("*.md") if p.name != "sources.md")
        for document in documents:
            result = scan.scan_file(document, RULES, "manuscript", None, None)
            must = [f"{f['rule']}: {f['context']}" for f in result["findings"] if f["level"] == "must"]
            self.assertEqual(must, [], f"{document.name}: {must}")

    def test_rewrite_cases_are_well_formed(self):
        cases = json.loads((ROOT / "tests" / "fixtures" / "cases.json").read_text(encoding="utf-8"))
        rule_ids = {r.id for r in RULES}
        ids = [c["id"] for c in cases]
        self.assertEqual(len(ids), len(set(ids)))
        self.assertGreaterEqual(len(cases), 15)
        for case in cases:
            self.assertTrue(case["request"].strip() and case["input"].strip(), case["id"])
            self.assertTrue(set(case["focus"]) <= rule_ids, case["id"])
            self.assertIsInstance(case["keep"], list)

    def test_scripts_run_from_a_copied_skill_folder(self):
        import shutil
        import tempfile
        with tempfile.TemporaryDirectory(prefix="plain paper ") as directory:
            copy = Path(directory) / "skills" / "plain-paper"
            shutil.copytree(ROOT, copy, ignore=shutil.ignore_patterns(".git", "__pycache__"))
            result = subprocess.run([sys.executable, str(copy / "scripts" / "scan.py"), "--strict",
                                     str(copy / "tests" / "fixtures" / "flagship_style.md")],
                                    capture_output=True, text=True, encoding="utf-8", cwd=directory)
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)


if __name__ == "__main__":
    unittest.main()
