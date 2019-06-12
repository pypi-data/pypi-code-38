# # # # # # # # # # # # # # # # # # # # # # # # # #
# Random Walk Model class
#
# Jonas Sukys
# Eawag, Switzerland
# jonas.sukys@eawag.ch
# All rights reserved.
# # # # # # # # # # # # # # # # # # # # # # # # # #

import numba
from scipy import stats
import numpy

from spux.models.model import Model
from spux.utils.annotate import annotate

# fast compiled C code for the computationally intenstive part of the model
@numba.njit
def walk (t_start, t_end, position, drift, stepsize, rvs):
    """Fast compiled C code for the computationally intenstive part of the model."""

    for step in range (t_start, t_end):
        if rvs [step] < drift:
            direction = 1
        else:
            direction = -1
        position += stepsize * direction

    return position

class Randomwalk (Model):
    """Class for Randomwalk model."""

    # no need for sandboxing
    sandboxing = 0

    # construct model
    def __init__ (self, stepsize=1):

        self.stepsize = stepsize

    # initialize model using specified 'inputset' and 'parameters'
    def init (self, inputset, parameters):
        """Initialize model using specified 'inputset' and 'parameters'."""

        # base class 'init (...)' method - OPTIONAL
        Model.init (self, inputset, parameters)

        self.position = parameters ["origin"]
        self.drift = parameters ["drift"]

        self.time = 0

    # run model up to specified 'time' and return the prediction
    def run (self, time):
        """Run model up to specified 'time' and return the prediction."""

        # base class 'run (...)' method - OPTIONAL
        Model.run (self, time)

        # pre-generate random variables for all steps
        steps = time - self.time
        distribution = stats.uniform (loc=-1, scale=2)
        rvs = distribution.rvs (steps, random_state=self.rng)

        # use fast compiled code to advance the random walk
        # self.position = walk (self.time, time, self.position, self.drift, self.stepsize, rvs)

        # update position (e.g., perform walk)
        directions = numpy.where (rvs < self.drift, 1, -1)
        self.position += self.stepsize * numpy.sum (directions)

        # update time
        self.time = time

        # return results
        return annotate (self.position, ['position'], time)
