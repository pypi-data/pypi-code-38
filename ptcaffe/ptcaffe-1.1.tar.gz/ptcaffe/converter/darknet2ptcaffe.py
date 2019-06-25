# --------------------------------------------------------
# ptcaffe
# Licensed under The MIT License [see LICENSE for details]
# Written by xiaohang 2018.3
# --------------------------------------------------------

from __future__ import division
import os
import sys
import ctypes
from ptcaffe.utils.config import cfg

darknet_version = "darknet" 
#darknet_version = "darknet_debug" 
#darknet_version = "darknet_alexeyab_debug" 
darknet_lib = ctypes.CDLL("%s/.ptcaffe/%s/libdarknet.so" % (os.getenv('HOME'), darknet_version), ctypes.RTLD_GLOBAL) # lib should be initialized before CaffeNet
#if darknet_version in ["darknet", "darknet_debug"]: cfg.YOLO_USE_CORRECT_REORG=False
use_identity_layer = False

import torch
import numpy as np
from collections import OrderedDict
from ptcaffe.caffenet import CaffeNet
from ptcaffe.utils.prototxt import save_prototxt
import ptcaffe_plugins.yolo

def parse_cfg(cfgfile):
    blocks = []
    fp = open(cfgfile, 'r')
    block =  None
    line = fp.readline()
    while line != '':
        line = line.rstrip()
        if line == '' or line[0] == '#':
            line = fp.readline()
            continue        
        elif line[0] == '[':
            if block:
                blocks.append(block)
            block = OrderedDict()
            block['type'] = line.lstrip('[').rstrip(']')
            # set default value
            if block['type'] == 'convolutional':
                block['batch_normalize'] = 0
        else:
            key,value = line.split('=')
            key = key.strip()
            if key == 'type':
                key = '_type'
            value = value.strip()
            block[key] = value
        line = fp.readline()

    if block:
        blocks.append(block)
    fp.close()
    return blocks

