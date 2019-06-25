# --------------------------------------------------------
# ptcaffe
# Licensed under The MIT License [see LICENSE for details]
# Written by xiaohang
# --------------------------------------------------------

import torch
import sys
import json
from gluoncv import model_zoo
from mxnet import sym
from ptcaffe.caffenet import CaffeNet

#def data(txt_file, info):
#  txt_file.write('name: "mxnet-mdoel"\n')
#  txt_file.write('layer {\n')
#  txt_file.write('  name: "data"\n')
#  txt_file.write('  type: "Input"\n')
#  txt_file.write('  top: "data"\n')
#  txt_file.write('  input_param {\n')
#  txt_file.write('    shape: { dim: 10 dim: 3 dim: 224 dim: 224 }\n') # TODO
#  txt_file.write('  }\n')
#  txt_file.write('}\n')
#  txt_file.write('\n')

def data(txt_file, info):
  txt_file.write('name: "mxnet-mdoel"\n')
  txt_file.write('input: "data"\n')
  txt_file.write('input_shape { dim: 10 dim: 3 dim: 224 dim: 224 }\n') # TODO
  #txt_file.write('input_shape { dim: 10 dim: 3 dim: 299 dim: 299 }\n') # TODO
  txt_file.write('\n')

def Convolution(txt_file, info):
  if 'param' in info:
      info_param = info['param']
  elif 'attrs' in info:
      info_param = info['attrs']

  if info_param['no_bias'] == 'True':
    bias_term = 'false'
  else:
    bias_term = 'true'  
  txt_file.write('layer {\n')
  txt_file.write('  bottom: "%s"\n'       % info['bottom'][0])
  txt_file.write('  top: "%s"\n'          % info['top'])
  txt_file.write('  name: "%s"\n'         % info['top'])
  txt_file.write('  type: "Convolution"\n')
  txt_file.write('  convolution_param {\n')
  txt_file.write('    num_output: %s\n'   % info_param['num_filter'])
  kernel_size = info_param['kernel'].lstrip('(').rstrip(')').split(',')
  kernel_size = [i.strip() for i in kernel_size]
  if kernel_size[0] == kernel_size[1]:
    txt_file.write('    kernel_size: %s\n'  % kernel_size[0]) # TODO
  else:
    txt_file.write('    kernel_h: %s\n'  % kernel_size[0]) # TODO
    txt_file.write('    kernel_w: %s\n'  % kernel_size[1]) # TODO
  pads = info_param['pad'].lstrip('(').rstrip(')').split(',')
  pads = [i.strip() for i in pads]
  if pads[0] == pads[1]:
    txt_file.write('    pad: %s\n'          % pads[0]) # TODO
  else:
    txt_file.write('    pad_h: %s\n'          % pads[0]) # TODO
    txt_file.write('    pad_w: %s\n'          % pads[1]) # TODO
  txt_file.write('    group: %s\n'        % info_param['num_group'])
  strides = info_param['stride'].lstrip('(').rstrip(')').split(',')
  strides = [i.strip() for i in strides]
  if strides[0] == strides[1]:
    txt_file.write('    stride: %s\n'       % strides[0])
  else:
    txt_file.write('    stride_h: %s\n'       % strides[0])
    txt_file.write('    stride_w: %s\n'       % strides[1])
  txt_file.write('    bias_term: %s\n'    % bias_term)
  txt_file.write('  }\n')
  if 'share' in info.keys() and info['share']:  
    if info['params'][0] != 'data':
      txt_file.write('  param {\n')
      txt_file.write('    name: "%s"\n'     % info['params'][0])
      txt_file.write('  }\n')
  txt_file.write('}\n')
  txt_file.write('\n')

def ChannelwiseConvolution(txt_file, info):
  Convolution(txt_file, info)
  
