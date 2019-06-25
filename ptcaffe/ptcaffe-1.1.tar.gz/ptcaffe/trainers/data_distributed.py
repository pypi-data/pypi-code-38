# --------------------------------------------------------
# ptcaffe
# Licensed under The MIT License [see LICENSE for details]
# Written by xiaohang and Li Kun 2018.6
# --------------------------------------------------------

import torch.nn as nn


class DistributedCaffeNet(nn.parallel.DistributedDataParallel):
    def __init__(self, module, device_ids=None, output_device=None, dim=0, boradcast_buffers=True, data_seperated=True):
        super(DistributedCaffeNet, self).__init__(module, device_ids, output_device, dim, boradcast_buffers)
        self.module.broadcast_device_ids(self.device_ids)
        for idx, replica in enumerate(self._module_copies):
            replica.broadcast_device_id(self.device_ids[idx])

    def forward(self):
        self.need_reduction = True
        input = self.module.forward_data()
        inputs = nn.parallel.scatter(input, self.device_ids)
        self._sync_params()
        if len(self.device_ids) == 1:
            return self.module(*inputs[0])

        outputs = self.parallel_apply(self._module_copies[:len(inputs)], inputs, [{}] * len(inputs))
        return self.gather(outputs, self.output_device)

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
        return self.module.set_automatic_outputs()

    def get_loss_weights(self):
        return self.module.get_loss_weights()

    def set_selector(self, selector):
        return self.module.set_selector(selector)

    def set_data_layer_gpu(self, device):
        return self.module.set_data_layer_gpu(device)

    def has_data_layer(self, phase=''):
        return self.module.has_data_layer(phase=phase)

    @property
    def eval_outputs(self):
        return self.module.eval_outputs

    @property
    def train_outputs(self):
        return self.module.train_outputs

    @property
    def train_batch_size(self):
        return self.module.train_batch_size
