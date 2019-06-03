from collections import OrderedDict, namedtuple
from itertools import count
from typing import Dict, List, Optional, Sequence, Tuple, Union

import numpy as np
import numpy.random as nr
from numba import njit
import pandas as pd
from pandas import DataFrame

Prob = float


def as_array(s: Union[np.array, pd.Series]):
    try:
        return s.values
    except AttributeError:
        return s


def unload(dct: Dict, ks: Union[List[str], str]) -> List[float]:
    if isinstance(ks, str):
        ks = ks.split()
    return [dct[k] for k in ks]


###############
# Simulations #
###############
def gen_probs(abgd: List[float], n=10):
    pa, pb, ta, tb = abgd
    p = nr.beta(pa, pb, size=n)
    th = nr.beta(ta, tb, size=n)
    return p, th


def gen_buy_die(
    n_opps,
    n_users,
    abgd: List[float],
    p_th: Optional[Tuple[Sequence[Prob], Sequence[Prob]]] = None,
    n_opps_name="n_opps",
    seed=0,
):
    """
    Given `n_opps` window size of opportunity, simulate Buy 'Til You Die process
    for `n_users` users.
    If arrays for latent variables p_th = (p, theta) are not passed, then these
    are drawn from beta distribution.
    """
    nr.seed(seed)
    if p_th is None:
        p, th = gen_probs(abgd, n=n_users)
    else:
        p, th = p_th
    txs, xs = np.empty_like(p, dtype=np.int), np.empty_like(p, dtype=np.int)
    bern = lambda p: nr.binomial(1, p, size=n_opps)

    for i, pi, thi in zip(count(), p, th):
        buys, dies = bern(pi), bern(thi)
        xs[i], txs[i] = get_x_tx(buys, dies)

    ret = DataFrame(
        OrderedDict([("p", p), ("th", th), ("frequency", xs), ("recency", txs)])
    ).assign(**{n_opps_name: n_opps})
    return ret


@njit
def get_x_tx(buys, dies) -> Tuple[int, int]:
    """
    Converts simulated 'buy'/'die' events into frequency/recency
    counts.
    """
    x = 0
    tx = 0
    for opp, buy, die in zip(range(1, len(buys) + 1), buys, dies):
        if die:
            break
        if buy:
            x += 1
            tx = opp
    return x, tx


_AbgdParams = namedtuple("AbgdParams", ["a", "b", "g", "d"])


class AbgdParams(_AbgdParams):
    def mod_param(self, **par_fns):
        dct = self._asdict().copy()
        for par_letter, f in par_fns.items():
            dct[par_letter] = f(dct[par_letter])
        return self.from_dct(dct)

    @property
    def _greek_dct_unicode(self):
        dct = self._asdict().copy()
        for name, letter in zip(["α", "β", "γ", "δ"], "abgd"):
            dct[name] = dct.pop(letter)
        return dct

    @classmethod
    def from_dct(cls, dct):
        return cls(*[dct[k] for k in "abgd"])

    @classmethod
    def from_greek_dct(cls, dct):
        return cls(*[dct[k] for k in ("alpha", "beta", "gamma", "delta")])

    def __repr__(self):
        st_repr = ", ".join(
            "{}: {:.1f}".format(k, v) for k, v in self._greek_dct_unicode.items()
        )
        return "BGBB Hyperparams <{}>".format(st_repr)
