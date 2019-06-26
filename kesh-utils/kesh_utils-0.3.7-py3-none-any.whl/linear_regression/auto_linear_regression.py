# Required imports
import numpy as np
import pandas as pd

from KUtils.common import utils as cutils

from sklearn.preprocessing import StandardScaler
from sklearn.preprocessing import MinMaxScaler
from sklearn.model_selection import train_test_split
from sklearn.feature_selection import RFE
from sklearn.linear_model import LinearRegression
import statsmodels.api as sm
from sklearn.metrics import mean_squared_error, r2_score

from imblearn.over_sampling import SMOTE

def fit(df, dependent_column,
        p_value_cutoff = 0.01,
        vif_cutoff = 5,
        acceptable_r2_change = 0.02,
        default_list_of_columns_to_retain = [],
        scale_numerical = False,
        scaler_object = StandardScaler(),
        include_target_column_from_scaling = True,
        apply_smote = False,
        dummies_creation_drop_column_preference='dropFirst', # Available options dropFirst, dropMax, dropMin
        train_split_size = 0.7,
        max_features_to_select = 0,
        random_state_to_use=43,
        include_data_in_return = False,
        verbose=False) :    # max_features_to_select=0 means Select all fields

    data_for_auto_lr = df
    
    
    response_dictionary = {} # Store all return content in the dictionary
    
    # If any null or nan found in datafrane, then throw a exception and return.
    if data_for_auto_lr.isna().sum().sum()>0 :
        raise Exception('Data is not clean, Null or nan values found in few columns. Check with df.isnull().sum()')
        
    ## Convert Categorical variables 
    df_categorical = data_for_auto_lr.select_dtypes(include=['object', 'category'])
    
    numerical_column_names =  [i for i in data_for_auto_lr.columns if not i in df_categorical.columns] 
    if verbose:
        print('Numerical columns :' + str(numerical_column_names))
        print('Categorical columns :' + str(df_categorical.columns))
        print('before dummies='+str(data_for_auto_lr.columns))
    data_for_auto_lr = cutils.createDummies(data_for_auto_lr, dummies_creation_drop_column_preference, exclude_columns=[dependent_column])
    if verbose:
        print('after dummies='+str(data_for_auto_lr.columns))
    ## Scale numerical Feature scaling
    #scaler = StandardScaler()
    if scale_numerical:
        if include_target_column_from_scaling==False:
            numerical_column_names.remove(dependent_column)
        cutils.scale_features(data_for_auto_lr, numerical_column_names, scaler_object)
    
        
        #data_for_auto_lr[numerical_column_names] = scaler_object.fit_transform(data_for_auto_lr[numerical_column_names])
        #if include_target_column_from_scaling==True:
        #    data_for_auto_lr[[dependent_column]] = scaler_object.fit_transform(data_for_auto_lr[[dependent_column]])
    
    if verbose:
        print('Building model...')
        
    # Model building starts here
    X = data_for_auto_lr.drop(dependent_column,1)
    y = data_for_auto_lr[dependent_column]
    
    test_split_size = (1-train_split_size)
    X_train, X_test, y_train, y_test = train_test_split(X, y, train_size=train_split_size, test_size=test_split_size, random_state=random_state_to_use)
    
    if apply_smote:
        print('Before smote ' + str(X_train.shape))
        smote = SMOTE(random_state=2)
        X_train_res, y_train_res = smote.fit_sample(X_train, y_train)
        # Convert X_train back as dataframe (Smote returns ndarray)
        X_train = pd.DataFrame(X_train_res, columns=X_train.columns)
        y_train = y_train_res
        print('After smote ' + str(X_train.shape))

    # Set max_features_to_select if not passed
    if max_features_to_select<=0 : # So no parameter passed, use all available column
        max_features_to_select = len(X_train.columns)
    
    # First run RFE
    lm = LinearRegression()
    rfe = RFE(lm,max_features_to_select) 
    rffilter = rfe.fit(X_train, y_train)
    columns_to_use_further = X_train.columns[rfe.support_]
    columns_to_use_further = columns_to_use_further.tolist()
    
    if verbose:
        print('First Model afte RFE')
        
    comment = 'After RFE(' + str(max_features_to_select) + ")" + str(columns_to_use_further)
    model_iteration_info = pd.DataFrame( columns=['comment','r2_train', 'r2_adj_train', 'aic', 'bic', 'p_value_fstat', 'rmse_test', 'r2_test'])
    model_iteration=0
    prev_adj_r2 = 1
    column_to_remove = ""
    retain_columns = default_list_of_columns_to_retain
                 
    no_more_backward_elimination_possible = False;
    while(not no_more_backward_elimination_possible):
        # Backward Elimination using Vif and p-value
        
        # Chec k p-value using stat
        X_train_sm = X_train[columns_to_use_further]
        X_train_sm = sm.add_constant(X_train_sm)
        
        lm_1 = sm.OLS(y_train, X_train_sm).fit()
        
        if verbose:
            print('R2=' + str(lm_1.rsquared) + ' R2Adj=' + str(lm_1.rsquared_adj) )
        
        # Lets predict on test data
        x_test_sm = X_test[columns_to_use_further]
        x_test_sm  = sm.add_constant(x_test_sm)
        y_pred_intr = lm_1.predict(x_test_sm)
        
        rmse_test = np.sqrt(mean_squared_error(y_test, y_pred_intr))
        
        r2_test = r2_score(y_test, y_pred_intr)
        
        if model_iteration==0:
            prev_adj_r2 = lm_1.rsquared_adj
            model_iteration_info.loc[model_iteration]=[comment, lm_1.rsquared, lm_1.rsquared_adj, lm_1.aic, lm_1.bic, lm_1.f_pvalue, rmse_test, r2_test]
            
        else:
            change_in_adjr2 = prev_adj_r2 - lm_1.rsquared_adj
            if change_in_adjr2 > acceptable_r2_change : # Put back the column
                columns_to_use_further = columns_to_use_further + [column_to_remove]
                retain_columns = retain_columns + [column_to_remove]
                model_iteration_info.loc[model_iteration_info.shape[0]]=['Degraded Adj R2, Putting back feature '+str(column_to_remove)+"(Reverting " + comment + ")", lm_1.rsquared, lm_1.rsquared_adj, lm_1.aic, lm_1.bic, lm_1.f_pvalue, rmse_test, r2_test ]
                if verbose:
                    print(model_iteration_info.loc[model_iteration]['comment'])
                # rebuild the model by putting back the last removed column
                X_train_sm = X_train[columns_to_use_further]
                X_train_sm = sm.add_constant(X_train_sm)            
                lm_1 = sm.OLS(y_train, X_train_sm).fit()
            else :
                prev_adj_r2 = lm_1.rsquared_adj
                retain_columns = default_list_of_columns_to_retain # Reset columns to retain in this iteration
                model_iteration_info.loc[model_iteration]=[comment, lm_1.rsquared, lm_1.rsquared_adj, lm_1.aic, lm_1.bic, lm_1.f_pvalue, rmse_test, r2_test]
                
        
        p_values_df = pd.DataFrame({'Feature':lm_1.pvalues.index, 'p-value':lm_1.pvalues.values}).sort_values(by='p-value', axis=0, ascending=False, inplace=False)
        p_values_df = p_values_df[(~p_values_df['Feature'].isin(retain_columns))]
        p_values_df_filtered = p_values_df[(p_values_df['p-value']>p_value_cutoff) & (p_values_df['Feature']!='const')]
        
        vif_df = cutils.calculate_vif(X_train[columns_to_use_further])
        vif_df = vif_df[(~vif_df['Feature'].isin(retain_columns))]
        vif_df_filtered = vif_df[(vif_df['Vif']>vif_cutoff)] # Already in asceinding order
        
        column_to_remove = ""
        for index, row in vif_df_filtered.iterrows():
            vif_with_high_value = row[0]        
            p_value_found = p_values_df_filtered[p_values_df_filtered['Feature']==vif_with_high_value]
            if len(p_value_found)>0 : # Common name found in feature in p-value df and vif df
                column_to_remove = vif_with_high_value
                #print('Found in both vif and p-value df')
                break # No need to check further
        
        if column_to_remove=="" and len(p_values_df_filtered)>0: # There is no column column left in vif and df
            column_to_remove = p_values_df_filtered.iloc[0]['Feature']
            #print('Found in p-value df')
            
        if column_to_remove=="" and len(vif_df_filtered)>0: # Still no column selected indicates all column are significant with low p-value
            for index, row in vif_df_filtered.iterrows():
                aVifFeature = row[0] 
                p_valueOfThatFeature = p_values_df[p_values_df['Feature']==aVifFeature]
                p_valueOfThatFeature  = p_valueOfThatFeature['p-value']
                #print(p_valueOfThatFeature)
                p_valueOfThatFeature = p_valueOfThatFeature[:,np.newaxis]
                #print(p_valueOfThatFeature)
                                
                if p_valueOfThatFeature[0][0]>0 :
                    column_to_remove = aVifFeature 
                    #print('column_to_remove='+column_to_remove)
                    #print(p_valueOfThatFeature[0][0])
                    break
        
        if column_to_remove!="":
            columns_to_use_further.remove(column_to_remove)
            comment = 'Removing ' + column_to_remove + ' with Vif=' + str(vif_df[(vif_df['Feature']==column_to_remove)].iloc[0]['Vif']) + ' p-value=' + str(p_values_df[(p_values_df['Feature']==column_to_remove)].iloc[0]['p-value'])
            if verbose:
                print(comment)
            #print(vif_df)
            #print(p_values_df)
           
        if column_to_remove == "" or len(columns_to_use_further)==0:
            no_more_backward_elimination_possible = True
            
        model_iteration = model_iteration + 1
    
    # Final model and R2 on test data
    X_train_sm = X_train[columns_to_use_further]
    X_train_sm = sm.add_constant(X_train_sm)
    
    lm_1 = sm.OLS(y_train, X_train_sm).fit()
    
    if verbose:
        print('\nFinal Linear Regression Model Stat & Detailed Summary\n')
        print(lm_1.summary())
    
    # Lets predict on test data
    x_test_sm = X_test[columns_to_use_further]
    x_test_sm  = sm.add_constant(x_test_sm)
    y_pred_final = lm_1.predict(x_test_sm)
    
    rmse_test = np.sqrt(mean_squared_error(y_test, y_pred_final))
    r2_test = r2_score(y_test, y_pred_final)
    
    model_iteration_info.loc[model_iteration]=['Final Model with '+str(columns_to_use_further), lm_1.rsquared, lm_1.rsquared_adj, lm_1.aic, lm_1.bic, lm_1.f_pvalue, rmse_test, r2_test]
    
    response_dictionary['model_iteration_info'] = model_iteration_info
    response_dictionary['r2_test'] = r2_test
    response_dictionary['p-values'] =  pd.DataFrame({'Feature':lm_1.pvalues.index, 'p-value':lm_1.pvalues.values}).sort_values(by='p-value', axis=0, ascending=False, inplace=False)

    response_dictionary['vif-values'] = cutils.calculate_vif(X_train[columns_to_use_further])
    
    response_dictionary['rmse_test'] = rmse_test
    
    response_dictionary['model_summary'] = lm_1.summary()
    
    if include_data_in_return:
        response_dictionary['final_input_data'] = data_for_auto_lr
        response_dictionary['features_in_final_model'] = columns_to_use_further
    
    # print('Done')
    return response_dictionary