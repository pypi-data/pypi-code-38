# --------------------------------------------------------
# ptcaffe
# Licensed under The MIT License [see LICENSE for details]
# Written by xiaohang 2017.12.16
# --------------------------------------------------------

from __future__ import division, print_function

import os
import sys
import math
import time
import torch
import torch.nn as nn
import torch.optim as optim
from ..caffenet import CaffeNet
from ..utils.prototxt import parse_solver
from .data_parallel import ParallelCaffeNet
from .data_distributed import DistributedCaffeNet
from ..utils.utils import *
from ..utils.config import cfg, parse_cfg_params_from_solver
from ..utils.logger import logger
from collections import OrderedDict
import random
import numpy as np
from tqdm import tqdm
import ptcaffe

class Trainer(object):
    def __init__(self, solver_file, weight_file, gpus, opts = None):
        #assert(solver_file is not None)
        self.solver_file   = solver_file
        if self.solver_file is None:
            if opts is not None and opts.model is not None:
                from ptcaffe.utils.prototxt import parse_prototxt
                net_info = parse_prototxt(opts.model)
                self.solver = net_info['solver']
        else:
            self.solver        = parse_solver(solver_file)
        self.protofile     = opts.model if opts and opts.model else self.solver['net']
        self.test_iter     = opts.iterations if opts and hasattr(opts, 'iterations') else None
        self.snapshot_file = opts.snapshot if opts and hasattr(opts, 'snapshot') else None
        self.weight_file   = weight_file if weight_file is not None else self.solver.get('weights', None)
        self.gpus          = gpus
        self.start_batch   = 0
        self.opts = opts

        parse_cfg_params_from_solver(self.solver)
        register_plugin(self.solver.get('plugin', None))

        self.set_seed()
        self.init_distributed()
        self.create_network()
        self.parse_solver()
        self.create_optimizer()
        self.load_weights()
        self.print_info()

        # compute time
        self.train_time = OrderedDict()
        self.train_time['adjust_learning_rate'] = 0.0
        self.train_time['zero_grad'] = 0.0
        self.train_time['forward'] = 0.0
        self.train_time['backward'] = 0.0
        self.train_time['update'] = 0.0
        self.samples_per_second = None

    def set_seed(self):
        seed = int(self.solver['seed']) if 'seed' in self.solver else random.randint(1, 10000)
        cfg.SEED = seed
        logger.info('set seed %d' % seed)
        random.seed(seed)
        np.random.seed(seed)
        torch.backends.cudnn.deterministic = cfg.CUDNN_DETERMINISTIC
        torch.manual_seed(seed)
        #if self.gpus is not None or 'device_id' in self.solver:
        #    torch.cuda.manual_seed_all(seed)

    def print_info(self):
        if logger.getEffectiveLevel() >= logger.MORE_INFO:
            logger.print('----------------------------------')
            logger.print('train_batch_size : %d'    % self.train_batch_size)
            logger.print('train_batch_num  : %d'    % self.train_batch_num)
            if self.test_batch_size:
                logger.print('test_batch_size  : %d'    % self.test_batch_size)
            if self.test_batch_num:
                logger.print('test_batch_num   : %d'    % self.test_batch_num)
            logger.print('base_lr          : %f'    % self.base_lr)
            logger.print('test_iter        : %d'    % self.test_iter)
            logger.print('test_interval    : %d'    % self.test_interval)
            if self.stepvalue is not None:
                logger.print('stepvalues       : %s'    % self.stepvalues)
            if self.stepsize is not None:
                logger.print('stepsize         : %s'    % self.stepsize)
            logger.print('display          : %d'    % self.display)
            logger.print('max_iter         : %d'    % self.max_iter)
            logger.print('snapshot         : %d'    % self.snapshot)
            logger.print('world_size       : %d'    % self.distributed_worldsize)
            logger.print('----------------------------------')

    def save_state(self, batch, savename):
        try:
            import ptcaffe_plugins
            ptcaffe_plugins_version = ptcaffe_plugins.__version__
        except:
            ptcaffe_plugins_version = 'None'

        state = {'batch': batch,
                'ptcaffe_version': ptcaffe.__version__,
                'python_version': python_version(),
                'torch_version': torch.__version__,
                'plugin_version': ptcaffe_plugins_version,
                'seed_value': cfg.SEED,
                'state_dict': self.net.state_dict(),
                'optimizer': self.optimizer.state_dict()}
        torch.save(state, savename)

    def epoch2iters(self, iter_str, batch_num = None, world_size = None):
        batch_num = self.train_batch_num if batch_num is None else batch_num
        world_size = self.distributed_worldsize if world_size is None else world_size
        if iter_str[-2:] == 'EP':
            assert(batch_num is not None)
            return int(float(iter_str[:-2]) * batch_num / world_size)
        else:
            return int(iter_str)

    def iters2epoch(self, iters):
        batch_num = self.train_batch_num
        world_size = self.distributed_worldsize
        assert(batch_num is not None)
        assert(world_size is not None)
        epoch = iters * world_size // batch_num
        remain = iters - epoch * batch_num // world_size
        return epoch, remain

    def print_time(self, seen):

        logger.print('================================================================================================================')
        self.net.print_forward_time()
        logger.print('%30s' % '----')
        for key in self.train_time.keys():
            t = self.train_time[key]
            logger.print('%30s%20f%20f%20d' % (key, t, t/seen, seen))
        logger.print('================================================================================================================')

    def create_snapshot_folder(self, snapshot_prefix):
        folder = '/'.join(snapshot_prefix.split('/')[:-1])
        if not os.path.exists(folder):
            logger.print('create folder %s' % folder)
            os.makedirs(folder)

    def init_distributed(self):
        #----------------------------
        self.distributed_backend   = self.solver.get('distributed_backend', 'nccl')
        self.distributed_master    = self.solver.get('distributed_master', None)
        self.distributed_worldsize = int(self.solver.get('distributed_worldsize', 1))
        self.distributed_rank      = self.solver.get('distributed_rank', None)

        # distributed param
        if self.distributed_worldsize > 1:
            if sys.version_info.major == 3:
                import multiprocessing as mp
                mp.set_start_method('spawn', force=True)
            assert(self.distributed_rank is not None)
            import torch.distributed as dist
            self.distributed_rank = int(self.distributed_rank)
            dist.init_process_group(backend=self.distributed_backend, init_method=self.distributed_master,
                                    world_size=self.distributed_worldsize, rank=self.distributed_rank)

    def create_network(self):
        # solver_mode and device_id
        self.solver_mode  = self.solver.get('solver_mode', None)
        self.device_id    = self.solver.get('device_id', None)
        self.gpus         = self.device_id if self.gpus is None else self.gpus

        if self.gpus:
            device_ids = self.gpus.split(',')
            device_ids = [int(i) for i in device_ids]
            cfg.NUM_GPUS = len(device_ids)  # will be used in data layer to calc batch_size (ngpus * base_batch_size)

        phase = 'TRAIN'
        if self.opts is not None:
            phase = 'TRAIN' if self.opts.cmd == 'train' else 'TEST'
        self.net = CaffeNet(self.protofile, phase = phase)

        self.train_batch_size = self.net.get_batch_size('TRAIN')
        self.train_batch_num  = self.net.get_batch_num('TRAIN')
        self.test_batch_size  = self.net.get_batch_size('TEST')
        self.test_batch_num   = self.net.get_batch_num('TEST')
        self.net.broadcast_apply( "get_train_batch_size", self.train_batch_size  )
        self.net.broadcast_apply( "get_train_batch_num", self.train_batch_num  )
        self.net.broadcast_apply( "get_test_batch_size", self.test_batch_size  )
        self.net.broadcast_apply( "get_test_batch_num", self.test_batch_num  )

        self.net.set_automatic_outputs()
        logger.print(self.net, level=logger.MORE_INFO)

        if self.gpus:
            logger.print('device_ids %s', device_ids)
            if self.distributed_worldsize > 1:
                self.net = DistributedCaffeNet(self.net.cuda(device_ids[0]), device_ids=device_ids)
            else:
                if len(device_ids) > 1:
                    logger.print('---- Multi GPUs ----')
                    self.net = ParallelCaffeNet(self.net.cuda(device_ids[0]), device_ids=device_ids)
                else:
                    logger.print('---- Single GPU %d ----' % device_ids[0])
                    self.net.cuda(device_ids[0])
                    self.net.broadcast_device_ids(device_ids)

    def parse_solver(self):
        solver                 = self.solver
        logger.print('solver: %s' % solver)
        #----------------------------
        self.test_iter         = self.epoch2iters(solver.get('test_iter', '0'), self.test_batch_num, 1) if self.test_iter is None else self.test_iter
        self.test_interval     = self.epoch2iters(solver['test_interval']) if 'test_interval' in solver else 99999

        self.base_lr           = float(solver['base_lr'])
        self.max_lr            = float(solver['max_lr']) if 'max_lr' in solver else None
        self.lr_descent_ratio  = float(solver.get('lr_descent_ratio', 1))
        self.base_bs           = int(solver['base_bs']) if 'base_bs' in solver else None
        self.momentum          = float(solver.get('momentum', 0.9))
        self.weight_decay      = float(solver.get('weight_decay', 0.0005))

        self.lr_policy         = solver.get('lr_policy', None)
        self.gamma             = float(solver.get('gamma', 0.1))
        self.power             = float(solver.get('power', 0.75))
        self.stepvalue         = solver.get('stepvalue', None)
        self.stepsize          = solver.get('stepsize', None)

        self.adam_betas        = (float(solver.get('adam_beta1', 0.5)), float(solver.get('adam_beta2', 0.999)))

        self.rmsprop_alpha     = float(solver.get('rmsprop_alpha', 0.99))
        self.rmsprop_eps       = float(solver.get('rmsprop_eps', 1e-8))
        self.rmsprop_centered  = solver.get('rmsprop_centered', 'false') == 'true'

        self.warmup_lr         = float(solver.get('warmup_lr', 0.0))
        self.warmup_step       = self.epoch2iters(solver.get('warmup_step', '-1'))
        self.warmup_mode       = solver.get('warmup_mode', 'constant')

        self.display           = self.epoch2iters(solver.get('display', '20'))
        self.max_iter          = self.epoch2iters(solver['max_iter'])
        self.snapshot          = self.epoch2iters(solver['snapshot'])
        self.snapshot_prefix   = solver['snapshot_prefix']
        self.test_after_train  = (solver.get('test_after_train', 'false') == 'true')
        self.test_initialization = (solver.get('test_initialization', 'false') == 'true')
        self.snapshot_after_train = (solver.get('snapshot_after_train', 'true') == 'true')

        self.solver_type       = solver.get('type', 'SGD').upper()

        self.selectors         = solver.get('selectors', None)
        self.train_selectors   = solver['train_selectors'] if 'train_selectors' in solver else self.selectors
        self.test_selectors    = solver['test_selectors'] if 'test_selectors' in solver else self.selectors
        self.selector_policy   = solver.get('selector_policy', 'ORDERED') # RANDOM, WEIGHTED
        self.selector_step     = solver.get('selector_step', None)
        self.selector_step     = None if self.selector_step is None else list( map(int,  self.selector_step.strip().split(",") ) )
        self.selector_probs    = solver.get('selector_probs', None)
        self.selector_rates    = solver.get('selector_rates', None)
        self.test_iters        = solver.get('test_iters', None)

        self.timing_interval   = int(solver.get('timing_interval', 10000))
        self.subdivision       = int(solver.get('subdivision', 1))

        self.visdom_interval   = int(solver.get('visdom_interval', 10))
        self.visdom_scale      = float(solver.get('visdom_scale', 1.0))
        self.visdom_server     = solver.get('visdom_server', None)
        self.visdom_port       = int(solver.get('visdom_port', 8097))
        self.visdom_incoming   = (solver.get('visdom_incoming', 'false') == 'true')
        self.visdom_env        = solver.get('visdom_env', 'main')

        self.clamp_grad        = float(solver['clamp_grad']) if 'clamp_grad' in solver else None
        self.best_evaluators   = solver.get('best_evaluator', None) # ref,op,thresh,prefix
        #----------------------------
        # base_lr
        if self.base_bs is not None:
            self.base_lr = self.train_batch_size * self.distributed_worldsize / self.base_bs * self.base_lr

        # lr_policy
        if self.lr_policy is None:
            if 'stepvalue'  in solver: self.lr_policy = 'multistep'
            elif 'stepsize' in solver: self.lr_policy = 'step'
        assert(self.lr_policy in ['fixed', 'step', 'exp', 'inv', 'multistep',
            'poly', 'sigmoid', 'triangle', 'triangle2', 'trianglee', 'sgdr',
            "step_sgdr", 'multistep_sgdr'])
        if self.lr_policy == 'step'      : assert('stepsize'  in solver)
        if self.lr_policy == 'exp'       : assert('gamma'     in solver)
        if self.lr_policy == 'inv'       : assert('gamma'     in solver and 'power' in solver)
        if 'multistep' in self.lr_policy : assert('stepvalue' in solver)
        if self.lr_policy == 'poly'      : assert('power'     in solver and 'max_iter' in solver)
        if self.lr_policy == 'sigmoid'   : assert('gamma'     in solver and 'stepsize' in solver)
        if self.lr_policy == 'triangle'  : assert('max_lr'    in solver and 'stepsize' in solver)
        if self.lr_policy == 'triangle2' : assert('max_lr'    in solver and 'stepsize' in solver)
        if self.lr_policy == 'trianglee' : assert('max_lr'    in solver and 'stepsize' in solver and 'gamma' in solver)
        if self.lr_policy == 'sgdr'      : assert('max_lr'    in solver and 'stepsize' in solver)


        # stepvalue, stepsize
        if self.stepvalue is not None:
            self.stepvalues    = self.stepvalue
            self.stepvalues    = self.stepvalues if isinstance(self.stepvalues, list) else [self.stepvalues]
            self.stepvalues    = [self.epoch2iters(item) for item in self.stepvalues]

        if self.stepsize is not None:
            self.stepsize    = self.epoch2iters(self.stepsize)

        # snapshot_prefix
        if self.opts != None and hasattr(self.opts, 'snapshot_prefix') and self.opts.snapshot_prefix != None:
            self.snapshot_prefix = self.opts.snapshot_prefix
        self.create_snapshot_folder(self.snapshot_prefix)

        # solver_type
        assert(self.solver_type in ['SGD', 'ADADELTA', 'AdaGrad', 'ADAM', 'NESTEROV', 'RMSPROP'])
        # selectors and selector_policy
        if self.train_selectors is not None:
            self.train_selectors = self.train_selectors.split(',')
            self.selector_indent_train = str(-max([len(selector) for selector in self.train_selectors]))
            if self.selector_probs:
                self.selector_probs = list( map( float, self.selector_probs.strip().strip(' ').split(',') ) )
            if self.selector_rates:
                self.selector_rates = list( map( int, self.selector_rates.strip().strip(' ').split(',') ) )

        if self.test_selectors is not None:
            self.test_selectors = self.test_selectors.split(',')
            self.selector_indent_test = str(-max([len(selector) for selector in self.test_selectors]))

        # test_iters
        if self.test_selectors is not None:
            if self.test_iters is not None:
                self.test_iters    = solver['test_iters'].split(',')
                self.test_iters    = [int(i.strip()) for i in self.test_iters]
            else:
                assert('test_iter' in solver)
                self.test_iters    = [self.test_iter] * len(self.test_selectors)
            assert(len(self.test_iters) == len(self.test_selectors))

        # visdom param
        if self.visdom_server is not None:
            cfg.VISDOM_SERVER = self.visdom_server
            cfg.VISDOM_SERVER_PORT = self.visdom_port
            cfg.VISDOM_SERVER_USING_INCOMING_SOCKET = self.visdom_incoming
            cfg.VISDOM_ENV_NAME =  self.visdom_env
        else:
            self.visdom_viz = None

        if cfg.VISDOM_SERVER is not None:
            server = cfg.VISDOM_SERVER
            if server.find('http://') < 0:
                server = 'http://%s' % server
            port = cfg.VISDOM_SERVER_PORT
            incoming = cfg.VISDOM_SERVER_USING_INCOMING_SOCKET
            env_name = cfg.VISDOM_ENV_NAME if cfg.VISDOM_ENV_NAME is not None else "main"
            logger.print('solver visom server: %s:%d, incoming=%s, env_name=%s' % (server, port, incoming, env_name))
            try:
                import visdom
                self.visdom_viz = visdom.Visdom(server=server, port=port, use_incoming_socket=incoming, env=env_name)
            except ImportError:
                self.visdom_viz = None
            self.visdom_wins = dict()

        # best model
        if self.best_evaluators is not None:
            if not isinstance(self.best_evaluators, list):
                self.best_evaluators = [self.best_evaluators]
            self.best_ops = dict()
            self.best_threshes = dict()
            self.best_prefixes = dict()
            self.best_vals = OrderedDict()
            for evaluator in self.best_evaluators:
                ref,op,thresh,prefix = evaluator.split(',')
                assert(op in ['min', 'max'])
                thresh = float(thresh)
                self.best_ops[ref] = op
                self.best_threshes[ref] = thresh
                self.best_prefixes[ref] = prefix
                self.best_vals[ref] = sys.float_info.min if op == 'max' else sys.float_info.max

    def create_optimizer(self):
        if self.solver_type == 'SGD':
            self.optimizer = optim.SGD(self.net.get_parameters(self.base_lr, self.weight_decay), momentum=self.momentum)
        elif self.solver_type == 'NESTEROV':
            self.optimizer = optim.SGD(self.net.get_parameters(self.base_lr, self.weight_decay), momentum=self.momentum, nesterov=True)
        elif self.solver_type == 'ADAM':
            self.optimizer = optim.Adam(self.net.get_parameters(self.base_lr, self.weight_decay), betas=self.adam_betas)
        elif self.solver_type == 'ADADELTA':
            self.optimizer = optim.Adadelta(self.net.get_parameters(self.base_lr, self.weight_decay))
        elif self.solver_type == 'RMSPROP':
            self.optimizer = optim.RMSprop(self.net.get_parameters(self.base_lr, self.weight_decay), alpha=self.rmsprop_alpha, \
                                           eps=self.rmsprop_eps, momentum=self.momentum, centered=self.rmsprop_centered)
            #self.optimizer = optim.RMSprop(self.net.get_parameters(self.base_lr, self.weight_decay))

    def load_weights(self):
        if self.snapshot_file:
            state = torch.load(self.snapshot_file)
            self.start_batch = state['batch']
            self.net.load_state_dict(state['state_dict'])
            self.optimizer.load_state_dict(state['optimizer'])
            logger.info('loaded state %s' % (self.snapshot_file))
            self.net.broadcast_apply('set_start_batch', self.start_batch)
        elif self.weight_file:
            if self.weight_file.find('.caffemodel') >= 0:
                logger.info('load caffe model %s' % self.weight_file)
                self.net.load_caffemodel(self.weight_file)
            elif self.weight_file.find('.pth') >= 0 or self.weight_file.find('.ptcmodel') >= 0:
                logger.info('load weights %s' % self.weight_file)
                self.net.load_model(self.weight_file)
            else:
                logger.error('unknown weight file ==> exit')
                exit()

    def adjust_learning_rate(self, batch):
        # compute lr
        if self.lr_policy == 'fixed':
            lr = self.base_lr
        elif self.lr_policy == 'step':
            times = int(batch / self.stepsize)
            lr = self.base_lr * (self.gamma ** times)
        elif self.lr_policy == 'exp':
            lr = self.base_lr * (self.gamma ** batch)
        elif self.lr_policy == 'inv':
            lr = self.base_lr * ((1 + self.gamma * batch) ** (-self.power))
        elif self.lr_policy == 'poly':
            lr = self.base_lr * ((1 - batch/self.max_iter) ** self.power)
        elif self.lr_policy == 'sigmoid':
            lr = self.base_lr * (1/(1+math.exp(-self.gamma * (batch - self.stepsize))))
        elif self.lr_policy == 'multistep':
            lr = self.base_lr
            if batch < self.warmup_step:
                if self.warmup_mode == 'linear':
                    lr = self.warmup_lr + batch/float(self.warmup_step) * (self.base_lr - self.warmup_lr)
                elif self.warmup_mode == 'constant':
                    lr = self.warmup_lr
            else:
                for i in range(len(self.stepvalues)):
                    if batch >= self.stepvalues[i]:
                        lr = lr * self.gamma
                    else:
                        break
        elif self.lr_policy == 'triangle':
            cycle = np.floor(1 + batch/(2.0*self.stepsize))
            x = np.abs(float(batch)/self.stepsize - 2*cycle + 1)
            lr= self.base_lr + (self.max_lr - self.base_lr)*np.maximum(0, (1 - x))
        elif self.lr_policy == 'triangle2':
            cycle = np.floor(1 + batch/(2.0*self.stepsize))
            x = np.abs(float(batch)/self.stepsize - 2*cycle + 1)
            lr = self.base_lr + (self.max_lr - self.base_lr)*np.maximum(0, (1 - x))/float(2**(cycle - 1))
        elif self.lr_policy == 'trianglee':
            cycle = np.floor(1 + batch/(2.0*self.stepsize))
            x = np.abs(float(batch)/self.stepsize - 2*cycle + 1)
            lr= self.base_lr + (self.max_lr - self.base_lr)*np.maximum(0, (1 - x))*self.gamma**(batch)
        elif self.lr_policy == 'sgdr':
            ratio = self.lr_descent_ratio if self.lr_descent_ratio is not None else 1
            remainder = float(batch % self.stepsize)
            offset = (ratio-1) / (ratio+1) * self.stepsize
            if remainder <  self.stepsize / (ratio + 1):
                lr = self.base_lr + (self.max_lr - self.base_lr)*(1 + np.cos(remainder*(ratio + 1)/ 2 / self.stepsize * np.pi))*0.5
            else:
                lr = self.base_lr + (self.max_lr - self.base_lr)*(1 + np.cos((remainder + offset)*(ratio+1)/(ratio*2) / self.stepsize * np.pi))*0.5
        elif self.lr_policy == 'step_sgdr':
            ratio = self.lr_descent_ratio if self.lr_descent_ratio is not None else 1
            remainder = float(batch % self.stepsize)
            offset = (ratio-1) / (ratio+1) * self.stepsize
            if remainder <  self.stepsize / (ratio + 1):
                lr = self.base_lr + (self.max_lr - self.base_lr)*(1 + np.cos(remainder*(ratio + 1)/ 2 / self.stepsize * np.pi))*0.5
            else:
                lr = self.base_lr + (self.max_lr - self.base_lr)*(1 + np.cos((remainder + offset)*(ratio+1)/(ratio*2) / self.stepsize * np.pi))*0.5
            if batch < self.warmup_step:
                lr = lr
            else:
                stepsize = self.stepsize
                lr = lr * 10**( -1.0*math.floor( ( batch-self.warmup_step )/stepsize ) )
        elif self.lr_policy == 'multistep_sgdr':
            ratio = self.lr_descent_ratio if self.lr_descent_ratio is not None else 1
            remainder = float(batch % self.stepsize)
            offset = (ratio-1) / (ratio+1) * self.stepsize
            if remainder <  self.stepsize / (ratio + 1):
                lr = self.base_lr + (self.max_lr - self.base_lr)*(1 + np.cos(remainder*(ratio + 1)/ 2 / self.stepsize * np.pi))*0.5
            else:
                lr = self.base_lr + (self.max_lr - self.base_lr)*(1 + np.cos((remainder + offset)*(ratio+1)/(ratio*2) / self.stepsize * np.pi))*0.5
            if batch < self.warmup_step:
                lr = lr
            else:
                for i in range(len(self.stepvalues)):
                    if batch >= self.stepvalues[i]:
                        lr = lr * self.gamma
                    else:
                        break


        # adjust lr
        for param_group in self.optimizer.param_groups:
            param_group['lr'] = lr * param_group['lr_mult']
        return lr

    def get_best_vals(self):
        if self.best_evaluators is not None:
            return self.best_vals
        else:
            return None

    # mode: 'train' or 'test'
    def run_eval(self, cur_batch=None):
         mode = self.opts.cmd
         self.net.broadcast_apply("set_logger", logger)
         self.net.eval()
         sum_outputs = []
         if cfg.VERBOSE_LEVEL >= 1:
             idx_iter = tqdm(range(self.test_iter))
         else:
             idx_iter = range(self.test_iter)

         for i in idx_iter:
             with torch.no_grad():
                 outputs = self.net()
             if outputs is not None:
                 if i == 0:
                     sum_outputs = [output.data.cpu() for output in outputs]
                 else:
                     for idx, output in enumerate(outputs):
                         sum_outputs[idx] += output.data.cpu()
         metric_dict = self.net.get_metrics()
         self.net.reset_metrics()

         if len(self.net.eval_outputs) > 0:
             for key, value in zip(self.net.eval_outputs, sum_outputs):
                 if key in metric_dict.keys():
                     value = metric_dict[key]
                 else:
                     value /= self.test_iter

                 if value.numel() == 1:
                     if cur_batch != None:
                         epoch, rest_batch = self.iters2epoch(cur_batch)
                         if self.net.selector == '':
                             logger.info('[%dEP%d]  test %s: %f' % (epoch, rest_batch, key, float(value)))
                         else:
                             fmt_str = '[%dEP%d][%'+self.selector_indent_test+'s]  test %s: %f'
                             logger.info(fmt_str % (epoch, rest_batch, self.net.selector, key, float(value)))
                     else:
                         logger.info('test %s: %f' % (key, float(value)))
                 else:
                     if cur_batch != None:
                         epoch, rest_batch = self.iters2epoch(cur_batch)
                         if self.net.selector == '':
                             logger.info('[%dEP%d]  test %s: %s %f' % (epoch, rest_batch, key, list(value.numpy()), float(value.mean())))
                         else:
                             fmt_str = '[%dEP%d][%'+self.selector_indent_test+'s]  test %s: %s %f'
                             logger.info(fmt_str % (epoch, rest_batch, self.net.selector, key, list(value.numpy()), float(value.mean())))
                     else:
                         logger.info('test %s: %s %f' % (key, list(value.numpy()), float(value.mean())))

                 if self.best_evaluators is not None and mode == 'train':
                     if key in self.best_vals:
                         op = self.best_ops[key]
                         thresh = self.best_threshes[key]
                         prefix = self.best_prefixes[key]
                         savename = '%s_%s.ptcmodel' % (self.snapshot_prefix, prefix)
                         cur_val = float(value.mean())
                         if op == 'max' and cur_val > self.best_vals[key]:
                             self.best_vals[key] = cur_val
                             if cur_val > thresh:
                                 logger.info('save best model %s' % (savename))
                                 self.net.save_model(savename)

                                 savename = '%s_%s.ptcstate' % (self.snapshot_prefix, prefix)
                                 logger.info('save best state %s' % (savename))
                                 self.save_state(cur_batch, savename)
                         elif op == 'min' and cur_val < self.best_vals[key]:
                             self.best_vals[key] = cur_val
                             if cur_val < thresh:
                                 logger.info('save best model %s' % (savename))
                                 self.net.save_model(savename)
                                 savename = '%s_%s.ptcstate' % (self.snapshot_prefix, prefix)
                                 logger.info('save best state %s' % (savename))
                                 self.save_state(cur_batch, savename)

                         logger.info('best %s value = %f' % (key, self.best_vals[key]))
                         if cur_batch is not None and self.visdom_viz is not None:
                             X = np.array([cur_batch+1])
                             Y = np.array([cur_val])
                             if key not in self.visdom_wins:
                                 self.visdom_wins[key] = self.visdom_viz.line(X=X, Y=Y, opts={'title': key})
                             else:
                                 self.visdom_viz.line(X=X, Y=Y, win = self.visdom_wins[key], opts = {'title': key}, update='append')



    def run(self):
        if cfg.FORCE_VISDOM and cfg.VISDOM_SERVER is None:
            logger.info('FORCE_VISDOM is True')
            logger.warning('Please set visdom_server in solver.prototxt!!!')
            logger.info('exit ptcaffe')
            exit()

        # test init weights
        if self.weight_file and self.test_initialization:
            logger.print('-------------------', level=logger.INFO)
            if self.test_selectors is None:
                self.net.set_selector('')
                self.run_eval(self.start_batch)
            else:
                for idx, selector in enumerate(self.test_selectors):
                    self.net.set_selector(selector)
                    self.net.set_automatic_outputs()
                    #print('set test selector %s' % selector)
                    self.test_iter = self.test_iters[idx]
                    self.run_eval(self.start_batch)
            logger.print('-------------------', level=logger.INFO)
        self.net.train()
        logger.info('base_lr = %f' % self.base_lr)

        self.lr = self.adjust_learning_rate(self.start_batch)
        display_start_time = time.time()
        display_omit_time = 0
        display_last_batch = self.start_batch-1
        self.visdom_loss = 0.0
        for batch in range(self.start_batch, self.max_iter):
            epoch, rest_batch = self.iters2epoch(batch)

            selector = None
            if self.train_selectors is not None:
                # switch task if multi-tasks
                if self.selector_policy == 'ORDERED':
                    if self.selector_rates:
                        try:
                            from functools import reduce
                        except: pass
                        assert(len(self.train_selectors) == len(self.selector_rates))
                        sel_idxs = list( range( len(self.train_selectors) ) )
                        fre_list = [ [ sel_idxs[i] ]* self.selector_rates[i] for i in range(len(self.selector_rates)) ]
                        fre_list = reduce(lambda x,y:x+y, fre_list)
                        sel_idx = fre_list[ batch % len(fre_list) ]
                    else:
                        sel_idx = batch % len(self.train_selectors)
                elif self.selector_policy == 'RANDOM':
                    if self.selector_probs:
                        sel_idx = np.random.choice( np.arange( len(self.train_selectors) ), p=self.selector_probs )
                    elif self.selector_rates:
                        try:
                            from functools import reduce
                        except: pass
                        assert(len(self.train_selectors) == len(self.selector_rates))
                        sel_idxs = list( range( len(self.train_selectors) ) )
                        fre_list = [ [ sel_idxs[i] ]* self.selector_rates[i] for i in range(len(self.selector_rates)) ]
                        fre_list = reduce(lambda x,y:x+y, fre_list)
                        sel_idx = random.choice(fre_list)
                    else:
                        sel_idx = random.randint(0, len(self.train_selectors)-1)
                elif self.selector_policy == "MULTISTEP":
                    assert (len(self.selector_step)==len(self.train_selectors)-1)
                    sel_idx = 0
                    for i in range(len(self.selector_step)):
                        if batch >= self.selector_step[i]:
                            sel_idx = i+1
                selector = self.train_selectors[sel_idx]
                self.net.set_selector(selector)
                self.net.set_automatic_outputs()
                #print('set train selector %s' % selector)
            t0 = time.time()
            self.lr = self.adjust_learning_rate(batch)
            t1 = time.time()
            self.optimizer.zero_grad()
            t2 = time.time()

            assert(self.subdivision == 1)
            if self.subdivision == 1:
                outputs = self.net()
                outputs = outputs if isinstance(outputs, tuple) else [outputs]
                outputs = [output.mean() for output in outputs]
                loss = outputs[0]
                outputs = outputs[1:]

                t3 = time.time()
                loss.backward()
                t4 = time.time()
                if self.clamp_grad is not None:
                    for name, param in self.net.named_parameters():
                        if param.grad is not None:
                            # this is used for mutli-task training, in which the clamp_ function of
                            # untrained branch's param will be called
                            param.grad.clamp_(-self.clamp_grad, self.clamp_grad)
                self.optimizer.step()
                t5 = time.time()

                self.train_time['adjust_learning_rate'] += t1 - t0
                self.train_time['zero_grad'] += t2 - t1
                self.train_time['forward'] += t3 - t2
                self.train_time['backward'] += t4 - t3
                self.train_time['update'] += t5 - t4

            # check loss nan
            if np.isnan(float(loss)):
                raise ValueError('loss is nan while training')

            # update visdom loss
            if np.isinf(float(loss)):
                self.visdom_loss += 0.0
            else:
                self.visdom_loss += float(loss) * self.visdom_scale

            if (batch+1) % self.visdom_interval == 0:
                visdom_start_time = time.time()
                if self.visdom_viz:
                    meanval = self.visdom_loss / self.visdom_interval
                    X = np.array([batch+1])
                    Y = np.array([meanval])
                    #if (batch+1) == self.visdom_interval:
                    if 'total_loss' not in self.visdom_wins:
                        self.visdom_wins['total_loss'] = self.visdom_viz.line(X=X, Y=Y, opts={'title': 'total loss'})
                    else:
                        self.visdom_viz.line(X=X, Y=Y, win =self.visdom_wins['total_loss'], opts={'title': 'total loss'}, update='append')
                self.visdom_loss = 0.0
                visdom_end_time = time.time()
                display_omit_time += visdom_end_time - visdom_start_time

            if (rest_batch+1) % self.display == 0:
                display_interval = batch - display_last_batch
                display_last_batch = batch

                display_end_time = time.time()
                samples_per_second = float(self.train_batch_size * self.subdivision * display_interval) / (display_end_time - display_start_time - display_omit_time)
                if self.samples_per_second is None:
                    self.samples_per_second = 0
                elif self.samples_per_second == 0:
                    self.samples_per_second = samples_per_second
                else:
                    self.samples_per_second = 0.9 * self.samples_per_second + 0.1 * samples_per_second
                    samples_per_second = self.samples_per_second

                samples_per_second = round(samples_per_second * 10)/10.0
                #days_eta = (self.max_iter-batch-1) / float(self.display) * (display_end_time - display_start_time - display_omit_time) / 86400.0
                days_eta = (self.max_iter-batch-1) * float(self.train_batch_size * self.subdivision) / samples_per_second / 86400.0
                if selector is None:
                    logger.info('[%dEP%d] Total loss = %f, lr = %f, %.1f samples/sec, eta %.1f days' % (epoch, rest_batch+1, float(loss), self.lr, samples_per_second, days_eta))
                else:
                    fmt_str = '[%dEP%d][%'+self.selector_indent_train+'s] Total loss = %f, lr = %f, %.1f samples/sec, eta %.1f days'
                    logger.info(fmt_str % (epoch, rest_batch+1, selector, float(loss), self.lr, samples_per_second, days_eta))

                loss_weights = self.net.get_loss_weights()
                idx = 0
                for name, value in zip(self.net.train_outputs, outputs):
                    if name in loss_weights:
                        if selector is None:
                            logger.info('[%dEP%d]     Train net output #%d: %s = %f (* %f = %f loss)' % (epoch, rest_batch+1, idx, name, float(value), loss_weights[name], float(value) * loss_weights[name]))
                        else:
                            fmt_str = '[%dEP%d][%'+self.selector_indent_train+'s]     Train net output #%d: %s = %f (* %f = %f loss)'
                            logger.info(fmt_str % (epoch, rest_batch+1, selector, idx, name, float(value), loss_weights[name], float(value) * loss_weights[name]))
                    else:
                        if selector is None:
                            logger.info('[%dEP%d]     Train net output #%d: %s = %f' % (epoch, rest_batch+1, idx, name, float(value)))
                        else:
                            fmt_str = '[%dEP%d][%'+self.selector_indent_train+'s]     Train net output #%d: %s = %f'
                            logger.info(fmt_str % (epoch, rest_batch+1, selector, idx, name, float(value)))
                    idx += 1
                display_start_time = time.time()
                display_omit_time = 0

            if (batch+1) % self.snapshot == 0: # or (self.snapshot_after_train and (batch+1) == self.max_iter):
                snapshot_start_time = time.time()
                epoch, rest_batch = self.iters2epoch(batch+1)
                if True:
                    if rest_batch == 0:
                        savename = '%s_epoch%04d.ptcstate' % (self.snapshot_prefix, epoch)
                    else:
                        savename = '%s_epoch%04d_%04d.ptcstate' % (self.snapshot_prefix, epoch, rest_batch)
                    logger.info('save state %s' % (savename))
                    self.save_state(batch+1, savename)
                if True:
                    if rest_batch == 0:
                        savename = '%s_epoch%04d.ptcmodel' % (self.snapshot_prefix, epoch)
                    else:
                        savename = '%s_epoch%04d_%04d.ptcmodel' % (self.snapshot_prefix, epoch, rest_batch)
                    logger.info('save weights %s' % (savename))
                    self.net.save_model(savename)
                snapshot_end_time = time.time()
                display_omit_time += snapshot_end_time - snapshot_start_time

            if (batch+1) == self.timing_interval:
                self.print_time(batch+1)

            if (batch+1) % self.test_interval == 0 or (self.test_after_train and (batch+1) == self.max_iter):
                test_start_time = time.time()
                logger.print('-------------------', level=logger.INFO)
                if self.test_selectors is None:
                    self.net.set_selector('')
                    self.run_eval(batch+1)
                else:
                    for idx, selector in enumerate(self.test_selectors):
                        self.net.set_selector(selector)
                        self.net.set_automatic_outputs()
                        #print('set test selector %s' % selector)
                        self.test_iter = self.test_iters[idx]
                        self.run_eval(batch+1)
                logger.print('-------------------', level=logger.INFO)
                self.net.train()
                test_end_time = time.time()
                display_omit_time += test_end_time - test_start_time

        # train finished
        if self.snapshot_after_train:
            if True:
                savename = '%s_final.ptcstate' % self.snapshot_prefix
                logger.info('save state %s' % (savename))
                self.save_state(batch+1, savename)
            if True:
                savename = '%s_final.ptcmodel' % self.snapshot_prefix
                logger.info('save weights %s' % (savename))
                self.net.save_model(savename)
