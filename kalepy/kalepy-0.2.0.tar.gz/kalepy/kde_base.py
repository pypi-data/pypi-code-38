"""
"""
import logging
import six

import numpy as np

from kalepy import kernels


class KDE(object):
    """Core class and primary API for using `Kalepy`, by constructin a KDE based on given data.

    The `KDE` class acts as an API to the underlying `kernel` structures and methods.  From the
    passed data, a 'bandwidth' is calculated and/or set (using optional specifications using the
    `bandwidth` argument).  A `kernel` is constructed (using optional specifications in the
    `kernel` argument) which performs the calculations of the kernel density estimation.


    Notes
    -----
    Reflection ::

        Reflective boundary conditions can be used to better reconstruct a PDF that is known to
        have finite support (i.e. boundaries outside of which the PDF should be zero).

        The `pdf` and `resample` methods accept the keyword-argument (kwarg) `reflect` to specify
        that a reflecting boundary should be used.

        reflect : (D,) array_like, None (default)
            Locations at which reflecting boundary conditions should be imposed.
            For each dimension `D`, a pair of boundary locations (for: lower, upper) must be
            specified, or `None`.  `None` can also be given to specify no boundary at that
            location.

            If a pair of boundaries are given, then the
            first value corresponds to the lower boundary, and the second value to the upper
            boundary, in that dimension.  If there should only be a single lower or upper
            boundary, then `None` should be passed as the other boundary value.

        Example:
           ```reflect=[None, [-1.0, 1.0], [0.0, None]]```
        specifies that the 0th dimension has no boundaries, the 1st dimension has
        boundaries at both -1.0 and 1.0, and the 2nd dimension has a lower boundary at 0.0,
        and no upper boundary.

    Projection / Marginalization ::

        The PDF can be calculated for only particular parameters/dimensions.
        The `pdf` method accepts the keyword-argument (kwarg) `params` to specify particular
        parameters over which to calculate the PDF (i.e. the other parameters are projected over).

        params : int, array_like of int, None (default)
            Only calculate the PDF for certain parameters (dimensions).

            If `None`, then calculate PDF along all dimensions.
            If `params` is specified, then the target evaluation points `pnts`, must only
            contain the corresponding dimensions.

        Example:
        If the `dataset` has shape (4, 100), but `pdf` is called with `params=(1, 2)`,
        then the `pnts` array should have shape `(2, M)` where the two provides dimensions
        correspond to the 1st and 2nd variables of the `dataset`.


    Examples
    --------
    Construct semi-random data:

    >>> import numpy as np
    >>> np.random.seed(1234)
    >>> data = np.random.normal(0.0, 1.0, 1000)

    Construct `KDE` instance using this data, and the default bandwidth and kernels.

    >>> import kalepy as kale
    >>> kde = kale.KDE(data)

    Compare original PDF and the data to the reconstructed PDF from the KDE:

    >>> xx = np.linspace(-3, 3, 400)
    >>> pdf_tru = np.exp(-xx*xx/2) / np.sqrt(2*np.pi)
    >>> pdf_kde = kde.pdf(xx)

    >>> import matplotlib.pyplot as plt
    >>> ll = plt.plot(xx, pdf_tru, 'k--', label='Normal PDF')
    >>> _, bins, _ = plt.hist(data, bins=14, density=True, \
                              color='0.5', rwidth=0.9, alpha=0.5, label='Data')
    >>> ll = plt.plot(xx, pdf_kde, 'r-', label='KDE')
    >>> ll = plt.legend()

    Compare the KDE reconstructed PDF to the "true" PDF, make sure the chi-squared is consistent:

    >>> dof = xx.size - 1
    >>> x2 = np.sum(np.square(pdf_kde - pdf_tru)/pdf_tru**2)
    >>> x2 = x2 / dof
    >>> x2 < 0.1
    True
    >>> print("Chi-Squared: {:.1e}".format(x2))
    Chi-Squared: 1.7e-02

    Draw new samples from the data and make sure they are consistent with the original data:

    >>> import scipy as sp
    >>> samp = kde.resample()
    >>> ll = plt.hist(samp, bins=bins, density=True, color='r', alpha=0.5, rwidth=0.5, \
                      label='Samples')
    >>> ks, pv = sp.stats.ks_2samp(data, samp)
    >>> pv > 0.05
    True
    >>> print("p-value: {:.1e}".format(pv))
    p-value: 9.5e-01

    """
    _BANDWIDTH_DEFAULT = 'scott'
    _SET_OFF_DIAGONAL = True

    def __init__(self, dataset, bandwidth=None, weights=None, kernel=None, neff=None):
        """Initialize the `KDE` class with the given dataset and optional specifications.

        Arguments
        ---------
        dataset : array_like (N,) or (D,N,)
            Dataset from which to construct the kernel-density-estimate.
            For multivariate data with `D` variables and `N` values, the data must be shaped (D,N).
            For univariate (D=1) data, this can be a single array with shape (N,).

        bandwidth : str, float, array of float, None  [optional]
            Specification for the bandwidth, or the method by which the bandwidth should be
            determined.  If a `str` is given, it must match one of the standard bandwidth
            determination methods.  If a `float` is given, it is used as the bandwidth in each
            dimension.  If an array of `float`s are given, then each value will be used as the
            bandwidth for the corresponding data dimension.
        weights : array_like (N,), None  [optional]
            Weights corresponding to each `dataset` point.  Must match the number of points `N` in
            the `dataset`.
            If `None`, weights are uniformly set to 1/N for each value.
        kernel : str, Distribution, None  [optional]
            The distribution function that should be used for the kernel.  This can be a `str`
            specification that must match one of the existing distribution functions, or this can
            be a `Distribution` subclass itself that overrides the `_evaluate` method.
        neff : int, None  [optional]
            An effective number of datapoints.  This is used in the plugin bandwidth determination
            methods.
            If `None`, `neff` is calculated from the `weights` array.  If `weights` are all
            uniform, then `neff` equals the number of datapoints `N`.

        """
        self.dataset = np.atleast_2d(dataset)
        ndim, ndata = self.dataset.shape
        if weights is None:
            weights = np.ones(ndata)/ndata

        self._ndim = ndim
        self._ndata = ndata

        if np.count_nonzero(weights) == 0 or np.any(~np.isfinite(weights) | (weights < 0)):
            raise ValueError("Invalid `weights` entries, all must be finite and > 0!")
        weights = np.atleast_1d(weights).astype(float)
        weights /= np.sum(weights)
        if np.shape(weights) != (ndata,):
            raise ValueError("`weights` input should be shaped as (N,)!")

        self._weights = weights

        if neff is None:
            neff = 1.0 / np.sum(weights**2)

        self._neff = neff

        if bandwidth is None:
            bandwidth = self._BANDWIDTH_DEFAULT
        data_cov = np.cov(dataset, rowvar=True, bias=False, aweights=weights)
        self._data_cov = np.atleast_2d(data_cov)
        self.set_bandwidth(bandwidth)

        # Convert from string, class, etc to a kernel
        dist = kernels.get_distribution_class(kernel)
        self._kernel = kernels.Kernel(distribution=dist, matrix=self.matrix)

        return

    def pdf(self, pnts, **kwargs):
        """Evaluate the kernel-density-estimate PDF at the given data-points.

        This method acts as an API to the `Kernel.pdf` method of this instance's `kernel`.

        Arguments
        ---------
        pnts : ([D,]M,) array_like of float
            The locations at which the PDF should be evaluated.  The number of dimensions `D` must
            match that of the `dataset` that initialized this class' instance.
            NOTE: If the `params` kwarg (see below) is given, then only those dimensions of the
            target parameters should be specified in `pnts`.

        kwargs ::
            Additional, optional keyword arguments passed to `Kernel.pdf`.  Accepted arguments:

            reflect : (D,) array_like, None (default)
                Locations at which reflecting boundary conditions should be imposed.
                For each dimension `D`, a pair of boundary locations (for: lower, upper) must be
                specified, or `None`.  `None` can also be given to specify no boundary at that
                location.  See class docstrings:`Reflection` for more information.

            params : int, array_like of int, None (default)
                Only calculate the PDF for certain parameters (dimensions).
                See class docstrings:`Projection` for more information.

        """
        result = self.kernel.pdf(pnts, self.dataset, self.weights, **kwargs)
        return result

    def resample(self, size=None, keep=None, reflect=None, squeeze=True):
        """Draw new values from the kernel-density-estimate calculated PDF.

        The KDE calculates a PDF from the given dataset.  This method draws new, semi-random data
        points from that PDF.

        Arguments
        ---------
        size : int, None (default)
            The number of new data points to draw.  If `None`, then the number of `datapoints` is
            used.

        keep : int, array_like of int, None (default)
            Parameters/dimensions where the original data-values should be drawn from, instead of
            from the reconstructed PDF.
            TODO: add more information.
        reflect : (D,) array_like, None (default)
            Locations at which reflecting boundary conditions should be imposed.
            For each dimension `D`, a pair of boundary locations (for: lower, upper) must be
            specified, or `None`.  `None` can also be given to specify no boundary at that
            location.
        squeeze : bool, (default: True)
            If the number of dimensions `D` is one, then return an array of shape (L,) instead of
            (1, L).

        Returns
        -------
        samples : ([D,]L) ndarray of float
            Newly drawn samples from the PDF, where the number of points `L` is determined by the
            `size` argument.
            If `squeeze` is True (default), and the number of dimensions in the original dataset
            `D` is one, then the returned array will have shape (L,).

        """
        samples = self.kernel.resample(
            self.dataset, self.weights,
            size=size, keep=keep, reflect=reflect, squeeze=squeeze)
        return samples

    # ==== Properties ====

    @property
    def weights(self):
        return self._weights

    @property
    def neff(self):
        return self._neff

    @property
    def ndim(self):
        return self._ndim

    @property
    def ndata(self):
        return self._ndata

    @property
    def kernel(self):
        return self._kernel

    # ==== BANDWIDTH ====

    def set_bandwidth(self, bandwidth):
        ndim = self.ndim
        _input = bandwidth
        matrix_white = np.zeros((ndim, ndim))

        if len(np.atleast_1d(bandwidth)) == 1:
            _bw, method = self._compute_bandwidth(bandwidth)
            if self._SET_OFF_DIAGONAL:
                matrix_white[...] = _bw
            else:
                idx = np.arange(ndim)
                matrix_white[idx, idx] = _bw
        else:
            if np.shape(bandwidth) == (ndim,):
                # bw_method = 'diagonal'
                for ii in range(ndim):
                    matrix_white[ii, ii] = self._compute_bandwidth(
                        bandwidth[ii], param=(ii, ii))[0]
                method = 'diagonal'
            elif np.shape(bandwidth) == (ndim, ndim):
                for ii, jj in np.ndindex(ndim, ndim):
                    matrix_white[ii, jj] = self._compute_bandwidth(
                        bandwidth[ii, jj], param=(ii, jj))[0]
                method = 'matrix'
            else:
                raise ValueError("`bandwidth` have shape (1,), (N,) or (N,) for `N` dimensions!")

        if np.any(np.isclose(matrix_white.diagonal(), 0.0)):
            ii = np.where(np.isclose(matrix_white.diagonal(), 0.0))[0]
            msg = "WARNING: diagonal '{}' of bandwidth is near zero!".format(ii)
            logging.warning(msg)

        matrix = self.data_cov * (matrix_white ** 2)

        # prev: bw_white
        self._matrix_white = matrix_white
        self._method = method
        self._input = _input
        # prev: bw_cov
        self._matrix = matrix
        return

    def _compute_bandwidth(self, bandwidth, param=None):
        if bandwidth is None:
            bandwidth = self._BANDWIDTH_DEFAULT

        if isinstance(bandwidth, six.string_types):
            if bandwidth == 'scott':
                bw = self.scott_factor(param=param)
            elif bandwidth == 'silverman':
                bw = self.silverman_factor(param=param)
            else:
                msg = "Unrecognized bandwidth str specification '{}'!".format(bandwidth)
                raise ValueError(msg)

            method = bandwidth

        elif np.isscalar(bandwidth):
            bw = bandwidth
            method = 'constant scalar'

        elif callable(bandwidth):
            bw = bandwidth(self, param=param)
            method = 'function'

        else:
            raise ValueError("Unrecognized `bandwidth` '{}'!".format(bandwidth))

        return bw, method

    def scott_factor(self, *args, **kwargs):
        return np.power(self.neff, -1./(self.ndim+4))

    def silverman_factor(self, *args, **kwargs):
        return np.power(self.neff*(self.ndim+2.0)/4.0, -1./(self.ndim+4))

    @property
    def matrix(self):
        return self._matrix

    @property
    def data_cov(self):
        return self._data_cov

    '''
    def pdf_grid(self, edges, *args, **kwargs):
        ndim = self._ndim
        if len(edges) != ndim:
            err = "`edges` must be (D,): an array of edges for each dimension!"
            raise ValueError(err)

        coords = np.meshgrid(*edges)
        shp = np.shape(coords)[1:]
        coords = np.vstack([xx.ravel() for xx in coords])
        pdf = self.pdf(coords, *args, **kwargs)
        pdf = pdf.reshape(shp)
        return pdf
    '''
