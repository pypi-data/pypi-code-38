#
# Copyright 2018 Shawn Lin
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import pandas as pd
from datetime import datetime, timedelta


# Return related statistics
def total_return(returns):
    """
    Compute total return from simple returns.

    Parameters
    ----------
    returns : pd.Series of periodic returns

    Returns
    -------
    total_returns : array-like
        Series of total returns.
    """
    if len(returns) < 1:
        return returns.copy()

    # Allocate Memory
    result = returns.copy()

    # Compute cumulative return
    result = result.add(1, fill_value=0)
    result = result.prod(skipna=True)
    result = result.add(-1)

    return result


def cum_return(returns):
    """
    Compute cumulative returns from simple returns.

    Parameters
    ----------
    returns : pd.Series of periodic returns

    Returns
    -------
    cumulative_returns : array-like
        Series of cumulative returns.
    """
    if len(returns) < 1:
        return returns.copy()

    # Allocate Memory
    result = returns.copy()

    # Compute cumulative return
    result = result.add(1, fill_value=0)
    result = result.cumprod(skipna=True)
    result = result.add(-1)

    return result


def vami(returns, starting_value=1000):
    """
    Compute VAMI (Value Added Monthly Index) from simple returns.

    Parameters
    ----------
    returns : pd.Series, np.ndarray, or pd.DataFrame
        Returns of the strategy as a percentage, noncumulative.
         - Time series with decimal returns.
         - Example::
            2015-07-16   -0.012143
            2015-07-17    0.045350
            2015-07-20    0.030957
            2015-07-21    0.004902
         - Also accepts two dimensional data. In this case, each column is
           cumulated.
    starting_value: float, optional
       The starting returns.

    Returns
    -------
    vami : array-like
        Series of cumulative returns.
    """
    result = cum_return(returns)
    result = result.add(1)
    result = result.multiply(starting_value)

    return result


def weekly_return(returns):
    """
    Compute weekly returns from higher frequency returns

    Parameters
    ----------
    returns : pd.Series of returns with periodicity shorter than a week

    Returns
    -------
    weekly_returns : array-like
        Series of weekly returns.
    """
    if len(returns) < 1:
        return returns.copy()

    # Allocate Memory
    result = returns.copy()

    # Compute cumulative return
    result = result.add(1, fill_value=0)
    result = result.groupby(pd.Grouper(freq="W")).prod()
    result = result - 1

    return result


def monthly_return(returns):
    """
    Compute monthly returns from higher frequency returns

    Parameters
    ----------
    returns : pd.Series of returns with periodicity shorter than a month

    Returns
    -------
    monthly_returns : array-like
        Series of monthly returns.
    """
    if len(returns) < 1:
        return returns.copy()

    # Allocate Memory
    result = returns.copy()

    # Compute cumulative return
    result = result.add(1, fill_value=0)
    result = result.groupby(pd.Grouper(freq="M")).prod()
    result = result - 1

    return result


def quarterly_return(returns):
    """
    Compute quarterly returns from higher frequency returns

    Parameters
    ----------
    returns : pd.Series of returns with periodicity shorter than a quarter

    Returns
    -------
    quarterly_returns : array-like
        Series of quarterly returns.
    """
    if len(returns) < 1:
        return returns.copy()

    # Allocate Memory
    result = returns.copy()

    # Compute cumulative return
    result = result.add(1, fill_value=0)
    result = result.groupby(pd.Grouper(freq="Q")).prod()
    result = result - 1

    return result


def annual_return(returns):
    """
    Compute annual returns from higher frequency returns

    Parameters
    ----------
    returns : pd.Series of returns with periodicity shorter than a year

    Returns
    -------
    annual_returns : array-like
        Series of annual returns.
    """
    if len(returns) < 1:
        return returns.copy()

    # Allocate Memory
    result = returns.copy()

    # Compute cumulative return
    result = result.add(1, fill_value=0)
    result = result.groupby(pd.Grouper(freq="A")).prod()
    result = result - 1

    return result


def period_return(returns, period):
    """
    Convert higher frequency returns

    Parameters
    ----------
    returns : pd.Series of returns with higher frequency than the target
      periodicity
    period : the target periodicity to convert the returns to, options are
        - week
        - month
        - quarter
        - year

    Returns
    -------
    monthly_returns : array-like
        Series of annual returns.
    """
    return_func = {
        "week": weekly_return,
        "month": monthly_return,
        "quarter": quarterly_return,
        "year": annual_return,
    }

    result = returns.copy()
    result = return_func[period](returns)

    return result


def annualized_return(returns, start_date=None, end_date=None):
    """
    Convert periodic returns into annualized return

    Parameters
    ----------
    returns : pd.Series of returns
    start_date end_date : string in %Y%m%d. Defaults to None. If given, use
    start or end as the start or end date of the series. This is useful for series
    that's already in a lower frequency (e.g. monthly returns) but the exact
    start or end dates are known. Providing start end in this case will generate
    more accurate annualized returns.

    Returns
    -------
    annualized_returns : array-like
        Series of annualized returns.
    """
    result = returns.copy()

    if start_date is None:
        start_date = returns.index[0]
    else:
        start_date = datetime.strptime(start_date, "%Y-%m-%d")
    if end_date is None:
        end_date = returns.index[-1]
    else:
        end_date = datetime.strptime(end_date, "%Y-%m-%d")

    diff_in_years = ((end_date - start_date).total_seconds() / timedelta(days=365.25).total_seconds())

    result = total_return(result)
    result = (result.add(1) ** (1 / diff_in_years)) - 1

    return result


# Risk related statistics
def annualized_std(returns, start_date=None, end_date=None):
    """
    Compute annualized standard deviation (volatility) from periodic returns

    Parameters
    ----------
    returns : pd.Series of returns
    start_date or end_date : string in %Y%m%d. Defaults to None. If given, use
    start or end as the start or end date of the series. This is useful for series
    that's already in a lower frequency (e.g. monthly returns) but the exact
    start or end dates are known. Providing start end in this case will generate
    more accurate annualized standard deviations.

    Returns
    -------
    annualized_returns : array-like
        Series of annualized returns.
    """
    result = returns.copy()

    if start_date is None:
        start_date = returns.index[0]
    else:
        start_date = datetime.strptime(start_date, "%Y-%m-%d")
    if end_date is None:
        end_date = returns.index[-1]
    else:
        end_date = datetime.strptime(end_date, "%Y-%m-%d")

    diff_in_years = ((end_date - start_date).total_seconds() / timedelta(days=365.25).total_seconds())

    result = result.std() * ((result.count() / diff_in_years) ** 0.5)

    return result
