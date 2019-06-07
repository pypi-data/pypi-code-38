#pylint: disable=logging-fstring-interpolation
"""
Visualization of a capability region.
"""

import logging
import gc
from collections import deque

import tkinter as tk
from tkinter import ttk

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
from matplotlib.patches import Polygon

from hynet.scenario.capability import CapRegion, HalfSpace
from hynet.visual.capability.utilities import (Axis,
                                               Bound,
                                               LinearFunction,
                                               Orientation,
                                               Point)
from hynet.visual.capability.settings import SettingsView

_log = logging.getLogger(__name__)

MESSAGE_DISAPPEAR_WAIT_TIME = 2500

SAVE_FILETYPES = (
    ("png files", "*.png"), ("pdf files", "*.pdf"), ("ps files", "*.ps"),
    ("eps files", "*.eps"), ("svg files", "*.svg"), ("all files", "*.*")
)


class Window(ttk.Frame):  # pylint: disable=too-many-ancestors
    """This class creates a window that visualizes a capability region."""
    SCALING_FACTOR = 1
    CAPABILITY_REGION_COLOR = '#BBBBBB'
    HALFSPACES_COLOR = '#777777'
    POLYGON_EDGE_COLOR = '#777777'
    POLYGON_FILL_COLOR = '#BAEBAC'

    # this map stores the matplotlib lines as Axis x Bound -> line associations
    _limit_lines = {}
    # this map stores the matplotlib lines as
    # {LEFT, RIGHT} x {TOP, BOTTOM} -> line associations
    _halfspace_lines = {}
    _polygon = []
    _callback_queue = deque()

    def __init__(self, master=None, capability_region=CapRegion(), edit=True):
        super().__init__(master, padding='3 3 12 12')
        self._master = master
        self._cap_region = capability_region
        self.grid(row=0, column=0, sticky=tk.N + tk.S + tk.E + tk.W)
        self.fig = Figure(tight_layout=True)
        self._ax = self.fig.add_subplot(1, 1, 1)
        self._configure_canvas()
        self._canvas = FigureCanvasTkAgg(self.fig, master=master)
        self._canvas.show()
        self._canvas.get_tk_widget().grid(row=0, column=0, padx=0, pady=0,
                                          sticky=[tk.N, tk.S, tk.E, tk.W])
        self._limit_lines = {}
        self._halfspace_lines = {}
        self._polygon = []
        self._callback_queue = deque()

        if edit:
            self._settings_view = SettingsView(master=master,
                                               cap_region=capability_region)
            self._settings_view.container.grid(row=0, column=1,
                                               padx=(20, 0), pady=0,
                                               sticky=[tk.W, tk.E, tk.S, tk.N])
            self._setup_capabilityregion_callbacks()
            self._setup_halfspace_callbacks()
            self._settings_view.power_factor.set_callback(
                self._update_powerfactor)
            self._settings_view.error_callback = self._show_message

            self._message_label = tk.Label(master=self._master, padx=0, pady=0,
                                           anchor=tk.S, height=2, fg="red")
            self._message_label.grid(row=1, column=0, padx=10, pady=(0, 10),
                                     sticky=[tk.N, tk.S, tk.E, tk.W])

        self.columnconfigure(0, weight=1)
        self.columnconfigure(1, weight=1)
        self.rowconfigure(0, weight=1)
        self._update_view()

    def _update_powerfactor(self, value):
        try:
            self._cap_region.add_power_factor_limit(value)
            # update the values from the capability region
            self._settings_view.update_from_capability_region()
        except ValueError as error:
            self._show_message(str(error))
        self._update_view()

    def _show_message(self, message, undo_callback=None):
        def _callback_now():
            self._message_label.config(text=message)
            _log.warning(message)

            _log.debug(
                f"_callback_now: Length of queue: {len(self._callback_queue)}")
            if self._callback_queue:
                next_callback = self._callback_queue.popleft()
                self.after(MESSAGE_DISAPPEAR_WAIT_TIME, next_callback)

        def _delayed_callback():
            _log.debug(
                f"Delayed_call: Length of queue: {len(self._callback_queue)} "
                f"With callback?: {not (undo_callback is None)}")
            if undo_callback:
                undo_callback()
            self._message_label.config(text='')
            if self._callback_queue:
                next_callback = self._callback_queue.popleft()
                self.after(MESSAGE_DISAPPEAR_WAIT_TIME, next_callback)

        _log.debug(f"Length of queue: {len(self._callback_queue)}")
        if self._callback_queue:
            self._callback_queue.append(_callback_now)
            self._callback_queue.append(_delayed_callback)
        else:
            # the order is important!
            self._callback_queue.append(_delayed_callback)
            _callback_now()

    def _update_view(self):
        self._update_polygon()
        self._draw_capability_region()
        # self.draw_halfspaces()
        self._ax.relim(visible_only=True)
        self._ax.autoscale()
        self._canvas.draw()

    def _configure_canvas(self):
        self._ax.autoscale()
        self._ax.grid(True, which='both')

        self._ax.set_xlabel('P', horizontalalignment="center", x=1.0)
        y_label = self._ax.set_ylabel('Q', horizontalalignment="center", y=1.0)
        y_label.set_rotation(0)
        # turn off the right spine/ticks
        self._ax.spines['right'].set_color('none')
        # turn off the top spine/ticks
        self._ax.spines['top'].set_color('none')

        # draw axes at (0,0)
        self._ax.spines['left'].set_position(('data', 0.0))
        self._ax.spines['bottom'].set_position(('data', 0.0))

        # equally distant axes
        self._ax.axis('equal')

    def _setup_capabilityregion_callbacks(self):
        # arrow heads: http://felix11h.github.io/blog/arrowheads-matplotlib
        def _create_value_change_callback(capability_region, axis, bound):
            def _callback(value):  # pylint: disable=too-many-branches
                axis_tuple = (axis, bound)
                if axis_tuple == (Axis.REACTIVE_POWER, Bound.MIN):
                    if capability_region.q_max < value:
                        raise ValueError(
                            f"Please choose a smaller value.\n{value} "
                            f"exceeds the upper bound on reactive power.")
                    else:
                        capability_region.q_min = value
                elif axis_tuple == (Axis.REACTIVE_POWER, Bound.MAX):
                    if capability_region.q_min > value:
                        raise ValueError(
                            f"Please choose a larger value.\n{value} "
                            f"is below the lower bound on reactive power.")
                    else:
                        capability_region.q_max = value
                elif axis_tuple == (Axis.ACTIVE_POWER, Bound.MIN):
                    if capability_region.p_max < value:
                        raise ValueError(
                            f"Please choose a smaller value.\n{value} "
                            f"exceeds the upper bound on active power.")
                    else:
                        capability_region.p_min = value
                elif axis_tuple == (Axis.ACTIVE_POWER, Bound.MAX):
                    if capability_region.q_min > value:
                        raise ValueError(
                            f"Please choose a larger value.\n{value} "
                            f"is below the lower bound on active power.")
                    else:
                        capability_region.p_max = value
                else:
                    ValueError("No implementation for axis " + str(axis) +
                               " and bound " + str(bound))
                p_same = self._cap_region.p_min == self._cap_region.p_max
                q_same = self._cap_region.q_min == self._cap_region.q_max
                if p_same or q_same:
                    self._settings_view.deactivate_all_halfspaces()
                    capability_region.rt = None
                    capability_region.lt = None
                    capability_region.rb = None
                    capability_region.lb = None
                self._update_view()

            return _callback

        self._settings_view.active_power.left_entry.set_callback(
            _create_value_change_callback(
                capability_region=self._cap_region,
                axis=Axis.ACTIVE_POWER,
                bound=Bound.MIN))
        self._settings_view.active_power.right_entry.set_callback(
            _create_value_change_callback(
                capability_region=self._cap_region,
                axis=Axis.ACTIVE_POWER,
                bound=Bound.MAX))
        self._settings_view.reactive_power.left_entry.set_callback(
            _create_value_change_callback(
                capability_region=self._cap_region,
                axis=Axis.REACTIVE_POWER,
                bound=Bound.MIN))
        self._settings_view.reactive_power.right_entry.set_callback(
            _create_value_change_callback(
                capability_region=self._cap_region,
                axis=Axis.REACTIVE_POWER,
                bound=Bound.MAX))
        self._settings_view.setup_halfspace_callbacks(self._update_view)

    def _draw_capability_region(self):

        def _parallel_to_axis(parallel_to, ends, orientation):
            if not len(ends) == 2:
                raise ValueError("A line must have 2 ends.")
            if orientation is Axis.REACTIVE_POWER:
                return ([Window.SCALING_FACTOR * ends[0],
                         Window.SCALING_FACTOR * ends[1]],
                        [parallel_to, parallel_to])
            if orientation is Axis.ACTIVE_POWER:
                return ([parallel_to, parallel_to],
                        [Window.SCALING_FACTOR * ends[0],
                         Window.SCALING_FACTOR * ends[1]])
            raise ValueError("Unknown orientation: " + orientation)

        def _draw_region_part(capability_region, axis, bound):
            """
            Parameters
            ----------
            capability_region: CapRegion
                The capability region specification.
            axis: Axis
                Either Axis.POWER or Axis.REACTIVE_POWER for the active
                and reactive power, respectively.
            bound: Bound
                Bound.MIN or Bound.MAX to specify the bound.

            Returns
            -------
            The line that was added to the plot.
            """
            limits = []
            bound_value = None
            if axis is Axis.ACTIVE_POWER:
                limits = [self._cap_region.q_min,
                          self._cap_region.q_max]
                if bound is Bound.MAX:
                    bound_value = capability_region.p_max
                elif bound is Bound.MIN:
                    bound_value = capability_region.p_min
                else:
                    raise ValueError("Unsupported Bound: " + bound)
            elif axis is Axis.REACTIVE_POWER:
                limits = [self._cap_region.p_min,
                          self._cap_region.p_max]
                if bound is Bound.MAX:
                    bound_value = capability_region.q_max
                elif bound is Bound.MIN:
                    bound_value = capability_region.q_min
                else:
                    raise ValueError("Unsupported Bound: " + bound)
            points = _parallel_to_axis(bound_value, limits, axis)

            return self._ax.plot(*points,
                                 color=Window.CAPABILITY_REGION_COLOR,
                                 zorder=0)[0]

        # remove all limit lines / points
        for axis, bound in [(a, b) for a in Axis for b in Bound]:
            if (axis, bound) in self._limit_lines:
                line = self._limit_lines[(axis, bound)]
                line.remove()
                del line
                del self._limit_lines[(axis, bound)]
        if (self._cap_region.p_min == self._cap_region.p_max) and \
            (self._cap_region.q_min == self._cap_region.q_max):
            point = self._ax.plot([self._cap_region.p_min],
                                  [self._cap_region.q_min], marker='o',
                                  linestyle='--', color='r')[0]
            self._limit_lines[(Axis.ACTIVE_POWER, Bound.MIN)] = point
        elif self._cap_region.p_min == self._cap_region.p_max:
            # draw only the line of p
            line = _draw_region_part(axis=Axis.ACTIVE_POWER, bound=Bound.MIN,
                                     capability_region=self._cap_region)
            self._limit_lines[(Axis.REACTIVE_POWER, Bound.MIN)] = line
        elif self._cap_region.q_min == self._cap_region.q_max:
            line = _draw_region_part(axis=Axis.REACTIVE_POWER, bound=Bound.MIN,
                                     capability_region=self._cap_region)
            self._limit_lines[(Axis.REACTIVE_POWER, Bound.MIN)] = line
        else:
            # create the rectangular capability region lines
            for axis, bound in [(a, b) for a in Axis for b in Bound]:
                line = _draw_region_part(axis=axis, bound=bound,
                                         capability_region=self._cap_region)
                self._limit_lines[(axis, bound)] = line

    def _draw_halfspaces(self):
        halfspace_options = {
            (Orientation.RIGHT, Orientation.TOP): self._cap_region.rt,
            (Orientation.LEFT, Orientation.TOP): self._cap_region.lt,
            (
                Orientation.RIGHT,
                Orientation.BOTTOM): self._cap_region.rb,
            (Orientation.LEFT, Orientation.BOTTOM): self._cap_region.lb}
        for (p, q), halfspace in halfspace_options.items():
            line_tuple = (p, q)
            line = self._halfspace_lines.get(line_tuple)
            if not halfspace and line is None:
                continue

            # now we remove any lines we need to remove as halfspace is None
            # but a line for this halfspace still exists
            # but during initialising the line is still None
            if line:
                del self._halfspace_lines[line_tuple]
                line.remove()
                del line

            # and add a line back, if the halfspace exists
            if halfspace:
                points = self._halfspace_points(p_orientation=p,
                                                q_orientation=q)
                line = self._ax.plot(*points,
                                     color=Window.HALFSPACES_COLOR,
                                     zorder=0)[0]
                self._halfspace_lines[line_tuple] = line

    def _halfspace_points(self, p_orientation, q_orientation):
        #   l/t     ^ q_max   r/t
        #           |
        # p_min     |         p_max
        # p --------|-------->
        #           |
        #           |
        #   l/b     q q_min   r/b
        if q_orientation is Orientation.TOP:
            q = self._cap_region.q_max
            possible_halfspaces = (
                self._cap_region.lt, self._cap_region.rt)
        elif q_orientation is Orientation.BOTTOM:
            q = self._cap_region.q_min
            possible_halfspaces = (
                self._cap_region.lb, self._cap_region.rb)
        else:
            raise ValueError(str(q_orientation) +
                             " is not allowed for q_orientation.")

        if p_orientation is Orientation.RIGHT:
            p = self._cap_region.p_max
            halfspace = possible_halfspaces[1]
        elif p_orientation is Orientation.LEFT:
            p = self._cap_region.p_min
            halfspace = possible_halfspaces[0]
        else:
            raise ValueError(str(p_orientation) +
                             " is not allowed for p_orientation.")
        if halfspace is None:
            return None

        # now we can be sure that the halfspace exists and we have
        # the right values
        limits = Point(p, q)
        line_functions = LinearFunction(halfspace, limits)

        x_points = [limits.p * Window.SCALING_FACTOR, limits.p,
                    line_functions.f_1(limits.q),
                    line_functions.f_1(limits.q * Window.SCALING_FACTOR)]
        y_points = [line_functions.f(limits.p * Window.SCALING_FACTOR),
                    line_functions.f(limits.p), limits.q,
                    limits.q * Window.SCALING_FACTOR]
        return x_points, y_points

    def _setup_halfspace_callbacks(self):
        halfspace_options = {(Orientation.RIGHT, Orientation.TOP):
                                 self._settings_view.rt_half_space,
                             (Orientation.LEFT, Orientation.TOP):
                                 self._settings_view.lt_half_space,
                             (Orientation.RIGHT, Orientation.BOTTOM):
                                 self._settings_view.rb_half_space,
                             (Orientation.LEFT, Orientation.BOTTOM):
                                 self._settings_view.lb_half_space}

        def _create_callback(p_orientation, q_orientation, slope):
            def _callback(value):
                # update the value on the capability region
                def _get_new_halfspace(old):
                    if old:
                        if slope:
                            return HalfSpace(slope=value, offset=old.offset)
                        return HalfSpace(slope=old.slope, offset=value)
                    return None

                line_tuple = (p_orientation, q_orientation)
                try:
                    if line_tuple == (Orientation.RIGHT, Orientation.TOP):
                        self._cap_region.rt = _get_new_halfspace(
                            self._cap_region.rt)
                    elif line_tuple == (Orientation.RIGHT, Orientation.BOTTOM):
                        self._cap_region.rb = _get_new_halfspace(
                            self._cap_region.rb)
                    elif line_tuple == (Orientation.LEFT, Orientation.TOP):
                        self._cap_region.lt = _get_new_halfspace(
                            self._cap_region.lt)
                    elif line_tuple == (Orientation.LEFT, Orientation.BOTTOM):
                        self._cap_region.lb = _get_new_halfspace(
                            self._cap_region.lb)
                    else:
                        raise ValueError(
                            str(line_tuple) + " is not a valid configuration!")
                except ValueError as error:
                    half_plane = halfspace_options[line_tuple]
                    halfspace = None
                    if line_tuple == (Orientation.RIGHT, Orientation.TOP):
                        halfspace = self._cap_region.rt
                    elif line_tuple == (Orientation.RIGHT, Orientation.BOTTOM):
                        halfspace = self._cap_region.rb
                    elif line_tuple == (Orientation.LEFT, Orientation.TOP):
                        halfspace = self._cap_region.lt
                    elif line_tuple == (Orientation.LEFT, Orientation.BOTTOM):
                        halfspace = self._cap_region.lb

                    if slope:
                        undo = half_plane.right_entry.error_state(
                            old_value=halfspace.slope)
                    else:
                        undo = half_plane.left_entry.error_state(
                            old_value=halfspace.offset)
                    self._show_message(str(error), undo)
                self._update_view()

            return _callback

        for (p, q), descriptive_entry in halfspace_options.items():
            left_callback = _create_callback(p_orientation=p, q_orientation=q,
                                             slope=False)
            right_callback = _create_callback(p_orientation=p, q_orientation=q,
                                              slope=True)

            descriptive_entry.left_entry.set_callback(left_callback)
            descriptive_entry.right_entry.set_callback(right_callback)

    def _update_polygon(self):
        try:
            polygon_vertices = self.compute_polygon_vertices(self._cap_region)
        except ValueError as error:
            self._show_message(str(error))
        # update the polygon
        if self._polygon:
            for polygon in self._polygon:
                polygon.remove()
            self._polygon = []

        if polygon_vertices:
            polygon = Polygon(np.array(polygon_vertices),
                              closed=True,
                              facecolor=Window.POLYGON_FILL_COLOR,
                              zorder=0)
            self._ax.add_patch(polygon)
            self._polygon.append(polygon)
            polygon_outline = Polygon(np.array(polygon_vertices),
                                      closed=True,
                                      edgecolor=Window.POLYGON_EDGE_COLOR,
                                      facecolor='none',
                                      zorder=4)
            self._ax.add_patch(polygon_outline)
            self._polygon.append(polygon_outline)

    def display_operating_point(self, point):
        """
        Display an operating point in the P/Q-plane of the capability region.

        Parameters
        ----------
        point: tuple(p,q)
            This tuple represents the operating point as a (p,q)-tuple of
            floats.
        """
        self._ax.plot([point[0]], [point[1]], label='Operating Point',
                      marker='+', linestyle='--', color='r')
        self._update_view()

    @staticmethod
    def compute_polygon_vertices(cap_region):
        """
        Compute the vertices of the capability region polygon.

        This function computes the intersections of the four lines that delimit
        the capability region. The algorithm starts with the left-top half
        space and continues clock-wise with the other half-spaces.

        The algorithm assumes that ``p_max != p_min`` and ``q_max != q_min``.
        Furthermore, the assumptions on the slopes and offsets must be
        satisfied as well. If the preconditions are met, the function returns
        a list of all vertices that specify the polygon, in a clock-wise
        ordering.

        Parameters
        ----------
        cap_region: CapRegion
            The capability region that shall be drawn.

        Returns
        -------
        list[tuple(p,q)]
            List of polygon vertices.
        """
        # pylint: disable=too-many-locals,too-many-statements,too-many-branches

        # l/t     ^ q_max   r/t
        #           |
        # p_min     |         p_max
        # p --------|-------->
        #           |
        #           |
        #   l/b     q q_min   r/b
        # start with lt and compute the q value with p_min
        # then continue with the intersection / the top points of lt and rt.
        # followed by the p_max point of rt, then do the same for the bottom
        # part
        # Remember that the halfspaces could be empty!
        # The offset is required to be positive!
        all_top_halfspaces_present = cap_region.lt is not None and \
                                     cap_region.rt is not None
        all_bottom_halfspaces_present = cap_region.lb is not None and \
                                        cap_region.rb is not None
        polygon_vertices = []
        limits_lt = Point(cap_region.p_min, cap_region.q_max)
        limits_rt = Point(cap_region.p_max,
                          cap_region.q_max)
        limits_rb = Point(cap_region.p_max,
                          cap_region.q_min)
        limits_lb = Point(cap_region.p_min,
                          cap_region.q_min)

        def _point_in_bounds(point):
            q_in_bounds = cap_region.q_min <= point.q <= cap_region.q_max
            p_in_bounds = cap_region.p_min <= point.p <= cap_region.p_max
            return q_in_bounds and p_in_bounds

        def _compute_and_limit(linear_function, limits, compute_coordinate):
            if compute_coordinate is Axis.ACTIVE_POWER:
                point = Point(linear_function.f_1(limits.q), limits.q)
                if not _point_in_bounds(point):
                    point = Point(limits.p, linear_function.f(limits.p))
            elif compute_coordinate is Axis.REACTIVE_POWER:
                point = Point(limits.p, linear_function.f(limits.p))
                if not _point_in_bounds(point):
                    point = Point(linear_function.f_1(limits.q), limits.q)
            else:
                raise ValueError(f"{compute_coordinate} is not implemented!")
            if not _point_in_bounds(point):
                _log.warning(f"Point {point} for halfspace with offset "
                             f"{linear_function.offset} and "
                             f"{linear_function.slope} slope is not in "
                             f"the bounds of the capability region. "
                             f"We will limit it to the limits of the "
                             f"capability region.")
                return limits
            return point

        if all_top_halfspaces_present:
            plf_lt = LinearFunction(cap_region.lt, limits_lt)
            plf_rt = LinearFunction(cap_region.rt, limits_rt)

            polygon_vertices.append(
                _compute_and_limit(plf_lt, limits_lt, Axis.REACTIVE_POWER))
            intersection = plf_lt.intersect_with(plf_rt)
            if intersection:
                # should be the case in all cases were the halfspace is present
                if _point_in_bounds(intersection):
                    polygon_vertices.append(intersection)
                else:
                    # compute the capped intersection with q_max (as the
                    # intersection of the two halfspace function is out of bounds
                    lt_top_point = _compute_and_limit(plf_lt, limits_lt,
                                                      Axis.ACTIVE_POWER)
                    rt_top_point = _compute_and_limit(plf_rt, limits_rt,
                                                      Axis.ACTIVE_POWER)
                    polygon_vertices.append(lt_top_point)
                    polygon_vertices.append(rt_top_point)
            else:
                message = "The top halfspaces are parallel, " \
                          "please check your input values!"
                raise ValueError(message)
            polygon_vertices.append(
                _compute_and_limit(plf_rt, limits_rt, Axis.REACTIVE_POWER))
        else:
            if cap_region.lt:
                plf = LinearFunction(cap_region.lt, limits_lt)
                lt_top_point = _compute_and_limit(plf, limits_lt,
                                                  Axis.REACTIVE_POWER)
                lt_bottom_point = _compute_and_limit(plf, limits_lt,
                                                     Axis.ACTIVE_POWER)
                rt_top_point = _compute_and_limit(plf, limits_rt,
                                                  Axis.REACTIVE_POWER)

                polygon_vertices.append(lt_top_point)
                polygon_vertices.append(lt_bottom_point)
                # append replacement point for rt
                if rt_top_point == lt_bottom_point:
                    polygon_vertices.append(limits_rt)
                else:
                    polygon_vertices.append(rt_top_point)

            elif cap_region.rt:
                plf = LinearFunction(cap_region.rt, limits_rt)
                # append replacement point for lt
                lt_top_point = _compute_and_limit(plf, limits_lt,
                                                  Axis.REACTIVE_POWER)
                rt_top_point = _compute_and_limit(plf, limits_rt,
                                                  Axis.ACTIVE_POWER)
                rt_bottom_point = _compute_and_limit(plf, limits_rt,
                                                     Axis.REACTIVE_POWER)
                if lt_top_point == rt_top_point:
                    polygon_vertices.append(limits_lt)
                else:
                    polygon_vertices.append(lt_top_point)

                polygon_vertices.append(rt_top_point)
                polygon_vertices.append(rt_bottom_point)
            else:
                polygon_vertices.append(limits_lt)
                polygon_vertices.append(limits_rt)

        if all_bottom_halfspaces_present:
            # p_min     |         p_max
            # p --------|-------->
            #           |
            #           |
            #   l/b     q q_min   r/b
            plf_rb = LinearFunction(cap_region.rb, limits_rb)
            plf_lb = LinearFunction(cap_region.lb, limits_lb)

            polygon_vertices.append(
                _compute_and_limit(plf_rb, limits_rb, Axis.REACTIVE_POWER))

            # compute the intersection of the two functions and determine if it
            # is still in bounds (i.e., the q is smaller than q_min
            intersection = plf_rb.intersect_with(plf_lb)
            if intersection:
                if _point_in_bounds(intersection):
                    polygon_vertices.append(intersection)
                else:
                    # first intersect rb with q_min and then lb
                    point_limited_rb_intersection = \
                        _compute_and_limit(plf_rb, limits_rb,
                                           Axis.ACTIVE_POWER)
                    polygon_vertices.append(point_limited_rb_intersection)
                    point_limited_lb_intersection = \
                        _compute_and_limit(plf_lb, limits_lb,
                                           Axis.ACTIVE_POWER)
                    polygon_vertices.append(point_limited_lb_intersection)
            else:
                message = "The bottom halfspaces are parallel, " \
                          "please check your input values!"
                raise ValueError(message)
            lb_end = _compute_and_limit(plf_lb, limits_lb, Axis.REACTIVE_POWER)
            polygon_vertices.append(lb_end)
        else:
            if cap_region.rb:
                plf_rb = LinearFunction(cap_region.rb, limits_rb)
                point_rb_top = _compute_and_limit(plf_rb, limits_rb,
                                                  Axis.REACTIVE_POWER)
                point_rb_bottom = _compute_and_limit(plf_rb, limits_rb,
                                                     Axis.ACTIVE_POWER)
                # compute replacement lb points
                point_lb_bottom = _compute_and_limit(plf_rb, limits_lb,
                                                     Axis.REACTIVE_POWER)
                polygon_vertices.append(point_rb_top)
                polygon_vertices.append(point_rb_bottom)

                if point_rb_bottom == point_lb_bottom:
                    polygon_vertices.append(limits_lb)
                else:
                    polygon_vertices.append(point_lb_bottom)

            elif cap_region.lb:
                plf_lb = LinearFunction(cap_region.lb, limits_lb)
                # limit value to bounds
                # compute replacement rb points
                point_rb_bottom = _compute_and_limit(plf_lb, limits_rb,
                                                     Axis.REACTIVE_POWER)
                point_lb_bottom = _compute_and_limit(plf_lb, limits_lb,
                                                     Axis.ACTIVE_POWER)
                point_lb_top = _compute_and_limit(plf_lb, limits_lb,
                                                  Axis.REACTIVE_POWER)

                if point_rb_bottom == point_lb_bottom:
                    polygon_vertices.append(limits_rb)
                else:
                    polygon_vertices.append(point_rb_bottom)
                polygon_vertices.append(point_lb_bottom)
                polygon_vertices.append(point_lb_top)
            else:
                polygon_vertices.append(limits_rb)
                polygon_vertices.append(limits_lb)

        return polygon_vertices

    @staticmethod
    def show(capability_region, edit=True, operating_point=None):
        """
        Create and show a capability region visualizer window.

        Parameters
        ----------
        capability_region: CapRegion
        edit: bool, optional
            If True (default), editing of the specified capability region is
            enabled.
        operating_point: tuple(p,q), optional
            If provided, this operating point is shown by a marker in the
            P/Q-plane.
        """
        # If we do not close the open figures, the settings view does not work
        # properly, strangely...maybe we try to find another fix sometime :)
        plt.close('all')

        root = tk.Tk()
        root.title("Capability Region Visualizer - Press [ESC] to exit.")
        tk.Grid.rowconfigure(root, 0, weight=1)
        tk.Grid.columnconfigure(root, 0, weight=1)
        app = Window(root, capability_region, edit)
        if operating_point:
            app.display_operating_point(operating_point)

        # Bind the escape key to exit the application
        def _quit(event):  # pylint: disable=unused-argument
            root.quit()     # Stop the main loop
            root.destroy()  # Close the window
        root.bind("<Escape>", _quit)

        # Set up the "Export as image" button
        button_frame = tk.Frame(root, padx=0, pady=0, bg="white")

        def _save_figure():
            from pathlib import Path
            from tkinter import filedialog
            file_path = filedialog.asksaveasfilename(initialdir=Path.home(),
                                                     filetypes=SAVE_FILETYPES,
                                                     title="Export as image...")
            if file_path:
                app.fig.savefig(file_path)

        save_fig = tk.Button(button_frame,
                             text='Export as image...',
                             command=_save_figure,
                             padx=10,
                             bg="white")
        save_fig.grid(row=0, column=0, sticky=[tk.N, tk.S, tk.E, tk.W])

        if edit:
            button_frame.grid(row=1, column=1, padx=(20, 0), pady=(15, 10),
                              sticky=[tk.N, tk.S, tk.E, tk.W])
            root.update()
            root.minsize(width=750, height=610)
        else:
            button_frame.grid(row=1, column=0, padx=10, pady=(0, 10),
                              sticky=tk.E)
            root.update()
            root.minsize(width=500, height=350)

        while True:
            try:
                root.mainloop()
                break
            except UnicodeDecodeError:
                # See https://stackoverflow.com/questions/16995969/
                # inertial-scrolling-in-mac-os-x-with-tkinter-and-python
                pass

        # REMARK: After closing the window, we received runtime errors that
        # stated "RuntimeError: main thread is not in main loop". This error
        # appears when tk is not run in the main thread, see
        # https://stackoverflow.com/questions/14694408/runtimeerror-main-thread-is-not-in-main-loop
        # However, GUI was run in the main thread, but the garbage collection
        # of the window by one of the threads spawn during the OPF computation,
        # see also
        # https://stackoverflow.com/questions/44781806/tkinter-objects-being-garbage-collected-from-the-wrong-thread
        # To avoid this issue, we enforce the garbage collection in the main
        # thread here:
        del root
        gc.collect()
