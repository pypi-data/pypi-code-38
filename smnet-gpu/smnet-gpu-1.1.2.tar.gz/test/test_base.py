# --------------------------------------------------------
# SMNet test
# Licensed under The MIT License [see LICENSE for details]
# Copyright 2019 smarsu. All Rights Reserved.
# --------------------------------------------------------

import os
import time
import numpy as np
import tensorflow as tf


def self_max_abs_error(a, b, thrs=0.1):
    """TODO(smarsu): a & b = 0"""
    a = np.array(a)
    b = np.array(b)
    smae = np.max(np.abs(a - b) / np.minimum(np.abs(a), np.abs(b)))
    if smae > thrs:
        raise ValueError('Too large error in func self_max_abs_error: {}, '
                         'the threshold is {}'.format(smae, thrs))
    return smae


class TestBase(object):
    def __init__(self, op_name, base_func, smnet_func, inputs_func, lr=1, epoch=200, border=0.01):
        """
        Args:
            base_func: Basic function implemented by tenflow to get base 
                result.
            smnet_func: The func implemented by smnet op.
            inputs_func: Randomly generate input datas by params.
        """
        self._op_name = op_name
        self._base_func = base_func
        self._smnet_func = smnet_func
        self._inputs_func = inputs_func
        self._lr = lr
        self._epoch = epoch
        self._border = border

        self._test_time = 0
        self._base_device = 'gpu'
        self._smnet_device = 'gpu'

    
    def test_case(self, **params):
        self._test_time += 1
        
        self._set_params(**params)
        if 'base_device' in params:
            self._set_base_device(params['base_device'])
        if 'smnet_device' in params:
            self._set_smnet_device(params['smnet_device'])

        gt_fst_res, gt_end_res, gt_tfst, gt_topt = self._run_base_func()
        sm_fst_res, sm_end_res, sm_tfst, sm_topt = self._run_smnet_func()

        self._show(gt_fst_res, gt_end_res, gt_tfst, gt_topt, 
                   sm_fst_res, sm_end_res, sm_tfst, sm_topt)

    
    def _set_params(self, **params):
        self._params = params
        self._args = self._inputs_func(**params, border=self._border)


    def _set_base_device(self, device):
        self._base_device = device

    
    def _set_smnet_device(self, device):
        self._smnet_device = device

    
    def _run_base_func(self):
        device = '0' if self._base_device == 'gpu' else ''
        os.environ['CUDA_VISIBLE_DEVICES'] = device
        tf.reset_default_graph()

        y = self._base_func(*self._args)

        opt = tf.train.GradientDescentOptimizer(self._lr).minimize(y)
        
        config = tf.ConfigProto() 
        config.gpu_options.allow_growth = True 
        with tf.Session(config=config) as sess:
            sess.run(tf.global_variables_initializer())

            fst_res = sess.run(y)

            for _ in range(self._epoch // 2):
                sess.run(opt)

            t1 = time.time()
            for _ in range(self._epoch // 2):
                sess.run(opt)
            t2 = time.time()
            end_res = sess.run(y)
            t3 = time.time()
        
        return fst_res, end_res, t3 - t2, (t2 - t1) / (self._epoch // 2)

    
    def _run_smnet_func(self):
        device = '0' if self._smnet_device == 'gpu' else ''
        os.environ['CUDA_VISIBLE_DEVICES'] = device
        import smnet as sm
        sm.reset_default_graph()
        
        y = self._smnet_func(*self._args, sm)

        sess = sm.Session()
        fst_res = sess.forward([y])[0]

        for _ in range(self._epoch // 2):
            sess.forward([])
            sess.optimize([y], lr=self._lr)

        t1 = time.time()
        for _ in range(self._epoch // 2):
            sess.forward([])
            sess.optimize([y], lr=self._lr)
        t2 = time.time()
        end_res = sess.forward([y])[0]
        t3 = time.time()

        return fst_res, end_res, t3 - t2, (t2 - t1) / (self._epoch // 2)


    def _show(self, gt_fst_res, gt_end_res, gt_tfst, gt_topt, 
              sm_fst_res, sm_end_res, sm_tfst, sm_topt):
        print("-------- {} test{} --------".format(self._op_name, self._test_time))
        for k, v in self._params.items():
            print('    {}: {}'.format(k, v))
        print()
        print('tf forward time: {} ms'.format(gt_tfst))
        print('sm forward time: {} ms'.format(sm_tfst))
        print()
        print('tf optimize time: {} ms'.format(gt_topt))
        print('sm optimize time: {} ms'.format(sm_topt))
        print()
        print('smae before opt: {}'.format(self_max_abs_error(gt_fst_res, sm_fst_res)))
        print('smae after opt: {}'.format(self_max_abs_error(gt_end_res, sm_end_res)))
        print("-------- {} test{} End --------\n".format(self._op_name, self._test_time))
