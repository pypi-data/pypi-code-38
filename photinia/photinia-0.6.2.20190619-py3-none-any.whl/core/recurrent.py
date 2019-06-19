#!/usr/bin/env python3


"""
@author: xi
@since: 2016-11-11
"""

import tensorflow as tf

from . import common
from .. import conf
from .. import init


class GRUCell(common.Widget):

    def __init__(self,
                 name,
                 input_size,
                 state_size,
                 with_bias=False,
                 w_init=init.TruncatedNormal(0, 1e-3),
                 u_init=init.Orthogonal(),
                 b_init=init.Zeros()):
        """The GRU cell.

        Args:
            name (str): The widget name.
            input_size: The input size.
            state_size: The state size.
            with_bias: If this cell has bias.
            w_init: The input weight initializer.
            u_init: The recurrent weight initializer.
            b_init: The bias initializer.

        """
        self._input_size = input_size
        self._state_size = state_size
        self._with_bias = with_bias
        self._w_init = w_init
        self._u_init = u_init
        self._b_init = b_init
        super(GRUCell, self).__init__(name)

    @property
    def input_size(self):
        return self._input_size

    @property
    def state_size(self):
        return self._state_size

    @property
    def output_size(self):
        return self._state_size

    @property
    def with_bias(self):
        return self._with_bias

    def _build(self):
        """Build the cell.
        The GRU cell is consists of 3 kinds of parameters:
        1) Update gate parameters (wz, uz, bz).
        2) Reset gate parameters (wr, ur, br).
        3) Activation parameters (wh, uh, bh).

        """
        self._wz = self._variable(
            name='wz',
            initializer=self._w_init,
            shape=(self._input_size, self._state_size),
            dtype=conf.dtype
        )
        self._wr = self._variable(
            name='wr',
            initializer=self._w_init,
            shape=(self._input_size, self._state_size),
            dtype=conf.dtype
        )
        self._wh = self._variable(
            name='wh',
            initializer=self._w_init,
            shape=(self._input_size, self._state_size),
            dtype=conf.dtype
        )
        #
        self._uz = self._variable(
            name='uz',
            initializer=self._u_init,
            shape=(self._state_size, self._state_size),
            dtype=conf.dtype
        )
        self._ur = self._variable(
            name='ur',
            initializer=self._u_init,
            shape=(self._state_size, self._state_size),
            dtype=conf.dtype
        )
        self._uh = self._variable(
            name='uh',
            initializer=self._u_init,
            shape=(self._state_size, self._state_size),
            dtype=conf.dtype
        )
        if self._with_bias:
            self._bz = self._variable(
                name='bz',
                initializer=self._b_init,
                shape=(self._state_size,),
                dtype=conf.dtype
            )
            self._br = self._variable(
                name='br',
                initializer=self._b_init,
                shape=(self._state_size,),
                dtype=conf.dtype
            )
            self._bh = self._variable(
                name='bh',
                initializer=self._b_init,
                shape=(self._state_size,),
                dtype=conf.dtype
            )

    @property
    def wz(self):
        return self._wz

    @property
    def wr(self):
        return self._wr

    @property
    def wh(self):
        return self._wh

    @property
    def uz(self):
        return self._uz

    @property
    def ur(self):
        return self._ur

    @property
    def uh(self):
        return self._uh

    @property
    def bz(self):
        return self._bz if self._with_bias else None

    @property
    def br(self):
        return self._br if self._with_bias else None

    @property
    def bh(self):
        return self._bh if self._with_bias else None

    def _setup(self,
               x,
               prev_h,
               activation=tf.nn.tanh,
               name='out'):
        """Setup the cell.

        Args:
            x: The input tensor. shape = (batch_size, input_size)
            prev_h: The previous state tensor. shape = (batch_size, state_size)
            activation: The activation function.
            name (str): The output name.

        Returns:
            The state tensor. shape = (batch_size, state_size)

        """
        if self._with_bias:
            z = tf.sigmoid(
                tf.matmul(x, self._wz) + tf.matmul(prev_h, self._uz) + self._bz,
                name='update_gate'
            )
            r = tf.sigmoid(
                tf.matmul(x, self._wr) + tf.matmul(prev_h, self._ur) + self._br,
                name='reset_gate'
            )
            h = tf.matmul(x, self._wh) + tf.matmul(r * prev_h, self._uh) + self._bh
        else:
            z = tf.sigmoid(
                tf.matmul(x, self._wz) + tf.matmul(prev_h, self._uz),
                name='update_gate'
            )
            r = tf.sigmoid(
                tf.matmul(x, self._wr) + tf.matmul(prev_h, self._ur),
                name='reset_gate'
            )
            h = tf.matmul(x, self._wh) + tf.matmul(r * prev_h, self._uh)
        h = activation(h) if activation is not None else h
        h = tf.add(z * prev_h, (1.0 - z) * h, name=name)
        return h


