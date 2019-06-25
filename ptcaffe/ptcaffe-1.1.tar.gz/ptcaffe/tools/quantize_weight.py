#1. make QLayer -> Layer
#2. copy weights from qmodel to model
#3. export a text file which records all quantization layers and corresponding min max

import copy
from ptcaffe.caffenet import CaffeNet
from collections import OrderedDict
from ptcaffe.utils.prototxt import save_prototxt


def quantize_weight(protofile, in_ptcmodel, out_ptcmodel):
    net = CaffeNet(protofile)
    net.load_model(in_ptcmodel)
    for layer in net.net_info['layers']:
        if layer['type'] in {'QConvolution', 'QInnerProduct'}:
            name = layer['name']
            print('Quantizing {} layer {!r}'.format(layer['type'], name))
            module = net.models[name].make_weights_quantized()
    print('Saving {}'.format(out_ptcmodel))
    net.save_model(out_ptcmodel)

