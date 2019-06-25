# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

"""Defines scoring models for approximating feature importance values."""

import numpy as np
import logging
import os
import yaml
from sys import version_info
from abc import ABCMeta, abstractmethod
from sklearn.externals import joblib

try:
    from azureml._logging import ChainedIdentity
except ImportError:
    from azureml.explain.model.common.chained_identity import ChainedIdentity
try:
    from azureml.core import VERSION
except ImportError:
    VERSION = None

from azureml.explain.model._internal.constants import LoggingNamespace, Scoring
from azureml.explain.model.common.explanation_utils import _get_raw_feature_importances, _get_dense_examples, \
    _transform_data
from azureml.explain.model._internal.raw_explain import DataMapper

import warnings

with warnings.catch_warnings():
    warnings.filterwarnings('ignore', 'Starting from version 2.2.1', UserWarning)
    import shap

LOGGER = '_logger'
SCORING_FILE = 'scoring_explainer.pkl'
DEPENDENCIES = 'dependencies'


def save(scoring_explainer, directory='.', conda_env=None, requirements=None, exist_ok=False):
    """Save the scoring explainer to disk.

    :param scoring_explainer: The scoring explainer object which is to be saved. Will be written out to
        [directory]/scoring_explainer.pkl.
    :type name: ScoringExplainer
    :param directory: The directory under which the serialized explainer should be stored.
        If it doesn't exist, it will be created.
    :type directory: str
    :param conda_env: Either a path to a yaml file storing conda environment information, or a dictionary in a format
        handled by yaml.safe_load(). Will be written out to [directory]/environment.yml. Should follow the same format
        as conda env export.
    :type conda_env: str or dict
    :param requirements: A path to a requirements file storing pip environment information. Will be written out to
        [directory]/requirements.txt.
    :type requirements: str
    :param exist_ok: If False (the default state), a warning will be thrown if the directory given already exists. If
        True, the current directory will be used and any overlapping contents will be overwritten.
    :type exist_ok: bool
    :return: The conda environment dict in case the user would like to further modify or save it.
    :rtype: dict
    """
    # general check on path existence and creation
    if not os.path.exists(directory):
        os.makedirs(directory)
    elif not exist_ok:
        raise Exception('A directory already exists at this path. Please choose another path '
                        'or set exist_ok=True to overwrite the contents of the current directory.')

    # if the user passed in a path to a requirements file, copy it into the given directory
    if requirements is not None:
        with open(requirements, 'r') as req_file:
            req_string = ''
            for line in req_file:
                req_string += line
        with open(os.path.join(directory, 'requirements.txt'), 'w') as out_file:
            out_file.writelines(req_string)

    # save scoring explainer to the given directory
    with open(os.path.join(directory, SCORING_FILE), 'wb') as stream:
        joblib.dump(scoring_explainer, stream)

    # save conda env to the given directory
    if conda_env is None:
        # if nothing is passed in, we construct the environment as best we can
        env = yaml.safe_load('name: azureml-mli-env\nchannels:\n  - defaults')
        python = '{}.{}.{}'.format(version_info.major, version_info.minor, version_info.micro)
        env[DEPENDENCIES] = ['python=' + python]
        azureml_version_info = '==' + VERSION if VERSION is not None else ''
        pip_deps = ['azureml-explain-model' + azureml_version_info,
                    'azureml-contrib-explain-model' + azureml_version_info]
        env[DEPENDENCIES].append({'pip': pip_deps})
        try:
            import sklearn
            env[DEPENDENCIES] += ['scikit-learn=' + sklearn.__version__]
        except ImportError:
            pass
    elif isinstance(conda_env, str):
        # if a path is passed in, copy the file over
        with open(conda_env, 'r') as f:
            env = yaml.safe_load(f)
    else:
        # assuming that if conda_env isn't a string or None, it's a dictionary
        env = conda_env
    with open(os.path.join(directory, 'environment.yml'), 'w') as out:
        yaml.safe_dump(env, stream=out, default_flow_style=False)
    return env


