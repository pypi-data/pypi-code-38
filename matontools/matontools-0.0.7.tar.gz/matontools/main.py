import pandas as pd
import numpy as np

#functions to write:

#graph missing data percentages in columns

#future:
# clean columns
import pickle
def unpickle_df(file_name):
    '''Unpickle a file'''
    with open(file_name, 'rb') as pickleFile:
        df = pickle.load(pickleFile)
    return df

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

import numpy as np
import scipy.stats


def mean_confidence_interval(data, confidence=0.95):
    '''
    Returns the mean of data with a lower and upper value based
    on the confidence level.

    INPUTS:
        - Data: typically list or array of values
        - Confidence level: defaults to .95, value between 0 and 1
    OUTPUTS:
        - Lower bound, mean, upper bound based on confidence level

    '''
    a = 1.0 * np.array(data) #unclear what this does, maybe converts ints to floats?
    n = len(a)
    m, se = np.mean(a), scipy.stats.sem(a) #stderror = std/sqrt(n)
    h = se * scipy.stats.t.ppf((1 + confidence) / 2., n-1) #gets the delta from the mean
    return m-h, m, m+h


def std_from_sample_mean(mean, n):
    return np.sqrt((mean*(1-mean))/n)
