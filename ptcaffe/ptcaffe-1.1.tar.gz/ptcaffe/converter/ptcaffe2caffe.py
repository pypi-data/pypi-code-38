# --------------------------------------------------------
# ptcaffe
# Licensed under The MIT License [see LICENSE for details]
# Written by xiaohang 2018.3
# --------------------------------------------------------

import os
import sys
import argparse
from collections import OrderedDict
from ptcaffe.utils.utils import make_list

import ptcaffe
from ptcaffe.utils.config import cfg
from ptcaffe.utils.utils import check_file_exists, register_plugin
from ptcaffe.utils.logger import logger
from ptcaffe.utils.prototxt import parse_prototxt

def verify_ptcaffe_caffe(ptcaffe_protofile, ptcaffe_weightfile, caffe_protofile, caffe_weightfile, phase, is_cuda=False, iterations=1):
    import os
    os.environ['GLOG_minloglevel'] = '2'
    import torch
    import torch.nn as nn
    from torch.nn.parameter import Parameter
    from ptcaffe.caffenet import CaffeNet
    from ptcaffe.layer_dict import Convolution, Deconvolution, BatchNorm, Scale, Normalize
    import numpy as np
    try:
        import caffe
    except ImportError:
        print("Unable to import caffe, verify failed")
        return

    def forward_deploy_ptcaffe(net, datas=None):
        if is_cuda:
            net.cuda()
        net.eval()
        net.VERIFY_DEBUG = True
        input_names = net.get_input_names(phase='TEST')
        if not isinstance(input_names, list): input_names = [input_names]

        if datas is None:
            blobs = net.forward()
        else:
            if is_cuda:
                input_datas = [torch.from_numpy(datas[name]).cuda() for name in input_names]
            else:
                input_datas = [torch.from_numpy(datas[name]) for name in input_names]
            blobs = net.forward(*input_datas)
        return blobs

    def forward_deploy_caffe(net, datas=None):
        if datas is None:
            output = net.forward()
        else:
            for name, data in datas.items():
                net.blobs[name].reshape(*data.shape)
                net.blobs[name].data[...] = data
            output = net.forward()
        return net.blobs

    def forward_train_caffe(protofile, weightfile):
        if is_cuda:
            caffe.set_device(0)
            caffe.set_mode_gpu()
        else:
            caffe.set_mode_cpu()
        net = caffe.Net(protofile, weightfile, caffe.TRAIN)
        output = net.forward()
        return net.blobs, net.params

    def forward_train_ptcaffe(protofile, weightfile, caffe_blobs):
        net = CaffeNet(protofile, phase='TRAIN')
        net.train()
        if is_cuda:
            net.cuda()
        net.load_model(weightfile)
        net.VERIFY_DEBUG = True
        input_names = net.get_input_names(phase='TRAIN')
        inputs = []
        for name in input_names:
            data = torch.from_numpy(caffe_blobs[name].data)
            if is_cuda:
                data = data.cuda()
            inputs.append(data)
        blobs = net(*inputs)
        return blobs, net.models

    def compare_weights_difference(pytorch_models, caffe_params):
        layer_names = pytorch_models.keys()
        print('------------ Parameter Difference ------------')
        for layer_name in layer_names:
            if type(pytorch_models[layer_name]) in [Convolution, Deconvolution, nn.Conv2d, nn.Linear, Scale, Normalize]:
                weight_diff = np.inf
                if hasattr(pytorch_models[layer_name], 'weight'):
                    pytorch_weight = pytorch_models[layer_name].weight.data
                    if is_cuda:
                        pytorch_weight = pytorch_weight.cpu().numpy()
                    else:
                        pytorch_weight = pytorch_weight.numpy()
                    caffe_weight = caffe_params[layer_name][0].data
                    weight_diff = abs(pytorch_weight - caffe_weight).sum()
                if hasattr(pytorch_models[layer_name], 'bias') and type(pytorch_models[layer_name].bias) == Parameter:
                    pytorch_bias = pytorch_models[layer_name].bias.data
                    if is_cuda:
                        pytorch_bias = pytorch_bias.cpu().numpy()
                    else:
                        pytorch_bias = pytorch_bias.numpy()
                    caffe_bias = caffe_params[layer_name][1].data
                    bias_diff = abs(pytorch_bias - caffe_bias).sum()
                    print('%-30s       weight_diff: %f        bias_diff: %f' % (layer_name, weight_diff, bias_diff))
                else:
                    print('%-30s       weight_diff: %f' % (layer_name, weight_diff))
            elif type(pytorch_models[layer_name]) in [nn.BatchNorm2d, BatchNorm]:
                if is_cuda:
                    pytorch_running_mean = pytorch_models[layer_name].running_mean.cpu().numpy()
                    pytorch_running_var = pytorch_models[layer_name].running_var.cpu().numpy()
                else:
                    pytorch_running_mean = pytorch_models[layer_name].running_mean.numpy()
                    pytorch_running_var = pytorch_models[layer_name].running_var.numpy()
                caffe_running_mean = caffe_params[layer_name][0].data/caffe_params[layer_name][2].data[0]
                caffe_running_var = caffe_params[layer_name][1].data/caffe_params[layer_name][2].data[0]
                running_mean_diff = abs(pytorch_running_mean - caffe_running_mean).sum()
                running_var_diff = abs(pytorch_running_var - caffe_running_var).sum()
                print('%-30s running_mean_diff: %f running_var_diff: %f' % (layer_name, running_mean_diff, running_var_diff))

    def compare_output_difference(pytorch_blobs, caffe_blobs):
        print('------------ Output Difference ------------')
        blob_names = pytorch_blobs.keys()
        for blob_name in blob_names:
            if is_cuda:
                pytorch_data = pytorch_blobs[blob_name].data.cpu().numpy()
            else:
                pytorch_data = pytorch_blobs[blob_name].data.numpy()
            caffe_data = caffe_blobs[blob_name].data
            try:
                diff = abs(pytorch_data - caffe_data).sum()
            except:
                diff = np.inf
            print('%-30s pytorch_shape: %-20s caffe_shape: %-20s output_diff: %f' % (blob_name, pytorch_data.shape, caffe_data.shape, diff/pytorch_data.size))

    def has_data_layer(protofile):
        net_info = parse_prototxt(protofile)
        if 'input' in net_info['props']:
            return False
        return True

    if phase == 'TRAIN':
        caffe_blobs, caffe_params = forward_train_caffe(caffe_protofile, caffe_weightfile)
        pytorch_blobs, pytorch_models = forward_train_ptcaffe(ptcaffe_protofile, ptcaffe_weightfile, caffe_blobs)
        compare_weights_difference(pytorch_models, caffe_params)
        compare_output_difference(pytorch_blobs, caffe_blobs)
    else:
        ptc_net = CaffeNet(ptcaffe_protofile, phase = 'TEST')
        ptc_net.load_model(ptcaffe_weightfile)
        pytorch_models = ptc_net.models
        input_names = ptc_net.get_input_names(phase='TEST')
        has_ptcaffe_data = ptc_net.has_data_layer(phase='TEST')

        if is_cuda:
            caffe.set_device(0)
            caffe.set_mode_gpu()
        else:
            caffe.set_mode_cpu()
        cf_net = caffe.Net(caffe_protofile, caffe_weightfile, caffe.TEST)
        caffe_params = cf_net.params
        has_caffe_data = has_data_layer(caffe_protofile)

        compare_weights_difference(pytorch_models, caffe_params)

        for i in range(iterations):
            datas = OrderedDict()
            print('===== iteration %d =====' % i)
            if has_ptcaffe_data:
                pytorch_blobs = forward_deploy_ptcaffe(ptc_net)
                for name in input_names:
                    datas[name] = pytorch_blobs[name].cpu().numpy()
                caffe_blobs = forward_deploy_caffe(cf_net, datas)
            elif has_caffe_data:
                caffe_blobs = forward_deploy_caffe(cf_net)
                for name in input_names:
                    datas[name] = caffe_blobs[name].data
                pytorch_blobs = forward_deploy_ptcaffe(ptc_net, datas)
            else:
                input_shapes = ptc_net.get_input_shapes(phase='TEST')
                if not isinstance(input_shapes[0], list): input_shapes = [input_shapes]
                if not isinstance(input_names, list): input_names = [input_names]
                for name, input_shape in zip(input_names, input_shapes):
                    datas[name] = torch.rand(input_shape).numpy()
                pytorch_blobs = forward_deploy_ptcaffe(ptc_net, datas)
                caffe_blobs   = forward_deploy_caffe(cf_net, datas)

            compare_output_difference(pytorch_blobs, caffe_blobs)
            del pytorch_blobs # could save memory
            del datas

