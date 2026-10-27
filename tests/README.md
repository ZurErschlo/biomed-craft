# Testing

Two kinds of test: automatic tests for the scripts, and rewrite cases for checking what an agent does with the skill.

## Automatic tests

```bash
python3 scripts/validate_package.py
python3 -m unittest discover -s tests -v
```

They check every rule against its examples, reading of each file format, the command-line options and exit codes, a passage in leading-journal style with no findings, an AI-style passage with the expected findings, the preservation check, and that must-level style rules stay rare in the calibration corpus.

## Rewrite cases

[fixtures/cases.json](fixtures/cases.json) holds synthetic passages, each with the request to give an agent. `keep` lists facts the rewrite must preserve and `focus` lists the rule IDs a good rewrite should address. Do not show `keep` or `focus` to the agent.

1. Give an agent the skill (or only `SKILL.md` and `references/`) and run each `request` on its `input`. Save each output to its own file.
2. Run the scripts on each output:

   ```bash
   python3 scripts/scan.py --level must output.md
   python3 scripts/check_preservation.py input.md output.md
   ```

3. Read every output and answer:
   - Did it add a fact, number, source or claim that the input did not contain?
   - Did it drop a number, condition, comparator, negation, time frame or citation?
   - Did it make a claim stronger or turn an association into a cause?
   - Did it remove a hedge that carried real uncertainty, or a null result?
   - Did it leave a sentence that was already fine unchanged?
   - Did it introduce new tells (formal substitutes, choppy short sentences, new contrast frames)?
   - Does the result read like the target journal?

One run per case shows behaviour on that run only. Add your own passages (with private details removed) to cover the documents you write.
