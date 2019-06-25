# --------------------------------------------------------
# ptcaffe
# Licensed under The MIT License [see LICENSE for details]
# Written by xiaohang
# --------------------------------------------------------

import torch
import onnx
import struct
from ptcaffe.caffenet import CaffeNet
from ptcaffe.utils.prototxt import save_prototxt
from collections import OrderedDict
from ptcaffe.utils.logger import logger

def onnx2prototxt(onnx_model, verbose=False):
    def dim_size(dims):
        count = 1
        for dim in dims:
            count *= dim
        return count
    graph = onnx_model.graph
    blob_mapping = dict()

    # 1. produce data names
    initializer_names = [item.name for item in graph.initializer]
    input_names = [item.name for item in graph.input]

    initializer_mapping = dict()
    for item in graph.initializer:
        initializer_mapping[item.name] = item
    input_mapping = dict()
    for item in graph.input:
        input_mapping[item.name] = item

    data_names = []
    for item in input_names:
        if not item in initializer_names:
            data_names.append(item)
    assert(len(data_names) > 0)

    props = OrderedDict()
    props['name'] = 'onnx2caffe model'
    if len(data_names) == 1:
        blob_mapping[data_names[0]] = 'data'
        props['input'] = 'data'
        props['input_shape'] = OrderedDict()
        dims = input_mapping[data_names[0]].type.tensor_type.shape.dim
        props['input_shape']['dim'] = [str(dim.dim_value) for dim in dims]
    else:
        props['input'] = []
        props['input_shape'] = []
        for idx, name in enumerate(data_names):
            input_name = 'data%d' % idx
            input_shape = OrderedDict()
            dims = input_mapping[name].type.tensor_type.shape.dim
            input_shape['dim'] = [str(dim.dim_value) for dim in dims]
            blob_mapping[name] = input_name
            props['input'].append(input_name)
            props['input_shape'].append(input_shape)
 
    # 2. create type_mapping
    type_mapping = {
                               'Conv': 'Convolution',
                               'Add' : 'Eltwise',
                            'Concat' : 'Concat',
                               'Relu': 'ReLU',
                            'MaxPool': 'Pooling',
                        'AveragePool': 'Pooling',
                               'Gemm': 'InnerProduct',
                            'Reshape': 'Reshape',
                            'Dropout': 'Dropout',
                            'Flatten': 'Flatten',
                 'BatchNormalization': 'BatchNorm',
                }
    weight_mapping = dict()

    # 3. convert layers
    layers = []
    relu_inplace = True
    prev_layer = OrderedDict()  # To merge Add and Conv
    for index in range(0,len(graph.node)):
        node    = graph.node[index]
        logger.debug('node%d type: %s' % (index, node.op_type))

        layer = OrderedDict()
        lname = str('layer%d_%s' % (index, node.op_type.lower()))
        ltype = type_mapping[node.op_type]
        layer['name']   = lname
        layer['type']   = ltype
        if node.op_type == 'Conv':
            assert(len(node.output) == 1)
            assert(node.input[0] in blob_mapping)
            layer['bottom'] = blob_mapping[node.input[0]]
            layer['top']    = lname
            blob_mapping[node.output[0]] = layer['top']
            convolution_param = OrderedDict()
            if len(node.input) == 2:
                convolution_param['bias_term'] = 'false'
            for attr in node.attribute:
                if attr.name == 'kernel_shape':
                    convolution_param['kernel_size'] = str(attr.ints[0])
                elif attr.name == 'strides':
                    convolution_param['stride'] = str(attr.ints[0])
                elif attr.name == 'pads':
                    convolution_param['pad'] = str(attr.ints[0])
                elif attr.name == 'dilations':
                    convolution_param['dilation'] = str(attr.ints[0])
                elif attr.name == 'group':
                    convolution_param['group'] = str(attr.i)
            layer['convolution_param'] = convolution_param
            layers.append(layer)

            weight = initializer_mapping[node.input[1]]
            if len(node.input) == 3:
                bias = initializer_mapping[node.input[2]]
            convolution_param['num_output'] = str(weight.dims[0])
            struct_fmt = '%df' % dim_size(weight.dims)
            weight_mapping[lname] = dict()
            weight_mapping[lname]['weight'] = struct.unpack(struct_fmt, weight.raw_data)
            if len(node.input) == 3:
                struct_fmt = '%df' % dim_size(bias.dims)
                weight_mapping[lname]['bias'] = struct.unpack(struct_fmt, bias.raw_data)
        elif node.op_type == 'BatchNormalization':
            assert(len(node.output) == 1)
            assert(node.input[0] in blob_mapping)
            layer['bottom'] = blob_mapping[node.input[0]]
            layer['top']    = lname #layer['bottom'] + '_bn'
            blob_mapping[node.output[0]] = layer['top']
            batch_norm_param = OrderedDict()
            batch_norm_param['affine'] = 'true'
            for attr in node.attribute:
                if attr.name == 'is_test':
                    if attr.i:
                        batch_norm_param['use_global_stats'] = 'true'
                elif attr.name == 'epsilon':
                    batch_norm_param['eps'] = str(attr.f)
                elif attr.name == 'momentum':
                    batch_norm_param['moving_average_fraction'] = str(attr.f)
            layer['batch_norm_param'] = batch_norm_param 
            layers.append(layer)

            weight       = initializer_mapping[node.input[1]]
            bias         = initializer_mapping[node.input[2]]
            running_mean = initializer_mapping[node.input[3]]
            running_var  = initializer_mapping[node.input[4]]
            bn_size      = dim_size(running_mean.dims)
            struct_fmt = '%df' % bn_size
            weight_mapping[lname] = dict()
            weight_mapping[lname]['weight']       = struct.unpack(struct_fmt, weight.raw_data)
            weight_mapping[lname]['bias']         = struct.unpack(struct_fmt, bias.raw_data)
            weight_mapping[lname]['running_mean'] = struct.unpack(struct_fmt, running_mean.raw_data)
            weight_mapping[lname]['running_var']  = struct.unpack(struct_fmt, running_var.raw_data)
        elif node.op_type == 'Relu':
            assert(len(node.output) == 1)
            assert(node.input[0] in blob_mapping)
            layer['bottom'] = blob_mapping[node.input[0]]
            if relu_inplace:
                layer['top']    = layer['bottom']
            else:
                layer['top']    = lname
            blob_mapping[node.output[0]] = layer['top']
            layers.append(layer)
        elif node.op_type == 'MaxPool':
            assert(len(node.output) == 1)
            assert(node.input[0] in blob_mapping)
            layer['bottom'] = blob_mapping[node.input[0]]
            layer['top']    = lname
            blob_mapping[node.output[0]] = layer['top']
            pooling_param = OrderedDict()
            pooling_param['pool'] = 'MAX'
            for attr in node.attribute:
                if attr.name == 'kernel_shape':
                    if len(attr.ints) == 1:
                        pooling_param['kernel_size'] = str(attr.ints[0])
                    elif len(attr.ints) >= 2:
                        if attr.ints[0] == attr.ints[1]:
                            pooling_param['kernel_size'] = str(attr.ints[0])
                        else:
                            pooling_param['kernel_h'] = str(attr.ints[0])
                            pooling_param['kernel_w'] = str(attr.ints[1])
                elif attr.name == 'pads':
                    if attr.ints[0] != 0:
                        pooling_param['pad'] = str(attr.ints[0])
                elif attr.name == 'strides':
                    pooling_param['stride'] = str(attr.ints[0])
            pooling_param['ceil_mode'] = 'false'
            layer['pooling_param'] = pooling_param
            layers.append(layer)
        elif node.op_type == 'AveragePool':
            assert(len(node.output) == 1)
            assert(node.input[0] in blob_mapping)
            layer['bottom'] = blob_mapping[node.input[0]]
            layer['top']    = lname
            blob_mapping[node.output[0]] = layer['top']
            pooling_param = OrderedDict()
            pooling_param['pool'] = 'AVE'
            for attr in node.attribute:
                if attr.name == 'kernel_shape':
                    if len(attr.ints) == 1:
                        pooling_param['kernel_size'] = str(attr.ints[0])
                    elif len(attr.ints) >= 2:
                        if attr.ints[0] == attr.ints[1]:
                            pooling_param['kernel_size'] = str(attr.ints[0])
                        else:
                            pooling_param['kernel_h'] = str(attr.ints[0])
                            pooling_param['kernel_w'] = str(attr.ints[1])
                elif attr.name == 'pads':
                    if attr.ints[0] != 0:
                        pooling_param['pad'] = str(attr.ints[0])
                elif attr.name == 'strides':
                    pooling_param['stride'] = str(attr.ints[0])
            layer['pooling_param'] = pooling_param
            layers.append(layer)
        elif node.op_type == 'Gemm':
            assert(len(node.output) == 1)
            assert(node.input[0] in blob_mapping)
            if prev_layer['type'] == 'Reshape':
                layer['bottom'] = prev_layer['bottom']
                blob_mapping[node.input[0]] = layer['bottom']
                layers.pop()
            else:
                layer['bottom'] = blob_mapping[node.input[0]]
            layer['top']    = lname
            blob_mapping[node.output[0]] = layer['top']

            inner_product_param = OrderedDict()
            layer['inner_product_param'] = inner_product_param
            layers.append(layer)

            weight       = initializer_mapping[node.input[1]]
            bias         = initializer_mapping[node.input[2]]
            inner_product_param['num_output'] = str(weight.dims[0])
            weight_size  = dim_size(weight.dims)
            bias_size    = dim_size(bias.dims)
            weight_fmt   = '%df' % weight_size
            bias_fmt     = '%df' % bias_size
            weight_mapping[lname] = dict()
            weight_mapping[lname]['weight'] = struct.unpack(weight_fmt, weight.raw_data)
            weight_mapping[lname]['bias'] = struct.unpack(bias_fmt, bias.raw_data)
        elif node.op_type == 'Reshape':
            assert(len(node.output) == 1)
            assert(node.input[0] in blob_mapping)
            layer['bottom'] = blob_mapping[node.input[0]]
            layer['top']    = lname
            blob_mapping[node.output[0]] = layer['top']
            layers.append(layer)
        elif node.op_type == 'Dropout':
            assert(node.input[0] in blob_mapping)
            assert(len(node.output) == 2)
            layer['bottom'] = blob_mapping[node.input[0]]
            layer['top']    = lname
            blob_mapping[node.output[0]] = layer['top']
            dropout_param = OrderedDict()
            dropout_param['dropout_ratio'] = str(node.attribute[1].f)
            layer['dropout_param'] = dropout_param
            layers.append(layer)
        elif node.op_type == 'Add':
            if node.input[1] in initializer_names:
                prev_layer['convolution_param']['bias_term'] = 'true'
                blob_mapping[node.output[0]] = blob_mapping[node.input[0]]
                bias = initializer_mapping[node.input[1]]
                struct_fmt = '%df' % bias.dims[0]
                weight_mapping[prev_layer['name']]['bias'] = struct.unpack(struct_fmt, bias.raw_data)
            else:
                assert(node.input[0] in blob_mapping)
                assert(node.input[1] in blob_mapping)
                layer['bottom'] = [blob_mapping[node.input[0]], blob_mapping[node.input[1]]]
                layer['top']    = lname
                blob_mapping[node.output[0]] = layer['top']
                layers.append(layer)
        elif node.op_type == 'Concat':
            layer['bottom'] = [blob_mapping[input] for input in node.input]
            layer['top']    = lname
            blob_mapping[node.output[0]] = layer['top']
            layers.append(layer)
        elif node.op_type == 'Flatten':
            assert(len(node.output) == 1)
            assert(node.input[0] in blob_mapping)
            layer['bottom'] = blob_mapping[node.input[0]]
            layer['top']    = lname
            blob_mapping[node.output[0]] = layer['top']
            flatten_param = OrderedDict()
            for attribute in node.attribute:
                if attribute.name == 'axis':
                    flatten_param['axis'] = attribute.i
            layer['flatten_param'] = flatten_param
            layers.append(layer)
        else:
            assert False, "unknown op_type %s" % node.op_type
        logger.debug('    %s' % layer)
        prev_layer = layer
    net_info = OrderedDict()
    net_info['props'] = props
    net_info['layers'] = layers
    return net_info, weight_mapping

