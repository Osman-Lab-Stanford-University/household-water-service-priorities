"""Statistical reference functions for household water-service priority analysis."""
from __future__ import annotations
import numpy as np
import pandas as pd
from scipy.optimize import minimize
from scipy.special import logsumexp, expit
from scipy.stats import chi2
from scipy.stats import multivariate_normal
from scipy.optimize import linear_sum_assignment
from sklearn.mixture import GaussianMixture
from sklearn.model_selection import train_test_split
import statsmodels.api as sm

DOMAINS=['affordability','access','reliability','efficiency','acceptability','quality','quantity','customer_service']
PRIORITY_QIDS=['Q2.9','Q3.9','Q4.5','Q5.4','Q6.6','Q7.5','Q8.6','Q9.5']
DEFICIT_QIDS=['Q2.2','Q3.1','Q13.1','Q5.1','Q6.2-Q6.4','Q7.1','Q8.1+Q8.3','Q9.2+Q9.3']

def helmert_basis(n=8):
    """n x (n-1) orthonormal contrasts (columns sum to zero)."""
    H=np.zeros((n,n-1))
    for j in range(1,n):
        H[:j,j-1]=1/np.sqrt(j*(j+1))
        H[j,j-1]=-j/np.sqrt(j*(j+1))
    return H

def score_priorities(df):
    cols=[f'priority_{x}' for x in DOMAINS]
    absent = [c for c in cols if c not in df]
    if absent:
        raise ValueError(f'Missing priority columns: {absent}')
    a=df[cols].apply(pd.to_numeric,errors='coerce').to_numpy(dtype=float)
    if a.ndim != 2 or a.shape[0] == 0:
        raise ValueError('Priority input must contain at least one household')
    if not np.isfinite(a).all():
        bad = [(cols[j], int(i)) for i,j in np.argwhere(~np.isfinite(a))[:8]]
        raise ValueError(f'All eight priority items must be finite and nonmissing; invalid (column, row): {bad}')
    if ((a < 0) | (a > 10)).any():
        raise ValueError('Priority values must be within 0..10')
    if not np.all(a == np.round(a)):
        raise ValueError('Administered priority ratings must be integers from 0 to 10')
    centered=a-a.mean(axis=1,keepdims=True)
    basis=helmert_basis()
    h=centered@basis
    equal=np.ptp(a,axis=1)==0
    return {'raw':a,'centered':centered,'helmert':h,'equal':equal,'differentiating':~equal,'rating_sd':np.std(a,axis=1,ddof=0)}

def standardized_deficits(df, reference_means=None, reference_sds=None):
    cols=[f'deficit_{x}' for x in DOMAINS]
    raw=df[cols].to_numpy(float)
    if raw.ndim != 2 or raw.shape[0] == 0:
        raise ValueError('Empty deficit input')
    if np.isinf(raw).any():
        raise ValueError('Deficits must not contain infinite values')
    if reference_means is None: means=np.nanmean(raw,axis=0)
    else: means=np.asarray(reference_means,float)
    if reference_sds is None: sds=np.nanstd(raw,axis=0,ddof=0)
    else: sds=np.asarray(reference_sds,float)
    if means.shape != (len(DOMAINS),) or sds.shape != (len(DOMAINS),):
        raise ValueError('Deficit reference vectors must have eight elements')
    if not np.isfinite(means).all() or not np.isfinite(sds).all() or np.any(sds<=0):
        raise ValueError('Non-finite or zero-variance deficit reference')
    return (raw-means)/sds,means,sds

def fit_gmm_grid(X, random_state=1729, starts=20, kmax=5):
    """Fit Gaussian-mixture candidates and return information criteria.

    Uses `starts` initializations and 500 EM iterations per candidate. This
    grid does not apply the manuscript's staged numerical-selection gates.
    """
    rows=[]; fitted={}
    for cov in ('spherical','tied','full'):
        for k in range(1,kmax+1):
            g=GaussianMixture(n_components=k,covariance_type=cov,n_init=starts,
                              max_iter=500,random_state=random_state,reg_covar=1e-6)
            g.fit(X)
            tag=f'{cov}_K{k}'; fitted[tag]=g
            rows.append({'model':tag,'bic':g.bic(X),'aic':g.aic(X),
                         'log_likelihood':g.score(X)*len(X),'converged':g.converged_,
                         'minimum_modal_share':np.bincount(g.predict(X),minlength=k).min()/len(X)})
    return pd.DataFrame(rows),fitted

def label_components_by_centroid_norm(g):
    order=np.argsort(np.linalg.norm(g.means_,axis=1))
    return order

