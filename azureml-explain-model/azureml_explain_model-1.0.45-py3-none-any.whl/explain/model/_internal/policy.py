# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

"""Defines explanation policies."""


def sampling_policy(allow_eval_sampling=False, max_dim_clustering=50, sampling_method="hdbscan",
                    explain_subset=None, **kwargs):
    """A set of parameters that can be tuned to speed up or improve the accuracy of the
    explain_model function during sampling. For execution time improvement, samples
    the evaluation data and/or reduces the set of features explained.

    :param allow_eval_sampling: Default to 'False'. Specify whether to allow sampling of evaluation data.
        If 'True', cluster the evaluation data and determine the optimal number
        of points for sampling. Set to 'True' to speed up the process when the
        evaluation data set is large and the user only wants to generate model
        summary info.
    :type allow_eval_sampling: bool
    :param max_dim_clustering: Default to 50 and only take effect when 'allow_eval_sampling' is
        set to 'True'. Specify the dimensionality to reduce the evaluation data before clustering
        for sampling. When doing sampling to determine how aggressively to downsample without getting poor
        explanation results uses a heuristic to find the optimal number of clusters. Since
        KMeans performs poorly on high dimensional data PCA or Truncated SVD is first run to
        reduce the dimensionality, which is followed by finding the optimal k by running
        KMeans until a local minimum is reached as determined by computing the silhouette
        score, reducing k each time.
    :type max_dim_clustering: int
    :param sampling_method: The sampling method for determining how much to downsample the evaluation data by.
        If allow_eval_sampling is True, the evaluation data is downsampled to a max_threshold, and then this
        heuristic is used to determine how much more to downsample the evaluation data without losing accuracy
        on the calculated feature importance values.  By default, this is set to hdbscan, but the user can
        also specify kmeans.  With hdbscan the number of clusters is automatically determined and multiplied by
        a threshold.  With kmeans, the optimal number of clusters is found by running KMeans until the maximum
        silhouette score is calculated, with k halved each time.
    :type sampling_method: int
    :param explain_subset: List of feature indices. If specified, only selects a subset of the
        features in the evaluation dataset for explanation, which will speed up the explanation
        process when number of features is large and the user already knows the set of interested
        features. The subset can be the top-k features from the model summary.
    :type explain_subset: list[int]
    :rtype: dict
    :return: The arguments for the sampling policy
    """
    kwargs["allow_eval_sampling"] = allow_eval_sampling
    kwargs["max_dim_clustering"] = max_dim_clustering
    kwargs["explain_subset"] = explain_subset
    kwargs["sampling_method"] = sampling_method
    return kwargs


def kernel_policy(nsamples='auto', silent=False, **kwargs):
    """A set of parameters for computing the shap_values using the KernelExplainer.

    :param nsamples: Default to 'auto'. Number of times to re-evaluate the model when
        explaining each prediction. More samples lead to lower variance estimates of the
        feature importance values, but incur more computation cost. When 'auto' is provided,
        the number of samples is computed according to a heuristic rule.
    :type nsamples: 'auto' or int
    :param silent: Default to 'False'.  Determines whether to display the explanation status bar
        when using shap_values from the KernelExplainer.
    :type silent: bool
    :rtype: dict
    :return: The arguments for the sampling policy
    """
    kwargs["nsamples"] = nsamples
    kwargs["silent"] = silent
    return kwargs
