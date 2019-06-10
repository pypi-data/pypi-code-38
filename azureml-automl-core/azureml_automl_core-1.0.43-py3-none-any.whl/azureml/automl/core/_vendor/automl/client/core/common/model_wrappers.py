# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""Module to wrap models that don't accept parameters such as 'fraction of the dataset'."""
from typing import Any, Dict, List, Optional, Tuple, Union, cast
from abc import ABC, abstractmethod
import importlib
import os
import pickle
import warnings

import lightgbm as lgb
import numpy as np
import pandas as pd
import scipy
import sklearn
import sklearn.decomposition
import sklearn.naive_bayes
import sklearn.pipeline
from scipy.special import inv_boxcox
from scipy.stats import norm, boxcox
from sklearn import preprocessing
from sklearn.utils.metaestimators import _BaseComposition
from sklearn.base import (BaseEstimator, ClassifierMixin, RegressorMixin,
                          TransformerMixin, clone)
from sklearn.calibration import CalibratedClassifierCV
from sklearn.decomposition import TruncatedSVD
from sklearn.ensemble import VotingClassifier
from sklearn.model_selection import train_test_split, StratifiedKFold, KFold
from sklearn.preprocessing import LabelEncoder, Normalizer
from sklearn.pipeline import Pipeline as SKPipeline
from pandas.tseries.frequencies import to_offset

import automl.client.core.common
from automl.client.core.common import constants
from automl.client.core.common import metrics
from automl.client.core.common import metrics_utilities as metrics_utils
from automl.client.core.common import time_series_data_frame as tsdf
from automl.client.core.common.exceptions import ConfigException
from automl.client.core.common.exceptions import DataException
from automl.client.core.common.types import DataInputType
from automl.client.core.common.constants import TimeSeriesInternal
from automl.client.core.common.time_series_data_frame import TimeSeriesDataFrame

try:
    import xgboost as xgb

    xgboost_present = True
except ImportError:
    xgboost_present = False


class _AbstractModelWrapper(ABC):
    """Abstract base class for the model wrappers."""

    def __init__(self):
        """Initialize AbstractModelWrapper class."""
        pass

    @abstractmethod
    def get_model(self):
        """
        Abstract method for getting the inner original model object.

        :return: An inner model object.
        """
        raise NotImplementedError


class LightGBMClassifier(BaseEstimator, ClassifierMixin, _AbstractModelWrapper):
    """
    LightGBM Classifier class.

    :param random_state:
        RandomState instance or None, optional (default=None)
        If int, random_state is the seed used by the random number generator;
        If RandomState instance, random_state is the random number generator;
        If None, the random number generator is the RandomState instance used
        by `np.random`.
    :type random_state: int or RandomState
    :param n_jobs: Number of parallel threads.
    :type n_jobs: int
    :param kwargs: Other parameters
        Check http://lightgbm.readthedocs.io/en/latest/Parameters.html
        for more parameters.
    """

    DEFAULT_MIN_DATA_IN_LEAF = 20

    def __init__(self, random_state=None, n_jobs=1, categorical_feature=None, **kwargs):
        """
        Initialize LightGBM Classifier class.

        :param random_state:
            RandomState instance or None, optional (default=None)
            If int, random_state is the seed used by the random number
            generator.
            If RandomState instance, random_state is the random number
            generator.
            If None, the random number generator is the RandomState instance
            used by `np.random`.
        :type random_state: int or RandomState
        :param n_jobs: Number of parallel threads.
        :type n_jobs: int
        :param categorical_feature: Indicies of the categorical columns.
        :param categorical_feature: np.ndarray
        :param kwargs: Other parameters
            Check http://lightgbm.readthedocs.io/en/latest/Parameters.html
            for more parameters.
        """
        self.params = kwargs
        self.params['random_state'] = random_state
        self.params['n_jobs'] = n_jobs
        self.model = None           # type: Optional[BaseEstimator]
        self._min_data_str = "min_data_in_leaf"
        self._min_child_samples = "min_child_samples"
        self._categoricals = categorical_feature

        if self._min_data_str not in kwargs and \
                self._min_child_samples not in kwargs:
            raise ValueError("neither min_data_in_leaf nor min_child_samples passed")

    def get_model(self):
        """
        Return LightGBM Classifier model.

        :return: Returns the fitted model if fit method has been called.
        Else returns None.
        """
        return self.model

    def fit(self, X: np.ndarray, y: np.ndarray, **kwargs: Any) -> "LightGBMClassifier":
        """
        Fit function for LightGBM Classifier model.

        :param X: Input data.
        :param y: Input target values.
        :param kwargs: other parameters
            Check http://lightgbm.readthedocs.io/en/latest/Parameters.html
            for more parameters.
        :return: Self after fitting the model.
        """
        N = X.shape[0]
        args = dict(self.params)
        if (self._min_data_str in args):
            if (self.params[self._min_data_str] ==
                    LightGBMClassifier.DEFAULT_MIN_DATA_IN_LEAF):
                args[self._min_child_samples] = self.params[
                    self._min_data_str]
            else:
                args[self._min_child_samples] = int(
                    self.params[self._min_data_str] * N) + 1
            del args[self._min_data_str]
        else:
            min_child_samples = self.params[self._min_child_samples]
            if min_child_samples > 0 and min_child_samples < 1:
                # we'll convert from fraction to int as that's what LightGBM expects
                args[self._min_child_samples] = int(
                    self.params[self._min_child_samples] * N) + 1
            else:
                args[self._min_child_samples] = min_child_samples

        verbose_str = "verbose"
        if verbose_str not in args:
            args[verbose_str] = -10

        if self._categoricals is not None:
            kwargs['categorical_feature'] = self._categoricals.tolist()

        self.model = lgb.LGBMClassifier(**args)
        self.model.fit(X, y, **kwargs)
        self.classes_ = np.unique(y)

        return self

    def get_params(self, deep: bool = True) -> Dict[str, Any]:
        """
        Return parameters for LightGBM Classifier model.

        :param deep:
                If True, will return the parameters for this estimator
                and contained subobjects that are estimators.
        :type deep: boolean
        :return: Parameters for the LightGBM classifier model.
        """
        params = {}
        params['random_state'] = self.params['random_state']
        params['n_jobs'] = self.params['n_jobs']
        if self.model:
            params.update(self.model.get_params(deep))
        else:
            params.update(self.params)

        return params

    def predict(self, X):
        """
        Prediction function for LightGBM Classifier model.

        :param X: Input data.
        :type X: numpy.ndarray
        :return: Prediction values from LightGBM Classifier model.
        """
        return self.model.predict(X)

    def predict_proba(self, X):
        """
        Prediction class probabilities for X for LightGBM Classifier model.

        :param X: Input data.
        :type X: numpy.ndarray
        :return: Prediction probability values from LightGBM Classifier model.
        """
        return self.model.predict_proba(X)


class XGBoostClassifier(BaseEstimator, ClassifierMixin, _AbstractModelWrapper):
    """
    XGBoost Classifier class.

    :param random_state:
        RandomState instance or None, optional (default=None)
        If int, random_state is the seed used by the random number generator;
        If RandomState instance, random_state is the random number generator;
        If None, the random number generator is the RandomState instance used
        by `np.random`.
    :type random_state: int or RandomState
    :param n_jobs: Number of parallel threads.
    :type n_jobs: int
    :param kwargs: Other parameters
        Check https://xgboost.readthedocs.io/en/latest/parameter.html
        for more parameters.
    """

    def __init__(self, random_state=0, n_jobs=1, **kwargs):
        """
        Initialize XGBoost Classifier class.

        :param random_state:
            RandomState instance or None, optional (default=None)
            If int, random_state is the seed used by the random number
            generator.
            If RandomState instance, random_state is the random number
            generator.
            If None, the random number generator is the RandomState instance
            used by `np.random`.
        :type random_state: int or RandomState
        :param n_jobs: Number of parallel threads.
        :type n_jobs: int
        :param kwargs: Other parameters
            Check https://xgboost.readthedocs.io/en/latest/parameter.html
            for more parameters.
        """
        self.params = kwargs
        self.params['random_state'] = random_state if random_state is not None else 0
        self.params['n_jobs'] = n_jobs
        self.model = None
        self.classes_ = None
        if not xgboost_present:
            raise ConfigException("xgboost not installed, please install xgboost for including xgboost based models")

    def get_model(self):
        """
        Return XGBoost Classifier model.

        :return: Returns the fitted model if fit method has been called.
        Else returns None.
        """
        return self.model

    def fit(self, X, y, **kwargs):
        """
        Fit function for XGBoost Classifier model.

        :param X: Input data.
        :type X: numpy.ndarray
        :param y: Input target values.
        :type y: numpy.ndarray
        :param kwargs: other parameters
            Check https://xgboost.readthedocs.io/en/latest/parameter.html
            for more parameters.
        :return: Self after fitting the model.
        """
        args = dict(self.params)
        verbose_str = "verbose"
        if verbose_str not in args:
            args[verbose_str] = -10

        self.model = xgb.XGBClassifier(**args)
        self.model.fit(X, y, **kwargs)
        self.classes_ = np.unique(y)

        return self

    def get_params(self, deep=True):
        """
        Return parameters for XGBoost Classifier model.

        :param deep: If True, will return the parameters for this estimator and contained subobjects that are
            estimators.
        :type deep: boolean
        :return: Parameters for the XGBoost classifier model.
        """
        if self.model:
            return self.model.get_params(deep)
        else:
            return self.params

    def predict(self, X):
        """
        Prediction function for XGBoost Classifier model.

        :param X: Input data.
        :type X: numpy.ndarray
        :return: Prediction values from XGBoost Classifier model.
        """
        if self.model is None:
            raise sklearn.exceptions.NotFittedError()
        return self.model.predict(X)

    def predict_proba(self, X):
        """
        Prediction class probabilities for X for XGBoost Classifier model.

        :param X: Input data.
        :type X: numpy.ndarray
        :return: Prediction probability values from XGBoost Classifier model.
        """
        if self.model is None:
            raise sklearn.exceptions.NotFittedError()
        return self.model.predict_proba(X)


class SparseNormalizer(TransformerMixin, _AbstractModelWrapper):
    """
    Normalizes rows of an input matrix. Supports sparse matrices.

    :param norm:
        Type of normalization to perform - l1’, ‘l2’, or ‘max’,
        optional (‘l2’ by default).
    :type norm: str
    """

    def __init__(self, norm="l2", copy=True):
        """
        Initialize function for Sparse Normalizer transformer.

        :param norm:
            Type of normalization to perform - l1’, ‘l2’, or ‘max’,
            optional (‘l2’ by default).
        :type norm: str
        """
        self.norm = norm
        self.norm_str = "norm"
        self.model = Normalizer(norm, copy=True)

    def get_model(self):
        """
        Return Sparse Normalizer model.

        :return: Sparse Normalizer model.
        """
        return self.model

    def fit(self, X, y=None):
        """
        Fit function for Sparse Normalizer model.

        :param X: Input data.
        :type X: numpy.ndarray
        :param y: Input target values.
        :type y: numpy.ndarray
        :return: Returns self.
        """
        return self

    def get_params(self, deep=True):
        """
        Return parameters for Sparse Normalizer model.

        :param deep:
            If True, will return the parameters for this estimator
            and contained subobjects that are estimators.
        :return: Parameters for Sparse Normalizer model.
        """
        params = {self.norm_str: self.norm}
        if self.model:
            params.update(self.model.get_params(deep))

        return params

    def transform(self, X):
        """
        Transform function for Sparse Normalizer model.

        :param X: Input data.
        :type X: numpy.ndarray
        :return: Transformed output of Sparse Normalizer.
        """
        return self.model.transform(X)


class SparseScaleZeroOne(BaseEstimator, TransformerMixin, _AbstractModelWrapper):
    """Transforms the input data by appending previous rows."""

    def __init__(self):
        """Initialize Sparse Scale Transformer."""
        self.scaler = None
        self.model = None

    def get_model(self):
        """
        Return Sparse Scale model.

        :return: Sparse Scale model.
        """
        return self.model

    def fit(self, X, y=None):
        """
        Fit function for Sparse Scale model.

        :param X: Input data.
        :type X: scipy.spmatrix
        :param y: Input target values.
        :type y: numpy.ndarray
        :return: Returns self after fitting the model.
        """
        self.model = sklearn.preprocessing.MaxAbsScaler()
        self.model.fit(X)
        return self

    def transform(self, X):
        """
        Transform function for Sparse Scale model.

        :param X: Input data.
        :type X: scipy.spmatrix
        :return: Transformed output of MaxAbsScaler.
        """
        if self.model is None:
            raise sklearn.exceptions.NotFittedError()
        X = self.model.transform(X)
        X.data = (X.data + 1) / 2
        return X

    def get_params(self, deep=True):
        """
        Return parameters for Sparse Scale model.

        :param deep:
            If True, will return the parameters for this estimator
            and contained subobjects that are estimators.
        :type deep: boolean
        :return: Parameters for Sparse Scale model.
        """
        return {}


class PreprocWrapper(TransformerMixin, _AbstractModelWrapper):
    """Normalizes rows of an input matrix. Supports sparse matrices."""

    def __init__(self, cls, module_name=None, class_name=None, **kwargs):
        """
        Initialize PreprocWrapper class.

        :param cls:
        :param kwargs:
        """
        self.cls = cls
        if cls is not None:
            self.module_name = cls.__module__
            self.class_name = cls.__name__
        else:
            self.module_name = module_name
            self.class_name = class_name

        self.args = kwargs
        self.model = None

    def get_model(self):
        """
        Return wrapper model.

        :return: wrapper model
        """
        return self.model

    def fit(self, X, y=None):
        """
        Fit function for PreprocWrapper.

        :param X: Input data.
        :type X: numpy.ndarray or scipy.spmatrix
        :param y: Ignored.
        :type y: numpy.ndarray
        :return: Returns an instance of self.
        """
        args = dict(self.args)
        if self.cls is not None:
            self.model = self.cls(**args)
        else:
            assert self.module_name is not None
            assert self.class_name is not None
            mod = importlib.import_module(self.module_name)
            self.cls = getattr(mod, self.class_name)

        self.model.fit(X)
        return self

    def get_params(self, deep=True):
        """
        Return parameters for PreprocWrapper.

        :param deep:
            If True, will return the parameters for this estimator
            and contained subobjects that are estimators.
        :type deep: boolean
        :return: Parameters for PreprocWrapper.
        """
        # using the cls field instead of class_name & class_name because these fields might not be set
        # when this instance is created through unpickling
        params = {'module_name': self.cls.__module__, 'class_name': self.cls.__name__}
        if self.model:
            params.update(self.model.get_params(deep))
        else:
            params.update(self.args)

        return params

    def transform(self, X):
        """
        Transform function for PreprocWrapper.

        :param X: Input data.
        :type X: numpy.ndarray or scipy.spmatrix
        :return: Transformed output of inner model.
        """
        return self.model.transform(X)

    def inverse_transform(self, X):
        """
        Inverse transform function for PreprocWrapper.

        :param X: New data.
        :type X: numpy.ndarray or scipy.spmatrix
        :return: Inverse transformed data.
        """
        return self.model.inverse_transform(X)


