import numpy as np
import pandas as pd

import statsmodels.api as sm

def createDummies(df, dummies_creation_drop_column_preference='dropFirst', exclude_columns=[], max_unique_values_dummies=1000) :
    ## Convert Categorical variables 
    df_categorical = df.select_dtypes(include=['object', 'category'])
    
    categorical_column_names = list(df_categorical.columns)
    
    for x in exclude_columns:
        if x in categorical_column_names: categorical_column_names.remove(x)
    
    # Todo: if unique values>max_unique_values_dummies skip the variable 
    
    for aCatColumnName in categorical_column_names:        
        dummy_df = pd.get_dummies(df[aCatColumnName], prefix=aCatColumnName)
    
        if dummies_creation_drop_column_preference=='dropFirst' :
            dummy_df = dummy_df.drop(dummy_df.columns[0], 1)
        elif dummies_creation_drop_column_preference=='dropMax' :
            column_with_max_records = aCatColumnName + "_" + df[aCatColumnName].value_counts().idxmax()
            dummy_df = dummy_df.drop(column_with_max_records, 1)
        elif dummies_creation_drop_column_preference=='dropMin' :
            column_with_min_records = aCatColumnName + "_" + df[aCatColumnName].value_counts().idxmin()
            dummy_df = dummy_df.drop(column_with_min_records, 1)
        else :
            raise Exception('Invalid value passed for dummies_creation_drop_column_preference. Valid options are: dropFirst, dropMax, dropMin')
        df = pd.concat([df, dummy_df], axis=1)
        df.drop([aCatColumnName], axis=1, inplace=True)
    return df

def calculate_vif(input_data, exclude_columns=[]):
    vif_df = pd.DataFrame( columns=['Feature','Vif'])
    x_vars = input_data.drop(exclude_columns, axis=1)
    xvar_names = x_vars.columns
    if len(xvar_names)>1: # Atlease 2 x column should be there to calculate vif
        for i in range(0,xvar_names.shape[0]):
            y=x_vars[xvar_names[i]]
            x=x_vars[xvar_names.drop(xvar_names[i])]        
            rsq=sm.OLS(y,x).fit().rsquared
            vif=round(1/(1-rsq),2)
            vif_df.loc[i]=[xvar_names[i],vif]
    return vif_df.sort_values(by='Vif', axis=0, ascending=False, inplace=False)

def standardize(x):
    return ((x-np.mean(x))/np.std(x))