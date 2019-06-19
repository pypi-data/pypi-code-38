#!/usr/bin/env python3

"""
@author: xi
@since: 2018-09-04
"""

import math

import tensorflow as tf

import photinia as ph


class GlimpseNetwork(ph.Widget):

    def __init__(self,
                 name,
                 retina_height,
                 retina_width,
                 num_channels,
                 num_scales,
                 h_input_size,
                 h_loc_size,
                 output_size):
        """The default glimpse network for images.

        Args:
            name (str): Widget name.
            retina_height (int): Retina height.
            retina_width (int): Retina width.
            num_channels (int): Number of channels.
            num_scales (int): NUmber of scales.
            h_input_size (int): Hidden size for input.
            h_loc_size (int): Hidden size for location.
            output_size (int): Output size.

        """
        self._retina_height = retina_height
        self._retina_width = retina_width
        self._num_channels = num_channels
        self._num_scales = num_scales
        self._h_input_size = h_input_size
        self._h_loc_size = h_loc_size
        self._output_size = output_size
        super(GlimpseNetwork, self).__init__(name)

    @property
    def retina_height(self):
        return self._retina_height

    @property
    def retina_width(self):
        return self._retina_width

    @property
    def num_channels(self):
        return self._num_channels

    @property
    def num_scales(self):
        return self._num_scales

    @property
    def output_size(self):
        return self._output_size

    def _build(self):
        input_size = self._input_size = self._retina_height * self._retina_width * self._num_channels
        self._input_layer = ph.Linear('input_layer', input_size * 3, self._h_input_size)
        self._loc_layer = ph.Linear('loc_layer', 2, self._h_loc_size)
        self._output_layer = ph.Linear('output_layer', self._h_input_size + self._h_loc_size, self._output_size)

    def _setup(self, x, loc, name='out'):
        glimpses = list()
        for i in range(1, self._num_scales + 1):
            glimpse = tf.image.extract_glimpse(x, (self._retina_height * i, self._retina_width * i), loc)
            glimpse = tf.image.resize_images(glimpse, (self._retina_height, self._retina_width))
            glimpse = tf.reshape(glimpse, (-1, self._input_size))
            glimpses.append(glimpse)

        h_x = self._input_layer.setup(tf.concat(glimpses, axis=1))
        h_x = ph.ops.lrelu(h_x)

        h_loc = self._loc_layer.setup(loc)
        h_loc = ph.ops.lrelu(h_loc)

        y = tf.concat((h_x, h_loc), axis=1)
        y = self._output_layer.setup(y)
        y = ph.ops.lrelu(y, name=name)
        return y


class LocationNetwork(ph.Widget):

    def __init__(self,
                 name,
                 input_size,
                 output_size):
        """The default location network.

        Args:
            name (str): Widget name.
            input_size (int): Input size.
            output_size (int): Output size. The dimension of the location vector.

        """
        self._input_size = input_size
        self._output_size = output_size
        super(LocationNetwork, self).__init__(name)

    @property
    def input_size(self):
        return self._input_size

    @property
    def output_size(self):
        return self._output_size

    def _build(self):
        self._layer = ph.Linear('layer', self._input_size, self._output_size)

    def _setup(self, x, stddev):
        mean = self._layer.setup(x)
        mean = tf.nn.tanh(mean)

        loc = mean + tf.random_normal(
            shape=(tf.shape(x)[0], self._output_size),
            stddev=stddev,
            dtype=ph.dtype
        )
        loc = tf.clip_by_value(loc, -1.0, 1.0)
        loc = tf.stop_gradient(loc)

        return loc, mean