class StandardScalerWrapper(PreprocWrapper):
    """Standard Scaler Wrapper around StandardScaler transformation."""

    def __init__(self, **kwargs):
        """Initialize Standard Scaler Wrapper class."""
        super().__init__(sklearn.preprocessing.StandardScaler,
                         **kwargs)


class NBWrapper(BaseEstimator, ClassifierMixin, _AbstractModelWrapper):
    """Naive Bayes Wrapper for conditional probabilities using either Bernoulli or Multinomial models."""

    def __init__(self, model, **kwargs):
        """
        Initialize Naive Bayes Wrapper class with either Bernoulli or Multinomial models.

        :param model: The actual model name.
        :type model: str
        """
        assert model in ['Bernoulli', 'Multinomial']
        self.model_name = model
        self.args = kwargs
        self.model = None

    def get_model(self):
        """
        Return Naive Bayes model.

        :return: Naive Bayes model.
        """
        return self.model

    def fit(self, X, y, **kwargs):
        """
        Fit function for Naive Bayes model.

        :param X: Input data.
        :type X: numpy.ndarray or scipy.spmatrix
        :param y: Input target values.
        :type y: numpy.ndarray
        :param kwargs: Other arguments.
        """
        if self.model_name == 'Bernoulli':
            base_clf = sklearn.naive_bayes.BernoulliNB(**self.args)
        elif self.model_name == 'Multinomial':
            base_clf = sklearn.naive_bayes.MultinomialNB(**self.args)
        model = base_clf
        is_sparse = scipy.sparse.issparse(X)
        # sparse matrix with negative cells
        if is_sparse and np.any(X < 0).max():
            clf = sklearn.pipeline.Pipeline(
                [('MinMax scaler', SparseScaleZeroOne()),
                 (self.model_name + 'NB', base_clf)])
            model = clf
        # regular matrix with negative cells
        elif not is_sparse and np.any(X < 0):
            clf = sklearn.pipeline.Pipeline(
                [('MinMax scaler',
                  sklearn.preprocessing.MinMaxScaler(
                      feature_range=(0, X.max()))),
                 (self.model_name + 'NB', base_clf)])
            model = clf

        self.model = model
        self.model.fit(X, y, **kwargs)
        if hasattr(self.model, "classes_"):
            self.classes_ = self.model.classes_
        else:
            self.classes_ = np.unique(y)

    def get_params(self, deep=True):
        """
        Return parameters for Naive Bayes model.

        :param deep:
            If True, will return the parameters for this estimator
            and contained subobjects that are estimators.
        :type deep: boolean
        :return: Parameters for Naive Bayes model.
        """
        params = {'model': self.model_name}
        if self.model:
            if isinstance(self.model, sklearn.pipeline.Pipeline):
                # we just want to get the parameters of the final estimator, excluding the preprocessors
                params.update(self.model._final_estimator.get_params(deep))
            else:
                params.update(self.model.get_params(deep))
        else:
            params.update(self.args)

        return params

    def predict(self, X):
        """
        Prediction function for Naive Bayes Wrapper Model.

        :param X: Input samples.
        :type X: numpy.ndarray or scipy.spmatrix
        :return: Prediction values from actual Naive Bayes model.
        """
        if self.model is None:
            raise sklearn.exceptions.NotFittedError()
        return self.model.predict(X)

    def predict_proba(self, X):
        """
        Prediction class probabilities for X for Naive Bayes Wrapper model.

        :param X: Input samples.
        :type X: numpy.ndarray or scipy.spmatrix
        :return: Prediction probability values from actual Naive Bayes model.
        """
        if self.model is None:
            raise sklearn.exceptions.NotFittedError()
        return self.model.predict_proba(X)


class TruncatedSVDWrapper(BaseEstimator, TransformerMixin, _AbstractModelWrapper):
    """
    Wrapper around Truncated SVD so that we only have to pass a fraction of dimensions.

    Read more at http://scikit-learn.org/stable/modules/generated/sklearn.decomposition.TruncatedSVD.html

    :param min_components: Min number of desired dimensionality of output data.
    :type min_components: int
    :param max_components: Max number of desired dimensionality of output data.
    :type max_components: int
    :param random_state: RandomState instance or None, optional, default = None
        If int, random_state is the seed used by the random number generator;
        If RandomState instance, random_state is the random number generator;
        If None, the random number generator is the RandomState instance used
        by np.random.
    :type random_state: int or RandomState
    :param kwargs: Other args taken by sklearn TruncatedSVD.
    """

    def __init__(
            self,
            min_components=2,
            max_components=200,
            random_state=None,
            **kwargs):
        """
        Initialize Truncated SVD Wrapper Model.

        :param min_components:
            Min number of desired dimensionality of output data.
        :type min_components: int
        :param max_components:
            Max number of desired dimensionality of output data.
        :type max_components: int
        :param random_state:
            RandomState instance or None, optional, default = None
            If int, random_state is the seed used by the random number
            generator;
            If RandomState instance, random_state is the random number
            generator;
            If None, the random number generator is the RandomState instance
            used by np.random.
        :type random_state: int or RandomState
        :param kwargs: Other args taken by sklearn TruncatedSVD.
        :return:
        """
        self._min_components = min_components
        self._max_components = max_components
        self.args = kwargs
        self.args['random_state'] = random_state

        self.n_components_str = "n_components"
        if self.n_components_str not in self.args:
            raise ValueError("n_components not passed")
        self.model = None

    def get_model(self):
        """
        Return sklearn Truncated SVD Model.

        :return: Truncated SVD Model.
        """
        return self.model

    def fit(self, X, y=None):
        """
        Fit function for Truncated SVD Wrapper Model.

        :param X: Input data.
        :type X: numpy.ndarray or scipy.spmatrix
        :param y: Ignored.
        :return: Returns an instance of self.
        :rtype: TruncatedSVDWrapper
        """
        args = dict(self.args)
        args[self.n_components_str] = min(
            self._max_components,
            max(self._min_components,
                int(self.args[self.n_components_str] * X.shape[1])))
        self.model = TruncatedSVD(**args)
        self.model.fit(X)

        return self

    def get_params(self, deep=True):
        """
        Return parameters for Truncated SVD Wrapper Model.

        :param deep:
            If True, will return the parameters for this estimator
            and contained subobjects that are estimators.
        :type deep: boolean
        :return: Parameters for Truncated SVD Wrapper Model.
        """
        params = {}
        params['min_components'] = self._min_components
        params['max_components'] = self._max_components
        params['random_state'] = self.args['random_state']
        if self.model:
            params.update(self.model.get_params(deep=deep))
        else:
            params.update(self.args)

        return self.args

    def transform(self, X):
        """
        Transform function for Truncated SVD Wrapper Model.

        :param X: Input data.
        :type X: numpy.ndarray or scipy.spmatrix
        :return: Transformed data of reduced version of X.
        :rtype: array
        """
        return self.model.transform(X)

    def inverse_transform(self, X):
        """
        Inverse Transform function for Truncated SVD Wrapper Model.

        :param X: New data.
        :type X: numpy.ndarray
        :return: Inverse transformed data. Always a dense array.
        :rtype: array
        """
        return self.model.inverse_transform(X)


class SVCWrapper(BaseEstimator, ClassifierMixin, _AbstractModelWrapper):
    """
    Wrapper around svm.SVC that always sets probability to True.

    Read more at:
    http://scikit-learn.org/stable/modules/generated/sklearn.svm.SVC.html.

    :param random_state: RandomState instance or None, optional, default = None
        If int, random_state is the seed used by the random number generator;
        If RandomState instance, random_state is the random number generator;
        If None, the random number generator is the RandomState instance used
        by np.random.
    :type random_state: int or RandomState
    :param: kwargs: Other args taken by sklearn SVC.
    """

    def __init__(self, random_state=None, **kwargs):
        """
        Initialize svm.SVC Wrapper Model.

        :param random_state:
            RandomState instance or None, optional, default = None
            If int, random_state is the seed used by the random number
            generator;
            If RandomState instance, random_state is the random number
            generator;
            If None, the random number generator is the RandomState instance
            used by np.random.
        :type random_state: int or RandomState
        :param: kwargs: Other args taken by sklearn SVC.
        """
        kwargs["probability"] = True
        self.args = kwargs
        self.args['random_state'] = random_state
        self.model = sklearn.svm.SVC(**self.args)

    def get_model(self):
        """
        Return sklearn.svm.SVC Model.

        :return: The svm.SVC Model.
        """
        return self.model

    def fit(self, X, y, **kwargs):
        """
        Fit function for svm.SVC Wrapper Model.

        :param X: Input data.
        :type X: numpy.ndarray or scipy.spmatrix
        :param y: Input target values.
        :type y: numpy.ndarray
        """
        self.model.fit(X, y, **kwargs)
        if hasattr(self.model, "classes_"):
            self.classes_ = self.model.classes_
        else:
            self.classes_ = np.unique(y)

    def get_params(self, deep=True):
        """
        Return parameters for svm.SVC Wrapper Model.

        :param deep:
            If True, will return the parameters for this estimator
            and contained subobjects that are estimators.
        :type deep: boolean
        :return: parameters for svm.SVC Wrapper Model.
        """
        params = {'random_state': self.args['random_state']}
        params.update(self.model.get_params(deep=deep))

        return params

    def predict(self, X):
        """
        Prediction function for svm.SVC Wrapper Model. Perform classification on samples in X.

        :param X: Input samples.
        :type X: numpy.ndarray or scipy.spmatrix
        :return: Prediction values from svm.SVC model.
        :rtype: array
        """
        return self.model.predict(X)

    def predict_proba(self, X):
        """
        Prediction class probabilities for X for svm.SVC Wrapper model.

        :param X: Input samples.
        :type X: numpy.ndarray
        :return: Prediction probabilities values from svm.SVC model.
        :rtype: array
        """
        return self.model.predict_proba(X)


class NuSVCWrapper(BaseEstimator, ClassifierMixin, _AbstractModelWrapper):
    """
    Wrapper around svm.NuSVC that always sets probability to True.

    Read more at:
    http://scikit-learn.org/stable/modules/generated/sklearn.svm.NuSVC.html.

    :param random_state: RandomState instance or None, optional, default = None
        If int, random_state is the seed used by the random number generator;
        If RandomState instance, random_state is the random number generator;
        If None, the random number generator is the RandomState instance used
        by np.random.
    :type random_state: int or RandomState
    :param: kwargs: Other args taken by sklearn NuSVC.
    """

    def __init__(self, random_state=None, **kwargs):
        """
        Initialize svm.NuSVC Wrapper Model.

        :param random_state: RandomState instance or None, optional,
        default = None
            If int, random_state is the seed used by the random number
            generator;
            If RandomState instance, random_state is the random number
            generator;
            If None, the random number generator is the RandomState instance
            used by np.random.
        :type random_state: int or RandomState
        :param: kwargs: Other args taken by sklearn NuSVC.
        """
        kwargs["probability"] = True
        self.args = kwargs
        self.args['random_state'] = random_state
        self.model = sklearn.svm.NuSVC(**self.args)

    def get_model(self):
        """
        Return sklearn svm.NuSVC Model.

        :return: The svm.NuSVC Model.
        """
        return self.model

    def fit(self, X, y, **kwargs):
        """
        Fit function for svm.NuSVC Wrapper Model.

        :param X: Input data.
        :type X: numpy.ndarray or scipy.spmatrix
        :param y: Input target values.
        :type y: numpy.ndarray
        """
        self.model.fit(X, y, **kwargs)
        if hasattr(self.model, "classes_"):
            self.classes_ = self.model.classes_
        else:
            self.classes_ = np.unique(y)

    def get_params(self, deep=True):
        """
        Return parameters for svm.NuSVC Wrapper Model.

        :param deep:
            If True, will return the parameters for this estimator
            and contained subobjects that are estimators.
        :type deep: boolean
        :return: Parameters for svm.NuSVC Wrapper Model.
        """
        params = {'random_state': self.args['random_state']}
        params.update(self.model.get_params(deep=deep))
        return params

    def predict(self, X):
        """
        Prediction function for svm.NuSVC Wrapper Model. Perform classification on samples in X.

        :param X: Input samples.
        :type X: numpy.ndarray or scipy.spmatrix
        :return: Prediction values from svm.NuSVC model.
        :rtype: array
        """
        return self.model.predict(X)

    def predict_proba(self, X):
        """
        Prediction class probabilities for X for svm.NuSVC Wrapper model.

        :param X: Input samples.
        :type X: numpy.ndarray
        :return: Prediction probabilities values from svm.NuSVC model.
        :rtype: array
        """
        return self.model.predict_proba(X)


