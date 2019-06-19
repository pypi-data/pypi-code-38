import numpy as np
import pandas as pd 


import matplotlib.pyplot as plt

from sklearn.model_selection import GridSearchCV
from sklearn.metrics import accuracy_score, make_scorer, recall_score, precision_score, roc_auc_score
from sklearn.tree import DecisionTreeClassifier

base_color_list = ['green', 'red', 'blue', 'orange', 'purple', 'brown', 'pink', 'gray', 'olive', 'cyan']

def tree_classfier_single_hyperparameter_tuning(X_train, y_train,                                                
                                                cv_folds=10, 
                                                hyper_parameter_name='max_depth',
                                                hyper_parameter_range = range(10, 40),                                                
                                                classifier_algo=DecisionTreeClassifier(random_state=100),
                                                refit='Precision',
                                                model_scoring = {'Precision': make_scorer(precision_score),
                                                                 'Recall': make_scorer(recall_score), #  'Accuracy': make_scorer(accuracy_score),
                                                                 'AUC': make_scorer(roc_auc_score)}
                                                ):
    # parameters to build the model on
    parameters = {hyper_parameter_name: hyper_parameter_range}

    # instantiate the model
    dtree = classifier_algo

    # fit tree on training data
    treeGrid = GridSearchCV(dtree, parameters, cv=cv_folds, scoring=model_scoring, refit=refit, return_train_score=True, verbose = 1)
    treeGrid.fit(X_train, y_train)

    # scores of GridSearch CV
    scores = treeGrid.cv_results_
    
    plot_single_hyperparameter_tuning_result(scores, hyper_parameter_name, model_scoring)

    print("Best score", treeGrid.best_score_)
    print("Best Estimator", treeGrid.best_estimator_)

    return scores
    
def plot_single_hyperparameter_tuning_result(scores, hyper_parameter_name, model_scoring) :
    
    plt.figure(figsize=(13, 8))
    plt.title("Multiple scorers evaluation", fontsize=16)
    
    plt.xlabel(hyper_parameter_name)
    plt.ylabel("Score")
    
    # Get the regular numpy array from the MaskedArray
    X_axis = np.array(scores['param_'+hyper_parameter_name].data, dtype=float)
    
    ax = plt.gca()
    ax.set_xlim(min(X_axis), max(X_axis))
    
    lowest_y_value=1
    
    for scorer, color in zip(sorted(model_scoring), base_color_list[:len(model_scoring)]):
        for sample, style in (('train', '--'), ('test', '-')):
            sample_score_mean = scores['mean_%s_%s' % (sample, scorer)]
            if min(sample_score_mean)<lowest_y_value:
                lowest_y_value = min(sample_score_mean)
            
            ax.plot(X_axis, sample_score_mean, style, color=color,
                    alpha=1 if sample == 'test' else 0.7,
                    label="%s (%s)" % (scorer, sample))
    
        best_index = np.nonzero(scores['rank_test_%s' % scorer] == 1)[0][0]
        best_score = scores['mean_test_%s' % scorer][best_index]
    
        # Plot a dotted vertical line at the best score for that scorer marked by x
        ax.plot([X_axis[best_index], ] * 2, [0, best_score],
                linestyle='-.', color=color, marker='x', markeredgewidth=3, ms=8)
    
        # Annotate the best score for that scorer
        ax.annotate("%0.2f" % best_score,
                    (X_axis[best_index], best_score + 0.005))
    ax.set_ylim(lowest_y_value, 1)
    plt.legend(loc="best")
    plt.grid(True)
    plt.show()
 
    
def tree_classfier_two_hyperparameter_tuning(X_train, y_train,
                                             cv_folds=10, 
                                             param_grid = {
                                                     'max_depth': range(3, 6, 1),
                                                     'min_samples_leaf': range(20, 101, 20)},                                             
                                             classifier_algo=DecisionTreeClassifier(random_state=100),
                                             refit='Precision',
                                             model_scoring = {'Precision': make_scorer(precision_score),
                                                              'Recall': make_scorer(recall_score), #  'Accuracy': make_scorer(accuracy_score),
                                                              'AUC': make_scorer(roc_auc_score)}
                                             ):
        
    dtree = classifier_algo
    grid_search = GridSearchCV(estimator = dtree, param_grid = param_grid, cv = cv_folds, verbose = 1, refit='Precision', return_train_score=True, scoring=model_scoring)

    # Fit the grid search to the data
    grid_search.fit(X_train,y_train)

    # scores of GridSearch CV
    scores = grid_search.cv_results_

    plot_two_hyperparameter_tuning_result(scores, param_grid, model_scoring)
    
    print("Best score", grid_search.best_score_)
    print("Best Estimator", grid_search.best_estimator_)
    
    return scores
    