def BatchNorm(txt_file, info):
  txt_file.write('layer {\n')
  txt_file.write('  bottom: "%s"\n'       % info['bottom'][0])
  txt_file.write('  top: "%s"\n'          % info['top'])
  txt_file.write('  name: "%s"\n'         % info['top'])
  txt_file.write('  type: "BatchNorm"\n')
  txt_file.write('  batch_norm_param {\n')
  txt_file.write('    use_global_stats: true\n')        # TODO
  txt_file.write('    moving_average_fraction: 0.9\n')  # TODO
  txt_file.write('    eps: 0.00001\n')                    # TODO
  txt_file.write('  }\n')
  txt_file.write('}\n')
  # if info['fix_gamma'] is "False":                    # TODO
  txt_file.write('layer {\n')
  txt_file.write('  bottom: "%s"\n'       % info['top'])
  txt_file.write('  top: "%s"\n'          % info['top'])
  txt_file.write('  name: "%s_scale"\n'   % info['top'])
  txt_file.write('  type: "Scale"\n')
  txt_file.write('  scale_param { bias_term: true }\n')
  txt_file.write('}\n')
  txt_file.write('\n')
  pass

def Activation(txt_file, info, is_leaky=False):
  txt_file.write('layer {\n')
  txt_file.write('  bottom: "%s"\n'       % info['bottom'][0])
  txt_file.write('  top: "%s"\n'          % info['top'])
  txt_file.write('  name: "%s"\n'         % info['top'])
  txt_file.write('  type: "ReLU"\n')      # TODO
  if is_leaky:
      txt_file.write('  relu_param {')
      txt_file.write('    negative_slope: 0.1')
      txt_file.write('  }')
  txt_file.write('}\n')
  txt_file.write('\n')
  pass

def Concat(txt_file, info):
  txt_file.write('layer {\n')
  txt_file.write('  name: "%s"\n'         % info['top'])
  txt_file.write('  type: "Concat"\n')
  for bottom_i in info['bottom']:
    txt_file.write('  bottom: "%s"\n'     % bottom_i)
  txt_file.write('  top: "%s"\n'          % info['top'])
  txt_file.write('}\n')
  txt_file.write('\n')
  pass
  
def ElementWiseAdd(txt_file, info):
  txt_file.write('layer {\n')
  txt_file.write('  name: "%s"\n'         % info['top'])
  txt_file.write('  type: "Eltwise"\n')
  for bottom_i in info['bottom']:
    txt_file.write('  bottom: "%s"\n'     % bottom_i)
  txt_file.write('  top: "%s"\n'          % info['top'])
  txt_file.write('}\n')
  txt_file.write('\n')
  pass

def ElementWiseSub(txt_file, info):
  txt_file.write('layer {\n')
  txt_file.write('  name: "%s"\n'         % info['top'])
  txt_file.write('  type: "Eltwise"\n')
  for bottom_i in info['bottom']:
    txt_file.write('  bottom: "%s"\n'     % bottom_i)
  txt_file.write('  top: "%s"\n'          % info['top'])
  txt_file.write('  eltwise_param {')
  txt_file.write('    operation: SUB')
  txt_file.write('  }')
  txt_file.write('}\n')
  txt_file.write('\n')


def ElementWiseMul(txt_file, info):
  txt_file.write('layer {\n')
  txt_file.write('  name: "%s"\n'         % info['top'])
  txt_file.write('  type: "Eltwise"\n')
  for bottom_i in info['bottom']:
    txt_file.write('  bottom: "%s"\n'     % bottom_i)
  txt_file.write('  top: "%s"\n'          % info['top'])
  txt_file.write('  eltwise_param {')
  txt_file.write('    operation: MUL')
  txt_file.write('  }')
  txt_file.write('}\n')
  txt_file.write('\n')

def AdaptiveAvgPool2d(txt_file, info):
  if 'param' in info:
      info_param = info['param']
  elif 'attrs' in info:
      info_param = info['attrs']
  txt_file.write('layer {\n')
  txt_file.write('  bottom: "%s"\n'       % info['bottom'][0])
  txt_file.write('  top: "%s"\n'          % info['top'])
  txt_file.write('  name: "%s"\n'         % info['top'])
  txt_file.write('  type: "AdaptiveAvgPool2d"\n')
  txt_file.write('  pytorch_param {\n')
  txt_file.write('    output_size: %s\n'  % info_param['output_size'])
  txt_file.write('  }\n')
  txt_file.write('}\n')
  txt_file.write('\n')
 

