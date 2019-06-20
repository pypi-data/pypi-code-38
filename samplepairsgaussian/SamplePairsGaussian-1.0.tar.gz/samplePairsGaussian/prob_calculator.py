import numpy as np
import logging
import sys

class ProbCalculator:
    """Calculates distances and probabilities for a set of particles.

    Attributes:
    posns (np.array([[float]])): particle positions. First axis are particles, seconds are coordinates in n-dimensional space
    n (int): number of particles
    std_dev (float): standard deviation for cutting off probabilities
    std_dev_clip_mult (float): multiplier for the standard deviation cutoff

    probs_first_particle (np.array([float])): probabilities for the first particle of length n
    are_probs_first_particle_normalized (bool): bool whether the probabilities are normalized
    max_prob_first_particle (float): the maximum probability value, useful for rejection sampling

    idxs_possible_second_particle (np.array([int])): indexes possible for the second particle
    no_idxs_possible_second_particle (int): number of indexes possible i.e. len(idxs_possible_second_particle)
    probs_second_particle (np.array([float])): probabilities for the first particle of length idxs_possible_second_particle
    are_probs_second_particle_normalized (bool): bool whether the probabilities are normalized
    max_prob_second_particle (float): the maximum probability value, useful for rejection sampling


    Private attributes:
    _logger (logger): logging
    _dists_squared (np.array([float])): square displacements of particles from eachother
    _uti ([np.array([int]),np.array([int])]): indexes for displacements forming an upper triangular matrix, from np.triu_indices
    _dists_squared_filter (np.array([float])): as _dists_squared, after cutoff is applied
    _uti0filter (np.array([int])): as _uti[0], after the cutoff is applied
    _uti1filter (np.array([int])): as _uti[1], after the cutoff is applied
    _gauss (np.array([float])) _dists_squared_filter converted to Gaussians
    """



    def __init__(self, posns, std_dev, std_dev_clip_mult):
        """Constructor.

        Args:
        posns (np.array([[float]])): particle positions. First axis are particles, seconds are coordinates in n-dimensional space
        std_dev (float): standard deviation for cutting off probabilities
        std_dev_clip_mult (float): multiplier for the standard deviation cutoff
        """

        # Setup the logger
        self._logger = logging.getLogger(__name__)
        formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
        ch = logging.StreamHandler()
        ch.setLevel(logging.DEBUG)
        ch.setFormatter(formatter)
        self._logger.addHandler(ch)

        # Level of logging to display
        self._logger.setLevel(logging.ERROR)

        # vars
        self.posns = posns
        self.n = len(self.posns)
        self.std_dev = std_dev
        self.std_dev_clip_mult = std_dev_clip_mult

        # Initialize all manner of other properties for possible later use
        self._uti = np.array([]).astype(int)
        self._dists_squared = np.array([])

        self._dists_squared_filter = np.array([])
        self._uti0filter = np.array([]).astype(int)
        self._uti1filter = np.array([]).astype(int)
        self._gauss = np.array([])
        self.probs_first_particle = np.array([])
        self.are_probs_first_particle_normalized = False
        self.max_prob_first_particle = 0.0

        self.idxs_possible_second_particle = np.array([]).astype(int)
        self.no_idxs_possible_second_particle = 0
        self.probs_second_particle = np.array([])
        self.are_probs_second_particle_normalized = False
        self.max_prob_second_particle = 0.0



    def set_logging_level(self, level):
        """Sets the logging level
        Args:
        level (logging): logging level
        """
        self._logger.setLevel(level)



    def compute_un_probs_first_particle(self):
        """Compute un-normalized probabilities for drawing the first particle out of n possible particles.
        After running this, the following arguments will be set:
            probs_first_particle
            are_probs_first_particle_normalized
            max_prob_first_particle
        """

        # Check there are sufficient particles
        if self.n < 2:
            self._logger.error("Error: computing distances for: " + str(self.n) + " particles. This can't work! Quitting.")
            sys.exit(0)

        # uti is a list of two (1-D) numpy arrays
        # containing the indices of the upper triangular matrix
        self._uti = np.triu_indices(self.n,k=1)        # k=1 eliminates diagonal indices

        # uti[0] is i, and uti[1] is j from the previous example
        dr = self.posns[self._uti[0]] - self.posns[self._uti[1]]            # computes differences between particle positions
        self._dists_squared = np.sum(dr*dr, axis=1)    # computes distances squared; D is a 4950 x 1 np array

        # Clip distances at std_dev_clip_mult * sigma
        max_dist_squared = pow(self.std_dev_clip_mult*self.std_dev,2)
        two_var = 2.0 * pow(self.std_dev,2)

        # Eliminate beyond max dist
        stacked = np.array([self._uti[0],self._uti[1],self._dists_squared]).T
        self._uti0filter, self._uti1filter, self._dists_squared_filter = stacked[stacked[:,2] < max_dist_squared].T
        self._uti0filter = self._uti0filter.astype(int)
        self._uti1filter = self._uti1filter.astype(int)

        # Compute gaussians
        self._gauss = np.exp(-self._dists_squared_filter/two_var)

        # Not normalized probs for first particle
        self.probs_first_particle = np.bincount(self._uti0filter,self._gauss,minlength=self.n) + np.bincount(self._uti1filter,self._gauss,minlength=self.n)
        self.are_probs_first_particle_normalized = False
        self.max_prob_first_particle = max(self.probs_first_particle)

    def normalize_probs_first_particle(self):
        """Normalize the probs for the first particle
        """

        self.are_probs_first_particle_normalized = True
        norm = np.sum(self.probs_first_particle)
        self.probs_first_particle /= norm
        self.max_prob_first_particle = 1.0

    def compute_un_probs_second_particle(self, idx_first_particle):
        """Compute un-normalized probabilities for drawing the second particle for a given first particle.
        After running this, the following arguments will be set:
            idxs_possible_second_particle
            no_idxs_possible_second_particle
            probs_second_particle
            are_probs_second_particle_normalized
            max_prob_second_particle

        Args:
        idx_first_particle (int): the index of the first particle in 0,1,...,n-1
        """

        # Not normalized probs for second particle probs
        true_false_0 = self._uti0filter == idx_first_particle
        true_false_1 = self._uti1filter == idx_first_particle

        # Idxs
        self.idxs_possible_second_particle = np.concatenate((self._uti1filter[true_false_0], self._uti0filter[true_false_1]))
        self.no_idxs_possible_second_particle = len(self.idxs_possible_second_particle)

        # Probs
        self.probs_second_particle = np.concatenate((self._gauss[true_false_0],self._gauss[true_false_1]))

        self.are_probs_second_particle_normalized = False
        self.max_prob_second_particle = max(self.probs_second_particle)

    def normalize_probs_second_particle(self):
        """Normalize the probs for the second particle
        """

        self.are_probs_second_particle_normalized = True
        norm = np.sum(self.probs_second_particle)
        self.probs_second_particle /= norm
        self.max_prob_second_particle = 1.0
