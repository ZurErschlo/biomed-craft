"""Tests for scan.py and the shared text helpers. Offline; standard library only."""

import json
import os
import subprocess
import sys
import tempfile
import unittest
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "scripts"
FIXTURES = Path(__file__).resolve().parent / "fixtures"
sys.path.insert(0, str(SCRIPTS))
# Keep the researcher's own style file out of the tests.
os.environ["BIOMED_CRAFT_HOME"] = tempfile.mkdtemp()

import scan  # noqa: E402
import textstats as ts  # noqa: E402

RULE_DATA, RULES = ts.load_rules()
EXAMPLES = {item["id"]: item["examples"] for item in RULE_DATA["rules"]}
STYLE_CATEGORIES = {"CON", "DEF", "META", "LEX", "STR", "FMT", "CAP"}


def rules_found(path: Path, doc: str = "manuscript", scope=None) -> set[str]:
    result = scan.scan_file(path, RULES, doc, scope, None)
    return {f["rule"] for f in result["findings"]}


def write_docx(path: Path, paragraphs: list[tuple[str, str]]) -> None:
    body = "".join(
        f'<w:p><w:pPr><w:pStyle w:val="{style}"/></w:pPr><w:r><w:t>{text}</w:t></w:r></w:p>'
        for style, text in paragraphs
    )
    xml = ('<?xml version="1.0" encoding="UTF-8"?><w:document xmlns:w="http://schemas.openxmlformats.org/'
           f'wordprocessingml/2006/main"><w:body>{body}</w:body></w:document>')
    with zipfile.ZipFile(path, "w") as archive:
        archive.writestr("word/document.xml", xml)


def write_pptx(path: Path, slides: list[str]) -> None:
    with zipfile.ZipFile(path, "w") as archive:
        for number, text in enumerate(slides, start=1):
            xml = ('<?xml version="1.0" encoding="UTF-8"?><p:sld xmlns:p="http://schemas.openxmlformats.org/'
                   'presentationml/2006/main" xmlns:a="http://schemas.openxmlformats.org/drawingml/2006/main">'
                   f'<p:cSld><p:spTree><p:sp><p:txBody><a:p><a:r><a:t>{text}</a:t></a:r></a:p></p:txBody></p:sp>'
                   '</p:spTree></p:cSld></p:sld>')
            archive.writestr(f"ppt/slides/slide{number}.xml", xml)


class RuleExamplesTest(unittest.TestCase):
    def test_every_regex_rule_matches_its_examples(self):
        for rule in ts.regex_rules(RULES):
            examples = EXAMPLES[rule.id]
            self.assertTrue(examples["hit"], f"{rule.id} has no hit example")
            for text in examples["hit"]:
                self.assertTrue(ts.rule_matches(rule, text), f"{rule.id} should match: {text}")
            for text in examples["miss"]:
                self.assertFalse(ts.rule_matches(rule, text), f"{rule.id} should not match: {text}")

    def test_rule_ids_are_unique_and_well_formed(self):
        ids = [r.id for r in RULES]
        self.assertEqual(len(ids), len(set(ids)))
        for rule in RULES:
            self.assertRegex(rule.id, r"^[A-Z]{3,4}-\d{2}$")
            self.assertIn(rule.category, RULE_DATA["categories"])
            self.assertIn(rule.level, RULE_DATA["levels"])
            self.assertTrue(set(rule.scopes) <= set(ts.SCOPES))
            self.assertTrue(rule.hint.strip())