def Pooling(txt_file, info):
  if 'param' in info:
      info_param = info['param']
  elif 'attrs' in info:
      info_param = info['attrs']
  pool_type = 'AVE' if info_param['pool_type'] == 'avg' else 'MAX'
  txt_file.write('layer {\n')
  txt_file.write('  bottom: "%s"\n'       % info['bottom'][0])
  txt_file.write('  top: "%s"\n'          % info['top'])
  txt_file.write('  name: "%s"\n'         % info['top'])
  txt_file.write('  type: "Pooling"\n')
  txt_file.write('  pooling_param {\n')
  txt_file.write('    pool: %s\n'         % pool_type)       # TODO
  txt_file.write('    kernel_size: %s\n'  % info_param['kernel'].split('(')[1].split(',')[0])
  if 'stride' in info_param:
      txt_file.write('    stride: %s\n'       % info_param['stride'].split('(')[1].split(',')[0])
  else:
      txt_file.write('    stride: 1\n')
  if 'pad' in info_param:
      txt_file.write('    pad: %s\n'          % info_param['pad'].split('(')[1].split(',')[0])
  else:
      txt_file.write('    pad: 0\n')
  if 'global_pool' in info_param and info_param['global_pool'] == 'True':
      txt_file.write('    global_pooling: true\n')
  if 'pooling_convention' in info_param:
      if info_param['pooling_convention'] == 'full':
        txt_file.write('    ceil_mode: true\n')
      elif info_param['pooling_convention'] == 'valid':
        txt_file.write('    ceil_mode: false\n')
  else:
      txt_file.write('    ceil_mode: false\n')
  txt_file.write('  }\n')
  txt_file.write('}\n')
  txt_file.write('\n')
  pass


def FullyConnected(txt_file, info):
  if 'param' in info:
      info_param = info['param']
  elif 'attrs' in info:
      info_param = info['attrs']
  txt_file.write('layer {\n')
  txt_file.write('  bottom: "%s"\n'     % info['bottom'][0])
  txt_file.write('  top: "%s"\n'        % info['top'])
  txt_file.write('  name: "%s"\n'       % info['top'])
  txt_file.write('  type: "InnerProduct"\n')
  txt_file.write('  inner_product_param {\n')
  txt_file.write('    num_output: %s\n' % info_param['num_hidden'])
  txt_file.write('  }\n')
  txt_file.write('}\n')
  txt_file.write('\n')
  pass

def Flatten(txt_file, info):
  if 'param' in info:
      info_param = info['param']
  elif 'attrs' in info:
      info_param = info['attrs']
  txt_file.write('layer {\n')
  txt_file.write('  bottom: "%s"\n'     % info['bottom'][0])
  txt_file.write('  top: "%s"\n'        % info['top'])
  txt_file.write('  name: "%s"\n'       % info['top'])
  txt_file.write('  type: "Flatten"\n')
  txt_file.write('  flatten_param {\n')
  txt_file.write('    axis: %d\n' % 1)
  txt_file.write('  }\n')
  txt_file.write('}\n')
  txt_file.write('\n')

  pass

def Dropout(txt_file, info):
  if 'param' in info:
      info_param = info['param']
  elif 'attrs' in info:
      info_param = info['attrs']
  txt_file.write('layer {\n')
  txt_file.write('  bottom: "%s"\n'     % info['bottom'][0])
  txt_file.write('  top: "%s"\n'        % info['top'])
  txt_file.write('  name: "%s"\n'       % info['top'])
  txt_file.write('  type: "Dropout"\n')
  txt_file.write('  dropout_param {\n')
  txt_file.write('    dropout_ratio: %f\n' % float(info_param['p']))
  txt_file.write('  }\n')
  txt_file.write('}\n')
  txt_file.write('\n')



def SoftmaxOutput(txt_file, info):
  pass

