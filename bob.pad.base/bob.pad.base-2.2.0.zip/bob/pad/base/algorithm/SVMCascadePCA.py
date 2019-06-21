#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Wed May 17 09:43:09 2017

@author: Olegs Nikisins
"""

#==============================================================================
# Import what is needed here:

from bob.pad.base.algorithm import Algorithm

import numpy as np

import bob.learn.libsvm

import bob.learn.linear

import bob.io.base

import os

import fnmatch

from bob.bio.video.utils import FrameContainer

from bob.pad.base.utils import convert_frame_cont_to_array, mean_std_normalize

#==============================================================================
# Main body :

class SVMCascadePCA(Algorithm):
    """
    This class is designed to train the **cascede** of SVMs given Frame Containers
    with features of real and attack classes. The procedure is the following:

    1. First, the input data is mean-std normalized.

    2. Second, the PCA is trained on normalized input features. Only the
       features of the **real** class are used in PCA training, both
       for one-class and two-class SVMs.

    3. The features are next projected given trained PCA machine.

    4. Prior to SVM training the features are again mean-std normalized.

    5. Next SVM machine is trained for each N projected features. First, preojected
       features corresponding to highest eigenvalues are selected. N is usually small
       N = (2, 3). So, if N = 2, the first SVM is trained for projected features 1 and 2,
       second SVM is trained for projected features 3 and 4, and so on.

    6. These SVMs then form a cascade of classifiers. The input feature vector is then
       projected using PCA machine and passed through all classifiers in the cascade.
       The decision is then made by majority voting.

    Both one-class SVM and two-class SVM cascades can be trained.
    In this implementation the grid search of SVM parameters is not supported.

    **Parameters:**

    ``machine_type`` : :py:class:`str`
        A type of the SVM machine. Please check ``bob.learn.libsvm`` for
        more details. Default: 'C_SVC'.

    ``kernel_type`` : :py:class:`str`
        A type of kerenel for the SVM machine. Please check ``bob.learn.libsvm``
        for more details. Default: 'RBF'.

    ``svm_kwargs`` : :py:class:`dict`
        Dictionary containing the hyper-parameters of the SVM.
        Default: {'cost': 1, 'gamma': 0}.

    ``N`` : :py:class:`int`
        The number of features to be used for training a single SVM machine
        in the cascade. Default: 2.

    ``pos_scores_slope`` : :py:class:`float`
        The positive scores returned by SVM cascade will be multiplied by this
        constant prior to majority voting. Default: 0.01 .

    ``frame_level_scores_flag`` : :py:class:`bool`
        Return scores for each frame individually if True. Otherwise, return a
        single score per video. Default: False.
    """

    def __init__(self,
                 machine_type = 'C_SVC',
                 kernel_type = 'RBF',
                 svm_kwargs = {'cost': 1, 'gamma': 0},
                 N = 2,
                 pos_scores_slope = 0.01,
                 frame_level_scores_flag = False):


        Algorithm.__init__(self,
                           machine_type = machine_type,
                           kernel_type = kernel_type,
                           svm_kwargs = svm_kwargs,
                           N = N,
                           pos_scores_slope = pos_scores_slope,
                           frame_level_scores_flag = frame_level_scores_flag,
                           performs_projection=True,
                           requires_projector_training=True)

        self.machine_type = machine_type
        self.kernel_type = kernel_type
        self.svm_kwargs = svm_kwargs
        self.N = N
        self.pos_scores_slope = pos_scores_slope
        self.frame_level_scores_flag = frame_level_scores_flag

        self.pca_projector_file_name = "pca_projector" # pca machine will be saved to .hdf5 file with this name
        self.svm_projector_file_name = "svm_projector" # svm machines will be saved to .hdf5 files with this name augumented by machine number

        self.pca_machine = None
        self.svm_machines = None


    #==========================================================================
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

        precision = ( np.sum(labels_real == 1) + np.sum(labels_attack == -1) ).astype( np.float ) / samples_num

        return precision


    #==========================================================================
    def train_pca(self, data):
        """
        Train PCA given input array of feature vectors. The data is mean-std
        normalized prior to PCA training.

        **Parameters:**

        ``data`` : 2D :py:class:`numpy.ndarray`
            Array of feature vectors of the size (N_samples x N_features).
            The features must be already mean-std normalized.

        **Returns:**

        ``machine`` : :py:class:`bob.learn.linear.Machine`
            The PCA machine that has been trained. The mean-std normalizers are
            also set in the machine.

        ``eig_vals`` : 1D :py:class:`numpy.ndarray`
            The eigen-values of the PCA projection.
        """

        # 1. Normalize the training data:
        data_norm, features_mean, features_std = mean_std_normalize(data)

        trainer = bob.learn.linear.PCATrainer() # Creates a PCA trainer

        [machine, eig_vals] = trainer.train(data_norm)  # Trains the machine with the given data

        # Set the normalizers for the PCA machine, needed to normalize the test samples.
        machine.input_subtract = features_mean # subtract the mean of train data
        machine.input_divide   = features_std  # divide by std of train data

        return machine, eig_vals


    #==========================================================================
    def train_svm(self, real, attack, machine_type, kernel_type, svm_kwargs):
        """
        One-class or two class-SVM is trained in this method given input features.
        The value of ``attack`` argument is not important in the case of one-class SVM.
        Prior to training the data is mean-std normalized.

        **Parameters:**

        ``real`` : 2D :py:class:`numpy.ndarray`
            Training features for the real class.

        ``attack`` : 2D :py:class:`numpy.ndarray`
            Training features for the attack class. If machine_type == 'ONE_CLASS'
            this argument can be anything, it will be skipped.

        ``machine_type`` : :py:class:`str`
            A type of the SVM machine. Please check ``bob.learn.libsvm`` for
            more details.

        ``kernel_type`` : :py:class:`str`
            A type of kerenel for the SVM machine. Please check ``bob.learn.libsvm``
            for more details.

        ``svm_kwargs`` : :py:class:`dict`
            Dictionary containing the hyper-parameters of the SVM.

        **Returns:**

        ``machine`` : object
            A trained SVM machine. The mean-std normalizers are also set in the
            machine.
        """

        one_class_flag = (machine_type == 'ONE_CLASS') # True if one-class SVM is used

        # Mean-std normalize the data before training
        real, attack, features_mean, features_std = self.norm_train_data(real, attack, one_class_flag)
        # real and attack - are now mean-std normalized

        trainer = bob.learn.libsvm.Trainer(machine_type = machine_type,
                                           kernel_type = kernel_type,
                                           probability = True)

        for key in svm_kwargs.keys():

            setattr(trainer, key, svm_kwargs[key]) # set the hyper-parameters of the SVM

        if not( one_class_flag ): # two-class SVM case

            data = [real, attack] # data for final training

        else: # one-class SVM case

            data = [real] # only real class used for training

        machine = trainer.train(data) # train the machine

        # add the normalizers to the trained SVM machine
        machine.input_subtract = features_mean # subtract the mean of train data
        machine.input_divide   = features_std  # divide by std of train data

        return machine


    #==========================================================================
    def get_data_start_end_idx(self, data, N):
        """
        Get indexes to select the subsets of data related to the cascades.
        First (n_machines - 1) SVMs will be trained using N features.
        Last SVM will be trained using remaining features, which is less or
        equal to N.

        **Parameters:**

        ``data`` : 2D :py:class:`numpy.ndarray`
            Data array containing the training features. The dimensionality is
            (N_samples x N_features).

        ``N`` : :py:class:`int`
            Number of features per single SVM.

        **Returns:**

        ``idx_start`` : [int]
            Starting indexes for data subsets.

        ``idx_end`` : [int]
            End indexes for data subsets.

        ``n_machines`` : :py:class:`int`
            Number of SVMs to be trained.
        """

        n_features = data.shape[1]

        n_machines = np.int(n_features/N)

        if (n_features - n_machines*N) > 1: # if more than one feature remains

            machines_num = range(0, n_machines, 1)

            idx_start = [item*N for item in machines_num]

            idx_end = [(item+1)*N for item in machines_num]

            idx_start.append( n_machines*N )

            idx_end.append( n_features )

            n_machines = n_machines + 1

        else:

            machines_num = range(0, n_machines, 1)

            idx_start = [item*N for item in machines_num]

            idx_end = [(item+1)*N for item in machines_num]

        return idx_start, idx_end, n_machines


    #==========================================================================
    def train_svm_cascade(self, real, attack, machine_type, kernel_type, svm_kwargs, N):
        """
        Train a cascade of SVMs, one SVM machine per N features. N is usually small
        N = (2, 3). So, if N = 2, the first SVM is trained for features 1 and 2,
        second SVM is trained for features 3 and 4, and so on.

        Both one-class and two-class SVM cascades can be trained. The value of
        ``attack`` argument is not important in the case of one-class SVM.

        The data is mean-std normalized prior to SVM cascade training.

        **Parameters:**

        ``real`` : 2D :py:class:`numpy.ndarray`
            Training features for the real class.

        ``attack`` : 2D :py:class:`numpy.ndarray`
            Training features for the attack class. If machine_type == 'ONE_CLASS'
            this argument can be anything, it will be skipped.

        ``machine_type`` : :py:class:`str`
            A type of the SVM machine. Please check ``bob.learn.libsvm`` for
            more details.

        ``kernel_type`` : :py:class:`str`
            A type of kerenel for the SVM machine. Please check ``bob.learn.libsvm``
            for more details.

        ``svm_kwargs`` : :py:class:`dict`
            Dictionary containing the hyper-parameters of the SVM.

        ``N`` : :py:class:`int`
            The number of features to be used for training a single SVM machine
            in the cascade.

        **Returns:**

        ``machines`` : :py:class:`dict`
            A dictionary containing a cascade of trained SVM machines.
        """

        one_class_flag = (machine_type == 'ONE_CLASS') # True if one-class SVM is used

        idx_start, idx_end, n_machines = self.get_data_start_end_idx(real, N)

        machines = {}

        for machine_num in range(0, n_machines, 1):

            if not(one_class_flag): # two-class SVM

                real_subset     = real[:, idx_start[machine_num] : idx_end[machine_num] ] # both real and attack classes are used
                attack_subset = attack[:, idx_start[machine_num] : idx_end[machine_num] ]

            else: # one-class SVM case

                real_subset     = real[:, idx_start[machine_num] : idx_end[machine_num] ] # only the real class is used
                attack_subset = []

            machine = self.train_svm(real_subset, attack_subset, machine_type, kernel_type, svm_kwargs)

            machines[ str(machine_num) ] = machine

            del machine

        return machines


    #==========================================================================
    def train_pca_svm_cascade(self, real, attack, machine_type, kernel_type, svm_kwargs, N):
        """
        This function is designed to train the **cascede** of SVMs given
        features of real and attack classes. The procedure is the following:

        1. First, the PCA machine is trained also incorporating mean-std
           feature normalization. Only the features of the **real** class are
           used in PCA training, both for one-class and two-class SVMs.

        2. The features are next projected given trained PCA machine.

        3. Next, SVM machine is trained for each N projected features. Prior to
           SVM training the features are again mean-std normalized. First, preojected
           features corresponding to highest eigenvalues are selected. N is usually small
           N = (2, 3). So, if N = 2, the first SVM is trained for projected features 1 and 2,
           second SVM is trained for projected features 3 and 4, and so on.

        Both one-class SVM and two-class SVM cascades can be trained.
        In this implementation the grid search of SVM parameters is not supported.

        **Parameters:**

        ``real`` : 2D :py:class:`numpy.ndarray`
            Training features for the real class.

        ``attack`` : 2D :py:class:`numpy.ndarray`
            Training features for the attack class. If machine_type == 'ONE_CLASS'
            this argument can be anything, it will be skipped.

        ``machine_type`` : :py:class:`str`
            A type of the SVM machine. Please check ``bob.learn.libsvm`` for
            more details.

        ``kernel_type`` : :py:class:`str`
            A type of kerenel for the SVM machine. Please check ``bob.learn.libsvm``
            for more details.

        ``svm_kwargs`` : :py:class:`dict`
            Dictionary containing the hyper-parameters of the SVM.

        ``N`` : :py:class:`int`
            The number of features to be used for training a single SVM machine
            in the cascade.

        **Returns:**

        ``pca_machine`` : object
            A trained PCA machine.

        ``svm_machines`` : :py:class:`dict`
            A cascade of SVM machines.
        """

        one_class_flag = (machine_type == 'ONE_CLASS') # True if one-class SVM is used

        # 1. Train PCA using normalized features of the real class:
        pca_machine, _ = self.train_pca(real) # the mean-std normalizers are already set in this machine

        # 2. Project the features given PCA machine:
        if not(one_class_flag):
            projected_real = pca_machine(real) # the normalizers are already set for the PCA machine, therefore non-normalized data is passed in
            projected_attack = pca_machine(attack) # the normalizers are already set for the PCA machine, therefore non-normalized data is passed in

        else:
            projected_real = pca_machine(real) # the normalizers are already set for the PCA machine, therefore non-normalized data is passed in
            projected_attack = []

        # 3. Train a cascade of SVM machines using **projected** data
        svm_machines = self.train_svm_cascade(projected_real, projected_attack, machine_type, kernel_type, svm_kwargs, N)

        return pca_machine, svm_machines


    #==========================================================================
    def save_machine(self, projector_file, projector_file_name, machine):
        """
        Saves the machine to the hdf5 file. The name of the file is specified in
        ``projector_file_name`` string. The location is specified in the
        path component of the ``projector_file`` string.

        **Parameters:**

        ``projector_file`` : :py:class:`str`
            Absolute name of the file to save the trained projector to, as
            returned by ``bob.pad.base`` framework. In this function only the path
            component is used.

        ``projector_file_name`` : :py:class:`str`
            The relative name of the file to save the machine to. Name without
            extension.

        ``machine`` : object
            The machine to be saved.
        """

        extension = ".hdf5"

        resulting_file_name = os.path.join( os.path.split(projector_file)[0], projector_file_name + extension )

        f = bob.io.base.HDF5File(resulting_file_name, 'w') # open hdf5 file to save to

        machine.save(f) # save the machine and normalization parameters

        del f


    #==========================================================================
    def save_cascade_of_machines(self, projector_file, projector_file_name, machines):
        """
        Saves a cascade of machines to the hdf5 files. The name of the file is
        specified in ``projector_file_name`` string and will be augumented with
        a number of the machine. The location is specified in the path component
        of the ``projector_file`` string.

        **Parameters:**

        ``projector_file`` : :py:class:`str`
            Absolute name of the file to save the trained projector to, as
            returned by ``bob.pad.base`` framework. In this function only the path
            component is used.

        ``projector_file_name`` : :py:class:`str`
            The relative name of the file to save the machine to. This name will
            be augumented with a number of the machine. Name without extension.

        ``machines`` : :py:class:`dict`
            A cascade of machines. The key in the dictionary is the number of
            the machine, value is the machine itself.
        """

        for key in machines:

            augumented_projector_file_name = projector_file_name + key

            machine = machines[key]

            self.save_machine(projector_file, augumented_projector_file_name, machine)


    #==========================================================================
    def train_projector(self, training_features, projector_file):
        """
        Train PCA and cascade of SVMs for feature projection and save them
        to files. The ``requires_projector_training = True`` flag must be set
        to True to enable this function.

        **Parameters:**

        ``training_features`` : [[FrameContainer], [FrameContainer]]
            A list containing two elements: [0] - a list of Frame Containers with
            feature vectors for the real class; [1] - a list of Frame Containers with
            feature vectors for the attack class.

        ``projector_file`` : :py:class:`str`
            The file to save the trained projector to, as returned by the
            ``bob.pad.base`` framework. In this class the names of the files to
            save the projectors to are modified, see ``save_machine`` and
            ``save_cascade_of_machines`` methods of this class for more details.
        """

        # training_features[0] - training features for the REAL class.
        real = convert_list_of_frame_cont_to_array(training_features[0]) # output is array
        # training_features[1] - training features for the ATTACK class.
        attack = convert_list_of_frame_cont_to_array(training_features[1]) # output is array

        # Train the PCA machine and cascade of SVMs
        pca_machine, svm_machines = self.train_pca_svm_cascade(real = real,
                                                               attack = attack,
                                                               machine_type = self.machine_type,
                                                               kernel_type = self.kernel_type,
                                                               svm_kwargs = self.svm_kwargs,
                                                               N = self.N)

        # Save the PCA machine
        self.save_machine(projector_file, self.pca_projector_file_name, pca_machine)

        # Save the cascade of SVMs:
        self.save_cascade_of_machines(projector_file, self.svm_projector_file_name, svm_machines)


    #==========================================================================
    def load_machine(self, projector_file, projector_file_name):
        """
        Loads the machine from the hdf5 file. The name of the file is specified in
        ``projector_file_name`` string. The location is specified in the
        path component of the ``projector_file`` string.

        **Parameters:**

        ``projector_file`` : :py:class:`str`
            Absolute name of the file to load the trained projector from, as
            returned by ``bob.pad.base`` framework. In this function only the path
            component is used.

        ``projector_file_name`` : :py:class:`str`
            The relative name of the file to load the machine from. Name without
            extension.

        **Returns:**

        ``machine`` : object
            A machine loaded from file.
        """

        extension = ".hdf5"

        resulting_file_name = os.path.join( os.path.split(projector_file)[0], projector_file_name + extension ) # name of the file

        f = bob.io.base.HDF5File(resulting_file_name, 'r') # file to read the machine from

        if "pca_" in projector_file_name:

            machine = bob.learn.linear.Machine(f)

        if "svm_" in projector_file_name:

            machine = bob.learn.libsvm.Machine(f)

        del f

        return machine


    #==========================================================================
    def get_cascade_file_names(self, projector_file, projector_file_name):
        """
        Get the list of file-names storing the cascade of machines. The location
        of the files is specified in the path component of the ``projector_file``
        argument.

        **Parameters:**

        ``projector_file`` : :py:class:`str`
            Absolute name of the file to load the trained projector from, as
            returned by ``bob.pad.base`` framework. In this function only the path
            component is used.

        ``projector_file_name`` : :py:class:`str`
            The **common** string in the names of files storing the
            cascade of pretrained machines. Name without extension.

        **Returns:**

        ``cascade_file_names`` : [str]
            A list of of **relative** file-names storing the cascade of machines.
        """

        path = os.path.split(projector_file)[0] # directory containing files storing the cascade of machines.

        files = []

        for f in os.listdir( path ):

            if fnmatch.fnmatch( f, projector_file_name + "*" ):

                files.append(f)

        return files


    #==========================================================================
    def load_cascade_of_machines(self, projector_file, projector_file_name):
        """
        Loades a cascade of machines from the hdf5 files. The name of the file is
        specified in ``projector_file_name`` string and will be augumented with
        a number of the machine. The location is specified in the path component
        of the ``projector_file`` string.

        **Parameters:**

        ``projector_file`` : :py:class:`str`
            Absolute name of the file to load the trained projector from, as
            returned by ``bob.pad.base`` framework. In this function only the path
            component is used.

        ``projector_file_name`` : :py:class:`str`
            The relative name of the file to load the machine from. This name will
            be augumented with a number of the machine. Name without extension.

        **Returns:**

        ``machines`` : :py:class:`dict`
            A cascade of machines. The key in the dictionary is the number of
            the machine, value is the machine itself.
        """

        files = self.get_cascade_file_names(projector_file, projector_file_name) # files storing the cascade

        machines = {}

        for idx, _ in enumerate(files):

            machine = self.load_machine( projector_file, projector_file_name + str(idx) )

            machines[ str(idx) ] = machine

        return machines


    #==========================================================================
    def load_projector(self, projector_file):
        """
        Load the pretrained PCA machine and a cascade of SVM classifiers from
        files to perform feature projection.
        This function sets the arguments ``self.pca_machine`` and ``self.svm_machines``
        of this class with loaded machines.

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

        # Load the PCA machine
        pca_machine = self.load_machine(projector_file, self.pca_projector_file_name)

        # Load the cascade of SVMs:
        svm_machines = self.load_cascade_of_machines(projector_file, self.svm_projector_file_name)

        self.pca_machine = pca_machine
        self.svm_machines = svm_machines


    #==========================================================================
    def combine_scores_of_svm_cascade(self, scores_array, pos_scores_slope):
        """
        First, multiply positive scores by constant ``pos_scores_slope`` in the
        input 2D array. The constant is usually small, making the impact of negative
        scores more significant.
        Second, the a single score per sample is obtained by avaraging the
        **pre-modified** scores of the cascade.

        **Parameters:**

        ``scores_array`` : 2D :py:class:`numpy.ndarray`
            2D score array of the size (N_samples x N_scores).

        ``pos_scores_slope`` : :py:class:`float`
            The positive scores returned by SVM cascade will be multiplied by this
            constant prior to majority voting. Default: 0.01 .

        **Returns:**

        ``scores`` : 1D :py:class:`numpy.ndarray`
            Vector of scores. Scores for the real class are expected to be
            higher, than the scores of the negative / attack class.
        """

        cols = []

        for col in scores_array.T:

            idx_vec = np.where(col>=0)

            col[idx_vec] *= pos_scores_slope # multiply positive scores by the constant

            cols.append(col)

        scores_array_modified = np.stack(cols, axis=1)

        scores = np.mean(scores_array_modified, axis = 1)

        return scores


    #==========================================================================
    def project(self, feature):
        """
        This function computes a vector of scores for each sample in the input
        array of features. The following steps are apllied:

        1. Convert input array to numpy array if necessary.

        2. Project features using pretrained PCA machine.

        3. Apply the cascade of SVMs to the preojected features.

        4. Compute a single score per sample by combining the scores produced
           by the cascade of SVMs. The combination is done using
           ``combine_scores_of_svm_cascade`` method of this class.

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
        """

        # 1. Convert input array to numpy array if necessary.
        if isinstance(feature, FrameContainer): # if FrameContainer convert to 2D numpy array

            features_array = convert_frame_cont_to_array(feature)

        else:

            features_array = feature

        # 2. Project features using pretrained PCA machine.
        pca_projected_features = self.pca_machine(features_array)

        # 3. Apply the cascade of SVMs to the preojected features.
        all_scores = []

        idx_start, idx_end, n_machines = self.get_data_start_end_idx(pca_projected_features, self.N)

        for machine_num in range(0, n_machines, 1): # iterate over SVM machines

            svm_machine = self.svm_machines[ str(machine_num) ] # select a machine

            # subset of PCA projected features to be passed to SVM machine
            pca_projected_features_subset = pca_projected_features[:, idx_start[machine_num] : idx_end[machine_num] ]

            # for two-class SVM select the scores corresponding to the real class only, done by [:,0]. Index [0] selects the class Index [1] selects the score..
            single_machine_scores = svm_machine.predict_class_and_scores( pca_projected_features_subset )[1][:,0]

            all_scores.append(single_machine_scores)

        all_scores_array   = np.stack(all_scores, axis = 1).astype(np.float)

        # 4. Combine the scores:

        one_class_flag = (svm_machine.machine_type == 'ONE_CLASS') # True if one-class SVM is used

        if not(one_class_flag):

            scores = np.mean(all_scores_array, axis = 1) # compute mean for two-class SVM

        else: # one class SVM case

            scores = self.combine_scores_of_svm_cascade(all_scores_array, self.pos_scores_slope)

        return scores


    #==========================================================================
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

            score = [np.mean( toscore )] # compute a single score per video

        return score





