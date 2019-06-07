import pandas as pd


def move_column(df, move, after=None, before=None):
    """Move a specific column to another position.

    Args:
        df (DataFrame): The self.
        move (str or [str]): Column(s) to move.
        after (str, optional): Move to after which column. Defaults to the last column.
        before (str, optional): Move to before which column. Override after if provided. Defaults to none.

    Returns:
        DataFrame: The modified DataFrame. No side-effect.
    """
    if isinstance(move, str):
        move = [move]
    c = [x for x in list(df.columns) if (x not in move)]
    if before is None:
        after = after or c[-1]
        i = c.index(after) + 1
        c[i:i] = move
        return df[c]
    else:
        i = c.index(before)
        c[i:i] = move
        return df[c]
