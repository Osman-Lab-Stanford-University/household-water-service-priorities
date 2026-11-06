import sys
from pathlib import Path
import numpy as np
import pandas as pd
import pytest
sys.path.insert(0, str(Path(__file__).resolve().parents[1]/'code'))
from priority_core import DOMAINS, h2_stacked_fe, score_priorities, h3b_fixed_measurement


def _households(n=14):
    rng=np.random.default_rng(223)
    d={'household_id':[f'H{i}' for i in range(n)]}
    for j,domain in enumerate(DOMAINS):
        d[f'priority_{domain}']=rng.integers(0,11,size=n)
        d[f'deficit_{domain}']=rng.normal(loc=j,scale=1.1,size=n)
    return pd.DataFrame(d)


def test_h2_reference_cohort_excludes_incomplete_before_standardizing():
    df=_households()
    baseline_st,baseline_fit,baseline=h2_stacked_fe(df)
    extra=_households(1).iloc[0].copy()
    extra['household_id']='EXCLUDED'
    extra['deficit_affordability']=1e8
    extra['deficit_reliability']=np.nan
    extended=pd.concat([df,pd.DataFrame([extra])],ignore_index=True)
    st,fit,info=h2_stacked_fe(extended)
    assert info['excluded_incomplete_households']==1
    assert info['complete_households']==len(df)
    assert np.allclose(info['means'],baseline['means'])
    assert np.allclose(info['sds'],baseline['sds'])
    assert np.allclose(st['z_deficit'],baseline_st['z_deficit'])
    assert np.isclose(fit.params['z_deficit'],baseline_fit.params['z_deficit'])


def test_h2_standardized_means_zero_on_estimation_cohort():
    st,fit,info=h2_stacked_fe(_households())
    assert len(st)==14*8
    assert np.allclose(st.groupby('domain')['z_deficit'].mean().to_numpy(),0,atol=1e-12)
    assert np.isfinite(fit.params['z_deficit'])
    assert np.isfinite(fit.bse['z_deficit'])


def test_h2_reject_duplicate_household_ids():
    df=_households();df.loc[1,'household_id']=df.loc[0,'household_id']
    with pytest.raises(ValueError,match='unique'): h2_stacked_fe(df)


def test_h2_reject_invalid_priority_instead_of_silently_fitting():
    df=_households();df['priority_reliability']=df['priority_reliability'].astype(float);df.loc[0,'priority_reliability']=2.5
    with pytest.raises(ValueError,match='integers'): h2_stacked_fe(df)


def test_h3b_exposes_convergence_status():
    rng=np.random.default_rng(10)
    X=rng.normal(size=(80,2)); L=rng.normal(size=(80,2))
    fit=h3b_fixed_measurement(X,L)
    assert isinstance(fit['success'],bool)
    assert 'message' in fit
    assert np.isfinite(fit['nll'])


def test_h3b_nonconverged_result_is_explicit(monkeypatch):
    import priority_core
    class FailedResult:
        success=False
        fun=11.0
        x=np.array([0.0,0.0])
        message='Optimization limit reached'
    monkeypatch.setattr(priority_core, 'minimize', lambda *args, **kwargs: FailedResult())
    fit=priority_core.h3b_fixed_measurement(np.ones((8,1)), np.zeros((8,2)))
    assert fit['success'] is False
    assert 'Optimization limit reached' in fit['message']
