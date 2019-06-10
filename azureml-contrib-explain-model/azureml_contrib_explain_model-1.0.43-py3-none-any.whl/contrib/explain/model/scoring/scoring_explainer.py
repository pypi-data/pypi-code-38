# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

"""Defines scoring models for approximating feature importance values."""

import numpy as np
import logging
import os
from abc import ABCMeta, abstractmethod
from sklearn.externals import joblib

try:
    from azureml._logging import ChainedIdentity
except ImportError:
    from azureml.explain.model.common.chained_identity import ChainedIdentity

from azureml.explain.model._internal.constants import LoggingNamespace
from azureml.explain.model.common.explanation_utils import _get_raw_feature_importances, _get_dense_examples, \
    _transform_data
from azureml.explain.model._internal.raw_explain import DataMapper

import warnings

with warnings.catch_warnings():
    warnings.filterwarnings('ignore', 'Starting from version 2.2.1', UserWarning)
    import shap

LOGGER = '_logger'


class ScoringExplainer(ChainedIdentity):
    """Defines a scoring model."""

    __metaclass__ = ABCMeta

    def __init__(self, data_transformer=None, transformations=None, **kwargs):
        """Initialize the ScoringExplainer.

        :param data_transformer: The pipeline of transformations that should be run on the data
            before explanation. If None, no transformations will be done.
        :type data_transformer: An object implementing .transform()
        :param transformations: sklearn.compose.ColumnTransformer or a list of tuples describing the column name and
            transformer. When transformations are provided, explanations are of the features before the
            transformation. The format for list of transformations is same as the one here:
            https://github.com/scikit-learn-contrib/sklearn-pandas.
            If the user is using a transformation that is not in the list of sklearn.preprocessing transformations that
            we support then we cannot take a list of more than one column as input for the transformation.
            A user can use the following sklearn.preprocessing  transformations with a list of columns since these are
            already one to many or one to one: Binarizer, KBinsDiscretizer, KernelCenterer, LabelEncoder, MaxAbsScaler,
            MinMaxScaler, Normalizer, OneHotEncoder, OrdinalEncoder, PowerTransformer, QuantileTransformer,
            RobustScaler, StandardScaler.
            Examples for transformations that work:
            [
                (["col1", "col2"], sklearn_one_hot_encoder),
                (["col3"], None) #col3 passes as is
            ]
            [
                (["col1"], my_own_transformer),
                (["col2"], my_own_transformer),
            ]
            Example of transformations that would raise an error since it cannot be interpreted as one to many:
            [
                (["col1", "col2"], my_own_transformer)
            ]
            This would not work since it is hard to make out whether my_own_transformer gives a many to many or one to
            many mapping when taking a sequence of columns.
        :type transformations: sklearn.compose.ColumnTransformer or list[tuple]
        """
        super(ScoringExplainer, self).__init__(**kwargs)
        self._logger.debug('Initializing ScoringExplainer')
        if data_transformer is not None and transformations is not None:
            raise Exception('Only one of data_transformer or transformations should be passed.')
        self._data_transformer = data_transformer
        if transformations is not None:
            self._data_mapper = DataMapper(transformations)
        else:
            self._data_mapper = None

    @abstractmethod
    def explain(self, evaluation_examples):
        """Use the model for scoring to approximate the feature importance values of data."""
        pass

    def _get_raw_explanations(self, engineered_importances):
        """Convert from an explanation of engineered features to an explanation of raw features.

        :param engineered_importances: The results of calling .explain() on engineered data.
        :type engineered_importances: np.array
        :return: The importances for the raw features originally passed to the scoring explainer.
        :rtype: np.array
        """
        if self._data_mapper is None:
            raise Exception('Feature map must be passed in to calculate raw feature importances.')
        return _get_raw_feature_importances(engineered_importances, self._data_mapper.feature_map)

    def predict(self, evaluation_examples, ys=None):
        """Use the TreeExplainer and tree model for scoring to get the feature importance values of data.

        Wraps the .explain() function.

        :param evaluation_examples: A matrix of feature vector examples (# examples x # features) on
            which to explain the model's output.
        :type evaluation_examples: numpy.array or pandas.DataFrame or scipy.sparse.csr_matrix
        :param ys: Labels for data, used in time series transformations.
        :type ys: numpy, pandas, dense, sparse data vector
        :return: For a model with a single output such as regression,
            this returns a matrix of feature importance values. For models with vector outputs
            this function returns a list of such matrices, one for each output. The dimension
            of this matrix is (# examples x # features).
        :rtype: list
        """
        return self.explain(evaluation_examples, ys=ys)

    def save(self, name, directory='.'):
        """Save the scoring explainer to disk.

        :param name: The filename under which the pickled scoring explainer should be stored.
        :type name: str
        :param directory: The directory under which the pickle file should be stored.
            If it doesn't exist, it will be created.
        :type directory: str
        :return: The path used.
        :rtype: str
        """
        os.makedirs(directory, exist_ok=True)
        location = os.path.join(directory, name)
        with open(location, 'wb') as stream:
            joblib.dump(self, stream)
        return location

    @staticmethod
    def load(path):
        """Load the scoring explainer from disk.

        :param path: The path under which the pickled scoring explainer was stored.
        :type path: str
        :return: The scoring explainer from an explanation, loaded from disk.
        :rtype: azureml.contrib.explain.model.scoring.scoring_explainer.ScoringExplainer
        """
        with open(path, 'rb') as stream:
            scoring_explainer = joblib.load(stream)
        return scoring_explainer

    def __getstate__(self):
        """Influence how TreeScoringExplainer is pickled.

        Removes logger which is not serializable.

        :return state: The state to be pickled, with logger removed.
        :rtype state: dict
        """
        odict = self.__dict__.copy()
        del odict[LOGGER]
        return odict

    def __setstate__(self, dict):
        """Influence how TreeScoringExplainer is unpickled.

        Re-adds logger which is not serializable.

        :param dict: A dictionary of deserialized state.
        :type dict: dict
        """
        self.__dict__.update(dict)
        parent = logging.getLogger(LoggingNamespace.AZUREML)
        self._logger = parent.getChild(self._identity)


