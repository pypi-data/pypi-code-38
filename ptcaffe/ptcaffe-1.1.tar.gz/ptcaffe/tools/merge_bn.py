# --------------------------------------------------------
# ptcaffe
# Licensed under The MIT License [see LICENSE for details]
# Written by diwanying and xiaohang
# --------------------------------------------------------

from ptcaffe.caffenet import CaffeNet
from ptcaffe.utils.prototxt import save_prototxt
from ptcaffe.utils.utils import register_plugin
from collections import OrderedDict
import pdb
import copy
import torch
import numpy as np

PARAM_NAME_DICT = {'Convolution':'convolution_param', 'Convolution3D': 'convolution3d_param'}

def make_list(obj):
    return obj if isinstance(obj, list) else [obj]

def cal_conv_weight(scale_weight, scale_bias, running_mean, running_std, conv_weight, conv_bias):
    view_size = [1 for _ in range(len(conv_weight.shape))]
    view_size[0] = -1
    if conv_bias is None:
        conv_bias   = - running_mean * scale_weight/running_std + scale_bias
    else:
        conv_bias   = - running_mean * scale_weight/running_std + scale_bias + conv_bias*scale_weight/running_std
    scale_data  = (scale_weight / running_std).view(*(view_size)).expand_as(conv_weight)
    conv_weight = conv_weight * scale_data
    return conv_weight, conv_bias

# merge_bn_proto steps
# 1. build infos: all_lnames, layer_to, blob_from, lname_index
# 2. find path conv -> batchnorm -> scale, conv -> batchnorm, when find
#    a. update the information in new_layers, set bias_term -> true
#    b. set conv_layer's top to scale_layer's top or bn_layer's top
#    c. add bn_lname and scale_lname to del_names
# 3. remove del_names from all_lnames and get final_layers then final_net_info

