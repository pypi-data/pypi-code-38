from .query import query
import pandas_light as pdt


def query_staff():
    """Return the staff info table.

    Returns:
        pd.DataFrame: Return as DataFrame.
    """
    sql = 'select * from view_teacher_info'
    return query(sql)


def vmap_staff(df, on='pyccode', identifier=None, take='sname'):
    """vmap some staff info into a DataFrame.
    
    Args:
        df (pd.DataFrame): The self.
        on (str, optional): The key column in df. Defaults to 'pyccode'.
        identifier(str, optional): The identifier of 'on' column. e.g. pyccode/sname. Defaults to on.
        take (str or [str], optional): [pyccode/sname/ename/cname]. Defaults to 'sname'.
    
    Returns:
        pd.DataFrame: Return as DataFrame. No side-effect.
    """
    s = query_staff()
    identifier = identifier or on
    return pdt.vmap(df, s, on=on, right_on=identifier, take=take)
