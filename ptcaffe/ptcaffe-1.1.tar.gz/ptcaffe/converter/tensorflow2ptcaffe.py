from __future__ import division, print_function

import cv2
import numpy as np
import os,sys

import argparse
import torch
import ptcaffe
from ptcaffe.caffenet import CaffeNet
from ptcaffe.utils.config import cfg
from ptcaffe.utils.logger import logger
from ptcaffe.utils.utils import make_list, make_tuple, register_plugin
from ptcaffe.utils.prototxt import parse_prototxt, save_prototxt
import tensorflow as tf

default_input_size = 224
default_input_channel = 3
default_data_format = 'NHWC'
make_inplace_protofile = False

place_holders = []
node_dict = dict()

def forward_node(name, sess):
    input_node = tf.get_default_graph().get_tensor_by_name(place_holders[0] + ":0")
    input_shape = node_dict[place_holders[0]].attr['shape'].shape.dim
    input_shape = [dim.size for dim in input_shape]
    if len(input_shape) == 4:
        if input_shape[0] == -1: input_shape[0] = 1
        if input_shape[1] == -1: input_shape[1] = default_input_size
        if input_shape[2] == -1: input_shape[2] = default_input_size
        if input_shape[3] == -1: input_shape[3] = default_input_channel
    else:
        input_shape = [1, default_input_size, default_input_size, default_input_channel]
    return sess.run(tf.get_default_graph().get_tensor_by_name(name+":0"), feed_dict={input_node: torch.rand(input_shape).numpy()})


def Data(fp, t):
    dims = t.attr['shape'].shape.dim
    dims = [dim.size for dim in dims]
    if len(dims) == 0:
        dims = [1, default_input_size, default_input_size, default_input_channel]

    fp.write('layer {\n')
    fp.write('  name: "%s"\n' % t.name)
    fp.write('  type: "Input"\n')
    fp.write('  top: "%s"\n' % t.name)
    fp.write('  input_param {\n')
    fp.write('    shape {\n')
    if len(dims) != 4:
        for dim in dims:
            fp.write('      dim: %d\n' % dim)
    else:
        N = dims[0]
        H = dims[1]
        W = dims[2]
        C = dims[3]
        fp.write('      dim: %d\n' % N)
        fp.write('      dim: %d\n' % C)
        fp.write('      dim: %d\n' % H)
        fp.write('      dim: %d\n' % W)
    fp.write('    }\n')
    fp.write('  }\n')
    fp.write('}\n')
    fp.write('\n')

def make_str(s):
    if type(s) == bytes:
        return s.decode()
    else:
        return s

def Convolution(fp, t, bias=None): 
    assert(len(t.input) == 2)
    data_format = make_str(t.attr['data_format'].s)

    fp.write('layer {\n')
    fp.write('  bottom: "%s"\n' % t.input[0])
    if bias is None:
        fp.write('  top: "%s"\n' % t.name)
    else:
        fp.write('  top: "%s"\n' % bias.name)
    fp.write('  name: "%s"\n' % t.name)
    fp.write('  type: "Convolution"\n')
    fp.write('  convolution_param {\n')

    read_node = node_dict[t.input[1]]
    if read_node.op == 'Const':
        np.frombuffer(node_dict[t.input[1]].attr['value'].tensor.tensor_content, np.float32)
        weight_dims = read_node.attr['value'].tensor.tensor_shape.dim
        weight_dims = [dim.size for dim in weight_dims]
    else: #if read_node.op == 'Identity':
        weight_node = node_dict[read_node.input[0]]
        weight_dims = weight_node.attr['shape'].shape.dim
        if len(weight_dims) == 0:
            weight_dims = weight_node.attr['value'].tensor.tensor_shape.dim
        weight_dims = [weight_dims[i].size for i in range(len(weight_dims))]

    if t.op == 'DepthwiseConv2dNative':
        num_group = weight_dims[2]
        num_output = weight_dims[2]
        assert(weight_dims[3] == 1)
    else:
        num_output = weight_dims[3]
        num_group = 1
    fp.write('    num_output: %d\n' % num_output)
    fp.write('    group: %d\n'      % num_group)

    # kernel_size
    kernel_h = weight_dims[0]
    kernel_w = weight_dims[1]
    if kernel_h == kernel_w:
      kernel_size = kernel_w
      fp.write('    kernel_size: %d\n'  % kernel_size)
    else:
      fp.write('    kernel_h: %d\n'  % kernel_h)
      fp.write('    kernel_w: %d\n'  % kernel_w)

    # stride
    strides = t.attr['strides'].list.i
    if data_format == 'NCHW' or data_format == b'NCHW':
        stride_h = strides[2]
        stride_w = strides[3]
    else: #if data_format == 'NHWC' or data_format == b'NHWC':
        stride_h = strides[1]
        stride_w = strides[2]
    if stride_h == stride_w:
        fp.write('    stride: %d\n'       % stride_h)
    else:
        fp.write('    stride_h: %d\n'       % stride_h)
        fp.write('    stride_w: %d\n'       % stride_w)

    # padding
    padding = make_str(t.attr['padding'].s)
    fp.write('    tf_padding: "%s"\n' % padding)

    if bias is None:
        fp.write('    bias_term: false\n')
    fp.write('  }\n')
    fp.write('}\n')
    fp.write('\n')