class SGDClassifierWrapper(BaseEstimator, ClassifierMixin, _AbstractModelWrapper):
    """
    SGD Classifier Wrapper Class.

    Wrapper around SGD Classifier to support predict probabilities on loss
    functions other than log loss and modified huber loss. This breaks
    partial_fit on loss functions other than log and modified_huber since the
    calibrated model does not support partial_fit.

    Read more at:
    http://scikit-learn.org/stable/modules/generated/sklearn.linear_model.SGDClassifier.html.
    """

    def __init__(self, random_state=None, n_jobs=1, **kwargs):
        """
        Initialize SGD Classifier Wrapper Model.

        :param random_state:
            RandomState instance or None, optional (default=None)
            If int, random_state is the seed used by the random number
            generator;
            If RandomState instance, random_state is the random number
            generator;
            If None, the random number generator is the RandomState
            instance used
            by `np.random`.
        :type random_state: int or RandomState
        :param n_jobs: Number of parallel threads.
        :type n_jobs: int
        :param kwargs: Other parameters.
        """
        self.loss = "loss"
        self.model = None
        self._calibrated = False

        self.args = kwargs
        self.args['random_state'] = random_state
        self.args['n_jobs'] = n_jobs
        loss_arg = kwargs.get(self.loss, None)
        if loss_arg in ["log", "modified_huber"]:
            self.model = sklearn.linear_model.SGDClassifier(**self.args)
        else:
            self.model = CalibratedModel(
                sklearn.linear_model.SGDClassifier(**self.args), random_state)
            self._calibrated = True

    def get_model(self):
        """
        Return SGD Classifier Wrapper Model.

        :return: Returns the fitted model if fit method has been called.
        Else returns None
        """
        return self.model

    def fit(self, X, y, **kwargs):
        """
        Fit function for SGD Classifier Wrapper Model.

        :param X: Input data.
        :type X: numpy.ndarray
        :param y: Input target values.
        :type y: numpy.ndarray
        :param kwargs: Other parameters.
        :return: Returns an instance of inner SGDClassifier model.
        """
        model = self.model.fit(X, y, **kwargs)
        if hasattr(model, "classes_"):
            self.classes_ = model.classes_
        else:
            self.classes_ = np.unique(y)

        return model

    def get_params(self, deep=True):
        """
        Return parameters for SGD Classifier Wrapper Model.

        :param deep:
            If True, will return the parameters for this estimator
            and contained subobjects that are estimators.
        :type deep: bool
        :return: parameters for SGD Classifier Wrapper Model.
        """
        params = {}
        params['random_state'] = self.args['random_state']
        params['n_jobs'] = self.args['n_jobs']
        params.update(self.model.get_params(deep=deep))
        return self.args

    def predict(self, X):
        """
        Prediction function for SGD Classifier Wrapper Model.

        :param X: Input data.
        :type X: numpy.ndarray
        :return: Prediction values from SGD Classifier Wrapper model.
        """
        return self.model.predict(X)

    def predict_proba(self, X):
        """
        Prediction class probabilities for X for SGD Classifier Wrapper model.

        :param X: Input data.
        :type X: numpy.ndarray
        :return:
            Prediction probability values from SGD Classifier Wrapper model.
        """
        return self.model.predict_proba(X)

    def partial_fit(self, X, y, **kwargs):
        """
        Return partial fit result.

        :param X: Input data.
        :type X: numpy.ndarray
        :param y: Input target values.
        :type y: numpy.ndarray
        :param kwargs: Other parameters.
        :return: Returns an instance of inner SGDClassifier model.
        """
        if self._calibrated:
            raise ValueError("Calibrated model used")

        return self.model.partial_fit(X, y, **kwargs)


class EnsembleWrapper(BaseEstimator, ClassifierMixin):
    """Wrapper around multiple pipelines that combine predictions."""

    def __init__(self, models=None, clf=None, weights=None, task=constants.Tasks.CLASSIFICATION,
                 **kwargs):
        """
        Initialize EnsembleWrapper model.

        :param models: List of models to use in ensembling.
        :type models: list
        :param clf:
        """
        self.models = models
        self.clf = clf
        self.classes_ = None
        if self.clf:
            if hasattr(self.clf, 'classes_'):
                self.classes_ = self.clf.classes_
        self.weights = weights
        self.task = task

    def fit(self, X, y):
        """
        Fit function for EnsembleWrapper.

        :param X: Input data.
        :type X: numpy.ndarray
        :param y: Input target values.
        :type y: numpy.ndarray
        :return:
        """
        for m in self.models:
            m.fit(X, y)
        return self

    def get_params(self, deep=True):
        """
        Return parameters for Ensemble Wrapper Model.

        :param deep:
            If True, will return the parameters for this estimator
            and contained subobjects that are estimators.
        :type deep: bool
        :return: parameters for Ensemble Wrapper Model.
        """
        params = {}
        params['models'] = self.models
        params['clf'] = self.clf

        return params

    @staticmethod
    def get_ensemble_predictions(preds, weights=None,
                                 task=constants.Tasks.CLASSIFICATION):
        """
        Combine an array of probilities from compute_valid_predictions.

        Probabilities are combined into a single array of shape [num_samples, num_classes].
        """
        preds = np.average(preds, axis=2, weights=weights)
        if task == constants.Tasks.CLASSIFICATION:
            preds /= preds.sum(1)[:, None]
            assert np.all(preds >= 0) and np.all(preds <= 1)

        return preds

    @staticmethod
    def compute_valid_predictions(models, X, model_file_name_format=None, num_scores=None, splits=None):
        """Return an array of probabilities of shape [num_samples, num_classes, num_models]."""
        found_model = False
        if model_file_name_format:
            for i in range(num_scores):
                model_file_name = model_file_name_format.format(i)
                if os.path.exists(model_file_name):
                    with open(model_file_name, 'rb') as f:
                        m = pickle.load(f)
                    found_model = True
                    break
        else:
            for m in models:
                if m is not None:
                    found_model = True
                    break
        if not found_model:
            raise ValueError('no models found')
        if isinstance(m, list):
            m = m[0]
        preds0 = EnsembleWrapper._predict_proba_if_possible(m, X)
        num_classes = preds0.shape[1]

        preds = np.zeros((X.shape[0], num_classes, num_scores if num_scores else len(models)))
        if model_file_name_format:
            for i in range(num_scores):
                model_file_name = model_file_name_format.format(i)
                if os.path.exists(model_file_name):
                    with open(model_file_name, 'rb') as f:
                        m = pickle.load(f)
                    if isinstance(m, list):
                        for cv_fold, split in enumerate(splits):
                            preds[split, :, i] = EnsembleWrapper._predict_proba_if_possible(m[cv_fold], X[split])
                    else:
                        preds[:, :, i] = EnsembleWrapper._predict_proba_if_possible(m, X)
        else:
            for i, m in enumerate(models):
                if m is None:
                    continue
                if isinstance(m, list):
                    for cv_fold, split in enumerate(splits):
                        preds[split, :, i] = EnsembleWrapper._predict_proba_if_possible(m[cv_fold], X[split])
                else:
                    preds[:, :, i] = EnsembleWrapper._predict_proba_if_possible(m, X)
        return preds

    @staticmethod
    def _predict_proba_if_possible(model, X):
        if hasattr(model, 'predict_proba'):
            preds = model.predict_proba(X)
        else:
            preds = model.predict(X)
            preds = preds.reshape(-1, 1)
        return preds

    def predict(self, X):
        """
        Prediction function for EnsembleWrapper model.

        :param X: Input data.
        :type X: numpy.ndarray
        :return: Prediction values from EnsembleWrapper model.
        """
        if self.task == constants.Tasks.CLASSIFICATION:
            probs = self.predict_proba(X)
            return np.argmax(probs, axis=1)
        else:
            return self.predict_regression(X)

    def predict_regression(self, X):
        """
        Predict regression results for X for EnsembleWrapper model.

        :param X: Input data.
        :type X: numpy.ndarray
        :return:
            Prediction probability values from EnsembleWrapper model.
        """
        valid_predictions = EnsembleWrapper.compute_valid_predictions(
            self.models, X)
        if self.clf is None:
            return EnsembleWrapper.get_ensemble_predictions(
                valid_predictions, self.weights, task=self.task)
        else:
            return self.clf.predict(valid_predictions.reshape(
                valid_predictions.shape[0],
                valid_predictions.shape[1] * valid_predictions.shape[2]))

    def predict_proba(self, X):
        """
        Prediction class probabilities for X for EnsembleWrapper model.

        :param X: Input data.
        :type X: numpy.ndarray
        :return:
            Prediction probability values from EnsembleWrapper model.
        """
        valid_predictions = EnsembleWrapper.compute_valid_predictions(
            self.models, X)
        if self.clf is None:
            return EnsembleWrapper.get_ensemble_predictions(
                valid_predictions, self.weights)
        else:
            # TODO make sure the order is same as during training\
            # ignore the first column due to collinearity
            valid_predictions = valid_predictions[:, 1:, :]
            return self.clf.predict_proba(valid_predictions.reshape(
                valid_predictions.shape[0],
                valid_predictions.shape[1] * valid_predictions.shape[2]))


class LinearSVMWrapper(BaseEstimator, ClassifierMixin, _AbstractModelWrapper):
    """
    Wrapper around linear svm to support predict_proba on sklearn's liblinear wrapper.

    :param random_state:
        RandomState instance or None, optional (default=None)
        If int, random_state is the seed used by the random number generator;
        If RandomState instance, random_state is the random number generator;
        If None, the random number generator is the RandomState instance used
        by `np.random`.
    :type random_state: int or RandomState
    :param kwargs: Other parameters.
    """

    def __init__(self, random_state=None, **kwargs):
        """
        Initialize Linear SVM Wrapper Model.

        :param random_state:
            RandomState instance or None, optional (default=None)
            If int, random_state is the seed used by the random number
            generator;
            If RandomState instance, random_state is the random number
            generator;
            If None, the random number generator is the RandomState
            instance used by `np.random`.
        :type random_state: int or RandomState
        :param kwargs: Other parameters.
        """
        self.args = kwargs
        self.args['random_state'] = random_state
        self.model = CalibratedModel(sklearn.svm.LinearSVC(**self.args))

    def get_model(self):
        """
        Return Linear SVM Wrapper Model.

        :return: Linear SVM Wrapper Model.
        """
        return self.model

    def fit(self, X, y, **kwargs):
        """
        Fit function for Linear SVM Wrapper Model.

        :param X: Input data.
        :type X: numpy.ndarray
        :param y: Input target values.
        :type y: numpy.ndarray
        :param kwargs: Other parameters.
        """
        self.model.fit(X, y, **kwargs)
        if hasattr(self.model, "classes_"):
            self.classes_ = self.model.classes_
        else:
            self.classes_ = np.unique(y)

    def get_params(self, deep=True):
        """
        Return parameters for Linear SVM Wrapper Model.

        :param deep:
            If True, will return the parameters for this estimator
            and contained subobjects that are estimators.
        :type deep: bool
        :return: parameters for Linear SVM Wrapper Model
        """
        params = {'random_state': self.args['random_state']}

        assert (isinstance(self.model, CalibratedModel))
        if isinstance(self.model.model, CalibratedClassifierCV):
            params.update(self.model.model.base_estimator.get_params(deep=deep))
        return params

    def predict_proba(self, X):
        """
        Prediction class probabilities for X for Linear SVM Wrapper model.

        :param X: Input data.
        :type X: numpy.ndarray
        :return: Prediction probability values from Linear SVM Wrapper model.
        """
        return self.model.predict_proba(X)

    def predict(self, X):
        """
        Prediction function for Linear SVM Wrapper Model.

        :param X: Input data.
        :type X: numpy.ndarray
        :return: Prediction values from Linear SVM Wrapper model.
        """
        return self.model.predict(X)


class CalibratedModel(BaseEstimator, ClassifierMixin, _AbstractModelWrapper):
    """
    Trains a calibrated model.

    Takes a base estimator as input and trains a calibrated model.
    :param base_estimator: Base Model on which calibration has to be performed.
    :param random_state:
        RandomState instance or None, optional (default=None)
        If int, random_state is the seed used by the random number generator;
        If RandomState instance, random_state is the random number generator;
        If None, the random number generator is the RandomState instance used
        by `np.random`.
    :type random_state: int or RandomState

    Read more at:
    http://scikit-learn.org/stable/modules/generated/sklearn.calibration.CalibratedClassifierCV.html.
    """

    def __init__(self, base_estimator, random_state=None):
        """
        Initialize Calibrated Model.

        :param base_estimator: Base Model on which calibration has to be
            performed.
        :param random_state:
            RandomState instance or None, optional (default=None)
            If int, random_state is the seed used by the random number
            generator.
            If RandomState instance, random_state is the random number
            generator.
            If None, the random number generator is the RandomState instance
            used by `np.random`.
        :type random_state: int or RandomState
        """
        self._train_ratio = 0.8
        self.random_state = random_state
        self.model = CalibratedClassifierCV(
            base_estimator=base_estimator, cv="prefit")

    def get_model(self):
        """
        Return the sklearn Calibrated Model.

        :return: The Calibrated Model.
        :rtype: sklearn.calibration.CalibratedClassifierCV
        """
        return self.model

    def fit(self, X, y, **kwargs):
        """
        Fit function for Calibrated Model.

        :param X: Input training data.
        :type X: numpy.ndarray
        :param y: Input target values.
        :type y: numpy.ndarray
        :return: self: Returns an instance of self.
        :rtype: CalibratedModel
        """
        arrays = [X, y]
        if "sample_weight" in kwargs:
            arrays.append(kwargs["sample_weight"])
        self.args = kwargs
        out_arrays = train_test_split(
            *arrays,
            train_size=self._train_ratio,
            random_state=self.random_state,
            stratify=y)
        X_train, X_valid, y_train, y_valid = out_arrays[:4]

        if "sample_weight" in kwargs:
            sample_weight_train, sample_weight_valid = out_arrays[4:]
        else:
            sample_weight_train = None
            sample_weight_valid = None

        # train model
        self.model.base_estimator.fit(
            X_train, y_train, sample_weight=sample_weight_train)

        # fit calibration model
        try:
            self.model.fit(X_valid, y_valid, sample_weight=sample_weight_valid)
        except ValueError as e:
            y_labels = np.unique(y)
            y_train_labels = np.unique(y_train)
            y_valid_labels = np.unique(y_valid)
            y_train_missing_labels = np.setdiff1d(y_labels, y_train_labels, assume_unique=True)
            y_valid_missing_labels = np.setdiff1d(y_labels, y_valid_labels, assume_unique=True)
            if y_train_missing_labels.shape[0] > 0 or y_valid_missing_labels.shape[0] > 0:
                missing_labels = np.union1d(y_train_missing_labels, y_valid_missing_labels)
                raise ValueError('y did not contain enough samples for the following labels: {}'
                                 .format(missing_labels.tolist())) from e
            else:
                raise

        # retrain base estimator on full dataset
        self.model.base_estimator.fit(X, y, **kwargs)
        if hasattr(self.model, "classes_"):
            self.classes_ = self.model.classes_
        else:
            self.classes_ = np.unique(y)
        return self

    def get_params(self, deep=True):
        """
        Return parameters for Calibrated Model.

        :param deep:
            If True, will return the parameters for this estimator
            and contained subobjects that are estimators.
        :type deep: bool
        :return: Parameters for Calibrated Model.
        """
        params = {'random_state': self.random_state}
        assert (isinstance(self.model, CalibratedClassifierCV))
        params['base_estimator'] = self.model.base_estimator
        return params

    def predict(self, X):
        """
        Prediction function for Calibrated Model.

        :param X: Input samples.
        :type X: numpy.ndarray
        :return: Prediction values from Calibrated model.
        :rtype: array
        """
        return self.model.predict(X)

    def predict_proba(self, X):
        """
        Prediction class probabilities for X for Calibrated model.

        :param X: Input samples.
        :type X: numpy.ndarray
        :return: Prediction proba values from Calibrated model.
        :rtype: array
        """
        return self.model.predict_proba(X)


