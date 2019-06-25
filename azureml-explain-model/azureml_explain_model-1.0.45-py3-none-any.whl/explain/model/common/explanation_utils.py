# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

"""Defines helpful utilities for summarizing and uploading data."""

import os
from math import ceil
import json
import io
import pickle
import logging
import numpy as np
import scipy as sp
from scipy import sparse
from sklearn.utils import shuffle
from sklearn.utils.sparsefuncs import csc_median_axis_0
try:
    from azureml._restclient.constants import RUN_ORIGIN
except ImportError:
    print("Could not import azureml.core, required if using run history")
from azureml.explain.model._internal.constants import History, IO

try:
    from azureml._logging import ChainedIdentity
except ImportError:
    from ..common.chained_identity import ChainedIdentity

import warnings

with warnings.catch_warnings():
    warnings.filterwarnings('ignore', 'Starting from version 2.2.1', UserWarning)
    import shap
    from shap.common import DenseData


module_logger = logging.getLogger(__name__)
module_logger.setLevel(logging.INFO)


def _summarize_data(X, k=10, to_round_values=True):
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
            module_logger.debug('Creating sparse data summary as csr matrix')
            # calculate median of sparse background data
            median_dense = csc_median_axis_0(X.tocsc())
            return sp.sparse.csr_matrix(median_dense)
        elif len(X) > 10 * k:
            module_logger.debug('Create dense data summary with k-means')
            # use kmeans to summarize the examples for initialization
            # if there are more than 10 x k of them
            return shap.kmeans(X, k, to_round_values)
    return X


def _get_raw_feature_importances(importance_values, raw_feat_indices, weights=None):
    """Return raw feature importances.

    :param importance_values: importance values computed for the dataset
    :type importance_values: np.array
    :param raw_feat_indices: list of lists of generated feature indices for each raw feature
    :type raw_feat_indices: list[list]
    :param weights: list of list of weights to be applied to the generated feature importance
    :type weights: list[list]
    :return: raw feature importances
    :rtype: np.array
    """
    # sets for each list of generated features
    raw_to_gen = []
    for generated_index_list in raw_feat_indices:
        raw_to_gen.append(set(generated_index_list))

    # compute number of parents for a generated feature
    num_gen_feats = importance_values.shape[-1]
    gen_feat_num_parents = np.ones(num_gen_feats)
    for i in range(num_gen_feats):
        gen_feat_num_parents[i] = sum([1 for gen_set in raw_to_gen if i in gen_set])

    def f(x):
        raw_feat_importances = []
        try:
            for i in range(len(raw_feat_indices)):
                feature_indices = raw_feat_indices[i]
                w = 1.0 / gen_feat_num_parents[feature_indices] if weights is None else weights[i]
                raw_feat_importances.append((x[feature_indices] * w).sum())
        except IndexError:
            raise Exception("A generated feature index in {} is greater than number of generated features.".format(
                feature_indices
            ))

        return raw_feat_importances

    return np.apply_along_axis(f, -1, importance_values)


def _transform_data(data, data_mapper=None):
    """Use mapper or transformer to convert raw data to engineered before explanation.

    :param data: The raw data to transform.
    :type data: numpy, pandas, dense, sparse data matrix
    :param data_mapper: A list of lists of generated feature indices for each raw feature.
    :type data_mapper: list[list[]]
    :return: The transformed data.
    :rtype: numpy, pandas, dense, sparse data matrix
    """
    if data_mapper is not None:
        return data_mapper.transform(data)
    return data


def _get_dense_examples(examples):
    if sp.sparse.issparse(examples):
        module_logger.debug('converting sparse examples to regular array')
        return examples.toarray()
    return examples


def _convert_to_list(shap_values):
    module_logger.debug('converting numpy array of list of numpy array to list')
    classification = isinstance(shap_values, list)
    if classification:
        # shap_values is a list of ndarrays
        shap_values_numpy_free = []
        for array in shap_values:
            shap_values_numpy_free.append(array.tolist())
        return shap_values_numpy_free
    else:
        # shap_values is a single ndarray
        return shap_values.tolist()


