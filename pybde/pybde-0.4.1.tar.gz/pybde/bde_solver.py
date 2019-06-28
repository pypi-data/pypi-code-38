from enum import IntEnum
import sys
import math
import logging
import heapq
import matplotlib.pyplot as plt
from pybde.boolean_time_series import BooleanTimeSeries


class IndexType(IntEnum):
    """
    Represents the type of an index, can be either a index to state variables,
    forced inputs or no index.
    """
    VARIABLE = 1
    FORCED_INPUT = 2
    NONE = 3


class CandidateSwitchFinder:
    """
    Discovers candidate switch points and keeps indexes into the result and
    forced input arrays for each delay.

    Parameters
    ----------

    delays: list of float
        Values of the time delays.
    x: list of float
        Input switch points
    start: float
        Start time of the simulation
    end: float
        End time of the simulation
    forced_x: list of float
        Switch points of the forces inputs. Default value is None.
    rel_tol:
        Relative tolerance used to compare times. Default value is 1e-09.
    abs_tol: float
        Absolute tolerance used to compare times. Default value is 0.0.


    Attributes
    ----------

    indices : list of int
        The current indices into the variables state array for each delay.

    forced_indices : list of int
        The current indices into the forced input state array for each delay.

    """
    def __init__(self, delays, x, start, end, forced_x=None, rel_tol=1e-09, abs_tol=0.0):

        self.logger = logging.getLogger(__name__ + ".CandidateSwitchFinder")

        self.rel_tol = rel_tol
        self.abs_tol = abs_tol

        self.start = start
        self.end = end
        self.delays = delays

        self.indices = [0] * len(delays)
        self.have_forced_inputs = (forced_x is not None)
        if self.have_forced_inputs:
            self.forced_indices = [0] * len(delays)

        # A priority queue that contains tuples of (t, i, IndexType, j) where:
        #   t is a candidate
        #   i is the delay index, 0..num_delays-1
        #   IndexType is the type of index : variable, forced or none
        #   j is the variable state or forced input index in accordance with previous value
        self.times = []

        for i, d in enumerate(self.delays):
            d = self.delays[i]
            for j, t in enumerate(x):
                if self.is_time_before_end(t + d):
                    heapq.heappush(self.times, (t + d, i, IndexType.VARIABLE, j))
                    self.logger.debug("Adding CSP (%s, %s, %s, %s)",
                                      t + d, i, IndexType.VARIABLE, j)

            if self.have_forced_inputs:
                for j, t in enumerate(forced_x):
                    if self.is_time_before_end(t + d):
                        heapq.heappush(self.times, (t + d, i, IndexType.FORCED_INPUT, j))
                        self.logger.debug("Adding CSP (%s, %s, %s, %s)",
                                          t + d, i, IndexType.FORCED_INPUT, j)

        # pop all the indexes until start - this gets all the index correct before start
        self.pop_until_start()
        self.logger.debug("Processed all CSPs before start.")

        # Add the start time in case it is not a candidate - give it no new index information
        heapq.heappush(self.times, (start, -1, IndexType.NONE, -1))
        self.logger.debug("Adding CSP (%s, %s, %s, %s)",
                          start, -1, IndexType.NONE, -1)

    def add_new_times(self, t, variable_state_index):
        """
        Given a new switch point add future candidate switch points.

        Parameters
        ----------

        t : float
            New switch point time.
        variable_state_index:
            Index into the state variables array for this switch point.
        """
        for i in range(0, len(self.delays)):
            new_time = self.delays[i] + t
            if self.is_time_before_end(new_time):
                heapq.heappush(self.times, (new_time, i, IndexType.VARIABLE, variable_state_index))
                self.logger.debug("Adding CSP "
                                  ""
                                  ""
                                  ""
                                  "(%s, %s, %s, %s)",
                                  new_time, i, IndexType.VARIABLE, variable_state_index)

    def get_next_time(self):
        """
        Gets the next candidate switch point.

        Returns
        -------

        float
            The time of the next candidate switch point, or None if not candidate switch
            points left.
        """
        self.logger.debug("CSPs: %s", self.times)

        times = []
        if self.times:
            next_time = self.pop_and_update_indices()
            times.append(next_time)

            while self.times and self.times_are_equal(self.times[0][0], next_time):
                times.append(self.times[0][0])
                self.pop_and_update_indices()

            # take the median time to avoid drift towards the lowest
            next_time = times[len(times)//2]
            self.logger.debug("Next time is: %s", next_time)

            return next_time

        return None

    def times_are_equal(self, t1, t2):
        """
        Compares if two times are equal within tolerance.

        Parameters
        ----------

        t1 : float
            A time point.
        t2 : float
            A time point.

        Returns
        -------

        bool
            True if the two times are equal, False otherwise.
        """
        return math.isclose(t1, t2, rel_tol=self.rel_tol, abs_tol=self.abs_tol)

    def is_time_before_end(self, t):
        """
        Tests if the given time is before or equal to the simulation end time.

        Parameters
        ---------

        t : float
            A time point.

        Returns
        -------

        bool
            True if the time is before or equal to the end point.

        """
        if t < self.end:
            return True

        return self.times_are_equal(t, self.end)

    def pop_until_start(self):
        """
        Removes all candidate end points that occur before the simulation start time,
        updating the indices for each delay as it does so.
        """
        while self.times and self.times[0][0] < self.start:
            self.pop_and_update_indices()

    def pop_and_update_indices(self):
        """
        Removes the next candidate switch point and updates the indices for each delay.

        Returns
        -------

        float
            Next candidate switch point.

        """
        next_time, delay_index, index_type, state_index = heapq.heappop(self.times)

        if index_type == IndexType.VARIABLE:
            self.indices[delay_index] = state_index
        elif index_type == IndexType.FORCED_INPUT:
            self.forced_indices[delay_index] = state_index

        return next_time


class BDESolver:
    """
    Boolean Delay Equation solver.

    Parameters
    ----------

    func : function func(Z) or func(Z1,Z2) if forced inputs are used
        Z is a list of lists - first index is delay, second is variable
        so Z[0][2] is the values of the 3rd variable at the 1st delay.
        If forcing inputs are used then a second argument Z2 is passed.
        The indexes are the same except they refer to the forcing inputs.

    delays : list of float
        Values of the time delays.
    history: list of BooleanTimeSeries
        History time series for each variable.
    forcing_inputs: list of BooleanTimeSeries
        Time series for each forcing input. Default value is None.
    rel_tol : float
        Relative tolerance used when comparing times. Default is 1e-08
    abs_tol : float
        Absolute tolerance used when comparing times. Default is 0.0
    """
    def __init__(self, func, delays, history, forcing_inputs=None,
                 rel_tol=1e-09, abs_tol=0.0):

        self.logger = logging.getLogger(__name__)

        self.rel_tol = rel_tol
        self.abs_tol = abs_tol

        self.func = func
        self.delays = delays
        self.t, self.y = BooleanTimeSeries.merge(history)
        self.history = history
        self.results = None

        # Validate history switch points
        for data in history:
            if data.t[0] != 0:
                raise ValueError("All history data must start at t=0")

        # All histories must end at the same time, this will be the simulation start time
        self.start_t = history[0].end
        for inp in history:
            if inp.end != self.start_t:
                raise ValueError("All history data must end at same time.")

        # Validate forced inputs
        if forcing_inputs:
            for data in forcing_inputs:
                if data.t[0] != 0:
                    raise ValueError("All forced input data must start at t=0")

        self.forced_inputs = forcing_inputs
        self.forced_t = None
        self.forced_y = None
        self.have_forced_inputs = (forcing_inputs is not None)
        if self.have_forced_inputs:
            self.forced_t, self.forced_y = BooleanTimeSeries.merge(forcing_inputs)

        self.res_t = None
        self.res_y = None
        self.end_t = None

        # Validate delays are all positive
        for d in delays:
            if d < 0:
                raise ValueError("All delays time must be positive")

        if self.start_t < max(self.delays):
            raise ValueError(
                "History must extend greater than or equal to the maximum delay ({}).".format(
                    max(self.delays)))

    def solve(self, end):
        """
        Run the simulation from the given start time until the given end time.

        Parameters
        ----------

        end : float
            End time.

        Returns
        -------

        list of BooleanTimeSeries
            A list containing a BooleanTimeSeries for each simulated variable.
        """

        if self.start_t >= end:
            raise ValueError("end time ({}) must be greater than simulation start time({})".format(
                end, self.start_t))

        self.end_t = end

        # Result arrays - we start with the given history
        self.res_t = self.t.copy()
        self.res_y = self.y.copy()

        candidate_switch_finder = CandidateSwitchFinder(
            self.delays, self.t, self.start_t, self.end_t, self.forced_t,
            rel_tol=self.rel_tol, abs_tol=self.abs_tol)

        t = candidate_switch_finder.get_next_time()
        while t is not None:
            self.logger.debug("======================================================")
            self.logger.debug("t=%f", t)
            Z = []
            for d_index in range(len(candidate_switch_finder.indices)):
                i = candidate_switch_finder.indices[d_index]
                self.logger.debug(
                    "Delay %s is at index %s of result list = %s", d_index, i, self.res_y)
                Z.append(self.res_y[i])

            if not self.have_forced_inputs:
                new_state = self.func(Z)
                self.logger.debug("Input to model function for time t=%f is %s", t, Z)
            else:
                Z2 = []
                for i in candidate_switch_finder.forced_indices:
                    Z2.append(self.forced_y[i])
                new_state = self.func(Z, Z2)
                self.logger.debug("Input to model function for time t=%f is %s, %s", t, Z, Z2)

            self.logger.debug("New state at t=%f is %s", t, new_state)

            # Keep this state if it has changed or this is the end of the simulation
            if new_state != self.res_y[-1] or t == self.end_t:
                self.logger.debug("State has changed so adding new state: %s", new_state)
                self.res_t.append(t)
                self.res_y.append(new_state)
                candidate_switch_finder.add_new_times(t, len(self.res_t) - 1)
            else:
                self.logger.debug("State has not changed")

            t = candidate_switch_finder.get_next_time()

        # Copy over labels and styles
        self.results = BooleanTimeSeries.unmerge(self.res_t, self.res_y, self.end_t)
        for i, result in enumerate(self.results):
            result.label = self.history[i].label
            result.style = self.history[i].style

        return self.results

    def print_result(self, file=sys.stdout):
        """
        Prints the result of the simulation.

        Parameters
        ----------

        file: file
            The file to write to.  Optional.  The default value is sys.stdout.
        """

        for i in range(len(self.res_t) - 1):
            print("{:8.2f} -> {:8.2f} : {}".format(
                self.res_t[i], self.res_t[i + 1],
                BDESolver._boolean_list_to_string(self.res_y[i]), file=file))
        if self.res_t[-2] != self.res_t[-1]:
            print("{:8.2f} -> {:8.2f} : {}".format(
                self.res_t[-1],
                self.res_t[-1],
                BDESolver._boolean_list_to_string(self.res_y[-1]),
                file=file))

    def plot_result(self):
        """
        Plots the simulation result to matplotlib.
        """

        to_plot = self.results
        if self.forced_inputs:
            to_plot += self.forced_inputs

        BooleanTimeSeries.plot_many(to_plot)
        plt.legend()
        plt.xlabel("time")
        plt.tight_layout()

    def show_result(self):

        """
        Plots the simulation result to matplotlib and shows it.
        """

        self.plot_result()
        plt.show()


    @staticmethod
    def _boolean_list_to_string(l):
        """
        Converts a boolean list to a string of T and F characters.

        Parameters
        ----------

        l : boolean list
            Boolean list to convert.

        Returns
        -------

        str
           string of T and F characters representing the content of the boolean list.
        """
        res = ""
        for x in l:
            if x:
                res += "T "
            else:
                res += "F "
        return res
