"""Tests for check_numbers.py. Offline; standard library only."""

import json
import subprocess
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "scripts"
FIXTURE = Path(__file__).resolve().parent / "fixtures" / "numbers.md"
sys.path.insert(0, str(SCRIPTS))

import check_numbers as cn  # noqa: E402


class NumbersTest(unittest.TestCase):
    def test_percentages(self):
        found = [p.match for p in cn.percentage_problems(
            "482 of 2104 patients (25.9%) died; 49 (2%) of 2609 died; 13/40 (35%) relapsed; 482/2104 (22·9%).", 1)]
        self.assertEqual(found, ["482 of 2104 patients (25.9%)", "13/40 (35%)"])

    def test_intervals(self):
        messages = [p.message for p in cn.interval_problems(
            "The odds ratio was 1·52 (95% CI 1·61–2·10). (HR, 0.83; 95% CI, 0.93-0.75). "
            "The rate ratio was 1.2 (0.0–3.4). Median age was 45 (30–60) years. "
            "(HR, 0.83; 95% CI, 0.75-0.93) and hazard ratio, 0.83; 95% confidence interval [CI], 0.75 to 0.93).", 1)]
        self.assertEqual(messages, ["the estimate lies outside its interval", "the lower bound is above the upper bound",
                                    "a ratio interval cannot reach zero"])

    def test_abstract_numbers_must_appear_elsewhere(self):
        result = cn.check_file(FIXTURE)
        self.assertEqual([p["match"] for p in result["problems"] if p["kind"] == "abstract"], ["37"])

    def test_cli(self):
        result = subprocess.run([sys.executable, str(SCRIPTS / "check_numbers.py"), "--strict", "--json", str(FIXTURE)],
                                capture_output=True, text=True, encoding="utf-8")
        self.assertEqual(result.returncode, 1)
        self.assertEqual(json.loads(result.stdout)["problems"], 5)


if __name__ == "__main__":
    unittest.main()