def paired_heldout_density(X, covariance_type='full',k=2,seed=1729,repetitions=50,starts=10):
    """Evaluate repeated held-out log densities for one GMM specification.

    This function does not compare alternative distribution families.
    """
    rows=[]
    for j in range(repetitions):
        tr,te=train_test_split(np.arange(len(X)),test_size=.2,random_state=seed+j)
        g=GaussianMixture(n_components=k,covariance_type=covariance_type,n_init=starts,random_state=seed+j)
        g.fit(X[tr]); rows.append({'split':j,'heldout_mean_log_density':g.score(X[te]),'train_n':len(tr),'test_n':len(te)})
    return pd.DataFrame(rows)

def match_components(reference_centroids, candidate_centroids):
    cost=np.linalg.norm(reference_centroids[:,None,:]-candidate_centroids[None,:,:],axis=2)
    row,col=linear_sum_assignment(cost)
    return dict(zip(row.tolist(),col.tolist()))

def h2_stacked_fe(df, domain_specific=False):
    """Estimate household/domain fixed-effects OLS with household-clustered SEs.

    The common estimation cohort has complete priority and deficit responses in
    all eight domains. Deficit moments are computed on that cohort (ddof=0).
    `domain_specific=True` estimates a separate slope for each domain.
    """
    import statsmodels.formula.api as smf
    required = ['household_id'] + [f'priority_{d}' for d in DOMAINS] + [f'deficit_{d}' for d in DOMAINS]
    absent = [c for c in required if c not in df]
    if absent:
        raise ValueError(f'Missing H2 input columns: {absent}')
    if df.empty or df['household_id'].isna().any() or df['household_id'].duplicated().any():
        raise ValueError('household_id must be present and unique for every input row')
    # Validate administered ratings before selecting the joint estimation sample.
    score_priorities(df)
    deficit_cols = [f'deficit_{d}' for d in DOMAINS]
    try:
        raw = df[deficit_cols].to_numpy(dtype=float)
    except (ValueError, TypeError) as exc:
        raise ValueError('Deficit fields must contain numeric values') from exc
    if np.isinf(raw).any():
        raise ValueError('Deficits must not contain infinite values')
    complete = np.isfinite(raw).all(axis=1)
    eligible = df.loc[complete].copy()
    if len(eligible) < 3:
        raise ValueError('At least three service-complete households are required')
    standardized, mu, sd = standardized_deficits(eligible)
    ids = np.repeat(eligible['household_id'].astype(str).to_numpy(), len(DOMAINS))
    domains = np.tile(DOMAINS, len(eligible))
    ratings = eligible[[f'priority_{d}' for d in DOMAINS]].to_numpy(float).reshape(-1)
    deficits = standardized.reshape(-1)
    st = pd.DataFrame({'household_id': ids, 'domain': domains,
                       'priority': ratings, 'z_deficit': deficits})
    term = '0 + C(domain):z_deficit' if domain_specific else 'z_deficit'
    model = smf.ols(f'priority ~ C(household_id) + C(domain) + {term}', st).fit(
        cov_type='cluster', cov_kwds={'groups': st['household_id']})
    return st, model, {'means': mu.tolist(), 'sds': sd.tolist(),
                       'input_households': len(df), 'complete_households': len(eligible),
                       'excluded_incomplete_households': int((~complete).sum())}


def h3a_logit(df,predictor_cols):
    y=(~score_priorities(df)['equal']).astype(int)
    X=sm.add_constant(df[predictor_cols].astype(float),has_constant='add')
    return sm.GLM(y,X,family=sm.families.Binomial()).fit(cov_type='HC3')


def gaussian_component_logdensities(model, X, component_order=None):
    """Public-API Gaussian log densities, WITHOUT mixing weights.

    Component columns are returned in the supplied A/B order; never infer original
    scientific labels from sklearn's arbitrary component indices.
    """
    X=np.asarray(X,dtype=float)
    if X.ndim != 2 or X.shape[0] == 0 or not np.isfinite(X).all():
        raise ValueError('X must be a nonempty, finite 2-D array')
    if not hasattr(model, 'means_') or X.shape[1] != model.means_.shape[1]:
        raise ValueError('Fitted model/dimension mismatch')
    k=model.n_components
    if component_order is None: component_order=list(range(k))
    if sorted(component_order) != list(range(k)):
        raise ValueError('component_order must be a permutation of fitted indices')
    vals=[]
    for i in component_order:
        if model.covariance_type=='full': cov=model.covariances_[i]
        elif model.covariance_type=='tied': cov=model.covariances_
        elif model.covariance_type=='diag': cov=np.diag(model.covariances_[i])
        elif model.covariance_type=='spherical': cov=np.eye(X.shape[1])*model.covariances_[i]
        else: raise ValueError('Unsupported covariance family')
        vals.append(multivariate_normal.logpdf(X,mean=model.means_[i],cov=cov,allow_singular=False))
    return np.column_stack(vals)


