# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

"""Defines the tabular explainer meta-api for returning the best explanation result based on the given model."""

from azureml.exceptions import UserErrorException

from azureml.explain.model import tabular_explainer
from azureml.explain.model._internal.constants import ExplainParams
from azureml.explain.model.dataset.decorator import tabular_decorator
from .shap.tree_explainer import TreeExplainer
from .shap.deep_explainer import DeepExplainer
from .shap.kernel_explainer import KernelExplainer


class TabularExplainer(tabular_explainer.TabularExplainer):
    """Defines the tabular explainer meta-api for returning the best explanation result based on the given model."""

    @tabular_decorator
    def explain_global(self, evaluation_examples, sampling_policy=None,
                       include_local=True):
        """Globally explains the black box model or function.

        :param evaluation_examples: A matrix of feature vector examples (# examples x # features) on which
            to explain the model's output.
        :type evaluation_examples: numpy.array or pandas.DataFrame or scipy.sparse.csr_matrix
        :param sampling_policy: Optional policy for sampling the evaluation examples.  See documentation on
            SamplingPolicy for more information.
        :type sampling_policy: SamplingPolicy
        :param include_local: Include the local explanations in the returned global explanation.
            If include_local is False, will stream the local explanations to aggregate to global.
        :type include_local: bool
        :return: A model explanation object. It is guaranteed to be a GlobalExplanation. If SHAP is used for the
            explanation, it will also have the properties of a LocalExplanation and the ExpectedValuesMixin. If the
            model does classification, it will have the properties of the PerClassMixin.
        :rtype: DynamicGlobalExplanation
        """
        kwargs = {ExplainParams.SAMPLING_POLICY: sampling_policy,
                  ExplainParams.INCLUDE_LOCAL: include_local}
        return self.explainer.explain_global(evaluation_examples, **kwargs)

    def _get_uninitialized_explainers(self):
        """Return the uninitialized explainers used by the tabular explainer.

        :return: A list of the uninitialized explainers.
        :rtype: list
        """
        return [TreeExplainer, DeepExplainer, KernelExplainer]

    def create_scoring_explainer(self, initialization_examples=None, data_transformer=None):
        """Create the scoring explainer for the tabular explainer.

        If the model being explained is not tree-based, initialization_examples must be passed.

        :param initialization_examples: The samples that will be used as background data for the scoring explainer.
        :type initialization_examples: numpy.array or iml.datatypes.DenseData or scipy.sparse.csr_matrix
        :param data_transformer: An object that converts raw features to engineered via .transform().
            The data output by transform should mirror the data passed into explain_global.
        :type data_transformer: An object with .transform()
        :return: The scoring explainer based on the model being explained.
        :rtype: ScoringExplainer
        """
        if self.explainer._datamapper is not None and data_transformer is not None:
            raise UserErrorException('If transformations for raw feature explanation '
                                     'were passed into the TabularExplainer init, '
                                     'please do not use data_transformer here.')
        if isinstance(self.explainer, TreeExplainer):
            return self.explainer.create_scoring_explainer(data_transformer=data_transformer)
        else:
            if initialization_examples is None:
                raise Exception('For this type of model, '
                                'please provide initialization examples to create_scoring_explainer.')
            return self.explainer.create_scoring_explainer(initialization_examples, data_transformer=data_transformer)
