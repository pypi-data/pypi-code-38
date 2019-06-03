import numpy as np
import scipy.stats as st
from lifetimes.datasets import load_donations
from pytest import fixture

from bgbb.bgbb_utils import gen_buy_die, AbgdParams
from bgbb.core import BGBB
from bgbb.wrappers import unload

df = fixture(load_donations)
bg = fixture(lambda: BGBB(params=[1.20, 0.75, 0.66, 2.78]))
bgdat = fixture(lambda: BGBB(params=[1.20, 0.75, 0.66, 2.78], data=load_donations()))
pars = fixture(lambda: [1.20, 0.75, 0.66, 2.78])


def check_prob(p):
    # Round for weird floating point issues
    p = p.round(10)
    return all(p >= 0) and all(p <= 1)


def test_len(df):
    assert len(df) == 22


def test_cond_prob_alive_nb(df, bg, pars):
    nbres = bg.rfn.cond_prob_alive(df, params=pars, nb=True)
    res = bg.rfn.cond_prob_alive(df, params=pars, nb=False)
    assert np.allclose(nbres, res)


def test_cond_prob_exp_rets(df, bg, pars):
    x, tx, n = unload(df, "frequency recency n")
    bg.data = df
    n14_orig = bg.conditional_expected_number_of_purchases_up_to_time(14)
    n14_nb = bg.cond_exp_rets_till_nb(14, x, tx, n, params=pars)
    n14_api = bg.rfn.cond_exp_rets_till(df, n_days_later=14)
    n14_api_nb = bg.rfn.cond_exp_rets_till(df, n_days_later=14, nb=True)
    assert np.allclose(n14_orig, n14_nb)
    assert np.allclose(n14_orig, n14_api)
    assert np.allclose(n14_orig, n14_api_nb)


def gen_samps_exp(bg, abgd, n_opps, n_users, seed=0):
    # Get median p, th from hyper params
    a, b, g, d = abgd
    actual_p = np.median(st.beta(a, b).rvs(100))
    actual_th = np.median(st.beta(g, d).rvs(100))

    pp, th = np.full(n_users, actual_p), np.full(n_users, actual_th)
    df = gen_buy_die(n_opps, n_users, abgd=abgd, p_th=[pp, th], seed=seed)
    p_est, th_est = bg._expec_p_th(*abgd, df.frequency, df.recency, df.n_opps)
    df = df.assign(P_est=p_est, Th_est=th_est)
    return actual_p, actual_th, p_est, th_est, df


def sim_expec_p_th_diffs(bg, abgd=[70.0, 30.0, 25.0, 75.0], seed=0):
    """
    Hacky test to make sure we can recover
    params p and θ from data generated by them. Hopefully, the median
    estimated params from BGBB._expec_p_th (p_est, th_est) aren't far off
    from the actual params (p_actual, th_actual) used to generate them.
    """
    p_actual, th_actual, p_est, th_est, sim_dat = gen_samps_exp(
        bg, abgd, n_opps=90, n_users=10000, seed=seed
    )
    p_diff = np.median(p_est) - p_actual
    assert abs(p_diff) < 0.03
    th_diff = np.median(th_est) - th_actual
    assert abs(th_diff) < 0.03
    return p_diff, th_diff


def test_expec_p_th(bg):
    sim_expec_p_th_diffs(bg, abgd=[25.0, 75.0, 70.0, 30.0], seed=0)
    sim_expec_p_th_diffs(bg, abgd=[70.0, 30.0, 25.0, 75.0], seed=0)


def test_p_interval(bgdat):
    p0n1 = bgdat.rfn.p_x_interval(n_star=1, x_star=0)
    p0n2 = bgdat.rfn.p_x_interval(n_star=2, x_star=0)

    assert check_prob(p0n1)
    assert check_prob(p0n2)

    p_any_n1 = 1 - p0n1
    p_any_n2 = 1 - p0n2
    assert (p_any_n2 > p_any_n1).all()


def test_p_interval_close_p_alive(bgdat, df):
    """
    The threshold for this test is somewhat arbitrary,
    but should check that P(ever return in a long interval)
    is a close approximation of P(alive).
    """

    p_alive = bgdat.rfn.cond_prob_alive(df)

    p_never_return = bgdat.rfn.p_x_interval(n_star=100, x_star=0)
    p_ever_return = 1 - p_never_return

    assert check_prob(p_alive)
    assert check_prob(p_never_return)
    assert check_prob(p_ever_return)

    assert np.corrcoef(p_alive, p_ever_return)[0, 1] > .99

    # Test case for x_star != 0
    p_return_once = bgdat.rfn.p_x_interval(n_star=100, x_star=1)
    assert check_prob(p_return_once)


def test_latent_variable_mean(bg):
    abgd = [25.0, 75.0, 70.0, 30.0]
    p_actual, th_actual, p_est, th_est, df = gen_samps_exp(
        bg, abgd, n_opps=90, n_users=10000, seed=0
    )
    bg2 = BGBB(params=abgd)
    p_est2, th_est2 = bg2.latent_variable_mean(df.frequency, df.recency, df.n_opps)
    assert np.allclose(p_est, p_est2)
    assert np.allclose(th_est, th_est2)


def beta_exp(a, b):
    """
    Expected value of beta distro
    https://en.wikipedia.org/wiki/Beta_distribution
    """
    return a / (a + b)


def test_gen_buy_die():
    """
    Somewhat circular way of testing the data generating process.
    Checks that params used to generate data with `gen_buy_die`
    can be reasonably recovered with fitter. Also checks that p, θ
    generated by `gen_probs` have mean close to what we'd expect.
    """
    a, b, g, d = abgd = [7, 3, 2, 8]
    n_opps = 90
    n_users = 10000
    df = gen_buy_die(n_opps, n_users, abgd=abgd, p_th=None, seed=0)

    # Check that mean generated p, θ values aren't far from expected
    assert abs((beta_exp(a, b) - df["p"].mean())) < 0.01
    assert abs((beta_exp(g, d) - df["th"].mean())) < 0.01

    rfn_df = (
        df.rename(columns={"n_opps": "n"})
        .groupby(["frequency", "recency", "n"])
        .size()
        .reset_index(drop=0)
        .rename(columns={0: "weights"})
    )

    bg = BGBB(penalizer_coef=0.0).rfn.fit(rfn_df.rename(columns={"weights": "n_custs"}))
    recovered_params = np.array(list(bg.params_.values()))
    assert (recovered_params.round() == abgd).all()


def test_AbgdParams():
    """
    Test repr, __init__, mod_param, from_dct functionality
    of AbgdParams.
    """
    pars = AbgdParams(7, 3, 2, 8)
    assert repr(pars) == "BGBB Hyperparams <α: 7.0, β: 3.0, γ: 2.0, δ: 8.0>"

    pars2 = pars.mod_param(a=lambda x: x + 1, d=lambda x: x / 2)
    assert pars.d == pars2.d * 2
    assert pars.a == pars2.a - 1

    assert AbgdParams.from_dct(pars._asdict()) == pars