def merge_bn_proto(input_protofile, output_prototxt):
    input_net = CaffeNet(input_protofile)
    layers = input_net.net_info['layers']

    all_lnames = [l['name'] for l in layers]
    blob_from = dict()
    layer_to = OrderedDict()
    lname_index = dict()

    for index, layer in enumerate(layers):
        assert('include' not in layer, "merge_bn works only for deploy prototxt")
        lname = layer['name']
        lname_index[lname] = index
        if 'bottom' in layer:
            bnames = make_list(layer['bottom'])
            for bname in bnames:
                if bname in blob_from:
                    if blob_from[bname] not in layer_to:
                        layer_to[blob_from[bname]] = []
                    layer_to[blob_from[bname]].append(lname)
        assert('top' in layer)
        tnames = make_list(layer['top'])
        for tname in tnames:
            blob_from[tname] = lname

    # find path: convolution -> batchnorm -> affine or scale
    new_net_info = copy.deepcopy(input_net.net_info)
    new_layers = new_net_info['layers']

    del_lnames = []
    for lname in all_lnames:
        index = lname_index[lname]
        layer = layers[index]
        ltype = layer['type']
        if ltype == 'Convolution' or ltype == 'Convolution3D':
            conv_lname = lname
            conv_layer = layer
            if conv_lname not in layer_to: continue

            conv_to_layers = layer_to[conv_lname]
            if len(conv_to_layers) > 1: continue
            conv_to_lname = conv_to_layers[0]
            conv_to_ltype = layers[lname_index[conv_to_lname]]['type']
            if conv_to_ltype == 'BatchNorm':
                bn_lname = conv_to_lname
                bn_layer = layers[lname_index[bn_lname]]
                bn_params = bn_layer.get('batch_norm_param', OrderedDict())
                if 'affine' in bn_params and bn_params['affine'] == 'true':
                    # start merge
                    del_lnames.append(bn_lname)
                    new_conv_layer = new_layers[lname_index[conv_lname]]
                    new_bn_layer = new_layers[lname_index[bn_lname]]
                    new_conv_layer['top'] = new_bn_layer['top']
                    new_conv_layer[PARAM_NAME_DICT[ltype]]['bias_term'] = 'true'
                    continue

                assert(bn_lname in layer_to)
                bn_to_layers = layer_to[bn_lname]
                assert(len(bn_to_layers) == 1)
                bn_to_lname = bn_to_layers[0]
                bn_to_type = layers[lname_index[bn_to_lname]]['type']
                if bn_to_type == 'Scale':
                    scale_lname = bn_to_lname

                    # start merge
                    del_lnames.append(scale_lname)
                    del_lnames.append(bn_lname)

                    new_conv_layer = new_layers[lname_index[conv_lname]]
                    new_scale_layer = new_layers[lname_index[scale_lname]]
                    new_conv_layer['top'] = new_scale_layer['top']
                    new_conv_layer[PARAM_NAME_DICT[ltype]]['bias_term'] = 'true'
            elif conv_to_ltype == 'Concat':
                concat_lname = conv_to_lname
                concat_to_layers = layer_to[concat_lname]
                if len(concat_to_layers) != 1: continue
                concat_to_lname = concat_to_layers[0]
                concat_to_ltype = layers[lname_index[concat_to_lname]]['type']
                if concat_to_ltype == 'BatchNorm':
                    bn_lname = concat_to_lname
                    bn_layer = layers[lname_index[bn_lname]]
                    bn_params = bn_layer.get('batch_norm_param', OrderedDict())
                    if 'affine' in bn_params and bn_params['affine'] == 'true':
                        # start merge
                        del_lnames.append(bn_lname)
                        new_conv_layer = new_layers[lname_index[conv_lname]]
                        new_concat_layer = new_layers[lname_index[concat_lname]]
                        new_bn_layer = new_layers[lname_index[bn_lname]]
                        new_concat_layer['top'] = new_bn_layer['top']
                        new_conv_layer[PARAM_NAME_DICT[ltype]]['bias_term'] = 'true'
                        continue

                    assert(bn_lname in layer_to)
                    bn_to_layers = layer_to[bn_lname]
                    assert(len(bn_to_layers) == 1)
                    bn_to_lname = bn_to_layers[0]
                    bn_to_type = layers[lname_index[bn_to_lname]]['type']
                    if bn_to_type == 'Scale':
                        scale_lname = bn_to_lname

                        # start merge
                        del_lnames.append(scale_lname)
                        del_lnames.append(bn_lname)

                        new_conv_layer = new_layers[lname_index[conv_lname]]
                        new_concat_layer = new_layers[lname_index[concat_lname]]
                        new_scale_layer = new_layers[lname_index[scale_lname]]
                        new_concat_layer['top'] = new_scale_layer['top']
                        new_conv_layer[PARAM_NAME_DICT[ltype]]['bias_term'] = 'true'


    valid_lnames = [lname for lname in all_lnames if lname not in del_lnames]
    final_layers = [new_layers[lname_index[lname]] for lname in valid_lnames]
    new_net_info['layers'] = final_layers

    print('save %s' % output_prototxt)
    save_prototxt(new_net_info, output_prototxt)