def FusedBatchNorm(fp, t):
    fp.write('layer {\n')
    fp.write('  bottom: "%s"\n' % t.input[0])
    fp.write('  top: "%s"\n' % t.name)
    fp.write('  name: "%s"\n' % t.name)
    fp.write('  type: "BatchNorm"\n')
    fp.write('  batch_norm_param {\n')
    fp.write('    affine: true\n')

    #moving_average_fraction = 0.999
    #fp.write('    moving_average_fraction: %f\n' % moving_average_fraction)

    epsilon = t.attr['epsilon'].f
    fp.write('    eps: %f\n' % epsilon)

    fp.write('  }\n')
    fp.write('}\n')
    fp.write('\n')

def ElementWiseAdd(fp, t):
    fp.write('layer {\n')
    fp.write('  bottom: "%s"\n' % t.input[0])
    fp.write('  bottom: "%s"\n' % t.input[1])
    fp.write('  top: "%s"\n' % t.name)
    fp.write('  name: "%s"\n' % t.name)
    fp.write('  type: "Eltwise"\n')
    fp.write('  eltwise_param {\n')
    fp.write('    operation: SUM\n')
    fp.write('  \n}')
    fp.write('}\n')
    fp.write('\n')

def Concat(fp, t, sess):
    fp.write('layer {\n')
    N = t.attr['N'].i
    for idx in range(N):
        fp.write('  bottom: "%s"\n' % t.input[idx])
    input_node = forward_node(t.input[0], sess)
    axis = node_dict[t.input[N]].attr['value'].tensor.int_val[0]
    if input_node.ndim == 4: # NHWC
        shape_dict = [0,2,3,1]
        axis = shape_dict[axis]
    elif input_node.ndim == 3: # N?C
        shape_dict = [0, 2, 1]
        axis = shape_dict[axis]
    
    fp.write('  top: "%s"\n' % t.name)
    fp.write('  name: "%s"\n' % t.name)
    fp.write('  type: "Concat"\n')
    fp.write('  concat_param {\n')
    fp.write('    axis: %d\n' % axis)
    fp.write('  \n}')
    fp.write('}\n')
    fp.write('\n')


def Squeeze(fp, t):
    fp.write('layer {\n')
    fp.write('  bottom: "%s"\n' % t.input[0])
    fp.write('  top: "%s"\n' % t.name)
    fp.write('  name: "%s"\n' % t.name)
    fp.write('  type: "Squeeze"\n')
    fp.write('  squeeze_param {\n')
    dims = t.attr['squeeze_dims'].list.i
    if default_data_format == 'NHWC': #->NCHW
        for idx,dim in enumerate(dims):
            if dim == 0: dims[idx] = 0
            elif dim == 1: dims[idx] = 2
            elif dim == 2: dims[idx] = 3
            elif dim == 3: dims[idx] = 1

    for dim in dims:
        fp.write('    dim: %d\n' % dim)
    fp.write('  }\n')
    fp.write('}\n')
    fp.write('\n')

def ReLU(fp, t):
    fp.write('layer {\n')
    fp.write('  bottom: "%s"\n' % t.input[0])
    fp.write('  top: "%s"\n' % t.name)
    fp.write('  name: "%s"\n' % t.name)
    fp.write('  type: "ReLU"\n')
    fp.write('}\n')
    fp.write('\n')

def ReLU6(fp, t):
    fp.write('layer {\n')
    fp.write('  bottom: "%s"\n' % t.input[0])
    fp.write('  top: "%s"\n' % t.name)
    fp.write('  name: "%s"\n' % t.name)
    fp.write('  type: "ReLU6"\n')
    fp.write('}\n')
    fp.write('\n')

def Softmax(fp, t):
    fp.write('layer {\n')
    fp.write('  bottom: "%s"\n' % t.input[0])
    fp.write('  top: "%s"\n' % t.name)
    fp.write('  name: "%s"\n' % t.name)
    fp.write('  type: "Softmax"\n')
    fp.write('}\n')
    fp.write('\n')

