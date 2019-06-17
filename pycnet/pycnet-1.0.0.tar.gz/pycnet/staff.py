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