class KernelScoringExplainer(ScoringExplainer):
    """Defines a scoring model based on KernelExplainer."""

    def __init__(self, model, initialization_examples, data_transformer=None, transformations=None, **kwargs):
        """Initialize the KernelScoringExplainer.

        :param model: The model to build the KernelExplainer from for local explanations.
        :type model: model that implements predict or predict_proba or function that accepts a 2d ndarray
        :param initialization_examples: A matrix of feature vector examples (# examples x # features) for
            initializing the explainer.
        :type initialization_examples: numpy.array or pandas.DataFrame or iml.datatypes.DenseData or
            scipy.sparse.csr_matrix
        :param data_transformer: The pipeline of transformations that should be run on the data
            before explanation. If None, no transformations will be done.
        :type data_transformer: An object implementing .transform()
        :param transformations: sklearn.compose.ColumnTransformer or a list of tuples describing the column name and
            transformer. When transformations are provided, explanations are of the features before the
            transformation. The format for list of transformations is same as the one here:
            https://github.com/scikit-learn-contrib/sklearn-pandas.
        :type transformations: sklearn.compose.ColumnTransformer or list[tuple]
        """
        super(KernelScoringExplainer, self).__init__(data_transformer=data_transformer,
                                                     transformations=transformations,
                                                     **kwargs)
        self._logger.debug('Initializing KernelScoringExplainer')
        try:
            model_function = model.predict_proba
        except:
            model_function = model.predict
        self.kernel_explainer = shap.KernelExplainer(model_function, initialization_examples)

    def explain(self, evaluation_examples, ys=None):
        """Use the TreeExplainer and tree model for scoring to get the feature importance values of data.

        :param evaluation_examples: A matrix of feature vector examples (# examples x # features) on
            which to explain the model's output.
        :type evaluation_examples: numpy.array or pandas.DataFrame or scipy.sparse.csr_matrix
        :param ys: Labels for data, used in time series transformations.
        :type ys: numpy, pandas, dense, sparse data vector
        :return local_importance_values: For a model with a single output such as regression,
            this returns a matrix of feature importance values. For models with vector outputs
            this function returns a list of such matrices, one for each output. The dimension
            of this matrix is (# examples x # features).
        :rtype local_importance_values: list
        """
        # convert raw data to engineered before explaining
        data = _transform_data(evaluation_examples, data_mapper=self._data_mapper,
                               data_transformer=self._data_transformer, ys=ys)

        values = self.kernel_explainer.shap_values(data)
        if self._data_mapper is not None:
            values = np.array(values) if isinstance(values, list) else values
            return self._get_raw_explanations(values).tolist()
        if not isinstance(values, list):
            values = values.tolist()
        # current slight hack for inconsistent shap deep explainer return type (list of numpy arrays)
        for i in range(len(values)):
            if not isinstance(values[i], list):
                values[i] = values[i].tolist()
        return values