def cfg2prototxt(cfgfile, merge_scale=True):
    blocks = parse_cfg(cfgfile)

    layers = []
    props = OrderedDict() 
    bottom = 'data'
    layer_id = 1
    topnames = dict()
    for block in blocks:
        if block['type'] == 'net':
            props['name'] = 'Darkent2Caffe'
            props['input'] = 'data'
            props['input_dim'] = ['1']
            props['input_dim'].append(block['channels'])
            props['input_dim'].append(block['height'])
            props['input_dim'].append(block['width'])
            continue
        elif block['type'] == 'convolutional':
            conv_layer = OrderedDict()
            conv_layer['bottom'] = bottom
            if 'name' in block:
                conv_layer['top'] = block['name']
                conv_layer['name'] = block['name']
            else:
                conv_layer['top'] = 'layer%d-conv' % layer_id
                conv_layer['name'] = 'layer%d-conv' % layer_id
            conv_layer['type'] = 'Convolution'
            convolution_param = OrderedDict()
            convolution_param['num_output'] = block['filters']
            convolution_param['kernel_size'] = block['size']
            if block['pad'] == '1':
                convolution_param['pad'] = str(int(int(convolution_param['kernel_size'])/2))
            convolution_param['stride'] = block['stride']
            if block['batch_normalize'] == '1':
                convolution_param['bias_term'] = 'false'
            else:
                convolution_param['bias_term'] = 'true'
            conv_layer['convolution_param'] = convolution_param
            layers.append(conv_layer)
            bottom = conv_layer['top']

            if block['batch_normalize'] == '1':
                bn_layer = OrderedDict()
                bn_layer['bottom'] = bottom
                bn_layer['top'] = bottom
                if 'name' in block:
                    bn_layer['name'] = '%s-bn' % block['name']
                else:
                    bn_layer['name'] = 'layer%d-bn' % layer_id
                bn_layer['type'] = 'BatchNorm'

                if merge_scale:
                    batch_norm_param = OrderedDict()
                    #batch_norm_param['use_global_stats'] = 'true'
                    batch_norm_param['affine'] = 'true'
                    bn_layer['batch_norm_param'] = batch_norm_param
                    layers.append(bn_layer)
                else:
                    layers.append(bn_layer)

                    scale_layer = OrderedDict()
                    scale_layer['bottom'] = bottom
                    scale_layer['top'] = bottom
                    if 'name' in block:
                        scale_layer['name'] = '%s-scale' % block['name']
                    else:
                        scale_layer['name'] = 'layer%d-scale' % layer_id
                    scale_layer['type'] = 'Scale'
                    scale_param = OrderedDict()
                    scale_param['bias_term'] = 'true'
                    scale_layer['scale_param'] = scale_param
                    layers.append(scale_layer)

            if block['activation'] != 'linear':
                relu_layer = OrderedDict()
                relu_layer['bottom'] = bottom
                relu_layer['top'] = bottom
                if 'name' in block:
                    relu_layer['name'] = '%s-act' % block['name']
                else:
                    relu_layer['name'] = 'layer%d-act' % layer_id
                relu_layer['type'] = 'ReLU'
                if block['activation'] == 'leaky':
                    relu_param = OrderedDict()
                    relu_param['negative_slope'] = '0.1'
                    relu_layer['relu_param'] = relu_param
                layers.append(relu_layer)
            topnames[layer_id] = bottom
            layer_id = layer_id+1
        elif block['type'] == 'maxpool':
            max_layer = OrderedDict()
            max_layer['bottom'] = bottom
            if 'name' in block:
                max_layer['top'] = block['name']
                max_layer['name'] = block['name']
            else:
                max_layer['top'] = 'layer%d-maxpool' % layer_id
                max_layer['name'] = 'layer%d-maxpool' % layer_id
            max_layer['type'] = 'Pooling'
            pooling_param = OrderedDict()
            pooling_param['kernel_size'] = block['size']
            pooling_param['stride'] = block['stride']
            pooling_param['pool'] = 'MAX'
            if 'pad' in block and int(block['pad']) == 1:
                pooling_param['pad'] = str(int((int(block['size'])-1)/2))
            max_layer['pooling_param'] = pooling_param
            layers.append(max_layer)
            bottom = max_layer['top']
            topnames[layer_id] = bottom
            layer_id = layer_id+1
        elif block['type'] == 'avgpool':
            avg_layer = OrderedDict()
            avg_layer['bottom'] = bottom
            if 'name' in  block:
                avg_layer['top'] = block['name']
                avg_layer['name'] = block['name']
            else:
                avg_layer['top'] = 'layer%d-avgpool' % layer_id
                avg_layer['name'] = 'layer%d-avgpool' % layer_id
            avg_layer['type'] = 'Pooling'
            pooling_param = OrderedDict()
            pooling_param['kernel_size'] = 7
            pooling_param['stride'] = 1
            pooling_param['pool'] = 'AVE'
            avg_layer['pooling_param'] = pooling_param
            layers.append(avg_layer)
            bottom = avg_layer['top']
            topnames[layer_id] = bottom
            layer_id = layer_id+1
        elif block['type'] == 'yolo':
            if True:
                yolo_layer = OrderedDict()
                yolo_layer['bottom'] = bottom
                if 'name' in block:
                    yolo_layer['top'] = block['name']
                    yolo_layer['name'] = block['name']
                else:
                    yolo_layer['top'] = 'layer%d-yolo' % layer_id
                    yolo_layer['name'] = 'layer%d-yolo' % layer_id
                yolo_layer['type'] = 'YoloLoss'
                include_param = OrderedDict()
                include_param['phase'] = 'TEST'
                #yolo_layer['include'] = include_param
                yolo_param = OrderedDict()
                yolo_param['stride'] = block['stride']
                yolo_param['mask'] = block['mask'].strip()
                yolo_param['anchors'] = block['anchors'].strip()
                yolo_param['classes'] = block['classes']
                yolo_param['num'] = block['num']
                yolo_param['ignore_thresh'] = block['ignore_thresh']
                yolo_param['truth_thresh'] = block['truth_thresh']
                yolo_layer['yolo_param'] = yolo_param
                layers.append(yolo_layer)
                bottom = yolo_layer['top']
            topnames[layer_id] = bottom
            layer_id = layer_id + 1
        elif block['type'] == 'region':
            if True:
                region_layer = OrderedDict()
                region_layer['bottom'] = bottom
                if 'name' in block:
                    region_layer['top'] = block['name']
                    region_layer['name'] = block['name']
                else:
                    region_layer['top'] = 'layer%d-region' % layer_id
                    region_layer['name'] = 'layer%d-region' % layer_id
                region_layer['type'] = 'RegionLoss'
                region_param = OrderedDict()
                region_param['anchors'] = block['anchors'].strip()
                region_param['bias_match'] = block.get('bias_match', '1')
                region_param['classes'] = block['classes']
                region_param['coords'] = block.get('coords', 4)
                region_param['num'] = block['num']
                region_param['softmax'] = block.get('softmax', '1')
                region_param['jitter'] = block.get('jitter', '0.3')
                region_param['rescore'] = block.get('rescore', '1')
                region_param['object_scale'] = block.get('object_scale', '5')
                region_param['noobject_scale'] = block.get('noobject_scale', '1')
                region_param['class_scale'] = block.get('class_scale', '1')
                region_param['coord_scale'] = block.get('coord_scale', '1')
                region_param['absolute'] = block.get('absolute', '1')
                region_param['thresh'] = block.get('thresh', '0.6')
                region_param['random'] = block.get('random', '1')
                region_layer['region_param'] = region_param
                layers.append(region_layer)
                bottom = region_layer['top']
            topnames[layer_id] = bottom
            layer_id = layer_id + 1
        elif block['type'] == 'reorg':
            reorg_layer = OrderedDict()
            reorg_layer['bottom'] = bottom
            if 'name' in block:
                reorg_layer['top'] = block['name']
                reorg_layer['name'] = block['name']
            else:
                reorg_layer['top'] = 'layer%d-reorg' % layer_id
                reorg_layer['name'] = 'layer%d-reorg' % layer_id
            reorg_layer['type'] = 'Reorg'
            reorg_param = OrderedDict()
            reorg_param['stride'] = block['stride']
            reorg_layer['reorg_param'] = reorg_param
            layers.append(reorg_layer)
            bottom = reorg_layer['top']
            topnames[layer_id] = bottom
            layer_id = layer_id + 1
        elif block['type'] == 'upsample':
            upsample_layer = OrderedDict()
            upsample_layer['bottom'] = bottom
            if 'name' in block:
                upsample_layer['top'] = block['name']
                upsample_layer['name'] = block['name']
            else:
                upsample_layer['top'] = 'layer%d-upsample' % layer_id
                upsample_layer['name'] = 'layer%d-upsample' % layer_id
            upsample_layer['type'] = 'YoloUpsample'
            upsample_param = OrderedDict()
            upsample_param['stride'] = block['stride']
            upsample_layer['upsample_param'] = upsample_param
            layers.append(upsample_layer)
            bottom = upsample_layer['top']
            topnames[layer_id] = bottom
            layer_id = layer_id + 1
        elif block['type'] == 'route':
            if block['layers'].find(',') > 0:
                layer_ids = block['layers'].split(',')
                layer_ids = [int(l.strip()) for l in layer_ids]
                assert(len(layer_ids) == 2)
                prev_layer_id0 = layer_id + layer_ids[0] if layer_ids[0] < 0 else layer_ids[0]+1
                prev_layer_id1 = layer_id + layer_ids[1] if layer_ids[1] < 0 else layer_ids[1]+1
                bottom0 = topnames[prev_layer_id0]
                bottom1 = topnames[prev_layer_id1]
                concat_layer = OrderedDict()
                concat_layer['bottom'] = [bottom0, bottom1]
                if 'name' in block:
                    concat_layer['top'] = block['name']
                    concat_layer['name'] = block['name']
                else:
                    concat_layer['top'] = 'layer%d-route' % layer_id
                    concat_layer['name'] = 'layer%d-route' % layer_id
                concat_layer['type'] = 'Concat'
                concat_param = OrderedDict()
                concat_param['axis'] = '1'
                concat_layer['concat_param'] = concat_param
                layers.append(concat_layer)
                bottom = concat_layer['top']
                topnames[layer_id] = bottom
            else:
                from_layer = int(block['layers'])
                prev_layer_id = layer_id + from_layer if from_layer < 0 else from_layer + 1
                bottom = topnames[prev_layer_id]
                if use_identity_layer:
                    identity_layer = OrderedDict()
                    identity_layer['bottom'] = bottom
                    if 'name' in block:
                        identity_layer['top'] = blob['name']
                        identity_layer['name'] = block['name']
                    else:
                        identity_layer['top'] = 'layer%d-route' % layer_id
                        identity_layer['name'] = 'layer%d-route' % layer_id
                    identity_layer['type'] = 'Identity'
                    layers.append(identity_layer)
                    bottom = identity_layer['top']
                topnames[layer_id] = bottom
            layer_id = layer_id + 1
        elif block['type'] == 'shortcut':
            from_id = int(block['from'])
            prev_layer_id1 = layer_id + from_id if from_id < 0 else from_id + 1
            prev_layer_id2 = layer_id - 1
            bottom1 = topnames[prev_layer_id1]
            bottom2= topnames[prev_layer_id2]
            shortcut_layer = OrderedDict()
            shortcut_layer['bottom'] = [bottom1, bottom2]
            if 'name' in block:
                shortcut_layer['top'] = block['name']
                shortcut_layer['name'] = block['name']
            else:
                shortcut_layer['top'] = 'layer%d-shortcut' % layer_id
                shortcut_layer['name'] = 'layer%d-shortcut' % layer_id
            shortcut_layer['type'] = 'Eltwise'
            eltwise_param = OrderedDict()
            eltwise_param['operation'] = 'SUM'
            shortcut_layer['eltwise_param'] = eltwise_param
            layers.append(shortcut_layer)
            bottom = shortcut_layer['top']
 
            if block['activation'] != 'linear':
                relu_layer = OrderedDict()
                relu_layer['bottom'] = bottom
                relu_layer['top'] = bottom
                if 'name' in block:
                    relu_layer['name'] = '%s-act' % block['name']
                else:
                    relu_layer['name'] = 'layer%d-act' % layer_id
                relu_layer['type'] = 'ReLU'
                if block['activation'] == 'leaky':
                    relu_param = OrderedDict()
                    relu_param['negative_slope'] = '0.1'
                    relu_layer['relu_param'] = relu_param
                layers.append(relu_layer)
            topnames[layer_id] = bottom
            layer_id = layer_id+1           
        elif block['type'] == 'connected':
            fc_layer = OrderedDict()
            fc_layer['bottom'] = bottom
            if 'name' in block:
                fc_layer['top'] = block['name']
                fc_layer['name'] = block['name']
            else:
                fc_layer['top'] = 'layer%d-fc' % layer_id
                fc_layer['name'] = 'layer%d-fc' % layer_id
            fc_layer['type'] = 'InnerProduct'
            fc_param = OrderedDict()
            fc_param['num_output'] = int(block['output'])
            fc_layer['inner_product_param'] = fc_param
            layers.append(fc_layer)
            bottom = fc_layer['top']

            if block['activation'] != 'linear':
                relu_layer = OrderedDict()
                relu_layer['bottom'] = bottom
                relu_layer['top'] = bottom
                if 'name' in block:
                    relu_layer['name'] = '%s-act' % block['name']
                else:
                    relu_layer['name'] = 'layer%d-act' % layer_id
                relu_layer['type'] = 'ReLU'
                if block['activation'] == 'leaky':
                    relu_param = OrderedDict()
                    relu_param['negative_slope'] = '0.1'
                    relu_layer['relu_param'] = relu_param
                layers.append(relu_layer)
            topnames[layer_id] = bottom
            layer_id = layer_id+1
        else:
            print('unknow layer type %s ' % block['type'])
            topnames[layer_id] = bottom
            layer_id = layer_id + 1

    net_info = OrderedDict()
    net_info['props'] = props
    net_info['layers'] = layers
    return net_info

