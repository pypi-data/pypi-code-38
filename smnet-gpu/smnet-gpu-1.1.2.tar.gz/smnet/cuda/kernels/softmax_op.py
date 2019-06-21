# --------------------------------------------------------
# SMNet conv2d cuda kernel
# Licensed under The MIT License [see LICENSE for details]
# Copyright 2019 smarsu. All Rights Reserved.
# --------------------------------------------------------

from .op_kernel import *

kernel = SourceModule("""
__global__ void softmax(int *n, float *input, float *output) {
    int idx = blockIdx.x * blockDim.x + threadIdx.x;
    if (idx < *n) {
        
    }
}
""")