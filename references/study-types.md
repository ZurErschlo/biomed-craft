# Study types

Identify the study type before writing or reviewing anything: the type decides the reporting guideline, the content a reader and a reviewer expect, the figures and tables, and some word choices. `scan.py` guesses the type from the text and prints its guess (`--type` overrides it).

Each file below covers one type: the content the paper must contain, what reviewers flag and the fix, and the writing conventions of leading journals for that type. General writing rules apply to every type; journal formats are in [journals.md](journals.md).

| Type | `--type` | Guideline | File |
|---|---|---|---|
| Health economic evaluation | `economic` | CHEERS 2022 | [study-types/economic.md](study-types/economic.md) |
| Disease and epidemiological modelling | `modelling` | GATHER, EPIFORGE 2020 | [study-types/modelling.md](study-types/modelling.md) |
| Systematic review and meta-analysis | `systematic-review` | PRISMA 2020, PRISMA-S, SWiM, PRISMA-ScR | [study-types/systematic-review.md](study-types/systematic-review.md) |
| Clinical prediction model | `prediction` | TRIPOD+AI, PROBAST | [study-types/prediction.md](study-types/prediction.md) |
| Observational study or database analysis | `observational` | STROBE, RECORD | [study-types/observational.md](study-types/observational.md) |
| Mendelian randomisation | `mendelian-randomisation` | STROBE-MR | [study-types/mendelian-randomisation.md](study-types/mendelian-randomisation.md) |
| Bioinformatics and computational | `computational` | REMARK, TRIPOD+AI, STREGA | [study-types/computational.md](study-types/computational.md) |
| Randomised trial | `trial` | CONSORT 2025, SPIRIT 2025 | [study-types/trial.md](study-types/trial.md) |
| Diagnostic accuracy | `diagnostic` | STARD 2015, STARD-AI | [study-types/diagnostic.md](study-types/diagnostic.md) |
| Laboratory and mechanistic | `laboratory` | ARRIVE 2.0, MDAR, MIQE 2.0 | [study-types/laboratory.md](study-types/laboratory.md) |
| Narrative and clinical review | `review` | SANRA (appraisal) | [study-types/review.md](study-types/review.md) |
| Qualitative and mixed methods | none; name it in the request | SRQR, COREQ, GRAMMS | [study-types/qualitative.md](study-types/qualitative.md) |
