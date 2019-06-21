#!/usr/bin/env python
# vim: set fileencoding=utf-8 :

import numpy as np
import bob.bio.video

import itertools


def convert_frame_cont_to_array(frame_container):
    """
    This function converts a single Frame Container into an array of features.
    The rows are samples, the columns are features.

    **Parameters:**

    ``frame_container`` : object
        A Frame Container conteining the features of an individual,
        see ``bob.bio.video.utils.FrameContainer``.

    **Returns:**

    ``features_array`` : 2D :py:class:`numpy.ndarray`
        An array containing features for all frames.
        The rows are samples, the columns are features.
    """
    return frame_container.as_array()


def convert_and_prepare_features(features, dtype='float64'):
    """
    This function converts a list or a frame container of features into a 2D array of features.
    If the input is a list of frame containers, features from different frame containers (individuals)
    are concatenated into the same list. This list is then converted to an array. The rows are samples,
    the columns are features.

    **Parameters:**

    ``features`` : [2D :py:class:`numpy.ndarray`] or [FrameContainer]
        A list or 2D feature arrays or a list of Frame Containers, see ``bob.bio.video.utils.FrameContainer``.
        Each frame Container contains feature vectors for the particular individual/person.

    **Returns:**

    ``features_array`` : 2D :py:class:`numpy.ndarray`
        An array containing features for all samples and frames.
    """

    if isinstance(
            features[0],
            bob.bio.video.FrameContainer):  # if FrameContainer convert to 2D numpy array
        features = convert_list_of_frame_cont_to_array(features)
    elif not isinstance(features, np.ndarray):
        features = np.vstack(features)

    if dtype is not None:
        features = features.astype(dtype)

    return features


def convert_list_of_frame_cont_to_array(frame_containers):
    """
    This function converts a list of Frame containers into an array of features.
    Features from different frame containers (individuals) are concatenated into the
    same list. This list is then converted to an array. The rows are samples,
    the columns are features.

    **Parameters:**

    ``frame_containers`` : [FrameContainer]
        A list of Frame Containers, , see ``bob.bio.video.utils.FrameContainer``.
        Each frame Container contains feature vectors for the particular individual/person.

    **Returns:**

    ``features_array`` : 2D :py:class:`numpy.ndarray`
        An array containing features for all frames of all individuals.
    """


    if isinstance( frame_containers[0], bob.bio.video.FrameContainer):

      feature_vectors = []
      for frame_container in frame_containers:
          video_features_array = convert_frame_cont_to_array(
            frame_container)
          feature_vectors.append(video_features_array)
    else:
      feature_vectors = frame_containers

    features_array = np.vstack(feature_vectors)

    return features_array


def combinations(input_dict):
    """
    Obtain all possible key-value combinations in the input dictionary
    containing list values.

    **Parameters:**

    ``input_dict`` : :py:class:`dict`
        Input dictionary with list values.

    **Returns:**

    ``combinations`` : [:py:class:`dict`]
        A list of dictionaries containing the combinations.
    """

    varNames = sorted(input_dict)

    combinations = [
        dict(zip(varNames, prod))
        for prod in itertools.product(*(input_dict[varName]
                                        for varName in varNames))
        ]

    return combinations


def select_uniform_data_subset(features, n_samples):
    """
    Uniformly select N samples/feature vectors from the input array of samples.
    The rows in the input array are samples. The columns are features.

    **Parameters:**

    ``features`` : 2D :py:class:`numpy.ndarray`
        Input array with feature vectors. The rows are samples, columns are features.

    ``n_samples`` : :py:class:`int`
        The number of samples to be selected uniformly from the input array of features.

    **Returns:**

    ``features_subset`` : 2D :py:class:`numpy.ndarray`
        Selected subset of features.
    """

    if features.shape[0] <= n_samples:

        features_subset = features

    else:

        uniform_step = np.int(features.shape[0] / n_samples)

        features_subset = features[0:np.int(uniform_step * n_samples):
        uniform_step, :]

    return features_subset


def select_quasi_uniform_data_subset(features, n_samples):
    """
    Select quasi uniformly N samples/feature vectors from the input array of samples.
    The rows in the input array are samples. The columns are features.
    Use this function if n_samples is close to the number of samples.

    **Parameters:**

    ``features`` : 2D :py:class:`numpy.ndarray`
        Input array with feature vectors. The rows are samples, columns are features.

    ``n_samples`` : :py:class:`int`
        The number of samples to be selected uniformly from the input array of features.

    **Returns:**

    ``features_subset`` : 2D :py:class:`numpy.ndarray`
        Selected subset of features.
    """

    if features.shape[0] <= n_samples:

        features_subset = features

    else:

        uniform_step = (1.0 * features.shape[0]) / n_samples

        element_num_list = range(0, n_samples)

        idx = [np.int(uniform_step * item) for item in element_num_list]

        features_subset = features[idx, :]

    return features_subset


