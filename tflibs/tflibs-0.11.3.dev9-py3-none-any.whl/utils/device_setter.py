""" Device setter """
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import tensorflow as tf


def device_setter(device=None):
    cpu = '/cpu:0'

    def device_fn(op: tf.Operation):
        cpu_ops = ['Trainable_Variables', 'RandomShuffle', 'Summary', 'Const', 'Assert', 'PyFunc', 'DenseToDenseSetOperation']
        return cpu if any(map(lambda k: k in op.name or k in op.type, cpu_ops)) else device

    return device_fn if device is not None else cpu
