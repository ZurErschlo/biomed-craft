"""Tests for check_preservation.py. Offline; standard library only."""

import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

SCRIPTS = Path(__file__).resolve().parents[1] / "scripts"
sys.path.insert(0, str(SCRIPTS))

import check_preservation as cp  # noqa: E402

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


if __name__ == "__main__":
    unittest.main()
