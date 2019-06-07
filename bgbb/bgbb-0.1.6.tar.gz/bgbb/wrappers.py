import inspect
from collections import OrderedDict
from functools import wraps
from typing import List

from lifetimes import BetaGeoBetaBinomFitter
import numpy as np

from bgbb.bgbb_utils import unload, as_array


abgd_names = "alpha beta gamma delta".split()


def frt(f):
    """Wraps lifetimes model methods that potentially
    take 'frequency', 'recency', 'T' as params,
    replace the func w/ one that takes a dataframe
    with these arguments as column names.
    """
    frt_params = {"frequency", "recency", "T", "n", "n_custs"}
    sig = inspect.signature(f)
    params = list(sig.parameters)

    @wraps(f)
    def wrapper(self, data, **k):
        k.update({p: data[p] for p in params if p in frt_params})
        return f(self, **k)

    return wrapper


def to_abgd_od(params):
    # type: (Union["OrderedDict[str, float]", List[float]]) -> OrderedDict[str, float]
    if isinstance(params, OrderedDict):
        return params
    return OrderedDict(zip(abgd_names, params))


def model_parameter_list(params, mod):
    return params or list(mod.params_.values())


class Rfn:
    """
    Wrapper for the BetaGeoBetaBinomFitter model. Instead of having to
    pass each of the r/f/n data and the a/b/g/d parameters, the corresponding
    wrapper functions here try to extract these columns from the model's
    attached dataframe, assuming it has columns "frequency", "recency", and "n".
    """

    def __init__(self, mod):
        self.mod = mod

    def cond_prob_alive(self, df, params: List[float] = None, n_days_later=0, nb=True):
        params = model_parameter_list(params, self.mod)
        frequency, recency, n = unload(df, "frequency recency n")
        kw = dict(
            frequency=frequency,
            recency=recency,
            n=n,
            params=params,
            n_days_later=n_days_later,
        )
        if nb:
            return self.mod.cond_prob_alive_nb(**kw)
        return self.mod.cond_prob_alive(**kw)

    @wraps(BetaGeoBetaBinomFitter.fit)
    def fit(self, df, **kw):
        frequency, recency, n = unload(df, "frequency recency n")
        if "n_custs" in df:
            n_custs = df["n_custs"]
        else:
            print("Warning: no n_custs column")
            n_custs = np.ones_like(frequency)
        return self.mod.fit(frequency, recency, n, n_custs, **kw)

    @wraps(BetaGeoBetaBinomFitter._loglikelihood)
    def _loglikelihood(self, df, params=None, parallel=True):
        x, tx, T = unload(df, "frequency recency n")
        params = model_parameter_list(params, self.mod)
        return self.mod._loglikelihood(params, x, tx, T, parallel=parallel)

    @wraps(BetaGeoBetaBinomFitter.conditional_expected_number_of_purchases_up_to_time)
    def cond_exp_rets_till(self, df, n_days_later, params=None, nb=False):
        x, tx, n = unload(df, "frequency recency n")
        params = model_parameter_list(params, self.mod)
        kw = dict(t=n_days_later, frequency=x, recency=tx, n=n, params=params)
        if nb:
            return self.mod.cond_exp_rets_till_nb(**kw)
        return self.mod.cond_exp_rets_till(**kw)

    def p_x_interval(self, n_star, x_star, ret_log=False, params=None, df=None):
        if df is None:
            df = self.mod.data
        x, tx, n = unload(df, "frequency recency n")
        params = model_parameter_list(params, self.mod)
        return self.mod.p_x_interval(
            params, f=x, r=tx, n=n, n_star=n_star, x_star=x_star, ret_log=ret_log
        )
