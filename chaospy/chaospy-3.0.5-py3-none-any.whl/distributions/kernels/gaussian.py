"""Gaussian kernel density estimation."""
import numpy
from scipy.special import ndtr, ndtri
from scipy.stats import gaussian_kde

from ..baseclass import Dist


class GaussianKDE(Dist):
    """
    Gaussian kernel density estimation.

    Examples:
        >>> distribution = GaussianKDE([0, 1, 1, 1, 2])
        >>> print(distribution)
        GaussianKDE()
        >>> q = numpy.linspace(0, 1, 7)[1:-1]
        >>> print(numpy.around(q, 4))
        [0.1667 0.3333 0.5    0.6667 0.8333]
        >>> print(numpy.around(distribution.fwd(distribution.inv(q)), 4))
        >>> print(numpy.around(distribution.inv(q), 4))
        >>> print(numpy.around(distribution.sample(4), 4))
        >>> print(numpy.around(distribution.mom(1), 4))
        >>> print(numpy.around(distribution.ttr([1, 2, 3]), 4))
    """

    def __init__(self, samples, lower=None, upper=None):

        samples = numpy.asarray(samples)
        if len(samples.shape) == 1:
            samples = samples.reshape(1, -1)
        kernel = gaussian_kde(samples, bw_method="scott")

        if lower is None:
            lower = samples.min(axis=-1)
        if upper is None:
            upper = samples.max(axis=-1)

        self.lower = lower
        self.upper = upper
        self.samples = samples
        self.l_fwd = numpy.linalg.cholesky(kernel.covariance)
        self.l_inv = numpy.linalg.inv(self.l_fwd)
        super(GaussianKDE, self).__init__()

    def __len__(self):
        return len(self.samples)

    def _pdf(self, x_data):
        out = numpy.zeros(x_data.shape)

        # first dimension is simple:
        for sample in self.samples[0]:
            z = self.l_inv[0, 0]*(x_data[0] - sample)
            out[0] += numpy.e**(-0.5*z*z) / len(self.samples[0])
        out[0] *= self.l_inv[0, 0]*(2*numpy.pi)**-0.5

        return out

    def _cdf(self, x_data):
        out = numpy.zeros(x_data.shape)

        # first dimension is simple:
        print(x_data)
        for sample in self.samples[0]:
            z = self.l_inv[0, 0]*(x_data[0] - sample)
            print(z)
            z = ndtr(z)
            out[0] += z / len(self.samples[0])

        return out

    def _ppf(self, u_data):
        out = numpy.zeros(u_data.shape)

        # first dimension is simple:
        z = self.l_fwd[0, 0]*ndtri(u_data[0])
        for sample in self.samples[0]:
            out[0] += (z + sample) / len(self.samples[0])
            # print("i", out)
        # print(out)

        return out

    def _bnd(self, x_data):
        return self.lower, self.upper
