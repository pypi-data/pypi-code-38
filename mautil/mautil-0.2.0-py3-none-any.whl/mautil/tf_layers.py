"""
the layer implementation for training variables sharing is based completely on scope.
This means if you create 2 layer object of Dense with same scope name, they will share variables.
By default it will use the layer name as the scope name
"""
import inspect
from collections import namedtuple
from functools import partial
from . import tf_util

import tensorflow as tf
from tensorflow.python.util import nest
from tensorflow.python.framework import tensor_shape
from tensorflow.python.framework import ops
from tensorflow.python.ops import math_ops
from tensorflow.python.ops import control_flow_ops


def add_dropout(inputs, dropout):
    outputs = []
    if not isinstance(inputs, tuple):
        inputs = tuple([inputs])

    for inp in inputs:
        if isinstance(dropout, Layer):
            output = dropout(inp)
        else:
            output = tf.nn.dropout(inp, keep_prob=dropout)
        outputs.append(output)
    if len(outputs) == 1:
        outputs = outputs[0]
    else:
        outputs = tuple(outputs)
    return outputs


class Layer(object):
    uid = 0

    def __init__(self, name = None, scope = None, initializer = None, **kwargs):
        self.name = self.__class__.__name__ + '_' + str(self.uid)
        self.__class__.uid += 1
        if name is not None:
            self.name = name

        if initializer is not None:
            self._initializer = initializer
        else:
            self._initializer = self._create_default_initializer()

        if scope is not None:
            with tf.variable_scope(scope, initializer=self._initializer, reuse=tf.AUTO_REUSE) as scope:
                self.scope = scope
        else:
            with tf.variable_scope(self.name, initializer=self._initializer, reuse=tf.AUTO_REUSE) as scope:
                self.scope = scope

        self._kwargs = kwargs
        self._input_dropout = kwargs.get('input_dropout', None)
        self._output_dropout = kwargs.get('output_dropout', None)

    def _create_default_initializer(self):
        return tf.contrib.layers.xavier_initializer(uniform=False)

    def get_vars(self):
        return tf.get_collection(tf.GraphKeys.TRAINABLE_VARIABLES, scope=self.scope.name)

    @property
    def weights(self):
        return self.get_vars()

    def _create_graph(self, inputs):
        return None

    def __call__(self, inputs, *args, **kwargs):
        with tf.variable_scope(self.scope, initializer=self._initializer):
            if self._input_dropout is not None:
                inputs = add_dropout(inputs, self._input_dropout)
            outputs = self._create_graph(inputs, *args, **kwargs)
            if self._output_dropout is not None:
                outputs = add_dropout(outputs, self._output_dropout)
            return outputs

    def __rrshift__(self, other, *args, **kwargs):
        """ >> """
        return self.__call__(other, *args, **kwargs)


class Dense(Layer):
    uid = 0

    def __init__(self, dim, activation=None, name=None, scope=None, initializer=None, **kwargs):
        super(Dense, self).__init__(name, scope, initializer, **kwargs)
        self.dim = dim
        self.activation = activation
        self.dense = partial(tf.layers.dense, kernel_initializer=self._initializer)

    def _create_graph(self, inputs):
        outs = self.dense(inputs, self.dim, activation=self.activation)
        return outs


class EMB(Layer):
    uid = 0

    def __init__(self, size, dim = None, embedding = None, trainable = True, name = None, scope=None, initializer=None, dtype=tf.float32, **kwargs):
        super(EMB, self).__init__(name, scope, initializer, **kwargs)
        self.size = size
        self.dim = dim
        self.embedding = embedding
        self.trainable = trainable
        self.dtype = dtype

    def _create_graph(self, inputs):
        if self.embedding is None:
            embed_var = tf.get_variable(self.name, [self.size, self.dim], dtype=self.dtype, trainable=self.trainable)
        else:
            embed_var = tf.get_variable(self.name, initializer=self.embedding, trainable=self.trainable)
        embedded = tf.nn.embedding_lookup(embed_var, inputs)
        return embedded


