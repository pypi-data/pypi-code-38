# # # # # # # # # # # # # # # # # # # # # # # # # #
# Wrapper class for tensorizing distributions from scipy.stats
# For a review of wrap'able distributions, see the list of univariate distributions at:
# https://docs.scipy.org/doc/scipy/reference/stats.html
#
# Jonas Sukys
# Eawag, Switzerland
# jonas.sukys@eawag.ch
# All rights reserved.
# # # # # # # # # # # # # # # # # # # # # # # # # #

import numpy
import pandas

from .distribution import Distribution
from spux.utils.transforms import rounding

class Tensor (Distribution):

    def __init__ (self, distributions, types_of_keys=None):

        self.distributions = distributions
        self.labels = list (distributions.keys ())
        self.types = {}

        for key in distributions:
            if types_of_keys is not None:
                if key not in types_of_keys:
                    raise ValueError("Fatal. Specified parameter is not in the list.")
                self.types [key] = types_of_keys [key]
                if types_of_keys[key][0:3].lower() == 'int' or types_of_keys[key].lower() == 'binary':
                    distributions [key].pdf = rounding (distributions [key].pmf)
                    distributions [key].logpdf = rounding (distributions [key].logpmf)
            else:
                self.types [key] = 'float'

    # evaluate a joint PDF of the tensorized random variables
    # 'parameters' is assumed to be of a pandas.Series type
    def pdf (self, parameters):
        """Evaluate the (joint) prob. distr. function of the tensorized, i.e. assuming independence, random variables 'parameters'.

        'parameters' are assumed to be of a pandas.Series type
        """

        pdfs = [ self.distributions [label] .pdf (parameter) for label, parameter in parameters.items () if not numpy.isnan (parameter) ]

        return numpy.prod (pdfs) if len (pdfs) > 0 else 0

    # evaluate a joint log-PDF of the tensorized random variables
    # 'parameters' is assumed to be of a pandas.Series type
    def logpdf (self, parameters):
        """Evaluate the logarithm of the (joint) prob. distr. function of the tensorized, i.e. assuming independence, random variables 'parameters'.

        'parameters' are assumed to be of a pandas.Series type
        """

        logpdfs = [ self.distributions [label] .logpdf (parameter) for label, parameter in parameters.items () if not numpy.isnan (parameter) ]

        return numpy.sum (logpdfs) if len (logpdfs) > 0 else float ('-inf')

    # return marginal PDF for the specified parameter
    def mpdf (self, label, parameter):
        """Return marginal PDF for the specified parameter."""

        return self.distributions [label] .pdf (parameter)

    # return marginal log-PDF for the specified parameter
    def logmpdf (self, label, parameter):
        """Return marginal log-PDF for the specified parameter."""

        return self.distributions [label] .logpdf (parameter)

    # return intervals for the specified centered probability mass
    def intervals (self, alpha=0.99):
        """Return intervals for the specified centered probability mass."""

        intervals = { label : list (distribution.interval (alpha)) for label, distribution in self.distributions.items () }
        return intervals

    # draw a random vector using the provided random state 'rng'
    def draw (self, rng):
        """Draw a random vector using the provided random state 'rng'.
        """

        parameters = { label : distribution.rvs (random_state = rng) for label, distribution in self.distributions.items () }
        return pandas.Series (parameters)