def main():
#if __name__ == '__main__':
    print('ptcaffe %s' % ptcaffe.__version__)

    parser = argparse.ArgumentParser(description='convert caffe model to ptcaffe model', usage='ptcaffe2caffe input_prototxt input_ptcmodel output_prototxt output_caffemodel', epilog="welcome!")
    parser.add_argument('params', help="input_prototxt input_ptcmodel output_prototxt output_caffemodel", nargs=4)
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
    input_ptcmodel  = args.params[1]
    output_protofile = args.params[2]
    output_caffemodel   = args.params[3]
    print('input_protofile = %s' % input_protofile)
    print('input_ptcmodel = %s' % input_ptcmodel)
    print('output_protofile = %s' % output_protofile)
    print('output_caffemodel = %s' % output_caffemodel)

    assert(input_protofile.find('.prototxt') > 0)
    #assert(input_ptcmodel.find('.ptcmodel') > 0)
    assert(output_protofile.find('.prototxt') > 0)
    assert(output_caffemodel.find('.caffemodel') > 0)
    assert(check_file_exists(input_protofile))
    assert(check_file_exists(output_protofile))

    from ptcaffe.caffenet import CaffeNet
    args.phase = args.phase if args.phase is not None else 'TEST'
    input_net = CaffeNet(input_protofile, phase=args.phase)
    input_net.load_model(input_ptcmodel)
    print('save %s' % output_caffemodel)
    input_net.save_model(output_caffemodel, output_protofile)

    iterations = 1 if args.iterations is None else args.iterations
    verify_ptcaffe_caffe(input_protofile, input_ptcmodel, output_protofile, output_caffemodel, phase=args.phase, is_cuda=(args.gpu is not None), iterations=iterations)
