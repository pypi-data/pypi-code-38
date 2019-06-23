#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  calc_similarity.py
#  Developed in 2019 by Hernan Gelaf-Romer <hernan_gelafromer@student.uml.edu>
#
#  Implements similarity functionality for dfs
#

from ditto_lib.utils.logging import logger
from ditto_lib.utils.error import error
from ditto_lib.utils.similarity import similarity
from ditto_lib.utils.scalar import scale
from ditto_lib.utils.dataframe import DataFrame
from ditto_lib.tasks.pca import pca

def calc_similarity(df, first_item, second_item, excluded_attributes=set(), method='euc', scale_method='standard', weights=None):
    '''
    Calculate the similarity between two items in a df

    Args:
    df(DataFrame): The dataframe
    first_item(str): The name of the first item
    second_item(str): The name of the second item
    excluded_attributes(set): A set of attribute names to exclude. Defaults to the empty set
    method('euc', 'man', 'jac', cos'): The method used to calculate similarity. Defaults
        to 'euc'
    weights(None, 'auto', list): The list of weights if you want to scale the data using weights.
            If 'auto' is selected, generates the data weights for automatically. Defaults to None
    scale_method(None, 'min_max', 'standard', 'max_abs'): The method used to scale the 
        data before calculating the similarity. Defaults to 'standard'
    '''
    if first_item not in df.items or second_item not in df.items:
        logger.log('error', "Could not find {} or {} in {}".format(
            first_item, second_item, df.name))
        raise ValueError("Could not find {} or {} in {}".format(
            first_item, second_item, df.name))
    else:
        first_item = df.item(first_item)
        second_item = df.item(second_item)
        first_values = []
        second_values = []
        for index, attribute in enumerate(df.attributes):
            if attribute.is_descriptor and attribute.name not in excluded_attributes:
                first_values.append(float(first_item[index]))
                second_values.append(float(second_item[index]))
        if scale_method is not None:
            if weights == 'auto':
                weights = [pair[1] for pair in pca(df)]
            scaled_values = scale(scale_method, [first_values, second_values], weights=weights)
            first_values = scaled_values[0]
            second_values = scaled_values[1]
        logger.log('debug', "first_values {}, second_values {}".format(
            first_values, second_values))
        return similarity(method, first_values, second_values)

def calc_all_similarities(df, item_name, excluded_attributes=set(), method='euc', scale_method='standard', weights=None, descending=True):
    '''
    Args:
    df(DataFrame): The dataframe
    first_item(str): The name of the first item
    excluded_attributes(set): A set of attribute names to exclude. Defaults to the empty set
    method('euc', 'man', 'jac', cos'): The method used to calculate similarity. Defaults
        to 'euc'
    weights(None, 'auto', list): The list of weights if you want to scale the data using weights.
            If 'auto' is selected, generates the data weights for automatically. Defaults to None
    scale_method(None, 'min_max', 'standard', 'max_abs'): The method used to scale the 
        data before calculating the similarity. Defaults to 'standard'
    descending(bool): Retrieve items in descending order based on their similarity scores, defaults
        to True
    '''
    if item_name not in df.items:
        logger.log('error', "Could not find item {} in {}".format(
            item_name, df.name))
        raise ValueError("Could not find item {} in {}".format(
            item_name, df.name))
    else:
        if weights is not None:
            weights = [pair[1] for pair in pca(df, excluded_attributes=excluded_attributes)]
        results = []
        for name in df.items.keys():
            if item_name != name:
                results.append(
                    (name, calc_similarity(df, item_name, name, method=method, 
                        excluded_attributes=excluded_attributes, scale_method=scale_method, weights=weights)))
        results.sort(key=lambda x: x[1], reverse=descending)
        return results
