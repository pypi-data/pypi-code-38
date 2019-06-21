#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Wed May 17 09:43:09 2017

@author: Olegs Nikisins
"""

# ==============================================================================
# Import what is needed here:

from bob.pad.base.algorithm import Algorithm
from bob.bio.video.utils import FrameContainer

import itertools as it

import numpy as np

import bob.learn.libsvm

import bob.io.base

import os

from bob.pad.base.utils import convert_frame_cont_to_array, convert_and_prepare_features, combinations, \
    select_uniform_data_subset, select_quasi_uniform_data_subset, mean_std_normalize, split_data_to_train_cv, \
    norm_train_cv_data, prepare_data_for_hyper_param_grid_search

# ==============================================================================
# Main body :


class SVM(Algorithm):
    """
    This class is designed to train SVM given features (either numpy arrays or Frame Containers)
    from real and attack classes. The trained SVM is then used to classify the
    testing data as either real or attack. The SVM is trained in two stages.
    First, the best parameters for SVM are estimated using train and
    cross-validation subsets. The size of the subsets used in hyper-parameter
    tuning is defined by ``n_samples`` parameter of this class. Once best
    parameters are determined, the SVM machine is trained using complete training
    set.

    **Parameters:**

    ``machine_type`` : :py:class:`str`
        A type of the SVM machine. Please check ``bob.learn.libsvm`` for
        more details. Default: 'C_SVC'.

    ``kernel_type`` : :py:class:`str`
        A type of kerenel for the SVM machine. Please check ``bob.learn.libsvm``
        for more details. Default: 'RBF'.

    ``n_samples`` : :py:class:`int`
        Number of uniformly selected feature vectors per class defining the
        sizes of sub-sets used in the hyper-parameter grid search.

    ``trainer_grid_search_params`` : :py:class:`dict`
        Dictionary containing the hyper-parameters of the SVM to be tested
        in the grid-search.
        Default: {'cost': [2**p for p in range(-5, 16, 2)], 'gamma': [2**p for p in range(-15, 4, 2)]}.

    ``mean_std_norm_flag`` : :py:class:`bool`
        Perform mean-std normalization of data if set to True. Default: False.

    ``frame_level_scores_flag`` : :py:class:`bool`
        Return scores for each frame individually if True. Otherwise, return a
        single score per video. Should be used only when features are in Frame Containers. Default: False.

    ``save_debug_data_flag`` : :py:class:`bool`
        Save the data, which might be usefull for debugging if ``True``.
        Default: ``True``.

    ``reduced_train_data_flag`` : :py:class:`bool`
        Reduce the amount of final training samples if set to ``True``.
        Default: ``False``.

    ``n_train_samples`` : :py:class:`int`
        Number of uniformly selected feature vectors per class defining the
        sizes of sub-sets used in the final traing of the SVM.
        Default: 50000.
    """

    def __init__(
            self,
            machine_type='C_SVC',
            kernel_type='RBF',
            n_samples=10000,
            trainer_grid_search_params={
                'cost': [2**p for p in range(-5, 16, 2)],
                'gamma': [2**p for p in range(-15, 4, 2)]
            },
            mean_std_norm_flag=False,
            frame_level_scores_flag=False,
            save_debug_data_flag=True,
            reduced_train_data_flag=False,
            n_train_samples=50000):

        Algorithm.__init__(
            self,
            machine_type=machine_type,
            kernel_type=kernel_type,
            n_samples=n_samples,
            trainer_grid_search_params=trainer_grid_search_params,
            mean_std_norm_flag=mean_std_norm_flag,
            frame_level_scores_flag=frame_level_scores_flag,
            save_debug_data_flag=save_debug_data_flag,
            reduced_train_data_flag=reduced_train_data_flag,
            n_train_samples=n_train_samples,
            performs_projection=True,
            requires_projector_training=True)

        self.machine_type = machine_type
        self.kernel_type = kernel_type
        self.n_samples = n_samples
        self.trainer_grid_search_params = trainer_grid_search_params
        self.mean_std_norm_flag = mean_std_norm_flag
        self.frame_level_scores_flag = frame_level_scores_flag
        self.save_debug_data_flag = save_debug_data_flag
        self.reduced_train_data_flag = reduced_train_data_flag
        self.n_train_samples = n_train_samples
        self.machine = None

    # ==========================================================================
    def comp_prediction_precision(self, machine, real, attack):
        """
        This function computes the precision of the predictions as a ratio
        of correctly classified samples to the total number of samples.

        **Parameters:**

        ``machine`` : object
            A pre-trained SVM machine.

        ``real`` : 2D :py:class:`numpy.ndarray`
            Array of features representing the real class.

        ``attack`` : 2D :py:class:`numpy.ndarray`
            Array of features representing the attack class.

        **Returns:**

        ``precision`` : :py:class:`float`
            The precision of the predictions.
        """

        labels_real = machine.predict_class(real)

        labels_attack = machine.predict_class(attack)

        samples_num = len(labels_real) + len(labels_attack)

        precision = (np.sum(labels_real == 1) + np.sum(labels_attack == -1)
                     ).astype(np.float) / samples_num

        return precision

    # ==========================================================================
    def train_svm(
            self,
            training_features,
            n_samples=10000,
            machine_type='C_SVC',
            kernel_type='RBF',
            trainer_grid_search_params={
                'cost': [2**p for p in range(-5, 16, 2)],
                'gamma': [2**p for p in range(-15, 4, 2)]
            },
            mean_std_norm_flag=False,
            projector_file="",
            save_debug_data_flag=True,
            reduced_train_data_flag=False,
            n_train_samples=50000):
        """
        First, this function tunes the hyper-parameters of the SVM classifier using
        grid search on the sub-sets of training data. Train and cross-validation
        subsets for both classes are formed from the available input training_features.

        Once successfull parameters are determined the SVM is trained on the
        whole training data set. The resulting machine is returned by the function.

        **Parameters:**

        ``training_features`` : [[FrameContainer], [FrameContainer]]
            A list containing two elements: [0] - a list of Frame Containers with
            feature vectors for the real class; [1] - a list of Frame Containers with
            feature vectors for the attack class.

        ``n_samples`` : :py:class:`int`
            Number of uniformly selected feature vectors per class defining the
            sizes of sub-sets used in the hyper-parameter grid search.

        ``machine_type`` : :py:class:`str`
            A type of the SVM machine. Please check ``bob.learn.libsvm`` for
            more details.

        ``kernel_type`` : :py:class:`str`
            A type of kerenel for the SVM machine. Please check ``bob.learn.libsvm``
            for more details.

        ``trainer_grid_search_params`` : :py:class:`dict`
            Dictionary containing the hyper-parameters of the SVM to be tested
            in the grid-search.

        ``mean_std_norm_flag`` : :py:class:`bool`
            Perform mean-std normalization of data if set to True. Default: False.

        ``projector_file`` : :py:class:`str`
            The name of the file to save the trained projector to. Only the path
            of this file is used in this function. The file debug_data.hdf5 will
            be save in this path. This file contains information, which might be
            usefull for debugging.

        ``save_debug_data_flag`` : :py:class:`bool`
            Save the data, which might be usefull for debugging if ``True``.
            Default: ``True``.

        ``reduced_train_data_flag`` : :py:class:`bool`
            Reduce the amount of final training samples if set to ``True``.
            Default: ``False``.

        ``n_train_samples`` : :py:class:`int`
            Number of uniformly selected feature vectors per class defining the
            sizes of sub-sets used in the final traing of the SVM.
            Default: 50000.

        **Returns:**

        ``machine`` : object
            A trained SVM machine.
        """

        one_class_flag = (
            machine_type == 'ONE_CLASS')  # True if one-class SVM is used

        # get the data for the hyper-parameter grid-search:
        real_train, real_cv, attack_train, attack_cv = \
            prepare_data_for_hyper_param_grid_search(training_features, n_samples)

        if mean_std_norm_flag:
            # normalize the data:
            real_train, real_cv, attack_train, attack_cv = norm_train_cv_data(
                real_train, real_cv, attack_train, attack_cv, one_class_flag)

        precisions_cv = [
        ]  # for saving the precision on the cross-validation set

        precisions_train = []

        trainer_grid_search_params_list = combinations(
            trainer_grid_search_params
        )  # list containing all combinations of params

        for trainer_grid_search_param in trainer_grid_search_params_list:

            # initialize the SVM trainer:
            trainer = bob.learn.libsvm.Trainer(
                machine_type=machine_type,
                kernel_type=kernel_type,
                probability=True)

            for key in trainer_grid_search_param.keys():
                setattr(trainer, key, trainer_grid_search_param[
                    key])  # set the params of trainer

            if not (one_class_flag):  # two-class SVM case

                data = [
                    np.copy(real_train),
                    np.copy(attack_train)
                ]  # data used for training the machine in the grid-search

            else:  # one class SVM case

                data = [np.copy(real_train)
                        ]  # only real class is used for training

            machine = trainer.train(data)  # train the machine

            precision_cv = self.comp_prediction_precision(
                machine, np.copy(real_cv), np.copy(attack_cv))

            precision_train = self.comp_prediction_precision(
                machine, np.copy(real_train), np.copy(attack_train))

            precisions_cv.append(precision_cv)

            precisions_train.append(precision_train)

            del data
            del machine
            del trainer

        # best SVM parameters according to CV set
        selected_params = trainer_grid_search_params_list[np.argmax(precisions_cv)]

        trainer = bob.learn.libsvm.Trainer(
            machine_type=machine_type,
            kernel_type=kernel_type,
            probability=True)

        for key in selected_params.keys():
            setattr(trainer, key,
                    selected_params[key])  # set the params of trainer

        # Save the data, which is usefull for debugging.
        if save_debug_data_flag:

            debug_file = os.path.join(
                os.path.split(projector_file)[0], "debug_data.hdf5")
            debug_dict = {}
            debug_dict['precisions_train'] = precisions_train
            debug_dict['precisions_cv'] = precisions_cv

            for key in selected_params.keys():
                debug_dict[key] = selected_params[key]

            f = bob.io.base.HDF5File(
                debug_file, 'w')  # open hdf5 file to save the debug data
            for key in debug_dict.keys():
                f.set(key, debug_dict[key])
            del f

        # training_features[0] - training features for the REAL class.
        real = convert_and_prepare_features(
            training_features[0])  # output is array
        # training_features[1] - training features for the ATTACK class.
        attack = convert_and_prepare_features(
            training_features[1])  # output is array

        features_mean = 0.0
        features_std = 1.0
        if mean_std_norm_flag:
            # Normalize the data:
            if not (one_class_flag):  # two-class SVM case

                features = np.vstack([real, attack])
                features_norm, features_mean, features_std = mean_std_normalize(
                    features)
                real = features_norm[0:real.shape[
                    0], :]  # The array is now normalized
                attack = features_norm[real.shape[
                    0]:, :]  # The array is now normalized

            else:  # one-class SVM case

                real, features_mean, features_std = mean_std_normalize(
                    real)  # use only real class to compute normalizers
                attack = mean_std_normalize(attack, features_mean,
                                                 features_std)
                # ``real`` and ``attack`` arrays are now normalizaed

        if reduced_train_data_flag:
            # uniformly select subsets of features:
            real = select_quasi_uniform_data_subset(real, n_train_samples)
            attack = select_quasi_uniform_data_subset(
                attack, n_train_samples)

        if not (one_class_flag):  # two-class SVM case

            data = [np.copy(real), np.copy(attack)]  # data for final training

        else:  # one-class SVM case

            data = [np.copy(real)]  # only real class used for training

        # free the memory of unnecessary data
        del real
        del attack

        machine = trainer.train(data)  # train the machine

        if mean_std_norm_flag:
            machine.input_subtract = features_mean  # subtract the mean of train data
            machine.input_divide = features_std  # divide by std of train data

        del data

        return machine

    # ==========================================================================
    def train_projector(self, training_features, projector_file):
        """
        Train SVM feature projector and save the trained SVM to a given file.
        The ``requires_projector_training = True`` flag must be set to True to
        enable this function.

        **Parameters:**

        ``training_features`` : [[FrameContainer], [FrameContainer]]
            A list containing two elements: [0] - a list of Frame Containers with
            feature vectors for the real class; [1] - a list of Frame Containers with
            feature vectors for the attack class.

        ``projector_file`` : :py:class:`str`
            The file to save the trained projector to.
            This file should be readable with the :py:meth:`load_projector` function.
        """

        machine = self.train_svm(
            training_features=training_features,
            n_samples=self.n_samples,
            machine_type=self.machine_type,
            kernel_type=self.kernel_type,
            trainer_grid_search_params=self.trainer_grid_search_params,
            mean_std_norm_flag=self.mean_std_norm_flag,
            projector_file=projector_file,
            save_debug_data_flag=self.save_debug_data_flag,
            reduced_train_data_flag=self.reduced_train_data_flag,
            n_train_samples=self.n_train_samples)

        f = bob.io.base.HDF5File(projector_file,
                                 'w')  # open hdf5 file to save to

        machine.save(f)  # save the machine and normalization parameters

        del f

    # ==========================================================================
    def load_projector(self, projector_file):
        """
        Load the pretrained projector/SVM from file to perform a feature projection.
        This function usually is useful in combination with the
        :py:meth:`train_projector` function.

        Please register `performs_projection = True` in the constructor to
        enable this function.

        **Parameters:**

        ``projector_file`` : :py:class:`str`
            The file to read the projector from.
        """

        f = bob.io.base.HDF5File(projector_file, 'r')

        self.machine = bob.learn.libsvm.Machine(f)

        del f

    # ==========================================================================
    def project(self, feature):
        """
        This function computes class probabilities for the input feature using pretrained SVM.
        The feature in this case is a Frame Container with features for each frame.
        The probabilities will be computed and returned for each frame.

        Set ``performs_projection = True`` in the constructor to enable this function.
        It is assured that the :py:meth:`load_projector` was called before the
        ``project`` function is executed.

        **Parameters:**

        ``feature`` : object
            A Frame Container conteining the features of an individual,
            see ``bob.bio.video.utils.FrameContainer``.

        **Returns:**

        ``probabilities`` : 1D or 2D :py:class:`numpy.ndarray`
            2D in the case of two-class SVM.
            An array containing class probabilities for each frame.
            First column contains probabilities for each frame being a real class.
            Second column contains probabilities for each frame being an attack class.
            1D in the case of one-class SVM.
            Vector with scores for each frame defining belonging to the real class.
            Must be writable with the ``write_feature`` function and
            readable with the ``read_feature`` function.
        """
        if isinstance(
                feature,
                FrameContainer):  # if FrameContainer convert to 2D numpy array

            features_array = convert_frame_cont_to_array(feature)

        else:

            features_array = feature

        features_array = features_array.astype('float64')

        if not (self.machine_type == 'ONE_CLASS'):  # two-class SVM case

            probabilities = self.machine.predict_class_and_probabilities(
                features_array)[1]

        else:

            probabilities = self.machine.predict_class_and_scores(
                features_array)[1]

        return probabilities

    # ==========================================================================
    def score(self, toscore):
        """
        Returns a probability of a sample being a real class.

        **Parameters:**

        ``toscore`` : 1D or 2D :py:class:`numpy.ndarray`
            2D in the case of two-class SVM.
            An array containing class probabilities for each frame.
            First column contains probabilities for each frame being a real class.
            Second column contains probabilities for each frame being an attack class.
            1D in the case of one-class SVM.
            Vector with scores for each frame defining belonging to the real class.

        **Returns:**

        ``score`` : :py:class:`float` or a 1D :py:class:`numpy.ndarray`
            If ``frame_level_scores_flag = False`` a single score is returned.
            One score per video.
            Score is a probability of a sample being a real class.
            If ``frame_level_scores_flag = True`` a 1D array of scores is returned.
            One score per frame.
            Score is a probability of a sample being a real class.
        """

        if toscore.ndim == 1:
          return [toscore[0]]

        if self.frame_level_scores_flag:

            score = toscore[:,
                            0]  # here score is a 1D array containing scores for each frame

        else:

            score = np.mean(toscore[:, 0])  # compute a single score per sample

        return score

    # ==========================================================================
    def score_for_multiple_projections(self, toscore):
        """
        Returns a list of scores computed by the score method of this class.

        **Parameters:**

        ``toscore`` : 1D or 2D :py:class:`numpy.ndarray`
            2D in the case of two-class SVM.
            An array containing class probabilities for each frame.
            First column contains probabilities for each frame being a real class.
            Second column contains probabilities for each frame being an attack class.
            1D in the case of one-class SVM.
            Vector with scores for each frame defining belonging to the real class.

        **Returns:**

        ``list_of_scores`` : [:py:class:`float`]
            A list containing the scores.
        """

        scores = self.score(
            toscore)  # returns float score or 1D array of scores

        if isinstance(scores, np.float):  # if a single score

            list_of_scores = [scores]

        else:

            list_of_scores = list(scores)

        return list_of_scores
