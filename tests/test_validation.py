import sys
from pathlib import Path
import numpy as np
import pandas as pd
import pytest
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'code'))
from priority_core import (DOMAINS,score_priorities,holm,bh_fdr,wald_chisq,
    h3b_fixed_measurement,gaussian_component_logdensities)
from sklearn.mixture import GaussianMixture

def make_df(v=3):
    return pd.DataFrame({f'priority_{d}':[v] for d in DOMAINS})

def test_non_integer_priority_rejected():
    x=make_df();x['priority_reliability']=2.5
    with pytest.raises(ValueError,match='integers'): score_priorities(x)

@pytest.mark.parametrize('v',[-1,11,np.nan,np.inf])
def test_out_of_range_nonfinite_priority_rejected(v):
    x=make_df();x['priority_reliability']=v
    with pytest.raises(ValueError): score_priorities(x)

@pytest.mark.parametrize('p',[[1.2,-.1],[.1,float('nan')],[]])
def test_bad_pvalues_rejected(p):
    with pytest.raises(ValueError): holm(p)
    with pytest.raises(ValueError): bh_fdr(p)

def test_singular_wald_rejected():
    with pytest.raises(ValueError,match='singular'):
        wald_chisq([1.],[ [0.] ],[0])

def test_h3b_bad_inputs_rejected():
    X=np.ones((10,2)); L=np.zeros((10,2));L[0,0]=np.nan
    with pytest.raises(ValueError,match='finite'):
        h3b_fixed_measurement(X,L)
    L=np.zeros((10,2));X[0,0]=np.nan
    with pytest.raises(ValueError,match='finite'):
        h3b_fixed_measurement(X,L)

def test_public_api_density_equals_sklearn_loglikelihood():
    rng=np.random.default_rng(88); X=rng.normal(size=(120,3))
    g=GaussianMixture(n_components=2,random_state=11,n_init=3).fit(X)
    L=gaussian_component_logdensities(g,X)
    from scipy.special import logsumexp
    assert L.shape==(120,2)
    assert np.allclose(logsumexp(L+np.log(g.weights_)[None,:],axis=1),g.score_samples(X),atol=1e-9)
