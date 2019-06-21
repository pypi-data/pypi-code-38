#!/usr/bin/env python
# vim: set fileencoding=utf-8 :
# Tiago de Freitas Pereira <tiago.pereira@idiap.ch>

import bob.learn.linear
import bob.io.base
import numpy
import scipy.spatial

import logging

logger = logging.getLogger("bob.bio.htface")

from bob.learn.linear import GFKMachine, GFKTrainer
from .GFK import GFK
from bob.bio.face.algorithm import GaborJet
import math


class GFK_GaborJet(GFK, GaborJet):
    """

    Gabor jets + GFK


    """

    def __init__(
            self,
            number_of_subspaces,  # if int, number of subspace dimensions; if float, percentage of variance to keep
            source_subspace_dimension,
            target_subspace_dimension,
            use_lda=False,  # BUild the subspaces with LDA
            distance_function=scipy.spatial.distance.euclidean,
            is_distance_function=True,
            uses_variances=False,
            use_pinv=True,
            kernel_per_jet=True,
            **kwargs  # parameters directly sent to the base class
    ):
        # For the time being, default parameters are fine
        GaborJet.__init__(self,
                          # parameters for the tool
                          'PhaseDiffPlusCanberra',
                          multiple_feature_scoring='average',
                          # some similarity functions might need a GaborWaveletTransform class, so we have to provide the parameters here as well...
                          gabor_directions=8,
                          gabor_scales=5,
                          gabor_sigma=2. * math.pi,
                          gabor_maximum_frequency=math.pi / 2.,
                          gabor_frequency_step=math.sqrt(.5),
                          gabor_power_of_k=0,
                          gabor_dc_free=True
                          )

        GFK.__init__(self,
                     number_of_subspaces=number_of_subspaces,
                     # if int, number of subspace dimensions; if float, percentage of variance to keep
                     source_subspace_dimension=source_subspace_dimension,
                     target_subspace_dimension=target_subspace_dimension,
                     use_lda=use_lda,  # BUild the subspaces with LDA
                     distance_function=distance_function,
                     is_distance_function=is_distance_function,
                     uses_variances=uses_variances,
                     use_pinv=use_pinv,
                     **kwargs
                     )

        self.kernel_per_jet = kernel_per_jet

    def _stack_gabor_jets_per_jet(self, jets):
        """
        Stacking the absolute values of the gabor jets per node
        """

        if self.use_lda:
            # Stackin the jets per jet position and per client

            client_abs = []
            for clients in jets:

                jets_abs = {}
                for j in clients:
                    shape = (0, len(j[0].abs))
                    jet_index = 0
                    for a in j:
                        if not jets_abs.has_key(jet_index):
                            jets_abs[jet_index] = numpy.zeros(shape=shape)
                        jets_abs[jet_index] = numpy.vstack((jets_abs[jet_index], a.abs))
                        jet_index += 1

                client_abs.append(jets_abs)
            return client_abs
        
        else:
            # Stackin the jets per jet position
            jets_abs = {}
            for j in jets:
                shape = (0, len(j[0].abs))
                jet_index = 0
                for a in j:
                    if jet_index not in jets_abs:
                        jets_abs[jet_index] = numpy.zeros(shape=shape)
                    jets_abs[jet_index] = numpy.vstack((jets_abs[jet_index], a.abs))
                    jet_index += 1

            return jets_abs

    def _stack_gabor_jets(self, jets):
        """
        Stacking the absolute values of the gabor jets
        """

        if self.use_lda:
            # Return the responses per client
            client_abs = []
            shape = (len(jets[0][0])*len(jets[0]), len(jets[0][0][0].abs))
            for clients in jets:
                jets_abs = numpy.zeros(shape=shape)
                jet_index = 0
                for j in clients:
                    for a in j:
                        #jets_abs = numpy.vstack((jets_abs, a.abs))
                        jets_abs[jet_index, :] = a.abs
                        jet_index += 1

                client_abs.append(jets_abs)
            return client_abs

        else:
            shape = (len(jets)*len(jets[0]), len(jets[0][0].abs))
            jets_abs = numpy.zeros(shape=shape)
            jet_index = 0
            for j in jets:
                for a in j:
                    #jets_abs = numpy.vstack((jets_abs, a.abs))
                    jets_abs[jet_index, :] = a.abs
                    jet_index += 1

            return jets_abs

    def train_projector(self, training_features, projector_file, metadata=None):
        """Compute the kernel using the jets.abs"""
        gfk_trainer = GFKTrainer(self.m_number_of_subspaces,
                                 subspace_dim_source=self.m_source_subspace_dimension,
                                 subspace_dim_target=self.m_target_subspace_dimension,
                                 eps=self.eps)

        source_jets, target_jets = self.split_data_by_modality(training_features, metadata, self.split_training_features_by_client)
        #self.split_training_features_by_client
        # Creating a kernel per jet

        if self.kernel_per_jet:

            # Stacking the jets per node
            source_jets_abs = self._stack_gabor_jets_per_jet(source_jets)
            target_jets_abs = self._stack_gabor_jets_per_jet(target_jets)

            if self.use_lda:

                from bob.learn.linear.GFK import null_space
                
                # Getting the list of keys
                keys = source_jets_abs[0].keys()
                logger.info("  -> Training {0} GFKs using PCA+LDA ".format(len(keys)))

                hdf5 = bob.io.base.HDF5File(projector_file, 'w')
                hdf5.set("nodes", len(keys))
                gfk_machine = []
                
                for k in keys:
                    
                    node_name = "node{0}".format(k)
                    logger.info("    -> Training node {0} ".format(node_name))
                                                
                    # Stacking the absolute values per client and per node
                    source_client_jets = [c[k] for c in source_jets_abs]
                    target_client_jets = [c[k] for c in target_jets_abs]

                    logger.info("      -> Training PCA+LDA for the source ")
                    Ps = self.train_pca_lda(source_client_jets)

                    logger.info("      -> Training PCA+LDA for the target ")
                    Pt = self.train_pca_lda(target_client_jets)
                                
                    logger.info("      -> Training GFK ")
                    G = gfk_trainer._train_gfk(numpy.hstack((Ps.weights, null_space(Ps.weights.T))),Pt.weights[:, 0:self.m_target_subspace_dimension])
                    machine = GFKMachine()
                    machine.source_machine = Ps
                    machine.target_machine = Pt
                    machine.G = G
                    
                    # Saving
                    hdf5.create_group(node_name)
                    hdf5.cd(node_name)
                    machine.save(hdf5)
                    hdf5.cd("..")

                    gfk_machine.append(machine)
            else:
                # Computing a kernel per node
                hdf5 = bob.io.base.HDF5File(projector_file, 'w')
                gfk_machine = []
                
                for k in source_jets_abs.keys():
                    node_name = "node{0}".format(k)
                    logger.info("  -> Training {0}".format(node_name))
                    machine = gfk_trainer.train(source_jets_abs[k], target_jets_abs[k])
                    hdf5.create_group(node_name)
                    hdf5.cd(node_name)
                    machine.save(hdf5)
                    gfk_machine.append(machine)
                    hdf5.cd("..")
                hdf5.set("nodes", len(source_jets_abs.keys()))

        else:
            # Creating one single kernel

            # Stacking the jets
            source_jets_abs = self._stack_gabor_jets(source_jets)
            target_jets_abs = self._stack_gabor_jets(target_jets)
            logger.info("  -> Training one single GFK ")
            
            if self.use_lda:
                from bob.learn.linear.GFK import null_space
                
                logger.info("  -> Training PCA+LDA for the source ")
                Ps = self.train_pca_lda(source_jets_abs)
                
                logger.info("  -> Training PCA+LDA for the target ")
                Pt = self.train_pca_lda(target_jets_abs)

                logger.info("  -> Training GFK ")
                G = gfk_trainer._train_gfk(numpy.hstack((Ps.weights, null_space(Ps.weights.T))),Pt.weights[:, 0:self.m_target_subspace_dimension])
                hdf5 = bob.io.base.HDF5File(projector_file, 'w')
                gfk_machine = GFKMachine()
                gfk_machine.source_machine = Ps
                gfk_machine.target_machine = Pt
                gfk_machine.G = G
                gfk_machine.save(hdf5)

            else:
                # Computing a kernel per node
                hdf5 = bob.io.base.HDF5File(projector_file, 'w')
                gfk_machine = gfk_trainer.train(source_jets_abs, target_jets_abs)
                gfk_machine.save(hdf5)

    def train_pca_lda(self, train_features):
        """
        Train PCA and LDA
        """
    
        # Train PCA first
        pca_machine = self._znorm_perclient_and_pca(train_features)
    
        # Project the data with PCA        
        pca_data = []
        for c in train_features:
            pca_data.append( pca_machine (c))
        
        # Train LDA
        lda_trainer = bob.learn.linear.FisherLDATrainer()
        lda_machine,_ = lda_trainer.train(pca_data)
        
        # Doing PCA+LDA
        pcalda_matrix = numpy.dot(pca_machine.weights, lda_machine.weights)
        linear_machine = bob.learn.linear.Machine(pcalda_matrix)
        linear_machine.input_subtract = pca_machine.input_subtract
        linear_machine.input_divide = pca_machine.input_divide
        
        return linear_machine

    def _znorm_perclient_and_pca(self, client_data):
        """
        ZNormalize the data and trains a PCA
        """
        # First normalize the data
        data = numpy.vstack([feature for feature in client_data]) # Stacking the features
        mu = numpy.average(data, axis=0)
        std = numpy.std(data, axis=0)
        
        # Train PCA
        pca_trainer = bob.learn.linear.PCATrainer()
        pca_machine,_ = pca_trainer.train(data)
        pca_machine.input_subtract = mu
        pca_machine.input_divide = std
        
        return pca_machine


    def load_projector(self, projector_file):
        """Reads the1 PCA projection matrix from file"""
                
        # read PCA projector
        hdf5 = bob.io.base.HDF5File(projector_file, 'r')

        # Loading one kernel per jet
        if self.kernel_per_jet:

            nodes = hdf5.get("nodes")
            self.gfk_machine = []
            hdf5 = bob.io.base.HDF5File(projector_file)
            for k in range(nodes):
                node_name = "node{0}".format(k)
                hdf5.cd(node_name)
                self.gfk_machine.append(GFKMachine(hdf5))
                hdf5.cd("..")
        else:
            hdf5 = bob.io.base.HDF5File(projector_file)
            self.gfk_machine = GFKMachine(hdf5)
            

    def project(self, feature):
        """Projects the data using the stored covariance matrix"""
        raise NotImplemented("There is no projection")

    def enroll(self, enroll_features):
        """enroll(enroll_features) -> model

        Enrolls the model using one of several strategies.
        Commonly, the bunch graph strategy [WFK97]_ is applied, by storing several Gabor jets for each node.

        When ``multiple_feature_scoring = 'average_model'``, for each node the average :py:class:`bob.ip.gabor.Jet` is computed.
        Otherwise, all enrollment jets are stored, grouped by node.

        **Parameters:**

        enroll_features : [[:py:class:`bob.ip.gabor.Jet`]]
          The list of enrollment features.
          Each sub-list contains a full graph.

        **Returns:**

        model : [[:py:class:`bob.ip.gabor.Jet`]]
          The enrolled model.
          Each sub-list contains a list of jets, which correspond to the same node.
          When ``multiple_feature_scoring = 'average_model'`` each sub-list contains a single :py:class:`bob.ip.gabor.Jet`.
        """

        return GaborJet.enroll(self, enroll_features)

    def write_model(self, model, model_file):
        """Writes the model enrolled by the :py:meth:`enroll` function to the given file.

        **Parameters:**

        model : [[:py:class:`bob.ip.gabor.Jet`]]
          The enrolled model.

        model_file : str or :py:class:`bob.io.base.HDF5File`
          The name of the file or the file opened for writing.
        """
        GaborJet.write_model(self, model, model_file)

    def read_model(self, model_file):
        """read_model(model_file) -> model

        Reads the model written by the :py:meth:`write_model` function from the given file.

        **Parameters:**

        model_file : str or :py:class:`bob.io.base.HDF5File`
          The name of the file or the file opened for reading.
        **Returns:**

        model : [[:py:class:`bob.ip.gabor.Jet`]]
          The list of Gabor jets read from file.
        """
        return GaborJet.read_model(self, model_file)

    def read_probe(self, probe_file):
        """read_probe(probe_file) -> probe

        Reads the probe file, e.g., as written by the :py:meth:`bob.bio.face.extractor.GridGraph.write_feature` function from the given file.

        **Parameters:**

        probe_file : str or :py:class:`bob.io.base.HDF5File`
          The name of the file or the file opened for reading.

        **Returns:**

        probe : [:py:class:`bob.ip.gabor.Jet`]
          The list of Gabor jets read from file.
        """
        return GaborJet.read_probe(self, probe_file)

    def score(self, model, probe):
        """
        Compute the Kernalized scalar product between the absolute values of the Jets
        """

        if self.kernel_per_jet:
            local_scores = [numpy.dot(
                numpy.dot(
                    (m[0].abs - machine.source_machine.input_subtract) / machine.source_machine.input_divide, machine.G),
                (p.abs - machine.target_machine.input_subtract) / machine.target_machine.input_divide)
                            for m, p, machine in zip(model, probe, self.gfk_machine)]
        else:
            local_scores = [numpy.dot(
                numpy.dot(
                    (m[0].abs - self.gfk_machine.source_machine.input_subtract) / self.gfk_machine.source_machine.input_divide, self.gfk_machine.G),
                (p.abs - self.gfk_machine.target_machine.input_subtract) / self.gfk_machine.target_machine.input_divide)
                            for m, p in zip(model, probe)]

        return numpy.average(local_scores)