class LSTMCell(common.Widget):

    def __init__(self,
                 name,
                 input_size,
                 state_size,
                 with_bias=True,
                 w_init=init.TruncatedNormal(0, 1e-3),
                 u_init=init.Orthogonal(),
                 b_init=init.Zeros()):
        """LSTM cell.

        Args:
            name (str): Widget name.
            input_size (int): Input size.
            state_size (int): State size.
            with_bias (bool): If True, the cell will involve biases.
            w_init (init.Initializer): Input weight initializer.
            u_init (initializers.Initializer): Recurrent weight initializer.
            b_init (initializers.Initializer): Bias initializer.

        """
        self._input_size = input_size
        self._state_size = state_size
        self._with_bias = with_bias
        self._w_init = w_init
        self._u_init = u_init
        self._b_init = b_init
        super(LSTMCell, self).__init__(name)

    @property
    def input_size(self):
        return self._input_size

    @property
    def state_size(self):
        return self._state_size

    @property
    def output_size(self):
        return self._state_size

    def _build(self):
        """Build the cell.
        The LSTM cell is consists of 4 kinds of parameters:
        1) Input gate parameters (wi, ui, bi).
        2) Forget gate parameters (wf, uf, bf).
        3) Output gate parameters (wo, uo, bo).
        4) Activation parameters (wc, uc, bc).

        """
        self._wi = self._variable(
            name='wi',
            initializer=self._w_init,
            shape=(self._input_size, self._state_size),
            dtype=conf.dtype
        )
        self._wf = self._variable(
            name='wf',
            initializer=self._w_init,
            shape=(self._input_size, self._state_size),
            dtype=conf.dtype
        )
        self._wo = self._variable(
            name='wo',
            initializer=self._w_init,
            shape=(self._input_size, self._state_size),
            dtype=conf.dtype
        )
        self._wc = self._variable(
            name='wc',
            initializer=self._w_init,
            shape=(self._input_size, self._state_size),
            dtype=conf.dtype
        )
        #
        self._ui = self._variable(
            name='ui',
            initializer=self._u_init,
            shape=(self._state_size, self._state_size),
            dtype=conf.dtype
        )
        self._uf = self._variable(
            name='uf',
            initializer=self._u_init,
            shape=(self._state_size, self._state_size),
            dtype=conf.dtype
        )
        self._uo = self._variable(
            name='uo',
            initializer=self._u_init,
            shape=(self._state_size, self._state_size),
            dtype=conf.dtype
        )
        self._uc = self._variable(
            name='uc',
            initializer=self._u_init,
            shape=(self._state_size, self._state_size),
            dtype=conf.dtype
        )
        #
        if self._with_bias:
            self._bi = self._variable(
                name='bi',
                initializer=self._b_init,
                shape=(self._state_size,),
                dtype=conf.dtype
            )
            self._bf = self._variable(
                name='bf',
                initializer=self._b_init,
                shape=(self._state_size,),
                dtype=conf.dtype
            )
            self._bo = self._variable(
                name='bo',
                initializer=self._b_init,
                shape=(self._state_size,),
                dtype=conf.dtype
            )
            self._bc = self._variable(
                name='bc',
                initializer=self._b_init,
                shape=(self._state_size,),
                dtype=conf.dtype
            )

    @property
    def wi(self):
        return self._wi

    @property
    def wf(self):
        return self._wf

    @property
    def wo(self):
        return self._wo

    @property
    def wc(self):
        return self._wc

    @property
    def ui(self):
        return self._ui

    @property
    def uf(self):
        return self._uf

    @property
    def uo(self):
        return self._uo

    @property
    def uc(self):
        return self._uc

    @property
    def bi(self):
        return self._bi if self._with_bias else None

    @property
    def bf(self):
        return self._bf if self._with_bias else None

    @property
    def bo(self):
        return self._bo if self._with_bias else None

    @property
    def bc(self):
        return self._bc if self._with_bias else None

    def _setup(self,
               x,
               prev_cell_state,
               prev_state,
               activation=tf.nn.tanh):
        """Setup the cell.

        Args:
            x (tf.Tensor): Input tensor.
                (batch_size, input_size)
            prev_cell_state (tf.Tensor): Previous cell state.
                (batch_size, state_size)
            prev_state (tf.Tensor): Previous state.
                (batch_size, state_size)
            activation: The activation function.

        Returns:
            tuple[tf.Tensor]: Tuple of cell states and states.
                (batch_size, seq_length, state_size)
                (batch_size, seq_length, state_size)

        """
        if self._with_bias:
            input_gate = tf.nn.sigmoid(
                tf.matmul(x, self._wi) + tf.matmul(prev_state, self._ui) + self._bi,
                name='input_gate'
            )
            forget_gate = tf.nn.sigmoid(
                tf.matmul(x, self._wf) + tf.matmul(prev_state, self._uf) + self._bf,
                name='forget_gate'
            )
            output_gate = tf.nn.sigmoid(
                tf.matmul(x, self._wo) + tf.matmul(prev_state, self._uo) + self._bo,
                name='output_gate'
            )
            cell_state = tf.matmul(x, self._wc) + tf.matmul(prev_state, self._uc) + self._bc
        else:
            input_gate = tf.nn.sigmoid(
                tf.matmul(x, self._wi) + tf.matmul(prev_state, self._ui),
                name='input_gate'
            )
            forget_gate = tf.nn.sigmoid(
                tf.matmul(x, self._wf) + tf.matmul(prev_state, self._uf),
                name='forget_gate'
            )
            output_gate = tf.nn.sigmoid(
                tf.matmul(x, self._wo) + tf.matmul(prev_state, self._uo),
                name='output_gate'
            )
            cell_state = tf.matmul(x, self._wc) + tf.matmul(prev_state, self._uc)
        if activation is not None:
            cell_state = activation(cell_state)
        cell_state = tf.add(forget_gate * prev_cell_state, input_gate * cell_state, name='cell_state')
        if activation is not None:
            cell_state = activation(cell_state)
        state = tf.multiply(output_gate, cell_state, name='state')
        return cell_state, state


