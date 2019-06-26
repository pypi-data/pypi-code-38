import numpy as np
import pandas as pd

import statsmodels.api as sm

from sklearn.preprocessing import StandardScaler
from sklearn.preprocessing import MinMaxScaler

base_color_list = ['green', 'red', 'blue', 'orange', 'purple', 'brown', 'pink', 'gray', 'olive', 'cyan']


def createDummies(df, dummies_creation_drop_column_preference='dropFirst', 
                  exclude_columns=[], 
                  max_unique_values_dummies=1000) :
    """
    Create dummies/One hot encoding for categorical variables.
    
    Parameters
    ----------
    df : The full dataframe.
        The list of categorical variable will be detected using datatype of each feature.
    
    dummies_creation_drop_column_preference : string, default 'dropFirst'. 
        Strategy to follow retain dummy columns from one hot encoding.
        Options are 
            1. 'dropFirst' - Drop the first feature column from the new dummies created
            2. 'dropMin' - Drop the column which has least count within the specific categorical feature
            3. 'dropMax' - Drop the column which has maximum count within the specific categorical feature
        
    exclude_columns : list, default empty list
        Bypass the dummy creation for the features included in this list. 
        Usefull in case if you have target column which we do not want to be converted.
        
    max_unique_values_dummies : int , default 1000
        exclude features which has more than 1000 unique levels in the categorical feature.
     
    """    
    
    ## Convert Categorical variables 
    df_categorical = df.select_dtypes(include=['object', 'category'])
    
    categorical_column_names = list(df_categorical.columns)
    
    for x in exclude_columns:
        if x in categorical_column_names: categorical_column_names.remove(x)
    
    # Todo: if unique values>max_unique_values_dummies skip the variable 
    
    for aCatColumnName in categorical_column_names:
        levels_in_categorical =  len(df[aCatColumnName].value_counts())
        if (levels_in_categorical<max_unique_values_dummies) :
            dummy_df = pd.get_dummies(df[aCatColumnName], prefix=aCatColumnName)
        
            if dummies_creation_drop_column_preference=='dropFirst' :
                dummy_df = dummy_df.drop(dummy_df.columns[0], 1)
            elif dummies_creation_drop_column_preference=='dropMax' :
                column_with_max_records = aCatColumnName + "_" + str(df[aCatColumnName].value_counts().idxmax())
                dummy_df = dummy_df.drop(column_with_max_records, 1)
            elif dummies_creation_drop_column_preference=='dropMin' :
                column_with_min_records = aCatColumnName + "_" + str(df[aCatColumnName].value_counts().idxmin())
                dummy_df = dummy_df.drop(column_with_min_records, 1)
            else :
                raise Exception('Invalid value passed for dummies_creation_drop_column_preference. Valid options are: dropFirst, dropMax, dropMin')
            df = pd.concat([df, dummy_df], axis=1)
            df.drop([aCatColumnName], axis=1, inplace=True)
    return df

def scale_features(df, columns_to_scale, scaler_object = StandardScaler()) :
    print('Scaling numerical columns:' + str(columns_to_scale) )
    print('Scaling with '+str(scaler_object))
    return scaler_object.fit_transform(df[columns_to_scale])


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