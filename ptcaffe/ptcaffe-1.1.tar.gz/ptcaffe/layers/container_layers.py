from __future__ import division, print_function

import torch
import torch.nn as nn
import torchvision.models as models
from collections import OrderedDict
from ptcaffe.utils.utils import make_list


class TorchVisionModel(nn.Module):
    def __init__(self, layer, input_shape):
        super(TorchVisionModel, self).__init__()
        model_param = layer.get('model_param', OrderedDict())
        model_name = model_param['model_name']
        pretrained = (model_param.get('pretrained', 'false') == 'true')
        self.num_classes = int(model_param.get('num_classes', 1000))
        self.net = models.__dict__[model_name](pretrained=pretrained)

    def forward(self, input):
        return self.net(input)

    def forward_shape(self, input_shape):
        nB = input_shape[0]
        nC = self.num_classes
        return [nB, nC]


class CaffeNetLayer(nn.Module):
    def __init__(self, layer, *input_shapes):
        from ptcaffe.caffenet import CaffeNet

        super(CaffeNetLayer, self).__init__()
        include_param = layer.get('include', OrderedDict())
        self.phase = include_param.get('phase', 'TEST')
        net_param = layer.get('net_param', OrderedDict())
        protofile = net_param['protofile']
        weightfile = net_param.get('weightfile', '')
        self.net = CaffeNet(protofile)
        self.net.set_nested(True)
        if 'output' in net_param:
            outputs = make_list(net_param['output'])
            self.net.set_outputs(*outputs)
        else:
            self.net.set_automatic_outputs()

        if weightfile != '':
            print('layer %s load weights from %s' % (layer['name'], weightfile))
            self.net.load_model(weightfile)

    def forward(self, *inputs):
        return self.net(*inputs)

    def forward_shape(self, *input_shapes):
        output_shapes = self.net.forward_shape(*input_shapes)
        return output_shapes


class TeacherLayer(nn.Module):
    def __init__(self, layer, *input_shapes):
        from ptcaffe.caffenet import CaffeNet

        super(TeacherLayer, self).__init__()
        teacher_param = layer.get('teacher_param', OrderedDict())
        protofile = teacher_param['protofile']
        weightfile = teacher_param['weightfile']
        verbose = int(teacher_param.get('verbose', '1'))
        self.teacher_protofile = protofile
        self.teacher_weightfile = weightfile
        self.teacher_model = CaffeNet(protofile, phase='TEST')
        self.teacher_model.load_model(weightfile)
        if 'output' in teacher_param:
            outputs = teacher_param['output'] if isinstance(teacher_param['output'], list) else [teacher_param['output']]
            self.teacher_model.set_outputs(*outputs)
        else:
            self.teacher_model.set_automatic_outputs(phase='TEST')

    def __repr__(self):
        return 'TeacherLayer(protofile=%s, weightfile=%s)' % (self.teacher_protofile, self.teacher_weightfile)

    def forward(self, *inputs):
        with torch.no_grad():
            if self.teacher_model.training:
                output = self.teacher_model(*inputs)[1:]
                return tuple(output)
            else:
                return self.teacher_model(*inputs)

    def forward_shape(self, *input_shapes):
        return self.teacher_model.forward_shape(*input_shapes)