class GRU(common.Widget):

    def __init__(self,
                 name,
                 input_size,
                 state_size,
                 activation=tf.nn.tanh):
        """The recurrent neural network with GRU cell.
        All sequence shapes follow (batch_size, seq_len, state_size).

        Args:
            name (str): The widget name.
            input_size: The input size.
            state_size: The state size.
            activation: The activation function for the GRU cell.

        """
        self._input_size = input_size
        self._state_size = state_size
        self._activation = activation
        super(GRU, self).__init__(name)

    @property
    def input_size(self):
        return self._input_size

    @property
    def state_size(self):
        return self._state_size

    @property
    def output_size(self):
        return self._state_size

    def _build(self):
        self._cell = GRUCell(
            'cell',
            input_size=self._input_size,
            state_size=self._state_size
        )

    def _setup(self,
               seq,
               init_state=None,
               name='states'):
        """Setup a sequence.

        Args:
            seq: The sequences.
                shape = (batch_size, seq_len, input_size)
            init_state: The initial state.
                shape = (batch_size, state_size)

        Returns:
            The forward states.
                shape = (batch_size, seq_len, state_size)

        """
        # check forward and backward initial states
        if init_state is None:
            batch_size = tf.shape(seq)[0]
            init_state = tf.zeros(shape=(batch_size, self._state_size), dtype=conf.dtype)

        # connect
        states_forward = tf.scan(
            fn=lambda acc, elem: self._cell.setup(elem, acc, activation=self._activation),
            elems=tf.transpose(seq, [1, 0, 2]),
            initializer=init_state
        )
        states_forward = tf.transpose(states_forward, [1, 0, 2], name=name)

        return states_forward