class CNN(Layer):
    uid = 0

    def __init__(self, dims, strides=None, name=None, scope=None, initializer=None, init_bias=0.0, padding='VALID', **kwargs):
        """
        :param dims: dims of filter 2d(height, width, channels), 1d(time, channels)
        """
        super(CNN, self).__init__(name, scope, initializer, **kwargs)
        self.dims = dims
        self.padding = padding
        self.init_bias = init_bias
        self.strides = strides

    def _create_graph(self, inputs):
        input_dim = inputs.get_shape().dims[-1].value
        dims = list(self.dims).copy()
        dims.insert(-1, input_dim)
        filters = tf.get_variable(self.name, dims, dtype=inputs.dtype)
        bias = tf.get_variable(self.name+'_b', dtype=inputs.dtype, initializer=tf.constant([self.init_bias]*self.dims[-1]))
        strides = self.strides
        if len(self.dims) == 3:
            if strides is None:
                strides = [1]*4
            outputs = tf.nn.conv2d(inputs, filters, strides, padding=self.padding) + bias
        elif len(self.dims) == 2:
            if strides is None:
                strides = 1
            outputs = tf.nn.conv1d(inputs, filters, strides, padding=self.padding) + bias
        return outputs


class RNN(Layer):
    uid = 0

    def __init__(self, dims, bidirection=True, cell_cls='tensorflow.nn.rnn_cell.GRUCell', dtype=tf.float32, swap_memory=True, name=None, scope=None, initializer=None, dropout=None, **kwargs):
        super(RNN, self).__init__(name, scope, initializer, **kwargs)
        self.dims = dims
        self.cell_cls = cell_cls
        self.bidirection = bidirection
        self.dtype = dtype
        self.dropout = dropout
        self.swap_memory = swap_memory
        self.cell = self._create_cell()
        if self.bidirection:
            self.cell_bw = self._create_cell()

    def _create_default_initializer(self):
        return tf.orthogonal_initializer()

    def _create_cell(self):
        multi_cell = tf_util.create_rnn_cell(self.dims, self.cell_cls, self.dropout)
        return multi_cell

    def _create_graph(self, inputs, inputs_lens=None, initial_state=None, rnn_func=None):
        if rnn_func is None:
            if self.bidirection:
                if initial_state is not None:
                    initial_state_fw, initial_state_bw = initial_state
                else:
                    initial_state_fw = None
                    initial_state_bw = None
                outs, stats = tf.nn.bidirectional_dynamic_rnn(self.cell, cell_bw, inputs, sequence_length = inputs_lens,  swap_memory = self.swap_memory,
                                                              dtype=self.dtype, initial_state_fw=initial_state_fw, initial_state_bw=initial_state_bw, scope=self.scope)
            else:
                outs, stats= tf.nn.dynamic_rnn(self.cell, inputs, sequence_length=inputs_lens,  swap_memory=self.swap_memory, dtype=self.dtype, initial_state=initial_state, scope=self.scope)
            if len(self.dims) == 1:
                if self.bidirection:
                    stats = tuple([s[-1] for s in stats])
                else:
                    stats = stats[-1]
            return outs, stats
        else:
            return rnn_func(self.cell, inputs, initial_state=initial_state)


class GumbelTeacherForceHelper(tf.contrib.seq2seq.TrainingHelper):
    def __init__(self, inputs, proj_layer, embedding, max_len, softmax_temperature, dropout=None):
        self._proj_layer = proj_layer
        self._embedding = embedding
        self._softmax_temperature = softmax_temperature
        self._dropout = dropout
        batch_size = tf.shape(inputs)[0]
        self._inputs_dim = inputs.get_shape().dims[-1]
        self._inputs_dtype = inputs.dtype
        sequence_lens = tf.ones([batch_size], dtype=tf.int32)*max_len
        super(GumbelTeacherForceHelper, self).__init__(inputs, sequence_lens)

    @property
    def sample_output_shape(self):
        return tuple([tensor_shape.TensorShape([self._inputs_dim]), tensor_shape.TensorShape([self._proj_layer.dim])])

    @property
    def sample_output_dtype(self):
        return self._inputs_dtype, self._inputs_dtype

    def sample(self, time, outputs, state, name=None):
        """sample for GreedyEmbeddingHelper."""
        del time, state  # unused by sample_fn
        # Outputs are logits, use argmax to get the most probable id
        if not isinstance(outputs, ops.Tensor):
            raise TypeError("Expected outputs to be a single Tensor, got: %s" %
                            type(outputs))
        logits = self._proj_layer(outputs)
        prob = tf_util.gumbel_softmax(logits, self._softmax_temperature)
        inp = tf.matmul(prob, self._embedding)
        if self._dropout is not None:
            inp = add_dropout(inp, dropout=self._dropout)
        return inp, logits

    def next_inputs(self, time, outputs, state, sample_outputs, name=None, **unused_kwargs):
        """next_inputs_fn for TrainingHelper."""
        with ops.name_scope(name, "TrainingHelperNextInputs",
                            [time, outputs, state]):
            next_time = time + 1
            finished = (next_time >= self._sequence_length)
            all_finished = math_ops.reduce_all(finished)
            next_inputs = sample_outputs[0]

            next_inputs = control_flow_ops.cond(
                all_finished, lambda: self._zero_inputs,
                lambda: next_inputs)
        return (finished, next_inputs, state)