class LightGBMRegressor(BaseEstimator, RegressorMixin, _AbstractModelWrapper):
    """
    LightGBM Regressor class.

    :param random_state:
        RandomState instance or None, optional (default=None)
        If int, random_state is the seed used by the random number generator;
        If RandomState instance, random_state is the random number generator;
        If None, the random number generator is the RandomState instance used
        by `np.random`.
    :type random_state: int or RandomState
    :param kwargs: Other parameters.
    """

    DEFAULT_MIN_DATA_IN_LEAF = 20

    def __init__(self, random_state=None, n_jobs=1, categorical_feature=None, **kwargs):
        """
        Initialize LightGBM Regressor class.

        :param random_state:
            RandomState instance or None, optional (default=None)
            If int, random_state is the seed used by the random number
            generator;
            If RandomState instance, random_state is the random number
            generator;
            If None, the random number generator is the RandomState
            instance used by `np.random`.
        :param categorical_feature: Indicies of the categorical columns.
        :type random_state: int or RandomState
        :param kwargs: Other parameters.
        """
        self.params = kwargs
        self.params['random_state'] = random_state
        self.params['n_jobs'] = n_jobs
        self.model = None
        self._min_data_in_leaf = "min_data_in_leaf"
        self._min_child_samples = "min_child_samples"

        self._categoricals = categorical_feature
        if self._min_data_in_leaf not in kwargs and \
                self._min_child_samples not in kwargs:
            raise ValueError("neither min_data_in_leaf nor min_child_samples passed")

    def get_model(self):
        """
        Return LightGBM Regressor model.

        :return:
            Returns the fitted model if fit method has been called.
            Else returns None
        """
        return self.model

    def fit(self, X, y, **kwargs):
        """
        Fit function for LightGBM Regressor model.

        :param X: Input data.
        :type X: numpy.ndarray
        :param y: Labels for the data.
        :type y: numpy.ndarray
        :param kwargs: Other parameters.
        :return: Returns self after fitting the model.
        """
        verbose_str = "verbose"
        n = X.shape[0]
        params = dict(self.params)
        if (self._min_data_in_leaf in params):
            if (self.params[self._min_data_in_leaf] ==
                    LightGBMRegressor.DEFAULT_MIN_DATA_IN_LEAF):
                params[self._min_child_samples] = self.params[
                    self._min_data_in_leaf]
            else:
                params[self._min_child_samples] = int(
                    self.params[self._min_data_in_leaf] * n) + 1
            del params[self._min_data_in_leaf]
        else:
            min_child_samples = self.params[self._min_child_samples]
            if min_child_samples > 0 and min_child_samples < 1:
                # we'll convert from fraction to int as that's what LightGBM expects
                params[self._min_child_samples] = int(
                    self.params[self._min_child_samples] * n) + 1
            else:
                params[self._min_child_samples] = min_child_samples

        if verbose_str not in params:
            params[verbose_str] = -1

        if self._categoricals is not None:
            kwargs['categorical_feature'] = self._categoricals.tolist()

        self.model = lgb.LGBMRegressor(**params)
        self.model.fit(X, y, **kwargs)

        return self

    def get_params(self, deep=True):
        """
        Return parameters for LightGBM Regressor model.

        :param deep:
            If True, will return the parameters for this estimator
            and contained subobjects that are estimators.
        :type deep: bool
        :return: Parameters for LightGBM Regressor model.
        """
        params = {}
        params['random_state'] = self.params['random_state']
        params['n_jobs'] = self.params['n_jobs']
        if self.model:
            params.update(self.model.get_params(deep=deep))
        else:
            params.update(self.params)

        return params

    def predict(self, X):
        """
        Prediction function for LightGBM Regressor model.

        :param X: Input data.
        :type X: numpy.ndarray
        :return: Prediction values from LightGBM Regressor model.
        """
        return self.model.predict(X)


class XGBoostRegressor(BaseEstimator, RegressorMixin, _AbstractModelWrapper):
    """
    XGBoost Regressor class.

    :param random_state:
        RandomState instance or None, optional (default=None)
        If int, random_state is the seed used by the random number generator;
        If RandomState instance, random_state is the random number generator;
        If None, the random number generator is the RandomState instance used
        by `np.random`.
    :type random_state: int or RandomState
    :param n_jobs: Number of parallel threads.
    :type n_jobs: int
    :param kwargs: Other parameters
        Check https://xgboost.readthedocs.io/en/latest/parameter.html
        for more parameters.
    """

    def __init__(self, random_state=0, n_jobs=1, **kwargs):
        """
        Initialize XGBoost Regressor class.

        :param random_state:
            RandomState instance or None, optional (default=None)
            If int, random_state is the seed used by the random number
            generator.
            If RandomState instance, random_state is the random number
            generator.
            If None, the random number generator is the RandomState instance
            used by `np.random`.
        :type random_state: int or RandomState
        :param n_jobs: Number of parallel threads.
        :type n_jobs: int
        :param kwargs: Other parameters
            Check https://xgboost.readthedocs.io/en/latest/parameter.html
            for more parameters.
        """
        self.params = kwargs
        self.params['random_state'] = random_state if random_state is not None else 0
        self.params['n_jobs'] = n_jobs
        self.model = None
        if not xgboost_present:
            raise ConfigException("xgboost not installed, please install xgboost for including xgboost based models")

    def get_model(self):
        """
        Return XGBoost Regressor model.

        :return: Returns the fitted model if fit method has been called.
        Else returns None.
        """
        return self.model

    def fit(self, X, y, **kwargs):
        """
        Fit function for XGBoost Regressor model.

        :param X: Input data.
        :type X: numpy.ndarray
        :param y: Input target values.
        :type y: numpy.ndarray
        :param kwargs: other parameters
            Check https://xgboost.readthedocs.io/en/latest/parameter.html
            for more parameters.
        :return: Self after fitting the model.
        """
        args = dict(self.params)
        verbose_str = "verbose"
        if verbose_str not in args:
            args[verbose_str] = -10

        self.model = xgb.XGBRegressor(**args)
        self.model.fit(X, y, **kwargs)

        return self

    def get_params(self, deep=True):
        """
        Return parameters for XGBoost Regressor model.

        :param deep:
            If True, will return the parameters for this estimator and contained subobjects that are estimators.
        :type deep: boolean
        :return: Parameters for the XGBoost classifier model.
        """
        if self.model:
            return self.model.get_params(deep)
        else:
            return self.params

    def predict(self, X):
        """
        Prediction function for XGBoost Regressor model.

        :param X: Input data.
        :type X: numpy.ndarray
        :return: Prediction values from XGBoost Regressor model.
        """
        if self.model is None:
            raise sklearn.exceptions.NotFittedError()
        return self.model.predict(X)


class RegressionPipeline(sklearn.pipeline.Pipeline):
    """
    A pipeline with quantile predictions.

    This pipeline is a wrapper on the sklearn.pipeline.Pipeline to
    provide methods related to quantile estimation on predictions.
    """

    def __init__(self,
                 pipeline: SKPipeline,
                 stddev: Union[float, List[float]]) -> None:
        """
        Create a pipeline.

        :param pipeline: The pipeline to wrap.
        :param stddev:
            The standard deviation of the residuals from validation fold(s).
        """
        super().__init__(pipeline.steps, memory=pipeline.memory)
        self._quantiles = [.5]
        self.pipeline = pipeline
        if not isinstance(stddev, list):
            stddev = [stddev]
        self._stddev = stddev

    @property
    def quantiles(self) -> List[float]:
        """Quantiles for the pipeline to predict."""
        return self._quantiles

    @quantiles.setter
    def quantiles(self, quantiles: Union[float, List[float]]) -> None:
        if not isinstance(quantiles, list):
            quantiles = [quantiles]

        for quant in quantiles:
            if quant == 0:
                raise ValueError("Quantile 0 is not supported.")
            if quant == 1:
                raise ValueError("Quantile 1 is not supported.")
            if quant < 0 or quant > 1:
                raise ValueError("Quantiles must be strictly less than 1 and greater than 0.")

        self._quantiles = quantiles

    def predict_quantiles(self, X: Any,
                          **predict_params: Any) -> pd.DataFrame:
        """
        Get the prediction and quantiles from the fitted pipeline.

        :param X: The data to predict on.
        :return: The requested quantiles from prediction.
        :rtype: pandas.DataFrame
        """
        pred = self.predict(X, **predict_params)
        return self._get_ci(pred, np.full(len(pred), self._stddev[0]), self._quantiles)

    def _get_ci(self, y_pred: np.array, stddev: np.array, quantiles: List[float]) -> pd.DataFrame:
        """
        Get Confidence intervales for predictions.

        :param y_pred: The predicted values.
        :param stddev: The standard deviations.
        :param quantiles: The desired quantiles.
        """
        res = pd.DataFrame()
        for quantile in quantiles:
            ci_bound = 0.0
            if quantile != .5:
                z_score = norm.ppf(quantile)
                ci_bound = z_score * stddev
            res[quantile] = pd.Series(y_pred + ci_bound)
        return res


