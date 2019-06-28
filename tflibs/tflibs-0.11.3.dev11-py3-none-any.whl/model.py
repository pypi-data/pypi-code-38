"""
    Model
    ~~~~~
"""
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import argparse
from collections import Iterable

import tensorflow as tf

from tflibs.utils import Attributes, image_summary


class _TensorDescriptor:
    def __init__(self, fn=None, summary=None):
        self._summary = summary

        self.fn = fn

    def __get__(self, instance, owner):
        val = self.fn(instance)

        if self.summary is not None:
            def define_summary(summary_name, tensor):
                if tensor.shape.ndims == 0:
                    tf.summary.scalar(summary_name, tensor)
                else:
                    tf.summary.histogram(summary_name, tensor)

            if isinstance(val, tf.Tensor):
                define_summary(self.summary, val)
            elif isinstance(val, Iterable):
                for i, t in enumerate(val):
                    define_summary('{}/{}'.format(self.summary, i), t)
            else:
                raise ValueError('Tensor should be either `tf.Tensor` or iterable of `tf.Tensor`')

            tf.logging.info('Summary {} is defined'.format(self.summary))

        setattr(instance, self.name, val)
        return val

    def __call__(self, fn):
        self.fn = fn

        return self

    @property
    def summary(self):
        return self._summary

    @property
    def fn(self):
        return self._fn

    @fn.setter
    def fn(self, new_fn):
        self._fn = new_fn
        if hasattr(new_fn, '__name__'):
            self._name = new_fn.__name__

    @property
    def name(self):
        return self._name


class _ImageDescriptor(_TensorDescriptor):
    def __init__(self, fn=None, summary=None):
        _TensorDescriptor.__init__(self, fn=fn, summary=None)

        self._img_summary = summary

    def __get__(self, instance, owner):
        val = _TensorDescriptor.__get__(self, instance, owner)

        if self.img_summary is not None:
            image_summary(self.img_summary, val)
            tf.logging.info('Summary {} is defined at `Images`'.format(self.img_summary))

        return val

    @property
    def img_summary(self):
        return self._img_summary


class _LossDescriptor(_TensorDescriptor):
    def __init__(self, fn=None, summary=None):
        _TensorDescriptor.__init__(self, fn=fn, summary=None)

        self._loss_summary = summary

    def __get__(self, instance, owner):
        val = _TensorDescriptor.__get__(self, instance, owner)

        if val not in tf.losses.get_losses():
            val = tf.identity(val, name='{}/value'.format(self.loss_summary))
            tf.losses.add_loss(val)

        return val

    @property
    def loss_summary(self):
        return self._loss_summary


class Model:
    tensor = _TensorDescriptor
    image = _ImageDescriptor
    loss = _LossDescriptor

    def __init__(self, features: dict, labels=None, **hparams):
        self._features = features
        self._labels = labels

        self._hparams = Attributes(**hparams)
        self._networks = Attributes()

    @property
    def features(self):
        return self._features

    @property
    def labels(self):
        return self._labels

    @property
    def hparams(self):
        return self._hparams

    @property
    def networks(self):
        return self._networks

    @staticmethod
    def model_fn(features, labels, mode, params):
        raise NotImplementedError

    @classmethod
    def add_model_args(cls, argparser: argparse.ArgumentParser, parse_args: argparse.Namespace):
        pass

    @classmethod
    def add_train_args(cls, argparser: argparse.ArgumentParser, parse_args: argparse.Namespace):
        pass

    @classmethod
    def add_eval_args(cls, argparser: argparse.ArgumentParser, parse_args: argparse.Namespace):
        pass

    @classmethod
    def make_map_fn(cls, mode, **hparams):
        raise NotImplementedError

    def summary_loss(self):
        losses = tf.losses.get_losses()
        tf.logging.info('Defining summaries of losses')
        for loss in losses:
            lname = loss.name  # type: str
            tokens = lname.split('/')
            while True:
                token = tokens.pop()
                token = token.rstrip(':0')
                if token != 'value':
                    tf.summary.scalar(token, loss, family='Losses')
                    tf.logging.info('Summary {} is defined at `Losses`'.format(token))
                    break


class Network:
    def __init__(self, **hparams):
        self._hparams = Attributes(**hparams)

    @property
    def hparams(self):
        return self._hparams

    def __call__(self, *args, **kwargs):
        raise NotImplementedError
