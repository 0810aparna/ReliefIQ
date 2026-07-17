# ADR-007: Binary Severity Classification Attempted (and Also Rejected)

## Status
Rejected — documented for the record, not implemented in production

## Context
The 4-class severity prediction (Low/Medium/High/Critical) evaluated
via LOOCV (ADR-006) did not beat its majority-class baseline (0.38 vs
0.46). Since the Decision Engine only ever needs a binary answer in
practice ("trigger the optimizer or not"), collapsing to a binary
target (Severe = High/Critical, Not Severe = Low/Medium) was tested as
a way to give the model a more learnable problem.

## Decision
Test binary classification with both XGBoost and Logistic Regression,
using the same LOOCV methodology, benchmarked against the binary
majority-class baseline.

## Alternatives Considered
- Keep 4-class only and accept the below-baseline result: rejected as
  a first step — binary collapse was a reasonable, cheap thing to try
  before abandoning ML entirely.
- Try further feature engineering before testing binary collapse:
  considered, but the binary test was faster to run and more directly
  diagnostic of whether the problem was granularity (too many classes)
  or genuinely insufficient signal in the available features.

## Consequences
Binary XGBoost (full features) scored 0.31 against a 0.62 baseline —
worse than the 4-class attempt, relatively speaking. Binary XGBoost
with a trimmed feature set and binary Logistic Regression both reached
0.54 — closer, but still below the 0.62 baseline. Since three different
modeling approaches (4-class XGBoost, binary XGBoost, binary Logistic
Regression) all failed to beat their respective baselines, this ruled
out "wrong model" or "wrong granularity" as the explanation and pointed
to insufficient signal in the available features relative to the
dataset size — directly motivating ADR-008's decision to abandon ML for
v1 in favor of a transparent composite score.