class ForecastingPipelineWrapper(RegressionPipeline):
    """A pipeline for forecasting."""

    # Constants for errors and warnings
    # Non recoverable errors.
    FATAL_WRONG_DESTINATION_TYPE = "The forecast_destination has wrong type."
    FATAL_WRONG_ORIGIN_TYPE = "The forecast_origin has wrong type."
    FATAL_DATA_SIZE_MISMATCH = "The length of y_pred is different from the X_pred"
    FATAL_WRONG_Y_TYPE = "y_pred has unsupported type."
    FATAL_NO_DATA_CONTEXT_TEMPL = "No y values were provided for grain {}"
    FATAL_DESTINATION_XOR_X_PRED = "Destination date and X_pred or y_pred are mutually exclusive."
    FATAL_X_Y_XOR = "X_pred and y_pred should both be None or both not None."
    FATAL_NO_LAST_DATE = "The last training date was not provided."
    FATAL_EARLY_DESTINATION = "The destination date appears earlier then the last training date."
    FATAL_NO_TARGET_IN_Y_DF_TEMPL = ("The y_pred is a data frame, "
                                     "but it does not contain target value column ({})")
    FATAL_WRONG_QUANTILE = "Quantile should be more then 0 but more then 1"
    FATAL_NO_TS_TRANSFORM = "The time series transform is absent."
    # Recoverable errors.
    ERR_NOTHING_TO_PREDICT = "The y values present for each date. Nothing to forecast."
    ERR_NON_CONTIGUOUS_Y = "The y values contains non contiguous NaN values."
    ERR_NO_DATA_CONTEXT = "No y values were provided."
    ERR_DF_CONTAINS_NAN = "The X_pred contains NaNs."

    def __init__(self,
                 pipeline: SKPipeline,
                 stddev: List[float]) -> None:
        """
        Create a pipeline.

        :param pipeline: The pipeline to wrap.
        :type pipeline: sklearn.pipeline.Pipeline
        :param stddev:
            The standard deviation of the residuals from validation fold(s).
        """
        super().__init__(pipeline, stddev)
        for name, transformer in pipeline.steps:
            # FIXME: Work item #400231
            if type(transformer).__name__ == 'TimeSeriesTransformer':
                ts_transformer = transformer

        if "ts_transformer" not in vars() or ts_transformer is None:
            raise DataException("The provided pipeline does not contain time series transformer.")

        self._ts_transformer = ts_transformer
        self._origin_col_name = ts_transformer.origin_column_name
        self._time_col_name = ts_transformer.time_column_name
        self._quantiles = [.5]
        self._horizon_idx = None   # type: Optional[int]
        self.grain_column_names = ts_transformer.grain_column_names
        self.target_column_name = ts_transformer.target_column_name
        self.data_frequency = ts_transformer.freq
        self.forecast_origin = {}  # type: Dict[Tuple[str], pd.Timestamp]

    @property
    def time_column_name(self) -> str:
        """Return the name of the time column."""
        return cast(str, self._time_col_name)

    @property
    def origin_col_name(self) -> str:
        """Return the origin column name."""
        # Note this method will return origin column name,
        # which is only used for reconstruction of a TimeSeriesDataFrame.
        # If origin column was introduced during transformation it is still None
        # on ts_transformer.
        if self._origin_col_name is None:
            self._origin_col_name = self._ts_transformer.origin_column_name
        # TODO: Double check type: Union[str, List[str]]
        ret = self._origin_col_name if self._origin_col_name \
            else constants.TimeSeriesInternal.ORIGIN_TIME_COLNAME_DEFAULT
        return cast(str, ret)

    def _check_data(self, X_pred: pd.DataFrame,
                    y_pred: pd.DataFrame,
                    forecast_destination: pd.Timestamp) -> None:
        """
        Check the user input.

        :param X_pred: the prediction dataframe combining X_past and X_future in a time-contiguous manner.
                       Empty values in X_pred will be imputed.
        :param y_pred: the target value combining definite values for y_past and missing values for Y_future.
        :param forecast_destination: Forecast_destination: a time-stamp value.
                                     Forecasts will be made all the way to the forecast_destination time,
                                     for all grains. Dictionary input { grain -> timestamp } will not be accepted.
                                     If forecast_destination is not given, it will be imputed as the last time
                                     occurring in X_pred for every grain.
        :raises: DataException

        """
        # Check types
        if forecast_destination is not None and not isinstance(forecast_destination, pd.Timestamp) and not isinstance(
                forecast_destination, np.datetime64):
            raise DataException(
                ForecastingPipelineWrapper.FATAL_WRONG_DESTINATION_TYPE)
        if (forecast_destination is None) == (
                X_pred is None or y_pred is None):
            # Raise the exception if user provided both forecast_destination
            # and prediction data frame.
            raise DataException(
                ForecastingPipelineWrapper.FATAL_DESTINATION_XOR_X_PRED)
        if (X_pred is None) != (y_pred is None):
            # If user provided only one of  X_pred or y_pred raise the error.
            raise DataException(ForecastingPipelineWrapper.FATAL_X_Y_XOR)

    def _create_prediction_data_frame(self,
                                      X_pred: pd.DataFrame,
                                      y_pred: Union[pd.DataFrame, np.ndarray],
                                      forecast_destination: pd.Timestamp,
                                      ignore_data_errors: bool) -> pd.DataFrame:
        """
        Create the data frame which will be used for preduiction purposes.

        :param X_pred: the prediction dataframe combining X_past and X_future in a time-contiguous manner.
                       Empty values in X_pred will be imputed.
        :param y_pred: the target value combining definite values for y_past and missing values for Y_future.
        :param forecast_destination: Forecast_destination: a time-stamp value.
                                     Forecasts will be made all the way to the forecast_destination time,
                                     for all grains. Dictionary input { grain -> timestamp } will not be accepted.
                                     If forecast_destination is not given, it will be imputed as the last time
                                     occurring in X_pred for every grain.
        :param ignore_data_errors: Ignore errors in user data.
        :returns: The clean data frame.
        :raises: DataException

        """
        if X_pred is not None:
            X_copy = X_pred.copy()
            if self.grain_column_names[0] == constants.TimeSeriesInternal.DUMMY_GRAIN_COLUMN and \
                    self.grain_column_names[0] not in X_copy.columns:
                X_copy[constants.TimeSeriesInternal.DUMMY_GRAIN_COLUMN] = \
                    constants.TimeSeriesInternal.DUMMY_GRAIN_COLUMN
            X_copy[self._time_col_name] = pd.to_datetime(
                X_copy[self._time_col_name].values)
            # Remember the forecast origins for each grain.
            # We will trim the data frame by these values at the end.
            for grain, df_one in X_copy.groupby(self.grain_column_names):
                self.forecast_origin[grain] = df_one[self._time_col_name].min()
            special_columns = self.grain_column_names.copy()
            special_columns.append(self._ts_transformer.time_column_name)
            if self.origin_col_name in X_copy.columns:
                special_columns.append(self.origin_col_name)
            if self._ts_transformer.group_column in X_copy.columns:
                special_columns.append(self._ts_transformer.group_column)
            for column in X_copy.columns:
                if column not in special_columns and \
                        column in X_copy.select_dtypes(include=[np.number]).columns and \
                        all(np.isnan(float(var)) for var in X_copy[column].values):
                    self._warn_or_raise(
                        ForecastingPipelineWrapper.ERR_DF_CONTAINS_NAN,
                        ignore_data_errors)
                    break

            if y_pred.shape[0] != X_pred.shape[0]:
                # May be we need to revisit this assertion.
                raise DataException(
                    ForecastingPipelineWrapper.FATAL_DATA_SIZE_MISMATCH)
            if isinstance(y_pred, pd.DataFrame):
                if self._ts_transformer.target_column_name not in y_pred.columns:
                    raise DataException(
                        ForecastingPipelineWrapper.FATAL_NO_TARGET_IN_Y_DF_TEMPL.format(
                            self._ts_transformer.time_column_name))
                X_copy = pd.merge(
                    left=X_copy,
                    right=y_pred,
                    how='left',
                    left_index=True,
                    right_index=True)
                if X_copy.shape[0] != X_pred.shape[0]:
                    raise DataException(
                        ForecastingPipelineWrapper.FATAL_DATA_SIZE_MISMATCH)
            elif isinstance(y_pred, np.ndarray) and X_copy.shape[0] == y_pred.shape[0]:
                X_copy[constants.TimeSeriesInternal.DUMMY_TARGET_COLUMN] = y_pred
            else:
                raise DataException(
                    ForecastingPipelineWrapper.FATAL_WRONG_Y_TYPE)
            # At that point we have generated the data frame which contains Target value column
            # filled with y_pred. The part which will need to be should be
            # filled with np.NaNs.
        else:
            # Create the empty data frame from the last date in the training set for each grain
            # and fill it with NaNs. Impute these data.
            if self._ts_transformer.dict_latest_date == {}:
                raise DataException(
                    ForecastingPipelineWrapper.FATAL_NO_LAST_DATE)
            dfs = []
            for grain_tuple in self._ts_transformer.dict_latest_date.keys():
                if pd.Timestamp(forecast_destination) <= self._ts_transformer.dict_latest_date[grain_tuple]:
                    raise DataException(
                        ForecastingPipelineWrapper.FATAL_EARLY_DESTINATION)
                # Start with the next date after the last seen date.
                start_date = self._ts_transformer.dict_latest_date[grain_tuple] + \
                    to_offset(self._ts_transformer.freq)
                df_dict = {
                    self._time_col_name: pd.date_range(
                        start=start_date,
                        end=forecast_destination,
                        freq=self._ts_transformer.freq)}
                if isinstance(grain_tuple, str):
                    df_dict[self.grain_column_names[0]] = grain_tuple
                else:
                    for i in range(len(self.grain_column_names)):
                        df_dict[self.grain_column_names[i]] = grain_tuple[i]
                for col in cast(List[Any], self._ts_transformer.columns):
                    if col not in df_dict.keys():
                        df_dict[col] = np.NaN
                # target_column_name is not in the data frame columns by
                # default.
                df_dict[self._ts_transformer.target_column_name] = np.NaN
                dfs.append(pd.DataFrame(df_dict))
            X_copy = pd.concat(dfs)
            # At that point we have generated the data frame which contains target value column.
            # The data frame is filled with imputed data. Only target column is filled with np.NaNs,
            # because all gap between training data and forecast_destination
            # should be predicted.
        return X_copy

    def _infer_missing_data(
            self,
            X: pd.DataFrame,
            ignore_data_errors: bool) -> pd.DataFrame:
        """
        Infer missing data in the data frame X.

        :param X: The data frame used for the inference.
        :param ignore_data_errors: Ignore errors in user data.
        :returns: the data frame with no NaNs
        :raises: DataException
        """
        df_inferred = []
        is_reported = False
        for grain, df_one in X.groupby(self.grain_column_names):
            time_offset = to_offset(self.data_frequency)
            first_unknown_y_date = self._get_last_y_one_grain(df_one, ignore_data_errors)
            if first_unknown_y_date is None:
                first_unknown_y_date = min(df_one[self._time_col_name])
            else:
                first_unknown_y_date = first_unknown_y_date + time_offset
            expected_start = max(self._ts_transformer.dict_latest_date.get(grain) + time_offset,
                                 first_unknown_y_date - time_offset * self._ts_transformer.max_horizon)
            hasgap = min(df_one[self._time_col_name]) > expected_start
            if all(np.isnan(y) for y in df_one[constants.TimeSeriesInternal.DUMMY_TARGET_COLUMN].values) and\
               not is_reported and hasgap and self._lag_or_rw_enabled():
                # Do not warn user multiple times.
                self._warn_or_raise(
                    ForecastingPipelineWrapper.ERR_NO_DATA_CONTEXT,
                    ignore_data_errors)
                is_reported = True
            if self._ts_transformer.dict_latest_date.get(grain) is None:
                raise DataException(
                    ForecastingPipelineWrapper.FATAL_NO_DATA_CONTEXT_TEMPL.format(grain))
            if min(df_one[self._time_col_name]) <= self._ts_transformer.dict_latest_date[grain]:
                raise DataException(
                    ForecastingPipelineWrapper.FATAL_EARLY_DESTINATION)
            # If we have a gap between train and predict data set, we need to extend the test set.
            # If there is no last known date, nothing can be done.
            if self._ts_transformer.dict_latest_date.get(grain):
                # If we know the last date, we can evaluate and fill the gap.
                if hasgap:
                    # If there is a gap between train and test data for the
                    # given grain, extend the test data frame.
                    ext_dates = pd.date_range(start=expected_start,
                                              end=pd.Timestamp(min(df_one[self._time_col_name].values)) - time_offset,
                                              freq=self.data_frequency)
                    extension = pd.DataFrame(np.nan, index=np.arange(
                        len(ext_dates)), columns=df_one.columns.values)
                    extension[self._time_col_name] = ext_dates
                    if isinstance(grain, str):
                        extension[self.grain_column_names[0]] = grain
                    else:
                        for i in range(len(self.grain_column_names)):
                            extension[self.grain_column_names[i]] = grain[i]
                    # Make a temporary time series data frame to apply
                    # imputers.
                    tsdf_ext = tsdf.TimeSeriesDataFrame(
                        extension,
                        time_colname=self._ts_transformer.time_column_name,
                        grain_colnames=self._ts_transformer.grain_column_names,
                        ts_value_colname=self._ts_transformer.target_column_name)
                    # Replace np.NaNs by imputed values.
                    tsdf_ext = self._ts_transformer.pipeline.get_pipeline_step(
                        constants.TimeSeriesInternal.IMPUTE_NA_NUMERIC_COLUMNS).transform(tsdf_ext)
                    tsdf_ext = self._ts_transformer.pipeline.get_pipeline_step(
                        constants.TimeSeriesInternal.IMPUTE_NA_FINAL).transform(tsdf_ext)
                    # Replace np.NaNs in y column.
                    imputer = self._ts_transformer.y_imputers.get(grain)
                    assert imputer is not None
                    tsdf_ext = imputer.transform(tsdf_ext)
                    # Return the regular data frame.
                    extension = pd.DataFrame(tsdf_ext)
                    extension.reset_index(drop=False, inplace=True)
                    df_one = pd.concat([extension, df_one])
            # Make sure we do not have a gaps in the y.
            # We are actually doing it only if ignore_data_errors is set to True,
            # or we do not have non contiguous NaNs and code have no effect.
            y_vals = df_one[self._ts_transformer.target_column_name]
            y_vals.fillna(None, 'bfill', axis=0, inplace=True)
            df_one.drop(
                self._ts_transformer.target_column_name,
                inplace=True,
                axis=1)
            df_one[self._ts_transformer.target_column_name] = y_vals.values
            df_inferred.append(df_one)
        X = pd.concat(df_inferred)
        return X

    def forecast(self,
                 X_pred: Optional[pd.DataFrame] = None,
                 y_pred: Optional[Union[pd.DataFrame,
                                        np.ndarray]] = None,
                 forecast_destination: Optional[pd.Timestamp] = None,
                 ignore_data_errors: bool = False) -> Tuple[np.ndarray,
                                                            pd.DataFrame]:
        """
        Do the forecast on the data frame X_pred.

        DataError is thrown if neither X_pred and y_pred nor
        :param X_pred: the prediction dataframe combining X_past and X_future in a time-contiguous manner.
                       Empty values in X_pred will be imputed.
        :param y_pred: the target value combining definite values for y_past and missing values for Y_future.
        :param forecast_destination: Forecast_destination: a time-stamp value.
                                     Forecasts will be made all the way to the forecast_destination time,
                                     for all grains. Dictionary input { grain -> timestamp } will not be accepted.
                                     If forecast_destination is not given, it will be imputed as the last time
                                     occurring in X_pred for every grain.
        :type forecast_destination: pd.Timestamp
        :param ignore_data_errors: Ignore errors in user data.
        :type ignore_data_errors: bool
        :returns: Y_pred, with the subframe corresponding to Y_future filled in with the respective forecasts.
                  Any missing values in Y_past will be filled by imputer.
        :rtype: tuple
        """
        self._check_data(X_pred, y_pred, forecast_destination)
        # Make sure that we have a data frame in both cases: when user provided X_pred and y_pred
        # or forecast_destination
        X_copy = self._create_prediction_data_frame(
            X_pred, y_pred, forecast_destination, ignore_data_errors)
        # We need to make sure that we have a context. If train set is followed by a test/predict set,
        # there should be no error. otherwise we will need to infer missing data.
        # The part of the data frame, for which y_pred is known will be
        # removed.
        self._get_last_known_y(X_copy, ignore_data_errors)
        X_copy = self._infer_missing_data(X_copy, ignore_data_errors)
        self._get_last_known_y(X_copy, ignore_data_errors)
        last_step = self.pipeline.steps[len(self.pipeline.steps) - 1][1]
        # Pre processing.
        test_feats = None
        y_known_series = None  # type: Optional[pd.Series]
        for i in range(len(self.pipeline.steps) - 1):
            # FIXME: Work item #400231
            if type(self.pipeline.steps[i][1]).__name__ == 'TimeSeriesTransformer':
                test_feats = self.pipeline.steps[i][1].transform(X_copy)
                # We do not need the target column now.
                # The target column is deleted by the rolling window during transform.
                # If there is no rolling window we need to make sure the column was dropped.
                if self._ts_transformer.target_column_name in test_feats.columns:
                    # We want to store the y_known_series for future use.
                    y_known_series = test_feats[self._ts_transformer.target_column_name]
                    test_feats.drop(self._ts_transformer.target_column_name, inplace=True, axis=1)
                X_copy = test_feats.copy()
            else:
                X_copy = self.pipeline.steps[i][1].transform(X_copy)
        # Create fake grains if we don't have it.
        if self.grain_column_names == constants.TimeSeriesInternal.DUMMY_GRAIN_COLUMN:
            X_copy[self.grain_column_names] = constants.TimeSeriesInternal.DUMMY_GRAIN_COLUMN
        y_preds = last_step.predict(X_copy)
        # We have unclosed gap should not be the case.
        assert (test_feats is not None)
        assert (y_preds.shape[0] == test_feats.shape[0])
        test_feats[constants.TimeSeriesInternal.DUMMY_TARGET_COLUMN] = y_preds
        test_feats = self.get_latest_origins(test_feats)
        test_feats = self._postprocess_output(test_feats, y_known_series)
        # Restore the index.
        list_index = [self.time_column_name] + self.grain_column_names
        if self.origin_col_name in test_feats.columns.values:
            list_index.append(self.origin_col_name)
        test_feats.set_index(list_index,
                             inplace=True)
        test_feats.sort_index(inplace=True)
        y_pred = test_feats[constants.TimeSeriesInternal.DUMMY_TARGET_COLUMN].values
        return y_pred, test_feats

    def get_latest_origins(self, X: pd.DataFrame) -> pd.DataFrame:
        """
        Filter the data frame with origin time column to have only the latest origins.

        If origin time column is not present, the data frame will be returned as is.
        **NOTE** This method modifies X to avoid copying big data.
        :param X: The time series data frame to be filtered.
        :type X: pd.DataFrame
        :returns: The filtered data frame.
        :rtype: pd.DataFrame

        """
        test_df = X.copy()
        # If test_df has non plain index, reset it, but keep.
        if isinstance(test_df.index, pd.MultiIndex):
            test_df.reset_index(drop=False, inplace=True)
        list_index = [self.time_column_name] + self.grain_column_names
        if self.origin_col_name in test_df.columns:
            # Take the latest
            last_ot = test_df.groupby(list_index, as_index=False)[
                self.origin_col_name].max()
            # Apply the filter.
            list_index.append(self.origin_col_name)
            test_df = pd.merge(
                left=test_df,
                right=last_ot,
                how='inner',
                on=list_index)
            # Make sure that index begins from 1.
            test_df.reset_index(inplace=True, drop=True)
        return test_df

    def apply_time_series_transform(self,
                                    X: pd.DataFrame,
                                    y: np.ndarray = None) -> pd.DataFrame:
        """
        Apply all time series transforms to the data frame X.

        :param X: The data frame to be transformed.
        :type X: pd.DataFrame
        :returns: The transformed data frame, having date, grain and origin
                  columns as indexes.
        :rtype: pd.DataFrame

        """
        X_copy = X.copy()
        if y is not None:
            X_copy[self.target_column_name] = y
        for i in range(len(self.pipeline.steps) - 1):
            # FIXME: Work item #400231
            if type(self.pipeline.steps[i][1]).__name__ == 'TimeSeriesTransformer':
                y = None
                if self.target_column_name in X_copy:
                    y = X_copy.pop(self.target_column_name).values
                X_copy = self.pipeline.steps[i][1].transform(X_copy, y)
                # When we made a time series transformation we need to break and return X.
                X_copy = self.get_latest_origins(X_copy)
                # Restore the index after it was dropped by get_latest_origins().
                ix = [self.time_column_name] + self.grain_column_names
                if self.origin_col_name in X_copy.columns:
                    ix.append(self.origin_col_name)
                X_copy.set_index(ix, drop=True, inplace=True)
                X_copy.sort_index(inplace=True)
                # If the target column was created by featurizers, drop it.
                if self.target_column_name in X_copy:
                    X_copy.drop(self.target_column_name, axis=1, inplace=True)
                return X_copy
            else:
                X_copy = self.pipeline.steps[i][1].transform(X_copy)

    def _lag_or_rw_enabled(self) -> bool:
        return self._ts_transformer._transforms.get(
            constants.TimeSeriesInternal.LAG_LEAD_OPERATOR) is not None or\
            self._ts_transformer._transforms.get(
            constants.TimeSeriesInternal.ROLLING_WINDOW_OPERATOR) is not None

    def _get_last_known_y(self,
                          X: pd.DataFrame,
                          ignore_data_errors: bool) -> Dict[str, pd.Timestamp]:
        """
        Return the value of date for the last known y.

        If no y is known for given grain, corresponding date is not returned.
        If y contains non contiguous numbers or NaNs the DataException is raised.
        :param X: The data frame. We need to make sure that y values
                  does not contain gaps.
        :param ignore_data_errors: Ignore errors in user data.
        :returns: dict containing grain->latest date for which y is known.
        :raises: DataException

        """
        dict_data = {}  # type: Dict[str, pd.Timestamp]
        if self.grain_column_names[0] == constants.TimeSeriesInternal.DUMMY_GRAIN_COLUMN:
            self._add_to_dict_maybe(
                dict_data, self._get_last_y_one_grain(
                    X, ignore_data_errors), self.grain_column_names[0])
        else:
            for grain, df_one in X.groupby(
                    self.grain_column_names, as_index=False):
                self._add_to_dict_maybe(
                    dict_data, self._get_last_y_one_grain(
                        df_one, ignore_data_errors), grain)
        for grain in self._ts_transformer.dict_latest_date.keys():
            data = dict_data.get(grain)
            if data is not None and data < self._ts_transformer.dict_latest_date.get(
                    grain):
                dict_data[grain] = self._ts_transformer.dict_latest_date.get(grain)
        return dict_data

    def _add_to_dict_maybe(self,
                           dt,
                           date,
                           grain):
        """Add date to dict if it is not None."""
        if date is not None:
            dt[grain] = date

    def _get_last_y_one_grain(self,
                              df_grain: pd.DataFrame,
                              ignore_data_errors: bool) -> Optional[pd.Timestamp]:
        """
        Get the date for the last known y.

        This y will be used in transformation, but will not be used
        in prediction (the data frame will be trimmed).
        :param df_grain: The data frame corresponding to single grain.
        :param ignore_data_errors: Ignore errors in user data.
        :returns: The date corresponding to the last known y or None.
        """
        # Make sure that frame is sorted by the time index.
        df_grain.set_index(self._time_col_name, inplace=True)
        df_grain.sort_index(inplace=True)
        df_grain.reset_index(drop=False, inplace=True)
        y = df_grain[constants.TimeSeriesInternal.DUMMY_TARGET_COLUMN].values
        nan_indexes = np.where(pd.isnull(y))
        if nan_indexes[0].size == 0:
            self._warn_or_raise(
                ForecastingPipelineWrapper.ERR_NOTHING_TO_PREDICT,
                ignore_data_errors)
            return pd.Timestamp(max(df_grain[self._time_col_name].values))
        elif np.amin(nan_indexes) == 0:
            # We do not have any known y.
            return None
        first_date = df_grain[self._time_col_name].values[max(
            np.amin(nan_indexes) - 1, 0)]
        if nan_indexes[0].size > 0:
            first_nan = np.amin(nan_indexes)
            if not all([pd.isnull(x) for x in y[first_nan:]]):
                self._warn_or_raise(
                    ForecastingPipelineWrapper.ERR_NON_CONTIGUOUS_Y,
                    ignore_data_errors)
                # In this case we need to return the last contiguous NaN.
                first_date = df_grain[self._time_col_name].values[max(
                    np.amax(nan_indexes) - 1, 0)]
        return pd.Timestamp(first_date)

    def _warn_or_raise(
            self,
            warning_text: str,
            ignore_data_errors: bool) -> None:
        """
        Raise DataException if the warnings_as_errors is True.

        :param warning_text: The text of error or warning.
        :param ignore_data_errors: if True raise the error, warn otherwise.
        """
        if ignore_data_errors:
            warnings.warn(warning_text)
        else:
            raise DataException(warning_text)

    def forecast_quantiles(self,
                           X_pred: Optional[pd.DataFrame] = None,
                           y_pred: Optional[Union[pd.DataFrame, np.ndarray]] = None,
                           forecast_destination: Optional[pd.Timestamp] = None,
                           ignore_data_errors: bool = False) -> pd.DataFrame:
        """
        Get the prediction and quantiles from the fitted pipeline.

        :param X_pred: The data to predict on.
        :param y_pred: The data predicted y.
        :param forecast_destination: The forecasting destination.
        :param ignore_data_errors: Whether or not to ignore data errors.
        :return: The requested prediction.
        """
        pred, transformed_data = self.forecast(X_pred, y_pred, forecast_destination, ignore_data_errors)
        NOT_KNOWN_Y = 'y_not_known'
        if X_pred is not None:
            # Figure out last known y for each grain.
            X_copy = X_pred.copy()
            X_copy[self.target_column_name] = y_pred

            # add dummy grain if needed to df
            if self.grain_column_names[0] == constants.TimeSeriesInternal.DUMMY_GRAIN_COLUMN and \
                    self.grain_column_names[0] not in X_copy.columns:
                X_copy[constants.TimeSeriesInternal.DUMMY_GRAIN_COLUMN] = \
                    constants.TimeSeriesInternal.DUMMY_GRAIN_COLUMN
            # ensure time column is a datetime type
            X_copy[self._time_col_name] = pd.to_datetime(X_copy[self._time_col_name].values)
            X_copy = self._infer_missing_data(X_copy, ignore_data_errors)
            # We ignore user errors, because if desired it was already rose.
            dict_known = self._get_last_known_y(X_copy, True)
            dfs = []
            for grain, df_one in transformed_data.groupby(self.grain_column_names):
                if grain in dict_known.keys():
                    # Some y values are known for the given grain.
                    # df_one.index.levels[0] is a time index. df_one is sorted by index.
                    df_one[NOT_KNOWN_Y] = df_one.index.levels[0] > dict_known[grain]
                else:
                    # Nothing is known. All data represent forecast.
                    df_one[NOT_KNOWN_Y] = True
                dfs.append(df_one)
            transformed_data = pd.concat(dfs)
            # Make sure we did not disturbed index.
            transformed_data.sort_index(inplace=True)
            # Make sure y is aligned to data frame.
            pred = transformed_data[TimeSeriesInternal.DUMMY_TARGET_COLUMN].values
        else:
            # If we have only destination date no y is known.
            transformed_data[NOT_KNOWN_Y] = True
        horizon_stddevs = np.zeros(len(pred))
        try:
            if self._horizon_idx is None:
                self._horizon_idx = cast(int,
                                         self._ts_transformer.get_engineered_feature_names().index('horizon_origin'))
        except ValueError:
            self._horizon_idx = None

        if self._horizon_idx:
            # If we know value for given horizon, its standard deviation is zero.
            is_known = transformed_data[NOT_KNOWN_Y].values.astype(int)
            horizons = transformed_data.values[:, self._horizon_idx].astype(int)
            for idx, horizon in enumerate(horizons):
                horizon = horizon - 1  # horizon needs to be 1 indexed
                try:
                    horizon_stddevs[idx] = self._stddev[horizon] * is_known[idx]
                except IndexError:
                    # In case of short training set cv may have nor estimated
                    # stdev for highest horizon(s). Fix it by returning np.NaN
                    horizon_stddevs[idx] = np.NaN
        else:
            horizon_stddevs.fill(self._stddev[0])

        return self._get_ci(pred, horizon_stddevs, self._quantiles)

    def _postprocess_output(self,
                            X: pd.DataFrame,
                            known_y: Optional[pd.Series]) -> pd.DataFrame:
        """
        Postprocess the data before returning it to user.

        Trim the data frame to the size of input.
        :param X: The data frame to be trimmed.
        :param known_y: The known or inferred y values.
                        We need to replace the existing values by them
        :returns: The data frame with the gap removed.

        """
        # If user have provided known y values, replace forecast by them even
        # if these values were imputed.
        if known_y is not None and any(not pd.isnull(val) for val in known_y):
            PRED_TARGET = 'forecast'
            known_df = pd.DataFrame({TimeSeriesInternal.DUMMY_TARGET_COLUMN: known_y})
            known_df.reset_index(drop=False, inplace=True)
            X.rename({TimeSeriesInternal.DUMMY_TARGET_COLUMN: PRED_TARGET}, axis=1, inplace=True)
            # Align known y and X
            X_merged = X.merge(known_df, on=known_y.index.names, how='inner')
            assert(X_merged.shape[0] == X.shape[0])
            # Replace all NaNs in the known y column by forecast.

            def swap(x):
                return x[PRED_TARGET] if pd.isnull(
                    x[TimeSeriesInternal.DUMMY_TARGET_COLUMN]) else x[TimeSeriesInternal.DUMMY_TARGET_COLUMN]

            X_merged[TimeSeriesInternal.DUMMY_TARGET_COLUMN] = X_merged.apply(lambda x: swap(x), axis=1)
            X = X_merged.drop(PRED_TARGET, axis=1)
        # If user provided X_pred, make sure returned data frame does not contain the inferred
        # gap between train and test.
        if self.forecast_origin:  # Filter only if we were provided by data frame.
            df_list = []
            for grain, df in X.groupby(
                    self.grain_column_names, as_index=False):
                if grain in self.forecast_origin.keys():
                    df = df[df[self._time_col_name] >= self.forecast_origin.get(grain)]
                df_list.append(df)
            return pd.concat(df_list)
        # self.forecast_origin dictionary is empty, no trimming required.
        return X


