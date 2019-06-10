# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

"""Defines the LIMEExplainer for computing explanations on black box models using LIME."""

import numpy as np

from azureml.explain.model.common.aggregate import add_explain_global_method
from azureml.explain.model.common.blackbox_explainer import BlackBoxExplainer, \
    add_prepare_function_and_summary_method, init_blackbox_decorator
from azureml.explain.model.dataset.decorator import tabular_decorator, init_tabular_decorator
from ..scoring.scoring_explainer import KernelScoringExplainer
from ..explanation.explanation import _create_local_explanation
from azureml.explain.model.common.explanation_utils import _transform_data
from azureml.explain.model._internal.constants import ExplanationParams, ExplainParams, ExplainType
from ..common.aggregate import contrib_add_explain_global_method
from azureml.explain.model.common.progress import get_tqdm

# Soft dependency for LIME
try:
    from lime.lime_tabular import LimeTabularExplainer
except ImportError:
    print("Could not import LIME, required for LIMEExplainer")

import warnings

with warnings.catch_warnings():
    warnings.filterwarnings('ignore', 'Starting from version 2.2.1', UserWarning)
    from shap.common import DenseData


@contrib_add_explain_global_method
@add_prepare_function_and_summary_method
@add_explain_global_method
class LIMEExplainer(BlackBoxExplainer):
    """Defines the LIME Explainer for explaining black box models or functions."""

    @init_tabular_decorator
    @init_blackbox_decorator
    def __init__(self, model, initialization_examples, is_function=False, explain_subset=None,
                 nclusters=10, features=None, classes=None, verbose=False, categorical_features=[],
                 show_progress=True, **kwargs):
        """Initialize the LIME Explainer.

        :param model: The model to explain or function if is_function is True.
        :type model: model that implements predict or predict_proba or function that accepts a 2d ndarray
        :param initialization_examples: A matrix of feature vector examples (# examples x # features) for
            initializing the explainer.
        :type initialization_examples: numpy.array or pandas.DataFrame or iml.datatypes.DenseData or
            scipy.sparse.csr_matrix
        :param is_function: Default set to false, set to True if passing function instead of model.
        :type is_function: bool
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
        :param verbose: If true, uses verbose logging in LIME.
        :type verbose: bool
        :param categorical_features: Categorical feature names or indexes.
            If names are passed, they will be converted into indexes first.
        :type categorical_features: Union[list[str], list[int]]
        :param show_progress: Default to 'True'.  Determines whether to display the explanation status bar
            when using LIMEExplainer.
        :type show_progress: bool
        """
        super(LIMEExplainer, self).__init__(model, is_function=is_function, **kwargs)
        self._logger.debug('Initializing LIMEExplainer')
        self.initialization_examples = initialization_examples
        self.classification = False
        self.features = initialization_examples.get_features(features=features)
        self.classes = classes
        self.nclusters = nclusters
        self.explain_subset = explain_subset
        self.show_progress = show_progress
        # If categorical_features is a list of string column names instead of indexes, make sure to convert to indexes
        if not all(isinstance(categorical_feature, int) for categorical_feature in categorical_features):
            categorical_features = initialization_examples.get_column_indexes(self.features, categorical_features)
        # Index the categorical string columns
        self._column_indexer = initialization_examples.string_index(columns=categorical_features)
        function, summary = self._prepare_function_and_summary(self.function, self.original_data_ref,
                                                               self.current_index_list, nclusters=nclusters,
                                                               explain_subset=explain_subset, **kwargs)
        if isinstance(summary, DenseData):
            summary = summary.data
        result = function(summary[0].reshape((1, -1)))
        # If result is 2D array, this is classification scenario, otherwise regression
        if len(result.shape) == 2:
            self.classification = True
            mode = ExplainType.CLASSIFICATION
        elif len(result.shape) == 1:
            self.classification = False
            mode = ExplainType.REGRESSION
        else:
            raise Exception('Invalid function specified, does not conform to specifications on prediction')
        self.explainer = LimeTabularExplainer(summary, feature_names=features, class_names=classes,
                                              categorical_features=categorical_features, verbose=verbose,
                                              mode=mode, discretize_continuous=False)
        self.explainer.function = function
        if self.classes is None and self.classification:
            raise ValueError('LIME Explainer requires classes to be specified')
        if self.classes is not None and not self.classification:
            if self.model is None:
                error = 'Classes is specified but function was predict, not predict_proba.'
            else:
                error = 'Classes is specified but model does not define predict_proba, only predict.'
            raise ValueError(error)

    @tabular_decorator
    def explain_global(self, evaluation_examples, sampling_policy=None,
                       include_local=True):
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
        :return: A model explanation object containing the global explanation.
        :rtype: GlobalExplanation
        """
        kwargs = {ExplainParams.METHOD: ExplainType.LIME,
                  ExplainParams.SAMPLING_POLICY: sampling_policy,
                  ExplainParams.INCLUDE_LOCAL: include_local}
        return self._explain_global(evaluation_examples, **kwargs)

    @tabular_decorator
    def explain_local(self, evaluation_examples):
        """Explain the function locally by using LIME.

        :param evaluation_examples: A matrix of feature vector examples (# examples x # features) on which
            to explain the model's output.
        :type evaluation_examples: DatasetWrapper
        :param features: A list of feature names.
        :type features: list[str]
        :param classes: Class names as a list of strings. The order of the class names should match
            that of the model output.  Only required if explaining classifier.
        :type classes: list[str]
        :return: A model explanation object containing the local explanation.
        :rtype: LocalExplanation
        """
        if self._column_indexer:
            evaluation_examples.apply_indexer(self._column_indexer)

        # Compute subset info prior
        if self.explain_subset:
            evaluation_examples.take_subset(self.explain_subset)

        # sample the evaluation examples
        # note: the sampled data is also used by KNN
        if self.sampling_policy is not None and self.sampling_policy.allow_eval_sampling:
            sampling_method = self.sampling_policy.sampling_method
            max_dim_clustering = self.sampling_policy.max_dim_clustering
            evaluation_examples.sample(max_dim_clustering, sampling_method=sampling_method)
        features = self.features
        if self.explain_subset:
            features = features[self.explain_subset]
        kwargs = {ExplainParams.METHOD: ExplainType.LIME}
        kwargs[ExplainParams.FEATURES] = features
        original_evaluation = evaluation_examples.original_dataset
        evaluation_examples = evaluation_examples.dataset
        if len(evaluation_examples.shape) == 1:
            evaluation_examples = evaluation_examples.reshape(1, -1)

        self._logger.debug('Running LIMEExplainer')
        if self.classification:
            kwargs[ExplanationParams.CLASSES] = self.classes
            kwargs[ExplainType.MODEL_TASK] = ExplainType.CLASSIFICATION
            num_classes = len(self.classes)
            labels = list(range(num_classes))
        else:
            kwargs[ExplainType.MODEL_TASK] = ExplainType.REGRESSION
            num_classes = 1
            labels = None
        lime_explanations = []

        tqdm = get_tqdm(self._logger, self.show_progress)

        if self.explain_subset:
            self.original_data_ref[0] = original_evaluation
            self.current_index_list.append(0)
            for ex_idx, example in tqdm(enumerate(evaluation_examples)):
                self.current_index_list[0] = ex_idx
                lime_explanations.append(self.explainer.explain_instance(example,
                                                                         self.explainer.function,
                                                                         labels=labels))
            self.current_index_list = [0]
        else:
            for ex_idx, example in tqdm(enumerate(evaluation_examples)):
                lime_explanations.append(self.explainer.explain_instance(example,
                                                                         self.explainer.function,
                                                                         labels=labels))
        if self.classification:
            lime_values = [None] * num_classes
            for lime_explanation in lime_explanations:
                for label in labels:
                    map_values = dict(lime_explanation.as_list(label=label))
                    if lime_values[label - 1] is None:
                        lime_values[label - 1] = [[map_values.get(feature, 0.0) for feature in features]]
                    else:
                        lime_values[label - 1].append([map_values.get(feature, 0.0) for feature in features])
        else:
            lime_values = None
            for lime_explanation in lime_explanations:
                map_values = dict(lime_explanation.as_list())
                if lime_values is None:
                    lime_values = [[map_values.get(feature, 0.0) for feature in features]]
                else:
                    lime_values.append([map_values.get(feature, 0.0) for feature in features])
        expected_values = None
        if self.model is not None:
            kwargs[ExplainParams.MODEL_TYPE] = str(type(self.model))
        else:
            kwargs[ExplainParams.MODEL_TYPE] = ExplainType.FUNCTION
        return _create_local_explanation(local_importance_values=np.array(lime_values),
                                         expected_values=np.array(expected_values),
                                         classification=self.classification,
                                         **kwargs)

    def create_scoring_explainer(self, data_transformer=None):
        """Create the scoring explainer for the kernel explainer.

        This will run explain_global in the background.

        :param evaluation_examples: The evaluation samples that have been used to generate
            the local importance values.
        :type evaluation_examples: numpy.array or iml.datatypes.DenseData or scipy.sparse.csr_matrix
        :param data_transformer: An object that converts raw features to engineered via .transform().
            The data output by transform should mirror the data passed into explain_global.
        :type data_transformer: An object with .transform()
        :return: The scoring explainer based on the model being explained.
        :rtype: KernelScoringExplainer
        """
        init_data = _transform_data(self.initialization_examples, data_transformer=data_transformer)
        return KernelScoringExplainer(self.model, init_data, data_transformer=data_transformer)