def Identity(fp, t):
    fp.write('layer {\n')
    fp.write('  bottom: "%s"\n' % t.input[0])
    fp.write('  top: "%s"\n' % t.name)
    fp.write('  name: "%s"\n' % t.name)
    fp.write('  type: "Identity"\n')
    fp.write('}\n')
    fp.write('\n')

def Flatten(fp, t):
    fp.write('layer {\n')
    fp.write('  bottom: "%s"\n' % t.input[0])
    fp.write('  top: "%s"\n' % t.name)
    fp.write('  name: "%s"\n' % t.name)
    fp.write('  type: "Flatten"\n')
    fp.write('  flatten_param {\n')
    fp.write('    axis: 1\n')
    fp.write('  }\n')
    fp.write('}\n')
    fp.write('\n')

def Reshape(fp, t, sess):
    shape = np.frombuffer(node_dict[t.input[1]].attr['value'].tensor.tensor_content, dtype = np.int32)
    if len(shape) == 0:
        shape = forward_node(t.input[1], sess)

    if len(shape) == 4:
        shape = [shape[0], shape[3], shape[1], shape[2]]
    elif len(shape) == 3:
        shape = [shape[0], shape[2], shape[1]]
    else:
        if shape[0] == 1: shape[0] = -1

    fp.write('layer {\n')
    fp.write('  bottom: "%s"\n' % t.input[0])
    fp.write('  top: "%s"\n' % t.name)
    fp.write('  name: "%s"\n' % t.name)
    fp.write('  type: "Reshape"\n')
    fp.write('  reshape_param {\n')
    fp.write('    shape {\n')
    
    for dim in shape:
        fp.write('      dim: %d\n' % dim)
    fp.write('    }\n')
    fp.write('  }\n')
    fp.write('}\n')
    fp.write('\n')
  
def Pooling(fp, t):
    data_format = make_str(t.attr['data_format'].s)

    fp.write('layer {\n')
    fp.write('  bottom: "%s"\n'  % t.input[0])
    fp.write('  top: "%s"\n'  % t.name)
    fp.write('  name: "%s"\n'  % t.name)
    fp.write('  type: "Pooling"\n')
    fp.write('  pooling_param {\n')
    
    if t.op == 'MaxPool':
        fp.write('    pool: MAX\n')
    elif t.op == 'AvgPool':
        fp.write('    pool: AVE\n')

    ksize = t.attr['ksize'].list.i
    if data_format == 'NCHW' or data_format == b'NCHW':
        kernel_h = ksize[2]
        kernel_w = ksize[3]
    else: #if data_format == 'NHWC':
        kernel_h = ksize[1]
        kernel_w = ksize[2]
    if kernel_h == kernel_w:
        fp.write('    kernel_size: %d\n' % kernel_h)
    else:
        fp.write('    kernel_h: %d\n' % kernel_h)
        fp.write('    kernel_w: %d\n' % kernel_w)
   
    strides = t.attr['strides'].list.i
    if data_format == 'NCHW' or data_format == b'NCHW':
        stride_h = strides[2]
        stride_w = strides[3]
    else: #if data_format == 'NHWC':
        stride_h = strides[1]
        stride_w = strides[2]
    if stride_h == stride_w:
        fp.write('    stride: %d\n' % stride_h)
    else:
        fp.write('    stride_h: %d\n' % stride_h)
        fp.write('    stride_w: %d\n' % stride_w)

    padding = make_str(t.attr['padding'].s)
    assert(padding == 'VALID' or padding == b'VALID')
    if padding == 'VALID':
        fp.write('    pad:  0\n')
    #fp.write('    ceil_mode: true\n')
    fp.write('  }\n')
    fp.write('}\n')
    fp.write('\n')


def InnerProduct(fp, t, bias=None):
    fp.write('layer {\n')
    fp.write('  bottom: "%s"\n' % t.input[0])
    if bias is None:
        fp.write('  top: "%s"\n' % t.name)
    else:
        fp.write('  top: "%s"\n' % bias.name)
    fp.write('  name: "%s"\n' % t.name)
    fp.write('  type: "InnerProduct"\n')
    fp.write('  inner_product_param {\n')

    read_node = node_dict[t.input[1]]
    weight_node = node_dict[read_node.input[0]]
    weight_dims = weight_node.attr['shape'].shape.dim
    if len(weight_dims) == 0:
        weight_dims = weight_node.attr['value'].tensor.tensor_shape.dim
    weight_dims = [weight_dims[i].size for i in range(len(weight_dims))]
    num_output = weight_dims[1]
    fp.write('    num_output: %d\n' % num_output)
    fp.write('  }\n')
    fp.write('}\n')
    fp.write('\n')
 
