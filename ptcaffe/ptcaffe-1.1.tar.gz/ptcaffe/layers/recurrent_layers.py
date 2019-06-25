from __future__ import division, print_function

import copy
from collections import OrderedDict

import torch
import torch.nn as nn

__all__ = ['GRU', 'LSTM']


class GRU(nn.GRU):
    def __init__(self, layer, input_shape):
        gru_param = layer['gru_param']
        self.num_output = int(gru_param['num_output'])
        self.bidirectional = (gru_param.get('bidirectional', 'false') == 'true')
        super(GRU, self).__init__(input_shape[2], self.num_output, bidirectional=self.bidirectional)

        # init weights
        weight_filler = gru_param.get('weight_filler', OrderedDict())
        weight_filler_type = weight_filler.get('type', 'gaussian')
        bias_filler = gru_param.get('bias_filler', OrderedDict())
        bias_filler_type = bias_filler.get('type', 'constant')
        for name, param in self.named_parameters():
            if name.startswith('weight_'):
                if weight_filler_type == 'xavier':
                    torch.nn.init.xavier_uniform_(param.data)
                elif weight_filler_type == 'gaussian':
                    std = float(weight_filler.get('std', 0.02))
                    torch.nn.init.normal_(param.data, 0, std)
                elif weight_filler_type == 'orthogonal':
                    gain = weight_filler.get('gain', 'relu')
                    gain = nn.init.calculate_gain(gain)
                    torch.nn.init.orthogonal(param.data, gain)
            elif name.startswith('bias_'):
                if bias_filler_type == 'constant':
                    value = float(bias_filler.get('value', 0.0))
                    param.data.fill_(value)

        # random init hidden state
        self.random_init_hidden = lstm_param.get("random_init_hidden", "false") == "true"
        self.num_directions = 2 if self.bidirectional else 1

    def __repr__(self):
        if self.bidirectional:
            return 'BGRU(%d)' % self.num_output
        else:
            return 'GRU(%d)' % self.num_output

    def forward_shape(self, input_shape):
        output_shape = copy.copy(input_shape)
        if self.bidirectional:
            output_shape[2] = self.num_output * 2
        else:
            output_shape[2] = self.num_output
        return output_shape

    def init_hidden(self, batch_size=1, device=-1):
        return torch.randn( self.num_layers * self.num_directions, batch_size, self.hidden_size ).to(device)

    def forward(self, x):
        if not self.random_init_hidden:
            x, _ = super(GRU, self).forward(x)
        else:
            bs = x.shape[0] if self.batch_first else x.shape[1]
            hidden  = self.init_hidden( bs, x.device)
            x, _ = super(GRU, self).forward(x, hidden)
        return x


class LSTM(nn.LSTM):
    def __init__(self, layer, input_shape):
        lstm_param = layer['lstm_param']
        self.num_output = int(lstm_param['num_output'])
        self.bidirectional = False
        if 'bidirectional' in lstm_param:
            self.bidirectional = (lstm_param['bidirectional'] == 'true')
        super(LSTM, self).__init__(input_shape[2], self.num_output, bidirectional=self.bidirectional)

        # init weights
        weight_filler = lstm_param.get('weight_filler', OrderedDict())
        weight_filler_type = weight_filler.get('type', 'gaussian')
        bias_filler = lstm_param.get('bias_filler', OrderedDict())
        bias_filler_type = bias_filler.get('type', 'constant')
        for name, param in self.named_parameters():
            if name.startswith('weight_'):
                if weight_filler_type == 'xavier':
                    torch.nn.init.xavier_uniform_(param.data)
                elif weight_filler_type == 'gaussian':
                    std = float(weight_filler.get('std', 0.02))
                    torch.nn.init.normal_(param.data, 0, std)
                elif weight_filler_type == 'orthogonal':
                    gain = weight_filler.get('gain', 'tanh')
                    gain = nn.init.calculate_gain(gain)
                    torch.nn.init.orthogonal(param.data, gain)
            elif name.startswith('bias_'):
                if bias_filler_type == 'constant':
                    value = float(bias_filler.get('value', 0.0))
                    param.data.fill_(value)

        # random init hidden state
        self.random_init_hidden = lstm_param.get("random_init_hidden", "false") == "true"
        self.num_directions = 2 if self.bidirectional else 1

    def __repr__(self):
        if self.bidirectional:
            return 'BLSTM(%d)' % self.num_output
        else:
            return 'LSTM(%d)' % self.num_output

    def forward_shape(self, input_shape):
        output_shape = copy.copy(input_shape)
        if self.bidirectional:
            output_shape[2] = self.num_output * 2
        else:
            output_shape[2] = self.num_output
        return output_shape

    def init_hidden(self, batch_size=1, device=-1):
        return (torch.randn(self.num_layers * self.num_directions, batch_size, self.hidden_size).to(device),
                torch.randn(self.num_layers * self.num_directions, batch_size, self.hidden_size).to(device),)

    def forward(self, x):
        if not self.random_init_hidden:
            x, _ = super(LSTM, self).forward(x)
        else:
            bs = x.shape[0] if self.batch_first else x.shape[1]
            hidden  = self.init_hidden( bs, x.device)
            x, _ = super(LSTM, self).forward(x, hidden)
        return x
