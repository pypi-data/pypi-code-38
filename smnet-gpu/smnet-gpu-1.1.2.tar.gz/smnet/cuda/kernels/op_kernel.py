# --------------------------------------------------------
# SMNet cuda kernel
# Licensed under The MIT License [see LICENSE for details]
# Copyright 2019 smarsu. All Rights Reserved.
# --------------------------------------------------------

import pycuda.driver as cuda
import pycuda.autoinit
from pycuda.compiler import SourceModule

from ..cuda import *


class OpKernel(object):
    def __init__(self):
        pass

    
    @property
    def cuda_num_threads(self):
        return 1024
        #return 512


    def get_cuda_num_blocks(self, size=None):
        if size is None:
            size = self.size
        return (size + self.cuda_num_threads - 1) // self.cuda_num_threads

    
    def get_cuda_num_blocks_arr(self):
        return [(size + self.cuda_num_threads - 1) // self.cuda_num_threads for size in self.sizes]