#-----------------------------------------------------------
# sort graph

def create_input_dict(tensors):
    input_dict = dict()
    for t in tensors:
        if t.name not in input_dict:
            input_dict[t.name] = []
        for name in t.input:
            input_dict[t.name].append(name)
            if name not in input_dict:
                input_dict[name] = []
    return input_dict

def create_output_dict(tensors):
    output_dict = dict()
    for t in tensors:
        for name in t.input:
            if name not in output_dict:
                output_dict[name] = []
            output_dict[name].append(t.name) 
        if t.name not in output_dict:
            output_dict[t.name] = []
    return output_dict
            

def find_norely_nodes(input_dict):
    norely_nodes = []
    for key, value in input_dict.items():
        if len(value) == 0: norely_nodes.append(key)
    return norely_nodes

def remove_norely_nodes(norely_nodes, input_dict, output_dict):
    for name in norely_nodes:
        del input_dict[name]
    for name in norely_nodes:
        outputs = output_dict[name]
        for output in outputs:
            input_dict[output].remove(name)
        del output_dict[name]

def sort_tensors(tensors):
    name_dict = dict()
    for t in tensors: name_dict[t.name] = t

    input_dict = create_input_dict(tensors)
    output_dict = create_output_dict(tensors)
    output_names = []
    while len(input_dict) > 0:
        #print('len(input_dict) = %d' % len(input_dict))
        norely_nodes = find_norely_nodes(input_dict)
        remove_norely_nodes(norely_nodes, input_dict, output_dict)
        #print('len(norely_nodes) = %d' % len(norely_nodes))
        output_names += norely_nodes
        #print('len(output_names) = %d' % len(output_names))

    output_tensors = []
    for name in output_names:
        if name in name_dict:
            output_tensors.append(name_dict[name])
    return output_tensors

def find_biasadd_from(tensors):
    biasadd_from = dict()
    for t in tensors:
        if t.op == 'BiasAdd':
            biasadd_from[t.input[0]] = t
    return biasadd_from

#-----------------------------------------------------------

os.environ['CUDA_VISIBLE_DEVICES']='-1'
frozen_graph = sys.argv[1]

def tf2prototxt(frozen_graph, protofile, filter_domains):

    with tf.gfile.FastGFile(frozen_graph, 'rb') as graphfile:
        graphdef = tf.GraphDef()
        graphdef.ParseFromString(graphfile.read())
        tf.import_graph_def(graphdef, name='',return_elements=[])

    fp = open(protofile, 'w')
    fp.write('name: "tf2ptcaffe network"\n')
    fp.write('\n')
    
    with tf.Session() as sess:
        tensors = [tensor for tensor in graphdef.node]
        tensors = sort_tensors(tensors)
        for t in tensors:
            node_dict[t.name] = t

        biasadd_from = find_biasadd_from(tensors)

        for idx in range(len(tensors)):
            t = tensors[idx]
            #ts = tf.get_default_graph().get_tensor_by_name(t.name + ":0")
            #data = ts.eval()
            #print('t.name', t.name, t.input)
            if t.name.find('/Initializer/') >= 0: continue

            is_filtered = False
            for domain in filter_domains:
                if t.name.find(domain) == 0: 
                    is_filtered=True
                    break
            if is_filtered: continue

            if t.op == 'Assign': continue
            if t.op == 'Cast': continue
            if t.op == 'Shape': continue
    
            if t.op == 'Placeholder':
                Data(fp, t)
                place_holders.append(t.name)
            elif t.op == 'VariableV2':
                continue
            elif t.op == 'Identity':
                if t.name.split('/')[-1] == 'read':
                    continue
                    #node_dict[t.name] = node_dict[t.input[0]]
                    #del node_dict[t.input[0]]
                else:
                    Identity(fp, t)
            elif t.op == 'Const':
                continue 
            elif t.op == 'Conv2D':
                if idx != len(tensors) - 1 and t.name in biasadd_from: #tensors[idx+1].op == 'BiasAdd':
                    #Convolution(fp, t, tensors[idx+1])
                    Convolution(fp, t, biasadd_from[t.name])
                else:
                    Convolution(fp, t)
            elif t.op == 'BiasAdd':
                continue
            elif t.op == 'DepthwiseConv2dNative':
                if idx != len(tensors) - 1 and tensors[idx+1].op == 'BiasAdd':
                    Convolution(fp, t, tensors[idx+1])
                else:
                    Convolution(fp, t)
            elif t.op == 'FusedBatchNorm':
                FusedBatchNorm(fp, t)
            elif t.op == 'Relu':
                ReLU(fp, t)
            elif t.op == 'Relu6':
                ReLU6(fp, t)
            elif t.op == 'MaxPool':
                Pooling(fp, t)
            elif t.op == 'StridedSlice':
                continue
            elif t.op == 'Pack':
                continue
            elif t.op == 'Reshape':
                if t.name.find('/flatten/Reshape') > 0:
                    Flatten(fp, t)
                else:
                    Reshape(fp, t, sess)
            elif t.op == 'MatMul':
                if idx != len(tensors) - 1 and t.name in biasadd_from: #tensors[idx+1].op == 'BiasAdd':
                    #InnerProduct(fp, t, tensors[idx+1])
                    InnerProduct(fp, t, biasadd_from[t.name])
                else:
                    InnerProduct(fp, t, None)
            elif t.op == 'Softmax':
                Softmax(fp, t)
            elif t.op == 'Add':
                ElementWiseAdd(fp, t)
            elif t.op == 'AvgPool':
                Pooling(fp, t)
            elif t.op == 'Squeeze':
                Squeeze(fp, t)
            elif t.op == 'ConcatV2':
                Concat(fp, t, sess)
            else:
                print('Unknown op %s' % t.op)
    fp.close()

    if len(filter_domains) > 0:
        filter_protofile(protofile, protofile)

