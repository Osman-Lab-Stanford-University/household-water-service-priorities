# Reproduction guide

## Installation and tests

Use Python 3.11 or later. From the repository root:

```bash
python -m pip install -r config/requirements.txt
python -m pytest -q tests
```

## Synthetic demonstration

```bash
python code/generate_synthetic_demo.py
python code/driver.py demo --out outputs/demo
```

The demonstration generates synthetic household observations using a fixed random seed to illustrate rating transformations and statistical functions.

## Empirical analysis requirements

The manuscript's H1–H3 findings were calculated from the study's original analytical workflow. The public repository supplies reference functions and documentation, not the complete executable empirical workflow. Replicating the empirical estimates requires authorized access to the corresponding survey inputs, cohort-screening decisions, source-item coding, model configurations, random seeds, validation splits and recorded model outputs.

An authorized analysis should construct the eligible cohorts, calculate domain measurements, implement the study's H1 comparisons and H2/H3 specifications, and assess the reported sensitivities using the methods described in the manuscript and Supplementary Information. The included GMM and H3B helpers implement individual operations rather than every selection, inference and bootstrap step.

## Numerical comparison

Compare calculated values against the 13 manuscript reference targets using [`code/check_reported_results.py`](../code/check_reported_results.py). Input requirements and output statuses are documented in [`NUMERICAL_VERIFICATION.md`](NUMERICAL_VERIFICATION.md).

Do not add restricted survey records or identifiers to the public repository.