class BasicDecoder(tf.contrib.seq2seq.BasicDecoder):
    class BasicDecoderOutput(namedtuple("BasicDecoderOutput", ("rnn_output", "sample_output"))):
        pass

    @property
    def output_size(self):
        # Return the cell output and the id
        if hasattr(self._helper, 'sample_output_shape'):
            sample_output = self._helper.sample_output_shape
        else:
            sample_output = self._helper.sample_ids_shape

        return self.BasicDecoderOutput(
            rnn_output=self._rnn_output_size(),
            sample_output=sample_output)

    @property
    def output_dtype(self):
        # Assume the dtype of the cell is the output_size structure
        # containing the input_state's first component's dtype.
        dtype = nest.flatten(self._initial_state)[0].dtype

        if hasattr(self._helper, 'sample_output_dtype'):
            sample_output = self._helper.sample_output_dtype
        else:
            sample_output = self._helper.sample_ids_dtype

        return self.BasicDecoderOutput(
            nest.map_structure(lambda _: dtype, self._rnn_output_size()),
            sample_output)

    def step(self, time, inputs, state, name=None):
        """Perform a decoding step.
        Args:
          time: scalar `int32` tensor.
          inputs: A (structure of) input tensors.
          state: A (structure of) state tensors and TensorArrays.
          name: Name scope for any created operations.
        Returns:
          `(outputs, next_state, next_inputs, finished)`.
        """
        with ops.name_scope(name, "BasicDecoderStep", (time, inputs, state)):
            cell_outputs, cell_state = self._cell(inputs, state)
            if self._output_layer is not None:
                cell_outputs = self._output_layer(cell_outputs)
            sample_outputs = self._helper.sample(
                time=time, outputs=cell_outputs, state=cell_state)
            if 'sample_outputs' in inspect.signature(self._helper.next_inputs).parameters:
                (finished, next_inputs, next_state) = self._helper.next_inputs(
                time=time,
                outputs=cell_outputs,
                state=cell_state,
                sample_outputs=sample_outputs)
            else:
                (finished, next_inputs, next_state) = self._helper.next_inputs(
                    time=time,
                    outputs=cell_outputs,
                    state=cell_state,
                    sample_ids=sample_outputs)
        outputs = self.BasicDecoderOutput(cell_outputs, sample_outputs)

        return (outputs, next_state, next_inputs, finished)


class DRNN(RNN):
    def _create_graph(self, inputs, inputs_lens=None, initial_state=None, max_len=None, helper_func=None, decoder_func=None, parallel_iterations=32, output_layer=None):
        if helper_func is None:
            return super(DRNN, self)._create_graph(inputs, inputs_lens, initial_state, None)
        else:
            dtype = inputs.dtype
            helper = helper_func(inputs)
            if initial_state is None:
                initial_state = self.cell.zero_state(tf.shape(inputs)[0], dtype)
            decoder = BasicDecoder(self.cell, helper, initial_state, output_layer=output_layer)
            outputs, state, sequence_lengths = tf.contrib.seq2seq.dynamic_decode(decoder, maximum_iterations=max_len, swap_memory=self.swap_memory, parallel_iterations=parallel_iterations, scope=self.scope)
            return outputs, state, sequence_lengths


class CudnnGRU(RNN):
    uid = 0
    def _create_graph(self, inputs, inputs_lens=None, initial_state=None, fetch_last_cell=True):
        if self.bidirection:
            direction = 'bidirectional'
        else:
            direction = 'unidirectional'
        rnn = tf.contrib.cudnn_rnn.CudnnGRU(len(self.dims), self.dims[-1], direction=direction)

        inputs = tf_util.transpose(inputs, 0, 1)
        outs, stats = rnn(inputs)
        stats = tuple(tf.squeeze(s, 0) for s in stats)
        outs = tf_util.transpose(outs, 0, 1)
        if fetch_last_cell:
            stats = stats[-1]
            if inputs_lens is not None:
                inds = tf.stack([tf.range(tf.shape(inputs_lens)[0]), inputs_lens - 1], 1)
                stats = tf.gather_nd(outs, inds)


        return outs, stats


