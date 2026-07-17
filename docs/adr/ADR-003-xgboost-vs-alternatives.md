# ADR-003: XGBoost as the Evaluated ML Candidate (Random Forest / LightGBM)

## Status
Accepted (as the ML candidate tested — see ADR-008 for the final
production decision, which did not end up using any ML model)

## Context
Flood severity prediction from tabular features (rainfall, landslide
count, population) needed a machine learning approach to evaluate
against a majority-class baseline. Several tabular-data model families
were candidates.

## Decision
Use XGBoost as the primary ML model to build, tune, and evaluate.

## Alternatives Considered
- **Random Forest**: simpler, less prone to overfitting on very small
  datasets in theory, but generally weaker than gradient boosting on
  structured tabular data at moderate sample sizes; kept as a mental
  benchmark rather than separately implemented, given time constraints
  and the small dataset size (n=13) making a full multi-model
  comparison less informative than it would be on a larger dataset.
- **LightGBM**: comparable performance to XGBoost in general, but adds
  a second boosting library dependency for no clear benefit at this
  dataset size; would only have been worth including as a deliberate
  benchmarking exercise, which was deprioritized in favor of spending
  the time on honest evaluation methodology (LOOCV, baseline
  comparison) instead.
- **Logistic Regression**: implemented and tested directly (see
  ADR-007) as a simpler alternative once XGBoost's LOOCV results
  underperformed baseline.

## Consequences
XGBoost's scikit-learn-compatible API and built-in SHAP support made
it fast to integrate into the evaluation pipeline. Ultimately, XGBoost
(in both 4-class and binary form) did not outperform a majority-class
baseline at n=13 samples (see ADR-006, ADR-007), which directly
motivated the pivot to a transparent composite score for production
(ADR-008). This ADR documents the model selection reasoning that led
to that evaluation, not a claim that XGBoost was the final production
choice.