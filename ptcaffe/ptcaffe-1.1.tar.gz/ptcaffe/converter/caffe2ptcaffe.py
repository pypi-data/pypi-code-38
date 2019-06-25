# --------------------------------------------------------
# ptcaffe
# Licensed under The MIT License [see LICENSE for details]
# Written by xiaohang 2018.3
# --------------------------------------------------------

import os
import sys
import argparse
from collections import OrderedDict

import ptcaffe
from ptcaffe.utils.config import cfg
from ptcaffe.utils.utils import check_file_exists, register_plugin
from ptcaffe.utils.logger import logger

def main():
#if __name__ == '__main__':
    print('ptcaffe %s' % ptcaffe.__version__)

    parser = argparse.ArgumentParser(description='convert caffe model to ptcaffe model', usage='caffe2ptcaffe input_prototxt input_caffemodel output_prototxt output_ptcmodel', epilog="welcome!")
    parser.add_argument('params', help="input_prototxt input_caffemodel output_prototxt output_ptcmodel", nargs=4)
    parser.add_argument('--phase', help='Optional; network phase (TRAIN or TEST)')
    parser.add_argument('--gpu', help='Optional; run in GPU mode on given device IDs separated by ","')
    parser.add_argument('--iterations', type=int, help='Optional; The number of iterations to run during test')
    parser.add_argument('--verbose', type=int, help='Optional; verbose level 0: no info, 1: receptive field, 2: debug')
    parser.add_argument('--plugin', help='Optional; enable plugin')
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


    input_protofile   = args.params[0]
    input_caffemodel  = args.params[1]
    output_protofile = args.params[2]
    output_ptcmodel   = args.params[3]
    print('input_protofile = %s' % input_protofile)
    print('input_caffemodel = %s' % input_caffemodel)
    print('output_protofile = %s' % output_protofile)
    print('output_ptcmodel = %s' % output_ptcmodel)

    assert(input_protofile.find('.prototxt') > 0)
    assert(input_caffemodel.find('.caffemodel') > 0)
    assert(output_protofile.find('.prototxt') > 0)
    assert(output_ptcmodel.find('.ptcmodel') > 0)
    assert(check_file_exists(input_protofile))
    assert(check_file_exists(output_protofile))
    #assert(input_protofile == output_protofile)

    from ptcaffe.caffenet import CaffeNet
    args.phase = args.phase if args.phase is not None else 'TEST'
    input_net = CaffeNet(input_protofile, phase=args.phase)
    input_net.load_model(input_caffemodel)
    print('save %s' % output_ptcmodel)
    input_net.save_model(output_ptcmodel)

    from .ptcaffe2caffe import verify_ptcaffe_caffe
    iterations = 1 if args.iterations is None else args.iterations
    for _ in range(iterations):
        verify_ptcaffe_caffe(output_protofile, output_ptcmodel, input_protofile, input_caffemodel, phase=args.phase, is_cuda=(args.gpu is not None))
