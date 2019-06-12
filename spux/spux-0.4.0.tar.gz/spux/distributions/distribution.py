# # # # # # # # # # # # # # # # # # # # # # # # # #
# Base class for distributions
#
# Jonas Sukys
# Eawag, Switzerland
# jonas.sukys@eawag.ch
# All rights reserved.
# # # # # # # # # # # # # # # # # # # # # # # # # #

import pandas

class Distribution (object):

    # evaluate a joint PDF of the distribution
    # 'parameters' is assumed to be of a pandas.DataFrame type
    def pdf (self, parameters):
        """Base method to be overloaded to evaluate the (joint) prob. distr. function of parameters.

        'parameters' are assumed to be of a pandas.DataFrame type
        """

        return float ('nan')

    # evaluate a joint log-PDF of the distribution
    # 'parameters' is assumed to be of a pandas.DataFrame type
    def logpdf (self, parameters):
        """Base method to be overloaded to evaluate the logarithm of the
        (joint) prob. distr. function of parameters.

        'parameters' are assumed to be of a pandas.DataFrame type
        """

        return float ('nan')

    # return marginal PDF for the specified parameter
    def mpdf (self, label, parameter):
        """Return marginal PDF for the specified parameter."""

        return float ('nan')

    # return marginal log-PDF for the specified parameter
    def logmpdf (self, label, parameter):
        """Return marginal log-PDF for the specified parameter."""

        return float ('nan')

    # return intervals (for each parameter) for the specified centered probability mass
    def intervals (self, alpha=0.99):
        """Return intervals for the specified centered probability mass.

        Intervals are returned for each parameter.
        """

        return { 'parameter' : [float ('nan'), float ('nan')] }

    # draw a random vector using the provided random state 'rng'
    def draw (self, rng):
        """
        Draw a random vector using the provided random state 'rng'.
        """

        parameters = { 'parameter' : float ('nan') }
        return pandas.Series (parameters)