# encoding: UTF-8


def paired(param, dtype, single, *pairs):
    ndim = len(pairs)
    if single in param and not any([p in param for p in pairs]):
        return tuple([dtype(param, single)] * ndim)
    try:
        return tuple([dtype(param, p) for p in pairs])
    except KeyError:
        return None


def kernel_size(param, ndim=2):
    pairs = ['kernel_' + p for p in 'dhw'[-ndim:]]
    return paired(param, integral, 'kernel_size', *pairs)


def pad(param, ndim=2):
    if ndim == 2 or 'pad' not in param:
        pairs = ['pad_' + p for p in 'dhw'[-ndim:]]
        return paired(param, integral, 'pad', *pairs)
    pad = integral(param, 'pad')
    return 0, pad, pad


def stride(param, ndim=2):
    pairs = ['stride_' + p for p in 'dhw'[-ndim:]]
    return paired(param, integral, 'stride', *pairs)


def boolean(param, key):
    return param[key] == 'true'


def integral(param, key, default=None):
    if default is not None:
        return int(param.get(key, default))
    return int(param[key])


def bias(param):
    return boolean(param, 'bias_term')


def dilation(param):
    return integral(param, 'dilation')


def num_output(param):
    return integral(param, 'num_output')


def group(param, default=1):
    return integral(param, 'group', default=default)


