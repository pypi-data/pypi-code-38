# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

"""Defines explanation policies."""

try:
    from azureml._logging import ChainedIdentity
except ImportError:
    from ..common.chained_identity import ChainedIdentity

from azureml.explain.model._internal.constants import History, Defaults


def storage_policy(block_size=None, max_num_blocks=None, **kwargs):
    """Set of parameters for defining the storage policy on explanations.

    :param block_size: The size of each block for the summary stored in artifacts storage.
    :type block_size: int
    :param max_num_blocks: The maximum number of blocks to store.
    :type max_num_blocks: int
    :rtype: dict
    :return: The arguments for the storage policy
    """
    kwargs[History.BLOCK_SIZE] = block_size
    kwargs[History.MAX_NUM_BLOCKS] = max_num_blocks
    return kwargs


class SamplingPolicy(ChainedIdentity):
    """Defines the sampling policy for downsampling the evaluation examples.

    The policy is a set of parameters that can be tuned to speed up or improve the accuracy of the
    explain_model function during sampling.
    """

    def __init__(self, allow_eval_sampling=False, max_dim_clustering=Defaults.MAX_DIM,
                 sampling_method=Defaults.HDBSCAN, **kwargs):
        """Initialize the SamplingPolicy.

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
        :type sampling_method: str
        :rtype: dict
        :return: The arguments for the sampling policy
        """
        super(SamplingPolicy, self).__init__(**kwargs)
        self._allow_eval_sampling = allow_eval_sampling
        self._max_dim_clustering = max_dim_clustering
        self._sampling_method = sampling_method

    @property
    def allow_eval_sampling(self):
        """Get whether to allow sampling of evaluation data.

        :return: Whether to allow sampling of evaluation data.
        :rtype: bool
        """
        return self._allow_eval_sampling

    @property
    def max_dim_clustering(self):
        """Get the dimensionality to reduce the evaluation data before clustering for sampling.

        :return: The dimensionality to reduce the evaluation data before clustering for sampling.
        :rtype: int
        """
        return self._max_dim_clustering

    @property
    def sampling_method(self):
        """Get the sampling method for determining how much to downsample the evaluation data by.

        :return: The sampling method for determining how much to downsample the evaluation data by.
        :rtype: str
        """
        return self._sampling_method