def onnx2ptcaffe(onnx_model_file, protofile, weightfile, verbose=False):
    onnx_model = onnx.load(onnx_model_file)
    net_info, weight_mapping = onnx2prototxt(onnx_model, verbose)
    print("save %s" % protofile)
    save_prototxt(net_info, protofile)
    caffe_model = CaffeNet(protofile, phase='TEST')
    for key in weight_mapping.keys():
        logger.debug('processing layer %s' % key)
        onnx_weights = weight_mapping[key]
        if 'weight' in onnx_weights:
            logger.debug('   weight')
            weight_data = caffe_model.models[key].weight.data
            weight_data.copy_(torch.FloatTensor(onnx_weights['weight']).view_as(weight_data))
        if 'bias' in onnx_weights:
            logger.debug('   bias')
            bias_data = caffe_model.models[key].bias.data
            bias_data.copy_(torch.FloatTensor(onnx_weights['bias']).view_as(bias_data))
        if 'running_mean' in onnx_weights:
            logger.debug('   running_mean')
            running_mean = caffe_model.models[key].running_mean
            running_mean.copy_(torch.FloatTensor(onnx_weights['running_mean']).view_as(running_mean))
        if 'running_var' in onnx_weights:
            logger.debug('   running_var')
            running_var = caffe_model.models[key].running_var
            running_var.copy_(torch.FloatTensor(onnx_weights['running_var']).view_as(running_var))
    print("save %s" % weightfile)
    caffe_model.save_model(weightfile)

if __name__ == '__main__':
    #net_info = onnx2prototxt('alexnet.proto', 'alexnet.prototxt')
    onnx2ptcaffe('resnet50.proto', 'resnet50.prototxt', 'resnet50.ptcmodel')
