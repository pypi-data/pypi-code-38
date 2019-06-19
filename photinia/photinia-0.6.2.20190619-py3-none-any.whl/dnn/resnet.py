#!/usr/bin/env python3

"""
@author: xi
@since: 2018-08-31
"""

import photinia as ph


class ResNet(ph.Widget):

    def __init__(self,
                 name,
                 input_size,
                 output_size,
                 hidden_size,
                 num_layers=1,
                 w_init=ph.init.GlorotNormal(),
                 b_init=ph.init.Zeros()):
        self._input_size = input_size
        self._output_size = output_size
        self._hidden_size = hidden_size
        self._num_layers = num_layers
        self._w_init = w_init
        self._b_init = b_init
        super(ResNet, self).__init__(name)

    def _build(self):
        self._input_layer = ph.Linear(
            'input_layer',
            self._input_size,
            self._hidden_size,
            w_init=self._w_init,
            b_init=self._b_init
        )

        res_layers = self._res_layers = list()
        for i in range(self._num_layers):
            res_layer = ph.ResidualLayer(
                f'res_{str(i)}',
                self._hidden_size,
                w_init=self._w_init,
                b_init=self._b_init
            )
            res_layers.append(res_layer)

        self._output_layer = ph.Linear(
            'output_layer',
            self._hidden_size,
            self._output_size,
            w_init=self._w_init,
            b_init=self._b_init
        )

    def _setup(self, input_x, activation=ph.ops.lrelu, name='out'):
        h = self._input_layer.setup(input_x)
        if activation:
            h = activation(h)

        for layer in self._res_layers:
            h = layer.setup(h, activation=activation)
            if activation:
                h = activation(h)

        y = self._output_layer.setup(h, name=name)
        return y
