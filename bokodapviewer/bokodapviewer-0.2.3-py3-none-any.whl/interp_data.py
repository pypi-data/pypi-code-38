'''interp_data function definition'''

import numpy
from .flip_data import flip_data


def interp_data(x_t, y_t, data_t, nu_tol=0,
                stat_box=None, interp_int_box=None):

    '''Uniform interpolation (if needed) for display'''

    # Check if interpolation needed

    interp_x = interp_y = False
    dx_t = numpy.abs(numpy.diff(x_t))
    if 100*(dx_t.max() - dx_t.min())/dx_t.mean() > nu_tol:
        interp_x = True
    dy_t = numpy.abs(numpy.diff(y_t))
    if 100*(dy_t.max() - dy_t.min())/dy_t.mean() > nu_tol:
        interp_y = True

    if not (interp_x or interp_y):  # Nothing to do
        return x_t, y_t, data_t

    if interp_x and interp_y:  # Can't do both
        if stat_box is not None:
            stat_box.text = '<font color="red">Error: more than one plot axis\
            non-uniform, please choose a different plot option</font>'
        return x_t, y_t, None

    if stat_box is not None:
        stat_box.text = '<font color="blue">Interpolating...</font>'

    if len(data_t.shape) == 3:
        is3d = True
    else:
        is3d = False

    o_dims = data_t.shape

    # Find the transpose order

    if is3d:
        if interp_x:
            t_ord = [0, 1, 2]
        elif interp_y:
            t_ord = [0, 2, 1]
    else:
        if interp_x:
            t_ord = [0, 1]
        elif interp_y:
            t_ord = [1, 0]

    # Get the interpolant

    if interp_x:
        ax_v = x_t.copy()
    else:
        ax_v = y_t.copy()

    ax_flipped = False
    if numpy.abs(ax_v[1]) < numpy.abs(ax_v[0]):
        ax_flipped = True
        ax_v = numpy.flipud(ax_v)  # Must be increasing for interpolation
        data_t = flip_data(interp_x, is3d, o_dims, data_t)

    interp_auto = False
    if interp_int_box is not None:
        try:  # Get interpolation interval if specified
            ax_int = float(interp_int_box.value)
            if stat_box is not None:
                stat_box.text = '<font color="blue">Interpolating using \
                specified interval...</font>'
        except ValueError:
            interp_auto = True
    else:
        interp_auto = True
    if interp_auto:
        ax_int = numpy.min(numpy.abs(numpy.diff(ax_v)))
        if stat_box is not None:
            stat_box.text = '<font color="blue">No interval specified: interpolating \
            using minimum available interval...</font>'

    if ax_v[0] < 0:
        ax_neg = True
        ax_v = -ax_v
    else:
        ax_neg = False

    n_pts = int(numpy.round((ax_v[-1] - ax_v[0])/ax_int)) + 1
    ax_v_i = numpy.linspace(ax_v[0], ax_v[-1], n_pts)
    ax_int = ax_v_i[1] - ax_v_i[0]
    if interp_int_box is not None:
        interp_int_box.value = str(ax_int)

    # Transpose and flatten for 1d interpolation

    data_v = numpy.transpose(data_t, t_ord).flatten()

    # Interpolate

    nreps = int(data_t.size/ax_v.size)
    olen = ax_v.size
    ilen = ax_v_i.size
    data_t = numpy.zeros(ilen*nreps)
    for rep in range(nreps):
        ostart = rep*olen
        istart = rep*ilen
        data_t[istart:istart+ilen] = numpy.interp(ax_v_i, ax_v,
                                                  data_v[ostart:ostart+olen])

    # Reshape and re-transpose

    if is3d:
        if interp_x:
            i_dims = [o_dims[0], o_dims[1], n_pts]
        else:
            i_dims = [o_dims[0], n_pts, o_dims[2]]
    else:
        if interp_x:
            i_dims = [o_dims[0], n_pts]
        else:
            i_dims = [n_pts, o_dims[1]]

    i_dims_t = [i_dims[t] for t in t_ord]

    # Reshape to transposed array

    data_t = numpy.reshape(data_t, i_dims_t)

    # Transpose back

    data_t = numpy.transpose(data_t, t_ord)

    # Flip the data if needed

    if ax_flipped:
        ax_v_i = numpy.flipud(ax_v_i)
        data_t = flip_data(interp_x, is3d, o_dims, data_t)

    # Change sign if needed

    if ax_neg:
        ax_v_i = -ax_v_i

    # Set the axis array and return

    if interp_x:
        x_t = ax_v_i
    else:
        y_t = ax_v_i

    return x_t, y_t, data_t
