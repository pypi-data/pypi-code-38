#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  pca.py
#  Developed in 2019 by Hernan Gelaf-Romer <hernan_gelafromer@student.uml.edu>
#
#  Implements principal component analysis functionality for dfs
#

from ditto_lib.utils.checker import check_package
from ditto_lib.utils.logging import logger
from ditto_lib.utils.dataframe import DataFrame

try: 
    from sklearn.decomposition import PCA
except:
    PCA = None

def pca(df, n_components=None, excluded_attributes=set(), **kwargs):
    '''
    Utlizes the Sklearn PCA, found here: https://scikit-learn.org/stable/modules/generated/sklearn.decomposition.PCA.html
    PCA analysis

    Args:
    df(DataFrame): The dataframe
    excluded_attributes(set): A set of attribute names to exclude. Defaults to the empty set
    n_components(int): Number of components to keep. If set to None, all components are kept. 
        Defaults to None
    **kwargs: Arguments and their descriptions can be found at the scikit-learn Principal Component
        Analysis web page
    '''
    check_package(PCA, 'sklearn', 'pca')
    raw = df.raw(excluded_attributes=excluded_attributes)
    analysis = []
    pca = PCA(**kwargs)
    logger.log('info', "Fitting for PCA")
    pca = pca.fit(raw['values']).explained_variance_ratio_
    logger.log('info', "Done fitting")
    for idx, name in enumerate(raw['attribute_names']):
        logger.log('debug', "Attribute {} with pca explained variance ratio {}".format(name, pca[idx]))
        analysis.append((name, pca[idx]))
    analysis.sort(key=lambda x: x[1], reverse=True)
    logger.log('debug', "Weights generated {}".format(analysis))
    if n_components is not None:
        return analysis[:n_components]
    else:
        return analysis