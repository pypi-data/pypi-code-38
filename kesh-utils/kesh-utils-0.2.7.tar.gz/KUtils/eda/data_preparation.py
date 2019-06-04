"""
from KUtils.eda import data_preparation as dp
"""

import numpy as np
import pandas as pd

from KUtils.eda import chartil

def plotUnique(df, optional_settings={}):
    unique_dict = {x: len(df[x].unique()) for x in df.columns}
    optional_settings.update({'x_label':'Features'}) 
    optional_settings.update({'y_label':'Unique values'})
    optional_settings.update({'chart_title':'Unique values in each Feature/Column'})

    if optional_settings.get('sort_by_value')==None:
        optional_settings.update({'sort_by_value':False})
        
    chartil.core_barchart_from_series(pd.Series(unique_dict), optional_settings) 
    
def plotNullInColumns(df, optional_settings={}):
    aSeries = df.isnull().sum() 
    if sum(aSeries>0):
        optional_settings.update({'exclude_zero_column':True})
        optional_settings.update({'x_label':'Features'}) 
        optional_settings.update({'y_label':'Missing Count'})
        optional_settings.update({'chart_title':'Count of missing values in each Feature/Column'})
        chartil.core_barchart_from_series(aSeries, optional_settings)
    else:
        print('Nothing to plot. All series value are 0')

def plotNullInRows(df, optional_settings={}):
    no_of_columns = df.shape[1]
    colNulls = df.isnull().sum(axis=1)
    colNulls = colNulls*100/no_of_columns
    df['nan_percentage']=colNulls
    
    # Todo: Try Range instead of hrdcoded value (Take care when Percentage is 0)
    df['nan_percentage_bin'] = pd.cut(df['nan_percentage'], 
              [-1, 0, 5, 10, 15, 20, 25, 30, 35, 40, 45, 50, 55, 60, 65, 70, 75, 80, 85, 90, 95, 100], 
              labels=['<0', '<=5%', '<=10%', '<=15', '<=20', '<=25', '<=30',
                      '<=35','<=40','<=45', '<=50', '<=55', '<=60', '<=65', '<=70', '<=75', '<=80','<=85', '<=90', '<=95', '<=100'])
    
    data_for_chart = df['nan_percentage_bin'].value_counts(dropna=False)  
    data_for_chart = data_for_chart.loc[data_for_chart.index!='<0'] # Remove zero percentage
    
    df.drop(['nan_percentage', 'nan_percentage_bin'], axis=1, inplace=True) # No more required
    
    if len(data_for_chart)==0:
        print('No nulls found')
    else:
        optional_settings.update({'x_label':'Percenatge Bin'}) 
        optional_settings.update({'y_label':'Number of records'})
        optional_settings.update({'chart_title':'Percenatge of missing values in each Row'})
        optional_settings.update({'sort_by_value':False})
        chartil.core_barchart_from_series(data_for_chart, optional_settings)
   
def cap_outliers_using_iqr(df, column_to_treat, lower_quantile=0.25, upper_quantile=0.75, iqr_range=1.5):
    q1 = df[column_to_treat].quantile(lower_quantile)
    q3 = df[column_to_treat].quantile(upper_quantile)
    iqr = q3 - q1
    lower_value = q1 - iqr_range*iqr
    upper_value = q3 + iqr_range*iqr
    df.loc[df[column_to_treat]<lower_value, column_to_treat] = lower_value
    df.loc[df[column_to_treat]>upper_value, column_to_treat] = upper_value
    print('Done')

def fill_category_column_na_with_new(df, column_name, na_column_name='Unknown'): 
    df[column_name].fillna(na_column_name, inplace=True)
    print('Done')
    
def fill_column_na_with_mode(df, column_name): # Can be applied to both categorical and numerical features
    df[column_name].fillna(df[column_name].mode()[0], inplace=True)
    print('Done')
    
def fill_column_na_with_mean(df, column_name): 
    df[column_name].fillna(df[column_name].mean(), inplace=True)
    print('Done')
    
def drop_rows_with_na_in_column(df, column_name):
    df.dropna(subset=[column_name], how='all', inplace = True)
    print('Done')
    
def drop_rows_with_na_percentage_in_row(df, percent_value):
    colNulls = (df.isnull().sum(axis=1))*100/(df.shape[1])
    df['nan_percentage']=colNulls    
    df.drop(df.index[df['nan_percentage'] >= percent_value], inplace = True)    
    df.drop(['nan_percentage'], axis=1, inplace=True) # nan_percentage No more required
    print('Done')
    
def cap_outliers_using_percentile(df, column_to_treat, lower_percent=2, upper_percent=98):
    upper_limit = np.percentile(df[column_to_treat], upper_percent) 
    lower_limit = np.percentile(df[column_to_treat], lower_percent) # Filter the outliers from the dataframe    
    df.loc[df[column_to_treat]<lower_limit, column_to_treat] = lower_limit
    df.loc[df[column_to_treat]>upper_limit, column_to_treat] = upper_limit
    print('Done')