def _generate_augmented_data(x, max_num_of_augmentations=np.inf):
    """Augment x by appending x with itself shuffled columnwise many times.

    :param x: data that has to be augmented
    :type x: nd array or sparse matrix of 2 dimensions
    :param max_augment_data_size: number of times we stack permuted x to augment.
    :type max_augment_data_size: int
    :return: augmented data with roughly number of rows that are equal to number of columns
    :rtype ndarray or sparse matrix
    """
    x_augmented = x
    vstack = sparse.vstack if sparse.issparse(x) else np.vstack
    for i in range(min(x.shape[1] // x.shape[0] - 1, max_num_of_augmentations)):
        x_permuted = shuffle(x.T, random_state=i).T
        x_augmented = vstack([x_augmented, x_permuted])

    return x_augmented


def _scale_tree_shap(shap_values, expected_values, prediction):
    """Scale the log odds shap values from TreeExplainer to be in terms of probability.

    Note this is just an approximation, since the logistic function is non-linear.
    The function is a modified version of the implementations posted on shap github issues:
    https://github.com/slundberg/shap/issues/29#issuecomment-374928027
    https://github.com/slundberg/shap/issues/29#issuecomment-408385378

    :param shap_values: The shap values to transform from log odds to probabilities.
    :type shap_values: np.array
    :param expected_values: The expected values as probabilities.
    :type expected_values: np.array
    :param prediction: The predicted probability from the teacher model.
    :type prediction: np.array
    :return: The transformed tree shap values as probabilities.
    :rtype list or ndarray
    """
    # In multiclass case, use expected values and predictions per class
    if isinstance(shap_values, list):
        values_to_convert = shap_values
        for idx, shap_values in enumerate(values_to_convert):
            values_to_convert[idx] = _scale_single_shap_matrix(shap_values, expected_values[idx], prediction[:, idx])
        return values_to_convert
    else:
        if len(prediction.shape) == 1:
            return _scale_single_shap_matrix(shap_values, expected_values, prediction)
        else:
            # Note: in binary classification with teacher probability this will be index 1,
            # but in binary classification with surrogate probability this will be index 0
            return _scale_single_shap_matrix(shap_values, expected_values, prediction[:, -1])


def _scale_single_shap_matrix(shap_values, expectation, prediction):
    """Scale a single class matrix of shap values to sum to the teacher model prediction.

    :param shap_values: The shap values of the mimic model.
    :type shap_values: np.array
    :param expected_values: The expected values as probabilities (base values).
    :type expected_values: np.array
    :param prediction: The predicted probability from the teacher model.
    :type prediction: np.array
    :return: The transformed tree shap values as probabilities.
    :rtype list or ndarray
    """
    mimic_prediction = np.sum(shap_values, axis=1)
    error = prediction - mimic_prediction - expectation
    absolute_error = np.abs(error)
    error_sign = np.sign(error)
    absolute_shap_vector = np.abs(shap_values)
    absolute_shap_magnitude = np.sum(absolute_shap_vector, axis=1)
    # We divide by one, when we know the numerator is 0
    safe_absolute_magnitude_denominator = np.where(absolute_shap_magnitude > 0., absolute_shap_magnitude, 1)
    flat_magnitude = np.multiply(np.maximum(absolute_error - absolute_shap_magnitude, 0.), error_sign)
    feature_dimension = shap_values.shape[1]
    proportional_correction = np.divide(
        np.multiply(
            np.multiply(
                error_sign,
                np.minimum(absolute_error, absolute_shap_magnitude))[:, None],
            absolute_shap_vector),
        safe_absolute_magnitude_denominator[:, None])
    flat_correction = np.full(shap_values.shape, np.divide(flat_magnitude[:, None], feature_dimension))
    return shap_values + proportional_correction + flat_correction


def _convert_single_instance_to_multi(instance_shap_values):
    """Convert a single shap values instance to multi-instance form.

    :param instance_shap_values: The shap values calculated for a new instance.
    :type instance_shap_values: np.array or list
    :return: The instance converted to multi-instance form.
    :rtype np.array or list
    """
    classification = isinstance(instance_shap_values, list)
    if classification:
        shap_values = instance_shap_values
        for i in range(len(shap_values)):
            shap_values[i] = shap_values[i].reshape(1, -1)
    else:
        shap_values = instance_shap_values
    return shap_values


def _append_shap_values_instance(shap_values, instance_shap_values):
    """Append a single instance of shap values to an existing multi-instance shap values list or array.

    :param shap_values: The existing shap values array or list.
    :type shap_values: np.array or list
    :param instance_shap_values: The shap values calculated for a new instance.
    :type instance_shap_values: np.array or list
    :return: The instance appended to the existing shap values.
    :rtype np.array or list
    """
    classification = isinstance(instance_shap_values, list)
    if classification:
        for i in range(len(shap_values)):
            cols_dim = len(instance_shap_values[i].shape)
            # col_dim can only be 1 or 2 here, depending on data passed to shap
            if cols_dim != 2:
                output_size = shap_values[i].shape[-1]
                tmp_shap_values_2d = instance_shap_values[i].reshape(1, output_size)
            else:
                tmp_shap_values_2d = instance_shap_values[i]
            # Append rows
            shap_values[i] = np.append(shap_values[i], tmp_shap_values_2d, axis=0)
    else:
        shap_values = np.append(shap_values, instance_shap_values, axis=0)
    return shap_values


def _sort_values(values, order):
    return np.array(values)[order]


def _unsort_1d(values, order):
    """Unsort a sorted 1d array based on the order that was used to sort it.

    :param values: The array that has been sorted.
    :type values: numpy.array
    :param order: The order list that was originally used to sort values.
    :type order: numpy.array
    :return: The unsorted array.
    :rtype: numpy.array
    """
    order_inverse = [None] * len(order)
    for i in range(len(order)):
        order_inverse[order[i]] = i
    return np.array(values)[order_inverse]


def _unsort_2d(values, order):
    """Unsort a sorted 2d array based on the order that was used to sort it.

    :param values: The array that has been sorted.
    :type values: numpy.array
    :param order: The order list that was originally used to sort values.
    :type order: numpy.ndarray
    :return: The unsorted array.
    :rtype: numpy.array
    """
    return np.array([_unsort_1d(values[i], order[i]).tolist() for i in range(len(order))])


def _order_imp(summary):
    """Compute the ranking of feature importance values.

    :param summary: A 3D array of the feature importance values to be ranked.
    :type summary: numpy.ndarray
    :return: The rank of the feature importance values.
    :rtype: numpy.ndarray
    """
    return summary.argsort()[..., ::-1]


# sorts a single dimensional feature list according to order
def _sort_feature_list_single(features, order):
    return list(map(lambda x: features[x], order))


# returns a list of lists, where each internal list is the feature list sorted according to the order of a single class
def _sort_feature_list_multiclass(features, order):
    return [list(map(lambda x: features[x], order_i)) for order_i in order]


# do the equivalent of a numpy array slice on a two-dimensional list
def _two_dimensional_slice(lst, end_index):
    return list(map(lambda x: x[:end_index], lst))


class ArtifactUploader(ChainedIdentity):
    """A class for uploading explanation data to run history."""

    def __init__(self, run, max_num_blocks=None, block_size=None, **kwargs):
        """Initialize the upload mixin by setting up the storage policy."""
        self.storage_policy = {History.MAX_NUM_BLOCKS: 3, History.BLOCK_SIZE: 100}
        self._update_storage_policy(max_num_blocks, block_size)
        super(ArtifactUploader, self).__init__(**kwargs)
        self._logger.debug('Initializing ArtifactUploader')
        self.run = run

    def _update_storage_policy(self, max_num_blocks, block_size):
        if max_num_blocks is not None:
            self.storage_policy[History.MAX_NUM_BLOCKS] = max_num_blocks
        if block_size is not None:
            self.storage_policy[History.BLOCK_SIZE] = block_size

    def _create_upload_dir(self, explanation_id):
        self._logger.debug('Creating upload directory')
        # create the outputs folder
        upload_dir = './explanation/{}/'.format(explanation_id)
        os.makedirs(upload_dir, exist_ok=True)
        return upload_dir

    def _upload_artifact(self, upload_dir, artifact_name, values, upload_type=None):
        self._logger.debug('Uploading artifact')
        try:
            if upload_type is None or upload_type == IO.JSON:
                json_string = json.dumps(values)
                stream = io.BytesIO(json_string.encode(IO.UTF8))
                self.run.upload_file('{}{}.{}'.format(upload_dir.lstrip('./'), artifact_name, IO.JSON), stream)
            else:
                pickle_string = pickle.dumps(values)
                stream = io.BytesIO(pickle_string)
                self.run.upload_file('{}{}.{}'.format(upload_dir.lstrip('./'), artifact_name, IO.PICKLE), stream)
        except ValueError as exp:
            self._logger.error('Cannot serialize numpy arrays as JSON')

    def _get_num_of_blocks(self, num_of_columns):
        block_size = self.storage_policy[History.BLOCK_SIZE]
        num_blocks = ceil(num_of_columns / block_size)
        max_num_blocks = self.storage_policy[History.MAX_NUM_BLOCKS]
        if num_blocks > max_num_blocks:
            num_blocks = max_num_blocks
        return num_blocks

    def _get_model_summary_artifacts(self, upload_dir, name, summary):
        self._logger.debug('Uploading model summary')
        num_columns = summary.shape[len(summary.shape) - 1]
        num_blocks = self._get_num_of_blocks(num_columns)
        block_size = self.storage_policy[History.BLOCK_SIZE]
        storage_metadata = {
            History.NAME: name,
            History.MAX_NUM_BLOCKS: self.storage_policy[History.MAX_NUM_BLOCKS],
            History.BLOCK_SIZE: self.storage_policy[History.BLOCK_SIZE],
            History.NUM_FEATURES: num_columns,
            History.NUM_BLOCKS: num_blocks
        }
        artifacts = [{} for _ in range(num_blocks)]
        # Chunk the summary and save it to Artifact
        start = 0
        for idx in range(num_blocks):
            if idx == num_blocks - 1:
                # on last iteration, grab everything that's left for the last block
                cols = slice(start, num_columns)
            else:
                cols = slice(start, start + block_size)
            block = summary[..., cols]
            block_name = '{}/{}'.format(name, idx)
            self._logger.debug('Uploading artifact for block: {}'.format(block_name))
            self._upload_artifact(upload_dir, block_name, block.tolist())
            artifacts[idx][History.PREFIX] = os.path.normpath('{}/{}/{}/{}'.format(RUN_ORIGIN,
                                                                                   self.run.id,
                                                                                   upload_dir,
                                                                                   block_name))
            start += block_size
        return artifacts, storage_metadata

    def upload_single_artifact_list(self, summary_object, artifact_tuple_list, explanation_id):
        """Upload data to individual run history artifacts from a list.

        :param summary_object: The object which aggregates metadata about the uploaded artifacts
        :type summary_object: ModelSummary
        :param artifact_tuple_list: A list with names, values, optional metadata and
            serialization format for each data type.  The serialization format can be
            json or pickle.
        :type artifact_tuple_list: (str, list, dict or None, str)
        :param explanation_id: The explanation ID the artifacts should be uploaded under
        :type explanation_id: str
        """
        upload_dir = self._create_upload_dir(explanation_id)
        for name, values, optional_metadata, upload_type in artifact_tuple_list:
            self._logger.debug('Uploading single {} artifact'.format(name))
            self._upload_artifact(upload_dir, name, values, upload_type)
            artifact_info = [{
                History.PREFIX: os.path.normpath('{}/{}/{}/{}'.format(RUN_ORIGIN,
                                                                      self.run.id,
                                                                      upload_dir,
                                                                      name))
            }]
            metadata_info = {History.NAME: name}
            if optional_metadata is not None:
                metadata_info.update(optional_metadata)
            summary_object.add_from_get_model_summary(name, (artifact_info, metadata_info))

    def upload_sharded_artifact_list(self, summary_object, artifact_tuple_list, explanation_id):
        """Upload data to sharded run history artifacts from a list.

        :param summary_object: The object which aggregates metadata about the uploaded artifacts
        :type summary_object: ModelSummary
        :param artifact_tuple_list: A list with names, and values for each data type
        :type artifact_tuple_list: (str, list)
        :param explanation_id: The explanation ID the artifacts should be uploaded under
        :type explanation_id: str
        """
        upload_dir = self._create_upload_dir(explanation_id)
        for name, values in artifact_tuple_list:
            self._logger.debug('Uploaded sharded {} artifacts'.format(name))
            artifacts = self._get_model_summary_artifacts(upload_dir, name, values)
            summary_object.add_from_get_model_summary(name, artifacts)
