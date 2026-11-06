#!/usr/bin/env python3
"""Generate wholly fictional test records. Never uses or reads respondent microdata."""
from pathlib import Path
import numpy as np, pandas as pd
DOMAINS=['affordability','access','reliability','efficiency','acceptability','quality','quantity','customer_service']
ROOT=Path(__file__).resolve().parents[1]
def build(seed=20261105,n=120):
    rng=np.random.default_rng(seed)
    a=rng.integers(0,11,size=(n,8))
    a[:12,:]=rng.integers(2,9,size=(12,1))
    z=rng.normal(size=(n,8))
    d={'household_id':[f'SYNTHETIC_{i:04d}' for i in range(n)], 'household_size':rng.integers(1,9,size=n)}
    for j,domain in enumerate(DOMAINS):d[f'priority_{domain}']=a[:,j]
    for j,domain in enumerate(DOMAINS):d[f'deficit_{domain}']=np.round(z[:,j],6)
    return pd.DataFrame(d)
def main():
    out=ROOT/'data/synthetic/SYNTHETIC_example_households.csv'
    out.parent.mkdir(parents=True,exist_ok=True)
    build().to_csv(out,index=False)
    print('Generated deterministic SYNTHETIC-only data:',out)
if __name__=='__main__':main()