def Reshape(txt_file, info):
  if 'param' in info:
      info_param = info['param']
  elif 'attrs' in info:
      info_param = info['attrs']
  txt_file.write('layer {\n')
  txt_file.write('  bottom: "%s"\n'     % info['bottom'][0])
  txt_file.write('  top: "%s"\n'        % info['top'])
  txt_file.write('  name: "%s"\n'       % info['top'])
  txt_file.write('  type: "Reshape"\n')
  txt_file.write('  reshape_param {\n')
  txt_file.write('    shape {\n')
  shapes = info_param['shape']
  shapes = str(shapes).lstrip('(').rstrip(')').split(',')
  shapes = [shape.strip() for shape in shapes]
  for dim in shapes:
      txt_file.write('      dim: %s\n' % dim)
  txt_file.write('    }\n')
  txt_file.write('  }\n')
  txt_file.write('}\n')
  txt_file.write('\n')
  pass

def Permute(txt_file, info):
  if 'param' in info:
      info_param = info['param']
  elif 'attrs' in info:
      info_param = info['attrs']
  info_param['axes'].strip('(').strip(')').split(',')
  txt_file.write('layer {\n')
  txt_file.write('  bottom: "%s"\n'     % info['bottom'][0])
  txt_file.write('  top: "%s"\n'        % info['top'])
  txt_file.write('  name: "%s"\n'       % info['top'])
  txt_file.write('  type: "Permute"\n')
  txt_file.write('  permute_param {\n')
  orders = info_param['axes']
  orders = str(orders).lstrip('(').rstrip(')').split(',')
  orders = [order.strip() for order in orders]
  for order in orders:
      txt_file.write('    order: %s\n' % order)
  txt_file.write('  }\n')
  txt_file.write('}\n')
  txt_file.write('\n')

def SliceAxis(txt_file, info):
  if 'param' in info:
      info_param = info['param']
  elif 'attrs' in info:
      info_param = info['attrs']
  txt_file.write('layer {\n')
  txt_file.write('  bottom: "%s"\n'    % info['bottom'][0])
  txt_file.write('  top: "%s"\n'       % info['top'])
  txt_file.write('  name: "%s"\n'      % info['top'])
  txt_file.write('  type: "SliceAxis"\n')
  txt_file.write('  slice_axis_param {')
  txt_file.write('    begin: %s' % str(info_param['begin']))
  txt_file.write('    end: %s' % str(info_param['end']))
  txt_file.write('    axis: %s' % str(info_param['axis']))
  txt_file.write('  }')
  txt_file.write('}\n')
  txt_file.write('\n')

def SliceLike(txt_file, info):
  txt_file.write('layer {\n')
  txt_file.write('  bottom: "%s"\n'    % info['bottom'][0])
  txt_file.write('  bottom: "%s"\n'    % info['params'])
  txt_file.write('  top: "%s"\n'       % info['top'])
  txt_file.write('  name: "%s"\n'      % info['top'])
  txt_file.write('  type: "SliceLike"\n')
  axes = str(info['attrs']['axes']).lstrip('(').rstrip(')').split(',')
  txt_file.write('  slice_like_param {')
  for axis in axes:
      txt_file.write('    axis: %s' % axis.strip())
  txt_file.write('  }')
  txt_file.write('}\n')
  txt_file.write('\n')

def Tile(txt_file, info):
  txt_file.write('layer {\n')
  txt_file.write('  bottom: "%s"\n'    % info['bottom'][0])
  txt_file.write('  top: "%s"\n'       % info['top'])
  txt_file.write('  name: "%s"\n'      % info['top'])
  txt_file.write('  type: "Tile"\n')
  dims = str(info['attrs']['reps']).lstrip('(').rstrip(')').split(',')
  txt_file.write('  tile_param {')
  for dim in dims:
      txt_file.write('    dim: %s' % dim.strip())
  txt_file.write('  }')
  txt_file.write('}\n')
  txt_file.write('\n')

def Repeat(txt_file, info):
  txt_file.write('layer {\n')
  txt_file.write('  bottom: "%s"\n'    % info['bottom'][0])
  txt_file.write('  top: "%s"\n'       % info['top'])
  txt_file.write('  name: "%s"\n'      % info['top'])
  txt_file.write('  type: "Repeat"\n')
  repeats = str(info['attrs']['repeats'])
  axis = str(info['attrs']['axis'])
  txt_file.write('  repeat_param {')
  txt_file.write('    axis: %s' % axis)
  txt_file.write('    repeats: %s' % repeats)
  txt_file.write('  }')
  txt_file.write('}\n')
  txt_file.write('\n')


