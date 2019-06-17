from .query import query
import pandas_light
import pandas_flavor as pf


def query_staff():
    """Return the staff info table.

    Returns:
        pd.DataFrame: Return as DataFrame.
    """
    sql = 'select * from view_teacher_info'
    return query(sql)


@pf.register_dataframe_method
def pycnet_vmap_staff(df, on='pyccode', identifier=None, take='sname'):
    """vmap some staff info into a DataFrame.

    Args:
        on (str, optional): The key column in df. Defaults to 'pyccode'.
        identifier(str, optional): The identifier of 'on' column. e.g. pyccode/sname. Defaults to on.
        take (str or [str], optional): [pyccode/sname/ename/cname]. Defaults to 'sname'.
    """
    identifier = identifier or on
    return df.vmap(query_staff(), on=on, right_on=identifier, take=take)


@pf.register_series_method
def pycnet_deep_staff(series, replace='pyccode', by='sname', delimiter=','):
    """Run a deep_replace_str on the Series, converting staff info.

    Args:
        replace (str, optional): Info to replace. Defaults to 'pyccode'.
        by (str, optional): Info to get. Defaults to 'sname'.
        delimiter (str, optional): The delimiter. Defaults to ','.
    """
    dct = query_staff().zipdict(replace, by)
    return series.deep_replace_str(delimiter, dct)
