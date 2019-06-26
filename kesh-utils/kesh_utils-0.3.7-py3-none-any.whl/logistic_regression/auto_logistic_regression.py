# Required imports
import numpy as np
import pandas as pd

import matplotlib.pyplot as plt

from KUtils.common import utils as cutils

from sklearn.preprocessing import StandardScaler
from sklearn.preprocessing import MinMaxScaler
from sklearn.model_selection import train_test_split
from sklearn.feature_selection import RFE
from sklearn.linear_model import LogisticRegression
import statsmodels.api as sm
from sklearn import metrics

from imblearn.over_sampling import SMOTE

def calculateGLMKpis(pred_df, cutoff_by='Precision-Recall', include_cutoff_df_in_return=False) :  # cutoff_by='Sensitivity-Specificity'
    
    cutoff_df = pd.DataFrame( columns = ['Probability', 'Accuracy', 'Sensitivity','Specificity', 'Precision', 'Recall'])
    
    for i in np.arange(0, 1, 0.01):
        pred_df['predicted'] = pred_df.Probability.map(lambda x: 1 if x > i else 0)
        
        local_confusion_matrix = metrics.confusion_matrix(pred_df['Actual'], pred_df['predicted'] )
        
        accuracy = metrics.accuracy_score(pred_df['Actual'], pred_df['predicted'])

        precision = metrics.precision_score(pred_df['Actual'], pred_df['predicted'])
        recall = metrics.recall_score(pred_df['Actual'], pred_df['predicted'])
        
        sensitivity = recall
        specificity =  local_confusion_matrix[0,0]/(local_confusion_matrix[0,0]+local_confusion_matrix[0,1])

        cutoff_df.loc[i] =[ i , accuracy, sensitivity, specificity, precision, recall]

    # Plot the chart with Accuracy, Sensitivity and Specificity
    # cutoff_df.plot.line(x='Probability', y=['Sensitivity','Specificity'])
    # plt.show()

    # Find probability cutoff by Precision-Recall or Sensitivity-Specificity
    probability_cutoff = 0
    for index, row in cutoff_df.iterrows():        
        if cutoff_by=='Precision-Recall':
            if row['Recall']<row['Precision'] :
                probability_cutoff = row['Probability']
                break
        else: # cutoff_by='Sensitivity-Specificity'
            if row['Sensitivity']<row['Specificity'] :
                probability_cutoff = row['Probability']
                break
            
    print('probability_cutoff:' + str(probability_cutoff))
    # Use this as Threshold cutoff 
    pred_df['predicted'] = pred_df.Probability.map(lambda x: 1 if x > probability_cutoff else 0)
    
    # Accuracy, precision, recall and f1 score
    local_confusion_matrix = metrics.confusion_matrix(pred_df['Actual'], pred_df['predicted'] )

    accuracy = metrics.accuracy_score(pred_df['Actual'], pred_df['predicted'])
    precision = metrics.precision_score(pred_df['Actual'], pred_df['predicted'])
    recall = metrics.recall_score(pred_df['Actual'], pred_df['predicted'])
    f1_score = metrics.f1_score(pred_df['Actual'], pred_df['predicted'])
    roc_auc = metrics.roc_auc_score(pred_df['Actual'], pred_df['predicted'])
    sensitivity = recall
    specificity =  local_confusion_matrix[0,0]/(local_confusion_matrix[0,0]+local_confusion_matrix[0,1])
    
    return_dictionary = {}
    return_dictionary['probability_cutoff'] = probability_cutoff
    return_dictionary['accuracy'] = accuracy
    return_dictionary['sensitivity'] = sensitivity
    return_dictionary['specificity'] = specificity
    return_dictionary['precision'] = precision
    return_dictionary['recall'] = recall
    return_dictionary['f1_score'] = f1_score
    return_dictionary['roc_auc'] = roc_auc
    if include_cutoff_df_in_return==True:
        return_dictionary['cutoff_df'] = cutoff_df
    return return_dictionary
    
