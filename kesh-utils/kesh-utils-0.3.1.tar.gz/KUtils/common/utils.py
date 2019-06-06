import numpy as np
import pandas as pd

def createDummies(df, dummies_creation_drop_column_preference='dropFirst', max_unique_values_dummies=1000) :
    ## Convert Categorical variables 
    df_categorical = df.select_dtypes(include=['object', 'category'])
    
    categorical_column_names = df_categorical.columns
    
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