def Unsqueeze(txt_file, info):
  if 'param' in info:
      info_param = info['param']
  elif 'attrs' in info:
      info_param = info['attrs']
  txt_file.write('layer {\n')
  txt_file.write('  bottom: "%s"\n'    % info['bottom'][0])
  txt_file.write('  top: "%s"\n'       % info['top'])
  txt_file.write('  name: "%s"\n'      % info['top'])
  txt_file.write('  type: "Unsqueeze"\n')
  txt_file.write('  unsqueeze_param {')
  txt_file.write('    dim: %s' % str(info_param['axis']))
  txt_file.write('  }')
  txt_file.write('}\n')
  txt_file.write('\n')

def MulScalar(txt_file, info):
  if 'param' in info:
      info_param = info['param']
  elif 'attrs' in info:
      info_param = info['attrs']
  txt_file.write('layer {\n')
  txt_file.write('  bottom: "%s"\n'    % info['bottom'][0])
  txt_file.write('  top: "%s"\n'       % info['top'])
  txt_file.write('  name: "%s"\n'      % info['top'])
  txt_file.write('  type: "MulScalar"\n')
  txt_file.write('  mul_scalar_param {')
  txt_file.write('    scalar: %s' % str(info_param['scalar']))
  txt_file.write('  }')
  txt_file.write('}\n')
  txt_file.write('\n')

def DivScalar(txt_file, info):
  if 'param' in info:
      info_param = info['param']
  elif 'attrs' in info:
      info_param = info['attrs']
  txt_file.write('layer {\n')
  txt_file.write('  bottom: "%s"\n'    % info['bottom'][0])
  txt_file.write('  top: "%s"\n'       % info['top'])
  txt_file.write('  name: "%s"\n'      % info['top'])
  txt_file.write('  type: "DivScalar"\n')
  txt_file.write('  div_scalar_param {')
  txt_file.write('    scalar: %s' % str(info_param['scalar']))
  txt_file.write('  }')
  txt_file.write('}\n')
  txt_file.write('\n')


def Arange(txt_file, info):
  if 'param' in info:
      info_param = info['param']
  elif 'attrs' in info:
      info_param = info['attrs']
  txt_file.write('layer {\n')
  txt_file.write('  top: "%s"\n'       % info['top'])
  txt_file.write('  name: "%s"\n'      % info['top'])
  txt_file.write('  type: "Arange"\n')
  txt_file.write('  arange_param {')
  txt_file.write('    start: %s' % str(info_param['start']))
  txt_file.write('    stop: %s' % str(info_param['stop']))
  txt_file.write('    step: %s' % str(info_param['step']))
  txt_file.write('  }')
  txt_file.write('}\n')
  txt_file.write('\n')

def ReLU6(txt_file, info):
  txt_file.write('layer {\n')
  txt_file.write('  bottom: "%s"\n'    % info['bottom'][0])
  txt_file.write('  top: "%s"\n'       % info['top'])
  txt_file.write('  name: "%s"\n'      % info['top'])
  txt_file.write('  type: "ReLU6"\n')
  txt_file.write('}\n')
  txt_file.write('\n')
  pass

def Sigmoid(txt_file, info):
  txt_file.write('layer {\n')
  txt_file.write('  bottom: "%s"\n'    % info['bottom'][0])
  txt_file.write('  top: "%s"\n'       % info['top'])
  txt_file.write('  name: "%s"\n'      % info['top'])
  txt_file.write('  type: "Sigmoid"\n')
  txt_file.write('}\n')
  txt_file.write('\n')
  pass

def Exp(txt_file, info):
  txt_file.write('layer {\n')
  txt_file.write('  bottom: "%s"\n'    % info['bottom'][0])
  txt_file.write('  top: "%s"\n'       % info['top'])
  txt_file.write('  name: "%s"\n'      % info['top'])
  txt_file.write('  type: "Exp"\n')
  txt_file.write('}\n')
  txt_file.write('\n')

