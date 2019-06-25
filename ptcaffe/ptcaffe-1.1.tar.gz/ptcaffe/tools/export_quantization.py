# --------------------------------------------------------
# ptcaffe
# Licensed under The MIT License [see LICENSE for details]
# Written by xiaohang and liuyufei
# --------------------------------------------------------

#1. make QLayer -> Layer
#2. copy weights from qmodel to model
#3. export a text file which records all quantization layers and corresponding min max

from ptcaffe.caffenet import CaffeNet
from collections import OrderedDict
import copy
from ptcaffe.utils.prototxt import save_prototxt

def save_qfile(qfile, relu6_names, quant_names, min_vals, max_vals):
    fp = open(qfile, 'w')
    for name in relu6_names:
        fp.write(name+",relu6\n")
    for name in quant_names:
        min_val = min_vals[name]
        max_val = max_vals[name]
        fp.write(name+",act,%f,%f\n" % (min_val, max_val))
    fp.close()

def export_quantization_model(input_protofile, input_ptmodel, output_protofile, output_caffemodel, output_qfile):
    input_net = CaffeNet(input_protofile)
    input_net.load_model(input_ptmodel)
    input_net_info = input_net.net_info
    # make weights quantized (useful for quantization without train)
    input_layers = input_net_info['layers']
    for layer in input_layers:
        lname = layer['name']
        ltype = layer['type']
        if ltype in ['QConvolution', 'QInnerProduct']:
            input_net.models[lname].make_weights_quantized()

    output_net_info = copy.deepcopy(input_net_info)
    output_layers = output_net_info['layers']
    quant_lnames = []
    relu6_lnames = []
    min_vals = dict()
    max_vals = dict()
    for layer in output_layers:
        lname = layer['name']
        if layer['type'] in ['QConvolution', 'QInnerProduct', 'QPooling', 'QReLU']:
            quant_lnames.append(lname)
            min_vals[lname] = input_net.models[lname].minval[0]
            max_vals[lname] = input_net.models[lname].maxval[0]
            layer['type'] = layer['type'][1:]
        elif layer['type'] == 'ReLU6':
            layer['type'] = 'ReLU'
            relu6_lnames.append(lname)
    print('save %s' % output_qfile)
    save_qfile(output_qfile, relu6_lnames,  quant_lnames, min_vals, max_vals)
    print('save %s' % output_protofile)
    save_prototxt(output_net_info, output_protofile)
    output_net = CaffeNet(output_protofile)
    output_net.load_model(input_ptmodel)
    print('save %s' % output_caffemodel)
    output_net.save_caffemodel(output_caffemodel)

if __name__ == '__main__':
    input_protofile = "input.prototxt"
    input_ptmodel = 'input.weights.pth'
    output_protofile = "output.prototxt"
    output_caffemodel = "output.caffemodel"
    output_qfile = "output.qfile"
    export_quantization_model(input_protofile, input_ptmodel, output_protofile, output_caffemodel, output_qfile)