def h3b_fixed_measurement(X, component_logdensities, start=None):
    """Fit a two-component concomitant likelihood with fixed component densities.

    Log-density columns must be ordered A then B. Returns coefficients and a
    convergence flag; inferential standard errors and bootstrap tests are not
    computed by this function.
    """
    X=np.asarray(X,dtype=float); L=np.asarray(component_logdensities,dtype=float)
    if X.ndim != 2 or len(X)==0 or not np.isfinite(X).all():
        raise ValueError('Predictors must be a nonempty finite 2-D matrix')
    if L.shape != (len(X),2) or not np.isfinite(L).all():
        raise ValueError('Frozen H1 log densities must be finite n x 2 (A,B)')
    XX=np.column_stack([np.ones(len(X)),X])
    initial=np.zeros(XX.shape[1]) if start is None else np.asarray(start,dtype=float)
    if initial.shape != (XX.shape[1],) or not np.isfinite(initial).all():
        raise ValueError('Invalid finite starting vector')
    def objective(beta):
        z=XX@beta
        return -np.sum(logsumexp(np.column_stack([-np.logaddexp(0,z)+L[:,0], -np.logaddexp(0,-z)+L[:,1]]),axis=1))
    def gradient(beta):
        z=XX@beta
        posterior=expit(z+L[:,1]-L[:,0])
        return XX.T@(expit(z)-posterior)
    res=minimize(objective,initial,jac=gradient,method='BFGS',options={'gtol':1e-6,'maxiter':1000})
    if not res.success and np.isfinite(res.fun) and np.isfinite(res.x).all():
        # Retry with a bounded-memory optimizer when BFGS does not converge.
        candidate=minimize(objective,res.x,jac=gradient,method='L-BFGS-B',
                           options={'maxiter':2000,'ftol':1e-12})
        if candidate.success and np.isfinite(candidate.fun):
            res=candidate
    if not np.isfinite(res.x).all() or not np.isfinite(res.fun):
        raise RuntimeError('H3B optimization produced nonfinite outputs')
    z=XX@res.x
    posterior=expit(z+L[:,1]-L[:,0])
    if not np.isfinite(posterior).all():
        raise RuntimeError('H3B posterior is nonfinite')
    return {'coef':res.x,'success':bool(res.success),'message':str(res.message),'nll':float(res.fun),'posterior_B':posterior}


def _valid_p(p):
    arr=np.asarray(p,dtype=float)
    if arr.ndim != 1 or len(arr)==0 or not np.isfinite(arr).all() or np.any((arr<0)|(arr>1)):
        raise ValueError('p-values must be a nonempty vector of finite values in [0,1]')
    return arr


def holm(p):
    p=_valid_p(p);order=np.argsort(p);out=np.empty(len(p))
    out[order]=np.maximum.accumulate(np.minimum(1,(len(p)-np.arange(len(p)))*p[order]))
    return out


def bh_fdr(p):
    p=_valid_p(p);order=np.argsort(p)
    tmp=np.minimum.accumulate((p[order]*len(p)/np.arange(1,len(p)+1))[::-1])[::-1]
    out=np.empty(len(p));out[order]=np.minimum(1,tmp)
    return out


def wald_chisq(beta,cov,idx):
    b=np.asarray(beta,dtype=float);V=np.asarray(cov,dtype=float)
    idx=np.asarray(idx,dtype=int)
    if b.ndim!=1 or V.shape!=(len(b),len(b)) or len(idx)==0 or len(set(idx))!=len(idx) or np.any(idx<0) or np.any(idx>=len(b)):
        raise ValueError('Invalid Wald coefficient/covariance/index dimensions')
    b=b[idx];V=V[np.ix_(idx,idx)]
    if not np.isfinite(b).all() or not np.isfinite(V).all() or not np.allclose(V,V.T,atol=1e-10):
        raise ValueError('Wald inputs must be finite with symmetric covariance')
    eig=np.linalg.eigvalsh(V)
    if eig.min()<=1e-12*max(1.,eig.max()):
        raise ValueError('Wald covariance is singular or not positive definite')
    w=float(b@np.linalg.solve(V,b))
    return {'chi2':w,'df':len(idx),'p':float(chi2.sf(w,len(idx)))}