# merge_bn steps
# 1. build infos: all_lnames, layer_to, blob_from, lname_index
# 2. find path conv -> batchnorm -> scale, conv -> batchnorm, when find
#    a. update the information in new_layers, set bias_term -> true
#    b. set conv_layer's top to scale_layer's top or bn_layer's top
#    c. add bn_lname and scale_lname to del_names
# 3. remove del_names from all_lnames and get final_layers then final_net_info
def merge_bn(input_protofile, input_ptmodel, output_prototxt, output_ptmodel):
    input_net = CaffeNet(input_protofile)
    input_net.load_model(input_ptmodel)
    layers = input_net.net_info['layers']

    all_lnames = [l['name'] for l in layers]
    blob_from = dict()
    layer_to = OrderedDict()
    lname_index = dict()

    for index, layer in enumerate(layers):
        assert('include' not in layer, "merge_bn works only for deploy prototxt")
        lname = layer['name']
        lname_index[lname] = index
        if 'bottom' in layer:
            bnames = make_list(layer['bottom'])
            for bname in bnames:
                if bname in blob_from:
                    if blob_from[bname] not in layer_to:
                        layer_to[blob_from[bname]] = []
                    layer_to[blob_from[bname]].append(lname)
        assert('top' in layer)
        tnames = make_list(layer['top'])
        for tname in tnames:
            blob_from[tname] = lname

    # find path: convolution -> batchnorm -> affine or scale
    new_net_info = copy.deepcopy(input_net.net_info)
    new_layers = new_net_info['layers']

    del_lnames = []
    saved_conv_lnames = []
    saved_conv_weights = dict()
    saved_conv_biases = dict()
    for lname in layer_to.keys():
        index = lname_index[lname]
        layer = layers[index]
        ltype = layer['type']
        if ltype == 'Convolution' or ltype == 'Convolution3D':
            conv_lname = lname
            conv_layer = layer
            if conv_lname not in layer_to: continue

            conv_to_layers = layer_to[conv_lname]
            if len(conv_to_layers) > 1: continue
            conv_to_lname = conv_to_layers[0]
            conv_to_ltype = layers[lname_index[conv_to_lname]]['type']
            if conv_to_ltype == 'BatchNorm':
                bn_lname = conv_to_lname
                bn_layer = layers[lname_index[bn_lname]]
                bn_params = bn_layer.get('batch_norm_param', OrderedDict())
                eps = float(bn_params.get('eps', 1e-5))
                running_mean = input_net.models[bn_lname].running_mean
                running_var  = input_net.models[bn_lname].running_var
                running_std  = (running_var+eps).sqrt()
                bn_to_layers = layer_to[bn_lname]
                if 'affine' in bn_params and bn_params['affine'] == 'true':
                    # start merge
                    del_lnames.append(bn_lname)
                    scale_weight = input_net.models[bn_lname].weight.data
                    scale_bias   = input_net.models[bn_lname].bias.data
                    conv_weight  = input_net.models[conv_lname].weight.data
                    conv_bias    = None if input_net.models[conv_lname].bias is None else input_net.models[conv_lname].bias.data
                    conv_weight, conv_bias = cal_conv_weight(scale_weight, scale_bias, running_mean, running_std, conv_weight, conv_bias)

                    saved_conv_weights[conv_lname] = conv_weight
                    saved_conv_biases[conv_lname] = conv_bias

                    new_conv_layer = new_layers[lname_index[conv_lname]]
                    new_bn_layer = new_layers[lname_index[bn_lname]]
                    new_conv_layer['top'] = new_bn_layer['top']
                    new_conv_layer[PARAM_NAME_DICT[ltype]]['bias_term'] = 'true'
                    saved_conv_lnames.append(conv_lname)
                    continue

                assert(bn_lname in layer_to)
                bn_to_layers = layer_to[bn_lname]
                assert(len(bn_to_layers) == 1)
                bn_to_lname = bn_to_layers[0]
                bn_to_type = layers[lname_index[bn_to_lname]]['type']
                if bn_to_type == 'Scale':
                    scale_lname = bn_to_lname

                    # start merge
                    del_lnames.append(scale_lname)
                    del_lnames.append(bn_lname)
                    scale_weight = input_net.models[scale_lname].weight.data
                    scale_bias   = input_net.models[scale_lname].bias.data
                    conv_weight  = input_net.models[conv_lname].weight.data
                    conv_bias    = None if input_net.models[conv_lname].bias is None else input_net.models[conv_lname].bias.data
                    conv_weight, conv_bias = cal_conv_weight(scale_weight, scale_bias, running_mean, running_std, conv_weight, conv_bias)

                    saved_conv_weights[conv_lname] = conv_weight
                    saved_conv_biases[conv_lname] = conv_bias

                    new_conv_layer = new_layers[lname_index[conv_lname]]
                    new_scale_layer = new_layers[lname_index[scale_lname]]
                    new_conv_layer['top'] = new_scale_layer['top']
                    new_conv_layer[PARAM_NAME_DICT[ltype]]['bias_term'] = 'true'
                    saved_conv_lnames.append(conv_lname)
            elif conv_to_ltype == 'Concat':
                concat_lname = conv_to_lname
                concat_layer = layers[lname_index[concat_lname]]
                concat_to_layers = layer_to[concat_lname]
                if len(concat_to_layers) != 1: continue
                concat_to_lname = concat_to_layers[0]
                concat_to_ltype = layers[lname_index[concat_to_lname]]['type']
                concat_bnames = make_list(concat_layer['bottom'])
                assert(len(concat_bnames) > 1)
                concat_from_lnames = [blob_from[bname] for bname in concat_bnames]
                concat_from_layers = [layers[lname_index[lname]] for lname in concat_from_lnames]
                concat_channels = [int(layer['convolution_param']['num_output']) for layer in concat_from_layers]
                concat_channels.insert(0,0)
                concat_cumsum_channels = np.cumsum(np.array(concat_channels))
                assert(conv_lname in concat_from_lnames)
                conv_index = concat_from_lnames.index(conv_lname)
                start_channel = concat_cumsum_channels[conv_index]
                end_channel = concat_cumsum_channels[conv_index+1]
                if concat_to_ltype == 'BatchNorm':
                    bn_lname = concat_to_lname
                    bn_layer = layers[lname_index[bn_lname]]
                    bn_params = bn_layer.get('batch_norm_param', OrderedDict())
                    eps = float(bn_params.get('eps', 1e-5))
                    running_mean = input_net.models[bn_lname].running_mean[start_channel:end_channel]
                    running_var  = input_net.models[bn_lname].running_var[start_channel:end_channel]
                    running_std  = (running_var+eps).sqrt()
                    if 'affine' in bn_params and bn_params['affine'] == 'true':
                        # start merge
                        if bn_lname not in del_lnames: del_lnames.append(bn_lname)

                        scale_weight = input_net.models[bn_lname].weight.data[start_channel:end_channel]
                        scale_bias   = input_net.models[bn_lname].bias.data[start_channel:end_channel]
                        conv_weight  = input_net.models[conv_lname].weight.data
                        conv_bias    = None if input_net.models[conv_lname].bias is None else input_net.models[conv_lname].bias.data
                        conv_weight, conv_bias = cal_conv_weight(scale_weight, scale_bias, running_mean, running_std, conv_weight, conv_bias)

                        saved_conv_weights[conv_lname] = conv_weight
                        saved_conv_biases[conv_lname] = conv_bias

                        new_conv_layer = new_layers[lname_index[conv_lname]]
                        new_concat_layer = new_layers[lname_index[concat_lname]]
                        new_bn_layer = new_layers[lname_index[bn_lname]]
                        new_concat_layer['top'] = new_bn_layer['top']
                        new_conv_layer[PARAM_NAME_DICT[ltype]]['bias_term'] = 'true'
                        saved_conv_lnames.append(conv_lname)
                        continue


                    assert(bn_lname in layer_to)
                    bn_to_layers = layer_to[bn_lname]
                    assert(len(bn_to_layers) == 1)
                    bn_to_lname = bn_to_layers[0]
                    bn_to_type = layers[lname_index[bn_to_lname]]['type']
                    if bn_to_type == 'Scale':
                        scale_lname = bn_to_lname

                        # start merge
                        if scale_lname not in del_lnames: del_lnames.append(scale_lname)
                        if bn_lname not in del_lnames: del_lnames.append(bn_lname)
                        scale_weight = input_net.models[scale_lname].weight.data[start_channel:end_channel]
                        scale_bias   = input_net.models[scale_lname].bias.data[start_channel:end_channel]
                        conv_weight  = input_net.models[conv_lname].weight.data
                        conv_bias    = None if input_net.models[conv_lname].bias is None else input_net.models[conv_lname].bias.data
                        conv_weight, conv_bias = cal_conv_weight(scale_weight, scale_bias, running_mean, running_std, conv_weight, conv_bias)

                        saved_conv_weights[conv_lname] = conv_weight
                        saved_conv_biases[conv_lname] = conv_bias

                        new_conv_layer = new_layers[lname_index[conv_lname]]
                        new_concat_layer = new_layers[lname_index[concat_lname]]
                        new_scale_layer = new_layers[lname_index[scale_lname]]
                        new_concat_layer['top'] = new_scale_layer['top']
                        new_conv_layer[PARAM_NAME_DICT[ltype]]['bias_term'] = 'true'
                        saved_conv_lnames.append(conv_lname)

    valid_lnames = [lname for lname in all_lnames if lname not in del_lnames]
    final_layers = [new_layers[lname_index[lname]] for lname in valid_lnames]
    new_net_info['layers'] = final_layers

    print('save %s' % output_prototxt)
    save_prototxt(new_net_info, output_prototxt)
    #---------------- merge proto over ---------------------

    output_net = CaffeNet(output_prototxt)
    input_state_dict = input_net.state_dict()
    output_state_dict = output_net.state_dict()
    for key in output_state_dict.keys():
        if 'num_batches_tracked' in key:
                continue
        if key in input_state_dict.keys():
            output_state_dict[key][:] = input_state_dict[key][:]

    for lname in output_net.models.keys():
        if lname in saved_conv_lnames:
            output_net.models[lname].weight.data.copy_(saved_conv_weights[lname])
            output_net.models[lname].bias.data.copy_(saved_conv_biases[lname])
    print('save %s' % output_ptmodel)
    output_net.save_model(output_ptmodel)
    #---------------- merge weights over ---------------------

    # verify networks
    input_net.set_automatic_outputs()
    output_net.set_automatic_outputs()
    input_net.VERIFY_DEBUG = True
    output_net.VERIFY_DEBUG = True
    input_net.eval()
    output_net.eval()
    input_shapes = input_net.get_input_shapes()
    assert(not isinstance(input_shapes[0], list))
    input_shape = input_shapes
    input = torch.rand(*input_shape)
    orig_output = input_net(input)
    nobn_output = output_net(input)

    for name in nobn_output.keys():
        diff = (orig_output[name] - nobn_output[name]).abs().mean()
        print('%s differene = %f' % (name,diff))


