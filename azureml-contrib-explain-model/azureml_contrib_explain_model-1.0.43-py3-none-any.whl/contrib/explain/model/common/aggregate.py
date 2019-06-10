# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

"""Defines the aggregate explainer decorator for aggregating local explanations to global."""

from ..explanation.explanation import _aggregate_global_from_local_explanation, _create_global_explanation
from azureml.explain.model.explanation.explanation import _aggregate_streamed_local_explanations
from azureml.explain.model._internal.constants import ExplainParams, ModelTask


def contrib_add_explain_global_method(cls):
    """Monkey patches the _aggregate_global_from_local_explanation on the contrib explainers.

    :param cls: The class to monkey-patch.
    :type cls: BaseExplainer
    :return: The monkey patched explainer.
    :rtype: BaseExplainer
    """
    def _explain_global(self, evaluation_examples, sampling_policy=None, include_local=True, **kwargs):
        """Explains the model by aggregating local explanations to global.

        :param evaluation_examples: A matrix of feature vector examples (# examples x # features) on which
            to explain the model's output.
        :type evaluation_examples: numpy.array or pandas.DataFrame or scipy.sparse.csr_matrix
        :param sampling_policy: Optional policy for sampling the evaluation examples.  See documentation on
            SamplingPolicy for more information.
        :type sampling_policy: SamplingPolicy
        :param include_local: Include the local explanations in the returned global explanation.
            If evaluation examples are specified and include_local is False, will stream the local
            explanations to aggregate to global.
        :type include_local: bool
        :return: A model explanation object containing the local and global explanation.
        :rtype: BaseExplanation
        """
        if include_local:
            kwargs = self._get_explain_global_agg_kwargs(evaluation_examples, sampling_policy=sampling_policy,
                                                         **kwargs)
            # Aggregate local explanation to global
            return _aggregate_global_from_local_explanation(**kwargs)
        else:
            if ExplainParams.CLASSIFICATION in kwargs:
                if kwargs[ExplainParams.CLASSIFICATION]:
                    model_task = ModelTask.Classification
                else:
                    model_task = ModelTask.Regression
            else:
                model_task = ModelTask.Unknown
            kwargs = _aggregate_streamed_local_explanations(self, evaluation_examples, model_task,
                                                            self.features, **kwargs)
            return _create_global_explanation(**kwargs)
    cls._explain_global = _explain_global
    return cls