class PipelineWithYTransformations(sklearn.pipeline.Pipeline):
    """
    Pipeline transformer class.

    Pipeline and y_transformer are assumed to be already initialized.

    But fit could change this to allow for passing the parameters of the
    pipeline and y_transformer.

    :param pipeline: sklearn.pipeline.Pipeline object.
    :type pipeline: sklearn.pipeline.Pipeline
    :param y_trans_name: Name of y transformer.
    :type y_trans_name: string
    :param y_trans_obj: Object that computes a transformation on y values.
    :return: Object of class PipelineWithYTransformations.
    """

    def __init__(self, pipeline, y_trans_name, y_trans_obj):
        """
        Pipeline and y_transformer are assumed to be already initialized.

        But fit could change this to allow for passing the parameters of the
        pipeline and y_transformer.

        :param pipeline: sklearn.pipeline.Pipeline object.
        :type pipeline: sklearn.pipeline.Pipeline
        :param y_trans_name: Name of y transformer.
        :type y_trans_name: string
        :param y_trans_obj: Object that computes a transformation on y values.
        :return: Object of class PipelineWithYTransformations.
        """
        self.pipeline = pipeline
        self.y_transformer_name = y_trans_name
        self.y_transformer = y_trans_obj
        self.steps = pipeline.__dict__.get("steps")

    def __str__(self):
        """
        Return transformer details into string.

        return: string representation of pipeline transform.
        """
        return "%s\nY_transformer(['%s', %s])" % (self.pipeline.__str__(),
                                                  self.y_transformer_name,
                                                  self.y_transformer.__str__())

    def fit(self, X, y, y_min=None, **kwargs):
        """
        Fit function for pipeline transform.

        Perform the fit_transform of y_transformer, then fit into the sklearn.pipeline.Pipeline.

        :param X: Input training data.
        :type X: numpy.ndarray or scipy.spmatrix
        :param y: Input target values.
        :type y: numpy.ndarray
        :param y_min: Minimum value of y, will be inferred if not set.
        :type y_min: numpy.ndarray
        :param kwargs: Other parameters
        :type kwargs: dict
        :return: self: Returns an instance of PipelineWithYTransformations.
        """
        self.pipeline.fit(X, self.y_transformer.fit_transform(y, y_min=y_min), **kwargs)
        return self

    def fit_predict(self, X, y, y_min=None):
        """
        Fit predict function for pipeline transform.

        :param X: Input data.
        :type X: numpy.ndarray or scipy.spmatrix
        :param y: Input target values.
        :type y: numpy.ndarray
        :param y_min: Minimum value of y, will be inferred if not set.
        :type y_min: numpy.ndarray
        :return: Prediction values after performing fit.
        """
        return self.fit(X, y, y_min).predict(X)

    def get_params(self, deep=True):
        """
        Return parameters for Pipeline Transformer.

        :param deep:
            If True, will return the parameters for this estimator
            and contained subobjects that are estimators.
        :type deep: bool
        :return: Parameters for Pipeline Transformer.
        """
        return {
            "Pipeline": self.pipeline.get_params(deep),
            "y_transformer": self.y_transformer.get_params(deep),
            "y_transformer_name": self.y_transformer_name
        }

    def predict(self, X):
        """
        Prediction function for Pipeline Transformer.

        Perform the prediction of sklearn.pipeline.Pipeline, then do the inverse transform from y_transformer.

        :param X: Input samples.
        :type X: numpy.ndarray or scipy.spmatrix
        :return: Prediction values from Pipeline Transformer.
        :rtype: array
        """
        return self.y_transformer.inverse_transform(self.pipeline.predict(X))


