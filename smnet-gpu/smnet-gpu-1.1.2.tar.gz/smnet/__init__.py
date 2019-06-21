# --------------------------------------------------------
# SMNet
# Licensed under The MIT License [see LICENSE for details]
# Copyright 2019 smarsu. All Rights Reserved.
# --------------------------------------------------------

"""Bring in all of the public SMNet interface into this module."""

from .blob import Variable, Tensor
from . import layer as nn
from .net import Net
from . import net

print('Hello SMNet!\n'
      'Env:\n'
      '    use_cuda: {};'
      '  profiling: {}'.format(net.use_cuda,
                               net.profiling))

# The operates of current graph.
# THESE OPS ARE DEPRECATED, use `Session` to get current graph.
forward = net.graph.forward
optimize = net.graph.optimize
save = net.graph.save
restore = net.graph.restore


def reset_default_graph():
    """Reset default graph.

    New a graph and reset the global default graph to it.
    The layers created later will be added to this graph.
    """
    net.Net()


def Session():
    """Get current graph.

    Args:
        graph: Current graph.
    """
    return net.graph


from .layers import cnn, rnn
from .ops import param_op  # utils, e.g. xavier initialization method...
from .third_party import nvarray
