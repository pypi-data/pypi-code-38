# --------------------------------------------------------
# ptcaffe
# Licensed under The MIT License [see LICENSE for details]
# Written by liuyufei and xiaohang 2017
# --------------------------------------------------------

# Changes
# 1. replicate model once by liuyufei
# 2. throw exception infomation during data parallel by liuyufei 2018.08.01

import threading

import torch
import torch.cuda.comm as comm
import torch.nn as nn
from torch.nn.parallel._functions import Broadcast
from torch.nn.parallel.parallel_apply import get_a_var
from torch.nn.parallel.scatter_gather import gather

from ptcaffe.utils.config import cfg
from ptcaffe.utils.logger import logger
from ptcaffe.utils.utils import SafeNetwork


def parallel_apply(modules, inputs, kwargs_tup=None, devices=None):
    """
    A debuggable variant of :func:`nn.parallel.parallel_apply`
    """
    assert len(modules) == len(inputs)
    if kwargs_tup is not None:
        assert len(modules) == len(kwargs_tup)
    else:
        kwargs_tup = ({},) * len(modules)
    if devices is not None:
        assert len(modules) == len(devices)
    else:
        devices = [None] * len(modules)

    lock = threading.Lock()
    results = {}

    grad_enabled = torch.is_grad_enabled()

    def _worker(i, module, input, kwargs, device=None):
        torch.set_grad_enabled(grad_enabled)

        if device is None:
            device = get_a_var(input).get_device()
        try:
            with torch.cuda.device(device):
                output = module(*input, **kwargs)
            with lock:
                results[i] = output
        except Exception as e:
            with lock:
                logger.error('Exception caught in thread {}'.format(threading.current_thread().ident))
                logger.exception(e)
                results[i] = e

    if len(modules) > 1:
        threads = [threading.Thread(target=_worker,
                                    args=(i, module, input, kwargs, device))
                   for i, (module, input, kwargs, device) in
                   enumerate(zip(modules, inputs, kwargs_tup, devices))]

        for thread in threads:
            thread.start()
        for thread in threads:
            thread.join()
    else:
        _worker(0, modules[0], inputs[0], kwargs_tup[0], devices[0])

    outputs = []
    for i in range(len(inputs)):
        output = results[i]
        if isinstance(output, Exception):
            raise output
        outputs.append(output)
    return outputs


class CallbackContext(object):
    pass


def execute_replication_callbacks(modules):
    master_copy = modules[0]
    nr_modules = len(list(master_copy.modules()))
    ctxs = [CallbackContext() for _ in range(nr_modules)]

    for i, module in enumerate(modules):
        for j, m in enumerate(module.modules()):
            if hasattr(m, '__data_parallel_replicate__'):
                m.__data_parallel_replicate__(ctxs[j], i)


