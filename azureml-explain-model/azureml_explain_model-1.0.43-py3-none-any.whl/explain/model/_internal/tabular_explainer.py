# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

"""Defines the tabular explainer for getting model explanations from tabular data."""

import os
import numpy as np
import pandas as pd
import scipy as sp
import sys

try:
    from azureml._restclient.assets_client import AssetsClient
    from azureml._restclient.constants import RUN_ORIGIN
except ImportError:
    print('Could not import azureml.core, required if using run history')
from .common import module_logger, _sort_values, _sort_feature_list_single, _sort_feature_list_multiclass
from .base_explainer import BaseExplainer
from .model_summary import ModelSummary
from .constants import Attributes, Defaults, ExplainType, History, SKLearn, BackCompat

import warnings

with warnings.catch_warnings():
    warnings.filterwarnings('ignore', 'Starting from version 2.2.1', UserWarning)
    import shap
    from shap.common import DenseData


def summarize_data(X, k, to_round_values=True):
    """Summarize a dataset.
    For dense dataset, use k mean samples weighted by the number of data points they
    each represent.
    For sparse dataset, use a sparse row for the background with calculated
    median for dense columns.

    :param X: Matrix of data samples to summarize (# samples x # features).
    :type X: numpy.array or pandas.DataFrame or scipy.sparse.csr_matrix
    :param k: Number of cluster centroids to use for approximation.
    :type k: int
    :param to_round_values: When using kmeans, for each element of every cluster centroid to match the nearest value
        from X in the corresponding dimension. This ensures discrete features
        always get a valid value.  Ignored for sparse data sample.
    :type to_round_values: bool
    :return: DenseData or SparseData object.
    :rtype: iml.datatypes.DenseData or iml.datatypes.SparseData
    """
    is_sparse = sp.sparse.issparse(X)
    if not isinstance(X, DenseData):
        if is_sparse:
            # instead of using kmeans, pass in background of zeros
            # for dense columns, calculate median of data
            # TODO: calculate median of data here
            return sp.sparse.csr_matrix((1, X.shape[1]), dtype=X.dtype)
        elif len(X) > 10 * k:
            # use kmeans to summarize the examples for initialization
            # if there are more than 10 x k of them
            return shap.kmeans(X, k, to_round_values)
    return X


