# --------------------------------------------------------
# ptcaffe
# Licensed under The MIT License [see LICENSE for details]
# Written by liuyufei
# --------------------------------------------------------

# encoding: UTF-8


"""
Painless communication layers with autograd support
"""

from __future__ import division, print_function
import copy
import threading
import torch.nn
from torch.nn.parallel._functions import Gather, Scatter, Broadcast, ReduceAddCoalesced

from ptcaffe.utils.utils import ThreadsSync

__all__ = ['BroadcastLayer', 'GatherLayer', 'AllGatherLayer', 'ScatterLayer', 'ReduceAddLayer', 'AllReduceAddLayer']


class CommunicationLayer(torch.nn.Module):
    def __init__(self, layer, input_shape):
        super(CommunicationLayer, self).__init__()
        self.rank = -1
        self.ranks = []
        self.inputs = dict()
        self.register_lock = threading.Lock()
        self.return_lock = threading.Lock()
        self.sync_before = ThreadsSync()
        self.sync_after = ThreadsSync()

        # parse layer_param
        param = layer.get('comm_param', {})
        self.dim = int(param.get('dim', 0))
        self.master_device = int(param.get('master_device', 0))

    def set_devices(self, device_ids):
        self.ranks = copy.copy(device_ids)

    def set_device(self, device):
        self.rank = device

    def forward_shape(self, input_shape):
        return copy.copy(input_shape)


class BroadcastLayer(CommunicationLayer):
    def forward(self, *tensors):
        if self.rank == self.master_device:
            for rank in self.ranks:
                self.inputs[rank] = []
            for tensor in tensors:
                if isinstance(tensor, (tuple, list)):
                    tensor = tensor[0]
                for replica, rank in zip(Broadcast.apply(self.ranks, tensor), self.ranks):
                    self.inputs[rank].append(replica)
        self.sync_after.wait_synchronize(len(self.ranks))
        with self.return_lock:
            tensors = self.inputs.pop(self.rank)
        return tuple(tensors)


class GatherLayer(CommunicationLayer):
    def forward_shape(self, input_shape):
        output_shape = copy.copy(input_shape)
        output_shape[self.dim] *= len(self.ranks)
        return output_shape

    def forward(self, *tensors):
        with self.register_lock:
            self.inputs[self.rank] = list(tensors)
        self.sync_before.wait_synchronize(len(self.ranks))
        if self.rank == self.master_device:
            transposed = list(zip(*[self.inputs[r] for r in self.ranks]))
            for i, tensors in enumerate(transposed):
                self.inputs[self.master_device][i] = Gather.apply(self.master_device, self.dim, *tensors)
        self.sync_after.wait_synchronize(len(self.ranks))
        with self.return_lock:
            tensors = self.inputs.pop(self.rank)
        return tuple(tensors)


class AllGatherLayer(CommunicationLayer):
    def forward_shape(self, input_shape):
        output_shape = copy.copy(input_shape)
        output_shape[self.dim] *= len(self.ranks)
        return output_shape

    def forward(self, *tensors):
        with self.register_lock:
            self.inputs[self.rank] = list(tensors)
        self.sync_before.wait_synchronize(len(self.ranks))
        if self.rank == self.master_device:
            transposed = list(zip(*[self.inputs[r] for r in self.ranks]))
            for i, tensors in enumerate(transposed):
                tensor = Gather.apply(self.master_device, self.dim, *tensors)
                for replica, rank in zip(Broadcast.apply(self.ranks, tensor), self.ranks):
                    self.inputs[rank][i] = replica
        self.sync_after.wait_synchronize(len(self.ranks))
        with self.return_lock:
            tensors = self.inputs.pop(self.rank)
        return tuple(tensors)


class ScatterLayer(CommunicationLayer):
    def forward_shape(self, input_shape):
        output_shape = copy.copy(input_shape)
        output_shape[self.dim] //= max(1, len(self.ranks))
        return output_shape

    def forward(self, *tensors):
        with self.register_lock:
            self.inputs[self.rank] = list(tensors)
        self.sync_before.wait_synchronize(len(self.ranks))
        if self.rank == self.master_device:
            for i, tensor in enumerate(tensors):
                if isinstance(tensor, (tuple, list)):
                    tensor = tensor[0]
                for scatter, rank in zip(Scatter.apply(self.ranks, None, self.dim, tensor), self.ranks):
                    self.inputs[rank][i] = scatter
        self.sync_after.wait_synchronize(len(self.ranks))
        with self.return_lock:
            tensors = self.inputs.pop(self.rank)
        return tuple(tensors)


class ReduceAddLayer(CommunicationLayer):
    def forward(self, *tensors):
        with self.register_lock:
            self.inputs[self.rank] = list(tensors)
        self.sync_before.wait_synchronize(len(self.ranks))
        if self.rank == self.master_device:
            transposed = list(zip(*[self.inputs[r] for r in self.ranks]))
            for i, tensors in enumerate(transposed):
                reduced = ReduceAddCoalesced.apply(self.master_device, 1, *tensors)
                self.inputs[self.master_device][i] = reduced
        self.sync_after.wait_synchronize(len(self.ranks))
        with self.return_lock:
            tensors = self.inputs.pop(self.rank)
        return tuple(tensors)


class AllReduceAddLayer(CommunicationLayer):
    def forward(self, *tensors):
        with self.register_lock:
            self.inputs[self.rank] = list(tensors)
        self.sync_before.wait_synchronize(len(self.ranks))
        if self.rank == self.master_device:
            transposed = list(zip(*[self.inputs[r] for r in self.ranks]))
            for i, tensors in enumerate(transposed):
                reduced = ReduceAddCoalesced.apply(self.master_device, 1, *tensors)
                for replica, rank in zip(Broadcast.apply(self.ranks, reduced), self.ranks):
                    self.inputs[rank][i] = replica
        self.sync_after.wait_synchronize(len(self.ranks))
        with self.return_lock:
            tensors = self.inputs.pop(self.rank)
        return tuple(tensors)