#------------ set ------------
def set_id(name, set_list):
    for idx,s in enumerate(set_list):
        if name in s: return idx
    return -1

def create_set(name, set_list):
    for s in set_list:
        if name in s:
            break
    set_list.append(set([name]))

def merge_sets(node1, node2, set_list):
    id1 = set_id(node1, set_list)
    id2 = set_id(node2, set_list)
    if id1 != id2:
        set1 = set_list[id1]
        set2 = set_list[id2]
        for item in set1:
            set2.add(item)
        del set_list[id1]

def find_largest_set(set_list):
    set_size = [0] * len(set_list)
    set_size = [len(s) for s in set_list]
    max_id = set_size.index(max(set_size))
    return set_list[max_id]

def filter_protofile(in_protofile, out_protofile):
    set_list = []
    net_info = parse_prototxt(in_protofile)
    layers = net_info['layers']

    # create set list
    blob_from = dict()
    for layer in layers:
        lname = layer['name']
        create_set(lname, set_list)

        bnames = make_list(layer['bottom']) if 'bottom' in layer else []
        tnames = make_list(layer['top']) if 'top' in layer else []
        for bname in bnames:
            if bname in blob_from:
                bnode = blob_from[bname]
                merge_sets(bnode, lname, set_list)
        for tname in tnames:
            blob_from[tname] = lname

    # find largest set
    largest_set = find_largest_set(set_list)

    # find layers in largest set
    new_layers = []
    for layer in layers:
        lname = layer['name']
        if lname in largest_set:
            new_layers.append(layer)

    # find inputs
    if 'bottom' in new_layers[0]:
        input_shape = [1, 3, default_input_size, default_input_size]
        input_name = new_layers[0]['bottom']
        net_info['props']['input'] = input_name
        net_info['props']['input_dim'] = input_shape
        net_info['layers'] = new_layers
        save_prototxt(net_info, out_protofile)

#-----------------------------

def get_next_name(ltype, name_mapping):
    base_name = ltype.lower()
    idx = 1
    new_name = "%s%d" % (base_name, idx)
    while new_name in name_mapping():
        idx += 1
        new_name = "%s%d" % (base_name, idx)

    return new_name