class BiGRU(common.Widget):

    def __init__(self,
                 name,
                 input_size,
                 state_size,
                 activation=tf.nn.tanh):
        """A very simple BiGRU structure comes from zhkun.
        All sequence shapes follow (batch_size, seq_len, state_size).

        Args:
            name (str): The widget name.
            input_size: The input size.
            state_size: The state size.
            activation: The activation function for the GRU cell.

        """
        self._input_size = input_size
        self._state_size = state_size
        self._activation = activation
        super(BiGRU, self).__init__(name)

    @property
    def input_size(self):
        return self._input_size

    @property
    def state_size(self):
        return self._state_size

    @property
    def output_size(self):
        return self._state_size

    def _build(self):
        self._cell_forward = GRUCell(
            'cell_forward',
            input_size=self._input_size,
            state_size=self._state_size
        )
        self._cell_backward = GRUCell(
            'cell_backward',
            input_size=self._input_size,
            state_size=self._state_size
        )

    def _setup(self,
               seq,
               init_state=None,
               name='states'):
        """Setup a sequence.

        Args:
            seq: A sequence or a pair of sequences.
                shape = (batch_size, seq_len, input_size)
            init_state: A tensor or a pair of tensors.

        Returns:
            The forward states and the backward states.
                shape = (batch_size, seq_len, state_size)

        """
        # check forward and backward sequences
        if isinstance(seq, (tuple, list)):
            if len(seq) != 2:
                raise ValueError('The seqs should be tuple with 2 elements.')
            seq_forward, seq_backward = seq
        else:
            seq_forward = seq
            seq_backward = tf.reverse(seq, axis=[1])

        # check forward and backward initial states
        if init_state is None:
            batch_size = tf.shape(seq_forward)[0]
            init_state_forward = tf.zeros(shape=(batch_size, self._state_size), dtype=conf.dtype)
            init_state_backward = tf.zeros(shape=(batch_size, self._state_size), dtype=conf.dtype)
        elif isinstance(init_state, (tuple, list)):
            if len(seq) != 2:
                raise ValueError('The init_states should be tuple with 2 elements.')
            init_state_forward, init_state_backward = init_state
        else:
            init_state_forward = init_state
            init_state_backward = init_state

        # connect
        states_forward = tf.scan(
            fn=lambda acc, elem: self._cell_forward.setup(elem, acc, activation=self._activation),
            elems=tf.transpose(seq_forward, [1, 0, 2]),
            initializer=init_state_forward
        )
        states_forward = tf.transpose(states_forward, [1, 0, 2], name=f'{name}_forward')
        states_backward = tf.scan(
            fn=lambda acc, elem: self._cell_backward.setup(elem, acc, activation=self._activation),
            elems=tf.transpose(seq_backward, [1, 0, 2]),
            initializer=init_state_backward
        )
        states_backward = tf.transpose(states_backward, [1, 0, 2], name=f'{name}_backward')

        return states_forward, states_backward