def cfg_blobs_in_ptcaffe(cfgfile):
    blocks = parse_cfg(cfgfile)

    layers = []
    props = OrderedDict() 
    layer_id = 1
    topnames = dict()
    for block in blocks:
        if block['type'] == 'net':
            continue
        elif block['type'] == 'convolutional':
            if 'name' in block:
                top = block['name']
            else:
                top = 'layer%d-conv' % layer_id
            topnames[layer_id] = top
            layer_id = layer_id+1
        elif block['type'] == 'maxpool':
            if 'name' in block:
                top = block['name']
            else:
                top = 'layer%d-maxpool' % layer_id
            topnames[layer_id] = top
            layer_id = layer_id+1
        elif block['type'] == 'avgpool':
            if 'name' in  block:
                top = block['name']
            else:
                top = 'layer%d-avgpool' % layer_id
            topnames[layer_id] = top
            layer_id = layer_id+1
        elif block['type'] == 'yolo':
            if 'name' in block:
                top = block['name']
            else:
                top = 'layer%d-yolo' % layer_id
            topnames[layer_id] = top
            layer_id = layer_id + 1
        elif block['type'] == 'region':
            if 'name' in block:
                top = block['name']
            else:
                top = 'layer%d-region' % layer_id
            topnames[layer_id] = top
            layer_id = layer_id + 1
        elif block['type'] == 'reorg':
            if 'name' in block:
                top = block['name']
            else:
                top = 'layer%d-reorg' % layer_id
            topnames[layer_id] = top
            layer_id = layer_id + 1
        elif block['type'] == 'upsample':
            if 'name' in block:
                top = block['name']
            else:
                top = 'layer%d-upsample' % layer_id
            topnames[layer_id] = top
            layer_id = layer_id + 1
        elif block['type'] == 'route':
            if block['layers'].find(',') > 0:
                if 'name' in block:
                    top = block['name']
                else:
                    top = 'layer%d-route' % layer_id
                topnames[layer_id] = top
            else:
                if use_identity_layer:
                    if 'name' in block:
                        top = block['name']
                    else:
                        top = 'layer%d-route' % layer_id
                else:
                    from_layer = int(block['layers'])
                    prev_layer_id = layer_id + from_layer if from_layer < 0 else from_layer + 1
                    top = topnames[prev_layer_id]
                topnames[layer_id] = top
            layer_id = layer_id + 1
        elif block['type'] == 'shortcut':
            if 'name' in block:
                top = block['name']
            else:
                top = 'layer%d-shortcut' % layer_id
            topnames[layer_id] = top
            layer_id = layer_id+1           
        elif block['type'] == 'connected':
            if 'name' in block:
                top = block['name']
            else:
                top = 'layer%d-fc' % layer_id
            topnames[layer_id] = top
            layer_id = layer_id+1
        else:
            print('unknow layer type %s ' % block['type'])
            layer_id = layer_id + 1
            exit()

    blobs = [topnames[i] for i in range(1, len(blocks))]
    return blobs

    # currently only support loading convoluton weights without batchnorm
