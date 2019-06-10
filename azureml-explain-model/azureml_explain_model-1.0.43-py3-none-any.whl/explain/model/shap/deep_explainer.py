# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

"""Defines an explainer for DNN models."""

import numpy as np
import sys

from ..common.structured_model_explainer import StructuredInitModelExplainer
from ..common.explanation_utils import _get_dense_examples, _convert_to_list
from ..explanation.explanation import _create_local_explanation
from ..common.aggregate import add_explain_global_method, init_aggregator_decorator
from ..dataset.decorator import tabular_decorator, init_tabular_decorator
from ..explanation.explanation import _create_raw_feats_local_explanation, \
    _get_raw_explainer_create_explanation_kwargs
from .kwargs_utils import _get_explain_global_kwargs
from azureml.explain.model._internal.constants import ExplainParams, Attributes, ExplainType
from azureml.explain.model._internal.raw_explain.raw_explain_utils import get_datamapper_and_transformed_data, \
    transform_with_datamapper

import warnings

with warnings.catch_warnings():
    warnings.filterwarnings('ignore', 'Starting from version 2.2.1', UserWarning)
    import shap


class logger_redirector(object):
    """A redirector for system error output to logger."""

    def __init__(self, module_logger):
        """Initialize the logger_redirector.

        :param module_logger: The logger to use for redirection.
        :type module_logger: logger
        """
        self.logger = module_logger

    def __enter__(self):
        """Start the redirection for logging."""
        self.logger.debug("Redirecting user output to logger")
        self.original_stderr = sys.stderr
        sys.stderr = self

    def write(self, data):
        """Write the given data to logger.

        :param data: The data to write to logger.
        :type data: str
        """
        self.logger.debug(data)

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Finishes the redirection for logging."""
        try:
            if exc_val:
                # The default traceback.print_exc() expects a file-like object which
                # OutputCollector is not. Instead manually print the exception details
                # to the wrapped sys.stderr by using an intermediate string.
                # trace = traceback.format_tb(exc_tb)
                import traceback
                trace = "".join(traceback.format_exception(exc_type, exc_val, exc_tb))
                print(trace, file=sys.stderr)
        finally:
            sys.stderr = self.original_stderr
            self.logger.debug("User scope execution complete.")


@add_explain_global_method
class DeepExplainer(StructuredInitModelExplainer):
    """An explainer for DNN models, implemented using shap's DeepExplainer, supports tensorflow and pytorch."""

    @init_tabular_decorator
    @init_aggregator_decorator
    def __init__(self, model, initialization_examples, explain_subset=None, nclusters=10,
                 features=None, classes=None, transformations=None, **kwargs):
        """Initialize the DeepExplainer.

        :param model: The DNN model to explain.
        :type model: pytorch or tensorflow model
        :param initialization_examples: A matrix of feature vector examples (# examples x # features) for
            initializing the explainer.
        :type initialization_examples: numpy.array or pandas.DataFrame or iml.datatypes.DenseData or
            scipy.sparse.csr_matrix
        :param explain_subset: List of feature indices. If specified, only selects a subset of the
            features in the evaluation dataset for explanation. The subset can be the top-k features
            from the model summary.
        :type explain_subset: list[int]
        :param nclusters: Number of means to use for approximation. A dataset is summarized with nclusters mean
            samples weighted by the number of data points they each represent. When the number of initialization
            examples is larger than (10 x nclusters), those examples will be summarized with k-means where
            k = nclusters.
        :type nclusters: int
        :param features: A list of feature names.
        :type features: list[str]
        :param classes: Class names as a list of strings. The order of the class names should match
            that of the model output.  Only required if explaining classifier.
        :type classes: list[str]
        :param transformations: sklearn.compose.ColumnTransformer or a list of tuples describing the column name and
        transformer. When transformations are provided, explanations are of the features before the transformation. The
        format for list of transformations is same as the one here:
        https://github.com/scikit-learn-contrib/sklearn-pandas.
        If the user is using a transformation that is not in the list of sklearn.preprocessing transformations that
        we support then we cannot take a list of more than one column as input for the transformation.
        A user can use the following sklearn.preprocessing  transformations with a list of columns since these are
        already one to many or one to one: Binarizer, KBinsDiscretizer, KernelCenterer, LabelEncoder, MaxAbsScaler,
        MinMaxScaler, Normalizer, OneHotEncoder, OrdinalEncoder, PowerTransformer, QuantileTransformer, RobustScaler,
        StandardScaler.
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
        This would not work since it is hard to make out whether my_own_transformer gives a many to many or one to many
        mapping when taking a sequence of columns.
        :type transformations: sklearn.compose.ColumnTransformer or list[tuple]
        """
        self._datamapper = None
        if transformations is not None:
            self._datamapper, _ = get_datamapper_and_transformed_data(transformations=transformations)

        super(DeepExplainer, self).__init__(model, initialization_examples, **kwargs)
        self._logger.debug('Initializing DeepExplainer')
        self.features = features
        self.classes = classes
        self.nclusters = nclusters
        self.explain_subset = explain_subset
        self.initialization_examples.compute_summary(nclusters=nclusters)
        self.transformations = transformations
        summary = self.initialization_examples.dataset
        # Suppress warning message from Keras
        with logger_redirector(self._logger):
            self.explainer = shap.DeepExplainer(self.model, summary.data)

    @tabular_decorator
    def explain_global(self, evaluation_examples, sampling_policy=None, include_local=True):
        """Explain the model globally by aggregating local explanations to global.

        :param evaluation_examples: A matrix of feature vector examples (# examples x # features) on which
            to explain the model's output.
        :type evaluation_examples: numpy.array or pandas.DataFrame or scipy.sparse.csr_matrix
        :param sampling_policy: Optional policy for sampling the evaluation examples.  See documentation on
            SamplingPolicy for more information.
        :type sampling_policy: SamplingPolicy
        :param include_local: Include the local explanations in the returned global explanation.
            If include_local is False, will stream the local explanations to aggregate to global.
        :type include_local: bool
        :return: A model explanation object. It is guaranteed to be a GlobalExplanation which also has the properties
            of LocalExplanation and ExpectedValuesMixin. If the model is a classifier, it will have the properties of
            PerClassMixin.
        :rtype: DynamicGlobalExplanation
        """
        kwargs = _get_explain_global_kwargs(sampling_policy, ExplainType.SHAP_DEEP, include_local)
        return self._explain_global(evaluation_examples, **kwargs)

    def _get_explain_local_kwargs(self, evaluation_examples):
        """Get the kwargs for explain_local to create a local explanation.

        :param evaluation_examples: A matrix of feature vector examples (# examples x # features) on which
            to explain the model's output.
        :type evaluation_examples: numpy.array or pandas.DataFrame or scipy.sparse.csr_matrix
        :return: Args for explain_local.
        :rtype: dict
        """
        self._logger.debug('Explaining deep model')
        if self._datamapper is not None:
            evaluation_examples = transform_with_datamapper(evaluation_examples, self._datamapper)

        # sample the evaluation examples
        if self.sampling_policy is not None and self.sampling_policy.allow_eval_sampling:
            sampling_method = self.sampling_policy.sampling_method
            max_dim_clustering = self.sampling_policy.max_dim_clustering
            evaluation_examples.sample(max_dim_clustering, sampling_method=sampling_method)
        kwargs = {ExplainParams.METHOD: ExplainType.SHAP_DEEP}
        if self.classes is not None:
            kwargs[ExplainParams.CLASSES] = self.classes
        kwargs[ExplainParams.FEATURES] = evaluation_examples.get_features(features=self.features)
        evaluation_examples = evaluation_examples.dataset
        # for now convert evaluation examples to dense format if they are sparse
        # until DeepExplainer sparse support is added
        shap_values = self.explainer.shap_values(_get_dense_examples(evaluation_examples))
        # slightly hacky fix - TODO update SHAP to be consistent for deep case
        # if len(shap_values) == 1:
        #     shap_values = shap_values[0]
        classification = isinstance(shap_values, list)
        if self.explain_subset:
            if classification:
                self._logger.debug('Classification explanation')
                for i in range(shap_values.shape[0]):
                    shap_values[i] = shap_values[i][:, self.explain_subset]
            else:
                self._logger.debug('Regression explanation')
                shap_values = shap_values[:, self.explain_subset]

        expected_values = None
        if hasattr(self.explainer, Attributes.EXPECTED_VALUE):
            self._logger.debug('reporting expected values')
            expected_values = self.explainer.expected_value
            if isinstance(expected_values, np.ndarray):
                expected_values = expected_values.tolist()
        local_importance_values = _convert_to_list(shap_values)
        if classification:
            kwargs[ExplainParams.MODEL_TASK] = ExplainType.CLASSIFICATION
        else:
            kwargs[ExplainParams.MODEL_TASK] = ExplainType.REGRESSION
        kwargs[ExplainParams.MODEL_TYPE] = str(type(self.model))
        kwargs[ExplainParams.LOCAL_IMPORTANCE_VALUES] = np.array(local_importance_values)
        kwargs[ExplainParams.EXPECTED_VALUES] = np.array(expected_values)
        kwargs[ExplainParams.CLASSIFICATION] = classification
        return kwargs

    @tabular_decorator
    def explain_local(self, evaluation_examples):
        """Explain the model by using shap's deep explainer.

        :param evaluation_examples: A matrix of feature vector examples (# examples x # features) on which
            to explain the model's output.
        :type evaluation_examples: numpy.array or pandas.DataFrame or scipy.sparse.csr_matrix
        :return: A model explanation object. It is guaranteed to be a LocalExplanation which also has the properties
            of ExpectedValuesMixin. If the model is a classfier, it will have the properties of the ClassesMixin.
        :rtype: DynamicLocalExplanation
        """
        kwargs = self._get_explain_local_kwargs(evaluation_examples)
        explanation = _create_local_explanation(**kwargs)

        if self._datamapper is None:
            return explanation
        else:
            # if transformations have been passed, then return raw features explanation
            raw_kwargs = _get_raw_explainer_create_explanation_kwargs(kwargs=kwargs)
            return _create_raw_feats_local_explanation(explanation, feature_map=self._datamapper.feature_map,
                                                       **raw_kwargs)
