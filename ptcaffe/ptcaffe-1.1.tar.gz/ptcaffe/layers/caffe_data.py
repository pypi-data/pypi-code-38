# --------------------------------------------------------
# PyTorchCaffe
# Licensed under The MIT License [see LICENSE for details]
# Written by xiaohang
# --------------------------------------------------------

from __future__ import division, print_function

import abc
import copy
import os
import threading
from collections import OrderedDict

import torch
import torch.multiprocessing as mp
import torch.nn as nn

from ptcaffe.utils.utils import make_list


# ----------- CaffeData-----------


class CaffeData(nn.Module):
    """ Data layer which use caffe engine
    layer {
      name: "mnist"
      type: "Data"
      top: "data"
      top: "label"
      include {
        phase: TRAIN
      }
      transform_param {
        scale: 0.00390625
      }
      data_param {
        source: "mnist_train_lmdb"
        batch_size: 64
        backend: LMDB
      }
    }

    # For the data above, you can display data as below
    layer {
        name: "display"
        type: "VisdomImage"
        bottom: "data"
        visdom_param {
            interval: 1
            scale: 0.00390625
        }
        server_param {
            server: "http://192.168.1.100"
        }
    }
    # ptcaffe run --model view.prototxt --iterations 1000
    """

    def __init__(self, layer):
        os.environ['GLOG_minloglevel'] = '2'
        from ..utils.prototxt import save_prototxt
        import caffe
        import random

        super(CaffeData, self).__init__()
        self.data_load_debug = False
        self.data_save_debug = False
        self.layer = copy.deepcopy(layer)
        self.device = -1
        net_info = OrderedDict()
        props = OrderedDict()
        props['name'] = 'temp network'
        net_info['props'] = props
        net_info['layers'] = [layer]

        rand_val = random.random()
        protofile = '.temp_data%f.prototxt' % rand_val
        save_prototxt(net_info, protofile)
        weightfile = '.temp_data%f.caffemodel' % rand_val
        open(weightfile, 'w').close()
        self.phase = 'TEST'
        if 'include' in self.layer and 'phase' in self.layer['include'] and self.layer['include']['phase'] == 'TRAIN':
            self.net = caffe.Net(protofile, weightfile, caffe.TRAIN)
            self.phase = 'TRAIN'
        else:
            self.net = caffe.Net(protofile, weightfile, caffe.TEST)
            self.phase = 'TEST'
        os.remove(protofile)
        os.remove(weightfile)

        tname = self.layer['top']
        self.tnames = tname if isinstance(tname, list) else [tname]

        # debug
        self.iter_id = 0

        # lock
        self.lock = threading.Lock()

        self.saved_inputs = None

    def __repr__(self):
        return 'CaffeData()'

    def get_batch_size(self):
        if self.saved_inputs is None:
            self.saved_inputs = self.forward()

        assert(len(self.saved_inputs) >= 1)
        return self.saved_inputs[0].shape[0]

    @abc.abstractmethod
    def get_batch_num(self):
        pass

    def forward_shape(self):
        if self.saved_inputs is None:
            self.saved_inputs = self.forward()

        output_shapes = [list(data.size()) for data in self.saved_inputs]
        if len(output_shapes) == 0:
            return
        elif len(output_shapes) == 1:
            return output_shapes[0]
        else:
            return output_shapes

    def set_device(self, device):
        if device is None:
            self.device = 0
        else:
            self.device = device

    def forward(self):
        if self.saved_inputs is not None:
            saved_inputs = self.saved_inputs
            if self.device != -1:
                saved_inputs = tuple([input.cuda(self.device) for input in saved_inputs])
            self.saved_inputs = None
            return saved_inputs

        self.lock.acquire()
        self.net.forward()
        self.lock.release()

        outputs = []
        for idx, name in enumerate(self.tnames):
            data = self.net.blobs[name].data
            data = torch.from_numpy(data)
            if self.phase == 'TRAIN':
                if self.device != -1:
                    outputs.append(data.cuda(self.device))
                else:
                    outputs.append(data)
            else:
                if self.device != -1:
                    outputs.append(data.cuda(self.device))
                else:
                    outputs.append(data)
        return tuple(outputs)