class DeepScoringExplainer(ScoringExplainer):
    """Defines a scoring model based on DeepExplainer."""

    def __init__(self, deep_model, initialization_examples, data_transformer=None, transformations=None, **kwargs):
        """Initialize the DeepScoringExplainer.

        :param deep_model: The model to build the DeepExplainer from for local explanations.
        :type deep_model: pytorch or tensorflow model
        :param initialization_examples: A matrix of feature vector examples (# examples x # features) for
            initializing the explainer.
        :type initialization_examples: numpy.array or pandas.DataFrame or iml.datatypes.DenseData or
            scipy.sparse.csr_matrix
        :param data_transformer: The pipeline of transformations that should be run on the data
            before explanation. If None, no transformations will be done.
        :type data_transformer: An object implementing .transform()
        :param transformations: sklearn.compose.ColumnTransformer or a list of tuples describing the column name and
            transformer. When transformations are provided, explanations are of the features before the
            transformation. The format for list of transformations is same as the one here:
            https://github.com/scikit-learn-contrib/sklearn-pandas.
        :type transformations: sklearn.compose.ColumnTransformer or list[tuple]
        """
        super(DeepScoringExplainer, self).__init__(data_transformer=data_transformer,
                                                   transformations=transformations,
                                                   **kwargs)
        self._logger.debug('Initializing DeepScoringExplainer')
        self.deep_explainer = shap.DeepExplainer(deep_model, initialization_examples)

    def explain(self, evaluation_examples, ys=None):
        """Use the DeepExplainer and deep model for scoring to get the feature importance values of data.

        :param evaluation_examples: A matrix of feature vector examples (# examples x # features) on
            which to explain the model's output.
        :type evaluation_examples: numpy.array or pandas.DataFrame or scipy.sparse.csr_matrix
        :param ys: Labels for data, used in time series transformations.
        :type ys: numpy, pandas, dense, sparse data vector
        :return local_importance_values: For a model with a single output such as regression,
            this returns a matrix of feature importance values. For models with vector outputs
            this function returns a list of such matrices, one for each output. The dimension
            of this matrix is (# examples x # features).
        :rtype local_importance_values: list
        """
        # convert raw data to engineered before explaining
        data = _transform_data(evaluation_examples, data_mapper=self._data_mapper,
                               data_transformer=self._data_transformer, ys=ys)

        values = self.deep_explainer.shap_values(data)
        if self._data_mapper is not None:
            values = np.array(values) if isinstance(values, list) else values
            return self._get_raw_explanations(values).tolist()
        if not isinstance(values, list):
            values = values.tolist()
        # current slight hack for inconsistent shap deep explainer return type (list of numpy arrays)
        for i in range(len(values)):
            if not isinstance(values[i], list):
                values[i] = values[i].tolist()
        return values