def plot_two_hyperparameter_tuning_result(scores, param_grid, model_scoring) :
    
    parameter_list = list(param_grid.keys())
    #for params in param_grid: 
    #    parameter_list = list(params.keys())
    
    outside_hyper_parameter = parameter_list[0]
    inside_hyper_parameter =  parameter_list[1]

    figurewidth=3*len(param_grid[outside_hyper_parameter])
    figureheight = figurewidth*0.75
    plt.figure(figsize=(figurewidth, figureheight))
    
    for n, depth in enumerate(param_grid[outside_hyper_parameter]):
        
        # subplot 1/n
        plt.subplot(1,len(param_grid[outside_hyper_parameter]), n+1)
        
        data_index = scores['param_'+outside_hyper_parameter]==depth
        
        
        
            
        plt.title(outside_hyper_parameter + "-" + str(depth), fontsize=16)
    
        plt.xlabel(inside_hyper_parameter)
        plt.ylabel("Score")
        
        # Get the regular numpy array from the MaskedArray
        x_axis_data = scores['param_'+inside_hyper_parameter].data
        x_axis_data = x_axis_data[data_index]
        X_axis = np.array(x_axis_data, dtype=float)
        
        ax = plt.gca()
        ax.set_xlim(min(X_axis), max(X_axis)+2)
        
        lowest_y_value=1
        
        for scorer, color in zip(sorted(model_scoring), base_color_list[:len(model_scoring)]):
            for sample, style in (('train', '--'), ('test', '-')):
                sample_score_mean = scores['mean_%s_%s' % (sample, scorer)]
                sample_score_mean = sample_score_mean[data_index]
                
                if min(sample_score_mean)<lowest_y_value:
                    lowest_y_value = min(sample_score_mean)
                
                ax.plot(X_axis, sample_score_mean, style, color=color,
                        alpha=1 if sample == 'test' else 0.7,
                        label="%s (%s)" % (scorer, sample))
        
            #best_score_data = scores['rank_test_%s' % scorer]
            #best_score_data = best_score_data[data_index]
            
            #best_index = np.nonzero(best_score_data == min(best_score_data))[0][0]
            #best_score = scores['mean_test_%s' % scorer][best_index]
        
            # Plot a dotted vertical line at the best score for that scorer marked by x
            #ax.plot([X_axis[best_index], ] * 2, [0, best_score],
            #        linestyle='-.', color=color, marker='x', markeredgewidth=3, ms=8)
        
            # Annotate the best score for that scorer
            #ax.annotate("%0.2f" % best_score,
            #            (X_axis[best_index], best_score + 0.005))
        ax.set_ylim(lowest_y_value, 1)
        plt.legend(loc="best")
        plt.grid(True)
    plt.show()
    
def plot_simple_two_hyperparameter_tuning_result(scores, param_grid, scorer='AUC', first_parameter=None, second_parameter=None) :
    
    cv_results = pd.DataFrame(scores)

    parameter_list = list(param_grid.keys())
    if len(parameter_list)>2:
        raise Exception('Only two parameter in grid result supported')

    #for params in param_grid: 
    #    parameter_list = list(params.keys())
    if first_parameter==None:
        param1 = parameter_list[0]
    else:
        param1 = first_parameter
        
    if second_parameter==None:
        param2 =  parameter_list[1]
    else :
        param2 = second_parameter
        
    # plotting
    figurewidth=3*len(param_grid[param1])
    figureheight = figurewidth*0.75
    plt.figure(figsize=(figurewidth,figureheight))
    
    for n, depth in enumerate(param_grid[param1]):
        # subplot 1/n
        plt.subplot(1,len(param_grid[param1]), n+1)
        depth_df = cv_results[cv_results['param_'+param1]==depth]
    
        plt.plot(depth_df["param_"+param2], depth_df["mean_test_"+scorer])
        plt.plot(depth_df["param_"+param2], depth_df["mean_train_"+scorer])
        plt.xlabel(param2)
        plt.ylabel('AUC')
        plt.title(param1+"={0}".format(depth))
        plt.ylim([0.60, 1])
        plt.legend(['test score', 'train score'], loc='best')
        #plt.xscale('log')

def iv_woe(df, columns_to_treat, target_column, value_preference='IV', drop_original_column=False, show_woe=False):
    
    #Empty Dataframe
    iv_df = pd.DataFrame()
    
    #Extract Column Names
    cols = columns_to_treat
    
    #Run WOE and IV on all the independent variables
    for ivars in cols:
        d0 = pd.DataFrame({'x': df[ivars], 'y': df[target_column]})
        d = d0.groupby("x", as_index=False).agg({"y": ["count", "sum"]})
        d.columns = ['Level', 'N', 'Events']
        d['% of Events'] = d['Events'] / d['Events'].sum()
        d['Non-Events'] = d['N'] - d['Events']
        d['% of Non-Events'] = d['Non-Events'] / d['Non-Events'].sum()
        d['WoE'] = np.log(d['% of Events']/d['% of Non-Events'])
        # Todo: What is to be done when you have -inf or +inf (now replace with -1 or 1)
        d=d.replace([-np.inf], -1)
        d=d.replace([np.inf], 1)        
        d['IV'] = d['WoE'] * (d['% of Events'] - d['% of Non-Events'])
        
        print("Information value of " + ivars + " is " + str(round(d['IV'].sum(),6)))
        temp =pd.DataFrame({"Variable" : [ivars], 
                            "IV" : [d['IV'].sum()]}, columns = ["Variable", "IV"])
        iv_df=pd.concat([iv_df,temp], axis=0)

        d.rename(columns={'WoE': ivars+'_WoE'}, inplace=True)
        d.rename(columns={'IV': ivars+'_IV'}, inplace=True)
        d.drop(['N', 'Events', '% of Events', 'Non-Events', '% of Non-Events'], axis=1, inplace=True)
        
        df = pd.merge(df, d, how='left', left_on =ivars, right_on='Level' )
        df.drop(['Level'], axis=1, inplace=True)
        if value_preference=='WoE': # Retain WoE
            df.drop([ivars+'_IV'], axis=1, inplace=True)
        else:
            df.drop([ivars+'_WoE'], axis=1, inplace=True)
        if drop_original_column==True:
            df.drop([ivars], axis=1, inplace=True)

        #Show WOE Table
        if show_woe == True:
            print(d)
    return df, iv_df