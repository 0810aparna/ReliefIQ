# Model Card — xgb_v1

## Training Data
13 Kerala districts, single 2018 flood season (district_wise_details.csv),
enriched with historical Kerala monsoon rainfall averages (rainfall_india.csv,
1901-2015) and population-scaled infrastructure estimates.

## Evaluation Method
Leave-One-Out Cross-Validation (LOOCV) — chosen because n=13 is too small
for a conventional train/test split to give a meaningful held-out sample;
LOOCV uses every district as a test case exactly once, giving 13 honest
out-of-fold predictions instead of one lucky/unlucky split.

## Metrics
- LOOCV Accuracy: <fill in>
- LOOCV Weighted F1: <fill in>

## Known Limitations
- Single flood season — model has not seen inter-year variation in real
  district-level conditions, only cross-district variation within one event.
- Small sample size (n=13) limits statistical confidence in any single metric.
- Infrastructure features remain synthetic (disclosed in DATA_SOURCES.md).

## Features Used
actual_rainfall_in_mm, normal_rainfall_in_mm, no_of_landslides, population,
rainfall_deviation_from_normal, rainfall_pct_of_normal, hospitals_per_100k