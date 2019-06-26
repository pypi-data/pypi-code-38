import numpy as np
import pandas as pd
import itertools

from KUtils.eda import chartil
from KUtils.eda import data_preparation as dp
from KUtils.linear_regression import auto_linear_regression as autolr

def fit(data_df, feature_group_list, dependent_column, max_level = 2, min_leaf_in_filtered_dataset=1000, no_of_bins_for_continuous_feature=10, verbose=False):
    df = data_df
    # The current implementation supports only upto 3 level
    if max_level>2:
        raise Exception('The current implementation supports only upto 2 feature combination. Use 1 or 2 feature combinations')
    if len(feature_group_list)<max_level:
        max_level = len(feature_group_list)

    # Rearrange/Rebuild feature group column list (Convert if there is any continous variable)
    final_feature_group_list = []
    
    column_to_drop_later = []
    for aFeature in feature_group_list:
        if df[aFeature].dtype.kind=='O': # Object or Category type
            final_feature_group_list.append(aFeature)
        else: # It is numeric, convert it to bin of 10size
            no_of_bins = no_of_bins_for_continuous_feature 
            start_idx = min(df[aFeature])
            end_idx = max(df[aFeature])
            step = (end_idx - start_idx)/no_of_bins
            bin_labels = np.arange(start_idx, end_idx, step).tolist()
            temp_column_name = aFeature+'_tmp_bin'
            df[temp_column_name] = pd.cut(df[aFeature], no_of_bins, labels=bin_labels )
            df[temp_column_name] = df[temp_column_name].astype('str')
            final_feature_group_list.append(temp_column_name)
            column_to_drop_later.append(temp_column_name)
            # Todo: Should we drop the original feature from df?
    
    group_idx =0
    group_model_info = pd.DataFrame( columns=['group_id','group_details', 'subgroup_id', 'subgroup_dataset_details', 'additional_comment', 'rmse_test', 'r2_test', 'dataset_size'])
    
    for iter_level in range(1, max_level+1):
        for subset in itertools.combinations(final_feature_group_list, iter_level):
            column_lists_to_process = list(subset)
            group_idx = group_idx + 1
            if len(column_lists_to_process)==1: # Single feature
                subgroup_idx = 0
                for aCatLevel in df[column_lists_to_process[0]].unique():
                    subgroup_idx = subgroup_idx + 1
                    if verbose==True:
                        print('Processing group:' + str(group_idx) + ' Subgroup:' + str(subgroup_idx) + ' Data filter:' + column_lists_to_process[0] + '==' + aCatLevel)
                    subset_df = df[(df[column_lists_to_process[0]]==aCatLevel)]
                    if subset_df.shape[0]<min_leaf_in_filtered_dataset:
                        group_model_info.loc[group_model_info.shape[0]] = [group_idx, str(column_lists_to_process), subgroup_idx, column_lists_to_process[0]+'='+aCatLevel, 'Insufficient datapoints', 0, 0, subset_df.shape[0]]
                        if verbose==True:
                            print('Insufficient datapoints')
                    else :
                        model_info = autolr.fit(subset_df, dependent_column, 
                                                        scale_numerical=True, acceptable_r2_change = 0.005,
                                                        include_target_column_from_scaling=True, 
                                                        dummies_creation_drop_column_preference='dropMin',
                                                        random_state_to_use=100, include_data_in_return=False)
                        group_model_info.loc[group_model_info.shape[0]] = [group_idx, str(column_lists_to_process), subgroup_idx, column_lists_to_process[0]+'='+aCatLevel, '', model_info['rmse_test'], model_info['r2_test'], subset_df.shape[0]]
            else: # Two feature combination
                subgroup_idx = 0
                for aCat1Level in df[column_lists_to_process[0]].unique():  
                    for aCat2Level in df[column_lists_to_process[1]].unique(): 
                        subgroup_idx = subgroup_idx + 1
                        if verbose==True:
                            print('Processing group:' + str(group_idx) + ' Subgroup:' + str(subgroup_idx) + ' Data filter:' + column_lists_to_process[0] + '==' + aCat1Level + ' & ' + column_lists_to_process[1] + '==' + aCat2Level)
                        subset_df = df[(df[column_lists_to_process[0]]==aCat1Level) & (df[column_lists_to_process[1]]==aCat2Level)]
                        if subset_df.shape[0]<min_leaf_in_filtered_dataset:
                            group_model_info.loc[group_model_info.shape[0]] = [group_idx, str(column_lists_to_process), subgroup_idx, column_lists_to_process[0]+'='+aCat1Level+' & '+column_lists_to_process[1]+'='+aCat2Level, 'Insufficient datapoints', 0, 0, subset_df.shape[0]]
                            if verbose==True:
                                print('Insufficient datapoints')
                        else :
                            model_info = autolr.fit(subset_df, dependent_column,
                                                    scale_numerical=True, acceptable_r2_change = 0.005,
                                                    include_target_column_from_scaling=True, 
                                                    dummies_creation_drop_column_preference='dropMin',
                                                    random_state_to_use=100, include_data_in_return=False)
                            group_model_info.loc[group_model_info.shape[0]] = [group_idx, str(column_lists_to_process), subgroup_idx, column_lists_to_process[0]+'='+aCat1Level+' & '+column_lists_to_process[1]+'='+aCat2Level, '', model_info['rmse_test'], model_info['r2_test'], subset_df.shape[0]]   
    
    
    group_model_info['cumulative_rmse_test'] = group_model_info['rmse_test']*group_model_info['dataset_size']
    group_model_info['cumulative_r2_test'] = group_model_info['r2_test']*group_model_info['dataset_size']
    
    group_model_summary = group_model_info.groupby(
       ['group_id']
    ).agg(
        {
             'group_id':'first',
             'group_details':'first',
             'dataset_size':sum,
             'cumulative_rmse_test': sum,
             'cumulative_r2_test':sum
        }
    )
    
    group_model_summary['mean_test_rmse'] = group_model_summary['cumulative_rmse_test']/group_model_summary['dataset_size']
    group_model_summary['mean_test_r2'] = group_model_summary['cumulative_r2_test']/group_model_summary['dataset_size']
    
    # Cleanup the features added for temporary purpose
    del group_model_summary['dataset_size']
    del group_model_summary['cumulative_rmse_test']
    del group_model_summary['cumulative_r2_test']
    
    del group_model_info['cumulative_rmse_test']
    del group_model_info['cumulative_r2_test']
       
    for x in column_to_drop_later:
        del df[x]
    
    return group_model_info, group_model_summary