class QuantileTransformerWrapper(BaseEstimator, TransformerMixin):
    """
    Quantile transformer wrapper class.

    Transform features using quantiles information.

    :param n_quantiles:
        Number of quantiles to be computed. It corresponds to the number
        of landmarks used to discretize the cumulative density function.
    :type n_quantiles: int
    :param output_distribution:
        Marginal distribution for the transformed data.
        The choices are 'uniform' (default) or 'normal'.
    :type output_distribution: string

    Read more at:
    http://scikit-learn.org/stable/modules/generated/sklearn.preprocessing.QuantileTransformer.html.
    """

    def __init__(self, n_quantiles=1000, output_distribution="uniform"):
        """
        Initialize function for Quantile transformer.

        :param n_quantiles:
            Number of quantiles to be computed. It corresponds to the number
            of landmarks used to discretize the cumulative density function.
        :type n_quantiles: int
        :param output_distribution:
            Marginal distribution for the transformed data.
            The choices are 'uniform' (default) or 'normal'.
        :type output_distribution: string
        """
        self.transformer = preprocessing.QuantileTransformer(
            n_quantiles=n_quantiles,
            output_distribution=output_distribution)

    def __str__(self):
        """
        Return transformer details into string.

        return: String representation of Quantile transform.
        """
        return self.transformer.__str__()

    def fit(self, y):
        """
        Fit function for Quantile transform.

        :param y: The data used to scale along the features axis.
        :type y: numpy.ndarray or scipy.spmatrix
        :return: Object of QuantileTransformerWrapper.
        :rtype: QuantileTransformerWrapper
        """
        self.transformer.fit(y.reshape(-1, 1))
        return self

    def get_params(self, deep=True):
        """
        Return parameters of Quantile transform as dictionary.

        :param deep:
            If True, will return the parameters for this estimator
            and contained subobjects that are estimators.
        :type deep: bool
        :return: Dictionary of Quantile transform parameters.
        """
        return {
            "transformer": self.transformer.get_params(deep=deep)
        }

    def transform(self, y):
        """
        Transform function for Quantile transform.

        :param y: The data used to scale along the features axis.
        :type y: numpy.ndarray or scipy.spmatrix
        :return: The projected data of Quantile transform.
        :rtype: numpy.ndarray or scipy.spmatrix
        """
        return self.transformer.transform(y.reshape(-1, 1)).reshape(-1)

    def inverse_transform(self, y):
        """
        Inverse transform function for Quantile transform. Back-projection to the original space.

        :param y: The data used to scale along the features axis.
        :type y: numpy.ndarray or scipy.spmatrix
        :return: The projected data of Quantile inverse transform.
        :rtype: numpy.ndarray or scipy.spmatrix
        """
        return self.transformer.inverse_transform(y.reshape(-1, 1)).reshape(-1)


class IdentityTransformer(BaseEstimator, TransformerMixin):
    """
    Identity transformer class.

    Returns the same X it accepts.
    """

    def fit(self,
            X: np.ndarray,
            y: Optional[np.ndarray] = None) -> Any:
        """
        Take X and does nothing with it.

        :param X: Features to transform.
        :param y: Target values.
        :return: This transformer.
        """
        return self

    def transform(self,
                  X: np.ndarray,
                  y: Optional[np.ndarray] = None) -> np.ndarray:
        """
        Perform the identity transform.

        :param X: Features to tranform.
        :param y: Target values.
        :return: The same X that was passed
        """
        return X


class LogTransformer(BaseEstimator, TransformerMixin):
    """
    Log transformer class.

    :param safe:
        If true, truncate values outside the transformer's
        domain to the nearest point in the domain.
    :type safe: boolean
    :return: Object of class LogTransformer.

    """

    def __init__(self, safe=True):
        """
        Initialize function for Log transformer.

        :param safe:
            If true, truncate values outside the transformer's
            domain to the nearest point in the domain.
        :type safe: boolean
        :return: Object of class LogTransformer.
        """
        self.base = np.e
        self.y_min = None
        self.scaler = None
        self.lower_range = 1e-5
        self.safe = safe

    def __str__(self):
        """
        Return transformer details into string.

        return: string representation of Log transform.
        """
        return "LogTransformer(base=e, y_min=%.5f, scaler=%s, safe=%s)" % \
               (self.y_min if self.y_min is not None else 0,
                self.scaler,
                self.safe)

    def fit(self, y, y_min=None):
        """
        Fit function for Log transform.

        :param y: Input training data.
        :type y: numpy.ndarray
        :param y_min: Minimum value of y, will be inferred if not set
        :type y_min: double
        :return: Returns an instance of the LogTransformer model.
        """
        if y_min is None:
            self.y_min = np.min(y)
        else:
            if (y_min is not None) and y_min <= np.min(y):
                self.y_min = y_min
            else:
                self.y_min = np.min(y)
                warnings.warn(
                    'Caution: y_min greater than observed minimum in y')

        if self.y_min > self.lower_range:
            self.y_min = self.lower_range
            self.scaler = preprocessing.StandardScaler(
                copy=False, with_mean=False,
                with_std=False).fit(y.reshape(-1, 1))
        else:
            y_max = np.max(y)
            self.scaler = preprocessing.MinMaxScaler(
                feature_range=(self.lower_range, 1)).fit(
                np.array([y_max, self.y_min]).reshape(-1, 1))

        return self

    def get_params(self, deep=True):
        """
        Return parameters of Log transform as dictionary.

        :param deep:
            If True, will return the parameters for this estimator
            and contained subobjects that are estimators.
        :type deep: boolean
        :return: Dictionary of Log transform parameters.
        """
        return {"base": self.base,
                "y_min": self.y_min,
                "scaler": self.scaler,
                "safe": self.safe
                }

    def return_y(self, y):
        """
        Return log value of y.

        :param y: Input data.
        :type y: numpy.ndarray
        :return: The log transform array.
        """
        return np.log(y)

    def transform(self, y):
        """
        Transform function for Log transform to return the log value.

        :param y: Input data.
        :type y: numpy.ndarray
        :return: The log transform array.
        """
        if self.y_min is None:
            raise Exception('Must fit before transforming')
        elif np.min(y) < self.y_min and \
                np.min(self.scaler.transform(
                    y.reshape(-1, 1)).reshape(-1, )) <= 0:
            if self.safe:
                warnings.warn("y_min greater than observed minimum in y, "
                              "clipping y to domain")
                y_copy = y.copy()
                y_copy[y < self.y_min] = self.y_min
                return self.return_y(
                    self.scaler.transform(y_copy.reshape(-1, 1)).reshape(-1, ))
            else:
                raise Exception('y_min greater than observed minimum in y')
        else:
            return self.return_y(
                self.scaler.transform(y.reshape(-1, 1)).reshape(-1, ))

    def inverse_transform(self, y):
        """
        Inverse transform function for Log transform.

        :param y: Input data.
        :type y: numpy.ndarray
        :return: Inverse Log transform.
        """
        # this inverse transform has no restrictions, can exponetiate anything
        if self.y_min is None:
            raise Exception('Must fit before transforming')
        else:
            return self.scaler.inverse_transform(
                np.exp(y).reshape(-1, 1)).reshape(-1, )


class PowerTransformer(BaseEstimator, TransformerMixin):
    """
    Power transformer class.

    :param power: Power to raise y values to.
    :type power: double
    :param safe:
        If true, truncate values outside the transformer's domain to
        the nearest point in the domain.
    :type safe: boolean
    """

    def __init__(self, power=1, safe=True):
        """
        Initialize function for Power transformer.

        :param power: Power to raise y values to.
        :type power: double
        :param safe:
            If true, truncate values outside the transformer's domain
            to the nearest point in the domain.
        :type safe: boolean
        """
        # power = 1 is the identity transformation
        self.power = power
        self.y_min = None
        self.accept_negatives = False
        self.lower_range = 1e-5
        self.scaler = None
        self.safe = safe

        # check if the exponent is everywhere defined
        if self.power > 0 and \
                (((self.power % 2 == 1) or (1 / self.power % 2 == 1)) or
                 (self.power % 2 == 0 and self.power > 1)):
            self.accept_negatives = True
            self.y_min = -np.inf
            self.offset = 0
            self.scaler = preprocessing.StandardScaler(
                copy=False, with_mean=False, with_std=False).fit(
                np.array([1], dtype=float).reshape(-1, 1))

    def __str__(self):
        """
        Return transformer details into string.

        return: String representation of Power transform.
        """
        return \
            "PowerTransformer(power=%.1f, y_min=%.5f, scaler=%s, safe=%s)" % (
                self.power,
                self.y_min if self.y_min is not None else 0,
                self.scaler,
                self.safe)

    def return_y(self, y, power, invert=False):
        """
        Return some 'power' of 'y'.

        :param y: Input data.
        :type y: numpy.ndarray
        :param power: Power value.
        :type power: double
        :param invert:
            A boolean whether or not to perform the inverse transform.
        :type invert: boolean
        :return: The transformed targets.
        """
        # ignore invert, the power has already been inverted
        # can ignore invert because no offsetting has been done
        if self.accept_negatives:
            if np.any(y < 0):
                mult = np.sign(y)
                y_inter = np.multiply(np.power(np.absolute(y), power), mult)
            else:
                y_inter = np.power(y, power)
        else:
            # these are ensured to only have positives numbers as inputs
            y_inter = np.power(y, power)

        if invert:
            return self.scaler.inverse_transform(
                y_inter.reshape(-1, 1)).reshape(-1, )
        else:
            return y_inter

    def get_params(self, deep=True):
        """
        Return parameters of Power transform as dictionary.

        :param deep:
            If True, will return the parameters for this estimator
            and contained subobjects that are estimators.
        :type deep: boolean
        :return: Dictionary of Power transform parameters.
        """
        return {
            "power": self.power,
            "scaler": self.scaler,
            "y_min": self.y_min,
            "accept_negatives": self.accept_negatives,
            "safe": self.safe
        }

    def fit(self, y, y_min=None):
        """
        Fit function for Power transform.

        :param y: Input training data.
        :type y: numpy.ndarray
        :param y_min: Minimum value of y, will be inferred if not set.
        :type y_min: double
        :return: Returns an instance of the PowerTransformer model.
        """
        if y_min is None:
            self.y_min = np.min(y)
        else:
            if (y_min is not None) and y_min <= np.min(y):
                self.y_min = y_min
            else:
                self.y_min = np.min(y)
                warnings.warn(
                    'Caution: y_min greater than observed minimum in y')

        if self.y_min > self.lower_range:
            self.y_min = self.lower_range
            self.scaler = preprocessing.StandardScaler(
                copy=False, with_mean=False,
                with_std=False).fit(y.reshape(-1, 1))
        else:
            y_max = np.max(y)
            self.scaler = preprocessing.MinMaxScaler(
                feature_range=(self.lower_range, 1)).fit(
                np.array([y_max, self.y_min]).reshape(-1, 1))
        return self

    def transform(self, y):
        """
        Transform function for Power transform.

        :param y: Input data.
        :type y: numpy.ndarray
        :return: Power transform result.
        """
        if self.y_min is None and not (self.power > 0 and self.power % 2 == 1):
            raise Exception('Must fit before transforming')
        elif np.min(y) < self.y_min and not self.accept_negatives and np.min(
                self.scaler.transform(y.reshape(-1, 1)).reshape(-1, )) <= 0:
            if self.safe:
                warnings.warn(
                    "y_min greater than observed minimum in y, clipping y to "
                    "domain")
                y_copy = y.copy()
                y_copy[y < self.y_min] = self.y_min
                return self.return_y(
                    self.scaler.transform(y_copy.reshape(-1, 1)).reshape(-1, ),
                    self.power, invert=False)
            else:
                raise Exception('y_min greater than observed minimum in y')
        else:
            return self.return_y(
                self.scaler.transform(y.reshape(-1, 1)).reshape(-1, ),
                self.power, invert=False)

    def inverse_transform(self, y):
        """
        Inverse transform function for Power transform.

        :param y: Input data.
        :type y: numpy.ndarray
        :return: Inverse Power transform result.
        """
        if self.y_min is None and \
                not (self.power > 0 and self.power % 2 == 1):
            raise Exception('Must fit before transforming')
        elif not self.accept_negatives and np.min(y) <= 0:
            if self.safe:
                warnings.warn(
                    "y_min greater than observed minimum in y, clipping y to "
                    "domain")
                transformed_min = np.min(y[y > 0])
                y_copy = y.copy()
                y_copy[y < transformed_min] = transformed_min
                return self.return_y(y_copy, 1 / self.power, invert=True)
            else:
                raise Exception('y_min greater than observed minimum in y')
        else:
            return self.return_y(y, 1 / self.power, invert=True)


class BoxCoxTransformerScipy(BaseEstimator, TransformerMixin):
    """
    Box Cox transformer class for normalizing non-normal data.

    :param lambda_val:
        Lambda value for Box Cox transform, will be inferred if not set.
    :type lambda_val: double
    :param safe:
        If true, truncate values outside the transformer's domain to
        the nearest point in the domain.
    :type safe: boolean
    """

    def __init__(self, lambda_val=None, safe=True):
        """
        Initialize function for Box Cox transformer.

        :param lambda_val:
            Lambda value for Box Cox transform, will be inferred if not set.
        :type lambda_val: double
        :param safe:
            If true, truncate values outside the transformer's domain
            to the nearest point in the domain.
        :type safe: boolean
        """
        # can also use lambda_val = 0 as equivalent to natural log transformer
        self.lambda_val = lambda_val
        self.lower_range = 1e-5
        self.y_min = None
        self.scaler = None
        self.fitted = False
        self.safe = safe

    def __str__(self):
        """
        Return transformer details into string.

        return: String representation of Box Cox transform.
        """
        return ("BoxCoxTransformer(lambda=%.3f, y_min=%.5f, scaler=%s, "
                "safe=%s)" %
                (self.lambda_val if self.lambda_val is not None else 0,
                 self.y_min if self.y_min is not None else 0,
                 self.scaler,
                 self.safe))

    def fit(self, y, y_min=None):
        """
        Fit function for Box Cox transform.

        :param y: Input training data.
        :type y: numpy.ndarray
        :param y_min: Minimum value of y, will be inferred if not set.
        :type y_min: double
        :return: Returns an instance of the BoxCoxTransformerScipy model.
        """
        self.fitted = True
        if y_min is None:
            self.y_min = np.min(y)
        else:
            if (y_min is not None) and y_min <= np.min(y):
                self.y_min = y_min
            else:
                self.y_min = np.min(y)
                warnings.warn(
                    'Caution: y_min greater than observed minimum in y')
        if self.y_min > self.lower_range:
            self.y_min = self.lower_range
            self.scaler = preprocessing.StandardScaler(
                copy=False,
                with_mean=False,
                with_std=False).fit(y.reshape(-1, 1))
        else:
            y_max = np.max(y)
            self.scaler = preprocessing.MinMaxScaler(
                feature_range=(self.lower_range, 1)).fit(
                np.array([y_max, self.y_min]).reshape(-1, 1))

        # reset if already fitted
        if self.lambda_val is None or self.fitted:
            y, self.lambda_val = boxcox(
                self.scaler.transform(y.reshape(-1, 1)).reshape(-1, ))
        return self

    def get_params(self, deep=True):
        """
        Return parameters of Box Cox transform as dictionary.

        :param deep:
            If True, will return the parameters for this estimator
            and contained subobjects that are estimators.
        :type deep: boolean
        :return: Dictionary of Box Cox transform parameters.
        """
        return {"lambda": self.lambda_val,
                "y_min": self.y_min,
                "scaler": self.scaler,
                "safe": self.safe
                }

    def transform(self, y):
        """
        Transform function for Box Cox transform.

        :param y: Input data.
        :type y: numpy.ndarray
        :return: Box Cox transform result.
        """
        if self.lambda_val is None:
            raise Exception('Must fit before transforming')
        elif np.min(y) < self.y_min and \
                np.min(
                    self.scaler.transform(y.reshape(-1, 1)).reshape(-1, )) <= 0:
            if self.safe:
                warnings.warn("y_min greater than observed minimum in y, "
                              "clipping y to domain")
                y_copy = y.copy()
                y_copy[y < self.y_min] = self.y_min
                return boxcox(
                    self.scaler.transform(y_copy.reshape(-1, 1)).reshape(-1, ),
                    self.lambda_val)
            else:
                raise Exception('y_min greater than observed minimum in y')
        else:
            return boxcox(
                self.scaler.transform(y.reshape(-1, 1)).reshape(-1, ),
                self.lambda_val)

    def inverse_transform(self, y):
        """
        Inverse transform function for Box Cox transform.

        :param y: Input data.
        :type y: numpy.ndarray
        :return: Inverse Box Cox transform result.
        """
        # inverse box_cox can take any number
        if self.lambda_val is None:
            raise Exception('Must fit before transforming')
        else:
            return self.scaler.inverse_transform(
                inv_boxcox(y, self.lambda_val).reshape(-1, 1)).reshape(-1, )


