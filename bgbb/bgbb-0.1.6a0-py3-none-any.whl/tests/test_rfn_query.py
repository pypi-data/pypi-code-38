import datetime as dt
import pandas as pd
from pandas.compat import lrange
from pandas import DataFrame

from bgbb.sql.sql_utils import run_rec_freq_spk, rec_freq_spk2pandas, to_s3_fmt
from pytest import fixture


MODEL_START_DATE = dt.date(2018, 6, 1)
MAX_OPPORTUNITIES = 9
DURATION = 10


def int2date(i):
    return MODEL_START_DATE + dt.timedelta(days=i - 1)


rfn_cols = ["Recency", "Frequency", "N"]


@fixture
def clients_daily_df():
    """
    Testing model window of 10 day.
    Day 0: day before model start date
    Day 1: first day of model range
    Day 10: last day of model range
    Day 11: first day *after* model range ('holdout start date')
    """
    #
    client_dates_i = [
        ("Beginning_end", [1, 3, 10]),
        ("Beginning_end_extra", [0, 1, 3, 10, 11]),
        (
            "Before_beginning",
            [0],
        ),  # Not included, since this is before model range
        ("Halfway_start", [5, 6, 11]),
        ("Every_day", lrange(11)),
        ("One_time_returner", [3, 4]),
        ("No_returns", [3]),
    ]

    client_dates = [
        (client_name, [int2date(i) for i in ints])
        for client_name, ints in client_dates_i
    ]

    clients_daily_df = DataFrame(
        [
            (client_name, to_s3_fmt(date))
            for client_name, dates in client_dates
            for date in dates
        ],
        columns=["client_id", "submission_date_s3"],
    )

    clients_daily_df = clients_daily_df.assign(
        app_name="Firefox",
        channel="release",
        sample_id="1",
        os="Linux",
        country="IN",
        fake_dim="fake_value",
    )

    return clients_daily_df


@fixture
def rfn_spk(clients_daily_df, spark):
    clients_daily_dfs = spark.createDataFrame(clients_daily_df)

    clients_daily_dfs.createOrReplaceTempView("clients_daily")
    rfn_dfs, _q = run_rec_freq_spk(
        spark,
        ho_win=1,
        model_win=10,
        sample_ids=[1],
        ho_start="2018-06-11",
        first_dims=["os", "country", "fake_dim"],
    )
    return rfn_dfs


@fixture
def rfn(rfn_spk):
    rfn = (
        rfn_spk.toPandas()
        .set_index("client_id")
        .assign(
            Max_day=lambda x: pd.to_datetime(x.Max_day).dt.date,
            Min_day=lambda x: pd.to_datetime(x.Min_day).dt.date,
        )
    )
    return rfn


def test_user_active_before_range_not_in_rfn(rfn):
    assert "Before_beginning" not in rfn.index
    assert "Beginning_end" in rfn.index
    # User activity outside of range shouldn't make a difference
    # to RFN data
    assert (
        rfn.loc["Beginning_end", rfn_cols]
        == rfn.loc["Beginning_end_extra", rfn_cols]
    ).all()


def test_every_day_user(rfn):
    """A user who shows up every day in a 10-day
    window should have a value of 9 for each value
    of R/F/N.
    """
    assert (rfn.loc["Every_day", rfn_cols] == MAX_OPPORTUNITIES).all()
    assert rfn.loc["Halfway_start"].N < MAX_OPPORTUNITIES


def test_date_range(rfn, clients_daily_df):
    "Dates in rfn don't extend to max/min dates in clients_daily"
    clients_daily_dates = pd.to_datetime(
        clients_daily_df.submission_date_s3
    ).dt.date

    assert clients_daily_dates.min() == int2date(0)
    assert rfn.Min_day.min() == int2date(1)

    assert clients_daily_dates.max() == int2date(11)
    assert rfn.Max_day.max() == int2date(10)


def test_rfn_invariants(rfn, duration=None):
    """
    Assert invariants based on definitions of R/F/N.
    """
    assert MAX_OPPORTUNITIES == DURATION - 1
    assert rfn.eval("Recency <= N").all()
    assert rfn.eval("Recency >= Frequency").all()
    assert (
        rfn.Frequency.eq(0) == rfn.Recency.eq(0)
    ).all(), "For those who never return, Frequency == Recency == 0"

    max_dur = (
        rfn.eval("Max_day - Min_day").astype("timedelta64[D]").astype(int).max()
    )
    assert max_dur == MAX_OPPORTUNITIES


def test_rec_freq_spk2pandas(rfn_spk):
    return rec_freq_spk2pandas(rfn_spk)


def test_rfn_cols(rfn):
    """
    final columns should include `first_dims`:
    os, country, and fake_dim.
    """
    scols = set(rfn.columns)
    expected_cols = set(
        [
            "sample_id",
            "Recency",
            "Frequency",
            "N",
            "Max_day",
            "Min_day",
            "os",
            "country",
            "fake_dim",
        ]
    )
    assert scols == expected_cols
