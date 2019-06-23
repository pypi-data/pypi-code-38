#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  random_forest.py
#  Developed in 2019 by Hernan Gelaf-Romer <hernan_gelafromer@student.uml.edu>
#
#  Implements random forest functionality for dfs
#

from ditto_lib.utils.checker import check_package
from ditto_lib.utils.logging import logger
from ditto_lib.utils.dataframe import DataFrame, Attribute

try: 
    from sklearn.ensemble import RandomForestRegressor, RandomForestClassifier
except:
    RandomForestRegressor = RandomForestClassifier = None

def random_forest_classifier(df, target_attribute, excluded_attributes=set(), n_components=None, **kwargs):
    '''
    Utilizes the Sklearn random forest classifier, found here: hhttps://scikit-learn.org/stable/modules/generated/sklearn.ensemble.RandomForestClassifier.html
    Random Forest Classifier. Returns results in order of most important attributes to least
    important. Results are returned in a list of tuples, where the first item in the tuple is the 
    attribute name, and the second item in the tuple is the attribute importance

    Args:
    df(DataFrame): The dataframe
    target_attribute(str): The name of the target attribute
    excluded_attributes(set): A set of attribute names to exclude. Defaults to the empty set
    n_components(int): How many attributes to return
    **kwargs: Arguments and their descirptions can be found at the scikit-learn RandomForestRegression 
        web page
    '''
    check_package(RandomForestClassifier, 'sklearn', 'random_forest_classifier')
    raw = df.raw(excluded_attributes=excluded_attributes)
    targets = _generate_values(df, target_attribute)
    clf = RandomForestClassifier(**kwargs)
    logger.log('info', "Fitting for random forest classifier")
    clf.fit(raw['values'], targets)
    logger.log('info', "Done fitting")
    results = []
    for idx, name in enumerate(raw['attribute_names']):
        logger.log('debug', "Attribute {} with importance {}".format(name, clf.feature_importances_[idx]))
        results.append((name, clf.feature_importances_[idx]))
    results.sort(key=lambda x: x[1], reverse=True)
    if n_components is not None:
        return results[:n_components]
    else:
        return results

def random_forest_regressor(df, target_attribute, excluded_attributes=set(), n_components=None, **kwargs):
    '''
    Utilizes the Sklearn random forest regressor, found here: https://scikit-learn.org/stable/modules/generated/sklearn.ensemble.RandomForestRegressor.html
    Random Forest Regressor. Returns results in order of most important attributes to least
    important. Results are returned in a list of tuples, where the first item in the tuple is the 
    attribute name, and the second item in the tuple is the attribute importance

    Args:
    df(DataFrame): The dataframe
    target_attribute(str): The name of the target attribute
    excluded_attributes(set): A set of attribute names to exclude. Defaults to the empty set
    n_components(int): How many attributes to return
    **kwargs: Arguments and their descirptions can be found at the scikit-learn RandomForestRegression 
        web page
    '''
    check_package(RandomForestRegressor, 'sklearn', 'random_forest_regressor')
    raw = df.raw(excluded_attributes=excluded_attributes)
    values = raw['values']
    targets = _generate_values(df, target_attribute)
    clf = RandomForestRegressor(**kwargs)
    logger.log('info', "Fitting for random forest regressor")
    clf.fit(values, targets)
    logger.log('info', "Done fitting")
    importances = clf.feature_importances_
    results = []
    for idx, name in enumerate(raw['attribute_names']):
        logger.log('debug', "Attribute {} with importance {}".format(name, importances[idx]))
        results.append((name, importances[idx]))
    results.sort(key=lambda x: x[1], reverse=True)
    if n_components is not None:
        return results[:n_components]
    else:
        return results

def _generate_values(df, name):
    attribute = Attribute(name)
    if attribute not in df.attributes:
        logger.log('error', "Tried to run random forest on non existent attribute {}".format(name))
        raise ValueError("Tried to run random forest on non existent attribute {}".format(name))
    else:
        index = df.attributes.index(attribute)
        values = []
        for item in df.items.values():
            if df.attributes[index].is_descriptor:
                values.append(float(item[index]))
            else:
                values.append(item[index])
        return values