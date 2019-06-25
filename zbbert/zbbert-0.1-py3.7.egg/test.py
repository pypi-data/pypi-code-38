# -*- coding: utf-8 -*-

import tensorflow as tf
import os

os.environ['CUDA_VISIABLE_DEVICES'] = '0'
gpu_device_name = tf.test.gpu_device_name()
print(gpu_device_name)