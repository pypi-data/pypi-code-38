#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Fri Aug 25 09:29:02 2017

@author: Olegs Nikisins
"""

#==============================================================================
# Import what is needed here:

from bob.pad.base.algorithm import Algorithm

from bob.bio.video.utils import FrameContainer

import numpy as np

from sklearn import linear_model

import bob.io.base

from bob.pad.base.utils import convert_frame_cont_to_array, convert_list_of_frame_cont_to_array, mean_std_normalize, \
    norm_train_data


#==============================================================================
# Main body :


class LogRegr(Algorithm):
    """
    This class is designed to train Logistic Regression classifier given Frame Containers
    with features of real and attack classes. The procedure is the following:

    1. First, the input data is mean-std normalized using mean and std of the
       real class only.

    2. Second, the Logistic Regression classifier is trained on normalized
       input features.

    3. The input features are next classified using pre-trained LR machine.

    **Parameters:**

    ``C`` : :py:class:`float`
        Inverse of regularization strength in LR classifier; must be a positive.
        Like in support vector machines, smaller values specify stronger
        regularization. Default: 1.0 .

    ``frame_level_scores_flag`` : :py:class:`bool`
        Return scores for each frame individually if True. Otherwise, return a
        single score per video. Default: ``False``.

    ``subsample_train_data_flag`` : :py:class:`bool`
        Uniformly subsample the training data if ``True``. Default: ``False``.

    ``subsampling_step`` : :py:class:`int`
        Training data subsampling step, only valid is
        ``subsample_train_data_flag = True``. Default: 10 .

    ``subsample_videos_flag`` : :py:class:`bool`
        Uniformly subsample the training videos if ``True``. Default: ``False``.

    ``video_subsampling_step`` : :py:class:`int`
        Training videos subsampling step, only valid is
        ``subsample_videos_flag = True``. Default: 3 .
    """

    def __init__(self,
                 C=1,
                 frame_level_scores_flag=False,
                 subsample_train_data_flag=False,
                 subsampling_step=10,
                 subsample_videos_flag=False,
                 video_subsampling_step=3):

        Algorithm.__init__(
            self,
            C=C,
            frame_level_scores_flag=frame_level_scores_flag,
            subsample_train_data_flag=subsample_train_data_flag,
            subsampling_step=subsampling_step,
            subsample_videos_flag=subsample_videos_flag,
            video_subsampling_step=video_subsampling_step,
            performs_projection=True,
            requires_projector_training=True)

        self.C = C

        self.frame_level_scores_flag = frame_level_scores_flag

        self.subsample_train_data_flag = subsample_train_data_flag

        self.subsampling_step = subsampling_step

        self.subsample_videos_flag = subsample_videos_flag

        self.video_subsampling_step = video_subsampling_step

        self.lr_machine = None  # this argument will be updated with pretrained LR machine

        self.features_mean = None  # this argument will be updated with features mean
        self.features_std = None  # this argument will be updated with features std

        # names of the arguments of the pretrained LR machine to be saved/loaded to/from HDF5 file:
        self.lr_param_keys = ["C", "classes_", "coef_", "intercept_"]


    #==========================================================================
    def train_lr(self, real, attack, C):
        """
        Train LR classifier given real and attack classes. Prior to training
        the data is mean-std normalized.

        **Parameters:**

        ``real`` : 2D :py:class:`numpy.ndarray`
            Training features for the real class.

        ``attack`` : 2D :py:class:`numpy.ndarray`
            Training features for the attack class.

        ``C`` : :py:class:`float`
            Inverse of regularization strength in LR classifier; must be a positive.
            Like in support vector machines, smaller values specify stronger
            regularization. Default: 1.0 .

        **Returns:**

        ``machine`` : object
            A trained LR machine.

        ``features_mean`` : 1D :py:class:`numpy.ndarray`
            Mean of the features.

        ``features_std`` : 1D :py:class:`numpy.ndarray`
            Standart deviation of the features.
        """

        real, attack, features_mean, features_std = norm_train_data(
            real, attack)
        # real and attack - are now mean-std normalized

        X = np.vstack([real, attack])

        Y = np.hstack([np.zeros(len(real)), np.ones(len(attack))])

        machine = linear_model.LogisticRegression(C=C)

        machine.fit(X, Y)

        return machine, features_mean, features_std

    #==========================================================================
    def save_lr_machine_and_mean_std(self, projector_file, machine,
                                     features_mean, features_std):
        """
        Saves the LR machine, features mean and std to the hdf5 file.
        The absolute name of the file is specified in ``projector_file`` string.

        **Parameters:**

        ``projector_file`` : :py:class:`str`
            Absolute name of the file to save the data to, as returned by
            ``bob.pad.base`` framework.

        ``machine`` : object
            The LR machine to be saved. As returned by sklearn.linear_model
            module.

        ``features_mean`` : 1D :py:class:`numpy.ndarray`
            Mean of the features.

        ``features_std`` : 1D :py:class:`numpy.ndarray`
            Standart deviation of the features.
        """

        f = bob.io.base.HDF5File(projector_file,
                                 'w')  # open hdf5 file to save to

        for key in self.lr_param_keys:  # ["C", "classes_", "coef_", "intercept_"]

            data = getattr(machine, key)

            f.set(key, data)

        f.set("features_mean", features_mean)

        f.set("features_std", features_std)

        del f

    #==========================================================================
    def subsample_train_videos(self, training_features, step):
        """
        Uniformly select subset of frmae containes from the input list

        **Parameters:**

        ``training_features`` : [FrameContainer]
            A list of FrameContainers

        ``step`` : :py:class:`int`
            Data selection step.

        **Returns:**

        ``training_features_subset`` : [FrameContainer]
            A list with selected FrameContainers
        """

        indexes = range(0, len(training_features), step)

        training_features_subset = [training_features[x] for x in indexes]

        return training_features_subset

    #==========================================================================
    def train_projector(self, training_features, projector_file):
        """
        Train LR for feature projection and save them to files.
        The ``requires_projector_training = True`` flag must be set to True
        to enable this function.

        **Parameters:**

        ``training_features`` : [[FrameContainer], [FrameContainer]]
            A list containing two elements: [0] - a list of Frame Containers with
            feature vectors for the real class; [1] - a list of Frame Containers with
            feature vectors for the attack class.

        ``projector_file`` : :py:class:`str`
            The file to save the trained projector to, as returned by the
            ``bob.pad.base`` framework.
        """

        # training_features[0] - training features for the REAL class.
        # training_features[1] - training features for the ATTACK class.

        if self.subsample_videos_flag:  # subsample videos of the real class

            real = convert_list_of_frame_cont_to_array(
                self.subsample_train_videos(
                    training_features[0],
                    self.video_subsampling_step))  # output is array

        else:

            real = convert_list_of_frame_cont_to_array(
                training_features[0])  # output is array

        if self.subsample_train_data_flag:

            real = real[range(0, len(real), self.subsampling_step), :]

        if self.subsample_videos_flag:  # subsample videos of the real class

            attack = convert_list_of_frame_cont_to_array(
                self.subsample_train_videos(
                    training_features[1],
                    self.video_subsampling_step))  # output is array

        else:

            attack = convert_list_of_frame_cont_to_array(
                training_features[1])  # output is array

        if self.subsample_train_data_flag:

            attack = attack[range(0, len(attack), self.subsampling_step), :]

        # Train the LR machine and get normalizers:
        machine, features_mean, features_std = self.train_lr(
            real=real, attack=attack, C=self.C)

        # Save the LR machine and normalizers:
        self.save_lr_machine_and_mean_std(projector_file, machine,
                                          features_mean, features_std)

    #==========================================================================
    def load_lr_machine_and_mean_std(self, projector_file):
        """
        Loads the machine, features mean and std from the hdf5 file.
        The absolute name of the file is specified in ``projector_file`` string.

        **Parameters:**

        ``projector_file`` : :py:class:`str`
            Absolute name of the file to load the trained projector from, as
            returned by ``bob.pad.base`` framework.

        **Returns:**

        ``machine`` : object
            The loaded LR machine. As returned by sklearn.linear_model module.

        ``features_mean`` : 1D :py:class:`numpy.ndarray`
            Mean of the features.

        ``features_std`` : 1D :py:class:`numpy.ndarray`
            Standart deviation of the features.
        """

        f = bob.io.base.HDF5File(projector_file,
                                 'r')  # file to read the machine from

        # initialize the machine:
        machine = linear_model.LogisticRegression()

        # set the params of the machine:
        for key in self.lr_param_keys:  # ["C", "classes_", "coef_", "intercept_"]

            data = f.read(key)

            setattr(machine, key, data)

        features_mean = f.read("features_mean")

        features_std = f.read("features_std")

        del f

        return machine, features_mean, features_std

    #==========================================================================
    def load_projector(self, projector_file):
        """
        Loads the machine, features mean and std from the hdf5 file.
        The absolute name of the file is specified in ``projector_file`` string.

        This function sets the arguments ``self.lr_machine``, ``self.features_mean``
        and ``self.features_std`` of this class with loaded machines.

        The function must be capable of reading the data saved with the
        :py:meth:`train_projector` method of this class.

        Please register `performs_projection = True` in the constructor to
        enable this function.

        **Parameters:**

        ``projector_file`` : :py:class:`str`
            The file to read the projector from, as returned by the
            ``bob.pad.base`` framework. In this class the names of the files to
            read the projectors from are modified, see ``load_machine`` and
            ``load_cascade_of_machines`` methods of this class for more details.
        """

        lr_machine, features_mean, features_std = self.load_lr_machine_and_mean_std(
            projector_file)

        self.lr_machine = lr_machine

        self.features_mean = features_mean

        self.features_std = features_std

    #==========================================================================
    def project(self, feature):
        """
        This function computes a vector of scores for each sample in the input
        array of features. The following steps are apllied:

        1. First, the input data is mean-std normalized using mean and std of the
           real class only.

        2. The input features are next classified using pre-trained LR machine.

        Set ``performs_projection = True`` in the constructor to enable this function.
        It is assured that the :py:meth:`load_projector` was **called before** the
        ``project`` function is executed.

        **Parameters:**

        ``feature`` : FrameContainer or 2D :py:class:`numpy.ndarray`
            Two types of inputs are accepted.
            A Frame Container conteining the features of an individual,
            see ``bob.bio.video.utils.FrameContainer``.
            Or a 2D feature array of the size (N_samples x N_features).

        **Returns:**

        ``scores`` : 1D :py:class:`numpy.ndarray`
            Vector of scores. Scores for the real class are expected to be
            higher, than the scores of the negative / attack class.
            In this case scores are probabilities.
        """

        # 1. Convert input array to numpy array if necessary.
        if isinstance(
                feature,
                FrameContainer):  # if FrameContainer convert to 2D numpy array

            features_array = convert_frame_cont_to_array(feature)

        else:

            features_array = feature

        features_array_norm, _, _ = mean_std_normalize(
            features_array, self.features_mean, self.features_std)

        scores = self.lr_machine.predict_proba(features_array_norm)[:, 0]

        return scores

    #==========================================================================
    def score(self, toscore):
        """
        Returns a probability of a sample being a real class.

        **Parameters:**

        ``toscore`` : 1D :py:class:`numpy.ndarray`
            Vector with scores for each frame/sample defining the probability
            of the frame being a sample of the real class.

        **Returns:**

        ``score`` : [:py:class:`float`]
            If ``frame_level_scores_flag = False`` a single score is returned.
            One score per video. This score is placed into a list, because
            the ``score`` must be an iterable.
            Score is a probability of a sample being a real class.
            If ``frame_level_scores_flag = True`` a list of scores is returned.
            One score per frame/sample.
        """

        if self.frame_level_scores_flag:

            score = list(toscore)

        else:

            score = [np.mean(toscore)]  # compute a single score per video

        return score
