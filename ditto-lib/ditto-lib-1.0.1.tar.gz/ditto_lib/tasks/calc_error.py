#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  calc_error.py
#  Developed in 2019 by Hernan Gelaf-Romer <hernan_gelafromer@student.uml.edu>
#
#  Implements error functionality for dfs
#

from ditto_lib.utils.logging import logger
from ditto_lib.utils.error import error, percent_error
from ditto_lib.utils.dataframe import DataFrame, Attribute

from math import sqrt


def calc_error(df, target_score, actual_score, method='rmse'):
    '''
    Calculates an error value based on the given method for the entire df.

    Args:
    df(DataFrame): The dataframe
    target_score(str): The name of the target score attribute\n
    actual_score(str): The name of the actual score attribute\n
    method('rmse', 'mse'): The error calculation method to use. Defaults
        to rmse
    '''
    target_att = Attribute(target_score)
    actual_att = Attribute(actual_score)
    if target_att not in df.attributes or actual_att not in df.attributes:
        logger.log('error', "{} or {} not in df {}".format(
            target_score, actual_score, df.name))
        raise ValueError("{} or {} not in df {}".format(
            target_score, actual_score, df.name))
    target_scores = []
    actual_scores = []
    for item in df.items.values():
        target_scores.append(
            float(item[df.attributes.index(target_att)]))
        actual_scores.append(
            float(item[df.attributes.index(actual_att)]))
    logger.log('debug', "Actual scores generated {}".format(actual_scores))
    logger.log('debug', "Target scores generated {}".format(target_scores))
    if method == 'rmse':
        return sqrt(error('mse', actual_score, target_score))
    else:
        return error(method, actual_scores, target_scores)


def generate_error(df, name, target_score, actual_score):
    '''
    Generate the percent error of one attribute compared to another
    attribute for every item in the df.
    
    Args:
    df(DataFrame): The dataframe
    target_score(str): The name of the target score attribute\n
    actual_score(str): The name of the actual score attribute\n
    method('rmse', 'mse'): The error calculation method to use. Defaults
        to rmse
    '''
    target_att = Attribute(target_score)
    actual_att = Attribute(actual_score)
    if target_att not in df.attributes or actual_att not in df.attributes:
        logger.log('error', "{} or {} not in df {}".format(
            target_score, actual_score, df.name))
        raise ValueError("{} or {} not in df {}".format(
            target_score, actual_score, df.name))
    df.attributes.add(Attribute(name, False))
    for item_name, item in df.items.items():
        target = float(item[df.attributes.index(target_att)])
        actual = float(item[df.attributes.index(actual_att)])
        error = percent_error(actual, target)
        item.append(error)
        logger.log('debug', "Percent error: {}, found between target score \
            {} and actual score {} for item {}".format(error,target_score, actual_score, item_name))