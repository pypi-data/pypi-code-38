from .query import query
import pandas_light
import pandas_flavor as pf
import pandas as pd
from .calendar import now_datetime


def query_access_log(fromtime, totime=None):
    """Return the access_log info table.
    
    Args:
        fromtime (str): From what time, in format '2000-12-31 13:45:30' or '2000-12-31'.
        totime (str, optional): To what time, in format '2000-12-31 13:45:30' or '2000-12-31'. Defaults to Now.
    
    Returns:
        pd.DataFrame: Return as DataFrame.
    """
    if totime is None:
        totime = now_datetime()
    df = query(
        f'select From_unixtime(log_time) as time, location, cardnum, pyccode from attend_log left join usertbl using (cardnum) where log_time BETWEEN Unix_timestamp("{fromtime}") AND Unix_timestamp("{totime}")  ORDER BY log_time DESC')
    if df.empty:
        df = pd.DataFrame(columns=['time','location','cardnum','pyccode'])
    return df


@pf.register_dataframe_method
def pycnet_vmap_access_log(df, fromtime, totime=None, pyccode='pyccode', delimiter='\n'):
    """vmap some access_log info into a DataFrame. Key must be pyccode.
    
    Args:
        fromtime (str): From what time, in format '2000-12-31 13:45:30' or '2000-12-31'.
        totime (str, optional): To what time, in format '2000-12-31 13:45:30' or '2000-12-31'. Defaults to Now.
        pyccode (str, optional): The column with pyccode. Defaults to 'pyccode'.
        delimiter (str, optional): The delimiter to join multiple access log. Defaults to '\n'. If set to None, only the lastest log is returned.
    """
    a = query_access_log(fromtime, totime)
    if delimiter is None:
        a = a.groupby(['pyccode'])['time'].max().reset_index()
    else:
        a = a.groupby(['pyccode'])['time'].apply(lambda s: delimiter.join(s)).reset_index()
    return df.vmap(a, on=pyccode, right_on='pyccode', take='time')
