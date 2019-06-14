"""
    Optimizer
"""
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

from enum import Enum

import tensorflow as tf
import numpy as np


class Optimizers(Enum):
    Adam = 'adam'
    AdaGrad = 'adagrad'
    Momentum = 'momentum'
    SGD = 'sgd'

    @classmethod
    def get(cls, name):
        if name == cls.Adam.value:
            return tf.train.AdamOptimizer
        elif name == cls.AdaGrad.value:
            return tf.train.AdagradOptimizer
        elif name == cls.Momentum.value:
            return tf.train.MomentumOptimizer
        elif name == cls.SGD.value:
            return tf.train.GradientDescentOptimizer
        else:
            raise ValueError()


# TODO: Universal optimizer
class Optimizer:
    def __init__(self, learning_rate: float, var_scope: str, optimizer=Optimizers.Adam, optimizer_params=None,
                 decay_policy='none',
                 decay_params=None, summary_gradients=False, clip_gradient=0., warm_up=None):
        if decay_policy == 'none':
            self._learning_rate = learning_rate
        elif decay_policy == 'dying':
            self._learning_rate = self.dying_decay(learning_rate, **decay_params)
        elif decay_policy == 'step':
            self._learning_rate = self.step_decay(learning_rate, **decay_params)
        elif decay_policy == 'lambda':
            self._learning_rate = self.lambda_decay(learning_rate, **decay_params)
        else:
            raise ValueError('`decay_policy` should be `none`, `dying` or `step`.')

        if warm_up is not None:
            global_step = tf.train.get_or_create_global_step()
            self._learning_rate = warm_up(self._learning_rate, global_step)

        tf.summary.scalar(var_scope, self._learning_rate, family='Learning_Rates')

        optimizer_fn = Optimizers.get(optimizer.value) if not callable(optimizer) else optimizer

        self.optimizer = optimizer_fn(learning_rate=learning_rate, **(optimizer_params or {}))
        self.var_scope = var_scope

        self._summary_gradients = summary_gradients
        self._clip_gradient = clip_gradient

        self._var_list = None

    @property
    def summary_gradients(self):
        return self._summary_gradients

    @property
    def var_list(self):
        if self._var_list is None:
            self._var_list = tf.trainable_variables('.*' + self.var_scope)

            tf.logging.info('Trainable variables in {}:'.format(self.var_scope))
            for var in self._var_list:
                tf.logging.info(var)

        return self._var_list

    def train_op(self, loss, global_step=None, colocate_gradients_with_ops=True):
        grads = self.compute_grad(loss, colocate_gradients_with_ops=colocate_gradients_with_ops)
        return self.apply_gradients(grads, global_step=global_step)

    def compute_grad(self, loss, colocate_gradients_with_ops=True):
        """
        Computes gradients of trainable variables with regard to a loss given.

        :param tf.Tensor loss: A `tf.Tensor` of a loss.
        :return: A list of tuples containing gradients and corresponding variables.
        :rtype: list
        """
        return self.optimizer.compute_gradients(loss, var_list=self.var_list,
                                                colocate_gradients_with_ops=colocate_gradients_with_ops)

    def apply_gradients(self, grads_and_vars, global_step=None):
        if self.summary_gradients:
            tf.contrib.training.add_gradients_summaries(grads_and_vars)

        if self._clip_gradient > 0.:
            g_step = tf.train.get_or_create_global_step() if global_step is None else global_step

            grads = [tf.reduce_any(tf.greater(tf.abs(grad), self._clip_gradient)) for grad, var in grads_and_vars]
            skip = tf.logical_and(tf.reduce_any(tf.convert_to_tensor(grads)), tf.greater(g_step, 10000))

            grads_and_vars = [(tf.cond(skip, true_fn=lambda: tf.zeros_like(grad), false_fn=lambda: grad), var)
                              for grad, var in grads_and_vars]

        return self.optimizer.apply_gradients(grads_and_vars, global_step=global_step)

    def minimize(self, loss, global_step=None, colocate_gradients_with_ops=True):
        grads = self.compute_grad(loss, colocate_gradients_with_ops=colocate_gradients_with_ops)
        return self.apply_gradients(grads, global_step=global_step)

    def apply_tower_gradients(self, tower_grads, global_step=None):
        """
        Returns average gradients.

        :param list tower_grads: A list of tuples containing gradients and corresponding variables.
        :return: Applying gradients operation
        :rtype: tf.Operation
        """
        avg_grad = self._average_gradients(tower_grads)
        if self._clip_gradient > 0.:
            grads = [tf.reduce_any(tf.greater(tf.abs(grad), self._clip_gradient)) for grad, var in avg_grad]
            skip = tf.reduce_any(tf.convert_to_tensor(grads))

            avg_grad = [(tf.cond(skip, true_fn=lambda: tf.zeros_like(grad), false_fn=lambda: grad), var)
                        for grad, var in avg_grad]

        apply_grad_op = self.apply_gradients(avg_grad, global_step=global_step)
        return apply_grad_op

    @staticmethod
    def _average_gradients(tower_grads):
        if len(tower_grads) == 1:
            return tower_grads[0]

        def filter_no_gradients(grad_and_vars):
            return not any(map(lambda gv: gv[0] is None, grad_and_vars))

        def reduce_gradients(grad_and_vars):
            # Note that each grad_and_vars looks like the following:
            #   ((grad0_gpu0, var0_gpu0), ... , (grad0_gpuN, var0_gpuN))
            grads = list(map(lambda gv: gv[0], grad_and_vars))

            # Get average gradients
            grads = tf.stack(grads)
            grad = tf.reduce_mean(grads, axis=0)

            # Get chief variable
            var = grad_and_vars[0][1]
            return grad, var

        return list(map(reduce_gradients, filter(filter_no_gradients, zip(*tower_grads))))

    @staticmethod
    def dying_decay(starter_learning_rate, train_iters, decay_iters, decay_steps):
        global_step = tf.train.get_or_create_global_step()

        start_decay = train_iters - decay_iters
        decay_rate = 1. - float(decay_steps) / float(decay_iters)
        learning_rate = tf.where(
            tf.greater_equal(global_step, start_decay),
            x=tf.train.exponential_decay(starter_learning_rate,
                                         global_step - start_decay,
                                         decay_steps,
                                         decay_rate),
            y=starter_learning_rate
        )

        return learning_rate

    @staticmethod
    def step_decay(starter_learning_rate, train_iters, decay_steps, decay_rate):
        global_step = tf.train.get_or_create_global_step()

        num_decay = train_iters // decay_steps

        boundaries = [decay_steps * (i + 1) for i in range(num_decay)]
        values = [starter_learning_rate * decay_rate ** i for i in range(num_decay + 1)]

        learning_rate = tf.train.piecewise_constant(global_step, boundaries, values)

        return learning_rate

    @staticmethod
    def lambda_decay(starter_learning_rate, lr_fn):
        global_step = tf.train.get_or_create_global_step()

        def fn(global_step, learning_rate):
            return np.float32(lr_fn(int(global_step), float(learning_rate)))

        return tf.py_func(fn, [global_step, starter_learning_rate], tf.float32)
