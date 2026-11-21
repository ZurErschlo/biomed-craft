"""Tests for check_numbers.py. Offline; standard library only."""

import json
import subprocess
import sys
import tempfile
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

    def test_of_total_counts_and_bare_intervals(self):
        self.assertEqual([p.match for p in cn.percentage_problems("Of 2104 patients, 482 (25.9%) died.", 1)],
                         ["Of 2104 patients, 482 (25.9%)"])
        self.assertEqual(cn.interval_problems("The range was (0.75-0.93) in the cohort.", 1), [])

    def test_inline_abstract_label(self):
        segments = cn.ts.read_markdown("Abstract: Mortality fell by 41%.\n\nResults: Mortality fell by 37%.")
        self.assertEqual([p.match for p in cn.abstract_problems(segments)], ["41"])

    def test_abstract_numbers_must_appear_elsewhere(self):
        result = cn.check_file(FIXTURE)
        self.assertEqual([p["match"] for p in result["problems"] if p["kind"] == "abstract"], ["37"])

    def test_cli(self):
        result = subprocess.run([sys.executable, str(SCRIPTS / "check_numbers.py"), "--strict", "--json", str(FIXTURE)],
                                capture_output=True, text=True, encoding="utf-8")
        self.assertEqual(result.returncode, 1)
        self.assertEqual(json.loads(result.stdout)["problems"], 5)

    def test_notes_do_not_count_as_problems(self):
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / "notes.md"
            path.write_text("The odds ratio was 2.10 (95% CI 1.20–2.94). Welch's test gave t(27.3) = 2.2, P = .30. "
                            "A mean of 3.45 (n = 30) was reported.\n", encoding="utf-8")
            command = [sys.executable, str(SCRIPTS / "check_numbers.py"), "--strict", "--json", str(path)]
            plain = subprocess.run(command, capture_output=True, text=True, encoding="utf-8")
            grim = subprocess.run(command[:2] + ["--grim-items", "1"] + command[2:], capture_output=True, text=True,
                                  encoding="utf-8")
        self.assertEqual(plain.returncode, 0)
        self.assertEqual(len(json.loads(plain.stdout)["files"][0]["notes"]), 2)
        self.assertEqual(grim.returncode, 1)
        self.assertEqual(json.loads(grim.stdout)["files"][0]["problems"][0]["kind"], "grim")


FLOW = """Figure 1: Study selection

Records identified from: Databases (n = 1180), Registers (n = 40)

Records removed before screening: Duplicate records removed (n = 300), Records marked as ineligible by automation tools (n = 20), Records removed for other reasons (n = 10)

Records screened (n = 890)

Records excluded (n = 760)

Reports sought for retrieval (n = 130)

Reports not retrieved (n = 6)

Reports assessed for eligibility (n = 124)

Reports excluded: Wrong population (n = 50), Wrong outcome (n = 30), Not a trial (n = 14)

Reports of included studies (n = 30)

Studies included in review (n = 26)
"""