def fit(df, dependent_column,
        p_value_cutoff = 0.01,
        vif_cutoff = 5,
        scoring='accuracy', # accuracy, sensitivity, specificity, precision, recall, f1_score, roc_auc 
        acceptable_model_performance = 0.02,
        cutoff_using = 'Sensitivity-Specificity', # Optiona are 'Sensitivity-Specificity' and 'Precision-Recall'
        scale_numerical = False,
        scaler_object = StandardScaler(),
        apply_smote = False,
        default_list_of_columns_to_retain = [], # Columsn or features must be in the model (Retain those features)       
        dummies_creation_drop_column_preference='dropFirst', # Available options dropFirst, dropMax, dropMin
        train_split_size = 0.7,
        max_features_to_select = 0, # max_features_to_select=0 means Select all fields
        random_state_to_use=43,
        include_data_in_return = False,
        verbose=False) :    

    data_for_auto_lr = df    
    
    response_dictionary = {} # Store all return content in the dictionary
    
    # If any null or nan found in datafrane, then throw a exception and return.
    if data_for_auto_lr.isna().sum().sum()>0 :
        raise Exception('Data is not clean, Null or nan values found in few columns. Check with df.isnull().sum()')
        
    if data_for_auto_lr[dependent_column].dtype.kind=='O':
        raise Exception('Target/dependent_column varibale not mapped to numeric 0 or 1. Convert to Numeric and try again')
        
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
    if scale_numerical:
        numerical_column_names.remove(dependent_column)        
        cutils.scale_features(data_for_auto_lr, numerical_column_names, scaler_object)
        # data_for_auto_lr[numerical_column_names] = scaler_object.fit_transform(data_for_auto_lr[numerical_column_names])
    
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
    if max_features_to_select==0 : # So no parameter passed, use all available column
        max_features_to_select = len(X_train.columns)-1
    
    if (max_features_to_select!=-1): # Run RFE
        # First run RFE
        glm = LogisticRegression(solver='lbfgs') # solver='lbfgs' Refer: https://machinelearningmastery.com/how-to-fix-futurewarning-messages-in-scikit-learn/
        rfe = RFE(glm, max_features_to_select) 
        rffilter = rfe.fit(X_train, y_train)
        columns_to_use_further = X_train.columns[rfe.support_]
        columns_to_use_further = columns_to_use_further.tolist()
    else:
        columns_to_use_further = X_train.columns
        columns_to_use_further = columns_to_use_further.tolist()
    
    if verbose:
        print('First Model afte RFE')
        
    comment = 'After RFE(' + str(max_features_to_select) + ")" + str(columns_to_use_further)
    
    model_iteration_info = pd.DataFrame( columns=['comment','probability_cutoff', 'accuracy', 'sensitivity', 'specificity', 'precision', 'recall', 'f1_score', 'roc_auc'])
    
    model_iteration=0
    prev_performance = 1
    column_to_remove = ""
    retain_columns = default_list_of_columns_to_retain
                 
    no_more_backward_elimination_possible = False;
    while(not no_more_backward_elimination_possible):
        # Backward Elimination using Vif and p-value
        
        # New model
        X_train_sm = sm.add_constant(X_train[columns_to_use_further])
        glm_1 = sm.GLM(y_train, X_train_sm, family=sm.families.Binomial()).fit()        
        
        # Lets predict on test data
        x_test_sm  = sm.add_constant(X_test[columns_to_use_further])
        y_pred_intr = glm_1.predict(x_test_sm)
        
        test_pred_df = pd.DataFrame({'Actual':y_test.values, 'Probability':y_pred_intr})
        return_dictionary = calculateGLMKpis(test_pred_df, cutoff_by=cutoff_using)

        if verbose:
            print('probability_cutoff=' + str(return_dictionary['probability_cutoff']) + ' '+ scoring + '=' + str(return_dictionary[scoring]) )
        
        
        if model_iteration==0:
            prev_performance = return_dictionary[scoring]
            model_iteration_info.loc[model_iteration]=[comment, return_dictionary['probability_cutoff'], 
                                     return_dictionary['accuracy'], return_dictionary['sensitivity'], 
                                     return_dictionary['specificity'], return_dictionary['precision'], 
                                     return_dictionary['recall'], return_dictionary['f1_score'], 
                                     return_dictionary['roc_auc']]
            
        else:
            change_in_performance = abs(prev_performance - return_dictionary[scoring])
            if change_in_performance > acceptable_model_performance : # Put back the column
                columns_to_use_further = columns_to_use_further + [column_to_remove]
                retain_columns = retain_columns + [column_to_remove]
                model_iteration_info.loc[model_iteration_info.shape[0]]=['Degraded model performance, Putting back feature '+str(column_to_remove)+"(Reverting " + comment + ")", return_dictionary['probability_cutoff'], 
                                     return_dictionary['accuracy'], return_dictionary['sensitivity'], 
                                     return_dictionary['specificity'], return_dictionary['precision'], 
                                     return_dictionary['recall'], return_dictionary['f1_score'], 
                                     return_dictionary['roc_auc'] ]
                if verbose:
                    print(model_iteration_info.loc[model_iteration]['comment'])
                # rebuild the model by putting back the last removed column
                X_train_sm = X_train[columns_to_use_further]
                X_train_sm = sm.add_constant(X_train_sm) 
                glm_1 = sm.GLM(y_train, X_train_sm, family=sm.families.Binomial()).fit()
            else :
                prev_performance = return_dictionary[scoring]
                retain_columns = default_list_of_columns_to_retain # Reset columns to retain in this iteration
                model_iteration_info.loc[model_iteration]=[comment, return_dictionary['probability_cutoff'], 
                                     return_dictionary['accuracy'], return_dictionary['sensitivity'], 
                                     return_dictionary['specificity'], return_dictionary['precision'], 
                                     return_dictionary['recall'], return_dictionary['f1_score'], 
                                     return_dictionary['roc_auc']]
                
        
        p_values_df = pd.DataFrame({'Feature':glm_1.pvalues.index, 'p-value':glm_1.pvalues.values}).sort_values(by='p-value', axis=0, ascending=False, inplace=False)
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

    glm_1 = sm.GLM(y_train, X_train_sm, family=sm.families.Binomial()).fit()        

    if verbose:
        print('\nFinal Linear Regression Model Stat & Detailed Summary\n')
        print(glm_1.summary())
    
    # Lets predict on test data
    x_test_sm  = sm.add_constant(X_test[columns_to_use_further])
    y_pred_final = glm_1.predict(x_test_sm)
    
    test_pred_df = pd.DataFrame({'Actual':y_test.values, 'Probability':y_pred_final})
    return_dictionary = calculateGLMKpis(test_pred_df, cutoff_by=cutoff_using, include_cutoff_df_in_return=True)
    
    final_confusion_matrix = metrics.confusion_matrix(test_pred_df['Actual'], test_pred_df['predicted'] )

    model_iteration_info.loc[model_iteration]=['Final Model with '+str(columns_to_use_further), return_dictionary['probability_cutoff'], 
                                     return_dictionary['accuracy'], return_dictionary['sensitivity'], 
                                     return_dictionary['specificity'], return_dictionary['precision'], 
                                     return_dictionary['recall'], return_dictionary['f1_score'], 
                                     return_dictionary['roc_auc']]
    
    response_dictionary['model_iteration_info'] = model_iteration_info
    response_dictionary['p-values'] =  pd.DataFrame({'Feature':glm_1.pvalues.index, 'p-value':glm_1.pvalues.values}).sort_values(by='p-value', axis=0, ascending=False, inplace=False)

    response_dictionary['vif-values'] = cutils.calculate_vif(X_train[columns_to_use_further])
    
    response_dictionary['model_summary'] = glm_1.summary()
    
    response_dictionary['cutoff_df'] = return_dictionary['cutoff_df']
    response_dictionary['confusion_matrix'] = final_confusion_matrix
    response_dictionary['prediction_df'] = test_pred_df
    
    if include_data_in_return:
        response_dictionary['final_input_data'] = data_for_auto_lr
        response_dictionary['features_in_final_model'] = columns_to_use_further
    
    # print('Done')
    return response_dictionary

# ROC curve in Python
# Defining the function to plot the ROC curve
def draw_roc( prediction_df ):
    
    actual = prediction_df['Actual']
    probs = prediction_df['predicted']
    fpr, tpr, thresholds = metrics.roc_curve( actual, probs,
                                              drop_intermediate = False )
    auc_score = metrics.roc_auc_score( actual, probs )
    
    plt.figure(figsize=(5, 5))
    plt.plot( fpr, tpr, label='ROC curve (area = %0.2f)' % auc_score )
    plt.plot([0, 1], [0, 1], 'k--')
    plt.xlim([0.0, 1.0])
    plt.ylim([0.0, 1.05])
    plt.xlabel('False Positive Rate or [1 - True Negative Rate]')
    plt.ylabel('True Positive Rate')
    plt.title('Receiver operating characteristic example')
    plt.legend(loc="lower right")
    plt.show()