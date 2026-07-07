# ADR-008: Composite Risk Score Instead of ML or Single-Threshold Rule (n=13)

## Status
Accepted

## Context
LOOCV evaluation of XGBoost (4-class, binary) and Logistic Regression,
benchmarked against majority-class baselines, showed no model reliably
beating baseline at n=13. Additionally, inspecting rainfall_pct_of_normal
against real 2018 severity labels showed no monotonic relationship —
the highest-ratio district (Idukki) was not the most severe, and the
lowest-severity district (Kollam) had a high ratio. This suggests real
flood severity in this event was driven by factors beyond rainfall ratio
alone (e.g., terrain, dam discharge) that aren't present in this dataset.

## Decision
Use a transparent, weighted composite score (rainfall ratio + landslide
count + rainfall deviation) as the v1 severity estimator, with explicitly
documented, non-fitted weights — rather than force either an ML model or
a single-feature threshold that would misrepresent 13 noisy points as a
learned boundary.

## Alternatives Considered
- Single-feature threshold: rejected — inspection showed no clean
  separation on any single available feature.
- ML model: rejected — see ADR benchmarking above; none beat baseline.

## Consequences
v1's severity estimate is an explicit heuristic, not a validated
predictive model — clearly disclosed in the model card. The system
remains structured (same interface, same pipeline) so a properly
validated ML model can replace this the moment a larger, multi-year,
multi-district dataset with terrain/drainage features becomes available.