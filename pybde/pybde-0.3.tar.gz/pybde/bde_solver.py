from enum import IntEnum
import sys
import math
import logging
import heapq
import numpy as np
import matplotlib.pyplot as plt


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
    Binary Delay Equation solver.

    Parameters
    ----------

    func : function func(Z) or func(Z1,Z2) if forced inputs are used
        Z is a list of lists - first index is delay, second is variable
        so Z[0][2] is the values of the 3rd variable at the 1st delay.
        If forcing inputs are used then a second argument Z2 is passed.
        The indexes are the same except they refer to the forcing inputs.

    delays : list of float
        Values of the time delays.
    x : list of float
        Candidate switch points of the input variable state.
    y : list of lists of float
        Variables states for each of the input switch points.  One sublist for each switch point.
    forced_x : list of float
        Candidate switch point of the forced input states.  Optional.  Default value is None.
    forced_y: list of lists of float
        Forced input states for each of the forced input switch points.  One sublist for each
        switch point.
    rel_tol : float
        Relative tolerance used when comparing times. Default is 1e-08
    abs_tol : float
        Absolute tolernace used when comparing times. Default is 0.0
    """
    def __init__(self, func, delays, x, y, forced_x=None, forced_y=None,
                 rel_tol=1e-09, abs_tol=0.0):

        self.logger = logging.getLogger(__name__)

        self.rel_tol = rel_tol
        self.abs_tol = abs_tol

        self.func = func
        self.delays = delays
        self.x = x
        self.y = y

        if forced_x is not None and forced_y is None:
            raise ValueError("Must specify forced_y input if specifying forced_x input")

        if forced_x is None and forced_y is not None:
            raise ValueError("Must specify forced_x input if specifying forced_y input")

        self.have_forced_inputs = (forced_x is not None)
        self.forced_x = forced_x
        self.forced_y = forced_y

        self.res_x = None
        self.res_y = None
        self.start_x = None
        self.end_x = None

        if len(x) != len(y):
            raise ValueError("input x list and input y list must be the same length")

        if self.x[0] != 0:
            raise ValueError("First input switch time in x must be 0.")

        if self.have_forced_inputs:
            if len(forced_x) != len(forced_y):
                raise ValueError(
                    "input forced_x list and input forced_y list must be the same length")
            if self.forced_x[0] != 0:
                raise ValueError("First forced input switch time in x_forced must be 0.")

        # Validate delays are all positive
        for d in delays:
            if d < 0:
                raise ValueError("All delays time must be positive")

        num_state_variables = len(y[0])
        for yy in y:
            if len(yy) != num_state_variables:
                raise ValueError("sublists of input y must all be the same length")

        if self.have_forced_inputs:
            num_forced_state_variables = len(forced_y[0])
            for yy in forced_y:
                if len(yy) != num_forced_state_variables:
                    raise ValueError("sublists of input forced_y must all be the same length")

    def solve(self, start, end):
        """
        Run the simulation from the given start time until the given end time.

        Parameters
        ----------

        start : float
            Start time.
        end : float
            End time.

        Returns
        -------

        list of float, list of lists of bool
            The list of switch point times and the list of lists of the variable states at each of
            these switch points.
        """

        if start < max(self.delays):
            raise ValueError(
                "start_time ({}) must be greater than or equal to the maximum delay ({}).".format(
                    start, max(self.delays)))

        if start <= self.x[-1]:
            raise ValueError("start_time ({}) must be greater than final input time ({}).".format(
                start, self.x[-1]))

        if start >= end:
            raise ValueError("start time ({}) must be less then end time ({})".format(start, end))

        self.end_x = end
        self.start_x = start

        # Result arrays - we start with the given history
        self.res_x = self.x.copy()
        self.res_y = self.y.copy()

        candidate_switch_finder = CandidateSwitchFinder(
            self.delays, self.x, self.start_x, self.end_x, self.forced_x,
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
            if new_state != self.res_y[-1] or t == self.end_x:
                self.logger.debug("State has changed so adding new state: %s", new_state)
                self.res_x.append(t)
                self.res_y.append(new_state)
                candidate_switch_finder.add_new_times(t, len(self.res_x)-1)
            else:
                self.logger.debug("State has not changed")

            t = candidate_switch_finder.get_next_time()

        # If the last result is not the end time then add it in
        last_time = self.res_x[-1]
        if last_time < self.end_x and not math.isclose(
                last_time, self.end_x, rel_tol=self.rel_tol, abs_tol=self.abs_tol):
            self.res_x.append(self.end_x)
            self.res_y.append(self.res_y[-1])

        return self.res_x, self.res_y

    def print_result(self, file=sys.stdout):
        """
        Prints the result of the simulation.

        Parameters
        ----------

        file: file
            The file to write to.  Optional.  The default value is sys.stdout.
        """

        for i in range(len(self.res_x)-1):
            print("{:8.2f} -> {:8.2f} : {}".format(
                self.res_x[i], self.res_x[i+1],
                BDESolver.boolean_list_to_string(self.res_y[i]), file=file))
        if self.res_x[-2] != self.res_x[-1]:
            print("{:8.2f} -> {:8.2f} : {}".format(
                self.res_x[-1],
                self.res_x[-1],
                BDESolver.boolean_list_to_string(self.res_y[-1]),
                file=file))

    def plot_result(self, variable_names=None, forcing_variable_names=None):
        """
        Plots the simulation result to matplotlib.

        Parameters
        -----------

        variable_names : list of string
            Names of the variables. Used to label the plots.  Optional.
        forcing_variable_names : list of string
            Names of the forced inputs . Used to label the plots.  Optional.
        """
        x_data, all_y_data = BDESolver.to_plots(self.res_x, self.res_y)

        if self.have_forced_inputs:
            forced_x_data, all_forced_y_data = \
                BDESolver.to_plots(self.forced_x, self.forced_y, end_time=self.end_x)
            num_forced_plots = len(all_forced_y_data)
            num_plots = len(all_y_data) + num_forced_plots

            num_plot = 1

            for y_data in all_forced_y_data:
                plt.subplot(num_plots, 1, num_plot)
                plt.plot(forced_x_data, y_data)
                if forcing_variable_names and num_plot <= len(forcing_variable_names):
                    plt.title(forcing_variable_names[num_plot - 1])
                plt.yticks([0, 1])
                plt.grid(True)
                num_plot += 1

        else:
            num_plots = len(all_y_data)
            num_forced_plots = 0
            num_plot = 1

        for y_data in all_y_data:
            plt.subplot(num_plots, 1, num_plot)
            plt.plot(x_data, y_data)
            if variable_names and num_plot - num_forced_plots <= len(variable_names):
                plt.title(variable_names[num_plot - num_forced_plots - 1])
            if num_plot == num_plots:
                plt.xlabel('time')
            plt.yticks([0, 1])
            plt.grid(True)

            num_plot += 1

            plt.tight_layout()

    def show_result(self, variable_names=None, forcing_variable_names=None):
        """
        Plots the simulation result to matplotlib and shows it.

        Parameters
        -----------

        variable_names : list of string
            Names of the variables. Used to label the plots.  Optional.
        forcing_variable_names : list of string
            Names of the forced inputs . Used to label the plots.  Optional.
        """
        self.plot_result(
            variable_names=variable_names, forcing_variable_names=forcing_variable_names)
        plt.show()

    def plot_inputs(self, start, end, variable_names=None, forcing_variable_names=None):
        """
        Plots the simulation inputs to matplotlib.

        Parameters
        ----------

        start : float
            Simulation start time.
        end : float
            Simulation end time.
        variable_names : list of string
            Names of the variables. Used to label the plots.  Optional.
        forcing_variable_names : list of string
            Names of the forced inputs . Used to label the plots.  Optional.
        """
        x_data, all_y_data = BDESolver.to_plots(self.x, self.y, end_time=start)

        xlim = None # limit of x axis
        if self.have_forced_inputs:
            forced_x_data, all_forced_y_data = \
                BDESolver.to_plots(self.forced_x, self.forced_y, end_time=end)

            num_forced_plots = len(all_forced_y_data)
            num_plots = len(all_y_data) + num_forced_plots

            num_plot = 1

            for y_data in all_forced_y_data:
                plt.subplot(num_plots, 1, num_plot)
                plt.plot(forced_x_data, y_data)
                if forcing_variable_names and num_plot <= len(forcing_variable_names):
                    plt.title(forcing_variable_names[num_plot - 1])
                plt.yticks([0, 1])
                plt.grid(True)
                num_plot += 1
                xlim = plt.xlim()

        else:
            num_plots = len(all_y_data)
            num_forced_plots = 0
            num_plot = 1

        for y_data in all_y_data:
            plt.subplot(num_plots, 1, num_plot)
            plt.plot(x_data, y_data)
            if variable_names and num_plot - num_forced_plots <= len(variable_names):
                plt.title(variable_names[num_plot - num_forced_plots - 1])
            if num_plot == num_plots:
                plt.xlabel('time')
            plt.yticks([0, 1])
            plt.grid(True)

            if self.have_forced_inputs:
                # Extend plot to the end of the simulations
                plt.xlim(xlim)

            num_plot += 1

        plt.tight_layout()

    def show_inputs(self, start, end, variable_names=None, forcing_variable_names=None):
        """
        Plots the simulation inputs to matplotlib and shows it.

        Parameters
        ----------

        start : float
            Simulation start time.
        end : float
            Simulation end time.
        variable_names : list of string
            Names of the variables. Used to label the plots.  Optional.
        forcing_variable_names : list of string
            Names of the forced inputs . Used to label the plots.  Optional.
        """
        self.plot_inputs(start, end,
                         variable_names=variable_names,
                         forcing_variable_names=forcing_variable_names)
        plt.show()

    @staticmethod
    def to_logical(x):
        """
        Converts and list of integers containing 1s and 0s to a list of boolean values.

        Parameter
        ---------

        x : list of integers
            List of integers containing 1s and 0s.

        Returns
        -------

        list of boolean
            A list where all 0s are replaced with False and all 1s replaced with True.
        """
        return (np.array(x) > 0).tolist()

    @staticmethod
    def boolean_list_to_string(l):
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

    @staticmethod
    def to_plots(x, y, end_time=-1):
        """
        Converts switch point data into plot data format.

        Parameters
        ----------

        x : list of float
            Switch point time values.
        y : list of lists of boolean
            List of list of state variables corresponding to the time values in the x parameter.
        end_time : float
            Final simulation time. Optional.
        Returns
        -------

        list of float, list of list of integers
            The first list is the time values of the plot format data, the second list contains
            lists of 0s and 1s representing the variable states at these time points.
        """
        res_x = []
        res_y = []

        res_x = [x[0]]
        for i in range(1, len(x)):
            res_x.append(x[i])
            res_x.append(x[i])
        if end_time > 0:
            res_x.append(end_time)

        for v in range(0, len(y[0])):
            plot_y = []
            for i in range(len(y)-1):
                plot_y.append(y[i][v])
                plot_y.append(y[i][v])
            plot_y.append(y[-1][v])
            if end_time > 0:
                plot_y.append(plot_y[-1])
            res_y.append(plot_y)

        return res_x, res_y
