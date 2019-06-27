'''flip_data function definition'''

import numpy


def flip_data(interp_x, is3d, o_dims, data_t):

    '''flip 2D or 3D data'''

    if interp_x:
        if is3d:
            for axi in range(o_dims[0]):
                data_t[axi] = numpy.fliplr(data_t[axi])
        else:
            data_t = numpy.fliplr(data_t)
    else:
        if is3d:
            for axi in range(o_dims[0]):
                data_t[axi] = numpy.flipud(data_t[axi])
        else:
            data_t = numpy.flipud(data_t)

    return data_t
