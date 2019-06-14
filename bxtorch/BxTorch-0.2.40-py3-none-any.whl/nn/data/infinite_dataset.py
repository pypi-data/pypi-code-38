#
#  nn/data/infinite_dataset.py
#  bxtorch
#
#  Created by Oliver Borchert on May 19, 2019.
#  Copyright (c) 2019 Oliver Borchert. All rights reserved.
#  

from abc import ABC
import torch.utils.data as torch_data
from .infinite_loader import InfiniteDataLoader

class InfiniteDataset(ABC):
    """
    The infinite dataset works similarly to PyTorch's Dataset. However, instead
    of having a fixed size, it yields infinitely many items via the ``next()``
    method.
    """

    # MARK: Initialization
    def __init__(self, generator):
        """
        Initializes a new infinite dataset.

        Parameters:
        -----------
        - generator: generator
            The generator yielding new items.
        """
        self.generator = generator

    # MARK: Instance Methods
    def loader(self, **kwargs):
        """
        Returns a data loader for this dataset.

        Parameters:
        -----------
        - kwargs: keyword arguments
            Paramaters passed directly to the DataLoader.

        Returns:
        --------
        - bxtorch.nn.InfiniteDataLoader
            The data loader with the specified attributes.
        """
        if hasattr(self, 'collate_fn'):
            kwargs['collate_fn'] = self.collate_fn
        return InfiniteDataLoader(self, **kwargs)

    # MARK: Private Methods
    def _transform(self, item):
        """
        Transforms the item retrieved from a generator to an object picked up
        by the data loader.
        The default implementation just returns the item as is.

        Parameters:
        -----------
        - item: generator item
            The item provided by the dataset's generator.

        Returns:
        --------
        - object
            The object returned for the data loader.
        """
        return item

    # MARK: Special Methods
    def __iter__(self):
        return self

    def __next__(self):
        return self._transform(next(self.generator))
