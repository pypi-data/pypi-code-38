import numpy as np
from bgbb import BGBB
from bgbb.sql.bgbb_udfs import (
    add_mau,
    add_p_th,
    mk_n_returns_udf,
    mk_p_alive_udf,
    mk_p_th_exp_udf,
)
from bgbb.wrappers import to_abgd_od
from lifetimes.datasets import load_donations
from lifetimes.fitters.beta_geo_beta_binom_fitter import BetaGeoBetaBinomFitter
from pandas import DataFrame
from pytest import fixture

df = fixture(load_donations)


@fixture
def dfs(df, spark):
    return spark.createDataFrame(df)


@fixture
def params():
    return [1.20, 0.75, 0.66, 2.78]


@fixture
def bgbb(params):
    return BGBB(params=params)


@fixture
def ref_model(params, df):
    reference_model = BetaGeoBetaBinomFitter()
    reference_model.data = df
    reference_model.params_ = to_abgd_od([1.20, 0.75, 0.66, 2.78])
    return reference_model


@fixture
def p_alive(bgbb, params):
    return mk_p_alive_udf(bgbb, params=params, alive_n_days_later=0)


@fixture
def n_returns(bgbb, params):
    return mk_n_returns_udf(bgbb, params=params, return_in_next_n_days=14)


@fixture
def p_th_est_udfs(bgbb, params):
    return mk_p_th_exp_udf(bgbb, params=params)


def test_p_alive(dfs, p_alive, ref_model):
    pa_ref = ref_model.conditional_probability_alive(0)

    df2 = dfs.withColumn(
        "P_alive", p_alive(dfs.frequency, dfs.recency, dfs.n)
    ).toPandas()

    assert np.allclose(df2.P_alive, pa_ref)


def test_n_returns(dfs, n_returns, ref_model):
    p14_ref = ref_model.conditional_expected_number_of_purchases_up_to_time(14)

    df2 = dfs.withColumn("P14", n_returns(dfs.frequency, dfs.recency, dfs.n)).toPandas()

    assert np.allclose(df2.P14, p14_ref)


def test_p_th_est_udf(dfs, p_th_est_udfs):
    """Just test structure and support of this function, since lifetimes
    doesn't have this function.
    """
    p_th_est, _, _ = p_th_est_udfs
    df = dfs.withColumn("p_th", p_th_est(dfs.frequency, dfs.recency, dfs.n)).toPandas()
    p_th_srs = df["p_th"]
    p, th = zip(*p_th_srs)
    p_th_df = DataFrame(dict(p=p, th=th))
    assert p_th_df.eval(
        "0 <= p <= 1 & 0 <= th <= 1"
    ).all(), "This function returns probabilities"


def test_add_p_th(dfs, bgbb, params):
    """
    Check that, given same # opportunities to return,
    higher frequency yields higher estimates of p.
    Also check that columns are as expected, and estimated
    probabilities are between [0, 1].
    """
    p_th_df = add_p_th(
        bgbb, dfs=dfs, params=params, fcol="frequency", rcol="Recency", ncol="N"
    ).toPandas()
    max_opp = p_th_df.n.min()  # noqa: F841
    mean_p_freq = (
        p_th_df.query("n == @max_opp & frequency > 0").groupby("frequency").p.mean()
    )
    # Looks something like:
    # frequency
    # 1    0.383420
    # 2    0.510549
    # 3    0.619845
    # 4    ...
    assert (
        mean_p_freq.is_monotonic_increasing
    ), "As frequency increases, p should as well"
    assert set(p_th_df) == {"frequency", "recency", "n", "n_custs", "p", "th"}
    assert p_th_df.eval(
        "0 <= p <= 1 & 0 <= th <= 1"
    ).all(), "This function returns probabilities"

    none_params = add_p_th(
        bgbb, dfs=dfs, params=None, fcol="frequency", rcol="Recency", ncol="N"
    ).toPandas()
    return none_params


def test_add_mau(dfs, bgbb, params):
    """
    Check that, given same # opportunities to return,
    higher frequency yields higher estimates of p.
    Also check that columns are as expected, and estimated
    probabilities are between [0, 1].
    """
    p_mau = add_mau(
        bgbb,
        dfs=dfs,
        params=params,
        fcol="frequency",
        rcol="Recency",
        ncol="N",
        n_days_future=28,
    ).toPandas()
    print(p_mau)
    max_opp = p_mau.n.min()  # noqa: F841
    mean_p_freq = (
        p_mau.query("n == @max_opp & frequency > 0")
        .groupby("frequency")
        .prob_mau.mean()
    )
    # Looks something like:
    # frequency
    # 1    0.383420
    # 2    0.510549
    # 3    0.619845
    # 4    ...
    assert (
        mean_p_freq.is_monotonic_increasing
    ), "As frequency increases, prob_mau should as well"
    assert set(p_mau) == {"frequency", "recency", "n", "n_custs", "prob_mau"}
    assert p_mau.eval("0 <= prob_mau <= 1").all(), "This function returns probabilities"

    none_params = add_p_th(
        bgbb, dfs=dfs, params=None, fcol="frequency", rcol="Recency", ncol="N"
    ).toPandas()
    assert len(
        none_params
    ), "Make sure API works by testing in the case of no params explicitly passed"
    return none_params
