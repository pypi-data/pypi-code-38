from .query import query
from .calendar import newest_schyear
import pandas_light as pdt


def query_student(schyear=None):
    """Return the student info table.

    Args:
        schyear (int, optional): Which schyear to retrieve. Defaults to all years.

    Returns:
        pd.DataFrame: Return as DataFrame.
    """
    if schyear is None:
        sql = 'select * from view_student_info'
    else:
        sql = f'select * from view_student_info where sch_year = {schyear}'
    return query(sql)


def vmap_student(df, pyccode='pyccode', take='cname'):
    """vmap some student info into a DataFrame. Key must be pyccode.

    Args:
        df (pd.DataFrame): The self.
        pyccode (str, optional): The column with pyccode. Defaults to 'pyccode'.
        take (str or [str], optional): [ename/cname/sex/cardnum]. Defaults to 'cname'.

    Returns:
        [type]: [description]
    """
    s = query('select distinct pyccode, ename, cname, sex, cardnum from view_student_info')
    return pdt.vmap(df, s, on=pyccode, right_on='pyccode', take=take)


def vmap_schooling(df, pyccode='pyccode', take=['cname', 'class', 'num'], schyear=None):
    """vmap some schooling info into a DataFrame. Key must be pyccode.

    Args:
        df (pd.DataFrame): The self.
        pyccode (str, optional): The column with pyccode. Defaults to 'pyccode'.
        take (str or [str], optional): [ename/cname/sex/cardnum/form/class/num]. Defaults to ['cname','class','num'].
        schyear (int, optional): The sch_year to look for. Defaults to newest_schyear.

    Returns:
        pd.DataFrame: Return as DataFrame. No side-effect.
    """
    schyear = schyear or newest_schyear()
    s = query_student(schyear)
    return pdt.vmap(df, s, on=pyccode, right_on='pyccode', take=take)