class PreFittedSoftVotingClassifier(VotingClassifier):
    """
    Pre-fitted Soft Voting Classifier class.

    :param estimators: Models to include in the PreFittedSoftVotingClassifier
    :type estimators: list of (string, estimator) tuples
    :param weights: Weights given to each of the estimators
    :type weights: numpy.ndarray
    :param flatten_transform:
        If True, transform method returns matrix with
        shape (n_samples, n_classifiers * n_classes).
        If False, it returns (n_classifiers, n_samples,
        n_classes).
    :type flatten_transform: boolean
    """

    def __init__(
            self, estimators, weights=None, flatten_transform=None,
            classification_labels=None):
        """
        Initialize function for Pre-fitted Soft Voting Classifier class.

        :param estimators:
            Models to include in the PreFittedSoftVotingClassifier
        :type estimators: list of (string, estimator) tuples
        :param weights: Weights given to each of the estimators
        :type weights: numpy.ndarray
        :param flatten_transform:
            If True, transform method returns matrix with
            shape (n_samples, n_classifiers * n_classes).
            If False, it returns (n_classifiers, n_samples, n_classes).
        :type flatten_transform: boolean
        """
        super().__init__(estimators=estimators,
                         voting='soft',
                         weights=weights,
                         flatten_transform=flatten_transform)
        self.estimators_ = [est[1] for est in estimators]
        if classification_labels is None:
            self.le_ = LabelEncoder().fit([0])
        else:
            self.le_ = LabelEncoder().fit(classification_labels)
        # Fill the classes_ property of VotingClassifier which is calculated
        # during fit.
        # This is important for the ONNX convert, when parsing the model object.
        self.classes_ = self.le_.classes_


class PreFittedSoftVotingRegressor(BaseEstimator, RegressorMixin):
    """
    Pre-fitted Soft Voting Regressor class.

    :param estimators: Models to include in the PreFittedSoftVotingRegressor
    :type estimators: list of (string, estimator) tuples
    :param weights: Weights given to each of the estimators
    :type weights: numpy.ndarray
    :param flatten_transform:
        If True, transform method returns matrix with
        shape (n_samples, n_classifiers). If False, it
        returns (n_classifiers, n_samples, 1).
    :type flatten_transform: boolean
    """

    def __init__(self, estimators, weights=None, flatten_transform=None):
        """
        Initialize function for Pre-fitted Soft Voting Regressor class.

        :param estimators:
            Models to include in the PreFittedSoftVotingRegressor
        :type estimators: list of (string, estimator) tuples
        :param weights: Weights given to each of the estimators
        :type weights: numpy.ndarray
        :param flatten_transform:
            If True, transform method returns matrix with
            shape (n_samples, n_classifiers). If False, it
            returns (n_classifiers, n_samples, 1).
        :type flatten_transform: boolean
        """
        self._wrappedEnsemble = PreFittedSoftVotingClassifier(
            estimators, weights, flatten_transform, classification_labels=[0])

    def fit(self, X, y, sample_weight=None):
        """
        Fit function for PreFittedSoftVotingRegressor model.

        :param X: Input data.
        :type X: numpy.ndarray or scipy.spmatrix
        :param y: Input target values.
        :type y: numpy.ndarray
        :param sample_weight: If None, then samples are equally weighted. This is only supported if all
            underlying estimators support sample weights.
        """
        return self._wrappedEnsemble.fit(X, y, sample_weight)

    def predict(self, X):
        """
        Predict function for Pre-fitted Soft Voting Regressor class.

        :param X: Input data.
        :type X: numpy.ndarray
        :return: Weighted average of predicted values.
        """
        predicted = self._wrappedEnsemble._predict(X)
        return np.average(predicted, axis=1, weights=self._wrappedEnsemble.weights)

    def get_params(self, deep=True):
        """
        Return parameters for Pre-fitted Soft Voting Regressor model.

        :param deep:
            If True, will return the parameters for this estimator
            and contained subobjects that are estimators.
        :type deep: boolean
        :return: dictionary of parameters
        """
        state = {
            "estimators": self._wrappedEnsemble.estimators,
            "weights": self._wrappedEnsemble.weights,
            "flatten_transform": self._wrappedEnsemble.flatten_transform
        }
        return state

    def set_params(self, **params):
        """
        Set the parameters of this estimator.

        :return: self
        """
        return super(PreFittedSoftVotingRegressor, self).set_params(**params)

    def __setstate__(self, state):
        """
        Set state for object reconstruction.

        :param state: pickle state
        """
        if '_wrappedEnsemble' in state:
            self._wrappedEnsemble = state['_wrappedEnsemble']
        else:
            # ensure we can load state from previous version of this class
            self._wrappedEnsemble = PreFittedSoftVotingClassifier(
                state['estimators'], state['weights'], state['flatten_transform'], classification_labels=[0])


class StackEnsembleBase(ABC, _BaseComposition):
    """StackEnsemble class. Represents a 2 layer Stacked Ensemble."""

    def __init__(self, base_learners, meta_learner, training_cv_folds=5):
        """
        Initialize function for StackEnsemble.

        :param base_learners:
            The collection of (name, estimator) for the base layer of the Ensemble
        :type base_learners: list of tuple of (string, Pipeline)
        :param meta_learner:
            The model used in the second layer of the Stack to generate the final predictions.
        :type meta_learner: Estimator / Pipeline
        :param training_cv_folds:
            The number of cross validation folds to be used during fitting of this Ensemble.
        :type training_cv_folds: int
        """
        super().__init__()
        self._base_learners = base_learners
        self._meta_learner = meta_learner
        self._training_cv_folds = training_cv_folds

    def fit(self, X: DataInputType, y: np.ndarray) -> 'StackEnsembleBase':
        """
        Fit function for StackEnsemble model.

        :param X: Input data.
        :param y: Input target values.
        :type y: numpy.ndarray
        :return: Returns self.
        """
        predictions = None  # type: np.ndarray

        # cache the CV split indices into a list
        cv_indices = list(self._get_cv_split_indices(X, y))

        y_out_of_fold_concat = None
        for _, test_indices in cv_indices:
            y_test = y[test_indices]
            if y_out_of_fold_concat is None:
                y_out_of_fold_concat = y_test
            else:
                y_out_of_fold_concat = np.concatenate((y_out_of_fold_concat, y_test))

        for index, (_, learner) in enumerate(self._base_learners):
            temp = None  # type: np.ndarray
            for train_indices, test_indices in cv_indices:
                X_train, X_test = X[train_indices], X[test_indices]
                y_train, y_test = y[train_indices], y[test_indices]
                cloned_learner = clone(learner)
                cloned_learner.fit(X_train, y_train)

                model_predictions = self._get_base_learner_predictions(cloned_learner, X_test)

                if temp is None:
                    temp = model_predictions
                else:
                    temp = np.concatenate((temp, model_predictions))

                if len(temp.shape) == 1:
                    predictions = np.zeros((y.shape[0], 1, len(self._base_learners)))
                else:
                    predictions = np.zeros((y.shape[0], temp.shape[1], len(self._base_learners)))

            if len(temp.shape) == 1:
                # add an extra dimension so that we can reuse the predictions array
                # across multiple training types
                temp = temp[:, None]
            predictions[:, :, index] = temp

        all_out_of_fold_predictions = []
        for idx in range(len(self._base_learners)):
            # get the vertical concatenation of the out of fold predictions from the selector
            # as they were already computed during the selection phase
            model_predictions = predictions[:, :, idx]
            all_out_of_fold_predictions.append(model_predictions)

        meta_learner_training = self._horizontal_concat(all_out_of_fold_predictions)
        cloned_meta_learner = clone(self._meta_learner)
        cloned_meta_learner.fit(meta_learner_training, y_out_of_fold_concat)

        final_base_learners = []
        for name, learner in self._base_learners:
            final_learner = clone(learner)
            final_learner.fit(X, y)
            final_base_learners.append((name, final_learner))

        self._base_learners = final_base_learners
        self._meta_learner = cloned_meta_learner

        return self

    def predict(self, X):
        """
        Predict function for StackEnsemble class.

        :param X: Input data.
        :return: Weighted average of predicted values.
        """
        predictions = self._get_base_learners_predictions(X)
        return self._meta_learner.predict(predictions)

    @staticmethod
    def _horizontal_concat(predictions_list: List[np.ndarray]) -> Optional[np.ndarray]:
        """
        Concatenate multiple base learner predictions horizontally.

        Given a list of out-of-fold predictions from base learners, it concatenates these predictions
        horizontally to create one 2D matrix which will be used as training set for the meta learner.
        In case we're dealing with a classification problem, we need to drop one column out of each
        element within the input list, so that the resulting matrix is not collinear (because the sum of all class
        probabilities would be equal to 1 )
        """
        if len(predictions_list) == 0:
            return None
        preds_shape = predictions_list[0].shape
        if len(preds_shape) == 2 and preds_shape[1] > 1:
            # remove first class prediction probabilities so that the matrix isn't collinear
            predictions_list = [np.delete(pred, 0, 1) for pred in predictions_list]
        elif len(preds_shape) == 1:
            # if we end up with a single feature, we'd have a single dimensional array, so we'll need to reshape it
            # in order for SKLearn to accept it as input
            predictions_list = [pred.reshape(-1, 1) for pred in predictions_list if pred.ndim == 1]

        # now let's concatenate horizontally all the predictions
        predictions = np.hstack(predictions_list)
        return predictions

    def _get_base_learners_predictions(self, X: List[np.ndarray]) -> Optional[np.ndarray]:
        predictions = [self._get_base_learner_predictions(estimator, X) for _, estimator in self._base_learners]
        return StackEnsembleBase._horizontal_concat(predictions)

    @abstractmethod
    def _get_cv_split_indices(self, X, y):
        pass

    @abstractmethod
    def _get_base_learner_predictions(self, model, X):
        pass

    def get_params(self, deep=True):
        """
        Return parameters for StackEnsemble model.

        :param deep:
                If True, will return the parameters for this estimator
                and contained subobjects that are estimators.
        :type deep: boolean
        :return: Parameters for the StackEnsemble model.
        """
        result = {
            "base_learners": self._base_learners,
            "meta_learner": self._meta_learner,
            "training_cv_folds": self._training_cv_folds
        }

        if not deep:
            return result

        base_layer_params = super(StackEnsembleBase, self)._get_params("_base_learners", deep=True)
        result.update(base_layer_params)
        meta_params = self._meta_learner.get_params(deep=True)
        for key, value in meta_params.items():
            result['%s__%s' % ("metalearner", key)] = value

        return result


class StackEnsembleClassifier(StackEnsembleBase, ClassifierMixin):
    """StackEnsembleClassifier class using 2 layers."""

    def __init__(self, base_learners, meta_learner, training_cv_folds=5):
        """
        Initialize function for StackEnsembleClassifier.

        :param base_learners:
            The collection of (name, estimator) for the base layer of the Ensemble
        :type base_learners: list of tuple of (string, Pipeline)
        :param meta_learner:
            The model used in the second layer of the Stack to generate the final predictions.
        :type meta_learner: Estimator / Pipeline
        :param training_cv_folds:
            The number of cross validation folds to be used during fitting of this Ensemble.
        :type training_cv_folds: int
        """
        super().__init__(base_learners, meta_learner, training_cv_folds=training_cv_folds)
        if hasattr(meta_learner, "classes_"):
            self.classes_ = meta_learner.classes_
        else:
            self.classes_ = None

    def fit(self, X: DataInputType, y: np.ndarray) -> 'StackEnsembleClassifier':
        """
        Fit function for StackEnsembleClassifier model.

        :param X: Input data.
        :param y: Input target values.
        :type y: numpy.ndarray
        :return: Returns self.
        """
        self.classes_ = np.unique(y)
        return super().fit(X, y)

    def predict_proba(self, X):
        """
        Prediction class probabilities for X from StackEnsemble model.

        :param X: Input data.
        :type X: numpy.ndarray
        :return: Prediction probability values from StackEnsemble model.
        """
        predictions = self._get_base_learners_predictions(X)
        return self._meta_learner.predict_proba(predictions)

    def _get_cv_split_indices(self, X, y):
        result = None
        try:
            kfold = StratifiedKFold(n_splits=self._training_cv_folds)
            result = kfold.split(X, y)
        except Exception as ex:
            print("Error trying to perform StratifiedKFold split. Falling back to KFold. Exception: {}".format(ex))
            # StratifiedKFold fails when there is a single example for a given class
            # so if that happens will fallback to regular KFold
            kfold = KFold(n_splits=self._training_cv_folds)
            result = kfold.split(X, y)

        return result

    def _get_base_learner_predictions(self, model, X):
        result = model.predict_proba(X)
        # let's make sure all the predictions have same number of columns
        if self.classes_ is not None and hasattr(model, "classes_"):
            result = metrics_utils.pad_predictions(result, model.classes_, self.classes_)
        return result


class StackEnsembleRegressor(StackEnsembleBase, RegressorMixin):
    """StackEnsembleRegressor class using 2 layers."""

    def __init__(self, base_learners, meta_learner, training_cv_folds=5):
        """
        Initialize function for StackEnsembleRegressor.

        :param base_learners:
            The collection of (name, estimator) for the base layer of the Ensemble
        :type base_learners: list of tuple of (string, Pipeline)
        :param meta_learner:
            The model used in the second layer of the Stack to generate the final predictions.
        :type meta_learner: Estimator / Pipeline
        :param training_cv_folds:
            The number of cross validation folds to be used during fitting of this Ensemble.
        :type training_cv_folds: int
        """
        super().__init__(base_learners, meta_learner, training_cv_folds=training_cv_folds)

    def _get_base_learner_predictions(self, model, X):
        return model.predict(X)

    def _get_cv_split_indices(self, X, y):
        kfold = KFold(n_splits=self._training_cv_folds)
        return kfold.split(X, y)