# ----------- MultiThreadsCaffeData-----------
class CaffeDataSet(object):
    def __init__(self, layer):
        self.layer = copy.deepcopy(layer)

        self.phase = 'TEST'
        include_param = layer.get('include', OrderedDict())
        self.phase = include_param.get('phase', 'TEST')
        self.tnames = make_list(layer['top'])

        self.net = None  # self.create_net()

    def create_net(self):
        os.environ['GLOG_minloglevel'] = '2'
        from ptcaffe.utils.prototxt import save_prototxt
        import caffe
        import random
        caffe.set_mode_cpu()

        net_info = OrderedDict()
        props = OrderedDict()
        props['name'] = 'temp_network'
        net_info['props'] = props
        net_info['layers'] = [self.layer]

        rand_val = random.random()
        protofile = '.temp_data%f.prototxt' % rand_val
        save_prototxt(net_info, protofile)

        weightfile = '.tmp_data%f.caffemodel' % rand_val
        open(weightfile, 'w').close()

        if self.phase == 'TRAIN':
            net = caffe.Net(protofile, weightfile, caffe.TRAIN)
        else:
            net = caffe.Net(protofile, weightfile, caffe.TEST)
        caffe.set_mode_gpu()
        os.remove(protofile)
        os.remove(weightfile)
        return net

    def __call__(self):
        if self.net is None:
            self.net = self.create_net()
        self.net.forward()
        outputs = [torch.from_numpy(self.net.blobs[name].data) for name in self.tnames]
        return tuple(outputs)


class CaffeWorkerThread(threading.Thread):
    def __init__(self, dataset, queue):
        super(CaffeWorkerThread, self).__init__()
        self.dataset = dataset
        self.queue = queue

    def run(self):
        while True:
            outputs = self.dataset()
            self.queue.put(outputs)


class CaffeWorkerProcess(mp.Process):
    def __init__(self, dataset, queue):
        super(CaffeWorkerProcess, self).__init__()
        self.dataset = dataset
        self.queue = queue

    def run(self):
        while True:
            outputs = self.dataset()
            print('outputs to queue')
            self.queue.put(outputs)


class CaffeDataLoader(object):
    def __init__(self, dataset, num_workers):
        from multiprocessing import Queue as MP_Queue
        self.queue = MP_Queue(maxsize=20)
        self.workers = [CaffeWorkerProcess(dataset, self.queue) for _ in range(num_workers)]
        for worker in self.workers:
            worker.start()

    def next(self):
        outputs = self.queue.get()
        return outputs


class CaffeData_MT(nn.Module):
    def __init__(self, layer):
        super(CaffeData_MT, self).__init__()
        self.layer = layer
        self.device = -1
        self.phase = 'TEST'
        if 'include' in layer and 'phase' in layer['include']:
            self.phase = layer['include']['phase']
        self.data_loader = self.create_data_loader(layer)
        self.batch_num = self.get_batch_num()
        self.batch_size = self.get_batch_size()

        self.saved_inputs = None

    def __repr__(self):
        return 'CaffeData_MT()'

    def get_batch_num(self):
        return 1e4

    def set_device(self, device):
        self.device = device

    def get_batch_size(self):
        if self.saved_inputs is None:
            self.saved_inputs = self.forward()

        assert(len(self.saved_inputs) >= 1)
        return self.saved_inputs[0].shape[0]

    def create_data_loader(self, layer):
        data_loader_param = layer.get('data_loader_param', OrderedDict())
        num_workers = int(data_loader_param.get('num_workers', 1))
        layer = copy.deepcopy(layer)
        if 'data_loader_param' in layer:
            del layer['data_loader_param']

        dataset = CaffeDataSet(layer)
        #kwargs = {'num_workers': num_workers, 'pin_memory': True}
        #data_loader = torch.utils.data.DataLoader(dataset, batch_size=1, shuffle=False, **kwargs)
        data_loader = CaffeDataLoader(dataset, num_workers=1)
        return data_loader

    def forward(self):
        if self.saved_inputs is not None:
            saved_inputs = self.saved_inputs
            if self.device != -1:
                saved_inputs = tuple([input.cuda(self.device) for input in saved_inputs])
            self.saved_inputs = None
            return saved_inputs

        fetch_datas = self.data_loader.next()

        if self.device != -1:
            outputs = [data.cuda(self.device) for data in fetch_datas]
        else:
            outputs = [data for data in fetch_datas]
        return tuple(outputs)

    def forward_shape(self):
        if self.saved_inputs is None:
            self.saved_inputs = self.forward()

        output_shapes = [list(data.size()) for data in self.saved_inputs]

        if len(output_shapes) == 1:
            return output_shapes[0]
        else:
            return output_shapes
