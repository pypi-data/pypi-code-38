from .prob_calculator_multispecies import *

import numpy as np

class SamplerMultiSpecies:
    """SamplerMultiSpecies class.

    Attributes:
    prob_calculator (ProbCalculator): probability calculator
    idx_first_particle (int): idx of the first particle chosen
    idx_second_particle (int): idx of the second particle chosen

    Private attributes:
    _logger (logger): logging
    """



    def __init__(self, prob_calculator_multispecies):
        """Constructor. Also computes distances.

        Args:
        prob_calculator_multispecies (ProbCalculatorMultiSpecies): probability calculator for multiple species
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

        # Prob prob_calculator
        self.prob_calculator_multispecies = prob_calculator_multispecies

        # Init all other structures
        self.idx_species_particles = None
        self.species_particles = None
        self.idx_first_particle = None
        self.idx_second_particle = None



    def set_logging_level(self, level):
        """Sets the logging level

        Args:
        level (logging): logging level
        """
        self._logger.setLevel(level)



    def rejection_sample_first_particle(self, no_tries_max=100, compute_probs_species=True, compute_probs=True):
        """Use rejection sampling to sample the first particle

        Args:
        no_tries_max (int): max. no. of tries for rejection sampling
        compute_probs (bool): whether to first call compute_probs_first_particle for the ProbCalculatorMultiSpecies

        Returns:
        bool: True for success, False for failure
        """

        # Form probabilities for species
        if compute_probs_species:
            self.prob_calculator_multispecies.compute_species_probs()

        # Form probabilities
        if compute_probs:
            for prob_calculator in self.prob_calculator_multispecies.prob_calculator_arr:
                prob_calculator.compute_un_probs_first_particle()

        i_try = 0
        self.idx_first_particle = None
        while self.idx_first_particle == None and i_try < no_tries_max:
            i_try += 1

            # Random species
            idx_species = np.random.choice(range(0,self.prob_calculator_multispecies.no_species), 1, p=self.prob_calculator_multispecies.probs_species)[0]

            # Random particle of this species (uniform)
            idx_particle = np.random.randint(self.prob_calculator_multispecies.prob_calculator_arr[idx_species].n)

            # Rejection sampling
            r = np.random.uniform(0.0,self.prob_calculator_multispecies.prob_calculator_arr[idx_species].max_prob_first_particle)
            if r < self.prob_calculator_multispecies.prob_calculator_arr[idx_species].probs_first_particle[idx_particle]:
                # Accept
                self.idx_first_particle = idx_particle
                self.idx_species_particles = idx_species
                self.species_particles = self.prob_calculator_multispecies.species_arr[idx_species]
                self._logger.info("Accepted first particle species: " + str(self.species_particles) + " idx: " + str(idx_particle) + " after: " + str(i_try) + " tries")
                return True

        # Getting here means failure
        self._logger.error("Error! Could not sample the first particle after: " + str(i_try) + " tries.")
        return False



    def rejection_sample_second_particle(self, no_tries_max=100, compute_probs=True):
        """Use rejection sampling to sample the second particle

        Args:
        no_tries_max (int): max. no. of tries for rejection sampling
        compute_probs (bool): whether to first call compute_probs_second_particle for the ProbCalculator

        Returns:
        bool: True for success, False for failure
        """

        # Form probabilities
        if compute_probs:
            self.prob_calculator_multispecies.prob_calculator_arr[self.idx_species_particles].compute_un_probs_second_particle(self.idx_first_particle)

        i_try = 0
        self.idx_second_particle = None
        while self.idx_second_particle == None and i_try < no_tries_max:
            i_try += 1

            # Random particle (uniform)
            idx = np.random.randint(self.prob_calculator_multispecies.prob_calculator_arr[self.idx_species_particles].no_idxs_possible_second_particle)

            # Rejection sampling
            r = np.random.uniform(0.0,self.prob_calculator_multispecies.prob_calculator_arr[self.idx_species_particles].max_prob_second_particle)
            if r < self.prob_calculator_multispecies.prob_calculator_arr[self.idx_species_particles].probs_second_particle[idx]:
                # Accept
                self.idx_second_particle = self.prob_calculator_multispecies.prob_calculator_arr[self.idx_species_particles].idxs_possible_second_particle[idx]

                self._logger.info("Accepted second particle species: " + str(self.species_particles) + " idx: " + str(idx) + " after: " + str(i_try) + " tries")

                return True

        # Getting here means failure
        self._logger.error("Error! Could not sample the second particle after: " + str(no_tries_max) + " tries.")
        return False



    def rejection_sample_pair(self, no_tries_max=100, compute_probs_species=True, compute_probs_first_particle=True):
        """Use rejection sampling to sample a pair of particles

        Args:
        no_tries_max (int): max. no. of tries for rejection sampling
        compute_probs_first_particle (bool): whether to first call compute_probs_first_particle for the ProbCalculator

        Returns:
        bool: True for success, False for failure
        """

        # Form probabilities for species
        if compute_probs_species:
            self.prob_calculator_multispecies.compute_species_probs()

        # Form probabilities
        if compute_probs_first_particle:
            for prob_calculator in self.prob_calculator_multispecies.prob_calculator_arr:
                prob_calculator.compute_un_probs_first_particle()

        # Turn off logging temp
        level = self._logger.level
        self._logger.setLevel(logging.CRITICAL)

        i_try = 0
        while i_try < no_tries_max:
            i_try += 1

            success = self.rejection_sample_first_particle(no_tries_max=1,compute_probs_species=False,compute_probs=False)
            if not success:
                continue # try again

            success = self.rejection_sample_second_particle(no_tries_max=1,compute_probs=True)
            if not success:
                continue # try again

            # Set logging back
            self._logger.setLevel(level)

            self._logger.info("Accepted pair particles species: " + str(self.species_particles) + " idxs: " + str(self.idx_first_particle) + " " + str(self.idx_second_particle) + " after: " + str(i_try) + " tries")

            # Done
            return True

        # Getting here means failure
        self._logger.error("Error! Could not sample the two particles after: " + str(no_tries_max) + " tries.")
        return False



    def cdf_sample_first_particle(self,compute_probs_species=True,compute_probs=True):
        """Sample the first particle by directly calculating the CDF via np.random.choice
        Ensures that the probabilities in the ProbCalculator are normalized before proceeding

        Args:
        compute_probs (bool): whether to first call compute_probs_first_particle for the ProbCalculator

        Returns:
        bool: True for success, False for failure
        """

        # Form probabilities for species
        if compute_probs_species:
            self.prob_calculator_multispecies.compute_species_probs()

        # Form probabilities
        if compute_probs:
            for prob_calculator in self.prob_calculator_multispecies.prob_calculator_arr:
                prob_calculator.compute_un_probs_first_particle()

        # Ensure normalized
        for prob_calculator in self.prob_calculator_multispecies.prob_calculator_arr:
            if prob_calculator.are_probs_first_particle_normalized == False:
                prob_calculator.normalize_probs_first_particle()

        # Choose species
        self.idx_species_particles = np.random.choice(range(0,self.prob_calculator_multispecies.no_species), 1, p=self.prob_calculator_multispecies.probs_species)[0]
        self.species_particles = self.prob_calculator_multispecies.species_arr[self.idx_species_particles]

        # Choose particle
        self.idx_first_particle = np.random.choice(range(0,self.prob_calculator_multispecies.prob_calculator_arr[self.idx_species_particles].n), 1, p=self.prob_calculator_multispecies.prob_calculator_arr[self.idx_species_particles].probs_first_particle)[0]

        self._logger.info("CDF sampled first particle species: " + str(self.species_particles) + " idx: " + str(self.idx_first_particle))

        return True



    def cdf_sample_second_particle(self,compute_probs=True):
        """Sample the second particle by directly calculating the CDF via np.random.choice
        Ensures that the probabilities in the ProbCalculator are normalized before proceeding

        Args:
        compute_probs (bool): whether to first call compute_probs_second_particle for the ProbCalculator

        Returns:
        bool: True for success, False for failure
        """

        # Form probabilities
        if compute_probs:
            self.prob_calculator_multispecies.prob_calculator_arr[self.idx_species_particles].compute_un_probs_second_particle(self.idx_first_particle)

        # Ensure normalized
        if self.prob_calculator_multispecies.prob_calculator_arr[self.idx_species_particles].are_probs_second_particle_normalized == False:
            self.prob_calculator_multispecies.prob_calculator_arr[self.idx_species_particles].normalize_probs_second_particle()

        # Choose
        self.idx_second_particle = np.random.choice(self.prob_calculator_multispecies.prob_calculator_arr[self.idx_species_particles].idxs_possible_second_particle, 1, p=self.prob_calculator_multispecies.prob_calculator_arr[self.idx_species_particles].probs_second_particle)[0]

        self._logger.info("CDF sampled second particle species: " + str(self.species_particles) + " idx: " + str(self.idx_second_particle))

        return True



    def cdf_sample_pair(self, compute_probs_species=True, compute_probs_first_particle=True):
        """Sample both particles directly using numpy.random.choice

        Args:
        compute_probs_first_particle (bool): whether to first call compute_probs_first_particle for the ProbCalculator

        Returns:
        bool: True for success, False for failure
        """

        # Form probabilities for species
        if compute_probs_species:
            self.prob_calculator_multispecies.compute_species_probs()

        # Form probabilities
        if compute_probs_first_particle:
            for prob_calculator in self.prob_calculator_multispecies.prob_calculator_arr:
                prob_calculator.compute_un_probs_first_particle()

        # Ensure normalized
        for prob_calculator in self.prob_calculator_multispecies.prob_calculator_arr:
            if prob_calculator.are_probs_first_particle_normalized == False:
                prob_calculator.normalize_probs_first_particle()

        # Turn off logging temp
        level = self._logger.level
        self._logger.setLevel(logging.CRITICAL)

        success = self.cdf_sample_first_particle(compute_probs_species=False, compute_probs=False)
        if not success:
            self._logger.setLevel(level)
            self._logger.error("Error! Could not sample the two particles using cdf_sample_pair.")
            return False

        success = self.cdf_sample_second_particle(compute_probs=True)
        if not success:
            self._logger.setLevel(level)
            self._logger.error("Error! Could not sample the two particles using cdf_sample_pair.")
            return False

        # Set logging back
        self._logger.setLevel(level)
        self._logger.info("CDF sampled pair particle species: " + str(self.species_particles) + " idxs: " + str(self.idx_first_particle) + " " + str(self.idx_second_particle))

        # Done
        return True