class TreeScoringExplainer(ScoringExplainer):
    """Defines a scoring model based on TreeExplainer."""

    def __init__(self, tree_model, data_transformer=None, transformations=None, **kwargs):
        """Initialize the TreeScoringExplainer.

        :param tree_model: The tree model to build the TreeExplainer from for local explanations.
        :type tree_model: tree-based model
        :param data_transformer: The pipeline of transformations that should be run on the data
            before explanation. If None, no transformations will be done.
        :type data_transformer: An object implementing .transform()
        :param transformations: sklearn.compose.ColumnTransformer or a list of tuples describing the column name and
            transformer. When transformations are provided, explanations are of the features before the
            transformation. The format for list of transformations is same as the one here:
            https://github.com/scikit-learn-contrib/sklearn-pandas.
        :type transformations: sklearn.compose.ColumnTransformer or list[tuple]
        """
        super(TreeScoringExplainer, self).__init__(data_transformer=data_transformer,
                                                   transformations=transformations,
                                                   **kwargs)
        self._logger.debug('Initializing TreeScoringExplainer')
        self.tree_explainer = shap.TreeExplainer(tree_model)
        # Only lightgbm and xgboost models don't directly fail with sparse data currently
        model_type_str = str(type(tree_model))
        self._convert_to_dense = not ("xgboost" in model_type_str or "lightgbm" in model_type_str)

    def explain(self, evaluation_examples, ys=None):
        """Use the TreeExplainer and tree model for scoring to get the feature importance values of data.

        :param evaluation_examples: A matrix of feature vector examples (# examples x # features) on
            which to explain the model's output.
        :type evaluation_examples: numpy.array or pandas.DataFrame or scipy.sparse.csr_matrix
        :param ys: Labels for data, used in time series transformations.
        :type ys: numpy, pandas, dense, sparse data vector
        :return local_importance_values: For a model with a single output such as regression,
            this returns a matrix of feature importance values. For models with vector outputs
            this function returns a list of such matrices, one for each output. The dimension
            of this matrix is (# examples x # features).
        :rtype local_importance_values: list
        """
        if self._convert_to_dense:
            evaluation_examples = _get_dense_examples(evaluation_examples)

        # convert raw data to engineered before explaining
        data = _transform_data(evaluation_examples, data_mapper=self._data_mapper,
                               data_transformer=self._data_transformer, ys=ys)

        values = self.tree_explainer.shap_values(data)
        if self._data_mapper is not None:
            values = np.array(values) if isinstance(values, list) else values
            return self._get_raw_explanations(values).tolist()
        if not isinstance(values, list):
            values = values.tolist()
        return values


class LinearScoringExplainer(ScoringExplainer):
    """Defines a scoring model based on LinearExplainer."""

    def __init__(self, linear_model, initialization_examples, data_transformer=None, transformations=None, **kwargs):
        """Initialize the LinearScoringExplainer.

        :param linear_model: The linear model to build the LinearExplainer from for local explanations.
        :type linear_model: linear model
        :param data_transformer: The pipeline of transformations that should be run on the data
            before explanation. If None, no transformations will be done.
        :type data_transformer: An object implementing .transform()
        :param transformations: sklearn.compose.ColumnTransformer or a list of tuples describing the column name and
            transformer. When transformations are provided, explanations are of the features before the
            transformation. The format for list of transformations is same as the one here:
            https://github.com/scikit-learn-contrib/sklearn-pandas.
        :type transformations: sklearn.compose.ColumnTransformer or list[tuple]
        """
        super(LinearScoringExplainer, self).__init__(data_transformer=data_transformer,
                                                     transformations=transformations,
                                                     **kwargs)
        self._logger.debug('Initializing LinearScoringExplainer')
        self.linear_explainer = shap.LinearExplainer(linear_model, initialization_examples)

    def explain(self, evaluation_examples, ys=None):
        """Use the LinearExplainer for scoring to get the feature importance values of data.

        :param evaluation_examples: A matrix of feature vector examples (# examples x # features) on
            which to explain the model's output.
        :type evaluation_examples: numpy.array or pandas.DataFrame or scipy.sparse.csr_matrix
        :param ys: Labels for data, used in time series transformations.
        :type ys: numpy, pandas, dense, sparse data vector
        :return local_importance_values: For a model with a single output such as regression,
            this returns a matrix of feature importance values. For models with vector outputs
            this function returns a list of such matrices, one for each output. The dimension
            of this matrix is (# examples x # features).
        :rtype local_importance_values: list
        """
        data = evaluation_examples

        # convert raw data to engineered before explaining
        data = _transform_data(evaluation_examples, data_mapper=self._data_mapper,
                               data_transformer=self._data_transformer, ys=ys)

        values = self.linear_explainer.shap_values(data)
        if self._data_mapper is not None:
            return self._get_raw_explanations(values).tolist()
        if not isinstance(values, list):
            values = values.tolist()
        return values
