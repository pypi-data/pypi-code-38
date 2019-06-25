# --------------------------------------------------------
# ptcaffe
# Licensed under The MIT License [see LICENSE for details]
# Written by xiaohang
# --------------------------------------------------------

import sys
import torch
import mxnet as mx
from gluoncv import model_zoo
from mxnet import nd, gluon
from ptcaffe.tools.gluon2ptcaffe.gluon2ptcaffe import gluon2ptcaffe
import numpy as np
from ptcaffe.caffenet import CaffeNet
from ptcaffe.utils.config import cfg

def forward_ptcaffe(model_name, image):
    protofile = '%s.prototxt' % model_name
    weightfile = '%s.ptcmodel' % model_name

    net = CaffeNet(protofile, phase = 'TEST')
    net.load_model(weightfile)
    net.VERIFY_DEBUG = True
    input = torch.from_numpy(image.asnumpy())
    net.eval()
    blobs = net(input)
    return blobs, net.models

def forward_mxnet(model_name, image):
    net = model_zoo.get_model(model_name, pretrained=True, prefix='%s_' % model_name.replace('.', 'dot'))
    input_symbols = mx.sym.var('data')
    output_symbol = net(input_symbols)
    internals = output_symbol.get_internals()
    output_names = internals.list_outputs()
    output_symbols = [internals[name] for name in output_names]
    params = net.collect_params()
    model = gluon.SymbolBlock(output_symbols, input_symbols, params=params)
    outputs = model(image)
    output_blobs = dict()
    for name, output in zip(output_names, outputs):
        if name.find('_output') >= 0:
            output_blobs[name] = output
    return output_blobs, params

def get_gluon_model(model_name):
    gluon2ptcaffe(model_name)
    
    image = nd.random.uniform(shape=(1, 3, 224, 224))
    #image = nd.random.uniform(shape=(1, 3, 299, 299))
    
    ptcaffe_blobs, ptcaffe_models = forward_ptcaffe(model_name, image)
    mxnet_blobs, mxnet_params = forward_mxnet(model_name, image)
           
    print('------------- Parameter Difference -------------')
    for mx_key in mxnet_params.keys():
        if '_weight' in mx_key:
            cf_key = mx_key.replace('_weight', '_fwd')
            cf_param = ptcaffe_models[cf_key].weight.data.numpy()
        elif '_bias' in mx_key:
            cf_key = mx_key.replace('_bias', '_fwd')
            cf_param = ptcaffe_models[cf_key].bias.data.numpy()
        elif '_gamma' in mx_key:
            cf_key = mx_key.replace('_gamma', '_fwd_scale')
            cf_param = ptcaffe_models[cf_key].weight.data.numpy()
        elif '_beta' in mx_key:
            cf_key = mx_key.replace('_beta', '_fwd_scale')
            cf_param = ptcaffe_models[cf_key].bias.data.numpy()
        elif '_running_mean' in mx_key:
            cf_key = mx_key.replace('_running_mean', '_fwd')
            cf_param = ptcaffe_models[cf_key].running_mean.numpy()
        elif '_running_var' in mx_key:
            cf_key = mx_key.replace('_running_var', '_fwd')
            cf_param = ptcaffe_models[cf_key].running_var.numpy()
        else:
            assert(False)
    
        mx_param = mxnet_params[mx_key].data().asnumpy()
        diff = abs(mx_param - cf_param).mean() 
        print('%-60s    diff: %f' % (mx_key, diff))
            
    print('------------- Output Difference -------------')
    for cf_key in ptcaffe_blobs.keys():
        mx_key = cf_key + '_output'
        if mx_key in mxnet_blobs.keys():
            mx_output = mxnet_blobs[mx_key].asnumpy()
            cf_output = ptcaffe_blobs[cf_key].data.numpy()
            diff = abs(mx_output - cf_output).mean()
            mx_mean = mx_output.mean()
            cf_mean = cf_output.mean()
            print('%-60s    diff: %f    mx_mean: %f    cf_mean: %f' % (mx_key, diff, mx_mean, cf_mean))
    
    