class logger_redirector(object):
    """A redirector for system error output to logger."""

    def __init__(self, module_logger):
        """Initialize the logger_redirector.

        :param module_logger: The logger to use for redirection.
        :type module_logger: logger
        """
        self.logger = module_logger

    def __enter__(self):
        """Start the redirection for logging."""
        self.logger.debug('Redirecting user output to logger')
        self.original_stderr = sys.stderr
        sys.stderr = self

    def write(self, data):
        """Write the given data to logger.

        :param data: The data to write to logger.
        :type data: str
        """
        self.logger.debug(data)

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Finishes the redirection for logging."""
        try:
            if exc_val:
                # The default traceback.print_exc() expects a file-like object which
                # OutputCollector is not. Instead manually print the exception details
                # to the wrapped sys.stderr by using an intermediate string.
                # trace = traceback.format_tb(exc_tb)
                import traceback
                trace = ''.join(traceback.format_exception(exc_type, exc_val, exc_tb))
                print(trace, file=sys.stderr)
        finally:
            sys.stderr = self.original_stderr
            self.logger.debug('User scope execution complete.')


class TabularExplainer(BaseExplainer):
    """Explain a model trained on a tabular dataset."""
    def __init__(self, workspace=None, experiment_name=None, run_id=None):
        """Initializes the Tabular Explainer.
        If workspace and experiment_name are provided, a new Run will be created and the model
        explanation data will be stored and managed by Run History service. The explanation
        data will be associated with this new Run and can be retrieved at a later time,
        for example, through its ID. If workspace, experiment_name and run_id are all provided,
        the explanation data will be associated with the Run that has the same Run ID.
        Otherwise, the data are only available locally.

        :param workspace: An object that represents a workspace.
        :type workspace: azureml.core.workspace.Workspace
        :param experiment_name: The name of an experiment.
        :type experiment_name: str
        :param run_id: A GUID that represents a run.
        :type run_id: str
        """
        BaseExplainer.__init__(self, workspace, experiment_name, run_id)
        if workspace is not None:
            self.assets_client = AssetsClient(workspace.service_context)
            self.workspace = workspace
        self.neighbors = None
        self.scaler = None
        self.nn_shap_values = None
        self.explainer = None

    def _reduce_eval_examples(self, evaluation_examples, max_dim_clustering=50):
        """Reduces the dimensionality of the evaluation examples if dimensionality is higher
        than max_dim_clustering.  If the dataset is sparse, we mean-scale the data and then run
        truncated SVD to reduce the number of features to max_dim_clustering.  For dense
        dataset, we also scale the data and then run PCA to reduce the number of features to
        max_dim_clustering.
        This is used to get better clustering results in _find_k.
        """
        from sklearn.decomposition import TruncatedSVD, PCA
        from sklearn.preprocessing import StandardScaler
        num_cols = evaluation_examples.shape[1]
        # Run PCA or SVD on input data and reduce to about 50 features prior to clustering
        components = min(max_dim_clustering, num_cols)
        reduced_eval_examples = evaluation_examples
        if components != num_cols:
            if sp.sparse.issparse(evaluation_examples):
                normalized_eval_examples = StandardScaler(with_mean=False).fit_transform(evaluation_examples)
                reducer = TruncatedSVD(n_components=components)
            else:
                normalized_eval_examples = StandardScaler().fit_transform(evaluation_examples)
                reducer = PCA(n_components=components)
            module_logger.info('reducing dimensionality to {} components for clustering'.format(str(components)))
            reduced_eval_examples = reducer.fit_transform(normalized_eval_examples)
        return reduced_eval_examples

    def _find_k_kmeans(self, evaluation_examples, max_dim_clustering=50):
        """Uses k-means to downsample the evaluation examples.
        Starting from k_upper_bound, cuts k in half each time and run k-means
        clustering on the evaluation_examples.  After each run, computes the
        silhouette score and stores k with highest silhouette score.
        We use optimal k to determine how much to downsample the evaluation_examples.
        """
        from sklearn.cluster import KMeans
        from sklearn.metrics import silhouette_score
        from math import log, isnan, ceil
        reduced_eval_examples = self._reduce_eval_examples(evaluation_examples, max_dim_clustering)
        num_rows = evaluation_examples.shape[0]
        k_upper_bound = 2000
        k_list = []
        k = min(num_rows / 2, k_upper_bound)
        for i in range(int(ceil(log(num_rows, 2) - 7))):
            k_list.append(int(k))
            k /= 2
        prev_highest_score = -1
        prev_highest_index = 0
        opt_k = int(k)
        for k_index, k in enumerate(k_list):
            module_logger.info('running KMeans with k: ' + str(k))
            km = KMeans(n_clusters=k).fit(reduced_eval_examples)
            clusters = km.labels_
            num_clusters = len(set(clusters))
            k_too_big = num_clusters <= 1
            if k_too_big or num_clusters == reduced_eval_examples.shape[0]:
                score = -1
            else:
                score = silhouette_score(reduced_eval_examples, clusters)
            if isnan(score):
                score = -1
            module_logger.info('KMeans silhouette score: ' + str(score))
            # Find k with highest silhouette score for optimal clustering
            if score >= prev_highest_score and not k_too_big:
                prev_highest_score = score
                prev_highest_index = k_index
        opt_k = k_list[prev_highest_index]
        module_logger.info('best silhouette score: ' + str(prev_highest_score))
        module_logger.info('found optimal k for KMeans: ' + str(opt_k))
        return opt_k

    def _find_k_hdbscan(self, evaluation_examples, max_dim_clustering=50):
        """Uses hdbscan to downsample the evaluation examples.
        We use optimal k to determine how much to downsample the evaluation_examples.
        """
        import hdbscan
        num_rows = evaluation_examples.shape[0]
        reduced_eval_examples = self._reduce_eval_examples(evaluation_examples, max_dim_clustering)
        hdbs = hdbscan.HDBSCAN(min_cluster_size=2).fit(reduced_eval_examples)
        clusters = hdbs.labels_
        opt_k = len(set(clusters))
        clustering_threshold = 5
        samples = opt_k * clustering_threshold
        module_logger.info('found optimal k for hdbscan: {}, will use clustering_threshold * k for sampling: {}'
                           .format(str(opt_k), str(samples)))
        return min(samples, num_rows)

    def _sample_evaluation_examples(self,
                                    evaluation_examples,
                                    max_dim_clustering=Defaults.MAX_DIM,
                                    sampling_method=Defaults.HDBSCAN):
        """Samples the evaluation examples.  First does random downsampling to upper_bound rows,
        then tries to find the optimal downsample based on how many clusters can be constructed
        from the data.  If sampling_method is hdbscan, uses hdbscan to cluster the evaluation
        data and then downsamples to that number of clusters.  If sampling_method is k-means,
        uses different values of k, cutting in half each time, and chooses the k with highest
        silhouette score to determine how much to downsample the data.
        The danger of using only random downsampling is that we might downsample too much
        or too little, so the clustering approach is a heuristic to give us some idea of
        how much we should downsample to.
        """
        from sklearn.utils import resample
        lower_bound = 200
        upper_bound = 10000
        num_rows = evaluation_examples.shape[0]
        module_logger.info('sampling evaluation examples')
        # If less than lower_bound rows, just return the full dataset
        if num_rows < lower_bound:
            return evaluation_examples
        # If more than upper_bound rows, sample randomly
        elif num_rows > upper_bound:
            module_logger.info('randomly sampling to 10k rows')
            evaluation_examples = resample(evaluation_examples, n_samples=upper_bound, random_state=7)
            num_rows = upper_bound
        if sampling_method == Defaults.HDBSCAN:
            try:
                opt_k = self._find_k_hdbscan(evaluation_examples, max_dim_clustering)
            except Exception as ex:
                module_logger.warning('Failed to use hdbscan due to error: {}\n'
                                      'Ensure hdbscan is installed with: pip install hdbscan'.format(str(ex)))
                opt_k = self._find_k_kmeans(evaluation_examples, max_dim_clustering)
        else:
            opt_k = self._find_k_kmeans(evaluation_examples, max_dim_clustering)
        # Resample based on optimal number of clusters
        if (opt_k < num_rows):
            return resample(evaluation_examples, n_samples=opt_k, random_state=7)
        return evaluation_examples

    def _get_dense_examples(self, examples):
        if sp.sparse.issparse(examples):
            return examples.toarray()
        return examples

    def _run_tree_explainer(self, model, evaluation_examples, explain_subset):
        try:
            module_logger.debug('Attempting to use TreeExplainer')
            self.explainer = shap.TreeExplainer(model)

            # for now convert evaluation examples to dense format if they are sparse
            # until TreeExplainer sparse support is added
            shap_values = self.explainer.shap_values(self._get_dense_examples(evaluation_examples))
            classification = isinstance(shap_values, list)
            if explain_subset:
                if classification:
                    for i in range(shap_values.shape[0]):
                        shap_values[i] = shap_values[i][:, explain_subset]
                else:
                    shap_values = shap_values[:, explain_subset]
            return shap_values, classification
        except Exception as ex:
            module_logger.debug('Encountered error when using TreeExplainer: ' + str(ex))
            return None

    def _run_deep_explainer(self, model, summary, evaluation_examples, **kwargs):
        try:
            explain_subset = kwargs.get('explain_subset', None)
            module_logger.debug('Attempting to use DeepExplainer')
            # Suppress warning message from Keras
            with logger_redirector(module_logger):
                self.explainer = shap.DeepExplainer(model, summary.data)
            # sample the evaluation examples
            allow_eval_sampling = kwargs.get('allow_eval_sampling', False)
            if allow_eval_sampling:
                max_dim_clustering = kwargs.get('max_dim_clustering', Defaults.MAX_DIM)
                sampling_method = kwargs.get('sampling_method', Defaults.HDBSCAN)
                evaluation_examples = self._sample_evaluation_examples(evaluation_examples, max_dim_clustering,
                                                                       sampling_method=sampling_method)

            # for now convert evaluation examples to dense format if they are sparse
            # until DeepExplainer sparse support is added
            shap_values = self.explainer.shap_values(self._get_dense_examples(evaluation_examples))
            classification = isinstance(shap_values, list)
            if explain_subset:
                if classification:
                    for i in range(shap_values.shape[0]):
                        shap_values[i] = shap_values[i][:, explain_subset]
                else:
                    shap_values = shap_values[:, explain_subset]
            return shap_values, classification
        except Exception as ex:
            module_logger.debug('Encountered error when using DeepExplainer: ' + str(ex))
            return None

    def _run_kernel_explainer(self, model, summary, evaluation_examples, original_evaluation, **kwargs):
        explain_subset = kwargs.get('explain_subset', None)

        def shap_values_on_prediction(f, summary):
            # Note: we capture index and f in the wrapper function below around the model prediction function.
            # When enumerating over the examples this values is updated and the update is visible in the
            # wrapper function below.  This is necessary to determine which example to tile when translating
            # back to the model's input domain.
            idx = 0

            def wrapper(data):
                """
                A private wrapper around the prediction function to add back in the removed columns
                when using the explain_subset parameter.
                We tile the original evaluation row by the number of samples generated
                and replace the subset of columns the user specified with the result from shap,
                which is the input data passed to the wrapper.
                :return: The prediction function wrapped by a helper method.
                """
                tiles = int(data.shape[0])
                evaluation_row = original_evaluation[idx]
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
                    examples = np.tile(original_evaluation[idx], tiles).reshape((data.shape[0],
                                                                                original_evaluation.shape[1]))
                examples[:, explain_subset] = data
                return f(examples)

            model_func = f
            if explain_subset:
                model_func = wrapper
            self.explainer = shap.KernelExplainer(model_func, summary)
            if explain_subset:
                output_shap_values = None
                for ex_idx, example in enumerate(evaluation_examples):
                    idx = ex_idx
                    tmp_shap_values = self.explainer.shap_values(example, **kwargs)
                    classification = isinstance(tmp_shap_values, list)
                    if classification:
                        if output_shap_values is None:
                            output_shap_values = tmp_shap_values
                            for i in range(len(output_shap_values)):
                                cols_dim = len(output_shap_values[i].shape)
                                concat_cols = output_shap_values[i].shape[cols_dim - 1]
                                output_shap_values[i] = output_shap_values[i].reshape(1, concat_cols)
                        else:
                            for i in range(len(output_shap_values)):
                                cols_dim = len(tmp_shap_values[i].shape)
                                # col_dim can only be 1 or 2 here, depending on data passed to shap
                                if cols_dim != 2:
                                    out_cols_dim = len(output_shap_values[i].shape)
                                    output_size = output_shap_values[i].shape[out_cols_dim - 1]
                                    tmp_shap_values_2d = tmp_shap_values[i].reshape(1, output_size)
                                else:
                                    tmp_shap_values_2d = tmp_shap_values[i]
                                # Append rows
                                output_shap_values[i] = np.append(output_shap_values[i],
                                                                  tmp_shap_values_2d, axis=0)
                    else:
                        if output_shap_values is None:
                            output_shap_values = tmp_shap_values
                        else:
                            output_shap_values = np.append(output_shap_values, tmp_shap_values, axis=0)
                return output_shap_values
            else:
                return self.explainer.shap_values(evaluation_examples, **kwargs)

        def classification_shap_values(model, summary):
            f = model.predict_proba
            return shap_values_on_prediction(f, summary)

        def regression_shap_values(model, summary):
            f = model.predict
            return shap_values_on_prediction(f, summary)

        try:
            # try to use predict_proba for classification scenario
            shap_values = classification_shap_values(model, summary)
        except AttributeError as ae:
            module_logger.info(
                'predict_proba not supported by given model, assuming regression model and trying predict: ' +
                str(ae))
            # try predict instead since this is likely a regression scenario
            shap_values = regression_shap_values(model, summary)
        classification = isinstance(shap_values, list)
        return shap_values, classification

    # Single node explain model function
    def explain_model(self, model, initialization_examples, evaluation_examples=None,
                      features=None, classes=None, nclusters=10,
                      top_k=None, create_scoring_model=False, **kwargs):
        """Explain a model by explaining its predictions on samples.
        :param model: An object that represents a model. It is assumed that for the classification case \
            it has a method of predict_proba() returning the prediction probabilities for each \
            class and for the regression case a method of predict() returning the prediction value.
        :type model: object
        :param initialization_examples: A matrix of feature vector examples (# examples x # features) for
            initializing the explainer. For small problems this set of examples for initialization can be
            the whole training set, but for larger problems consider using a single reference value or using
            the built-in kmeans function to summarize the whole or downsampled training set by
            specifying nclusters (the number of cluster centroids). A function summarize_data is
            also provided to summarize the initialization_examples separately. The output of this
            function can be passed to this method.
        :type initialization_examples: numpy.array or pandas.DataFrame or iml.datatypes.DenseData or
                                      scipy.sparse.csr_matrix
        :param evaluation_examples: A matrix of feature vector examples (# examples x # features) on which
            to explain the model's output.
        :type evaluation_examples: numpy.array or pandas.DataFrame or scipy.sparse.csr_matrix
        :param features: A list of feature names.
        :type features: list[str]
        :param classes: Class names, in any form that can be converted to an array of str. This includes
            lists, lists of tuples, tuples, tuples of tuples, tuples of lists and ndarrays. The order of
            the class names should match that of the model output.
        :type classes: array_like[str]
        :param nclusters: Number of means to use for approximation. A dataset is summarized with nclusters mean
            samples weighted by the number of data points they each represent. When the number of initialization
            examples is larger than (10 x nclusters), those examples will be summarized with k-means where
            k = nclusters.
        :type nclusters: int
        :param top_k: Number of the top most important features in model summary. If specified, only the model
            summary data corresponding to the top K most important features will be returned/stored.
        :type top_k: int
        :param create_scoring_model: Creates a model that can be used for scoring to approximate the feature
            importance values of data faster than SHAP.  See explain_from_scoring_model for more details.
        :type create_scoring_model: bool
        :return: tuple(run, local_importance_values, expected_values, global_importance_values,
            overall_important_features, per_class_importance_values, per_class_important_features)
            where
            - run = An object that represents an model explanation run. Only availabe if workspace
            and experiment_name are both provided.
            - local_importance_values = For a model with a single output such as regression, this returns
            a matrix of feature importance values. For models with vector outputs this function returns a
            list of such matrices, one for each output. The dimension of this matrix is (# examples x # features).
            - expected_values = The expected value of the model applied to the set of initialization examples.
            For SHAP values, when a version older than 0.20.0 is used, this value is None. The expected
            values are in the last columns of the matrices in local_importance_values. In this case, the
            dimension of those matrix is (# examples x (# features + 1)). This causes each row to sum to
            the model output for that example.
            - global_importance_values = The model level feature importance values sorted in
            descending order.
            - overall_important_features = The feature names sorted in the same order as in global_importance_values
            or the indexes that would sort global_importance_values.
            - per_class_importance_values = The class level feature importance values sorted in
            descending order where a binary classification (this class or not) is evaluated. Only available
            for the classification case.
            - per_class_important_features = The feature names sorted in the same order as in per_class_values
            or the indexes that would sort per_class_values. Only available for the classification case.
        :rtype: (azureml.core.run.Run, Union[list, list[list]], list, list, list, list, list)
        """
        if evaluation_examples is None:
            raise ValueError('evaluation_examples is required')
        explain_subset = kwargs.get('explain_subset', None)
        # try to use TreeExplainer which is more accurate first
        result = self._run_tree_explainer(model, evaluation_examples, explain_subset)
        # if model is not a Tree-based model, try to use the Deep Explainer
        if (result is None):
            summary = summarize_data(initialization_examples, nclusters)
            module_logger.debug('Could not use TreeExplainer, using DeepExplainer instead')
            result = self._run_deep_explainer(model, summary, evaluation_examples, **kwargs)
            # otherwise, use the KernelExplainer as the default for least-specific-model
            if (result is None):
                module_logger.debug('Could not use TreeExplainer and DeepExplainer, using KernelExplainer instead')
                # Compute subset info prior
                original_evaluation = None
                if explain_subset:
                    original_evaluation = evaluation_examples
                    eval_is_df = isinstance(original_evaluation, pd.DataFrame)
                    eval_is_series = isinstance(original_evaluation, pd.Series)
                    if eval_is_df or eval_is_series:
                        original_evaluation = original_evaluation.values
                    evaluation_examples = original_evaluation[:, explain_subset]
                    init_is_df = isinstance(initialization_examples, pd.DataFrame)
                    init_is_series = isinstance(initialization_examples, pd.Series)
                    if init_is_df or init_is_series:
                        initialization_examples = initialization_examples.values
                    initialization_examples = initialization_examples[:, explain_subset]
                    # Edge case: Take the subset of the summary in this case,
                    # more optimal than recomputing the summary!
                    if isinstance(summary, DenseData):
                        summary = DenseData(summary.data[:, explain_subset], summary.group_names[explain_subset])
                    else:
                        summary = summary[:, explain_subset]
                # sample the evaluation examples
                # note: the sampled data is also used by KNN below
                allow_eval_sampling = kwargs.get('allow_eval_sampling', False)
                if allow_eval_sampling:
                    max_dim_clustering = kwargs.get('max_dim_clustering', Defaults.MAX_DIM)
                    sampling_method = kwargs.get('sampling_method', Defaults.HDBSCAN)
                    evaluation_examples = self._sample_evaluation_examples(evaluation_examples, max_dim_clustering,
                                                                           sampling_method=sampling_method)
                result = self._run_kernel_explainer(model, summary, evaluation_examples, original_evaluation,
                                                    **kwargs)
        shap_values, classification = result
        if create_scoring_model:
            # normalize features prior to using knn
            from sklearn.preprocessing import StandardScaler
            if sp.sparse.issparse(evaluation_examples):
                self.scaler = StandardScaler(with_mean=False).fit(evaluation_examples)
            else:
                self.scaler = StandardScaler().fit(evaluation_examples)
            # compute nearest neighbors, can be used in scoring path
            from sklearn.neighbors import NearestNeighbors
            scaled_data = self.scaler.transform(evaluation_examples)
            self.neighbors = NearestNeighbors(n_neighbors=1, algorithm=SKLearn.BALL_TREE).fit(scaled_data)
            self.nn_shap_values = shap_values
        if features is None and isinstance(initialization_examples, pd.DataFrame):
            features = initialization_examples.columns.tolist()
        if classification:
            # TODO
            shap_values, expected_values, global_importance_values, global_importance_names, global_importance_rank, \
                per_class_values, per_class_names, per_class_rank = \
                self._compute_summary(shap_values, classification, features, top_k)
        else:
            shap_values, expected_values, global_importance_values, global_importance_names, global_importance_rank = \
                self._compute_summary(shap_values, classification, features, top_k)
        # Convert all values to list
        if classification:
            # shap_values is a list of ndarrays
            shap_values_numpy_free = []
            for array in shap_values:
                shap_values_numpy_free.append(array.tolist())
            shap_values = shap_values_numpy_free
            l_per_class_values = per_class_values.tolist()
            l_per_class_names = per_class_names.tolist()
        else:
            shap_values = shap_values.tolist()
        if expected_values is not None:
            # expected values may be a vector or a scalar
            if isinstance(expected_values, np.ndarray):
                expected_values = expected_values.tolist()
        l_global_importance_values = global_importance_values.tolist()
        l_global_importance_names = global_importance_names.tolist()
        if self.run is not None:
            # save model type and explainer type
            model_type = ExplainType.CLASSIFICATION if classification else ExplainType.REGRESSION
            self.run.add_properties({ExplainType.MODEL: model_type,
                                     ExplainType.EXPLAINER: ExplainType.TABULAR})
            # upload the shap values, overall summary, per class summary, classes and feature names
            upload_dir = self._create_upload_dir()
            self._upload_artifact(upload_dir, BackCompat.SHAP_VALUES, shap_values)
            if expected_values is not None:
                self._upload_artifact(upload_dir, History.EXPECTED_VALUES, expected_values)
            summary_object = ModelSummary()
            if features is not None:
                if isinstance(features, np.ndarray):
                    features = features.tolist()
                self._upload_artifact(upload_dir, History.FEATURES, features)
                # TODO what if feature names are really long
                summary_object.add_from_get_model_summary(
                    History.GLOBAL_IMPORTANCE_NAMES,
                    self._get_model_summary_artifacts(upload_dir,
                                                      History.GLOBAL_IMPORTANCE_NAMES,
                                                      np.array(_sort_feature_list_single(features,
                                                                                         global_importance_rank))))
                if classification:
                    summary_object.add_from_get_model_summary(
                        History.PER_CLASS_NAMES,
                        self._get_model_summary_artifacts(upload_dir,
                                                          History.PER_CLASS_NAMES,
                                                          np.array(_sort_feature_list_multiclass(features,
                                                                                                 per_class_rank))))

            summary_object.add_from_get_model_summary(
                History.GLOBAL_IMPORTANCE_VALUES,
                self._get_model_summary_artifacts(upload_dir,
                                                  History.GLOBAL_IMPORTANCE_VALUES,
                                                  global_importance_values))
            summary_object.add_from_get_model_summary(
                History.GLOBAL_IMPORTANCE_RANK,
                self._get_model_summary_artifacts(upload_dir,
                                                  History.GLOBAL_IMPORTANCE_RANK,
                                                  global_importance_rank))
            if classification:
                summary_object.add_from_get_model_summary(
                    History.PER_CLASS_VALUES,
                    self._get_model_summary_artifacts(upload_dir,
                                                      History.PER_CLASS_VALUES,
                                                      per_class_values))
                summary_object.add_from_get_model_summary(
                    History.PER_CLASS_RANK,
                    self._get_model_summary_artifacts(upload_dir,
                                                      History.PER_CLASS_RANK,
                                                      per_class_rank))
                if classes is not None:
                    if isinstance(classes, np.ndarray):
                        classes = classes.tolist()
                    self._upload_artifact(upload_dir, History.CLASSES, classes)
                    class_artifact_info = [{History.PREFIX: os.path.normpath('{}/{}/{}/{}'.format(RUN_ORIGIN,
                                                                             self.run.id,
                                                                             upload_dir,
                                                                             History.CLASSES))}]
                    class_metadata_info = {History.NUM_CLASSES: len(classes)}
                    summary_object.add_from_get_model_summary(History.CLASSES,
                                                              (class_artifact_info, class_metadata_info))
                self._upload_artifact(upload_dir,
                                      History.RICH_METADATA,
                                      summary_object.get_metadata_dictionary())
                self.assets_client.create_asset(History.EXPLANATION_ASSET,
                                                summary_object.get_artifacts(),
                                                metadata_dict={History.METADATA_ARTIFACT: History.RICH_METADATA},
                                                run_id=self.run.id,
                                                properties={History.TYPE: History.EXPLANATION,
                                                            History.VERSION_TYPE: History.EXPLANATION_ASSET_TYPE_V2})
                return self.run, shap_values, expected_values, l_global_importance_values, l_global_importance_names, \
                    l_per_class_values, l_per_class_names
            else:
                self._upload_artifact(upload_dir,
                                      History.RICH_METADATA,
                                      summary_object.get_metadata_dictionary())
                self.assets_client.create_asset(History.EXPLANATION_ASSET,
                                                summary_object.get_artifacts(),
                                                metadata_dict={History.METADATA_ARTIFACT: History.RICH_METADATA},
                                                run_id=self.run.id,
                                                properties={History.TYPE: History.EXPLANATION,
                                                            History.VERSION_TYPE: History.EXPLANATION_ASSET_TYPE_V2})
                return self.run, shap_values, expected_values, l_global_importance_values, l_global_importance_names
        else:
            if classification:
                return shap_values, expected_values, l_global_importance_values, l_global_importance_names, \
                    l_per_class_values, l_per_class_names
            else:
                return shap_values, expected_values, l_global_importance_values, l_global_importance_names

    def _compute_summary(self, shap_values, classification, features, top_k):
        expected_values = None
        if self.explainer is not None and hasattr(self.explainer, Attributes.EXPECTED_VALUE):
            expected_values = self.explainer.expected_value
        if classification:
            # calculate the summary
            per_class_values = np.mean(np.absolute(shap_values), axis=1)
            i = np.arange(len(per_class_values))[:, np.newaxis]
            per_class_rank = self._order_imp(per_class_values)
            global_importance_values = np.mean(per_class_values, axis=0)
            global_importance_rank = self._order_imp(global_importance_values)
            if top_k is not None and len(global_importance_rank) > top_k:
                global_importance_rank = global_importance_rank[0:top_k]
                per_class_rank = per_class_rank[:, 0:top_k]
            # sort the per class summary
            per_class_values = per_class_values[i, per_class_rank]
            # sort the overall summary
            global_importance_values = global_importance_values[global_importance_rank]
        else:
            global_importance_values = np.mean(np.absolute(shap_values), axis=0)
            global_importance_rank = self._order_imp(global_importance_values)
            if top_k is not None and len(global_importance_rank) > top_k:
                global_importance_rank = global_importance_rank[0:top_k]
            # sort the overall summary
            global_importance_values = global_importance_values[global_importance_rank]
        if features is not None:
            global_importance_names = _sort_values(features, global_importance_rank)
            if classification:
                per_class_names = _sort_values(features, per_class_rank)
        else:
            # return order of importance
            global_importance_names = global_importance_rank
            if classification:
                per_class_names = per_class_rank
        if classification:
            return shap_values, expected_values, global_importance_values, global_importance_names, \
                global_importance_rank, per_class_values, per_class_names, per_class_rank
        else:
            return shap_values, expected_values, global_importance_values, global_importance_names, \
                global_importance_rank

    def explain_from_scoring_model(self, evaluation_examples):
        """Uses the model generated by explain_model for scoring to approximate the feature importance
        values of data faster than SHAP.

        :param evaluation_examples: A matrix of feature vector examples (# examples x # features) on
            which to explain the model's output.
        :type evaluation_examples: numpy.array or pandas.DataFrame or scipy.sparse.csr_matrix
        :return local_importance_values: For a model with a single output such as regression,
            this returns a matrix of feature importance values. For models with vector outputs
            this function returns a list of such matrices, one for each output. The dimension
            of this matrix is (# examples x # features).
        :rtype local_importance_values: list
        """
        _, indices = self.neighbors.kneighbors(self.scaler.transform(evaluation_examples))
        # flatten indices for 1-NN
        indices = [index for row in indices for index in row]
        classification = isinstance(self.nn_shap_values, list)
        if classification:
            shap_values = []
            for i in range(len(self.nn_shap_values)):
                shap_values.append(self.nn_shap_values[i][indices].tolist())
            return shap_values
        else:
            return self.nn_shap_values[indices].tolist()

    def explain_from_cached_explainer(self, evaluation_examples, features=None, top_k=None, **kwargs):
        """Uses the explainer from explain_model to calculate the feature importances for the evaluation data.

        :param evaluation_examples: A matrix of feature vector examples (# examples x # features) on
            which to explain the model's output.
        :type evaluation_examples: numpy.array or pandas.DataFrame or scipy.sparse.csr_matrix
        :param features: A list of feature names.
        :type features: list[str]
        :param top_k: Number of the top most important features in model summary. If specified, only the model
            summary data corresponding to the top K most important features will be returned/stored.
        :type top_k: int
        :return: tuple(run, local_importance_values, expected_values, global_importance_values,
            overall_important_features, per_class_importance_values, per_class_important_features)
            where
            - run = An object that represents an model explanation run. Only availabe if workspace
            and experiment_name are both provided.
            - local_importance_values = For a model with a single output such as regression, this returns
            a matrix of feature importance values. For models with vector outputs this function returns a
            list of such matrices, one for each output. The dimension of this matrix is (# examples x # features).
            - expected_values = The expected value of the model applied to the set of initialization examples.
            For SHAP values, when a version older than 0.20.0 is used, this value is None. The expected
            values are in the last columns of the matrices in local_importance_values. In this case, the
            dimension of those matrix is (# examples x (# features + 1)). This causes each row to sum to
            the model output for that example.
            - global_importance_values = The model level feature importance values sorted in
            descending order.
            - overall_important_features = The feature names sorted in the same order as in global_importance_values
            or the indexes that would sort global_importance_values.
            - per_class_importance_values = The class level feature importance values sorted in
            descending order where a binary classification (this class or not) is evaluated. Only available
            for the classification case.
            - per_class_important_features = The feature names sorted in the same order as in per_class_values
            or the indexes that would sort per_class_values. Only available for the classification case.
        :rtype: (azureml.core.run.Run, Union[numpy.ndarray, list[numpy.ndarray]], numpy.ndarray, numpy.ndarray,
            numpy.ndarray, numpy.ndarray, numpy.ndarray)
        """
        shap_values = self.explainer.shap_values(evaluation_examples, **kwargs)
        classification = isinstance(shap_values, list)
        if classification:
            shap_values, expected_values, global_importance_values, global_importance_names, _, \
                per_class_values, per_class_names, _ = \
                self._compute_summary(shap_values, classification, features, top_k)
            return shap_values, expected_values, global_importance_values, global_importance_names, \
                per_class_values, per_class_names
        else:
            shap_values, expected_values, global_importance_values, global_importance_names, _ = \
                self._compute_summary(shap_values, classification, features, top_k)
            return shap_values, expected_values, global_importance_values, global_importance_names
