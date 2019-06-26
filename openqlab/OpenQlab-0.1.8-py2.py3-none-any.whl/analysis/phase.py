from pandas import Series
from numpy import sign


def accumulated_phase(df: Series, limit: float=340) -> None:
    """Scan a row of a :obj:`pandas.DataFrame` and calculate the absolute phase delay.

    Looks for a jump in the phase of at least :obj:`limit` and adds ±360° to remove the phase jump.

    Parameters
    ----------
    df : Series
        Row of a :obj:`pandas.DataFrame`.
    limit : float
        Minimum phase difference to detect a phase jump.

    Returns
    -------
    None
        The row is changed inplace, no need for a return value.

    """
    if len(df.shape) != 1:
        raise ValueError('The DataFrame should only contain one single column.')
    for i in range(1, len(df)):
        if abs(df.iloc[i-1] - df.iloc[i]) > limit:
            df.iloc[i:] += 360 * sign(df.iloc[i-1] - df.iloc[i])