#    if isinstance(orig_output, tuple):
#        for i in range(len(orig_output)):
#            diff = (orig_output[i] - nobn_output[i]).abs().mean()
#            print('difference = %f' % diff)
#    else:
#        diff = (orig_output - nobn_output).abs().mean()
#        print('differene = %f' % diff)
#

import os
import sys
import argparse
from collections import OrderedDict
from ptcaffe.utils.config import cfg
import ptcaffe
def main():
    print('ptcaffe %s' % ptcaffe.__version__)

    parser = argparse.ArgumentParser(description='merge_bn in ptcaffe model', usage='merge_bn input_prototxt input_ptcmodel output_prototxt output_ptcmodel\nor: merge_bn input_prototxt output_prototxt', epilog="welcome!")
    parser.add_argument('params', help="input_prototxt [input_ptcmodel] output_prototxt [output_ptcmodel]", nargs='+')
    parser.add_argument('--phase', help='Optional; network phase (TRAIN or TEST)')
    parser.add_argument('--verbose', type=int, help='Optional; verbose level 0: no info, 1: receptive field, 2: debug')
    parser.add_argument('--register', help='Optional; register files')
    parser.add_argument('--plugin', help='Optional; enable plugin')
    args = parser.parse_args()

    print('args: %s' % args)

    register_plugin(args.plugin)

    if args.verbose is not None:
        from ptcaffe.utils.logger import logger
        cfg.VERBOSE_LEVEL = args.verbose
        if args.verbose == 0:
            logger.set_level(logger.INFO)
        elif args.verbose == 1:
            logger.set_level(logger.MORE_INFO)
        elif args.verbose >= 2:
            logger.set_level(logger.DEBUG)

    if len(args.params) == 4:
        input_protofile   = args.params[0]
        input_ptcmodel  = args.params[1]
        output_protofile = args.params[2]
        output_ptcmodel   = args.params[3]
        print('input_protofile = %s' % input_protofile)
        print('input_ptcmodel = %s' % input_ptcmodel)
        print('output_protofile = %s' % output_protofile)
        print('output_ptcmodel = %s' % output_ptcmodel)
        merge_bn(input_protofile, input_ptcmodel, output_protofile, output_ptcmodel)
    elif len(args.params) == 2:
        input_protofile   = args.params[0]
        output_protofile = args.params[1]
        print('input_protofile = %s' % input_protofile)
        print('output_protofile = %s' % output_protofile)
        merge_bn_proto(input_protofile, output_protofile)

if __name__ == "__main__":
    main()
