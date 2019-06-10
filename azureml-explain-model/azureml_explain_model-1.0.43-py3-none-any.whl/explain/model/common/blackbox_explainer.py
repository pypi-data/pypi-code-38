# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

"""Defines the black box explainer API, which can either take in a black box model or function."""

import numpy as np
import scipy as sp
from functools import wraps

from .base_explainer import BaseExplainer
from .aggregate import init_aggregator_decorator

try:
    from azureml._logging import ChainedIdentity
except ImportError:
    from ..common.chained_identity import ChainedIdentity


class BlackBoxMixin(ChainedIdentity):
    """Mixin for black box models or functions."""

    def __init__(self, model, is_function=False, **kwargs):
        """Initialize the BlackBoxMixin.

        :param model: The model to explain or function if is_function is True.
        :type model: model that implements predict or predict_proba or function that accepts a 2d ndarray
        :param is_function: Default set to false, set to True if passing predict or predict_proba
            function instead of model.
        :type is_function: bool
        """
        super(BlackBoxMixin, self).__init__(**kwargs)
        self._logger.debug('Initializing BlackBoxMixin')
        # If true, this is a classification model
        self.predict_proba_flag = hasattr(model, "predict_proba")

        if is_function:
            self._logger.debug('Function passed in, no model')
            self.function = model
            self.model = None
        else:
            self._logger.debug('Model passed in')
            self.model = model
            if self.predict_proba_flag:
                self.function = self.model.predict_proba
            else:
                errMsg = 'predict_proba not supported by given model, assuming regression model and trying predict'
                self._logger.info(errMsg)
                # try predict instead since this is likely a regression scenario
                self.function = self.model.predict


class BlackBoxExplainer(BaseExplainer, BlackBoxMixin):
    """The base class for black box models or functions."""

    def __init__(self, model, is_function=False, **kwargs):
        """Initialize the BlackBoxExplainer.

        :param model: The model to explain or function if is_function is True.
        :type model: model that implements predict or predict_proba or function that accepts a 2d ndarray
        :param is_function: Default set to false, set to True if passing predict or predict_proba
            function instead of model.
        :type is_function: bool
        """
        super(BlackBoxExplainer, self).__init__(model, is_function=is_function, **kwargs)
        self._logger.debug('Initializing BlackBoxExplainer')


def init_blackbox_decorator(init_func):
    """Decorate a constructor to wrap initialization examples in a DatasetWrapper.

    Provided for convenience for tabular data explainers.

    :param init_func: Initialization constructor where the second argument is a dataset.
    :type init_func: Initialization constructor.
    """
    init_func = init_aggregator_decorator(init_func)

    @wraps(init_func)
    def init_wrapper(self, model, *args, **kwargs):
        self.explainer = None
        self.current_index_list = [0]
        self.original_data_ref = [None]
        return init_func(self, model, *args, **kwargs)

    return init_wrapper


def add_prepare_function_and_summary_method(cls):
    """Decorate blackbox explainer to allow aggregating local explanations to global.

    Adds two protected methods _function_subset_wrapper and _prepare_function_and_summary to
    the blackbox explainer.  The former creates a wrapper around the prediction function for
    explaining subsets of features in the evaluation samples dataset.  The latter calls the
    former to create a wrapper and also computes the summary background dataset for the explainer.
    """
    def _function_subset_wrapper(self, original_data_ref, explain_subset, f, current_index_list):
        """Create a wrapper around the prediction function.

        See more details on wrapper.

        :return: The wrapper around the prediction function.
        """
        def wrapper(data):
            """Private wrapper around the prediction function.

            Adds back in the removed columns when using the explain_subset parameter.
            We tile the original evaluation row by the number of samples generated
            and replace the subset of columns the user specified with the result from shap,
            which is the input data passed to the wrapper.

            :return: The prediction function wrapped by a helper method.
            """
            # If list is empty, just return the original data, as this is the background case
            original_data = original_data_ref[0]
            idx = current_index_list[0]
            tiles = int(data.shape[0])
            evaluation_row = original_data[idx]
            if sp.sparse.issparse(evaluation_row):
                if not sp.sparse.isspmatrix_csr(evaluation_row):
                    evaluation_row = evaluation_row.tocsr()
                nnz = evaluation_row.nnz
                rows, cols = evaluation_row.shape
                rows *= tiles
                shape = rows, cols
                if nnz == 0:
                    examples = sp.sparse.csr_matrix(shape, dtype=evaluation_row.dtype).tolil()
                else:
                    new_indptr = np.arange(0, rows * nnz + 1, nnz)
                    new_data = np.tile(evaluation_row.data, rows)
                    new_indices = np.tile(evaluation_row.indices, rows)
                    examples = sp.sparse.csr_matrix((new_data, new_indices, new_indptr),
                                                    shape=shape).tolil()
            else:
                examples = np.tile(original_data[idx], tiles).reshape((data.shape[0], original_data.shape[1]))
            examples[:, explain_subset] = data
            return f(examples)
        return wrapper

    def _prepare_function_and_summary(self, function, original_data_ref,
                                      current_index_list, explain_subset=None, **kwargs):
        if explain_subset:
            # Note: need to take subset before compute summary
            self.initialization_examples.take_subset(explain_subset)
        self.initialization_examples.compute_summary(**kwargs)
        if explain_subset:
            if original_data_ref[0] is None:
                # This is only used for construction; not used during general computation
                original_data_ref[0] = self.initialization_examples.original_dataset
            function = self._function_subset_wrapper(original_data_ref, explain_subset,
                                                     function, current_index_list)
        summary = self.initialization_examples.dataset
        return function, summary

    setattr(cls, '_function_subset_wrapper', _function_subset_wrapper)
    setattr(cls, '_prepare_function_and_summary', _prepare_function_and_summary)
    return cls
