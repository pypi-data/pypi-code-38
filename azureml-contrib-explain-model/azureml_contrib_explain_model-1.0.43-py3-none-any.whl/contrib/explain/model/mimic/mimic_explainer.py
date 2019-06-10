# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

"""Defines the Mimic Explainer for computing explanations on black box models or functions.

The mimic explainer trains an explainable model to reproduce the output of the given black box model.
The explainable model is called a surrogate model and the black box model is called a teacher model.
Once trained to reproduce the output of the teacher model, the surrogate model's explanation can
be used to explain the teacher model.
"""

from azureml.exceptions import UserErrorException
from azureml.explain.model.mimic import mimic_explainer
from ..scoring.scoring_explainer import TreeScoringExplainer, LinearScoringExplainer
from ..explanation.explanation import _create_local_explanation, _create_global_explanation, \
    _aggregate_global_from_local_explanation
from azureml.explain.model.dataset.decorator import tabular_decorator
from azureml.explain.model.explanation.explanation import _create_raw_feats_global_explanation, \
    _create_raw_feats_local_explanation, _get_raw_explainer_create_explanation_kwargs
from azureml.explain.model._internal.raw_explain.raw_explain_utils import transform_with_datamapper
from ..common.aggregate import contrib_add_explain_global_method


@contrib_add_explain_global_method
class MimicExplainer(mimic_explainer.MimicExplainer):
    """Defines the Mimic Explainer for explaining black box models or functions."""

    def explain_global(self, evaluation_examples=None, include_local=True):
        """Globally explains the blackbox model using the surrogate model.

        If evaluation_examples are unspecified, retrieves global feature importances from explainable
        surrogate model.  Note this will not include per class feature importances.  If evaluation_examples
        are specified, aggregates local explanations to global from the given evaluation_examples - which
        computes both global and per class feature importances.

        :param evaluation_examples: A matrix of feature vector examples (# examples x # features) on which to
            explain the model's output.  If specified, computes feature importances through aggregation.
        :type evaluation_examples: numpy.array or pandas.DataFrame or scipy.sparse.csr_matrix
        :param include_local: Include the local explanations in the returned global explanation.
            If evaluation examples are specified and include_local is False, will stream the local
            explanations to aggregate to global.
        :type include_local: bool
        :return: A model explanation object. It is guaranteed to be a GlobalExplanation. If evaluation_examples are
            passed in, it will also have the properties of a LocalExplanation. If the model is a classifier (has
            predict_proba), it will have the properties of ClassesMixin, and if evaluation_examples were passed in it
            will also have the properties of PerClassMixin.
        :rtype: DynamicGlobalExplanation
        """
        kwargs = super(MimicExplainer, self)._get_explain_global_kwargs(evaluation_examples,
                                                                        include_local=include_local)
        if evaluation_examples is not None and include_local:
            return _aggregate_global_from_local_explanation(**kwargs)
        explanation = _create_global_explanation(**kwargs)

        # if transformations have been passed, then return raw features explanation
        new_kwargs = _get_raw_explainer_create_explanation_kwargs(kwargs=kwargs)
        return explanation if self._datamapper is None else _create_raw_feats_global_explanation(
            explanation, feature_map=self._datamapper.feature_map, **new_kwargs)

    @tabular_decorator
    def explain_local(self, evaluation_examples):
        """Locally explains the blackbox model on the provided examples using the surrogate model.

        :param evaluation_examples: A matrix of feature vector examples (# examples x # features) on which
            to explain the model's output.
        :type evaluation_examples: numpy.array or pandas.DataFrame or scipy.sparse.csr_matrix
        :return: A model explanation object. It is guaranteed to be a LocalExplanation. If the model is a classifier,
            it will have the properties of the ClassesMixin.
        :rtype: DynamicLocalExplanation
        """
        if self._datamapper is not None:
            evaluation_examples = transform_with_datamapper(evaluation_examples, self._datamapper)

        kwargs = super(MimicExplainer, self)._get_explain_local_kwargs(evaluation_examples)
        explanation = _create_local_explanation(**kwargs)

        # if transformations have been passed, then return raw features explanation
        raw_kwargs = _get_raw_explainer_create_explanation_kwargs(kwargs=kwargs)
        return explanation if self._datamapper is None else _create_raw_feats_local_explanation(
            explanation, feature_map=self._datamapper.feature_map, **raw_kwargs)

    def create_scoring_explainer(self, data_transformer=None):
        """Create the scoring explainer for the mimic explainer.

        :param data_transformer: An object that converts raw features to engineered via .transform().
            The data output by transform should mirror the data passed into explain_global.
        :type data_transformer: An object with .transform()
        :return: The scoring explainer based on the model being explained.
        :rtype: ScoringExplainer
        """
        if self._datamapper is not None and data_transformer is not None:
            raise UserErrorException('If transformations for raw feature explanation '
                                     'were passed into the TabularExplainer init, '
                                     'please do not use data_transformer here.')
        try:
            return TreeScoringExplainer(self.surrogate_model.model,
                                        data_transformer=data_transformer,
                                        transformations=self.transformations)
        except:
            return LinearScoringExplainer(self.surrogate_model.model,
                                          self.initialization_examples.dataset,
                                          data_transformer=data_transformer,
                                          transformations=self.transformations)
