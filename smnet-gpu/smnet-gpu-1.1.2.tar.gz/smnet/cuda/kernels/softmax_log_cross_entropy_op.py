# --------------------------------------------------------
# SMNet conv2d cuda kernel
# Licensed under The MIT License [see LICENSE for details]
# Copyright 2019 smarsu. All Rights Reserved.
# --------------------------------------------------------

from .op_kernel import *

kernel = SourceModule("""
__global__ void softmax_log_cross_entropy(int *n, float *labels, float *logits) {
    int idx = blockIdx.x * blockDim.x + threadIdx.x;
    if (idx < *n) {
        //__expf
    }
}
""")
