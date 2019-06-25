# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

"""Defines utilities for handling kwargs on SHAP-based explainers."""

from azureml.explain.model.shap import kwargs_utils


def _get_explain_global_kwargs(sampling_policy, method, include_local):
    """Get the kwargs for explain_global.

    :param sampling_policy: Optional policy for sampling the evaluation examples.  See documentation on
        SamplingPolicy for more information.
    :type sampling_policy: SamplingPolicy
    :param include_local: Include the local explanations in the returned global explanation.
        If include_local is False, will stream the local explanations to aggregate to global.
    :type include_local: bool
    :return: Args for explain_global.
    :rtype: dict
    """
    kwargs = kwargs_utils._get_explain_global_kwargs(sampling_policy, method, include_local)
    return kwargs
