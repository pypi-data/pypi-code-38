from __future__ import division, print_function

import argparse
from ptcaffe.utils.utils import register_plugin
from ptcaffe.utils.config import cfg
from ptcaffe.utils.logger import logger
from ptcaffe.deploynet import DeployNet

def run_demo():
    parser = argparse.ArgumentParser(description='A caffe-like deep learning framework on pytorch')
    parser.add_argument('cmd', choices=['train', 'test', 'server', 'time', 'run', 'macc', 'demo'], help="ptcaffe commands: train, test, server, time, run, 'macc', get_model, rename_model, export_qmodel, quantize_weight, demo")
    parser.add_argument('--model', help='Optional; The model definition protocol buffer text file')
    parser.add_argument('--weights', help='Optional; the pretrained weights to initialize finetuning')
    parser.add_argument('--gpu', help='Optional; run in GPU mode on given device IDs separated by ","')
    parser.add_argument('--verbose', type=int, help='Optional; verbose level 0: standard info, 1: receptive field, 2: debug')
    parser.add_argument('--plugin', help='Optional; plugins to support more self defined layers; multiple plugins should be seperate by comma')
    parser.add_argument('--input', help="set input")
    parser.add_argument('--output', help="set output")
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

    net = DeployNet(args.model, args.weights, args.gpu)

    inputs = get_inputs(args.input)
    outputs = get_outputs(args.output, inputs)

    for infile, outfile in zip(inputs, outputs):
        net(infile, outfile)

def get_inputs(input):
    return [input]

def get_outputs(output, inputs):
    return [output]

def save_image(image, savename):
    if isinstance(image, np.array):
        cv2.imwrite(savename, image)
        print('save cv2 image %s' % savename)
    else:
        image.save(savename)
        print('save pil image %s' % savename)
