# --------------------------------------------------------
# SMNet test
# Licensed under The MIT License [see LICENSE for details]
# Copyright 2019 smarsu. All Rights Reserved.
# --------------------------------------------------------

import os
import time
#import smnet as sm
import tensorflow as tf
import numpy as np
from test_base import TestBase

np.random.seed(196)


def gt_matmul(a, b):
    a = tf.constant(a)
    b = tf.Variable(b)
    y = tf.matmul(a, b)
    return y


def sm_matmul(a, b, sm=None):
    a = sm.Tensor(a)
    b = sm.Variable(b)
    y = sm.nn.matmul(a, b)
    return y


def to_inputs(n, k, m, **params):
    border = params['border']
    a = np.random.uniform(-border, border, (n, k))
    b = np.random.uniform(-border, border, (k, m))

    return (a, b)


if __name__ == '__main__':
    """
    matrix1: [n, k]
    matrix2: [k, m]
    """
    testbase = TestBase('Matmul', gt_matmul, sm_matmul, to_inputs)

    # test1 
    n = 32
    k = 4096
    m = 4096
    base_device = 'cpu'
    smnet_device = 'cpu'

    testbase.test_case(n=n, k=k, m=m, base_device=base_device, smnet_device=smnet_device)
