import math
import matplotlib.pyplot as plt
import numpy as np


class BooleanTimeSeries:
    """
    Boolean time series.

    Parameters
    ----------

    t : list of float, or numpy array of float
        Time points at which state changes occur.
    y : list of bool
        New state at each of the time points in t. If this list is
        shorter than t then it will be padded with alternate True
        and False values continuing from the sequence specified.
    end : float
        The end time of the time series
    label : str
        Label used when plotting the time series. Optional. Default value is None.
    style : str
        matplotlib style used when plotting the time series. Optional. Default value is None.

    Attributes
    ----------

    t : list of float, or numpy array of float
        Time points at which state changes occur.
    y : list of bool
        New state at each of the time points in t.
    end : float
        The end time of the time series
    label : str
        Label used when plotting the time series.
    style : str
        matplotlib style used when plotting the time series.

    """

    rel_tol = 1e-09
    abs_tol = 0.0

    def __init__(self, t, y, end, label=None, style=None):
        self.t = t
        self.y = y

        # Handle numpy arrays as input
        if isinstance(self.t, np.ndarray):
            self.t = self.t.tolist()
        if isinstance(self.y, np.ndarray):
            self.y = self.y.tolist()

        self.end = end
        self.label = label
        self.style = style

        # Pad out the state values to be the length of the inputs
        while len(y) < len(t):
            y.append(not y[-1])

        if len(y) > len(t):
            raise ValueError("Cannot specify more value elements (y) that time elements (t).")

        for i in range(len(t)-1):
            if t[i] >= t[i+1]:
                raise ValueError("Time values (t) must be incrementing.")

        if end < t[-1]:
            raise ValueError("End time must be equal to or greater than last switch time")

    def __str__(self):
        """
        String showing details of the Boolean time series.

        Returns
        -------

        str
            Details of the Boolean time series.
        """
        return 't={}, y={}, end={}'.format(self.t, self.y, self.end)

    def __repr__(self):
        """
        String showing representation of the Boolean time series.

        Returns
        -------

        str
            Representation of the Boolean time series.
        """
        return 'BooleanTimeSeries({},{},{},{},{})'.format(
            self.t, self.y, self.end, self.label, self.style)

    def cut(self, new_start, new_end, keep_switch_on_end=False):
        """
        Cuts and returns a part of the time series.

        Parameters
        ----------

        new_start : float
            Starting time of the part to cut.
        new_end : float
            End time of the part to cut.
        keep_switch_on_end:
            Specifies if a switch point at the new end time should be kept or not. Optional. Default
            is False.

        Returns
        -------

        BooleanTimeSeries
            New Boolean time series identical to the original put restricted to the specified
            range.
        """
        res_t = []
        res_y = []

        if BooleanTimeSeries._is_time_before_or_equal(new_end, new_start):
            raise ValueError("End cut time cannot be before start cut time")

        # Error if cut out of range
        if BooleanTimeSeries._is_time_before(new_start, self.t[0]):
            raise ValueError("Cannot cut from a value before the start.")

        # Find the start
        if BooleanTimeSeries._is_time_before(self.end, new_end):
            raise ValueError("Cannot cut to a value after the end.")

        for i, tt in enumerate(self.t):
            if BooleanTimeSeries._is_time_before_or_equal(new_start, tt):
                if BooleanTimeSeries._is_time_before(tt, new_end) or \
                        (keep_switch_on_end and BooleanTimeSeries._times_are_equal(tt, new_end)):
                    if not res_t and not BooleanTimeSeries._times_are_equal(new_start, tt):
                        res_t.append(new_start)
                        res_y.append(last_state_before_start)
                    res_t.append(tt)
                    res_y.append(self.y[i])
            else:
                last_state_before_start = self.y[i]

        # If we have no switch points then add a single state at the start
        if not res_t:
            res_t.append(new_start)
            res_y.append(last_state_before_start)

        return BooleanTimeSeries(res_t, res_y, new_end, label=self.label, style=self.style)

    def compress(self):  # Remove redundant switch points
        """
        Compresses the internal representation to remove redundant time points where the state
        does not change.

        Returns
        -------

        BooleanTimeSeries
            self
        """
        previous_y = None
        res_t = []
        res_y = []
        for i, yy in enumerate(self.y):
            if yy != previous_y:
                res_t.append(self.t[i])
                res_y.append(yy)
                previous_y = yy
        self.t = res_t
        self.y = res_y

        return self


    def hamming_distance(self, other):
        """
        Calculates the Hamming distance comparing this Boolean time series with another.

        Parameters
        ----------

        other : BooleanTimeSeries
            Boolean time series to compare with.

        Returns
        -------

        Hamming distance which is the total duration for which the two time series differ.
        """

        if self.end != other.end or self.t[0] != other.t[0]:
            raise ValueError("Can only calculate Hamming distance over identical ranges.")
        distance = 0.0

        times, states = BooleanTimeSeries.merge([self, other])
        times.append(self.end)

        for i, state in enumerate(states):
            if state[0] != state[1]:
                distance += times[i+1] - times[i]

        return distance

    def plot(self, offset=0, scale=1):
        """
        Plots the Boolean time series to a matplotlib plot.

        If present the plot label and line style are taken from the label and style attributes of
        this BooleanTimeSeries instance.

        The plot will not be displayed. To show or save the plot use the appropriate matplotlib
        functionality.

        Parameters
        ----------

        offset : float
            Specifies an offset from 0 and 1 at which to plot the line. This can be very useful if
            plotting multiple Boolean time series on the same plot. Optional. Default is 0.

        scale : float
            Specifies that the value to plot for True is a value other than 1. This can be useful
            when plotting Boolean time series alongside experimental data.  Optional. Default is 1.
        """
        plot_t, plot_y = self.to_plot_data(offset=offset, scale=scale)
        if self.style:
            plt.plot(plot_t, plot_y, self.style, label=self.label)
        else:
            plt.plot(plot_t, plot_y, label=self.label)

    def show(self, offset=0, scale=1):
        """
        Plots the Boolean time series to a matplotlib plot and shows it.

        If present the plot label and line style are taken from the label and style attributes of
        this BooleanTimeSeries instance.

        Parameters
        ----------

        offset : float
            Specifies an offset from 0 and 1 at which to plot the line. This can be very useful if
            plotting multiple Boolean time series on the same plot. Optional. Default is 0.

        scale : float
            Specifies that the value to plot for True is a value other than 1. This can be useful
            when plotting Boolean time series alongside experimental data.  Optional. Default is 1.
        """
        plot_t, plot_y = self.to_plot_data(offset=offset, scale=scale)
        if self.style:
            plt.plot(plot_t, plot_y, self.style, label=self.label)
        else:
            plt.plot(plot_t, plot_y, label=self.label)
        plt.yticks([0, 1])
        plt.grid(True)
        plt.tight_layout()

    def to_plot_data(self, offset=0, scale=1):
        """
        Obtains the Boolean time series in a format suitable for plotting as using various plotting
        libraries.

        This method is useful if you wish to take full control over how the results are plotted.

        Parameters
        ----------

        offset : float
            Specifies an offset from 0 and 1 at which to plot the line. This can be very useful if
            plotting multiple Boolean time series on the same plot. Optional. Default is 0.

        scale : float
            Specifies that the value to plot for True is a value other than 1. This can be useful
            when plotting Boolean time series alongside experimental data.  Optional. Default is 1.

        Returns
        -------

        list of float, list of bool

            The first list contains the time values, the second list contains the corresponding y
            values.
        """
        res_y = []
        res_t = [self.t[0]]
        for i in range(1, len(self.t)):
            res_t.append(self.t[i])
            res_t.append(self.t[i])
        if self.t[-1] < self.end and not np.isclose(self.t[-1], self.end):
            res_t.append(self.end)

        for i in range(len(self.y)-1):
            res_y.append(self.y[i] * scale + offset)
            res_y.append(self.y[i] * scale + offset)
        res_y.append(self.y[-1] * scale + offset)
        if self.t[-1] < self.end and not np.isclose(self.t[-1], self.end):
            res_y.append(self.y[-1] * scale + offset)

        return res_t, res_y

    @staticmethod
    def plot_many(list_of_time_series, offset=0.05):
        """
        Plots multiple Boolean time series to a matplotlib plot.

        The plot will not be displayed. To show or save the plot use the appropriate matplotlib
        functionality.

        Parameters
        ----------

        list_of_time_series : list of BooleanTimeSeries
            Time series to plot.

        offset : float
            Specifies an vertical axis offset between each plot. Optional. Default is 0.05
        """
        for i, time_series in enumerate(list_of_time_series):
            time_series.plot(offset=offset*i)
        plt.yticks([0, 1])
        plt.grid(True)
        plt.tight_layout()

    @staticmethod
    def show_many(list_of_time_series, offset=0.05):
        """
        Plots multiple Boolean time series to a matplotlib plot and shows it.

        Parameters
        ----------

        list_of_time_series : list of BooleanTimeSeries
            Time series to plot.

        offset : float
            Specifies an vertical axis offset between each plot. Optional. Default is 0.05
        """
        BooleanTimeSeries.plot_many(list_of_time_series, offset=offset)
        plt.show()

    @staticmethod
    def absolute_threshold(t, y, threshold):
        """
        Produces Boolean time series data from numerical time series data using thresholding
        and linear interpolation.

        Parameters
        ----------

        t : list of float, or numpy array of float
            Time points
        y : list of float, or numpy array of float
            Values corresponding to the time points.

        threshold : float
            Absolute threshold.

        Returns
        -------

        A Boolean time series produced by thresholding the input data at the specified threshold.
        Then the value is above the threshold the Boolean time series is True, otherwise it is
        False. Linear interpolation is used to determine the time at which the state changes.
        """
        t = np.array(t)
        y = np.array(y)
        res_x = [t[0]]

        # If start on the threshold then look ahead to see the first state value
        initial_state = False  # Default state if all data is on the threshold plateau
        prev = 0
        for i, yy in enumerate(y):
            if yy != threshold:
                initial_state = yy > threshold
                prev = i
                break

        for i in range(1, len(t)):
            v = (y[prev] - threshold) * (y[i] - threshold)
            if v < 0:
                # We have a threshold crossing - interpolate where it crosses
                if prev == i-1:
                    m = (y[i]-y[prev])/(t[i]-t[prev])
                    c = y[i] - m * t[i]
                    intercept = (threshold-c)/m
                    res_x.append(intercept)
                else:
                    # We're exiting a plateau
                    res_x.append((t[i] - t[prev])/2)
                prev = i
            elif v > 0:
                prev = i

        return BooleanTimeSeries(res_x, [initial_state], t[-1])

    @staticmethod
    def relative_threshold(t, y, threshold):
        """
        Produces Boolean time series data from numerical time series data using relative
        thresholding and linear interpolation.

        Parameters
        ----------

        t : list of float, or numpy array of float
            Time points
        y : list of float, or numpy array of float
            Values corresponding to the time points.

        threshold : float
            Relative threshold.  The absolute threshold will be (max(y)-min(y)*threshold)-min(y).

        Returns
        -------

        A Boolean time series produced by thresholding the input data at the specified threshold.
        Then the value is above the threshold the Boolean time series is True, otherwise it is
        False. Linear interpolation is used to determine the time at which the state changes.
        """
        t = np.array(t)
        y = np.array(y)
        mn = y.min(axis=0)
        mx = y.max(axis=0)
        return BooleanTimeSeries.absolute_threshold(t, y, mn + threshold * (mx - mn))

    @staticmethod
    def merge(inputs):
        """
        Takes a list of BooleanTimeSeries objects and outputs two lists. The first list is the
        switch point times and the second list is a list of lists of the state variables at
        these time points.

        Parameters
        ----------

        inputs : list of BooleanTimeSeries

        Returns
        -------

        list of float, list of list of bool
            The first list is the switch point times and the second list is a list of lists of the
            state variables at these time points.
        """
        # Check all inputs have same start time
        for i in range(len(inputs)-1):
            if inputs[i].t[0] != inputs[i+1].t[0]:
                raise ValueError("Cannot merge inputs with different start times")

        x = [inputs[0].t[0]]
        y = []
        indexes = [0] * len(inputs)
        y.append(BooleanTimeSeries._get_state(indexes, inputs))
        t, indexes = BooleanTimeSeries._get_next_time(indexes, inputs)
        while t:
            x.append(t)
            y.append(BooleanTimeSeries._get_state(indexes, inputs))
            t, indexes = BooleanTimeSeries._get_next_time(indexes, inputs)

        return x, y

    @staticmethod
    def unmerge(t, y, end):
        """
        Constructs multiple BooleanTimeSeries object from lists of state variables at each time
        point.

        Parameters
        ----------

        t : list of float
            List of switch time points.
        y : list of list of bool
            List of lists of state variables at each time point.

        Returns
        -------

        list of BooleanTimeSeries:
            List of the BooleanTimeSeries data.
        """
        result = []
        num_values = len(y[0])
        for i in range(num_values):
            y_data = []
            for yy in y:
                y_data.append(yy[i])
            result.append(BooleanTimeSeries(t, y_data, end).compress())

        return result


    @staticmethod
    def _get_state(indexes, list_of_boolean_time_series):
        """
        Obtains the state vector build by following the given index for each state variable.

        Parameters
        ----------

        indexes : list int
            List of indexes into the states, one index for each state variable

        list_of_boolean_time_series : list of BooleanTimeSeries
            List of Boolean time series for each state variable.

        Returns
        -------

        list of bool
            The state vector obtained by indexing into the Boolean time series for each
            state variable.
        """
        state = []
        for i in range(len(indexes)):
            state.append(list_of_boolean_time_series[i].y[indexes[i]])
        return state

    @staticmethod
    def _get_next_time(indexes, list_of_boolean_time_series):
        """
        Gets the next switch time by following the indexes into each Boolean time series.

        Parameters
        ----------

        indexes : list int
            List of indexes into the states, one index for each state variable

        list_of_boolean_time_series : list of BooleanTimeSeries
            List of Boolean time series for each state variable.

        Returns
        -------

        float, list of int
            The first return value is the next timepoint (or None is there are no more timepoints).
            The second return value is the updated indexes.

        """
        times = []
        t = None
        for i in range(len(indexes)):
            if indexes[i] + 1 < len(list_of_boolean_time_series[i].t):
                times.append(list_of_boolean_time_series[i].t[indexes[i] + 1])

        # Return if no times found
        if not times:
            return None, None

        t = min(times)

        # Now update the indexes
        for i in range(len(indexes)):
            if indexes[i] + 1 < len(list_of_boolean_time_series[i].t):
                if BooleanTimeSeries._is_time_before_or_equal(
                        list_of_boolean_time_series[i].t[indexes[i] + 1], t):
                    indexes[i] = indexes[i]+1

        return t, indexes

    @staticmethod
    def _times_are_equal(t1, t2):
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
        return math.isclose(
            t1, t2, rel_tol=BooleanTimeSeries.rel_tol, abs_tol=BooleanTimeSeries.abs_tol)

    @staticmethod
    def _is_time_before(t1, t2):
        """
        Tests if the given time is before or equal to the simulation end time.

        Parameters
        ---------

        t1 : float
            A time point.
        t2 : float
            A time point.

        Returns
        -------

        bool
            True if the t1 is before or equal to the t2.

        """
        return t1 < t2 and not BooleanTimeSeries._times_are_equal(t1, t2)

    @staticmethod
    def _is_time_before_or_equal(t1, t2):
        """
        Tests if the given time is before or equal to the simulation end time.

        Parameters
        ---------

        t1 : float
            A time point.
        t2 : float
            A time point.

        Returns
        -------

        bool
            True if the t1 is before or equal to the t2.

        """
        return t1 < t2 or BooleanTimeSeries._times_are_equal(t1, t2)
