# -*- coding: utf-8 -*-
# @author: Amir Mohammadi

from bob.pad.base.algorithm import Algorithm
from bob.pad.base.utils import convert_and_prepare_features
from bob.bio.gmm.algorithm import GMM
import logging
import numpy as np
from collections.abc import Iterable
from multiprocessing import cpu_count

logger = logging.getLogger(__name__)


def bic(trainer, machine, X):
    """Bayesian information criterion for the current model on the input X.

    Parameters
    ----------
    X : array of shape (n_samples, n_dimensions)

    Returns
    -------
    bic : float
        The lower the better.
    """
    log_likelihood = trainer.compute_likelihood(machine)
    n_parameters = (
        machine.means.size + machine.variances.size + len(machine.weights) - 1
    )
    return -2 * log_likelihood * X.shape[0] + n_parameters * np.log(X.shape[0])


class OneClassGMM2(Algorithm):
    """A one class GMM implementation based on Bob's GMM implementation which is more
    stable than scikit-learn's one."""

    def __init__(
        self,
        # parameters for the GMM
        number_of_gaussians,
        # parameters of UBM training
        kmeans_training_iterations=25,  # Maximum number of iterations for K-Means
        gmm_training_iterations=25,  # Maximum number of iterations for ML GMM Training
        training_threshold=5e-4,  # Threshold to end the ML training
        variance_threshold=5e-4,  # Minimum value that a variance can reach
        update_weights=True,
        update_means=True,
        update_variances=True,
        n_threads=cpu_count(),
        **kwargs
    ):
        kwargs.setdefault("performs_projection", True)
        kwargs.setdefault("requires_projector_training", True)
        super().__init__(**kwargs)
        self.gmm_alg = GMM(
            number_of_gaussians=number_of_gaussians,
            kmeans_training_iterations=kmeans_training_iterations,
            gmm_training_iterations=gmm_training_iterations,
            training_threshold=training_threshold,
            variance_threshold=variance_threshold,
            update_weights=update_weights,
            update_means=update_means,
            update_variances=update_variances,
            n_threads=n_threads,
        )
        self.number_of_gaussians = number_of_gaussians

    def train_projector(self, training_features, projector_file):
        del training_features[1]
        real = convert_and_prepare_features(training_features[0], dtype="float64")
        del training_features[0]

        if isinstance(self.number_of_gaussians, Iterable):
            logger.info(
                "Performing grid search for GMM on number_of_gaussians: %s",
                self.number_of_gaussians,
            )
            lowest_bic = np.infty
            best_n_gaussians = None
            for nc in self.number_of_gaussians:
                logger.info("Testing for number_of_gaussians: %s", nc)
                self.gmm_alg.gaussians = nc
                self.gmm_alg.train_ubm(real)
                bic_ = bic(self.gmm_alg.ubm_trainer, self.gmm_alg.ubm, real)
                logger.info("BIC for number_of_gaussians: %s is %s", nc, bic_)
                if bic_ < lowest_bic:
                    gmm = self.gmm_alg.ubm
                    lowest_bic = bic_
                    best_n_gaussians = nc
                    logger.info("Best parameters so far: number_of_gaussians %s", nc)

            assert best_n_gaussians is not None
            self.gmm_alg.gaussians = best_n_gaussians
        else:
            self.gmm_alg.train_ubm(real)
            gmm = self.gmm_alg.ubm

        self.gmm_alg.ubm = gmm
        self.gmm_alg.save_ubm(projector_file)

    def load_projector(self, projector_file):
        self.gmm_alg.load_ubm(projector_file)

    def project(self, feature):
        feature = convert_and_prepare_features([feature], dtype="float64")[0]

        return self.gmm_alg.ubm(feature)

    def score(self, toscore):
        return [toscore]