def tf2ptcaffe(frozen_graph, protofile, ptcmodel, filter_domains):
    tf2prototxt(frozen_graph, protofile, filter_domains)

    sess = tf.Session()

    #from ptcaffe.utils.logger import logger
    #logger.set_level(logger.DEBUG)

    cf_net = CaffeNet(protofile, phase='TEST')
    cf_models = cf_net.models
    net_info = cf_net.net_info
    layers = net_info['layers']
    for layer in layers:
        lname = layer['name']
        ltype = layer['type']
        if ltype in ['Convolution', 'InnerProduct']:
            self_node = node_dict[lname]
            read_node = node_dict[self_node.input[1]]
            if read_node.op == 'Const':
                dims = read_node.attr['value'].tensor.tensor_shape.dim
                dims = [dim.size for dim in dims]
                tf_weight = np.frombuffer(read_node.attr['value'].tensor.tensor_content, np.float32).reshape(dims)
            else: #if read_node.op == 'Identity':
                weight_node = node_dict[read_node.input[0]]
                weight_name = weight_node.name
                tf_weight = sess.run(tf.get_default_graph().get_tensor_by_name(weight_name + ":0"))
            if ltype == 'Convolution':
                if self_node.op == 'Conv2D':
                    cf_models[lname].weight.data.copy_(torch.from_numpy(tf_weight.transpose((3,2,0,1))))
                elif self_node.op == 'DepthwiseConv2dNative':
                    cf_models[lname].weight.data.copy_(torch.from_numpy(tf_weight.transpose((2,3,0,1))))
                convolution_param = layer['convolution_param']
                bias_term = (convolution_param.get('bias_term', 'true') == 'true')
            else:
                cf_models[lname].weight.data.copy_(torch.from_numpy(tf_weight.transpose((1,0))))
                inner_product_param = layer['inner_product_param']
                bias_term = (inner_product_param.get('bias_term', 'true') == 'true')

            if bias_term:
                top = layer['top']
                biasadd_node = node_dict[top]
                read_node = node_dict[biasadd_node.input[1]]
                if read_node.op == 'Const':
                    tf_bias = np.frombuffer(read_node.attr['value'].tensor.tensor_content, np.float32)
                else: #if read_node.op == 'Identity':
                    bias_node = node_dict[read_node.input[0]]
                    bias_name = bias_node.name
                    tf_bias = sess.run(tf.get_default_graph().get_tensor_by_name(bias_name + ":0"))
                cf_models[lname].bias.data.copy_(torch.from_numpy(tf_bias))
        elif ltype == 'BatchNorm':
            self_node = node_dict[lname]
            weights = []
            for i in range(1,5):
                input_node = node_dict[self_node.input[i]]
                if input_node.op == 'Const':
                    weight = np.frombuffer(input_node.attr['value'].tensor.tensor_content, np.float32)
                else:
                    weight = np.frombuffer(node_dict[input_node.input[0]].attr['value'].tensor.tensor_content, dtype = np.float32)
                #weight = sess.run(tf.get_default_graph().get_tensor_by_name(self_node.input[i] + ":0"))
                weights.append(weight)
            cf_models[lname].weight.data.copy_(torch.from_numpy(weights[0]))
            cf_models[lname].bias.data.copy_(torch.from_numpy(weights[1]))
            cf_models[lname].running_mean.data.copy_(torch.from_numpy(weights[2]))
            cf_models[lname].running_var.data.copy_(torch.from_numpy(weights[3]))

    cf_net.save_model(ptcmodel)

    # ------- verify -------
    if cfg.VERBOSE_LEVEL >= 2:
        cf_net.set_automatic_outputs()
        cf_net.VERIFY_DEBUG = True

        input_shape = cf_net.get_input_shapes()
        input_shape[0] = 1
        cf_input_data = torch.rand(input_shape)
        tf_input_data = cf_input_data.numpy().transpose(0,2,3,1)

        input_name = make_list(cf_net.get_input_names())[0]
        cf_result_dict = cf_net(cf_input_data)

        output_keys = cf_result_dict.keys()
        tf_output_nodes = [tf.get_default_graph().get_tensor_by_name(output_name + ':0') for output_name in output_keys]
        tf_input_node = tf.get_default_graph().get_tensor_by_name(input_name + ':0')
        tf_results = sess.run(tf_output_nodes, feed_dict={tf_input_node: tf_input_data})

        for idx,key in enumerate(output_keys):
            cf_result = cf_result_dict[key].detach().numpy()
            tf_result = tf_results[idx]
            if cf_result.ndim == 4:
                cf_result = cf_result.transpose(0,2,3,1)
            try:
                diff = float((abs(tf_result - cf_result)).mean())
                print('%40s\tdiff = %f' % (key, diff))
            except:
                print('%40s\tdiff = NAN' % (key))
    else:
        cf_net.set_automatic_outputs()
    
        input_shape = cf_net.get_input_shapes()
        input_shape[0] = 1
        cf_input_data = torch.rand(input_shape)
        tf_input_data = cf_input_data.numpy().transpose(0,2,3,1)
    
        input_name = make_list(cf_net.get_input_names())[0]
        output_name = cf_net.eval_outputs[0]
    
        tf_input_node = tf.get_default_graph().get_tensor_by_name(input_name + ':0')
        tf_output_node = tf.get_default_graph().get_tensor_by_name(output_name + ':0')
        tf_result = sess.run(tf_output_node, feed_dict={tf_input_node: tf_input_data})
    
        if len(cf_net.eval_outputs) > 1:
            cf_result = cf_net(cf_input_data)[0].detach().numpy()
    
        else:
            cf_result = cf_net(cf_input_data).detach().numpy()
    
        diff = float((abs(tf_result - cf_result)).mean())
        print('diff = %f' % diff)

