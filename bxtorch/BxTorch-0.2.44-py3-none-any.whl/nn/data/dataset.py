#
#  nn/data/dataset.py
#  bxtorch
#
#  Created by Oliver Borchert on May 21, 2019.
#  Copyright (c) 2019 Oliver Borchert. All rights reserved.
#  

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