class RecurrentAttentionNetwork(ph.Model):

    def __init__(self,
                 name,
                 input_x,
                 glimpse_network,
                 location_network,
                 state_size,
                 num_classes,
                 num_steps,
                 stddev=0.1,
                 num_mc_samples=10,
                 optimizer=tf.train.RMSPropOptimizer(1e-4, 0.9, 0.9),
                 reg=ph.reg.L1L2Regularizer(1e-5)):
        """Recurrent Attention Network.

        Args:
            name (str): Widget name.
            input_x: Input of the network. It can be a placeholder.
            glimpse_network (ph.Widget): The glimpse network.
            location_network (ph.Widget): The location network.
            state_size (int): State size.
            num_classes (int): Number of the classes.
            num_steps (int): Number of step of the RNN.
            stddev (float): stddev for sampling.
            num_mc_samples (int): Number of Monte Carlo samplings.
            optimizer: Optimizer.
            reg (ph.reg.Regularizer): Regularizer.

        """
        self._input_x = input_x
        self._glimpse_network = glimpse_network
        self._location_network = location_network
        self._state_size = state_size
        self._num_classes = num_classes
        self._num_steps = num_steps
        self._stddev = stddev
        self._num_mc_samples = num_mc_samples
        self._optimizer = optimizer
        self._reg = reg
        super(RecurrentAttentionNetwork, self).__init__(name)

    @property
    def state_size(self):
        return self._state_size

    @property
    def num_classes(self):
        return self._num_classes

    @property
    def num_steps(self):
        return self._num_steps

    def _build(self):
        input_x = tf.tile(self._input_x, [self._num_mc_samples] + [1] * (len(self._input_x.shape) - 1))
        g_net = self._glimpse_network
        l_net = self._location_network

        input_stddev = tf.placeholder(
            shape=(),
            dtype=ph.dtype,
            name='input_stddev'
        )

        cell = self._cell = ph.GRUCell(
            'cell',
            g_net.output_size,
            self._state_size,
            w_init=ph.init.GlorotUniform()
        )
        batch_size = tf.shape(input_x)[0]
        init_state = tf.zeros(shape=(batch_size, self._state_size), dtype=ph.dtype)
        init_loc = tf.random_uniform((batch_size, 2), minval=-1, maxval=1)

        def _loop(acc, _):
            prev_state, loc, _ = acc
            g = g_net.setup(input_x, loc)
            state = cell.setup(g, prev_state)
            next_loc, next_mean = l_net.setup(state, input_stddev)
            return state, next_loc, next_mean

        states, locs, means = tf.scan(
            fn=_loop,
            elems=tf.zeros(shape=(self._num_steps,), dtype=tf.int8),
            initializer=(init_state, init_loc, init_loc)
        )  # (num_steps, batch_size, *)

        baseline_layer = self._baseline_layer = ph.Linear('baseline_layer', self._state_size, 1)

        def _make_baseline(state):
            baseline = baseline_layer.setup(state)  # (batch_size, 1)
            baseline = tf.reshape(baseline, (-1,))  # (batch_size,)
            return baseline

        baselines = tf.map_fn(_make_baseline, states)  # (num_steps, batch_size)
        baselines = tf.transpose(baselines)  # (batch_size, num_steps)

        predict_layer = self._predict_layer = ph.Linear('predict_layer', self._state_size, self._num_classes)
        last_state = states[-1]  # (batch_size, state_size)
        prob = predict_layer.setup(last_state)
        prob = tf.nn.softmax(prob)  # (batch_size, num_classes)
        label = tf.argmax(prob, 1)  # (batch_size,)
        self._step_predict = ph.Step(
            inputs=input_x,
            outputs=label,
            givens={input_stddev: 1e-3}
        )

        self._input_label = ph.placeholder('input_label', (None,), tf.int64)
        input_label = tf.tile(self._input_label, (self._num_mc_samples,))
        prob_ = tf.one_hot(input_label, self._num_classes)  # (batch_size, num_classes)
        predict_loss = self._predict_loss = -tf.reduce_mean(ph.ops.log_likelihood(prob_, prob))

        reward = tf.cast(tf.equal(label, input_label), tf.float32)  # (batch_size,)
        rewards = tf.reshape(reward, (-1, 1))  # (batch_size, 1)
        rewards = tf.tile(rewards, (1, self._num_steps))  # (batch_size, num_steps)
        rewards = tf.stop_gradient(rewards)
        baseline_loss = self._baseline_loss = tf.reduce_mean(ph.ops.mean_square_error(rewards, baselines))

        advantages = rewards - tf.stop_gradient(baselines)
        logll = self._log_gaussian(locs, means, input_stddev)
        logll = tf.reduce_sum(logll, 2)  # (num_steps, batch_size)
        logll = tf.transpose(logll)  # (batch_size, num_steps)
        logll_ratio = self._logll_ratio = tf.reduce_mean(logll * advantages)

        loss = self._loss = predict_loss - logll_ratio + baseline_loss
        if self._reg is not None:
            self._reg.setup(self.get_trainable_variables())
            update = self._optimizer.minimize(loss + self._reg.get_loss())
        else:
            update = self._optimizer.minimize(loss)
        self._step_train = ph.Step(
            inputs=(self._input_x, self._input_label),
            outputs=(loss, tf.reduce_mean(rewards)),
            updates=update,
            givens={input_stddev: self._stddev}
        )

    @staticmethod
    def _log_gaussian(x, mean, stddev):
        return -(0.5 * tf.square((x - mean) / stddev) +
                 0.5 * math.log(2. * math.pi) + tf.log(stddev))

    @property
    def predict_loss(self):
        return self._predict_loss

    @property
    def baseline_loss(self):
        return self._baseline_loss

    @property
    def logll_ratio(self):
        return self._logll_ratio

    @property
    def loss(self):
        return self._loss

    @property
    def step_predict(self):
        return self._step_predict

    @property
    def step_train(self):
        return self._step_train


