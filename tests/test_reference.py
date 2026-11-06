import sys
from pathlib import Path
import numpy as np,pandas as pd
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'code'))
from priority_core import *
def test_helmert():
    h=helmert_basis();assert h.shape==(8,7);assert np.allclose(h.T@h,np.eye(7));assert np.allclose(h.sum(axis=0),0)
def test_scores_and_origin():
    df=pd.DataFrame({f'priority_{d}':[3,idx+1] for idx,d in enumerate(DOMAINS)})
    r=score_priorities(df); assert r['equal'].tolist()==[True,False];assert np.allclose(r['helmert'][0],0)
    assert np.allclose(r['helmert']@helmert_basis().T,r['centered'])
def test_adjustments():
    a=holm([.03,.01,.02]);assert np.allclose(a,[.04,.03,.04]);assert np.all(bh_fdr([.01,.04,.1])>=0)
def test_frozen_measurement_likelihood():
    rng=np.random.default_rng(4);X=rng.normal(size=(60,2)); L=rng.normal(size=(60,2))
    z=h3b_fixed_measurement(X,L);assert np.isfinite(z['nll']);assert np.all((z['posterior_B']>=0)&(z['posterior_B']<=1))
