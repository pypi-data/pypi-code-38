#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  outliers.py
#  Developed in 2019 by Hernan Gelaf-Romer <hernan_gelafromer@student.uml.edu>
#
#  Implements outliers functionality for dfs
#

from ditto_lib.utils.checker import check_package
from ditto_lib.utils.logging import logger
from ditto_lib.utils.dataframe import DataFrame
from ditto_lib.utils.scalar import scale, weighted
from ditto_lib.tasks.pca import pca

try:
    from sklearn.neighbors import LocalOutlierFactor
    from sklearn.ensemble import IsolationForest
except:
    LocalOutlierFactor = IsolationForest = None

def local_outlier_factor(df, excluded_attributes=set(), scale_method='standard', weights=None, **kwargs):
        '''
        Utilizes the Sklearn LocalOutlierFactor, found here: https://scikit-learn.org/stable/modules/generated/sklearn.neighbors.LocalOutlierFactor.html
        Return the list of items which are considered outliers.

        Args:
        df(DataFrame): The dataframe
        excluded_attributes(set): A set of attribute names to exclude. Defaults to the empty set
        scale_method(None, 'robust', 'min_max', 'standard', 'max_abs'): A method to scale the data before
            continuing to downstream classifiers. Defaults to standard
        weights(None, 'auto', list): The list of weights if you want to scale the data using weights.
            If 'auto' is selected, generates the data weights for automatically. Defaults to None
        **kwargs: Arguments and their descriptions can be found at the scikit-learn Local Outlier 
            Factor web page
        '''
        check_package(LocalOutlierFactor, 'sklearn', 'detect_outliers')
        raw = _raw_modified(df, scale_method, weights, excluded_attributes)
        outliers = []
        for idx, score in enumerate(LocalOutlierFactor(**kwargs).fit_predict(raw['values'])):
            if score == -1:
                outliers.append(raw['item_names'][idx])
        return outliers

def isolation_forest(df, excluded_attributes=set(), scale_method='standard', weights=None, **kwargs):
    '''
    Utilizes the Sklearn IsolationForest, found here: https://scikit-learn.org/stable/modules/generated/sklearn.ensemble.IsolationForest.html#sklearn.ensemble.IsolationForest
    Return the list of items which are considered outliers.

    Args:
    df(DataFrame): The dataframe
    excluded_attributes(set): A set of attribute names to exclude. Defaults to the empty set
    scale_method(None, 'robust', 'min_max', 'standard', 'max_abs'): A method to scale the data before
        continuing to downstream classifiers. Defaults to standard
    weights(None, 'auto', list): The list of weights if you want to scale the data using weights.
        If 'auto' is selected, generates the data weights for automatically. Defaults to None
    **kwargs: Arguments and their descriptions can be found at the scikit-learn Isolation Forest web page
    '''
    check_package(IsolationForest, 'sklearn', 'isolation_forest')
    raw = _raw_modified(df, scale_method, weights, excluded_attributes)
    clf = IsolationForest(**kwargs)
    logger.log('info', "Fitting for Isolation Forest")
    results = clf.fit_predict(raw['values'])
    logger.log('info', "Done fitting for Isolation Forest")
    outliers = []
    for name, result in zip(raw['item_names'], results):
        if result == -1:
            outliers.append(name)
    return outliers

def isolation_forest_anom(df, excluded_attributes=set(), scale_method='standard', weights=None, **kwargs):
    '''
    Utilizes the Sklearn IsolationForest, found here: https://scikit-learn.org/stable/modules/generated/sklearn.ensemble.IsolationForest.html#sklearn.ensemble.IsolationForest
    Return the list of items which are considered outliers.

    Args:
    df(DataFrame): The dataframe
    excluded_attributes(set): A set of attribute names to exclude. Defaults to the empty set
    scale_method(None, 'robust', 'min_max', 'standard', 'max_abs'): A method to scale the data before
        continuing to downstream classifiers. Defaults to standard
    weights(None, 'auto', list): The list of weights if you want to scale the data using weights.
        If 'auto' is selected, generates the data weights for automatically. Defaults to None
    **kwargs: Arguments and their descriptions can be found at the scikit-learn Isolation Forest web page
    '''
    
    check_package(IsolationForest, 'sklearn', 'isolation_forest')
    raw = _raw_modified(df, scale_method, weights, excluded_attributes)
    clf = IsolationForest(**kwargs)
    logger.log('info', "Fitting for Isolation Forest")
    clf.fit(raw['values'])
    logger.log('info', "Done fitting for Isolation Forest")
    results = clf.decision_function(raw['values'])
    return [(name, result) for name, result in zip(raw['item_names'], results)]

def _raw_modified(df, scale_method, weights, excluded_attributes):
    data = df.raw(excluded_attributes=excluded_attributes)
    if scale_method is not None:
        data['values'] = scale(scale_method, data['values'])
    if weights is not None:
        if weights == 'auto':
            weights = [pair[1] for pair in pca(df, excluded_attributes=excluded_attributes)]
        data['values'] = weighted(data['values'], weights)
    return data