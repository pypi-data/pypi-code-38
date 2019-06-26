import numpy as np
import pandas as pd

def extract_best_original_feature_from_pca(pca_components, original_column_names, 
                                           no_of_pca_components=5,  
                                           no_of_best_features_per_pca=4,
                                           print_features=False):
    
    pca_df = pd.DataFrame({'Feature':original_column_names})
    for i in range(0, len(pca_components),1):
        pca_df['PC_'+str(i+1)] = pca_components[i]
    
    
    important_feature_list=[]
    
    for i in range(1,(no_of_pca_components+1)):
        pca_feature_name = 'PC_'+str(i)    
        
        sorted_df = pca_df.sort_values(by=[pca_feature_name], ascending=[False])
        max_variance_rows = sorted_df.iloc[0:no_of_best_features_per_pca:,[0,i]]
        important_feature_list = important_feature_list + list(max_variance_rows.iloc[:,0]) 
        if print_features:
            print('\nFor ' + pca_feature_name + ' Top ' + str(no_of_best_features_per_pca) + ' variations captured from')
            print(max_variance_rows)
    
    if print_features:
        print('\nImportant features extracted from PCA based on max variance\n')
        print(important_feature_list)

    return pca_df, important_feature_list