# ADR-008: Composite Risk Score Instead of ML or a Single-Threshold Rule

## Status
Accepted

## Context
LOOCV evaluation of XGBoost (4-class and binary) and Logistic
Regression, benchmarked against majority-class baselines, showed no
model reliably beating baseline at n=13 (ADR-006, ADR-007).
Additionally, inspecting the single strongest candidate feature
(rainfall as a percentage of normal) against real 2018 severity labels
showed no monotonic relationship — the highest-ratio district (Idukki,
2.8x normal rainfall) was not the most severe, and a lower-ratio
district (Kollam) had the lowest severity label. This suggested real
flood severity in this event was driven by factors beyond rainfall
ratio alone (e.g., terrain, dam discharge, drainage) not present in
this dataset.

## Decision
Use a transparent, weighted composite score combining three available
real signals — rainfall ratio to normal, landslide count, and rainfall
deviation from normal — with explicitly documented, non-fitted weights
(0.4 / 0.4 / 0.2), as the v1 severity estimator. This is implemented in
`services/rule_based_predictor.py` behind the same `SeverityPredictor`
interface an ML model would use, so it can be swapped later without
touching the rest of the pipeline.

## Alternatives Considered
- **Single-feature threshold** (e.g., rainfall ratio alone): rejected
  — inspection showed no clean separation on any single available
  feature; a single threshold would misrepresent noisy, non-monotonic
  data as a clean decision boundary.
- **ML model despite failing to beat baseline**: rejected — presenting
  an unvalidated model as functioning intelligence, or silently keeping
  whichever configuration happened to score highest without regard to
  the baseline comparison, would be misleading regardless of how
  plausible the output looked.

## Consequences
v1's severity estimate is an explicit, disclosed heuristic — not a
validated predictive model — clearly stated in
`models/saved/model_card.md`. Every prediction is fully explainable:
the dashboard's Risk Assessment page shows the exact contribution of
each of the three components, which is a stronger and more honest form
of "explainability" than a SHAP plot on top of a model that doesn't
outperform guessing. The system's interfaces and orchestrator (see the
interfaces/orchestrator refactor) mean a properly validated ML model
could replace this predictor later, given a larger, multi-year,
multi-district dataset — without requiring changes anywhere else in the
pipeline.