def load(directory):
    """Load the scoring explainer from disk.

    :param directory: The directory under which the serialized explainer is stored. Assumes that
        scoring_explainer.pkl is available at the top level of the directory.
    :type directory: str
    :return: The scoring explainer from an explanation, loaded from disk.
    :rtype: azureml.contrib.explain.model.scoring.scoring_explainer.ScoringExplainer
    """
    with open(os.path.join(directory, SCORING_FILE), 'rb') as stream:
        scoring_explainer = joblib.load(stream)
    return scoring_explainer


def _unwrap_tabular(explainer):
    """Remove the tabular layer around a direct explainer.

    :param explainer: An explainer.
    :type explainer: BaseExplainer
    :return: An explainer, which will be a direct explainer if the original was a TabularExplainer.
    :rtype: BaseExplainer
    """
    if 'TabularExplainer' in str(type(explainer)):
        explainer = explainer.explainer
    return explainer


class ScoringExplainer(ChainedIdentity):
    """Defines a scoring model."""

    __metaclass__ = ABCMeta

    def __init__(self, original_explainer, **kwargs):
        """Initialize the ScoringExplainer.

        :param original_explainer: The training time explainer originally used to explain the model.
        :type original_explainer: BaseExplainer
        """
        super(ScoringExplainer, self).__init__(**kwargs)
        self._logger.debug('Initializing ScoringExplainer')

        if original_explainer.transformations is not None:
            self._data_mapper = DataMapper(original_explainer.transformations)
        else:
            self._data_mapper = None

        # If the original was a MimicExplainer, we need custom logic to pull the model out
        if hasattr(original_explainer, Scoring.SURROGATE_MODEL):
            self._model = original_explainer.surrogate_model.model
        else:
            self._model = original_explainer.model
        self._features = original_explainer.features

    def fit(self, X, y=None):
        """Implement dummy method required to fit scikit-learn pipeline interface."""
        return self

    @abstractmethod
    def explain(self, evaluation_examples):
        """Use the model for scoring to approximate the feature importance values of data."""
        pass

    @property
    def features(self):
        """Get the feature names passed into the original explainer.

        :return: The feature names, or None if none were given by the user.
        :rtype: list[str] or None
        """
        if self._features is not None and not isinstance(self._features, list):
            self._features = self._features.tolist()
        return self._features

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

    def predict(self, evaluation_examples):
        """Use the TreeExplainer and tree model for scoring to get the feature importance values of data.

        Wraps the .explain() function.

        :param evaluation_examples: A matrix of feature vector examples (# examples x # features) on
            which to explain the model's output.
        :type evaluation_examples: numpy.array or pandas.DataFrame or scipy.sparse.csr_matrix
        :return: For a model with a single output such as regression,
            this returns a matrix of feature importance values. For models with vector outputs
            this function returns a list of such matrices, one for each output. The dimension
            of this matrix is (# examples x # features).
        :rtype: list
        """
        return self.explain(evaluation_examples)

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

    def __init__(self, original_explainer, initialization_examples=None, **kwargs):
        """Initialize the KernelScoringExplainer.

        If the original explainer was using a SHAP KernelExplainer and no initialization data was passed in,
        the core of the original explainer will be reused. If the original explainer used another method or new
        initialization data was passed in under initialization_examples, a new explainer will be created.

        :param original_explainer: The training time explainer originally used to explain the model.
        :type original_explainer: BaseExplainer
        :param initialization_examples: A matrix of feature vector examples (# examples x # features) for
            initializing the explainer.
        :type initialization_examples: numpy.array or pandas.DataFrame or iml.datatypes.DenseData or
            scipy.sparse.csr_matrix
        """
        super(KernelScoringExplainer, self).__init__(original_explainer, **kwargs)
        self._logger.debug('Initializing KernelScoringExplainer')
        try:
            self._model_function = self._model.predict_proba
        except:
            self._model_function = self._model.predict

        original_explainer = _unwrap_tabular(original_explainer)

        self._kernel_explainer = None
        has_explainer = hasattr(original_explainer, Scoring.EXPLAINER)
        if initialization_examples is not None:
            # Create new explainer
            init_data = _transform_data(initialization_examples, data_mapper=self._data_mapper)
            self._kernel_explainer = shap.KernelExplainer(self._model_function, init_data)
        elif has_explainer and type(original_explainer.explainer) == shap.KernelExplainer:
            # Reuse core of original explainer
            self._kernel_explainer = original_explainer.explainer
        else:
            raise Exception('Please pass initialization_examples to create a new explainer.')

    def explain(self, evaluation_examples):
        """Use the TreeExplainer and tree model for scoring to get the feature importance values of data.

        :param evaluation_examples: A matrix of feature vector examples (# examples x # features) on
            which to explain the model's output.
        :type evaluation_examples: numpy.array or pandas.DataFrame or scipy.sparse.csr_matrix
        :return local_importance_values: For a model with a single output such as regression,
            this returns a matrix of feature importance values. For models with vector outputs
            this function returns a list of such matrices, one for each output. The dimension
            of this matrix is (# examples x # features).
        :rtype local_importance_values: list
        """
        # convert raw data to engineered before explaining
        data = _transform_data(evaluation_examples, data_mapper=self._data_mapper)

        values = self._kernel_explainer.shap_values(data)
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

    def __init__(self, original_explainer, initialization_examples=None, **kwargs):
        """Initialize the DeepScoringExplainer.

        If the original explainer was using a SHAP DeepExplainer and no initialization data was passed in,
        the core of the original explainer will be reused. If the original explainer used another method or new
        initialization data was passed in under initialization_examples, a new explainer will be created.

        :param original_explainer: The training time deep explainer originally used to explain the model.
        :type original_explainer: BaseExplainer
        :param initialization_examples: A matrix of feature vector examples (# examples x # features) for
            initializing the explainer.
        :type initialization_examples: numpy.array or pandas.DataFrame or iml.datatypes.DenseData or
            scipy.sparse.csr_matrix
        """
        super(DeepScoringExplainer, self).__init__(original_explainer,
                                                   **kwargs)
        self._logger.debug('Initializing DeepScoringExplainer')

        original_explainer = _unwrap_tabular(original_explainer)

        self._deep_explainer = None
        has_explainer = hasattr(original_explainer, Scoring.EXPLAINER)
        if initialization_examples is not None:
            # Create new explainer
            init_data = _transform_data(initialization_examples, data_mapper=self._data_mapper)
            self._deep_explainer = shap.DeepExplainer(self._model, init_data)
        elif has_explainer and type(original_explainer.explainer) == shap.DeepExplainer:
            # Reuse core of original explainer
            self._deep_explainer = original_explainer.explainer
        else:
            raise Exception('Please pass initialization_examples to create a new explainer.')

    def explain(self, evaluation_examples):
        """Use the DeepExplainer and deep model for scoring to get the feature importance values of data.

        :param evaluation_examples: A matrix of feature vector examples (# examples x # features) on
            which to explain the model's output.
        :type evaluation_examples: numpy.array or pandas.DataFrame or scipy.sparse.csr_matrix
        :return local_importance_values: For a model with a single output such as regression,
            this returns a matrix of feature importance values. For models with vector outputs
            this function returns a list of such matrices, one for each output. The dimension
            of this matrix is (# examples x # features).
        :rtype local_importance_values: list
        """
        # convert raw data to engineered before explaining
        data = _transform_data(evaluation_examples, data_mapper=self._data_mapper)

        values = self._deep_explainer.shap_values(data)
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

    def __init__(self, original_explainer, **kwargs):
        """Initialize the TreeScoringExplainer.

        If the original explainer was using a SHAP TreeExplainer, the core of the original explainer will be reused.
        If the original explainer used another method, a new explainer will be created.

        :param original_explainer: The training time tree explainer originally used to explain the model.
        :type original_explainer: BaseExplainer
        """
        super(TreeScoringExplainer, self).__init__(original_explainer, **kwargs)
        self._logger.debug('Initializing TreeScoringExplainer')

        original_explainer = _unwrap_tabular(original_explainer)

        has_explainer = hasattr(original_explainer, Scoring.EXPLAINER)
        if has_explainer and type(original_explainer.explainer) == shap.TreeExplainer:
            # Reuse core of original explainer
            self._tree_explainer = original_explainer.explainer
        else:
            # Create new explainer
            self._tree_explainer = shap.TreeExplainer(self._model)

        # Only lightgbm and xgboost models don't directly fail with sparse data currently
        model_type_str = str(type(self._model))
        self._convert_to_dense = not ("xgboost" in model_type_str or "lightgbm" in model_type_str)

    def explain(self, evaluation_examples):
        """Use the TreeExplainer and tree model for scoring to get the feature importance values of data.

        :param evaluation_examples: A matrix of feature vector examples (# examples x # features) on
            which to explain the model's output.
        :type evaluation_examples: numpy.array or pandas.DataFrame or scipy.sparse.csr_matrix
        :return local_importance_values: For a model with a single output such as regression,
            this returns a matrix of feature importance values. For models with vector outputs
            this function returns a list of such matrices, one for each output. The dimension
            of this matrix is (# examples x # features).
        :rtype local_importance_values: list
        """
        if self._convert_to_dense:
            evaluation_examples = _get_dense_examples(evaluation_examples)

        # convert raw data to engineered before explaining
        data = _transform_data(evaluation_examples, data_mapper=self._data_mapper)

        values = self._tree_explainer.shap_values(data)
        if self._data_mapper is not None:
            values = np.array(values) if isinstance(values, list) else values
            return self._get_raw_explanations(values).tolist()
        if not isinstance(values, list):
            values = values.tolist()
        return values


