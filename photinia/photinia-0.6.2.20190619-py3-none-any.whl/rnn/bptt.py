#!/usr/bin/env python3

"""
@author: xi
@since: 2018-08-22
"""

import numpy as np
import tensorflow as tf

import photinia as ph


class BPTT(ph.Model):

    def __init__(self,
                 name,
                 input_list,
                 input_prev_state,
                 state,
                 var_list,
                 optimizer=tf.train.RMSPropOptimizer(1e-5, 0.9, 0.9),
                 max_replay=None):
        """Back Propagation Through Time (BPTT)

        Args:
            name (str): Model name.
            input_list (list|tuple): The inputs of the RNN.
            input_prev_state: Input for the previous state of the RNN.
            state: The output state of the RNN.
            var_list (list|tuple): The parameters(variables) that want to train.
                This usually set as cell.get_trainable_variables().
            optimizer: The optimizer used to train the parameters.
            max_replay (int): The max length of the activation history.

        """
        self._input_list = input_list
        self._prev_state = input_prev_state
        self._state = state
        self._var_list = var_list
        self._optimizer = optimizer
        self._max_replay = max_replay

        self._state_size = input_prev_state.shape[1]
        self._replay = list()
        super(BPTT, self).__init__(name)

    def _build(self):
        self._step_get_state = ph.Step(
            inputs=(*self._input_list, self._prev_state),
            outputs=self._state
        )

        #
        # reset gradient
        grad_zeros_list = [
            tf.zeros(
                shape=var_.shape,
                dtype=var_.dtype,
                name='grad_' + ph.utils.get_basename(var_.name) + '_init'
            )
            for var_ in self._var_list
        ]
        self._grad_acc_list = [
            ph.variable(
                name='grad_' + ph.utils.get_basename(grad_zero.name),
                initial_value=grad_zero,
                trainable=False
            )
            for grad_zero in grad_zeros_list
        ]
        self._step_reset_grad = ph.Step(
            updates=tf.group(*[
                tf.assign(grad, value)
                for grad, value in zip(self._grad_acc_list, grad_zeros_list)
            ])
        )

        #
        # update gradient
        grad_state = ph.placeholder(
            name='grad_' + ph.utils.get_basename(self._prev_state.name),
            shape=self._prev_state.shape,
            dtype=self._prev_state.dtype
        )
        grad_weight = ph.placeholder('grad_weight', ())
        grad_list = tf.gradients(self._state, self._var_list, grad_state)
        grad_prev_state = tf.gradients(self._state, [self._prev_state], grad_state)[0]
        self._step_update_grad = ph.Step(
            inputs=(*self._input_list, self._prev_state, grad_state, grad_weight),
            outputs=(grad_prev_state, tf.reduce_sum(tf.abs(grad_prev_state))),
            updates=tf.group(*[
                tf.assign_add(grad_acc, grad * grad_weight)
                for grad_acc, grad in zip(self._grad_acc_list, grad_list)
            ])
        )

        #
        # apply gradient
        self._step_apply_grad = ph.Step(
            updates=self._optimizer.apply_gradients(
                zip(self._grad_acc_list, self._var_list)
            )
        )

    def reset(self):
        self._step_reset_grad()
        self._replay.clear()

    def get_state(self, input_list, prev_state=None):
        if prev_state is None:
            batch_size = len(input_list)
            prev_state = np.zeros((batch_size, self._state_size), np.float32)
        self._replay.append((input_list, prev_state))
        if self._max_replay is not None:
            if len(self._replay) > self._max_replay:
                self._replay.pop(0)
        return self._step_get_state(*input_list, prev_state)

    def update_gradients(self, grad_state, t=-1, weight=1.0):
        input_list, prev_state = self._replay[t]
        grad_state, a = self._step_update_grad(*input_list, prev_state, grad_state, weight)
        for input_list, prev_state in reversed(self._replay[:t]):
            grad_state, a = self._step_update_grad(*input_list, prev_state, grad_state, weight)

    def apply_gradients(self, reset=True):
        self._step_apply_grad()
        if reset:
            self.reset()
