import pandas as pd
import numpy as np

#functions to write:

#graph missing data percentages in columns

#future:
# clean columns
def graph_missing_data(df):
    '''
    Function takes in a df and graphs the missing data per column
    as a percentage. It doens't show columns with no missing data.

    INPUT:
        - DF
    OUTPUT:
        - DF of the percentage per column.
    '''
    missing_data = {}
    for i in df.columns[1:]:
        if df[i].isnull().sum() > 0:
            missing_percent = round((df[i].isnull().sum()/df.shape[0])*100,1)
            #print (f'{missing_percent}% of column {i} is null.')
            missing_data[i]=missing_percent
    missing_percentages = pd.DataFrame.from_dict(missing_data, orient='index')
    return missing_percentages