class RAM(ph.Model):

    def __init__(self,
                 name,
                 retina_height,
                 retina_width,
                 num_channels,
                 num_scales,
                 h_input_size,
                 h_loc_size,
                 glimpse_size,
                 state_size,
                 num_classes,
                 num_steps,
                 stddev=0.1,
                 num_mc_samples=10,
                 optimizer=tf.train.RMSPropOptimizer(1e-4, 0.9, 0.9),
                 reg=ph.reg.L1L2Regularizer(1e-5)):
        """Recurrent Model of Visual Attention

        Args:
            name (str): Model name.
            retina_height (int): Retina height.
            retina_width (int): Retina width.
            num_channels (int): Number of channels.
            num_scales (int): NUmber of scales.
            h_input_size (int): Hidden size for input.
            h_loc_size (int): Hidden size for location.
            glimpse_size (int): Glimpse vector size.
            state_size (int): State size of the recurrent network.
            num_classes (int): Number of classes.
            num_steps (int): How many glimpses will look.
            stddev (float): stddev for sampling.
            num_mc_samples (int): Number of Monte Carlo samplings.
            optimizer: Optimizer.
            reg (ph.reg.Regularizer): Regularizer.

        """
        self._retina_height = retina_height
        self._retina_width = retina_width
        self._num_channels = num_channels
        self._num_scales = num_scales
        self._h_input_size = h_input_size
        self._h_loc_size = h_loc_size
        self._glimpse_size = glimpse_size
        self._state_size = state_size
        self._num_classes = num_classes
        self._num_steps = num_steps
        self._stddev = stddev
        self._num_mc_samples = num_mc_samples
        self._optimizer = optimizer
        self._reg = reg
        super(RAM, self).__init__(name)

    def _build(self):
        input_image = self._input_image = tf.placeholder(
            shape=(None, None, None, self._num_channels),
            dtype=ph.dtype,
            name='input_image'
        )
        g_net = self._g_net = GlimpseNetwork(
            'g_net',
            self._retina_height,
            self._retina_width,
            self._num_channels,
            self._num_scales,
            self._h_input_size,
            self._h_loc_size,
            self._glimpse_size
        )
        l_net = self._l_net = LocationNetwork(
            'l_net',
            self._state_size,
            2,  # (x, y)
        )
        ra_net = self._ra_net = RecurrentAttentionNetwork(
            'ra_net',
            input_image,
            g_net,
            l_net,
            self._state_size,
            self._num_classes,
            self._num_steps,
            self._stddev,
            self._num_mc_samples,
            self._optimizer,
            self._reg
        )
        self._step_predict = ra_net.step_predict
        self._step_train = ra_net.step_train

    def predict(self, image):
        return self._step_predict(image)

    def train(self, image, label):
        return self._step_train(image, label)
