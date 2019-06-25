from __future__ import division, print_function

import torch.nn as nn
from ptcaffe.utils.utils import parse_types
import warnings
import copy

__all__ = ["Embedding", "EmbeddingBag"]

WARNING = """
Keep in mind that only a limited number of optimizers support sparse gradients: currently it's optim.SGD (CUDA and CPU), optim.SparseAdam (CUDA and CPU) and optim.Adagrad (CPU)
@from pytorch 1.0
"""
class PtcaffeSparseLayerWarning(UserWarning):
    pass

class Embedding(nn.Embedding):
    def __init__(self, layer, input_shape):
        # PARAM:
        # num_embeddings,
        # embedding_dim,
        # padding_idx=None,
        # max_norm=None,
        # norm_type=2.0,
        # scale_grad_by_freq=False,
        # sparse=False,
        # _weight=None
        warnings.warn(WARNING, PtcaffeSparseLayerWarning)
        kwargs = parse_types(layer['embedding_param'])
        super(Embedding, self).__init__(**kwargs)

    def forward_shape(self, input_shape): # ... -> ... x self.embedding_dim
        input_shape = copy.copy(input_shape)
        input_shape += [self.embedding_dim]
        return input_shape

class EmbeddingBag(nn.EmbeddingBag):
    def __init__(self, layer, input_shape):
        # PARAM:
        # num_embeddings,
        # embedding_dim,
        # max_norm=None,
        # norm_type=2.0,
        # scale_grad_by_freq=False,
        # mode='mean',
        # sparse=False
        warnings.warn(WARNING, PtcaffeSparseLayerWarning)
        kwargs = parse_types(layer['embeddingbag_param'])
        super(EmbeddingBag, self).__init__(**kwargs)

    def forward_shape(self, input_shape): # B -> B x self.embedding_dim
        input_shape = copy.copy(input_shape)
        input_shape += [self.embedding_dim]
        return input_shape
