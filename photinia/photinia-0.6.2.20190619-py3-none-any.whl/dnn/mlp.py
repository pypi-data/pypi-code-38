#!/usr/bin/env python3

"""
@author: xi
@since: 2018-07-22
"""

import photinia as ph


class MLP(ph.Widget):

    def __init__(self,
                 name,
                 input_size,
                 output_size,
                 hidden_size,
                 w_init=ph.init.GlorotNormal(),
                 b_init=ph.init.Zeros()):
        self._input_size = input_size
        self._output_size = output_size
        self._hidden_size = hidden_size
        self._w_init = w_init
        self._b_init = b_init
        super(MLP, self).__init__(name)

    def _build(self):
        self._input_layer = ph.Linear(
            'input_layer',
            self._input_size,
            self._hidden_size,
            w_init=self._w_init,
            b_init=self._b_init
        )
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
        y = self._output_layer.setup(h, name=name)
        return y
