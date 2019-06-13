#
#  nn/modules/lstm.py
#  bxtorch
#
#  Created by Oliver Borchert on June 13, 2019.
#  Copyright (c) 2019 Oliver Borchert. All rights reserved.
#

import numpy as np
import torch
import torch.jit as jit
import torch.nn as nn
from typing import List, Tuple, Optional

class StackedLSTM(jit.ScriptModule):
    """
    The stacked LSTM is an extension to PyTorch's native LSTM allowing stacked
    LSTMs with different hidden dimensions being stacked.
    """

    __constants__ = ['batch_first', 'num_stacked', 'lstms']

    # MARK: Initialization
    def __init__(self, input_size, hidden_sizes, bias=True, batch_first=False,
                 cudnn=True):
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
        - cudnn: bool, default: True
            Whether to use PyTorch's LSTM implementation which uses cuDNN on
            Nvidia GPUs. You usually don't want to change the default value,
            however, PyTorch's default implementation does not allow higher-
            order gradients of the LSTMCell as of version 1.1.0. When this
            value is set to False, we therefore use a (slower) implementation
            of a LSTM cell which allows higher-order gradients.
        """
        super().__init__()

        self.batch_first = batch_first
        self.num_stacked = len(hidden_sizes)

        cell_class = nn.LSTMCell if cudnn else _LSTMCell

        lstms = []
        dims = zip([input_size] + hidden_sizes, hidden_sizes)
        for i, (in_dim, out_dim) in enumerate(dims):
            lstms.append(cell_class(in_dim, out_dim, bias=bias))
        self.lstms = nn.ModuleList(lstms)

    # MARK: Instance Methods
    @jit.script_method
    def forward(self, 
                inputs: torch.Tensor,
                initial_states: Optional[
                    List[Tuple[torch.Tensor, torch.Tensor]]] = None, 
                return_sequence: bool = True):
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
        # code is kind of weird and complicated due to JIT script
        # for your own good, don't try to optimize until after PyTorch 1.1.0

        if self.batch_first:
            inputs = inputs.transpose(1, 0)

        sequence_length, batch_size = inputs.size()[0:2]

        # Initialize the state to empty vectors is needed for jit to properly
        # compile the function
        if initial_states is None:
            states = [(torch.empty(0), torch.empty(0))]
        else:
            states = initial_states

        # Here, we go into the stacked LSTM one by one, storing intermediate 
        # outputs. Unfortunately, we cannot do the loop the other way around
        # as a bug in Torch Script prevents using ModuleList inside a nested
        # loop...
        outputs = []
        i = 0
        for lstm in self.lstms:
            for n in range(inputs.size(0)):
                val = inputs[n] if i == 0 else outputs[n]
                output, cell = lstm(
                    val, None if states[i][0].size(0) == 0 else states[i]
                )
                states[i] = (output, cell)
                if i == 0:
                    outputs.append(output)
                else:
                    outputs[n] = output
            i += 1

        if return_sequence:
            result = torch.stack(outputs)
            if self.batch_first: # set batch first, sequence length second
                result = result.transpose(1, 0)
            return result
        else:
            return outputs[-1]


class _LSTMCell(jit.ScriptModule):
    """
    LSTMCell which does not have cuDNN support but allows for higher-order
    gradients.
    Consult PyTorch's LSTMCell for documentation on the class's initialization
    parameter and how to call it.
    """

    __constants__ = ['hidden_size', 'has_bias']

    # MARK: Initialization
    def __init__(self, input_size, hidden_size, bias=True):
        super().__init__()

        self.hidden_size = hidden_size

        self.input_weight = nn.Parameter(
            torch.FloatTensor(input_size, 4 * hidden_size)
        )
        self.hidden_weight = nn.Parameter(
            torch.FloatTensor(hidden_size, 4 * hidden_size)
        )

        if bias:
            self.bias = nn.Parameter(torch.FloatTensor(4 * hidden_size))
            self.has_bias = True
        else:
            self.has_bias = False

        self.reset_parameters()

    # MARK: Instance Methods
    def reset_parameters(self):
        sqrt_hidden = np.sqrt(1 / self.hidden_size)
        init_from = (-sqrt_hidden, sqrt_hidden)
        for p in self.parameters():
            nn.init.uniform_(p, *init_from)

    @jit.script_method
    def forward(self, 
                x_in: torch.Tensor,
                state: Optional[Tuple[torch.Tensor, torch.Tensor]] = None):

        if state is None:
            size = (x_in.size(0), self.hidden_size)
            hidden_state = torch.zeros(
                *size, dtype=torch.float, device=x_in.device
            )
            cell_state = torch.zeros(
                *size, dtype=torch.float, device=x_in.device
            )
        else:
            hidden_state, cell_state = state

        # 1) Perform matrix multiplications for input and last hidden state
        if self.has_bias:
            x = torch.addmm(self.bias, x_in, self.input_weight)
            h = torch.addmm(self.bias, hidden_state, self.hidden_weight)
        else:
            x = x_in.matmul(self.input_weight)
            h = hidden_state.matmul(self.hidden_weight)

        forget_gate_x, input_gate_x_1, input_gate_x_2, output_gate_x = \
            x.split(self.hidden_size, dim=1)
        forget_gate_h, input_gate_h_1, input_gate_h_2, output_gate_h = \
            h.split(self.hidden_size, dim=1)

        # 2) Forget gate
        forget_gate = torch.sigmoid(forget_gate_x + forget_gate_h)

        # 3) Input gate
        input_gate_1 = torch.sigmoid(input_gate_x_1 + input_gate_h_1)
        input_gate_2 = torch.tanh(input_gate_x_2 + input_gate_h_2)
        input_gate = forget_gate * cell_state + input_gate_1 * input_gate_2

        # 4) Output gate
        output_gate_1 = torch.sigmoid(output_gate_x + output_gate_h)
        output_gate = output_gate_1 * torch.tanh(input_gate)

        return output_gate, input_gate
