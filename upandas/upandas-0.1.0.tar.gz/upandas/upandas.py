import pandas as pd
import numpy as np
import uncertainties
from uncertainties import ufloat, nominal_value, std_dev
from uncertainties.unumpy import uarray, nominal_values, std_devs

def separate_to_useries(ser):
    rows = ser.index
    u_rows = rows[rows.str.match('^u_')]
    n_rows= u_rows.str.lstrip('u_')
    other_rows = rows.drop(n_rows).drop(u_rows)
    uncerts_series = pd.Series(
        {n: ufloat(ser[n], ser[u]) for n, u in zip(n_rows, u_rows)} )
    others_series = ser.loc[other_rows]
    new_series = pd.concat([uncerts_series, others_series])
    return new_series

def separate_to_udataframe(df):
    cols  = df.columns
    u_cols = cols[cols.str.match('^u_')]
    n_cols = u_cols.str.lstrip('u_')
    other_cols = cols.drop(n_cols).drop(u_cols)
    uncerts_frame  = pd.DataFrame(
        {n: uarray(df.loc[:, n], df.loc[:, u]) for n, u in zip(n_cols, u_cols)} )
    others_frame = df.loc[:, other_cols]
    new_frame = pd.concat([uncerts_frame, others_frame], axis=1)
    return new_frame
        
def separate_to_u(df):
    dtype = type(df)
    if dtype == pd.core.series.Series:
        return separate_to_useries(df)
    elif dtype == pd.core.frame.DataFrame: 
        return separate_to_udataframe(df)
    else:
        raise TypeError("Don't know how to deal with a {:s}".format(dtype))

def useries_to_separate(useries):
    rows = useries.index
    uf_rows = rows[ [isinstance(ex, uncertainties.core.UFloat) for ex in useries]  ]
    other_rows = rows.drop(uf_rows)
    uncert_series = pd.Series()
    for uf in uf_rows:
        uncert_series[uf]           =  useries[uf].nominal_value
        uncert_series[ 'u_'+uf] = useries[uf].std_dev
        others_series = useries.loc[other_rows]
        new_series = pd.concat([uncert_series, others_series])
    return new_series

def udataframe_to_separate(udf):
    cols  = udf.columns
    first = udf.iloc[0]
    uf_cols = cols [ [isinstance(ex, uncertainties.core.UFloat) for ex in first] ]
    other_cols = cols.drop(uf_cols)
    uncerts_frame  = pd.DataFrame()
    for uf in uf_cols:
        uarr = udf[uf].values
        uncerts_frame[uf] = nominal_values(uarr)
        uncerts_frame['u_'+uf] = std_devs(uarr)
    others_frame = udf.loc[:, other_cols]
    new_frame = pd.concat([uncerts_frame, others_frame], axis=1)
    return new_frame
    

"""Given a dataframe with uarray columns, yields a 'separate uncerts' dataframe
    with columns x and u_x for each uarray column x"""
def u_to_separate(udf):
    dtype = type(udf)
    if type(udf) == pd.core.series.Series:
        return useries_to_separate(udf)
    elif type(udf) == pd.core.frame.DataFrame:
        return udataframe_to_separate(udf)
    else:
        raise TypeError("Don't know how to deal with a {:s}".format(dtype))
    
if __name__ == "__main__":
    df = pd.DataFrame({
        'x':  [1.3,4.7], 'u_x': [0.3,0.4], 
        'y': [0.9,-0.8], 'u_y':[0.03,0.02],
        'a': [0.01, -0.01],
        'b' :[4.5,-2.01]})
    ser = df.iloc[0]
    