class ParallelCaffeNet(nn.Module):
    def __init__(self, module, device_ids=None, data_seperated=True, output_device=None, dim=0):
        super(ParallelCaffeNet, self).__init__()

        if not torch.cuda.is_available():
            self.module = module
            self.device_ids = []
            return

        if device_ids is None:
            device_ids = list(range(torch.cuda.device_count()))
        if output_device is None:
            output_device = device_ids[0]
        self.dim = dim
        self.module = module
        self.module.broadcast_device_ids(device_ids)
        self.device_ids = device_ids
        self.data_seperated = data_seperated
        self.output_device = output_device
        if len(self.device_ids) == 1:
            self.module.cuda(device_ids[0])
        else:
            self.replicas = torch.nn.parallel.replicate(self.module, self.device_ids)
            for replica in self.replicas:
                replica.broadcast_apply('set_network', SafeNetwork(replica))

    def convert2batch(self, label, batch_size, ngpus):
        if ngpus > 1:
            num = label.size(2)
            label = label.expand(ngpus, 1, num, 8).contiguous()
            sub_sz = batch_size / ngpus
            for i in range(ngpus):
                sub_label = label[i, 0, :, 0]
                mask = (sub_label >= i * sub_sz) * (sub_label < (i + 1) * sub_sz)
                sub_label[~mask] = -1
                sub_label[mask] = sub_label[mask] - sub_sz * i
                label[i, 0, :, 0] = sub_label

        return label

    def forward(self, *outside_datas):
        if not self.device_ids:
            return self.module()
        if len(self.device_ids) == 1:
            return self.module()
        if self.data_seperated:
            if len(outside_datas) == 0:
                input = self.module.forward_data()
            else:
                input = outside_datas

            self.update_replicate(self.module, self.replicas, self.device_ids)
            if cfg.SYNCBN:
                execute_replication_callbacks(self.replicas)

            for idx, replica in enumerate(self.replicas):
                replica.broadcast_device_id(self.device_ids[idx])
            inputs = nn.parallel.scatter(input, self.device_ids)
            replicas = self.replicas[:len(inputs)]
            outputs = parallel_apply(replicas, inputs)
        else:
            self.update_replicate(self.module, self.replicas, self.device_ids)
            if cfg.SYNCBN:
                execute_replication_callbacks(self.replicas)
            for idx, replica in enumerate(self.replicas):
                replica.broadcast_device_id(self.device_ids[idx])
            outputs = self.parallel_apply(self.replicas, self.device_ids, 'forward')
        return self.gather(outputs, self.output_device)

    def forward_backward(self):
        if not self.device_ids:
            return self.module()
        if len(self.device_ids) == 1:
            return self.module()
        self.update_replicate(self.module, self.replicas, self.device_ids)
        outputs = self.parallel_apply(self.replicas, self.device_ids, 'forward_backward')
        return self.gather(outputs, self.output_device)

    def parallel_apply(self, modules, devices, func='forward'):
        lock = threading.Lock()
        results = {}

        def _worker(i, module, results, lock, device):
            try:
                with torch.cuda.device(device):
                    with lock:
                        inputs = module.forward_data()
                    if func == 'forward':
                        output = module(*inputs)
                    elif func == 'forward_backward':
                        output = module.forward_backward(*inputs)
                with lock:
                    results[i] = output
            except Exception as e:
                with lock:
                    results[i] = e

        if len(modules) > 1:
            threads = [threading.Thread(target=_worker,
                                        args=(i, module, results, lock, device),
                                        )
                       for i, (module, device) in
                       enumerate(zip(modules, devices))]

            for thread in threads:
                thread.start()
            for thread in threads:
                thread.join()
        else:
            _worker(0, modules[0], results, lock, devices[0])

        outputs = []
        for i in range(len(modules)):
            output = results[i]
            if isinstance(output, Exception):
                raise output
            outputs.append(output)
        return outputs

    def gather(self, outputs, output_device):
        return gather(outputs, output_device, dim=self.dim)

    def save_caffemodel(self, deploy_prototxt, caffemodel):
        return self.module.save_caffemodel(deploy_prototxt, caffemodel)

    def print_forward_time(self):
        return self.module.print_forward_time()

    def save_model(self, modelname):
        return self.module.save_model(modelname)

    def load_model(self, modelname):
        return self.module.load_model(modelname)

    def load_caffemodel(self, modelname):
        return self.module.load_caffemodel(modelname)

    def get_parameters(self, base_lr, weight_decay):
        return self.module.get_parameters(base_lr, weight_decay)

    def set_automatic_outputs(self):
        if len(self.device_ids) > 1:
            for replica in self.replicas:
                replica.set_automatic_outputs()
        return self.module.set_automatic_outputs()

    def get_loss_weights(self):
        return self.module.get_loss_weights()

    def set_selector(self, selector):
        if len(self.device_ids) > 1:
            for replica in self.replicas:
                replica.set_selector(selector)
        return self.module.set_selector(selector)

    def set_data_layer_gpu(self, device):
        return self.module.set_data_layer_gpu(device)

    def has_data_layer(self, phase=''):
        return self.module.has_data_layer(phase=phase)

    @property
    def selector(self):
        return self.module.selector

    @property
    def eval_outputs(self):
        return self.module.eval_outputs

    @property
    def train_outputs(self):
        return self.module.train_outputs

    @property
    def train_batch_size(self):
        return self.module.train_batch_size

    def eval(self):
        super(ParallelCaffeNet, self).eval()
        for replica in self.replicas:
            replica.eval()

    def train(self, train=True):
        super(ParallelCaffeNet, self).train(train)
        for replica in self.replicas:
            replica.train(train)

    def broadcast_apply(self, func_name, *args, **kwargs):
        for replica in self.replicas:
            replica.broadcast_apply(func_name, *args, **kwargs)

    def get_metrics(self):
        return self.replicas[0].get_metrics()

    def reset_metrics(self):
        self.replicas[0].reset_metrics()

    @staticmethod
    def update_replicate(network, replicates, devices, detach=False):
        devices = tuple(devices)
        num_replicas = len(devices)

        # distribute parameters & buffers
        params = list(network.parameters())
        param_indices = {param: idx for idx, param in enumerate(params)}
        param_copies = Broadcast.apply(devices, *params)
        if len(params) > 0:
            param_copies = [param_copies[i:i + len(params)] for i in range(0, len(param_copies), len(params))]
        
        # TODO deprecate legacy API
        if hasattr(network, '_all_buffers'):
            buffers = list(network._all_buffers())
        else:
            buffers = list(network.buffers())
        buffer_indices = {buf: idx for idx, buf in enumerate(buffers)}
        buffer_copies = comm.broadcast_coalesced(buffers, devices)

        module_copies = [list(replica.modules()) for replica in replicates]

        modules = list(network.modules())
        for i, module in enumerate(modules):
            for key, param in module._parameters.items():
                if param is None:
                    for j in range(num_replicas):
                        replica = module_copies[j][i]
                        replica._parameters[key] = None
                else:
                    param_idx = param_indices[param]
                    for j in range(num_replicas):
                        replica = module_copies[j][i]
                        replica._parameters[key] = param_copies[j][param_idx].detach() \
                            if detach else param_copies[j][param_idx]
            for key, buf in module._buffers.items():
                if buf is None:
                    for j in range(num_replicas):
                        replica = module_copies[j][i]
                        replica._buffers[key] = None
                else:
                    buffer_idx = buffer_indices[buf]
                    for j in range(num_replicas):
                        replica = module_copies[j][i]
                        replica._buffers[key] = buffer_copies[j][buffer_idx]
