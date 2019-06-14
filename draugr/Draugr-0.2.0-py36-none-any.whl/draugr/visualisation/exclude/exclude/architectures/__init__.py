import torch
import torch.nn as nn


# A temporary solution from the master branch.
# https://github.com/pytorch/pytorch/blob/7752fe5d4e50052b3b0bbc9109e599f8157febc0/torch/nn/init.py#L312
# Remove after the next version of PyTorch gets release.
def orthogonal(tensor, gain=1):
  if tensor.ndimension() < 2:
    raise ValueError("Only tensors with 2 or more dimensions are supported")

  rows = tensor.size(0)
  cols = tensor[0].numel()
  flattened = torch.Tensor(rows, cols).normal_(0, 1)

  if rows < cols:
    flattened.t_()

  # Compute the qr factorization
  q, r = torch.qr(flattened)
  # Make Q uniform according to https://arxiv.org/pdf/math-ph/0609050.pdf
  d = torch.diag(r, 0)
  ph = d.sign()
  q *= ph.expand_as(q)

  if rows < cols:
    q.t_()

  tensor.view_as(q).copy_(q)
  tensor.mul_(gain)
  return tensor


def _maybe_infer_hidden_layers(self,
                               input_multiplier=8,
                               output_multiplier=6):
  if self._hidden_layers is None or self._hidden_layers == -1:
    if self._input_shape and self._output_shape:

      h_1_size = int(self._input_shape[0] * input_multiplier)
      h_3_size = int(self._output_shape[0] * output_multiplier)

      h_2_size = int(numpy.sqrt(h_1_size * h_3_size))
      self._hidden_layers = NamedOrderedDictionary([h_1_size,
                                                    h_2_size,
                                                    h_3_size
                                                    ]).as_list()
    else:
      logging.info('No input or output size')
