#!/usr/bin/env python
# vim: set fileencoding=utf-8 :

import numpy

from bob.pad.base.algorithm import Algorithm
import bob.learn.mlp
import bob.io.base

import logging
logger = logging.getLogger(__name__)


class MLP(Algorithm):
    """Interfaces an MLP classifier used for PAD

    Attributes
    ----------
    hidden_units : :py:obj:`tuple` of :any:`int`
      The number of hidden units in each hidden layer
    max_iter : :any:`int`
      The maximum number of training iterations
    precision : :any:`float`
      criterion to stop the training: if the difference
      between current and last loss is smaller than
      this number, then stop training.
    """

    def __init__(self, hidden_units=(10, 10), max_iter=1000, precision=0.001, **kwargs):
        """Init function

        Parameters
        ----------
        hidden_units : :py:obj:`tuple` of int
          The number of hidden units in each hidden layer
        max_iter : int
          The maximum number of training iterations
        precision : float
          criterion to stop the training: if the difference
          between current and last loss is smaller than
          this number, then stop training.

        """
        Algorithm.__init__(self,
                           performs_projection=True,
                           requires_projector_training=True,
                           **kwargs)

        self.hidden_units = hidden_units
        self.max_iter = max_iter
        self.precision = precision
        self.mlp = None

    def train_projector(self, training_features, projector_file):
        """Trains the MLP

        Parameters
        ----------
        training_features : :any:`list` of :py:class:`numpy.ndarray`
          Data used to train the MLP. The real attempts are in training_features[0] and the attacks are in training_features[1]
        projector_file : str
          Filename where to save the trained model.

        """
        # training is done in batch (i.e. using all training data)
        batch_size = len(training_features[0]) + len(training_features[1])

        # The labels
        label_real = numpy.zeros((len(training_features[0]), 2), dtype='float64')
        label_real[:, 0] = 1
        label_attack = numpy.zeros((len(training_features[1]), 2), dtype='float64')
        label_attack[:, 1] = 0

        real = numpy.array(training_features[0])
        attack = numpy.array(training_features[1])
        X = numpy.vstack([real, attack])
        Y = numpy.vstack([label_real, label_attack])

        # Building MLP architecture
        input_dim = real.shape[1]
        shape = []
        shape.append(input_dim)
        for i in range(len(self.hidden_units)):
            shape.append(self.hidden_units[i])
        # last layer contains two units: one for each class (i.e. real and attack)
        shape.append(2)
        shape = tuple(shape)

        self.mlp = bob.learn.mlp.Machine(shape)
        self.mlp.output_activation = bob.learn.activation.Logistic()
        self.mlp.randomize()
        trainer = bob.learn.mlp.BackProp(batch_size, bob.learn.mlp.CrossEntropyLoss(self.mlp.output_activation), self.mlp, train_biases=True)

        n_iter = 0
        previous_cost = 0
        current_cost = 1
        while (n_iter < self.max_iter) and (abs(previous_cost - current_cost) > self.precision):
            previous_cost = current_cost
            trainer.train(self.mlp, X, Y)
            current_cost = trainer.cost(self.mlp, X, Y)
            n_iter += 1
            logger.debug("Iteration {} -> cost = {} (previous = {}, max_iter = {})".format(n_iter, trainer.cost(self.mlp, X, Y), previous_cost, self.max_iter))

        f = bob.io.base.HDF5File(projector_file, 'w')
        self.mlp.save(f)

    def project(self, feature):
        """Project the given feature

        Parameters
        ----------
        feature : :py:class:`numpy.ndarray`
          The feature to classify

        Returns
        -------
        numpy.ndarray
          The value of the two units in the last layer of the MLP.
        """
       # if isinstance(feature, FrameContainer):
       #     feature = convert_frame_cont_to_array(feature)
        return self.mlp(feature)

    def score(self, toscore):
        """Returns the probability of the real class.

        Parameters
        ----------
        toscore : :py:class:`numpy.ndarray`

        Returns
        -------
        float
         probability of the authentication attempt to be real.
        """
        if toscore.ndim == 1:
            return [toscore[0]]
        else:
            return numpy.mean([toscore[:, 0]])
