from collections import Iterator
from functools import reduce
from math import floor
from operator import mul

import numpy as np
from scipy.linalg import norm

from .. import _info
from .._data_obj import NDVar, Case, UTS, dataobj_repr, ascategorial, asndvar
from .._utils.numpy_utils import newaxis


class RevCorrData:
    """Restructure input NDVars into arrays for reverse correlation
    
    Attributes
    ----------
    y : NDVar
        Dependent variable.
    x : NDVar | sequence of NDVar
        Predictors.
    segments : np.ndarray
        ``(n_segments, 2)`` array of segment ``[start, stop]`` indices.
    cv_segments : Sequence
        Sequence of ``(all_segments, train, test)`` tuples, where each is a
        2d-array of ``[start, stop]`` indices.
    cv_indexes : Sequence
        Only available for segmented data. For each partition, the index into
        :attr:`.segments` used as test set.
    """
    def __init__(self, y, x, error, scale_data, ds=None):
        y = asndvar(y, ds=ds)
        if isinstance(x, (tuple, list, Iterator)):
            x = (asndvar(x_, ds=ds) for x_ in x)
        else:
            x = asndvar(x, ds=ds)

        # scale_data param
        if isinstance(scale_data, bool):
            scale_in_place = False
        elif isinstance(scale_data, str):
            if scale_data == 'inplace':
                scale_in_place = True
            else:
                raise ValueError("scale_data=%r" % (scale_data,))
        else:
            raise TypeError("scale_data=%r, need bool or str" % (scale_data,))

        # check y and x
        if isinstance(x, NDVar):
            x_name = x.name
            x = (x,)
            multiple_x = False
        else:
            x = tuple(x)
            assert all(isinstance(x_, NDVar) for x_ in x)
            x_name = tuple(x_.name for x_ in x)
            multiple_x = True
        time_dim = y.get_dim('time')
        if any(x_.get_dim('time') != time_dim for x_ in x):
            raise ValueError("Not all NDVars have the same time dimension")
        n_times = len(time_dim)

        # determine cases (used as segments)
        n_cases = segments = None
        for x_ in x:
            # determine cases
            if n_cases is None:
                if x_.has_case:
                    n_cases = len(x_)
                    # check y
                    if not y.has_case:
                        raise ValueError(f'y={y!r}: x has case dimension but y does not')
                    elif len(y) != n_cases:
                        raise ValueError(f'y={y!r}: different number of cases from x {n_cases}')
                    # prepare segment index
                    seg_i = np.arange(0, n_cases * n_times + 1, n_times, np.int64)[:, newaxis]
                    segments = np.hstack((seg_i[:-1], seg_i[1:]))
                else:
                    n_cases = 0
            elif n_cases:
                if len(x_) != n_cases:
                    raise ValueError(f'x={x}: not all components have same number of cases')
            else:
                assert not x_.has_case, 'some but not all x have case'
        case_to_segments = n_cases > 0

        # vector dimension
        vector_dims = [dim.name for dim in y.dims if dim._connectivity_type == 'vector']
        if not vector_dims:
            vector_dim = None
        elif len(vector_dims) == 1:
            vector_dim = vector_dims.pop()
        else:
            raise NotImplementedError(f"y={y!r}: more than one vector dimension ({', '.join(vector_dims)})")

        # y_data: flatten to ydim x time array
        last = ('time',)
        n_ydims = -1
        if case_to_segments:
            last = ('case',) + last
            n_ydims -= 1
        if vector_dim:
            last = (vector_dim,) + last
        y_dimnames = y.get_dimnames(last=last)
        ydims = y.get_dims(y_dimnames[:n_ydims])
        n_times_flat = n_cases * n_times if case_to_segments else n_times
        n_flat = reduce(mul, map(len, ydims), 1)
        shape = (n_flat, n_times_flat)
        y_data = y.get_data(y_dimnames).reshape(shape)
        # shape for exposing vector dimension
        if vector_dim:
            if not scale_data:
                raise NotImplementedError("Vector data without scaling")
            n_flat_prevector = reduce(mul, map(len, ydims[:-1]), 1)
            n_vector = len(ydims[-1])
            assert n_vector > 1
            vector_shape = (n_flat_prevector, n_vector, n_times_flat)
        else:
            vector_shape = None

        # x_data:  predictor x time array
        x_data = []
        x_meta = []
        x_names = []
        n_x = 0
        for x_ in x:
            ndim = x_.ndim - bool(n_cases)
            if ndim == 1:
                xdim = None
                dimnames = ('case' if n_cases else newaxis, 'time')
                data = x_.get_data(dimnames)
                index = n_x
                x_names.append(dataobj_repr(x_))
            elif ndim == 2:
                dimnames = x_.get_dimnames(last='time')
                xdim = x_.get_dim(dimnames[-2])
                if n_cases:
                    dimnames = (xdim.name, 'case', 'time')
                data = x_.get_data(dimnames)
                index = slice(n_x, n_x + len(data))
                x_repr = dataobj_repr(x_)
                for v in xdim:
                    x_names.append("%s-%s" % (x_repr, v))
            else:
                raise NotImplementedError("x with more than 2 dimensions")
            if n_cases:
                data = data.reshape((-1, n_cases * n_times))
            x_data.append(data)
            x_meta.append((x_.name, xdim, index))
            n_x += len(data)

        if len(x_data) == 1:
            x_data = x_data[0]
            x_is_copy = False
        else:
            x_data = np.concatenate(x_data)
            x_is_copy = True

        if scale_data:
            if not scale_in_place:
                y_data = y_data.copy()
                if not x_is_copy:
                    x_data = x_data.copy()
                    x_is_copy = True

            y_mean = y_data.mean(1)
            x_mean = x_data.mean(1)
            y_data -= y_mean[:, newaxis]
            x_data -= x_mean[:, newaxis]
            # for vector data, scale by vector norm
            if vector_shape:
                y_data_vector_shape = y_data.reshape(vector_shape)
                y_data_scale = norm(y_data_vector_shape, axis=1)
            else:
                y_data_vector_shape = None
                y_data_scale = y_data

            if error == 'l1':
                y_scale = np.abs(y_data_scale).mean(-1)
                x_scale = np.abs(x_data).mean(-1)
            elif error == 'l2':
                y_scale = (y_data_scale ** 2).mean(-1) ** 0.5
                x_scale = (x_data ** 2).mean(-1) ** 0.5
            else:
                raise RuntimeError(f"error={error!r}")

            if vector_shape:
                y_data_vector_shape /= y_scale[:, newaxis, newaxis]
            else:
                y_data /= y_scale[:, newaxis]
            x_data /= x_scale[:, newaxis]
            # for data-check
            y_check = y_scale
            x_check = x_scale
            # zero-padding for convolution
            x_pads = -x_mean / x_scale
        else:
            y_mean = x_mean = y_scale = x_scale = None
            y_check = y_data.var(1)
            x_check = x_data.var(1)
            x_pads = np.zeros(n_x)
        # check for flat data
        zero_var = [y.name or 'y'] if np.any(y_check == 0) else []
        zero_var.extend(x_name[i] for i, v in enumerate(x_check) if v == 0)
        if zero_var:
            raise ValueError("Flat data: " + ', '.join(zero_var))
        # check for NaN
        has_nan = [y.name] if np.isnan(y_check.sum()) else []
        has_nan.extend(x_name[i] for i, v in enumerate(x_check) if np.isnan(v))
        if has_nan:
            raise ValueError("Data with NaN: " + ', '.join(has_nan))

        self.error = error
        self.time = time_dim
        self.segments = segments
        self.cv_segments = self.cv_indexes = self.partitions = self.model = None
        self._scale_data = bool(scale_data)
        self.shortest_segment_n_times = n_times
        # y
        self.y = y_data
        self.y_mean = y_mean
        self.y_scale = y_scale
        self.y_name = y.name
        self.y_info = _info.copy(y.info)
        self.ydims = ydims
        self.yshape = tuple(map(len, ydims))
        self.full_y_dims = y.get_dims(y_dimnames)
        self.vector_dim = vector_dim  # vector dimension name
        self.vector_shape = vector_shape  # flat shape with vector dim separate
        # x
        self.x = x_data
        self.x_mean = x_mean
        self.x_scale = x_scale
        self.x_name = x_name
        self._x_meta = x_meta
        self._multiple_x = multiple_x
        self._x_is_copy = x_is_copy
        self.x_pads = x_pads

    def initialize_cross_validation(self, partitions=None, model=None, ds=None):
        if partitions is not None and partitions <= 1:
            raise ValueError(f"partitions={partitions}")
        cv_segments = []  # list of (segments, train, test)
        n_times = len(self.time)
        if self.segments is None:
            if model is not None:
                raise TypeError(f'model={dataobj_repr(model)!r}: model cannot be specified in unsegmented data')
            if partitions is None:
                partitions = 10
            seg_n_times = int(floor(n_times / partitions))
            # first
            for i in range(partitions):
                test = ((seg_n_times * i, seg_n_times * (i + 1)),)
                if i == 0:  # first
                    train = ((seg_n_times, n_times),)
                elif i == partitions - 1:  # last
                    train = ((0, n_times - seg_n_times),)
                else:
                    train = ((0, seg_n_times * i),
                             (seg_n_times * (i + 1), n_times))
                cv_segments.append((np.vstack((train, test)), train, test))
            cv_segments = (tuple(np.array(s, np.int64) for s in cv) for cv in cv_segments)
        else:
            n_total = len(self.segments)
            if model is None:
                cell_indexes = [np.arange(n_total)]
            else:
                model = ascategorial(model, ds=ds, n=n_total)
                cell_indexes = [np.flatnonzero(model == cell) for cell in model.cells]
            cell_sizes = [len(i) for i in cell_indexes]
            cell_size = min(cell_sizes)
            cell_sizes_are_equal = len(set(cell_sizes)) == 1
            if partitions is None:
                if cell_sizes_are_equal:
                    if 3 <= cell_size <= 10:
                        partitions = cell_size
                    else:
                        raise NotImplementedError(f"Automatic partition for {cell_size} cases")
                else:
                    raise NotImplementedError(f'Automatic partition for variable cell size {tuple(cell_sizes)}')

            if partitions > cell_size:
                if not cell_sizes_are_equal:
                    raise ValueError(f'partitions={partitions}: > smallest cell size ({cell_size}) with unequal cell sizes')
                elif partitions % cell_size:
                    raise ValueError(f'partitions={partitions}: not a multiple of cell_size ({cell_size})')
                elif len(cell_sizes) > 1:
                    raise NotImplementedError(f'partitions={partitions} with more than one cell')
                n_parts = partitions // cell_size
                segments = []
                for start, stop in self.segments:
                    d = (stop - start) / n_parts
                    starts = [int(round(start + i * d)) for i in range(n_parts)]
                    starts.append(stop)
                    for i in range(n_parts):
                        segments.append((starts[i], starts[i+1]))
                segments = np.array(segments, np.int64)
                index_range = np.arange(partitions)
                indexes = [index_range == i for i in range(partitions)]
            else:
                segments = self.segments
                indexes = []
                for i in range(partitions):
                    index = np.zeros(n_total, bool)
                    for cell_index in cell_indexes:
                        index[cell_index[i::partitions]] = True
                    indexes.append(index)

            cv_segments = ((segments, segments[np.invert(i)], segments[i]) for i in indexes)
            self.cv_indexes = tuple(indexes)
        self.partitions = partitions
        self.cv_segments = tuple(cv_segments)
        self.model = dataobj_repr(model)

    def data_scale_ndvars(self):
        if self._scale_data:
            # y
            if self.yshape:
                y_mean = NDVar(self.y_mean.reshape(self.yshape), self.ydims, self.y_info, self.y_name)
            else:
                y_mean = self.y_mean[0]
            # scale does not include vector dim
            if self.vector_dim:
                dims = self.ydims[:-1]
                shape = self.yshape[:-1]
            else:
                dims = self.ydims
                shape = self.yshape
            if shape:
                y_scale = NDVar(self.y_scale.reshape(shape), dims, self.y_info, self.y_name)
            else:
                y_scale = self.y_scale[0]
            # x
            x_mean = []
            x_scale = []
            for name, dim, index in self._x_meta:
                if dim is None:
                    x_mean.append(self.x_mean[index])
                    x_scale.append(self.x_scale[index])
                else:
                    dims = (dim,)
                    x_mean.append(NDVar(self.x_mean[index], dims, {}, name))
                    x_scale.append(NDVar(self.x_scale[index], dims, {}, name))
            if self._multiple_x:
                x_mean = tuple(x_mean)
                x_scale = tuple(x_scale)
            else:
                x_mean = x_mean[0]
                x_scale = x_scale[0]
        else:
            y_mean = y_scale = x_mean = x_scale = None
        return y_mean, y_scale, x_mean, x_scale

    def package_kernel(self, h, tstart):
        """Package kernel as NDVar
        
        Parameters
        ----------
        h : array  (n_y, n_x, n_times)
            Kernel data.
        """
        h_time = UTS(tstart, self.time.tstep, h.shape[-1])
        hs = []
        if self._scale_data:
            info = _info.for_normalized_data(self.y_info, 'Response')
        else:
            info = self.y_info

        for name, dim, index in self._x_meta:
            x = h[:, index, :]
            if dim is None:
                dims = (h_time,)
            else:
                dims = (dim, h_time)
            if self.ydims:
                dims = self.ydims + dims
                if len(self.ydims) > 1:
                    x = x.reshape(self.yshape + x.shape[1:])
            else:
                x = x[0]
            hs.append(NDVar(x, dims, info, name))

        if self._multiple_x:
            return tuple(hs)
        else:
            return hs[0]

    def package_value(
            self,
            value: np.ndarray,  # data
            name: str,  # NDVar name
            info: dict = None,  # NDVar info
            meas: str = None,  # for NDVar info
    ):
        if not self.yshape:
            return value[0]

        # shape
        has_vector = value.shape[0] > self.yshape[0]
        if self.vector_dim and not has_vector:
            dims = self.ydims[:-1]
            shape = self.yshape[:-1]
        else:
            dims = self.ydims
            shape = self.yshape
        if not dims:
            return value[0]
        elif len(shape) > 1:
            value = value.reshape(shape)

        # info
        if meas:
            info = _info.for_stat_map(meas, old=info)
        elif info is None:
            info = self.y_info

        return NDVar(value, dims, info, name)

    def package_y_like(self, data, name):
        shape = tuple(map(len, self.full_y_dims))
        data = data.reshape(shape)
        # roll Case to first axis
        for axis, dim in enumerate(self.full_y_dims):
            if isinstance(dim, Case):
                data = np.rollaxis(data, axis)
                dims = list(self.full_y_dims)
                dims.insert(0, dims.pop(axis))
                break
        else:
            dims = self.full_y_dims
        return NDVar(data, dims, {}, name)

    def vector_correlation(self, y, y_pred):
        "Correlation for vector data"
        assert self._scale_data
        assert self.error in ('l1', 'l2')
        assert y.ndim == y_pred.ndim == 3
        # import ipdb; ipdb.set_trace()
        y_pred_norm = norm(y_pred, axis=1)
        y_norm = norm(y, axis=1)
        # l2 correlation
        y_pred_scale = (y_pred_norm ** 2).mean(1) ** 0.5
        y_pred_scale[y_pred_scale == 0] = 1
        y_pred_l2 = y_pred / y_pred_scale[:, newaxis, newaxis]
        if self.error == 'l1':
            y_scale = (y_norm ** 2).mean(1) ** 0.5
            y_l2 = y / y_scale[:, newaxis, newaxis]
        else:
            y_l2 = y
        r_l2 = np.multiply(y_l2, y_pred_l2, out=y_pred_l2).sum(1).mean(1)
        # l1 correlation
        if self.error == 'l1':
            y_pred_scale = y_pred_norm.mean(1)
            y_pred_scale[y_pred_scale == 0] = 1
            y_pred_l1 = y_pred / y_pred_scale[:, newaxis, newaxis]
            # E|X| = 1 --> E√XX = 1
            yy = np.multiply(y, y_pred_l1, out=y_pred_l1).sum(1)
            sign = np.sign(yy)
            np.abs(yy, out=yy)
            yy **= 0.5
            yy *= sign
            r_l1 = yy.mean(1)
        else:
            r_l1 = None
        return r_l2, r_l1
