from __future__ import division, print_function

import torchvision.transforms as T
from ptcaffe.utils.utils import make_list

__all__ = ['Tensor_Normalize', 'Tensor_Unsqueeze']

class Tensor_Normalize(T.Normalize):
    def __init__(self, mean, std):
        mean = make_list(mean)
        std = make_list(std)
        super(Tensor_Normalize, self).__init__(mean, std)

class Tensor_Unsqueeze(object):
    def __init__(self, dim):
        self.dim = dim

    def __call__(self, input):
        output = input.unsqueeze(dim=self.dim)
        return output