class LinearScoringExplainer(ScoringExplainer):
    """Defines a scoring model based on LinearExplainer."""

    def __init__(self, original_explainer, initialization_examples, **kwargs):
        """Initialize the LinearScoringExplainer.

        :param original_explainer: The training time explainer originally used to explain the linear model.
        :type original_explainer: BaseExplainer
        :param initialization_examples: A matrix of feature vector examples (# examples x # features) for
            initializing the explainer.
        :type initialization_examples: numpy.array or pandas.DataFrame or iml.datatypes.DenseData or
            scipy.sparse.csr_matrix
        """
        super(LinearScoringExplainer, self).__init__(original_explainer, **kwargs)
        self._logger.debug('Initializing LinearScoringExplainer')
        init_data = _transform_data(initialization_examples, data_mapper=self._data_mapper)
        self._linear_explainer = shap.LinearExplainer(self._model, init_data)

    def explain(self, evaluation_examples):
        """Use the LinearExplainer for scoring to get the feature importance values of data.

        :param evaluation_examples: A matrix of feature vector examples (# examples x # features) on
            which to explain the model's output.
        :type evaluation_examples: numpy.array or pandas.DataFrame or scipy.sparse.csr_matrix
        :return local_importance_values: For a model with a single output such as regression,
            this returns a matrix of feature importance values. For models with vector outputs
            this function returns a list of such matrices, one for each output. The dimension
            of this matrix is (# examples x # features).
        :rtype local_importance_values: list
        """
        data = evaluation_examples

        # convert raw data to engineered before explaining
        data = _transform_data(evaluation_examples, data_mapper=self._data_mapper)

        values = self._linear_explainer.shap_values(data)
        if self._data_mapper is not None:
            return self._get_raw_explanations(values).tolist()
        if not isinstance(values, list):
            values = values.tolist()
        return values
