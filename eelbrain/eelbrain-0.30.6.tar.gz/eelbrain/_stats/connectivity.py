# Author: Christian Brodbeck <christianbrodbeck@nyu.edu>
import numpy as np
from numpy import newaxis
from scipy.ndimage import generate_binary_structure

from .._data_obj import Dimension


class Connectivity:
    """N-dimensional connectivity"""
    __slots__ = ('struct', 'custom', 'vector')

    def __init__(self, dims, parc=None):
        types = [dim._connectivity_type for dim in dims]
        invalid = set(types).difference(Dimension._CONNECTIVITY_TYPES)
        if invalid:
            raise RuntimeError(f"Invalid connectivity type: {', '.join(invalid)}")

        # vector: will be collapsed by test function
        n_vector = types.count('vector')
        if n_vector > 1:
            raise NotImplementedError("More than one axis with vector connectivity")
        elif n_vector:
            self.vector = types.index('vector')
            types = types[:self.vector] + type[self.vector + 1:]
        else:
            self.vector = None

        # custom connectivity
        self.custom = {}
        n_custom = types.count('custom')
        if n_custom > 1:
            raise NotImplementedError("More than one axis with custom connectivity")
        elif n_custom:
            axis = types.index('custom')
            if axis > 0:
                raise NotImplementedError(
                    "Custom connectivity on axis other than first")
            custom_dim = dims[axis]
            if custom_dim.name == parc:
                edges = custom_dim.connectivity(disconnect_parc=True)
            else:
                edges = custom_dim.connectivity()
            dim_length = len(custom_dim)
            src = edges[:, 0]
            n_edges = np.bincount(src, minlength=dim_length)
            edge_stop = np.cumsum(n_edges)
            edge_start = edge_stop - n_edges
            self.custom[axis] = (edges, edge_start, edge_stop)

        # prepare struct for grid connectivity
        self.struct = generate_binary_structure(len(dims), 1)
        for i, ctype in enumerate(types):
            if ctype != 'grid':
                self.struct[(slice(None),) * i + (slice(None, None, 2),)] = False

    def __getstate__(self):
        return {k: getattr(self, k) for k in self.__slots__}

    def __setstate__(self, state):
        for k, v in state.items():
            setattr(self, k, v)


def find_peaks(x, connectivity, out=None):
    """Find peaks (local maxima, including plateaus) in x

    Returns
    -------
    out : array (x.shape, bool)
        Boolean array which is True only on local maxima.
    """
    if out is None:
        out = np.empty(x.shape, np.bool8)
    elif out.dtype.kind != 'b':
        raise TypeError("out needs to be array of boolean type, got type %s" %
                        out.dtype)
    elif out.shape != x.shape:
        raise ValueError("out needs to have same shape as x, got x.shape = %s"
                         "but out.shape = %s" % (x.shape, out.shape))
    out.fill(True)

    # move through each axis in both directions and discard descending
    # slope. Do most computationally intensive axis last.
    for ax in range(x.ndim - 1, -1, -1):
        if ax in connectivity.custom:
            shape = (len(x), -1)
            xsa = x.reshape(shape)
            outsa = out.reshape(shape)
            axlen = xsa.shape[1]

            conn_src, conn_dst = connectivity.custom[ax][0].T
            for i in range(axlen):
                data = xsa[:, i]
                outslice = outsa[:, i]
                if not np.any(outslice):
                    continue

                # find all points under a slope
                sign = np.sign(data[conn_src] - data[conn_dst])
                no = set(conn_src[sign < 0])
                no.update(conn_dst[sign > 0])

                # expand to equal points
                border = no
                while border:
                    # forward
                    idx = np.in1d(conn_src, border)
                    conn_dst_sub = conn_dst[idx]
                    eq = np.equal(data[conn_src[idx]], data[conn_dst_sub])
                    new = set(conn_dst_sub[eq])
                    # backward
                    idx = np.in1d(conn_dst, border)
                    conn_src_sub = conn_src[idx]
                    eq = np.equal(data[conn_src_sub], data[conn_dst[idx]])
                    new.update(conn_src_sub[eq])

                    # update
                    new.difference_update(no)
                    no.update(new)
                    border = new

                # mark vertices or whole isoline
                if no:
                    outslice[list(no)] = False
                elif not np.all(outslice):
                    outslice.fill(False)
        else:
            if x.ndim == 1:
                xsa = x[:, newaxis]
                outsa = out[:, newaxis]
            else:
                xsa = x.swapaxes(0, ax)
                outsa = out.swapaxes(0, ax)
            axlen = len(xsa)

            kernel = np.empty(xsa.shape[1:], dtype=np.bool8)

            diff = np.diff(xsa, 1, 0)

            # forward
            kernel.fill(True)
            for i in range(axlen - 1):
                kernel &= outsa[i]
                kernel[diff[i] > 0] = True
                kernel[diff[i] < 0] = False
                outsa[i + 1] *= kernel

            # backward
            kernel.fill(True)
            for i in range(axlen - 2, -1, -1):
                kernel &= outsa[i + 1]
                kernel[diff[i] < 0] = True
                kernel[diff[i] > 0] = False
                outsa[i] *= kernel

    return out
