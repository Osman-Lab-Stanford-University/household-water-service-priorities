#!/usr/bin/env python3
"""Command-line utilities for priority measurements and synthetic demonstrations."""
import argparse,json,sys
from pathlib import Path
import numpy as np,pandas as pd
sys.path.insert(0,str(Path(__file__).resolve().parent))
from priority_core import *
ROOT=Path(__file__).resolve().parents[1]
def demo(out):
    df=pd.read_csv(ROOT/'data/synthetic/SYNTHETIC_example_households.csv')
    if not df['household_id'].astype(str).str.startswith('SYNTHETIC_').all():
        raise ValueError('Demo input must contain only explicitly synthetic IDs')
    sc=score_priorities(df)
    zg,means,sds=standardized_deficits(df)
    diff=sc['helmert'][sc['differentiating']]
    grid,models=fit_gmm_grid(diff,starts=4,kmax=3)
    out.mkdir(parents=True,exist_ok=True)
    grid.to_csv(out/'synthetic_gmm_discovery.csv',index=False)
    pd.DataFrame({'domain':DOMAINS,'synthetic_deficit_mean':means,'synthetic_deficit_sd':sds}).to_csv(out/'synthetic_domain_reference.csv',index=False)
    # Evaluate the likelihood with fitted synthetic component densities
    g=models['full_K2']; ids=np.flatnonzero(sc['differentiating']); selected=df.iloc[ids]
    logdens=gaussian_component_logdensities(g,diff,component_order=[0,1])
    res=h3b_fixed_measurement(np.asarray(selected[['household_size']].astype(float)),logdens)
    diag={'data_type':'SYNTHETIC ONLY','synthetic_households':len(df), 'synthetic_differentiators':len(diff),
          'centered_max_abs_sum':float(np.max(np.abs(sc['centered'].sum(axis=1)))),
          'helmert_reconstruction_max_error':float(np.max(np.abs((sc['helmert']@helmert_basis().T)-sc['centered']))),
          'h3b_synthetic_demo_success':res['success'],'h3b_synthetic_demo_message':res['message']}
    (out/'synthetic_diagnostics.json').write_text(json.dumps(diag,indent=2))
    print(json.dumps(diag,indent=2))
def inspect(path,out):
    df=pd.read_csv(path); need=['household_id']+[f'priority_{x}' for x in DOMAINS]
    absent=[x for x in need if x not in df]
    if absent:raise ValueError(f'Missing core columns: {absent}')
    if df.household_id.isna().any() or df.household_id.duplicated().any():raise ValueError('Missing or duplicate household_id in input')
    sc=score_priorities(df)
    info={'analysis_mode':'input_inspection','input_rows':len(df),'equal_rating_rows':int(sc['equal'].sum()),'differentiating_rows':int(sc['differentiating'].sum()),
          'contains_deficits':all(f'deficit_{x}' in df for x in DOMAINS)}
    out.mkdir(parents=True,exist_ok=True)
    (out/'input_screening.json').write_text(json.dumps(info,indent=2));print(json.dumps(info,indent=2))
if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('command',choices=['demo','inspect']);parser.add_argument('--input',type=Path);parser.add_argument('--out',type=Path,default=ROOT/'outputs');a=parser.parse_args()
    if a.command=='demo':demo(a.out)
    elif not a.input:parser.error('--input is required for inspect')
    else:inspect(a.input,a.out)
