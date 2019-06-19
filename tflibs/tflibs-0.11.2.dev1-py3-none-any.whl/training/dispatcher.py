"""
    Dispatches operations over multiple GPU devices and calculates tower loss
"""
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import tensorflow as tf

from tflibs.utils import map_dict, unpack_tuple
from tflibs.training.optimizer import Optimizer


class Dispatcher:
    """
    A class for dispatching operations over multiple GPU devices and calculating tower loss

    :param class model_cls: Model class.
    :param dict model_param: A dict of model parameters.
    :param list gpus: A list of gpu ids.
    :param dict features: A dict of `tf.Tensor` containing feature values.
    :param tf.Tensor labels: A `tf.Tensor` of labels.
    """

    def __init__(self, model_cls, model_param, features, labels=None, num_towers=1, model_parallelism=True):
        # TODO: Even if features are not split into exact same size, process it

        # Split inputs
        split_feature_dict = map_dict(lambda k, v: (k, tf.split(v, num_towers)), features)
        split_features = list(
            map(lambda gpu: map_dict(lambda k, v: (k, v[gpu]), split_feature_dict), range(num_towers)))

        args = [split_features]
        if labels is not None:
            split_labels = tf.split(labels, num_towers)
            args.append(split_labels)

        self._models = list(map(unpack_tuple(lambda i, args: model_cls(*args,
                                                                       model_idx=i,
                                                                       model_parallelism=model_parallelism,
                                                                       **model_param)), enumerate(zip(*args))))

    def minimize(self, optimizer: Optimizer, loss_fn, depends=None, global_step=None, colocate_gradients_with_ops=True):
        """
        Gets `loss_fn` which maps model object to loss tensor, caculates tower loss and minimize it.

        :param tflibs.training.Optimizer optimizer: An optimizer.
        :param function loss_fn: A function that maps model object to loss tensor.
        :param tf.Operation depends: An operation that should be run before running an optimization.
        :param global_step:
        :param colocate_gradients_with_ops:
        :return: Train op.
        :rtype: tf.Operation
        """
        if not isinstance(depends, (tuple, list)):
            depends = [depends] if depends is not None else None

        with tf.control_dependencies(depends):
            def compute_grad(model):
                loss = loss_fn(model)
                return optimizer.compute_grad(loss, colocate_gradients_with_ops=colocate_gradients_with_ops)

            tower_grads = list(map(compute_grad, self._models))
            apply_grad_op = optimizer.apply_tower_gradients(tower_grads, global_step=global_step)

            return apply_grad_op

    @property
    def models(self):
        return self._models

    @property
    def chief(self):
        return self.models[0]
