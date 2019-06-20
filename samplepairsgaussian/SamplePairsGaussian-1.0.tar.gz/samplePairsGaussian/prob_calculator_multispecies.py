from .prob_calculator import *

class ProbCalculatorMultiSpecies:

    def __init__(self, prob_calculator_arr, species_arr):
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

        # Length
        if len(species_arr) != len(prob_calculator_arr):
            self._logger.error("Error: length of species array = " + str(len(species_arr)) + " does not match the probabilities: " + str(len(prob_calculator_arr)) + "; Quitting.")
            sys.exit(0)

        # vars
        self.no_species = len(species_arr)
        self.prob_calculator_arr = prob_calculator_arr
        self.species_arr = species_arr

        # compute species probabilities
        self.compute_species_probs()

    def set_logging_level(self, level):
        """Sets the logging level
        Args:
        level (logging): logging level
        """
        self._logger.setLevel(level)

    def compute_species_probs(self):
        """compute probabilities for the different species.
        """

        self.probs_species = np.zeros(self.no_species)
        for i in range(0,self.no_species):
            self.probs_species[i] = self.prob_calculator_arr[i].n
        self.n_total = np.sum(self.probs_species)
        self.probs_species /= self.n_total