def convert_array_to_list_of_frame_cont(data):
    """
    Convert an input 2D array to a list of FrameContainers.

    **Parameters:**

    ``data`` : 2D :py:class:`numpy.ndarray`
        Input data array of the dimensionality (N_samples X N_features ).

        **Returns:**

    ``frame_container_list`` : [FrameContainer]
        A list of FrameContainers, see ``bob.bio.video.utils.FrameContainer``
        for further details. Each frame container contains one feature vector.
    """

    frame_container_list = []

    for idx, vec in enumerate(data):
        frame_container = bob.bio.video.FrameContainer(
        )  # initialize the FrameContainer

        frame_container.add(0, vec)

        frame_container_list.append(
            frame_container)  # add current frame to FrameContainer

    return frame_container_list


def mean_std_normalize(features,
                       features_mean=None,
                       features_std=None,
                       copy=True,
                       ):
    """
    The features in the input 2D array are mean-std normalized.
    The rows are samples, the columns are features. If ``features_mean``
    and ``features_std`` are provided, then these vectors will be used for
    normalization. Otherwise, the mean and std of the features is
    computed on the fly.

    **Parameters:**

    ``features`` : 2D :py:class:`numpy.ndarray`
        Array of features to be normalized.

    ``features_mean`` : 1D :py:class:`numpy.ndarray`
        Mean of the features. Default: None.

    ``features_std`` : 2D :py:class:`numpy.ndarray`
        Standart deviation of the features. Default: None.

    **Returns:**

    ``features_norm`` : 2D :py:class:`numpy.ndarray`
        Normalized array of features.

    ``features_mean`` : 1D :py:class:`numpy.ndarray`
        Mean of the features.

    ``features_std`` : 1D :py:class:`numpy.ndarray`
        Standart deviation of the features.
    """

    if copy:
        features = np.copy(features)
    else:
        features = np.asarray(features)

    # Compute mean and std if not given:
    if features_mean is None:
        features_mean = np.mean(features, axis=0)

        features_std = np.std(features, axis=0)

    features_std[features_std == 0.0] = 1.0

    features_norm = (features - features_mean) / features_std

    return features_norm, features_mean, features_std


def norm_train_data(real, attack):
    """
    Mean-std normalization of input data arrays. The mean and std normalizers
    are computed using real class only.

    **Parameters:**

    ``real`` : 2D :py:class:`numpy.ndarray`
        Training features for the real class.

    ``attack`` : 2D :py:class:`numpy.ndarray`
        Training features for the attack class.

    **Returns:**

    ``real_norm`` : 2D :py:class:`numpy.ndarray`
        Mean-std normalized training features for the real class.

    ``attack_norm`` : 2D :py:class:`numpy.ndarray`
        Mean-std normalized training features for the attack class.
        Or an empty list if ``one_class_flag = True``.

    ``features_mean`` : 1D :py:class:`numpy.ndarray`
        Mean of the features.

    ``features_std`` : 1D :py:class:`numpy.ndarray`
        Standart deviation of the features.
    """

    real_norm, features_mean, features_std = mean_std_normalize(real)

    attack_norm, _, _ = mean_std_normalize(attack, features_mean,
                                           features_std)

    return real_norm, attack_norm, features_mean, features_std


def split_data_to_train_cv(features):
    """
    This function is designed to split the input array of features into two
    subset namely train and cross-validation. These subsets can be used to tune the
    hyper-parameters of the SVM. The splitting is 50/50, the first half of the
    samples in the input are selected to be train set, and the second half of
    samples is cross-validation.

    **Parameters:**

    ``features`` : 2D :py:class:`numpy.ndarray`
        Input array with feature vectors. The rows are samples, columns are features.

    **Returns:**

    ``features_train`` : 2D :py:class:`numpy.ndarray`
        Selected subset of train features.

    ``features_cv`` : 2D :py:class:`numpy.ndarray`
        Selected subset of cross-validation features.
    """

    half_samples_num = np.int(features.shape[0] / 2)

    features_train = features[0:half_samples_num, :]
    features_cv = features[half_samples_num:2 * half_samples_num + 1, :]

    return features_train, features_cv