def Mean(txt_file, info):
  txt_file.write('layer {\n')
  txt_file.write('  bottom: "%s"\n'    % info['bottom'][0])
  txt_file.write('  top: "%s"\n'       % info['top'])
  txt_file.write('  name: "%s"\n'      % info['top'])
  txt_file.write('  type: "Mean"\n')
  txt_file.write('}\n')
  txt_file.write('\n')


def ContribBoxNMS(txt_file, info):
  txt_file.write('layer {\n')
  txt_file.write('  bottom: "%s"\n'    % info['bottom'][0])
  txt_file.write('  top: "%s"\n'       % info['top'])
  txt_file.write('  name: "%s"\n'      % info['top'])
  txt_file.write('  type: "ContribBoxNMS"\n')
  txt_file.write('}\n')
  txt_file.write('\n')

  
# ----------------------------------------------------------------

def write_node(txt_file, info):
    if 'label' in info['name']:
        return        
    if info['op'] == 'null' and info['name'] == 'data':
        data(txt_file, info)
    elif info['op'] == 'Convolution':
        Convolution(txt_file, info)
    elif info['op'] == 'ChannelwiseConvolution':
        ChannelwiseConvolution(txt_file, info)
    elif info['op'] == 'BatchNorm':
        BatchNorm(txt_file, info)
    elif info['op'] == 'Activation':
        Activation(txt_file, info)
    elif info['op'] == 'LeakyReLU':
        Activation(txt_file, info, is_leaky=True)
    elif info['op'] == 'clip':
        ReLU6(txt_file, info)
    elif info['op'] in ['elemwise_add', 'ElementWiseSum']:
        ElementWiseAdd(txt_file, info)
    elif info['op'] in ['elemwise_sub', 'ElementWiseSub']:
        ElementWiseSub(txt_file, info)
    elif info['op'] == '_Plus':
        ElementWiseAdd(txt_file, info)
    elif info['op'] == 'Concat':
        Concat(txt_file, info)
    elif info['op'] == 'Pooling':
        Pooling(txt_file, info)
    elif info['op'] == 'Flatten':
        Flatten(txt_file, info)
    elif info['op'] == 'Dropout':
        Dropout(txt_file, info)
    elif info['op'] == 'FullyConnected':
        FullyConnected(txt_file, info)
    elif info['op'] == 'SoftmaxOutput':
        SoftmaxOutput(txt_file, info)
    elif info['op'] == 'Reshape':
        Reshape(txt_file, info)
    elif info['op'] == 'transpose':
        Permute(txt_file, info)
    elif info['op'] == 'slice_axis':
        SliceAxis(txt_file, info)
    elif info['op'] == 'slice_like':
        SliceLike(txt_file, info)
    elif info['op'] == 'tile':
        Tile(txt_file, info)
    elif info['op'] == 'repeat':
        Repeat(txt_file, info)
    elif info['op'] == 'sigmoid':
        Sigmoid(txt_file, info)
    elif info['op'] == 'exp':
        Exp(txt_file, info)
    elif info['op'] == 'mean':
        Mean(txt_file, info)
    elif info['op'] == 'broadcast_add':
        ElementWiseAdd(txt_file, info)
    elif info['op'] == 'broadcast_mul':
        ElementWiseMul(txt_file, info)
    elif info['op'] == 'expand_dims':
        Unsqueeze(txt_file, info)
    elif info['op'] == '_mul_scalar':
        MulScalar(txt_file, info)
    elif info['op'] == '_div_scalar':
        DivScalar(txt_file, info)
    elif info['op'] == '_arange':
        Arange(txt_file, info)
    elif info['op'] == '_contrib_box_nms':
        ContribBoxNMS(txt_file, info)
    elif info['op'] == '_contrib_AdaptiveAvgPooling2D':
        AdaptiveAvgPool2d(txt_file, info)
    else:
        import pdb; pdb.set_trace()
        sys.exit("Warning!  Unknown mxnet op:{}".format(info['op']))
        #print("Warning!  Unknown mxnet op:{}".format(info['op']))


