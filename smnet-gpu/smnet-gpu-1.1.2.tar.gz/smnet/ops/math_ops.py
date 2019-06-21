# --------------------------------------------------------
# SMNet math ops
# Licensed under The MIT License [see LICENSE for details]
# Copyright 2019 smarsu. All Rights Reserved.
# --------------------------------------------------------

"""Basic mathematical operations based on numpy.

Because we need high performance calculations, we don't do error checking.
"""

import numpy as np

# Set eps to avoid overflow.
EPS = 1e6
neg_EPS = -EPS
inv_EPS = 1 / EPS
neg_inv_EPS = -1 / EPS


def sqrt(a):
    """Compute sqrt"""
    return np.sqrt(a)


def l2_loss(a):
    """Compute the l2 loss of a.
    
    output = (a**2) / 2
    """
    a = np.clip(a, neg_EPS, EPS)
    return .5 * np.square(a)
