# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

"""Defines the structured model based APIs for explainer used on specific types of models."""

from .base_explainer import BaseExplainer


class StructuredInitModelExplainer(BaseExplainer):
    """Defines the base StructuredInitModelExplainer API for explainers.

    Used on specific models that require initialization examples.
    """

    def __init__(self, model, initialization_examples, **kwargs):
        """Initialize the StructuredInitModelExplainer.

        :param model: The white box model to explain.
        :type model: model
        :param initialization_examples: A matrix of feature vector examples (# examples x # features) for
            initializing the explainer.
        :type initialization_examples: numpy.array or pandas.DataFrame or iml.datatypes.DenseData or
            scipy.sparse.csr_matrix
        """
        super(StructuredInitModelExplainer, self).__init__(**kwargs)
        self._logger.debug('Initializing StructuredInitModelExplainer')
        self.model = model
        self.initialization_examples = initialization_examples


class PureStructuredModelExplainer(BaseExplainer):
    """Defines the base PureStructuredModelExplainer API for explainers used on specific models."""

    def __init__(self, model, **kwargs):
        """Initialize the PureStructuredModelExplainer.

        :param model: The white box model to explain.
        :type model: model
        """
        super(PureStructuredModelExplainer, self).__init__(**kwargs)
        self._logger.debug('Initializing PureStructuredModelExplainer')
        self.model = model
