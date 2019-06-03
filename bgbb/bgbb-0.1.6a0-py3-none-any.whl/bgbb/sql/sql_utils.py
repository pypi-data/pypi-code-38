import datetime as dt
from typing import List, Union

import pandas as pd
from pandas.compat import lmap


S3_DAY_FMT = "%Y%m%d"
S3_DAY_FMT_DASH = "%Y-%m-%d"


def to_s3_fmt(date):
    return date.strftime(S3_DAY_FMT)


def to_samp_ids(samp_ids: Union[List[int], int]) -> str:
    """
    iter of ints to SQL string version for main_summary
    >>> to_samp_ids([0, 1, 2])
    "'0', '1', '2'"
    """
    if not isinstance(samp_ids, (list, range)):
        samp_ids = [samp_ids]
    samp_ids_i = lmap(int, samp_ids)  # type: List[int]
    invalid_sample = set(samp_ids_i) - set(range(100))
    if invalid_sample:
        raise ValueError(
            "{} is outside of the valid range [0, 99]".format(invalid_sample)
        )
    return to_sql_list(map(str, samp_ids_i))


def to_sql_list(xs):
    """stringify lists for SQL queries
    >>> to_sql_list([1, 2, 3]) == '1, 2, 3'
    """

    def to_sql_literal(x):
        if isinstance(x, str):
            return "'{}'".format(x)
        return str(x)

    res = ", ".join(map(to_sql_literal, xs))
    return res


def first_dim_select(dims: List[str], indent=8):
    joiner = "\n{indent}, ".format(indent=" " * indent)
    return "".join(
        "{joiner}first({col}) as {col}".format(joiner=joiner, col=col)
        for col in dims
    )


def insert_country(
    q, insert_before="{sample_comment}", countries: List[str] = ["GB"]
):
    "Insert country restriction into SQL string for testing"
    i = q.find(insert_before)
    to_insert = "AND country IN ({})\n      ".format(to_sql_list(countries))
    return q[:i] + to_insert + q[i:]


def mk_time_params(ho_win=14, model_win=90, ho_start="2018-08-01"):
    """
    Return container whose attributes are holdout and model input
    date ranges, specified by a training window `model_win`,
    holdout evaluation window `ho_win` and holdout start date `ho_start`
    (day after last day in model window).
    """

    def r():
        pass

    r.ho_start_datet = pd.to_datetime(ho_start)
    r.ho_start_date = r.ho_start_datet.date()
    r.ho_last_date = r.ho_start_date + dt.timedelta(days=ho_win - 1)
    r.model_start_date = r.ho_start_date - dt.timedelta(days=model_win)

    # Str format
    mod_ho_ev = [r.model_start_date, r.ho_start_date, r.ho_last_date]
    # mod_ho_ev_str
    (r.model_start_date_str, r.ho_start_date_str, r.ho_last_date_str) = map(
        to_s3_fmt, mod_ho_ev
    )

    # r.__dict__.update(locals())
    return r


base_query = """
with cid_day as (
    SELECT
        C.client_id
        , C.sample_id
        , C.submission_date_s3
        , from_unixtime(unix_timestamp(C.submission_date_s3, 'yyyyMMdd'),
                        'yyyy-MM-dd') AS sub_date
        {first_dims}
    FROM clients_daily C
    WHERE
        app_name = 'Firefox'
        AND channel = 'release'
      {sample_comment}  AND sample_id in ({sample_ids})
)

-- clients_daily aggregates from window *before*
-- the holdout date
, cid_model as (
    SELECT
        C.client_id
        , C.sample_id
        , MIN(C.sub_date) AS Min_day
        , MAX(C.sub_date) AS Max_day
        , COUNT(*) AS X{select_first_dims}
    FROM cid_day C
    WHERE
        C.submission_date_s3 >= '{model_start_date_str}'
        AND C.submission_date_s3 < '{ho_start_date_str}'
    GROUP BY 1, 2
)

, cid_holdout as (
    SELECT
        C.client_id
        , COUNT(*) AS N_holdout
    FROM cid_day C
    WHERE
      C.submission_date_s3 >= '{ho_start_date_str}'
      AND C.submission_date_s3 <= '{ho_last_date_str}'
    GROUP BY 1
)

, rec_freq as (
    SELECT
        C.client_id
        , C.sample_id
        , datediff(C.Max_day, Min_day) AS Recency
        , X - 1 AS Frequency
        -- N: # opportunities to return
        , datediff('{ho_start_date}', Min_day) - 1  AS N
        , C.Max_day
        , C.Min_day
        {first_dims}
    FROM cid_model C
)

, rec_freq_holdout as (
  SELECT R.*
        , coalesce(H.N_holdout, 0) AS N_holdout
  FROM rec_freq R
  LEFT JOIN cid_holdout H
    ON R.client_id = H.client_id
)

SELECT * FROM {qname}
"""


