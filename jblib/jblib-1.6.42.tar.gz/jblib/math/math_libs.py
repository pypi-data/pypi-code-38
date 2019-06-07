import pandas as pd
import numpy as np

def mean_deviation(data, mean=None):
    '''
    DESCRIPTION:
        This function takes a Pandas DataFrame column in and then returns a series of calculated mean deviations
        
    FUNCTION:
        mean_deviation(data)
        
    EXAMPLE:
        data["MeanDeviation"] = pd.Series(mean_deviation(data['column']), index=data.index)
    '''
    diff_values = list()
    if not mean:
        mean = data.mean()
        
    for i in range(0, len(data)):
        diff_value = abs(data[i] - mean)
        diff_values.append(diff_value)
        
    return diff_values

def standard_deviation(data, mean=None):
    '''
    DESCRIPTION:
        This function takes a Pandas DataFrame column in and then returns the calculated standard deviation
        
    FUNCTION:
        standard_deviation(data)
        
    EXAMPLE:
        standard_dev = standard_deviation(data['column'])
    '''
    diff_values = list()
    if not mean:
        mean = data.mean()
        
    for i in range(0, len(data)):
        diff_value = data[i] - mean
        diff_value = diff_value * diff_value
        diff_values.append(diff_value)
        
    standard_dev = np.array(diff_values).mean()
        
    return np.sqrt(standard_dev)