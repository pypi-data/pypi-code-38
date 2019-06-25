# --------------------------------------------------------
# ptcaffe
# Licensed under The MIT License [see LICENSE for details]
# Written by xiaohang 2018.3
# --------------------------------------------------------

import argparse
import torch

import ptcaffe
from ptcaffe.tools.pytorch2ptcaffe.onnx2ptcaffe import onnx2ptcaffe
from ptcaffe.utils.prototxt import save_prototxt
from ptcaffe.caffenet import CaffeNet
from ptcaffe.utils.config import cfg
from ptcaffe.utils.logger import logger
from ptcaffe.utils.utils import register_plugin

def pytorch2ptcaffe(input_protofile, input_ptcmodel, output_protofile, output_ptcmodel):
    input_net = CaffeNet(input_protofile)
    input_net.load_model(input_ptcmodel)
    input_net.set_automatic_outputs()
    input_net.eval()
    onnx_protofile = input_protofile.replace('.prototxt', '.onnx.proto')
    input_shape = input_net.get_input_shapes()
    assert(not isinstance(input_shape[0], list))
    dummy_input = torch.randn(input_shape)
    verbose =  (cfg.VERBOSE_LEVEL == 1)
    torch.onnx.export(input_net, dummy_input, onnx_protofile, verbose=verbose)
    onnx2ptcaffe(onnx_protofile, output_protofile, output_ptcmodel)

    # verify
    output_net = CaffeNet(output_protofile, phase='TEST')
    output_net.load_model(output_ptcmodel)
    output_net.set_automatic_outputs()
    output_net.eval()

    input = torch.randn(input_shape)
    pytorch_output = input_net(input)
    ptcaffe_output = output_net(input)

    diff = (pytorch_output - ptcaffe_output).data.abs().mean()
    print('difference between pytorch and ptcaffe: %f' % diff)
   
def test():
    from collections import OrderedDict
    props = OrderedDict()
    props['name'] = 'resnet50'
    props['input'] = 'data'
    props['input_dim'] = ['1', '3', '224', '224']
    layers = []
    layer = OrderedDict()
    layer['bottom'] = 'data'
    layer['name'] = 'resnet50'
    layer['type'] = 'TorchVisionModel'
    layer['top'] = 'fc1000'
    model_param = OrderedDict()
    model_param['model_name'] = 'resnet50'
    model_param['pretrained'] = 'true'
    model_param['num_classes'] = '1000'
    layer['model_param'] = model_param
    layers.append(layer)
    net_info = OrderedDict()
    net_info['props'] = props
    net_info['layers'] = layers
    save_prototxt(net_info, 'input.prototxt')
    input_net = CaffeNet('input.prototxt', phase='TEST')
    input_net.save_model('input.ptcmodel')
    pytorch2ptcaffe('input.prototxt', 'input.ptcmodel', 'output.prototxt', 'output.ptcmodel')

def build_parser():
    parser = argparse.ArgumentParser(description='convert caffe model to ptcaffe model', usage='ptcaffe2caffe input_prototxt input_ptcmodel output_prototxt output_caffemodel', epilog="welcome!")
    parser.add_argument('params', help="input_prototxt input_ptcmodel output_prototxt output_caffemodel", nargs="+")
    #parser.add_argument('--phase', help='Optional; network phase (TRAIN or TEST)')
    #parser.add_argument('--gpu', help='Optional; run in GPU mode on given device IDs separated by ","')
    parser.add_argument('--verbose', type=int, help='Optional; verbose level 0: no info, 1: receptive field, 2: debug')
    parser.add_argument('--plugin', choices=['faster_rcnn', 'ssd', 'yolo', 'caffe'], help='Optional; enable plugin')
    return parser

def main():
    print('ptcaffe %s' % ptcaffe.__version__)
    print('currently only support pytorch 0.4.0 and onnx 1.3.0')
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

    if len(args.params) == 1 and args.params[0] == 'test':
        test()
    elif len(args.params) == 4:
        input_protofile   = args.params[0]
        input_ptcmodel  = args.params[1]
        output_protofile = args.params[2]
        output_ptcmodel   = args.params[3]

        print('input_protofile = %s' % input_protofile)
        print('input_ptcmodel = %s' % input_ptcmodel)
        print('output_protofile = %s' % output_protofile)
        print('output_ptcmodel = %s' % output_ptcmodel)
        pytorch2ptcaffe(input_protofile, input_ptcmodel, output_protofile, output_ptcmodel)

if __name__ == '__main__':
    test()