def darknet2ptcaffe(cfgfile, weightfile, protofile, ptmodelfile, merge_scale=True):
    net_info = cfg2prototxt(cfgfile, merge_scale)
    print('save %s' % protofile)
    save_prototxt(net_info, protofile)
    ptc_net = CaffeNet(protofile, phase='TEST')

    blocks = parse_cfg(cfgfile)
    fp = open(weightfile, 'rb')
    major = np.fromfile(fp, count=1, dtype=np.int32)
    minor = np.fromfile(fp, count=1, dtype=np.int32)
    revision = np.fromfile(fp, count=1, dtype=np.int32)
    if (major*10+minor)>=2 and major < 1000 and minor < 1000:
        seen = np.fromfile(fp, count=1, dtype=np.int64)
    else:
        seen = np.fromfile(fp, count=1, dtype=np.int32)
    buf = np.fromfile(fp, dtype = np.float32)
    fp.close()

    layers = []
    layer_id = 1
    start = 0
    for block in blocks:
        if start >= buf.size:
            break

        if block['type'] == 'net':
            continue
        elif block['type'] == 'convolutional':
            batch_normalize = int(block['batch_normalize'])
            if 'name' in block:
                conv_layer_name = block['name']
                bn_layer_name = '%s-bn' % block['name']
                if not merge_scale: scale_layer_name = '%s-scale' % block['name']
            else:
                conv_layer_name = 'layer%d-conv' % layer_id
                bn_layer_name = 'layer%d-bn' % layer_id
                if not merge_scale: scale_layer_name = 'layer%d-scale' % layer_id

            if batch_normalize:
                if merge_scale:
                    conv_weight = ptc_net.models[conv_layer_name].weight.data
                    running_mean = ptc_net.models[bn_layer_name].running_mean
                    running_var = ptc_net.models[bn_layer_name].running_var
                    scale_weight = ptc_net.models[bn_layer_name].weight.data
                    scale_bias = ptc_net.models[bn_layer_name].bias.data
    
                else:
                    conv_weight = ptc_net.models[conv_layer_name].weight.data
                    running_mean = ptc_net.models[bn_layer_name].running_mean
                    running_var = ptc_net.models[bn_layer_name].running_var
                    scale_weight = ptc_net.models[scale_layer_name].weight.data
                    scale_bias = ptc_net.models[scale_layer_name].bias.data
    
                scale_bias.copy_(torch.from_numpy(buf[start:start+scale_bias.numel()]))
                start = start + scale_bias.numel()
                scale_weight.copy_(torch.from_numpy(buf[start:start+scale_weight.numel()]))
                start = start + scale_weight.numel()
                running_mean.copy_(torch.from_numpy(buf[start:start+running_mean.numel()]))
                start = start + running_mean.numel()
                running_var.copy_(torch.from_numpy(buf[start:start+running_var.numel()]))
                start = start + running_var.numel()
                conv_weight.view(-1).copy_(torch.from_numpy(buf[start:start+conv_weight.numel()]))
                start = start + conv_weight.numel() 

            else:
                conv_bias = ptc_net.models[conv_layer_name].bias.data
                conv_weight = ptc_net.models[conv_layer_name].weight.data
                conv_bias.copy_(torch.from_numpy(buf[start:start+conv_bias.numel()]))
                start = start + conv_bias.numel()
                conv_weight.view(-1).copy_(torch.from_numpy(buf[start:start+conv_weight.numel()]))
                start = start + conv_weight.numel() 
            layer_id = layer_id+1
        elif block['type'] == 'connected':
            if 'name' in block:
                fc_layer_name = block['name']
            else:
                fc_layer_name = 'layer%d-fc' % layer_id
            
            fc_bias = ptc_net.models[fc_layer_name].bias.data
            fc_weight = ptc_net.models[fc_layer_name].weight.data
            fc_bias.copy_(torch.from_numpy(buf[start:start+fc_bias.numel()]))
            start = start + fc_bias.numel()
            fc_weight.view(-1).copy_(torch.from_numpy(buf[start:start+fc_weight.numel()]))
            start = start + fc_weight.numel() 

            layer_id = layer_id + 1
        else:
            layer_id = layer_id + 1

    print('save %s' % ptmodelfile)
    ptc_net.save_model(ptmodelfile) 