# TODO: test both holdout=True and False
def mk_rec_freq_q(
    q,
    holdout=False,
    model_start_date_str: str = None,
    pcd=None,
    sample_ids: List[int] = [1],
    first_dims: List[str] = [],
    **k
):
    """
    holdout: pull # of returns in holdout period?
    @first_dims: list of dimensions that should be relatively
    stable with clients, like `os`, `channel`, etc. The query
    will pull the first of these values for each client.
    """
    qname = "rec_freq_holdout" if holdout else "rec_freq"
    sample_ids_str = to_samp_ids(sample_ids)  # type: str
    first_dims_alias = first_dim_select(first_dims, indent=8)
    first_dims_agg = "".join(", " + dim for dim in first_dims)

    kw = dict(
        model_start_date_str=model_start_date_str,
        sample_ids=sample_ids_str,
        sample_comment="" if sample_ids else "--",
        qname=qname,
        pcd=pcd,
        select_first_dims=first_dims_alias,
        first_dims=first_dims_agg,
    )
    kw.update(k)
    kw = {k: v for k, v in kw.items() if v is not None}
    return q.format(**kw)


def run_rec_freq_spk(
    spark,
    rfn_base_query=base_query,
    ho_win=14,
    model_win=90,
    holdout=False,
    sample_ids: List[int] = [],
    first_dims: List[str] = [],
    ho_start="2018-08-01",
    ho_days_in_future=None,
):
    """
    holdout: whether to pull # of returns in holdout period. Useful
        for evaluating model.
    ho_days_in_future: int?; if 1, set the first day in holdout period
        to be tomorrow. Negative numbers will set it to before today.
    """
    if ho_days_in_future is not None:
        ho_start = dt.date.today() + dt.timedelta(days=ho_days_in_future)
    r = mk_time_params(ho_win=ho_win, model_win=model_win, ho_start=ho_start)
    r.q = mk_rec_freq_q(
        q=rfn_base_query,
        holdout=holdout,
        # ignore_pcd=ignore_pcd,
        sample_ids=sample_ids,
        model_start_date_str=r.model_start_date_str,
        pcd=r.model_start_date,
        ho_start_date=r.ho_start_date,
        ho_last_date_str=r.ho_last_date_str,
        ho_start_date_str=r.ho_start_date_str,
        first_dims=first_dims,
    )
    dfs = spark.sql(r.q)
    return dfs, r.q


def reduce_rec_freq_spk(dfs, rfn_cols=["Recency", "Frequency", "N"]):
    """Reduce r/f/n spark dataframe to r/f/n pattern count.
    This can be used for fitting.
    """
    return dfs.groupby(rfn_cols).count().withColumnRenamed("count", "n_users")


def rec_freq_spk2pandas(df_spk):
    df = df_spk.toPandas()
    df = df.assign(
        Max_day=lambda x: pd.to_datetime(x.Max_day),
        Min_day=lambda x: pd.to_datetime(x.Min_day),
    )
    return df


def run_rec_freq(
    spark, ho_win=14, model_win=90, sample_ids=[1], ho_start="2018-08-01"
):
    df_spk, q = run_rec_freq_spk(
        spark,
        ho_win=ho_win,
        model_win=model_win,
        sample_ids=sample_ids,
        ho_start=ho_start,
    )
    df = rec_freq_spk2pandas(df_spk)
    return df, df_spk, q
