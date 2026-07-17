# ADR-006: Leave-One-Out Cross-Validation for a Small Dataset (n=13)

## Status
Accepted

## Context
The real 2018 Kerala flood dataset has 13 usable district records (one
per district, one flood season). A conventional train/test split (e.g.,
80/20) would leave roughly 2-3 districts for testing — too few to
produce a statistically meaningful accuracy estimate, and highly
sensitive to which specific districts happened to land in the test set.

## Decision
Use Leave-One-Out Cross-Validation (LOOCV): train on 12 districts, test
on the 1 held-out district, repeated 13 times so every district serves
as the test case exactly once. Report the aggregate out-of-fold
accuracy across all 13 folds.

## Alternatives Considered
- **Single train/test split**: rejected — too few test samples to
  trust the resulting accuracy number, and results would vary
  substantially depending on the random split chosen.
- **k-fold cross-validation (k=5)**: viable, but at n=13 each fold
  would only hold out 2-3 samples per fold while still not using every
  single sample as its own held-out test case; LOOCV is the natural
  limit of k-fold as k approaches n, and is the standard, defensible
  choice specifically for very small datasets.

## Consequences
LOOCV produced an honest accuracy of 0.38 (4-class), which was directly
compared against a majority-class baseline of 0.46 — revealing that the
initial XGBoost model was actually underperforming the simplest
possible baseline, a finding that a single lucky train/test split could
easily have masked. This honest result is what motivated the further
investigation documented in ADR-007 and the eventual pivot in ADR-008.