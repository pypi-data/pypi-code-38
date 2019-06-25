# --------------------------------------------------------
# ptcaffe
# Licensed under The MIT License [see LICENSE for details]
# Written by xiaohang
# --------------------------------------------------------

import time
import os
import importlib
import argparse
from collections import OrderedDict
from ptcaffe.tools.cmds import time_net, run_net, other_cmds
from ptcaffe.tools.demo import run_demo
from ptcaffe.utils.config import cfg
from ptcaffe.utils.logger import logger
from ptcaffe.utils.utils import python_version, register_plugin
import torch
import ptcaffe

def main():
    try:
        import ptcaffe_plugins
        print('ptcaffe %s python %s torch %s plugins %s' % (ptcaffe.__version__, python_version(), torch.__version__, ptcaffe_plugins.__version__))
    except:
        print('ptcaffe %s python %s torch %s plugins None' % (ptcaffe.__version__, python_version(), torch.__version__))
    import sys
    if len(sys.argv) > 1:
        if sys.argv[1] in ['get_model', 'export_qmodel', 'rename_model', 'quantize_weight']:
            return other_cmds(sys.argv)
        elif sys.argv[1] == 'demo':
            return run_demo()

    parser = argparse.ArgumentParser(description='A caffe-like deep learning framework on pytorch')
    parser.add_argument('cmd', choices=['train', 'test', 'server', 'time', 'run', 'macc'], help="ptcaffe commands: train, test, server, time, run, 'macc', get_model, rename_model, export_qmodel, quantize_weight, demo")
    parser.add_argument('--solver', help='The solver definition protocol buffer text file')
    parser.add_argument('--model', help='Optional; The model definition protocol buffer text file')
    parser.add_argument('--weights', help='Optional; the pretrained weights to initialize finetuning')
    parser.add_argument('--snapshot', help='Optional; the snapshot solver state to resume training')
    parser.add_argument('--iterations', type=int, help='Optional; The number of iterations to run during test')
    parser.add_argument('--phase', help='Optional; network phase (TRAIN or TEST). Used for time, run')
    parser.add_argument('--gpu', help='Optional; run in GPU mode on given device IDs separated by ","')
    parser.add_argument('--verbose', type=int, help='Optional; verbose level 0: standard info, 1: receptive field, 2: debug')
    parser.add_argument('--plugin', help='Optional; plugins to support more self defined layers; multiple plugins should be seperate by comma')
    parser.add_argument('--lr', help=argparse.SUPPRESS)
    parser.add_argument('--snapshot_prefix', help=argparse.SUPPRESS)
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

    if args.cmd == 'time':
        return time_net(args)
    elif args.cmd == 'run':
        return run_net(args)
    elif args.cmd == 'server':
        from ptcaffe.utils.prototxt import parse_prototxt
        from ptcaffe.servers import SERVER_DICT

        net_info = parse_prototxt(args.model)
        server_param = net_info.get('server', OrderedDict())
        server_type = server_param.get('type', 'basic')
        server_port = int(server_param.get('port', '8080'))
        server_host = server_param.get('host', '0.0.0.0')
        server_debug = (server_param.get('debug', 'false') == 'true')

        app = SERVER_DICT[server_type](args.model, args.weights, args.gpu)
        app.run(host=server_host, port=server_port, debug=server_debug)

    elif args.cmd in ['train', 'test']:
        #assert(args.solver is not None)
        from ..trainers.trainer import Trainer
        trainer = Trainer(args.solver, args.weights, args.gpu, args)
        if args.cmd == 'train':
            trainer.run()
        else:
            if trainer.test_selectors is None:
                trainer.net.set_selector("")
                trainer.run_eval()
            else:
                for idx, selector in enumerate(trainer.test_selectors):
                    trainer.net.set_selector(selector)
                    trainer.net.set_automatic_outputs()
                    trainer.test_iter = trainer.test_iters[idx]
                    trainer.run_eval()
    elif args.cmd == 'macc':
        from torchstat import stat
        from ptcaffe.caffenet import CaffeNet
        net = CaffeNet(args.model, phase='TEST')
        net.eval()
        if args.gpu:
            assert(args.gpu.find(',') == -1)
            print('set gpu device %s' % args.gpu)
            net.cuda(int(args.gpu))
        input_shapes = net.get_input_shapes(phase='TEST')
        if isinstance(input_shapes[0], int):
            input_shape = input_shapes[1:]
            stat(net, input_shape)
