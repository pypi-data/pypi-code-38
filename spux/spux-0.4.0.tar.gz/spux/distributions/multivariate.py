# # # # # # # # # # # # # # # # # # # # # # # # # #
# Wrapper class for multivariate distributions from scipy.stats
# For a review of wrap'able distributions, see the multivariate section in:
# https://docs.scipy.org/doc/scipy/reference/stats.html
#
# Jonas Sukys
# Eawag, Switzerland
# jonas.sukys@eawag.ch
# All rights reserved.
# # # # # # # # # # # # # # # # # # # # # # # # # #

import pandas

from .distribution import Distribution

class Multivariate (Distribution):

    def __init__ (self, distribution, labels, marginals=None):

        self.distribution = distribution
        self.labels = labels
        self.marginals = marginals

    # evaluate a joint PDF
    # 'parameters' is assumed to be of a pandas.DataFrame type
    def pdf (self, parameters):
        """Evaluate the (joint) prob. distr. function of (covariate) parameters.

        'parameters' are assumed to be of a pandas.DataFrame type
        """

        ordered = [ parameters [label] for label in self.labels ]
        return self.distribution.pdf (ordered)

    # evaluate a joint log-PDF
    # 'parameters' is assumed to be of a pandas.DataFrame type
    def logpdf (self, parameters):
        """
        Evaluate the logarithm of the (joint) prob. distr. function of (covariate) parameters.

        'parameters' are assumed to be of a pandas.DataFrame type
        """

        ordered = [ parameters [label] for label in self.labels ]
        return self.distribution.logpdf (ordered)

    # return marginal PDF for the specified parameter
    def mpdf (self, label, parameter):
        """Return marginal PDF for the specified parameter."""

        if self.marginals is not None:
            return self.marginals [label] .pdf (parameter)
        else:
            return float ('nan')

    # return marginal log-PDF for the specified parameter
    def logmpdf (self, label, parameter):
        """Return marginal log-PDF for the specified parameter."""

        if self.marginals is not None:
            return self.marginals [label] .logpdf (parameter)
        else:
            return float ('nan')

    # return intervals for the specified centered probability mass
    def intervals (self, alpha=0.99):
        """Return intervals for the specified centered probability mass."""

        if self.marginals is not None:
            intervals = { label : list (distribution.interval (alpha)) for label, distribution in self.marginals.items () }
        else:
            intervals = [float ('nan'), float ('nan')]

        return intervals

    # draw a random parameter vector using the provided RNG engine
    # 'offset' is assumed to be of a pandas.DataFrame type
    def draw (self, rng):
        """Draw a random vector using the provided random state 'rng'."""

        vector = self.distribution.rvs (random_state = rng)
        parameters = { label : vector [index] for index, label in enumerate (self.labels) }
        return pandas.Series (parameters)
