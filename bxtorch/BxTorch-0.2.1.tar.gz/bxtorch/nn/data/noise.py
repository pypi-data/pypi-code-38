#
#  nn/data/noise.py
#  bxtorch
#
#  Created by Oliver Borchert on May 19, 2019.
#  Copyright (c) 2019 Oliver Borchert. All rights reserved.
#  

from .infinite_dataset import InfiniteDataset
import bxtorch.nn.functional as X

class NoiseDataset(InfiniteDataset):
    """
    Infinite dataset for generating noise from a given probability distribution.
    Should be used with Generative Adversarial Networks.
    """

    # MARK: Initialization
    def __init__(self, noise_type, dimension):
        """
        Initializes a new dataset with the given noise type.

        Parameters:
        -----------
        - noise_type: str
            The noise type to use.
        - dimension: int
            The dimension of the noise to generate.
        """
        super().__init__(self._generator_func(noise_type, dimension))

    # MARK: Generator
    def _generator_func(self, noise_type, dimension):
        while True:
            yield X.generate_noise([dimension], noise_type)
