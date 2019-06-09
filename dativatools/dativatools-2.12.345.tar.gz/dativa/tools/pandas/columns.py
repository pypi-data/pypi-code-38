# (c) 2012-2018 Dativa, all rights reserved
# -----------------------------------------
#  This code is licensed under MIT license (see license.txt for details)

"""
A set of functions to improve dataframe column handling in pandas
"""


def get_column_name(df, column, total_columns=None):
    """
    gets the name of a column from either an integer or a passed name.
    Allows the total columns to be overwritten for cases where additional columns
    are added to the dataframe.
    """
    if total_columns is None:
        total_columns = df.shape[1]

    if column in df.columns:
        return column

    try:
        column_index = int(column)
        if column_index < 0:
            column_index = column_index + total_columns
        return df.columns.values.tolist()[column_index]
    except (ValueError, TypeError):  # we should be testing this?
        try:
            from dativa.file_processing import FpInvalidSourceFieldError  # noqa
            raise FpInvalidSourceFieldError(column)
        except ImportError:  # so let's qa it
            raise KeyError('Invalid column name: {}'.format(column))


def get_unique_column_name(df, name, suffix='_clean'):
    """
    Gets a unique name for a new column
    """
    
    if name not in df.columns:
        return name
    else:
        return get_unique_column_name(df, str(name) + suffix)
