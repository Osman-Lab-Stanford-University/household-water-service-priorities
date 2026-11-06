"""Independent mathematical checks of the H2 and H3B reference methods."""
import sys
from pathlib import Path
import numpy as np
import pandas as pd
from scipy.optimize._numdiff import approx_derivative
from scipy.special import expit, logsumexp

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'code'))
from priority_core import DOMAINS, h2_stacked_fe


def test_h2_pooled_slope_matches_within_transformed_least_squares():
    rng = np.random.default_rng(316)
    n = 24
    values = {'household_id': [f'H{i:03d}' for i in range(n)]}
    for j, domain in enumerate(DOMAINS):
        values[f'priority_{domain}'] = rng.integers(0, 11, n)
        values[f'deficit_{domain}'] = rng.normal(loc=j, size=n)
    stacked, model, _ = h2_stacked_fe(pd.DataFrame(values))
    z = stacked['z_deficit'].to_numpy().reshape(n, 8)
    y = stacked['priority'].to_numpy().reshape(n, 8)
    z_within = z - z.mean(axis=0)[None, :] - z.mean(axis=1)[:, None] + z.mean()
    y_within = y - y.mean(axis=0)[None, :] - y.mean(axis=1)[:, None] + y.mean()
    independent_slope = np.sum(z_within * y_within) / np.sum(z_within ** 2)
    assert np.isclose(model.params['z_deficit'], independent_slope, atol=1e-12)


def test_h3b_two_component_analytic_gradient_matches_finite_differences():
    rng = np.random.default_rng(317)
    X = rng.normal(size=(50, 3))
    densities = rng.normal(size=(50, 2))
    design = np.column_stack([np.ones(len(X)), X])
    beta = np.array([0.4, -0.2, 0.7, -0.5])

    def objective(b):
        logits = design @ b
        log_a = -np.logaddexp(0, logits) + densities[:, 0]
        log_b = -np.logaddexp(0, -logits) + densities[:, 1]
        return -np.sum(logsumexp(np.column_stack([log_a, log_b]), axis=1))

    logits = design @ beta
    analytic = design.T @ (expit(logits) - expit(logits + densities[:, 1] - densities[:, 0]))
    numerical = approx_derivative(lambda b: np.array([objective(b)]), beta).ravel()
    assert np.allclose(analytic, numerical, rtol=1e-7, atol=1e-7)
