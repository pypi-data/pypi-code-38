# Load required libraries
import numpy as np
import pandas as pd
import math  

def find_best_stacking_blend(df, 
                             actual_target_column_name, 
                             columns_to_blend, 
                             starting_weight=1,
                             max_weight=10,
                             step_weight=1,
                             minimize_loss='rmse', # mae
                             verbose=False):
    
    print('Running...')
    print('..........Have patience - Brute force with all combination will take time-')
    no_of_columns_to_blend=len(columns_to_blend)
    weight_df = pd.DataFrame({'Feature':columns_to_blend})
    weight_df['weight'] = starting_weight
    
    all_possibilities_completed = False
    previous_best_total_error = 100000000
    
    best_blends_df = pd.DataFrame(columns=[minimize_loss] + columns_to_blend)
    while(all_possibilities_completed==False): 
        start_pos = no_of_columns_to_blend-1
        
        is_weights_valid=False
        while(is_weights_valid==False and start_pos>=0) :
            weight_df.iloc[start_pos,1] = weight_df.iloc[start_pos,1] + step_weight
            if (start_pos==0 and weight_df.iloc[start_pos,1]>max_weight):
                is_weights_valid=True
                all_possibilities_completed=True
                break
            else:
                if (weight_df.iloc[start_pos,1]<=max_weight):
                    is_weights_valid=True
                else :
                    weight_df.iloc[start_pos,1] = starting_weight
                    start_pos = start_pos - 1
                    
        if (all_possibilities_completed==False):
            #print(weight_df)
            df['new_value'] = 0
            for i in range(0, no_of_columns_to_blend, 1):
                df['new_value'] = df['new_value'] + df[columns_to_blend[i]]*weight_df.iloc[i,1]
            df['new_value']=df['new_value']/sum(weight_df['weight'])
            #mse
            df['error'] = abs(df[actual_target_column_name]-df['new_value'])
            if minimize_loss=='rmse':
                df['error']=df['error']*df['error']
            total_error = sum(df['error'])
            if minimize_loss=='rmse':
                degree_of_freedom = (df.shape[0]-1)
                total_error = math.sqrt(total_error)/degree_of_freedom
            #print('total_error='+str(total_error))
            #print('previous_best_total_error='+str(previous_best_total_error))
            if (total_error<previous_best_total_error):
                previous_best_total_error = total_error            
                #print(weight_df)
                location_for_new_entry_in_best_blend_df = best_blends_df.shape[0]
                best_blends_df = best_blends_df.append(pd.Series(), ignore_index=True)
                best_blends_df.iloc[location_for_new_entry_in_best_blend_df:,0]=total_error
                for i in range(0, no_of_columns_to_blend, 1):
                    best_blends_df.iloc[location_for_new_entry_in_best_blend_df:,(i+1)]=weight_df.iloc[i,1]
                if verbose:
                    print('\nNew best blend coeficient found with total_error='+str(total_error))
                    print(best_blends_df.iloc[best_blends_df.shape[0]-1:])
    del  df['new_value']
    del  df['error']

    print('\nFinal Best blend coefficients found at ')
    print(best_blends_df.iloc[best_blends_df.shape[0]-1:])
    print('With least error ' + str(best_blends_df.iloc[best_blends_df.shape[0]-1:,0]))
    print('Done') 
    
    return best_blends_df