def json2prototxt(mx_json_file, cf_prototxt_file):
    with open(mx_json_file) as json_file:    
      jdata = json.load(json_file)
    
    with open(cf_prototxt_file, "w") as prototxt_file:
      for i_node in range(0,len(jdata['nodes'])):
        node_i    = jdata['nodes'][i_node]
        if str(node_i['op']) == 'null' and str(node_i['name']) != 'data':
          continue
        
        print('{}, \top:{}, name:{} -> {}'.format(i_node,node_i['op'].ljust(20),
                                            node_i['name'].ljust(30),
                                            node_i['name']).ljust(20))
        info = node_i
        
        info['top'] = info['name']
        info['bottom'] = []
        info['params'] = []
        for input_idx_i in node_i['inputs']:
          input_i = jdata['nodes'][input_idx_i[0]]
          if str(input_i['op']) != 'null' or (str(input_i['name']) == 'data'):
            info['bottom'].append(str(input_i['name']))
          if str(input_i['op']) == 'null':
            info['params'].append(str(input_i['name']))
            if not str(input_i['name'].replace('_weight', '')).startswith(str(node_i['name']).replace('_fwd', '')):
              print('           use shared weight -> %s'% str(input_i['name']))
              info['share'] = True
          
        write_node(prototxt_file, info)

def gluon2ptcaffe(model_name):
    mx_json = '%s-symbol.json' % model_name
    cf_prototxt = '%s.prototxt' % model_name
    cf_model = '%s.ptcmodel' % model_name
    
    net_mx = model_zoo.get_model(model_name, pretrained=True, prefix='%s_' % model_name.replace('.', 'dot'))
    
    x = sym.var('data')
    y = net_mx(x)
    if isinstance(y, tuple):
        z = y[0].mean() + y[1].mean() + y[2].mean()
        z.save(mx_json)
    else:
        y.save(mx_json)
    json2prototxt(mx_json, cf_prototxt)
    
    mx_params = net_mx.collect_params()
    
    #from ptcaffe.utils.logger import logger
    #logger.set_level(logger.DEBUG)
    net_cf = CaffeNet(cf_prototxt, phase='TEST')
    cf_models = net_cf.models
    
    mx_keys = mx_params.keys()
    for i_key,key_i in enumerate(mx_keys):
    
      try:    
        if 'data' is key_i:
          pass
        elif '_weight' in key_i:
          key_caffe = key_i.replace('_weight','_fwd')
          cf_models[key_caffe].weight.data.copy_(torch.from_numpy(mx_params[key_i].data().asnumpy()))
        elif '_bias' in key_i:
          key_caffe = key_i.replace('_bias','_fwd')
          cf_models[key_caffe].bias.data.copy_(torch.from_numpy(mx_params[key_i].data().asnumpy()))
        elif '_gamma' in key_i:
          key_caffe = key_i.replace('_gamma','_fwd_scale')
          cf_models[key_caffe].weight.data.copy_(torch.from_numpy(mx_params[key_i].data().asnumpy()))
        elif '_beta' in key_i:
          key_caffe = key_i.replace('_beta','_fwd_scale')
          cf_models[key_caffe].bias.data.copy_(torch.from_numpy(mx_params[key_i].data().asnumpy()))
        elif '_running_mean' in key_i:
          key_caffe = key_i.replace('_running_mean','_fwd')
          cf_models[key_caffe].running_mean.copy_(torch.from_numpy(mx_params[key_i].data().asnumpy()))
        elif '_running_var' in key_i:
          key_caffe = key_i.replace('_running_var','_fwd')
          cf_models[key_caffe].running_var.copy_(torch.from_numpy(mx_params[key_i].data().asnumpy()))
        else:
          sys.exit("Warning!  Unknown mxnet:{}".format(key_i))
      
        print("% 3d | %s -> %s, initialized." 
               %(i_key, key_i.ljust(40), key_caffe.ljust(30)))
        
      except KeyError:
        print("\nWarning!  key error mxnet:{}".format(key_i))  
          
    # ------------------------------------------
    # Finish
    net_cf.save_model(cf_model)
    print("\n- Finished.\n")


if __name__ == '__main__':
    if len(sys.argv) == 2:
        gluon2ptcaffe(sys.argv[1])
    else:
        print('Usage: gluon2ptcaffe model_name')
        print('e.g. mobilenet1.0')