def norm_train_cv_data(real_train,
                       real_cv,
                       attack_train,
                       attack_cv,
                       one_class_flag=False):
    """
    Mean-std normalization of train and cross-validation data arrays.

    **Parameters:**

    ``real_train`` : 2D :py:class:`numpy.ndarray`
        Subset of train features for the real class.

    ``real_cv`` : 2D :py:class:`numpy.ndarray`
        Subset of cross-validation features for the real class.

    ``attack_train`` : 2D :py:class:`numpy.ndarray`
        Subset of train features for the attack class.

    ``attack_cv`` : 2D :py:class:`numpy.ndarray`
        Subset of cross-validation features for the attack class.

    ``one_class_flag`` : :py:class:`bool`
        If set to ``True``, only positive/real samples will be used to
        compute the mean and std normalization vectors. Set to ``True`` if
        using one-class SVM. Default: False.

    **Returns:**

    ``real_train_norm`` : 2D :py:class:`numpy.ndarray`
        Normalized subset of train features for the real class.

    ``real_cv_norm`` : 2D :py:class:`numpy.ndarray`
        Normalized subset of cross-validation features for the real class.

    ``attack_train_norm`` : 2D :py:class:`numpy.ndarray`
        Normalized subset of train features for the attack class.

    ``attack_cv_norm`` : 2D :py:class:`numpy.ndarray`
        Normalized subset of cross-validation features for the attack class.
    """
    if not (one_class_flag):

        features_train = np.vstack([real_train, attack_train])

        features_train_norm, features_mean, features_std = mean_std_normalize(
            features_train)

        real_train_norm = features_train_norm[0:real_train.shape[0], :]

        attack_train_norm = features_train_norm[real_train.shape[0]:, :]

        real_cv_norm, _, _ = mean_std_normalize(
            real_cv, features_mean, features_std)

        attack_cv_norm, _, _ = mean_std_normalize(
            attack_cv, features_mean, features_std)

    else:  # one-class Classifier case

        # only real class used for training in one class Classifier:
        real_train_norm, features_mean, features_std = mean_std_normalize(
            real_train)

        attack_train_norm, _, _ = mean_std_normalize(
            attack_train, features_mean, features_std)

        real_cv_norm, _, _ = mean_std_normalize(
            real_cv, features_mean, features_std)

        attack_cv_norm, _, _ = mean_std_normalize(
            attack_cv, features_mean, features_std)

    return real_train_norm, real_cv_norm, attack_train_norm, attack_cv_norm


def prepare_data_for_hyper_param_grid_search(training_features, n_samples):
    """
    This function converts a list of all training features returned by ``read_features``
    method of the extractor to the subsampled train and cross-validation arrays for both
    real and attack classes.

    **Parameters:**

    ``training_features`` : [[FrameContainer], [FrameContainer]]
        A list containing two elements: [0] - a list of Frame Containers with
        feature vectors for the real class; [1] - a list of Frame Containers with
        feature vectors for the attack class.

    ``n_samples`` : :py:class:`int`
        Number of uniformly selected feature vectors per class.

    **Returns:**

    ``real_train`` : 2D :py:class:`numpy.ndarray`
        Selected subset of train features for the real class.
        The number of samples in this set is n_samples/2, which is defined
        by split_data_to_train_cv method of this class.

    ``real_cv`` : 2D :py:class:`numpy.ndarray`
        Selected subset of cross-validation features for the real class.
        The number of samples in this set is n_samples/2, which is defined
        by split_data_to_train_cv method of this class.

    ``attack_train`` : 2D :py:class:`numpy.ndarray`
        Selected subset of train features for the attack class.
        The number of samples in this set is n_samples/2, which is defined
        by split_data_to_train_cv method of this class.

    ``attack_cv`` : 2D :py:class:`numpy.ndarray`
        Selected subset of cross-validation features for the attack class.
        The number of samples in this set is n_samples/2, which is defined
        by split_data_to_train_cv method of this class.
    """

    # training_features[0] - training features for the REAL class.
    real = convert_and_prepare_features(
        training_features[0])  # output is array
    # training_features[1] - training features for the ATTACK class.
    attack = convert_and_prepare_features(
        training_features[1])  # output is array

    # uniformly select subsets of features:
    real_subset = select_uniform_data_subset(real, n_samples)
    attack_subset = select_uniform_data_subset(attack, n_samples)

    # split the data into train and cross-validation:
    real_train, real_cv = split_data_to_train_cv(real_subset)
    attack_train, attack_cv = split_data_to_train_cv(attack_subset)

    return real_train, real_cv, attack_train, attack_cv
