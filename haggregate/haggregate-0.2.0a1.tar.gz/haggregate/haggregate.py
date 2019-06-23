import numpy as np
import pandas as pd
from htimeseries import HTimeseries

methods = {
    "sum": pd.Series.sum,
    "mean": pd.Series.mean,
    "max": pd.Series.max,
    "min": pd.Series.min,
}


class AggregateError(Exception):
    pass


def aggregate(hts, target_step, method, min_count=1, missing_flag="MISS"):
    result = HTimeseries()

    # Set metadata of result
    result = HTimeseries()
    attrs = (
        "unit",
        "time_zone",
        "time_step",
        "interval_type",
        "variable",
        "precision",
        "location",
    )
    for attr in attrs:
        setattr(result, attr, getattr(hts, attr, None))
    result.timestamp_rounding = 0
    result.timestamp_offset = 0
    if hasattr(hts, "title"):
        result.title = "Aggregated " + hts.title
    if hasattr(hts, "comment"):
        result.comment = (
            "Created by aggregating the time series that had this comment:\n\n"
            + hts.comment
        )

    # Reindex the source so that it has no missing records but has NaNs instead,
    # starting from one before and ending in one after
    current_range = hts.data.index
    try:
        freq = pd.tseries.frequencies.to_offset(pd.infer_freq(current_range))
        if freq is None:
            raise AggregateError(
                "Can't infer time series step; maybe it's not regularized"
            )
    except ValueError:
        # Can't infer frequency - insufficient number of records
        return result
    first_timestamp = (current_range[0] - pd.Timedelta("1S")).floor(target_step)
    end_timestamp = current_range[-1].ceil(target_step)
    new_range = pd.date_range(first_timestamp, end_timestamp, freq=freq)
    source_data = hts.data.reindex(new_range)

    # Do the resampling
    resampler = source_data["value"].resample(
        target_step, closed="right", label="right"
    )
    result_values = resampler.agg(methods[method])

    # Convert to NaN when there aren't enough source records
    values_count = resampler.count()
    result_values[values_count < min_count] = np.nan
    result.data["value"] = result_values

    # Set the missing flag wherever the source has a missing value and the target has
    # a value
    max_count = int(pd.Timedelta(target_step) / freq)
    result.data["flags"] = (values_count < max_count).apply(
        lambda x: missing_flag if x else ""
    )

    # Remove leading and trailing NaN values from the result
    while pd.isnull(result.data["value"]).iloc[0]:
        result.data = result.data.drop(result.data.index[0])
    while pd.isnull(result.data["value"]).iloc[-1]:
        result.data = result.data.drop(result.data.index[-1])

    return result
