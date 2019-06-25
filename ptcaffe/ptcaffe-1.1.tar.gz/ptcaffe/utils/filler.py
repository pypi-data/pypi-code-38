import math
import torch
from torch.nn.init import calculate_gain, _calculate_fan_in_and_fan_out


def xavier_init(tensor, mode='FAN_IN', activation_type='relu'):
    gain = 1.0
    fan_in, fan_out = _calculate_fan_in_and_fan_out(tensor)
    if mode == 'FAN_IN':
        std = gain * math.sqrt(1.0 / fan_in)
    elif mode == 'FAN_OUT':
        std = gain * math.sqrt(1.0 / fan_out)
    elif mode == 'AVERAGE':
        std = gain * math.sqrt(2.0 / (fan_in + fan_out))
    else:
        raise ValueError('Unknown xavier initialize mode {!r}'.format(mode))
    a = math.sqrt(3.0) * std  # Calculate uniform bounds from standard deviation
    with torch.no_grad():
        return tensor.uniform_(-a, a)


def msra_init(tensor, mode='AVERAGE', activation_type='relu'):
    fan_in, fan_out = _calculate_fan_in_and_fan_out(tensor)
    gain = calculate_gain(activation_type)
    if mode == 'FAN_IN':
        std = gain * math.sqrt(1.0 / fan_in)
    elif mode == 'FAN_OUT':
        std = gain * math.sqrt(1.0 / fan_out)
    elif mode == 'AVERAGE':
        std = gain * math.sqrt(2.0 / (fan_in + fan_out))
    else:
        raise ValueError('Unknown msra initialize mode {!r}'.format(mode))
    with torch.no_grad():
        return tensor.normal_(0, std)