class BuiltinChecksTest(unittest.TestCase):
    def scan_text(self, text: str, doc: str = "manuscript") -> set[str]:
        segments = ts.read_markdown(text)
        findings, _ = scan.scan_segments(segments, RULES, "test", "md", doc)
        return {f.rule for f in findings}

    def test_stacked_openers(self):
        self.assertIn("STR-04", self.scan_text("Moreover, costs rose. Furthermore, uptake fell."))
        self.assertNotIn("STR-04", self.scan_text("However, costs rose. Uptake fell."))

    def test_rhetorical_question(self):
        self.assertIn("STR-05", self.scan_text("Why does uptake vary so much? Access is the main reason."))
        self.assertNotIn("STR-05", self.scan_text("Uptake varied by district."))

    def test_response_letters_may_describe_revisions(self):
        text = "As requested by the reviewer, we added a sensitivity analysis."
        self.assertIn("META-02", self.scan_text(text))
        self.assertNotIn("META-02", self.scan_text(text, doc="response"))


class FormatsTest(unittest.TestCase):
    def test_leading_journal_style_text_has_no_findings(self):
        result = scan.scan_file(FIXTURES / "leading_style.md", RULES, "manuscript", None, None)
        must = [f for f in result["findings"] if f["level"] == "must"]
        review = [f for f in result["findings"] if f["level"] == "review"]
        self.assertEqual(must, [], must)
        self.assertEqual(review, [], review)

    def test_ai_style_text_triggers_expected_rules(self):
        found = rules_found(FIXTURES / "ai_style.md")
        expected = {"LEX-02", "CON-01", "META-03", "ENG-01", "ENG-02", "ENG-04", "META-10", "META-02", "STR-04",
                    "DEF-01", "DEF-02", "STR-03", "STR-07", "DEF-08", "DEF-05", "DEF-07", "META-05", "CAP-01",
                    "HYG-01", "HYG-03", "HYG-07"}
        self.assertTrue(expected <= found, expected - found)

    def test_markdown_code_is_skipped(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "draft.md"
            path.write_text("Costs rose in `amr_rate` terms.\n\n```python\nwe delve into code\n```\n", encoding="utf-8")
            self.assertEqual(rules_found(path), set())

    def test_r_plotting_code(self):
        found = rules_found(FIXTURES / "plot.R")
        self.assertTrue({"FIG-01", "FIG-02", "FIG-03", "FIG-05"} <= found, found)
        segments = ts.read_segments(FIXTURES / "plot.R")
        texts = {s.text for s in segments}
        self.assertIn("Incidence (per 100 000)", texts)
        self.assertIn("HR 0.69", texts)
        self.assertNotIn("Helvetica", texts)
        self.assertNotIn("text", texts)

    def test_python_plotting_code(self):
        found = rules_found(FIXTURES / "plot.py")
        self.assertTrue({"FIG-01", "HYG-03"} <= found, found)
        texts = {s.text for s in ts.read_segments(FIXTURES / "plot.py")}
        self.assertNotIn("black", texts)
        self.assertNotIn("upper left", texts)

    def test_quarto_chunks_are_read_for_figure_text(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "paper.qmd"
            path.write_text('Mortality fell.\n\n```{r}\np + labs(subtitle = "Descriptive only")\n```\n', encoding="utf-8")
            self.assertIn("FIG-01", rules_found(path))

    def test_svg_text(self):
        self.assertIn("HYG-03", rules_found(FIXTURES / "figure.svg"))

    def test_latex(self):
        segments = ts.read_segments(FIXTURES / "sample.tex")
        scopes = {s.scope for s in segments}
        self.assertEqual(scopes, {"prose", "caption"})
        found = rules_found(FIXTURES / "sample.tex")
        self.assertIn("LEX-01", found)
        self.assertIn("META-05", found)
        self.assertNotIn("HYG-03", found)

    def test_docx(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "paper.docx"
            write_docx(path, [("Normal", "We delve into costs."), ("Caption", "This figure shows incidence by year."),
                              ("Normal", "**Background** Tuberculosis is common.")])
            segments = ts.read_segments(path)
            self.assertEqual([s.scope for s in segments], ["prose", "caption", "prose"])
            found = rules_found(path)
            self.assertTrue({"LEX-01", "META-05", "STR-09"} <= found, found)

    def test_pptx(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "talk.pptx"
            write_pptx(path, ["Our approach is groundbreaking", "Results are in fig_final"])
            segments = ts.read_segments(path)
            self.assertEqual([s.scope for s in segments], ["slide", "slide"])
            self.assertTrue({"LEX-01", "HYG-07"} <= rules_found(path))


class CommandLineTest(unittest.TestCase):
    def run_scan(self, *args, cwd=None):
        return subprocess.run([sys.executable, str(SCRIPTS / "scan.py"), *args], capture_output=True, text=True,
                              encoding="utf-8", cwd=cwd)

    def test_json_and_strict_from_unrelated_directory(self):
        with tempfile.TemporaryDirectory() as directory:
            result = self.run_scan("--json", str(FIXTURES / "ai_style.md"), cwd=directory)
            self.assertEqual(result.returncode, 0, result.stderr)
            payload = json.loads(result.stdout)
            self.assertGreater(payload["summary"]["must"], 0)
            strict = self.run_scan("--strict", str(FIXTURES / "ai_style.md"), cwd=directory)
            self.assertEqual(strict.returncode, 1)
            clean = self.run_scan("--strict", str(FIXTURES / "leading_style.md"), cwd=directory)
            self.assertEqual(clean.returncode, 0, clean.stdout)

    def test_profile_uses_calibration(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "long.md"
            text = (FIXTURES / "leading_style.md").read_text(encoding="utf-8")
            path.write_text("\n\n".join([text] * 3), encoding="utf-8")
            result = self.run_scan("--json", "--profile", "--journal", "lancet", str(path))
            self.assertEqual(result.returncode, 0, result.stderr)
            profile = json.loads(result.stdout)["files"][0]["profile"]
            metrics = {row["metric"]: row for row in profile}
            self.assertIn("sentence_median", metrics)
            self.assertIsNotNone(metrics["sentence_median"]["p10"])

    def test_unknown_reference_group_is_an_error(self):
        result = self.run_scan("--journal", "nowhere", str(FIXTURES / "leading_style.md"))
        self.assertEqual(result.returncode, 2)

    def test_help(self):
        for script in ("scan.py", "check_preservation.py", "calibrate.py"):
            result = subprocess.run([sys.executable, str(SCRIPTS / script), "--help"], capture_output=True, text=True,
                                    encoding="utf-8")
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertIn("usage:", result.stdout.lower())


class CalibrationTest(unittest.TestCase):
    def test_calibration_and_corpus_agree(self):
        calibration = ts.load_calibration()
        corpus = json.loads((SCRIPTS / "corpus.json").read_text(encoding="utf-8"))
        research = [p for p in corpus if p["type"] == "research"]
        self.assertEqual(calibration["groups"]["core"]["papers"], len(research))
        self.assertGreaterEqual(len(research), 100)
        for paper in corpus:
            self.assertRegex(paper["doi"], r"^10\.\d{4,9}/")
            self.assertNotIn("text", paper)

    def test_must_level_style_rules_are_rare_in_leading_journal_prose(self):
        calibration = ts.load_calibration()
        before = calibration["groups"]["core_before_2023"]["rules"]
        core = calibration["groups"]["core"]["rules"]
        for rule in RULES:
            if rule.level != "must" or rule.category not in STYLE_CATEGORIES or rule.id not in core:
                continue
            self.assertLessEqual(before[rule.id]["paper_share"], 0.10, rule.id)
            self.assertLessEqual(core[rule.id]["per_10k_words"], 0.6, rule.id)

    def test_must_level_style_rules_are_rare_in_every_design_and_family(self):
        calibration = ts.load_calibration()
        named = set(RULE_DATA["designs"]) | set(RULE_DATA["families"])
        for name, group in calibration["groups"].items():
            if name not in named or group["papers"] < 20:
                continue
            for rule in RULES:
                stats = group["rules"].get(rule.id)
                if stats is None or rule.category not in STYLE_CATEGORIES:
                    continue
                if rule.level_for(name, name) == "must":
                    self.assertLessEqual(stats["paper_share"], 0.15, f"{rule.id} in {name}")
                    self.assertLessEqual(stats["per_10k_words"], 1.0, f"{rule.id} in {name}")


class ResearchDocumentsTest(unittest.TestCase):
    def must_and_review(self, name: str, doc: str) -> tuple[set[str], set[str]]:
        result = scan.scan_file(FIXTURES / name, RULES, doc, None, None)
        must = {f["rule"] for f in result["findings"] if f["level"] == "must"}
        review = {f["rule"] for f in result["findings"] if f["level"] == "review"}
        return must, review

    def test_plan_rules(self):
        must, review = self.must_and_review("plan_bad.md", "plan")
        self.assertTrue({"PLAN-01", "PLAN-02", "PLAN-03", "PLAN-04", "META-12"} <= must, must)
        self.assertTrue({"PLAN-05", "PLAN-07"} <= review, review)
        self.assertEqual(self.must_and_review("plan_good.md", "plan"), (set(), set()))

    def test_log_rules_allow_dates_and_file_names(self):
        must, review = self.must_and_review("log_bad.md", "log")
        self.assertEqual(must, {"META-12"})
        self.assertEqual(review, {"LOG-01", "LOG-02"})
        self.assertEqual(self.must_and_review("log_good.md", "log"), (set(), set()))

    def test_code_rules(self):
        must, review = self.must_and_review("analysis_bad.R", "code")
        expected = {"CODE-01", "CODE-02", "CODE-03", "CODE-04", "CODE-05", "CODE-06", "CODE-07", "CODE-08",
                    "CODE-10", "CODE-11", "HYG-06", "META-12"}
        self.assertTrue(expected <= must, expected - must)
        self.assertIn("CODE-12", review)
        self.assertEqual(self.must_and_review("analysis_good.R", "code"), (set(), set()))

    def test_document_rules_stay_out_of_manuscripts(self):
        found = rules_found(FIXTURES / "plan_bad.md")
        self.assertFalse({r for r in found if r.startswith(("PLAN", "LOG", "CODE"))}, found)

    def test_comments_and_strings(self):
        segments = ts.read_code('x <- "a # b"  # why: keep the hash\n# Purpose: demo', "r")
        self.assertEqual([(s.scope, s.text) for s in segments if s.scope != "figure"],
                         [("code", 'x <- "a # b"'), ("comment", "why: keep the hash"), ("comment", "Purpose: demo")])


class StudyDesignTest(unittest.TestCase):
    TEXTS = {
        "economic": "We estimated the incremental cost-effectiveness ratio (ICER) per quality-adjusted life-year (QALY) "
                    "gained. Costs and QALYs were discounted. The ICER was below the willingness-to-pay threshold, and "
                    "the strategy was cost-effective in 80% of simulations; budget impact was modest. QALYs were "
                    "estimated from EQ-5D. The ICER was sensitive to price.",
        "systematic-review": "We did a systematic review and meta-analysis registered with PROSPERO and reported to "
                             "PRISMA. We searched MEDLINE, Embase and Web of Science. Two reviewers assessed risk of "
                             "bias. Pooled estimates came from random-effects models. The meta-analysis included 40 "
                             "studies, and the systematic review found consistent results.",
        "trial": "In this double-blind, placebo-controlled trial, patients were randomly assigned to drug or placebo. "
                 "Randomisation was stratified by site. The primary end point was death at 28 days in the "
                 "intention-to-treat population, reported to CONSORT. Randomised patients who received placebo had "
                 "more events; placebo recipients were followed for 90 days. The randomised groups were similar.",
        "laboratory": "Mice lacking the receptor were generated with CRISPR. Western blot and flow cytometry of mouse "
                      "tissue showed loss of the protein. In vitro, cell lines transfected with the plasmid recovered "
                      "the phenotype, and in vivo the knockout mice were protected.",
        "computational": "We analysed single-cell RNA-seq data and bulk RNA-seq data with a bioinformatic pipeline. "
                         "Reads were aligned to the reference genomes, and genome-wide association statistics were "
                         "combined with a machine learning model and phylogenetic analysis.",
        "modelling": "We built a compartmental transmission model calibrated to notification data and simulated "
                     "scenarios to 2035. Projections under each scenario were compared with the status quo, and "
                     "simulations varied the reproduction number.",
        "mendelian-randomisation": "We did a two-sample Mendelian randomisation study with genetic instruments for "
                                   "body mass index. Genetically predicted adiposity was associated with risk. MR-Egger and "
                                   "weighted median estimates agreed, pleiotropy tests were null, and we followed STROBE-MR. "
                                   "Mendelian randomisation estimates were consistent across instrumental variables.",
        "prediction": "We developed and externally validated a prediction model with LASSO and present it as a nomogram. "
                      "Discrimination (C statistic) and calibration slope were good, the calibration plot was close to the "
                      "diagonal, decision curve analysis showed net benefit, and we followed TRIPOD and PROBAST. The "
                      "prediction model kept its discrimination at external validation.",
        "observational": "In this population-based cohort study, we used registry data and electronic health records. "
                         "Hazard ratios were estimated with Cox models, and odds ratios with logistic regression, "
                         "adjusted for confounders identified from the cohort.",
    }

    def test_designs_are_detected(self):
        for design, text in self.TEXTS.items():
            self.assertEqual(ts.detect_design(text)[0], design, design)

    def test_design_edge_cases(self):
        review = ("This review summarises the evidence from randomised trials of anticoagulation after venous "
                  "thromboembolism. " + "Patients were randomly assigned to drug or placebo in double-blind trials "
                  "with intention-to-treat analyses. " * 3)
        self.assertEqual(ts.detect_design(review)[0], "review")
        eqtl = "We mapped cis-eQTL and cis-pQTL across tissues; pleiotropy was common and instrumental variables were scarce. " * 3
        self.assertNotEqual(ts.detect_design(eqtl)[0], "mendelian-randomisation")
        early = ("In this first-in-human, open-label, dose-escalation phase 1 trial, patients received the antibody. "
                 "Dose-limiting toxicities were recorded during the phase 1 study. " * 2 +
                 "We also studied the antibody in mice and in cell lines.")
        self.assertEqual(ts.detect_design(early)[0], "trial")
        emulation = ("The emulated target trial compared randomly assigned initiation with placebo in an "
                     "intention-to-treat analysis of registry data. " * 3)
        self.assertEqual(ts.detect_design(emulation)[0], "observational")

    def test_dashes_exclude_ranges(self):
        text = "The effect—small but real—persisted, and one factor – cost – dominated from 2010–2020 in ages 18 – 65."
        self.assertEqual(len(ts.DASH.findall(text)), 4)

    def test_review_needs_no_methods_heading(self):
        text = "In this Review, we summarise treatment of latent tuberculosis.\n\nThis Review discusses new regimens."
        self.assertEqual(ts.detect_design(text)[0], "review")
        self.assertNotEqual(ts.detect_design("Methods\n" + text)[0], "review")

    def test_levels_follow_the_design(self):
        lex11 = next(r for r in RULES if r.id == "LEX-11")
        self.assertEqual((lex11.level_for("trial"), lex11.level_for("review"), lex11.level_for("")),
                         ("must", "review", "must"))
        result = scan.scan_file(Path("x.md"), RULES, "manuscript", None, None,
                                text="An intriguing finding emerged in this cohort.", design="laboratory")
        self.assertEqual([(f["rule"], f["level"]) for f in result["findings"]], [("LEX-11", "review")])


if __name__ == "__main__":
    unittest.main()