def verify_ptcaffe_darknet(lib, protofile, ptcmodel, cfgfile, weightfile):
    import ctypes
    import math
    import random
    
    #lib = CDLL("libdarknet.so", RTLD_GLOBAL)
    network_width = lib.network_width
    network_width.argtypes = [ctypes.c_void_p]
    network_width.restype = ctypes.c_int

    network_height = lib.network_height
    network_height.argtypes = [ctypes.c_void_p]
    network_height.restype = ctypes.c_int
    
    if darknet_version == "darknet_alexeyab_debug":
        network_predict = lib.network_predict2
    else:
        network_predict = lib.network_predict
    network_predict.argtypes = [ctypes.c_void_p, ctypes.POINTER(ctypes.c_float)]
    network_predict.restype = ctypes.POINTER(ctypes.c_float)
    
    set_batch_network = lib.set_batch_network
    set_batch_network.argtypes = [ctypes.c_void_p, ctypes.c_int]
    
    load_net = lib.load_network
    load_net.argtypes = [ctypes.c_char_p, ctypes.c_char_p, ctypes.c_int]
    load_net.restype = ctypes.c_void_p
    #-----------

    import numpy as np
    import torch
    from ptcaffe.caffenet import CaffeNet
    import ptcaffe_plugins.yolo

    #1. create networks
    ptc_net = CaffeNet(protofile, phase='TEST')
    #ptc_net.set_verbose(3)
    ptc_net.load_model(ptcmodel)
    ptc_net.eval()
    last_top = ptc_net.net_info['layers'][-1]['top']
    assert(not isinstance(last_top, list))
    ptc_net.set_outputs(last_top)

    if sys.version_info.major == 2:
        dark_net = load_net(cfgfile,  weightfile, 0)
    else:
        dark_net = load_net(cfgfile.encode('utf-8'),  weightfile.encode('utf-8'), 0)
    #set_batch_network(dark_net, 1)

    #2. inputs
    width = network_width(dark_net)
    height = network_height(dark_net)
    input_shape = [1, 3, height, width]
    print('input_shape: %s' % input_shape)
    ptc_input = torch.rand(input_shape)
    dark_input = ptc_input.numpy().ctypes.data_as(ctypes.POINTER(ctypes.c_float))
    
    #3. compute outputs
    if darknet_version == 'darknet':
        ptc_out = ptc_net(ptc_input)
    
        dark_out = network_predict(dark_net, dark_input)
        dark_out = np.ctypeslib.as_array(ctypes.cast(dark_out, ctypes.POINTER(ctypes.c_float)), ptc_out.shape)
        dark_out = torch.from_numpy(dark_out)
    
        #4. compute difference
        print('output_shape: %s' % list(ptc_out.shape))
        diff = (ptc_out - dark_out).abs().mean()
        print('verify diff: %f' % diff.item())
    else:
        get_network_outputs = lib.get_network_outputs
        get_network_outputs.argtypes = [ctypes.c_void_p]
        get_network_outputs.restype = ctypes.POINTER(ctypes.POINTER(ctypes.c_float))

        ptc_net.VERIFY_DEBUG = True
        ptc_blobs = ptc_net(ptc_input)
        blob_names = cfg_blobs_in_ptcaffe(cfgfile)
        dark_out = network_predict(dark_net, dark_input)
        dark_blobs = get_network_outputs(dark_net)

        print('---------------------------')
        print('layer\t%-20s\t%-20s\toutput_diff\tptc_mean\tdark_mean' % ('name','shape'))
        for idx, name in enumerate(blob_names):
            ptc_out = ptc_blobs[name].data
            dark_out = dark_blobs[idx]
            dark_out = np.ctypeslib.as_array(ctypes.cast(dark_out, ctypes.POINTER(ctypes.c_float)), ptc_out.shape)
            dark_out = torch.from_numpy(dark_out)
            #print('output_shape: %s' % list(ptc_out.shape))
            diff = (ptc_out - dark_out).abs().mean()
            ptc_mean = ptc_out.abs().mean()
            dark_mean = dark_out.abs().mean()
            print('%5d\t%-20s\t%-20s\t%f\t%f\t%f' % (idx, name, list(ptc_out.shape), float(diff), float(ptc_mean), float(dark_mean)))


