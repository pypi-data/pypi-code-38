# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

"""Defines the tabular explainer meta-api for returning the best explanation result based on the given model."""

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
