#
#  nn/data/dataset.py
#  bxtorch
#
#  Created by Oliver Borchert on May 21, 2019.
#  Copyright (c) 2019 Oliver Borchert. All rights reserved.
#  

import math
import numpy as np
import torch.utils.data as torch_data

class Dataset(torch_data.Dataset):
    """
    Subclass of a simple PyTorch dataset which includes an additional
    ``loader`` function such that subclasses can directly initialize data
    loaders. If the dataset defines a function named ``collate_fn``, it is
    used instead of the default collate function.
    """

    def loader(self, **kwargs):
        """
        Returns a data loader for this dataset.

        Parameters:
        -----------
        - kwargs: keyword arguments
            Paramaters passed directly to the DataLoader.

        Returns:
        --------
        - torch.utils.data.DataLoader
            The data loader with the specified attributes.
        """
        if hasattr(self, 'collate_fn'):
            kwargs['collate_fn'] = self.collate_fn
        return torch_data.DataLoader(self, **kwargs)

    def random_split(self, *sizes, seed=None):
        """
        Splits the dataset randomly into multiple subsets.

        Parameters:
        -----------
        - sizes: variadic argument of float
            The sizes of the splits, given as fraction of the size of the
            dataset. Hence, the sizes must sum to 1.
        - seed: int, default: None
            If given, uses the specified seed to sample the indices for each
            subset.

        Returns:
        --------
        - list of bxtorch.nn.Subset
            The random splits of this dataset.
        """
        assert math.isclose(sum(sizes), 1), \
            "Sizes do not sum to 1."

        randomizer = np.random.RandomState(seed)
        
        # Get subset sizes
        nums = []
        for i, size in enumerate(sizes):
            if i == len(sizes) - 1:
                nums.append(len(self) - sum(nums))
            else:
                nums.append(int(np.round(size * len(self))))

        # Get subset indices
        indices = randomizer.permutation(len(self))
        index_choices = []
        c = 0
        for num in nums:
            index_choices.append(indices[c:c+num])
            c += num

        # Generate subsets
        return [
            Subset(
                self, indices, 
                getattr(self, 'collate_fn', None)
            ) for indices in index_choices
        ]



class Subset(torch_data.Subset):
    """
    Subclass of a PyTorch dataset. Enables preserving the collate function of
    a custom dataset easily. Usually, you don't need to use the class directly.
    """

    # MARK: Initialization
    def __init__(self, dataset, indices, collate_fn=None):
        """
        Initializes a new subset of a dataset.

        Parameters:
        -----------
        - dataset: torch.utils.data.Dataset
            The underlying dataset.
        - indices: iterable of int
            The indices of the underlying dataset that this subset contains.
        - collate_fn: callable, default: None
            A collate function for use in a data loader. Primarily used
            internally.
        """
        super().__init__(dataset, indices)
        self._collate_fn = collate_fn

    # MARK: Instance Methods
    def loader(self, **kwargs):
        """
        Returns a data loader for this subset.

        Parameters:
        -----------
        - kwargs: keyword arguments
            Paramaters passed directly to the DataLoader.

        Returns:
        --------
        - torch.utils.data.DataLoader
            The data loader with the specified attributes.
        """
        if self._collate_fn is not None:
            kwargs['collate_fn'] = self._collate_fn
        return torch_data.DataLoader(self, **kwargs)
