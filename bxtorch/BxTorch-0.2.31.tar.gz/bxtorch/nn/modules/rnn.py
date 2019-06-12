#
#  nn/modules/rnn.py
#  bxtorch
#
#  Created by Oliver Borchert on May 19, 2019.
#  Copyright (c) 2019 Oliver Borchert. All rights reserved.
#

import torch
import torch.nn as nn

class StackedLSTM(nn.Module):
    """
    The stacked LSTM is an extension to PyTorch's native LSTM allowing stacked
    LSTMs with different hidden dimensions being stacked.
    """

    # MARK: Initialization
    def __init__(self, input_size, hidden_sizes, bias=True, batch_first=False):
        """
        Initializes a new stacked LSTM according to the given parameters.

        Parameters:
        -----------
        - input_size: int
            The dimension of the sequence's elements.
        - hidden_sizes: list of int
            The dimensions of the stacked LSTM's layers.
        - bias: bool, default: True
            Whether to use biases in the LSTM.
        - batch_first: bool, default: False
            Whether the batch or the sequence can be found in the first
            dimension.
        """
        super().__init__()
        self.batch_first = batch_first

        lstms = []
        dims = zip([input_size] + hidden_sizes, hidden_sizes)
        for i, (in_dim, out_dim) in enumerate(dims):
            lstms.append(nn.LSTMCell(in_dim, out_dim, bias=bias))
        self.lstms = nn.ModuleList(lstms)

    # MARK: Instance Methods
    def forward(self, inputs, initial_states=None, return_sequence=True):
        """
        Computes the forward pass through the stacked LSTM.

        Parameters:
        -----------
        - inputs: torch.FloatTensor [S, B, N]
            The inputs fed to the LSTM one after the other. Sequence length S,
            batch size B, and input size N. If ``batch_first`` is set to True,
            the first and second dimension should be swapped.
        - initial_states: list of tuple of 
                (torch.FloatTensor [H_i], torch.FloatTensor [H_i]),
                default: None
            The initial states for all LSTM layers. The length of the list must
            match the number of layers in the LSTM, the sizes of the states must
            match the hidden sizes of the LSTM layers. If None is given, the
            initial states are defaulted to all zeros.
        - return_sequence: bool, default: True
            Whether to return all outputs from the last LSTM layer or only the
            last one.

        Returns:
        --------
        - torch.FloatTensor [S, B, K] or torch.FloatTensor [B, K]
            Depending on whether sequences are returned, either all outputs
            or only the output from the last cell are returned. If the stacked
            LSTM was initialized with ``batch_first``, the first and second
            dimension are swapped when sequences are returned.
        """
        if self.batch_first:
            inputs = inputs.transpose(1, 0)

        sequence_length, batch_size = inputs.size()[0:2]
        states = initial_states or [None] * len(self.lstms)

        outputs = []
        for n, input_val in enumerate(inputs):
            output = None

            for i, lstm in enumerate(self.lstms):
                val = input_val if i == 0 else output
                output, cell = lstm(val, states[i])
                states[i] = (output, cell)

            if return_sequence or n == sequence_length - 1:
                outputs.append(output)

        if return_sequence:
            result = torch.stack(outputs)
            if self.batch_first:
                result = result.transpose(1, 0)
            return result
        else:
            return outputs[0]
