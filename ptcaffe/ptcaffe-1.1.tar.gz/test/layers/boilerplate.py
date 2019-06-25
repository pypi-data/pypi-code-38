# encoding: UTF-8

from collections import OrderedDict
import random
import itertools


def random_name(length=16):
    return ''.join([chr(random.randrange(ord('a'), ord('z') + 1)) for _ in range(length)])


def random_names(n=1, length=16):
    return [random_name(length=length) for _ in range(n)]


def layer(typename, param, tops=1, bottoms=1, param_key=None, **kwargs):
    if param_key is None:
        param_key = typename.lower() + '_param'
    return OrderedDict(name=random_name(),
                       type=typename,
                       top=random_names(tops),
                       bottom=random_names(bottoms),
                       **{param_key: param},
                       **kwargs)


def generate_nd_integral_param(dims, values, single=None, optional=False):
    values = [str(value) for value in values]
    if optional:
        yield OrderedDict()
    for param in itertools.product(values, repeat=len(dims)):
        yield OrderedDict(zip(dims, param))
    if single is not None:
        for param in values:
            yield OrderedDict({single: param})


def generate_nd_cnn_param(single, prefix=None, ndim=2, values=None, optional=False):
    if prefix is None:
        prefix = single
    if values is None:
        values = [1, 2, 3]
    dims = [prefix + suffix for suffix in ['d', 'h', 'w'][-ndim:]]
    return generate_nd_integral_param(dims=dims, values=values, single=single, optional=optional)


def generate_kernel_size(ndim, values=None):
    return generate_nd_cnn_param('kernel_size', 'kernel_', ndim=ndim, values=values)


def generate_pad(ndim, values=None):
    return generate_nd_cnn_param('pad', 'pad_', ndim=ndim, values=values, optional=True)


def generate_stride(ndim, values=None):
    return generate_nd_cnn_param('stride', 'stride_', ndim=ndim, values=values, optional=True)


def generate_pooling_type(*args, **kwargs):
    for pool in ['MAX', 'AVE']:
        yield OrderedDict([('pool', pool)])


def generate_boolean_param(key):
    for value in ['true', 'false']:
        yield OrderedDict([(key, value)])


def generate_pooling_ceil_mode(*args, **kwargs):
    return generate_boolean_param('ceil_mode')


def generate_pooling_global_pooling(*args, **kwargs):
    return generate_boolean_param('global_pooling')

def generate_batchnorm_global_stats(*args, **kwargs):
    return generate_boolean_param('use_global_stats')

def generate_batchnorm_affine(*args, **kwargs):
    return generate_boolean_param('affine')

def generate_batchnorm_using_moving_average(*args, **kwargs):
    return generate_boolean_param('using_moving_average')

def generate_batchnorm_last_gamma(*args, **kwargs):
    return generate_boolean_param('using_last_gamma')

def generate_batchnorm_momentum(*args, **kwargs):
    yield OrderedDict(moving_average_fraction=random.random())

def generate_batchnorm_eps(*args, **kwargs):
    yield OrderedDict(eps=random.random())

def generate_batchnorm_filler_type(key):
    if key == 'gaussian':
        return OrderedDict(type=key,mean=random.random(),std=random.random())
    elif key == 'constant':
        return OrderedDict(type=key,value=random.random())
    elif key == 'scale':
        return OrderedDict(value=random.random())

def generate_batchnorm_weight_filler(*args, **kwargs):
    for value in ['gaussian', 'constant']:
        yield OrderedDict(weight_filler=generate_batchnorm_filler_type(value))

def generate_batchnorm_bias_filler(*args, **kwargs):
    yield OrderedDict(bias_filler=generate_batchnorm_filler_type('constant'))

def generate_dilation(ndim=None, values=None):
    if values is None:
        values = [1, 2]
    for value in values:
        yield OrderedDict(dilation=value)


def generate_bias(ndim=None, values=None):
    yield OrderedDict(bias_term='true')
    yield OrderedDict(bias_term='false')


def generate_num_output(ndim, values):
    if values is None:
        values = [64, 128]
    for value in values:
        yield OrderedDict(num_output=value)


def generate_param(*meta_generators, ndim=2, values=None):
    generators = [meta_generator(ndim=ndim, values=values) for meta_generator in meta_generators]
    for params in itertools.product(*generators):
        merged = OrderedDict()
        for param in params:
            merged.update(param)
        yield merged


def generate_group(ndim, values):
    for value in values:
        yield OrderedDict(group=str(value))


def rename(param, pairs):
    renamed = OrderedDict(param)
    for key in param:
        if key in pairs:
            renamed[pairs[key]] = renamed[key]
            del renamed[key]
    return renamed


def dropout(p, iterable):
    for obj in iterable:
        if random.random() < p:
            yield obj


CONVOLUTION_GENERATORS = [generate_kernel_size, generate_stride, generate_pad,
                          generate_dilation, generate_bias, generate_num_output]

LINEAR_GENERATORS = [generate_bias, generate_num_output]

POOLING_GENERATORS = [generate_kernel_size, generate_stride, generate_pad,
                      generate_pooling_type, generate_pooling_ceil_mode, generate_pooling_global_pooling]

BATCHNORM_GENERATORS = [generate_batchnorm_global_stats, generate_batchnorm_affine, generate_batchnorm_momentum,
                       generate_batchnorm_eps, generate_batchnorm_weight_filler, generate_batchnorm_bias_filler]