#-------------- simplify names ----------------

def get_valid_name(ltype, name_set):
    idx = 1
    while True:
        if ltype == 'Convolution':
            valid_name = "conv%d" % idx
        elif ltype == 'ReLU6':
            valid_name = "relu%d" % idx
        elif ltype == 'BatchNorm':
            valid_name = "bn%d" % idx
        else:
            valid_name = "%s%d" % (ltype.lower(), idx)
        if valid_name not in name_set:
            break
        else:
            idx += 1
    return valid_name


def make_top_sameas_lname(layers):
    name_mapping = dict()
    for layer in layers:
        lname = layer['name']
        bnames = make_list(layer['bottom']) if 'bottom' in layer else []
        new_bnames = [name_mapping[bname] if bname in name_mapping else bname for bname in bnames]
        if len(bnames) == 1: layer['bottom'] = new_bnames[0]
        elif len(bnames) > 1: layer['bottom'] = new_bnames
 
        if 'top' in layer:
            top = layer['top']
            if top != lname:
                name_mapping[top] = lname 
                layer['top'] = lname

def make_inplace_top(layers):
    name_mapping = dict()
    for layer in layers:
        lname = layer['name']
        ltype = layer['type']
        bnames = make_list(layer['bottom']) if 'bottom' in layer else []
        new_bnames = [name_mapping[bname] if bname in name_mapping else bname for bname in bnames]
        if len(bnames) == 1: layer['bottom'] = new_bnames[0]
        elif len(bnames) > 1: layer['bottom'] = new_bnames
 
        if 'top' in layer:
            top = layer['top']
            if ltype in ['BatchNorm', 'Scale', 'ReLU', 'ReLU6']:
                name_mapping[top] = new_bnames[0]
                layer['top'] = new_bnames[0]

def simplify_protofile(in_protofile, out_protofile):
    name_set = set()

    net = CaffeNet(in_protofile, phase='TEST')
    net.set_automatic_outputs()
    net_info = net.net_info
    input_names = make_list(net.get_input_names())

    make_top_sameas_lname(net_info['layers'])
    if make_inplace_protofile:
        make_inplace_top(net_info['layers'])

    for name in input_names:
        name_set.add(name)
    for layer in net_info['layers']:
        name_set.add(layer['name'])

    name_dict = dict()
    for idx,name in enumerate(input_names):
        new_name = 'data%d' % idx
        name_dict[name] = new_name
        name_set.add(new_name)

    for layer in net_info['layers']:
        ltype = layer['type']
        lname = layer['name']
        new_lname = get_valid_name(ltype, name_set)
        name_set.add(new_lname)
        name_dict[lname] = new_lname 

    for idx,out_name in enumerate(net.eval_outputs):
        if out_name not in name_dict:
            new_name = "output%d" % idx
            name_dict[out_name] = new_name

    if 'input' in net_info['props']:
        old_names = make_list(net_info['props']['input'])
        new_names = [name_dict[old_name] for old_name in old_names]
        if len(old_names) == 1:
            net_info['props']['input'] = new_names[0]
        elif len(old_names) > 1:
            net_info['props']['input'] = new_names

    for layer in net_info['layers']:
        bnames = make_list(layer['bottom']) if 'bottom' in layer else []
        tnames = make_list(layer['top']) if 'top' in layer else []
        new_bnames = [name_dict[old_name] if old_name in name_dict else old_name for old_name in bnames]
        new_tnames = [name_dict[old_name] if old_name in name_dict else old_name for old_name in tnames]
        if len(bnames) == 1: layer['bottom'] = new_bnames[0]
        elif len(bnames) > 1: layer['bottom'] = new_bnames
        if len(tnames) == 1: layer['top'] = new_tnames[0]
        elif len(tnames) > 1: layer['top'] = new_tnames
        layer['name'] = name_dict[layer['name']]
    save_prototxt(net_info, out_protofile) 