def verify_ptcaffe_darknet_train(lib, protofile, ptcmodel, cfgfile, weightfile):
    import ctypes
    import math
    import random
    
    #lib = CDLL("libdarknet.so", RTLD_GLOBAL)
    network_width = lib.network_width
    network_width.argtypes = [ctypes.c_void_p]
    network_width.restype = ctypes.c_int

    network_height = lib.network_height
    network_height.argtypes = [ctypes.c_void_p]
    network_height.restype = ctypes.c_int

    print_network = lib.print_network
    print_network.argtypes = [ctypes.c_void_p]

    get_network_outputs = lib.get_network_outputs
    get_network_outputs.argtypes = [ctypes.c_void_p]
    get_network_outputs.restype = ctypes.POINTER(ctypes.POINTER(ctypes.c_float))

    get_network_deltas = lib.get_network_deltas
    get_network_deltas.argtypes = [ctypes.c_void_p]
    get_network_deltas.restype = ctypes.POINTER(ctypes.POINTER(ctypes.c_float))
    
    network_forward_backward_debug = lib.network_forward_backward_debug
    network_forward_backward_debug.argtypes = [ctypes.c_void_p, ctypes.POINTER(ctypes.c_float), ctypes.POINTER(ctypes.c_float)]
    network_forward_backward_debug.restype = ctypes.POINTER(ctypes.c_float)
    
    set_batch_network = lib.set_batch_network
    set_batch_network.argtypes = [ctypes.c_void_p, ctypes.c_int]
    
    load_net = lib.load_network
    load_net.argtypes = [ctypes.c_char_p, ctypes.c_char_p, ctypes.c_int]
    load_net.restype = ctypes.c_void_p
    #-----------

    import numpy as np
    import torch
    from ptcaffe.caffenet import CaffeNet
    import ptcaffe.plugins.yolo
    from ptcaffe.plugins.yolo.pytorch_yolo2.utils import read_truths
    from PIL import Image
    import torchvision

    #1. create networks
    ptc_net = CaffeNet(protofile, phase='TRAIN')
    #ptc_net.set_verbose(3)
    ptc_net.load_model(ptcmodel)
    ptc_net.train()
    last_top = ptc_net.net_info['layers'][-1]['top']
    assert(not isinstance(last_top, list))
    ptc_net.set_outputs(last_top)

    if sys.version_info.major == 2:
        dark_net = load_net(cfgfile,  weightfile, 0)
    else:
        dark_net = load_net(cfgfile.encode('utf-8'),  weightfile.encode('utf-8'), 0)
    #set_batch_network(dark_net, 1)

    #2. inputs
    width = network_width(dark_net)
    height = network_height(dark_net)
    imgpath = os.getenv('HOME') + "/.ptcaffe/data/yolov2/train_verify416x416.png"
    labpath = os.getenv('HOME') + "/.ptcaffe/data/yolov2/train_verify416x416.txt"

    img = Image.open(imgpath).convert('RGB')
    img = torchvision.transforms.ToTensor()(img)
    assert(img.size(1) == height)
    assert(img.size(2) == width)

    label = torch.zeros(30 * 5)
    tmp = torch.from_numpy(read_truths(labpath).astype('float32')).view(-1)
    tsz = tmp.numel()
    label[0:tsz] = tmp
    dark_label = torch.cat((label.view(-1,5)[:,1:], label.view(-1,5)[:,:1]),1).view(1, -1)
    
    input_shape = [1, 3, height, width]
    print('input_shape: %s' % input_shape)
    ptc_input = img.view(input_shape)
    ptc_target = label.view(1,-1)
    dark_input = ptc_input.numpy().ctypes.data_as(ctypes.POINTER(ctypes.c_float))
    dark_target = dark_label.numpy().ctypes.data_as(ctypes.POINTER(ctypes.c_float))
    
    #3. compute outputs
    dark_out = network_forward_backward_debug(dark_net, dark_input, dark_target)
    #print_network(dark_net)

    ptc_net.net_info['props']['input'] = ['data', 'label']
    del ptc_net.net_info['props']['input_dim']
    data_input_shape = OrderedDict()
    data_input_shape['dim'] = ['1', '3', '416', '416']
    label_input_shape = OrderedDict()
    label_input_shape = OrderedDict()
    label_input_shape['dim'] = ['1', '150']
    ptc_net.net_info['props']['input_shape'] = [data_input_shape, label_input_shape]
    for layer in ptc_net.net_info['layers']:
        if layer['type'] in ['RegionLoss', 'YoloLoss']:
            layer['bottom'] = [layer['bottom'], 'label']

    new_protofile = protofile.replace('.prototxt', '.train.prototxt')
    print('save %s' % new_protofile)
    save_prototxt(ptc_net.net_info, new_protofile)

    #4. compute difference
    if False:
        ptc_out = ptc_net(ptc_input, ptc_target)[1]
        print('ptc_out: ', ptc_out)
        ptc_out.backward()
    
        dark_out = np.ctypeslib.as_array(ctypes.cast(dark_out, ctypes.POINTER(ctypes.c_float)), ptc_out.shape)
        dark_out = torch.from_numpy(dark_out)
        print('dark_out: ', dark_out)
    
        print('output_shape: %s' % list(ptc_out.shape))
        diff = (ptc_out - dark_out).abs().mean()
        print('verify diff: %f' % diff.item())
    else:
        ptc_net.VERIFY_DEBUG = True
        ptc_blobs = ptc_net(ptc_input, ptc_target)
        dark_blobs = get_network_outputs(dark_net)
        blob_names = cfg_blobs_in_ptcaffe(cfgfile)
    
        print('---------------------------')
        print('layer\t%-20s\t%-20s\toutput_diff\tptc_mean\tdark_mean' % ('name','shape'))
        for idx, name in enumerate(blob_names):
            ptc_out = ptc_blobs[name]
            dark_out = dark_blobs[idx]
            dark_out = np.ctypeslib.as_array(ctypes.cast(dark_out, ctypes.POINTER(ctypes.c_float)), ptc_out.shape)
            dark_out = torch.from_numpy(dark_out)
            diff = (ptc_out - dark_out).abs().mean()
            ptc_mean = ptc_out.abs().mean()
            dark_mean = dark_out.abs().mean()
            print('%5d\t%-20s\t%-20s\t%f\t%f\t%f' % (idx, name, list(ptc_out.shape), diff.item(), ptc_mean.item(), dark_mean.item()))

        # for backward
        if True:
            dark_deltas = get_network_deltas(dark_net) # n-1

            ptc_deltas = dict()
            def record_grad_hook(var_name):
                def record_grad(grad):
                    if var_name in ptc_deltas:
                        print('duplicated var_name: %s, first = %f, second = %f' % (var_name, ptc_deltas[var_name].abs().mean().item(), grad.abs().mean().item()))
                        ptc_deltas[var_name] += grad.clone()
                    else:
                        ptc_deltas[var_name] = grad.clone()
                return record_grad

            for name in blob_names:
                #ptc_blobs[name].grad.zero_()
                ptc_blobs[name].register_hook(record_grad_hook(name))

            grad_from_darknet=False
            if grad_from_darknet:
                last_second_top = ptc_net.net_info['layers'][-2]['top']
                ptc_var = ptc_blobs[last_second_top]
                dark_delta = dark_deltas[len(blob_names)-2]
                dark_delta = np.ctypeslib.as_array(ctypes.cast(dark_delta, ctypes.POINTER(ctypes.c_float)), ptc_var.shape)
                dark_delta = torch.from_numpy(dark_delta)
                ptc_var.backward(dark_delta)
            else:
                ptc_loss = torch.zeros(1)
                for layer in ptc_net.net_info['layers']:
                    if layer['type'] == 'YoloLoss':
                        tname = layer['top']
                        ptc_loss += ptc_blobs[tname]
                ptc_loss.backward()

            print('---------------------------')
            print('layer\t%-20s\t%-20s\tdelta_diff\tptc_mean\tdark_mean' % ('name','shape'))
            for idx, name in enumerate(blob_names):
                if grad_from_darknet:
                    if idx == len(blob_names) - 1: continue

                if name not in ptc_deltas: continue
                ptc_delta = ptc_deltas[name]
                dark_delta = dark_deltas[idx]
                dark_delta = np.ctypeslib.as_array(ctypes.cast(dark_delta, ctypes.POINTER(ctypes.c_float)), ptc_delta.shape)
                dark_delta = torch.from_numpy(dark_delta)
                diff = (ptc_delta + dark_delta).abs().mean()
                ptc_mean = ptc_delta.abs().mean()
                dark_mean = dark_delta.abs().mean()
                print('%5d\t%-20s\t%-20s\t%f\t%f\t%f' % (idx, name, list(ptc_delta.shape), diff.item(), ptc_mean.item(), dark_mean.item()))


#if __name__ == '__main__':

def main():
    import sys
    import ptcaffe
    print('ptcaffe %s' % ptcaffe.__version__)
    if len(sys.argv) != 5 and len(sys.argv) != 6 and len(sys.argv) != 7:
        print('Usage: darknet2ptcaffe model.cfg model.weights model.prototxt model.ptcmodel merge_scale train_verify')
        print('merge_scale: 0 or 1')
        print('train_verify: 0 or 1')
        exit()

    input_cfg = sys.argv[1]
    input_weights = sys.argv[2]
    output_protofile = sys.argv[3]
    output_weights = sys.argv[4]
    merge_scale = int(sys.argv[5]) if len(sys.argv) >= 6 else 1
    train_verify = int(sys.argv[6]) if len(sys.argv) >= 7 else 0

    darknet2ptcaffe(input_cfg, input_weights, output_protofile, output_weights, merge_scale)
    if train_verify:
        verify_ptcaffe_darknet_train(darknet_lib, output_protofile, output_weights, input_cfg, input_weights)
    else:
        verify_ptcaffe_darknet(darknet_lib, output_protofile, output_weights, input_cfg, input_weights)
