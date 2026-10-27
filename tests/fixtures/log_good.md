# Execution log

Status: model fitted; deduplication pending. Next: refit after deduplication.

## 2026-05-12

- Fitted the Poisson model of monthly notifications (analysis/03_model.R). The deviance ratio was 2.8, so the negative binomial rule in the plan applies; output in data/output/model_nb.rds.
- Problem: 41 duplicate notification IDs after linkage; recorded before any rerun.
- Decision: deduplicate on ID and date of diagnosis before linkage (plan: Data, linkage).