def simplify_model_names(in_protofile, in_weightfile, out_protofile, out_weightfile):
    simplify_protofile(in_protofile, out_protofile)

    net = CaffeNet(out_protofile, phase='TEST')
    net.load_renamed_model(in_weightfile)
    net.save_model(out_weightfile)

    # verify difference
    print('-------------- verifying simplified network -------------')
    net1 = CaffeNet(in_protofile, phase='TEST')
    net1.load_model(in_weightfile)
    if make_inplace_protofile:
        net1.set_automatic_outputs()
    else:
        net1.VERIFY_DEBUG = True

    net2 = CaffeNet(out_protofile, phase='TEST')
    net2.load_model(out_weightfile)
    if make_inplace_protofile:
        net2.set_automatic_outputs()
    else:
        net2.VERIFY_DEBUG = True

    input_shape = net1.get_input_shapes()
    input_data = torch.rand(input_shape)

    if make_inplace_protofile:
        outputs1 = make_tuple(net1(input_data))
        outputs2 = make_tuple(net2(input_data))
        for idx, (out1, out2) in enumerate(zip(outputs1, outputs2)):
            diff = float((out1 - out2).abs().mean())
            print('diff%d = %f' % (idx, diff))
    else:
        dict1 = net1(input_data)
        dict2 = net2(input_data)

        assert(len(dict1) == len(dict2))
    
        keys1 = dict1.keys()
        keys2 = dict2.keys()
        for key1, key2 in zip(keys1, keys2):
            output1 = dict1[key1]
            output2 = dict2[key2]
            diff = float((output1 - output2).abs().mean())
            print('%-30s -> %-15s\tdiff = %f' % (key1, key2, diff))
    
#-----------------------------------------------


if __name__ == '__main__':
    #tf2prototxt(sys.argv[1], sys.argv[2])
    #tf2ptcaffe(sys.argv[1], sys.argv[2], sys.argv[3])
    main()


def build_parser():
    parser = argparse.ArgumentParser(description='convert tensorflow model to ptcaffe model', usage='tensorflow2ptcaffe input_frozen.pb output_prototxt output_caffemodel', epilog="welcome!")
    parser.add_argument('params', help="input_frozen.pb output_prototxt output_caffemodel", nargs="+")
    parser.add_argument('--verbose', type=int, help='Optional; verbose level 0: no info, 1: receptive field, 2: debug')
    parser.add_argument('--plugin', help='Optional; enable plugin')
    parser.add_argument('--filter', help='Optional; filter out domains')
    parser.add_argument('--input_size', help='Optional; input image size')
    parser.add_argument('--input_channel', help='Optional; input image channel')
    parser.add_argument('--simplify', action='store_true', default=False, help='Optional; simplify names in protofile')
    parser.add_argument('--inplace', action='store_true', default=False, help='Optional; make inplace top for batchnorm, scale, relu, relu6')
    return parser

def main():
    print('ptcaffe %s' % ptcaffe.__version__)
    
    parser = build_parser()
    args = parser.parse_args()
    print('args: %s' % args)

    register_plugin(args.plugin)
    if args.verbose is not None:
        cfg.VERBOSE_LEVEL = args.verbose
        if args.verbose == 0:
            logger.set_level(logger.INFO)
        elif args.verbose == 1:
            logger.set_level(logger.MORE_INFO)
        elif args.verbose >= 2:
            logger.set_level(logger.DEBUG)

    global default_input_size
    global default_input_channel
    default_input_size = int(args.input_size) if args.input_size else default_input_size
    default_input_channel = int(args.input_channel) if args.input_channel else default_input_channel
    if len(args.params) == 2:
        input_frozen_pb   = args.params[0]
        output_protofile = args.params[1]
        filter_domains = args.filter
        print('input_frozen_pb = %s' % input_frozen_pb)
        print('output_protofile = %s' % output_protofile)
        if filter_domains is not None:
            print('filter_domains = %s' % filter_domains)
        if filter_domains:
            filter_domains = filter_domains.split(',')
        else:
            filter_domains = []
        tf2prototxt(input_frozen_pb, output_protofile, filter_domains)
    elif len(args.params) == 3:
        input_frozen_pb   = args.params[0]
        output_protofile = args.params[1]
        output_ptcmodel   = args.params[2]
        filter_domains = args.filter

        print('input_frozen_pb = %s' % input_frozen_pb)
        print('output_protofile = %s' % output_protofile)
        print('output_ptcmodel = %s' % output_ptcmodel)
        if filter_domains is not None:
            print('filter_domains = %s' % filter_domains)
        if filter_domains:
            filter_domains = filter_domains.split(',')
        else:
            filter_domains = []

        if args.simplify:
            if args.inplace: 
                global make_inplace_protofile
                make_inplace_protofile = True
            tf2ptcaffe(input_frozen_pb, ".tmp.prototxt", ".tmp.ptcmodel", filter_domains)
            simplify_model_names(".tmp.prototxt", ".tmp.ptcmodel", output_protofile, output_ptcmodel)
            os.remove('.tmp.prototxt')
            os.remove('.tmp.ptcmodel')
        else:
            tf2ptcaffe(input_frozen_pb, output_protofile, output_ptcmodel, filter_domains)