class StatisticsTest(unittest.TestCase):
    def test_p_values_match_reference_values(self):
        self.assertAlmostEqual(cn.two_sided_p("z", 1.96, None, None), 0.05, places=4)
        self.assertAlmostEqual(cn.two_sided_p("t", 2.0, 10, None), 0.0734, places=4)
        self.assertAlmostEqual(cn.two_sided_p("F", 4.0, 1, 10), cn.two_sided_p("t", 2.0, 10, None), places=10)
        self.assertAlmostEqual(cn.two_sided_p("chi2", 3.841, 1, None), 0.05, places=4)
        self.assertAlmostEqual(cn.two_sided_p("chi2", 10.0, 4, None), 0.0404, places=4)

    def test_reported_p_values(self):
        def messages(text):
            return [p.message for p in cn.statistic_problems(text, 1)[0]]
        for consistent in ("The groups differed (t(28) = 2.10, P = .045).", "Groups differed, F(2, 45) = 4.12, p = 0.023.",
                           "The association held (χ²(1) = 5.20, P = 0.023).", "z = 1.96, P = .05",
                           "Rates differed (chi-square = 6.5, df = 2, P = .04).", "The rate rose (z = 4.2; P = 2.7 × 10−5).",
                           "t = 2.1, P = .04", "The effect was large (z = 4.417, P = 1e-5).",
                           "Fit was adequate (χ²(1000000) = 1000000, P = .50)."):
            self.assertEqual(messages(consistent), [], consistent)
        self.assertEqual(messages("We found χ²(1) = -3.84, P = .05 overall."), ["a χ² statistic cannot be negative"])
        self.assertEqual(messages("We found F(2, 30) = -4.00, P = .029 overall."), ["an F statistic cannot be negative"])
        self.assertEqual(messages("The groups differed (t(28) = 2.10, P = .21)."),
                         ["t(28) = 2.10 gives a two-sided P between 0.044 and 0.045, not P = .21"])
        self.assertEqual(messages("The association held (χ²(1) = 5.20, P < 0.001)."),
                         ["χ²(1) = 5.20 gives P of about 0.023, not P < 0.001"])
        one_sided = messages("Scores rose, t(20) = 1.80, P = .04.")
        self.assertEqual(len(one_sided), 1)
        self.assertIn("fits a one-sided test", one_sided[0])

    def test_tests_that_cannot_be_checked_become_notes(self):
        problems, notes = cn.statistic_problems("Welch's test gave t(27.3) = 2.2, P = .30.", 1)
        self.assertEqual(problems, [])
        self.assertIn("'Welch'", notes[0].message)
        problems, notes = cn.statistic_problems("Fit was poor (χ²(1000000000) = 1000000000, P = .50).", 1)
        self.assertEqual(problems, [])
        self.assertIn("could not be computed", notes[0].message)

    def test_ratio_intervals_on_the_log_scale(self):
        self.assertEqual(cn.symmetry_notes("The odds ratio was 2.10 (95% CI 1.50–2.94). The hazard ratio was 0.82 "
                                           "(95% CI 0.71–0.94).", 1), [])
        notes = cn.symmetry_notes("The odds ratio was 2.10 (95% CI 1.20–2.94).", 1)
        self.assertEqual(len(notes), 1)
        self.assertIn("centers on 1.88", notes[0].message)
        self.assertEqual(cn.symmetry_notes("The odds ratio was 2.10 (95% UI 1.20–2.94).", 1), [])
        self.assertEqual(cn.symmetry_notes("The HR was 2.10 (95% CI 1.20–2.94) from a bootstrap interval.", 1), [])

    def test_grim(self):
        text = "Item scores had a mean of 3.45 (n = 30) in one group and a mean of 3.47 (n = 30) in the other."
        self.assertEqual([p.match for p in cn.grim_problems(text, 1, 1)], ["mean of 3.45 … n = 30"])
        self.assertEqual(cn.grim_problems(text, 1, 4), [])  # 120 answers: every value with two decimals is possible
        self.assertEqual(cn.grim_problems("The mean was 3.45 in 30 people (n = 30, n = 28).", 1, 1), [])


class FlowTest(unittest.TestCase):
    def check(self, text):
        return [(p.match, p.message) for p in cn.flow_problems(cn.ts.read_markdown(text))]

    def test_consistent_flow(self):
        self.assertEqual(self.check(FLOW), [])

    def test_flow_arithmetic(self):
        text = FLOW.replace("Records screened (n = 890)", "Records screened (n = 880)").replace(
            "Wrong outcome (n = 30)", "Wrong outcome (n = 31)").replace("in review (n = 26)", "in review (n = 32)")
        self.assertEqual(self.check(text), [
            ("records screened (n = 880)", "1220 identified minus 330 removed before screening is 890"),
            ("reports sought for retrieval (n = 130)", "880 minus 760 is 120"),
            ("reports of included studies (n = 30)", "124 minus 95 is 29")])  # 32 studies in 30 reports is possible

    def test_duplicate_as_a_reason_for_exclusion(self):
        text = ("Records identified (n = 100)\nDuplicates removed (n = 10)\nRecords screened (n = 90)\n"
                "Records excluded (n = 10)\nReports sought for retrieval (n = 80)\nReports not retrieved (n = 0)\n"
                "Reports assessed for eligibility (n = 80)\nReports excluded:\nWrong outcome (n = 40)\n"
                "Duplicate population (n = 20)\nReports of included studies (n = 20)\nStudies included in review (n = 22)\n")
        self.assertEqual(self.check(text), [])

    def test_reasons_and_repeated_labels(self):
        text = FLOW.replace("Reports excluded: Wrong population", "Reports excluded (n = 94): Wrong population")
        self.assertEqual(self.check(text), [])
        self.assertEqual(self.check(text.replace("(n = 94)", "(n = 90)")),
                         [("reports excluded (n = 90)", "the reasons add up to 94"),
                          ("reports of included studies (n = 30)", "124 minus 90 is 34")])
        twice = FLOW + "\nRecords screened (n = 400)\n"
        self.assertEqual(self.check(twice), [])


if __name__ == "__main__":
    unittest.main()
