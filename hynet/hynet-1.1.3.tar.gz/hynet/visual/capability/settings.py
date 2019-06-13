"""
Settings view to edit parameters in the capability region visualizer.
"""

import logging
from re import compile as compile_regex

import tkinter as tk
from tkinter import ttk

from hynet.scenario.capability import HalfSpace, CapRegion
from hynet.visual.capability.utilities import Orientation

_log = logging.getLogger(__name__)

DIGITS = 5


class SettingsView(tk.ttk.Frame):  # pylint: disable=too-many-ancestors
    """
    Settings view to edit parameters in the capability region visualizer.
    """
    def __init__(self, master=None, cap_region=CapRegion()):
        super(SettingsView, self).__init__(master)
        self.error_callback = None
        self.container = tk.Frame(master, padx=0, pady=0, bg="white")
        self.capability_region = cap_region
        power_tuple = (cap_region.p_min, cap_region.p_max)
        reactive_tuple = (cap_region.q_min, cap_region.q_max)
        # active power view (i.e., first row)
        self.active_power = ValueView(self.container,
                                      'Active power:',
                                      left_value_name='Minimum:',
                                      right_value_name='Maximum:',
                                      initial_value_tuple=power_tuple)
        self.active_power.container.grid(row=0, column=0, sticky=[tk.W, tk.E])

        # reactive power view (i.e., second row)
        self.reactive_power = ValueView(self.container,
                                        'Reactive power:',
                                        left_value_name='Minimum:',
                                        right_value_name='Maximum:',
                                        initial_value_tuple=reactive_tuple)
        self.reactive_power.container.grid(row=1, column=0,
                                           sticky=[tk.W, tk.E])

        # halfplane views (i.e., third to sixth row)
        self.rt_half_space = ValueView(self.container,
                                       'Right-top half-space:',
                                       initial_value_tuple=cap_region.rt,
                                       checkbox_state=cap_region.rt is not None)
        self.rt_half_space.container.grid(row=2, column=0,
                                          sticky=[tk.W, tk.E])

        self.rb_half_space = ValueView(self.container,
                                       'Right-bottom half-space:',
                                       initial_value_tuple=cap_region.rb,
                                       checkbox_state=cap_region.rb is not None)
        self.rb_half_space.container.grid(row=3, column=0,
                                          sticky=[tk.W, tk.E])

        self.lt_half_space = ValueView(self.container,
                                       'Left-top half-space:',
                                       initial_value_tuple=cap_region.lt,
                                       checkbox_state=cap_region.lt is not None)
        self.lt_half_space.container.grid(row=4, column=0,
                                          sticky=[tk.W, tk.E])

        self.lb_half_space = ValueView(self.container,
                                       'Left-bottom half-space:',
                                       initial_value_tuple=cap_region.lb,
                                       checkbox_state=cap_region.lb is not None)
        self.lb_half_space.container.grid(row=5, column=0,
                                          sticky=[tk.W, tk.E])

        self.power_factor = PowerFactorView(self.container)
        self.power_factor.container.grid(row=6, column=0, sticky=[tk.W, tk.E])
        spacer = tk.Frame(self.container, bg="white")
        spacer.grid(row=7, column=0, sticky=[tk.W, tk.E, tk.S, tk.N])

        self.rowconfigure(7, weight=1)

        # setup all error_callbacks
        for value_view in [self.lt_half_space,
                           self.lb_half_space,
                           self.rt_half_space,
                           self.rb_half_space, self.active_power,
                           self.reactive_power]:
            value_view.error_callback = self._proxy_error_callback

    def setup_halfspace_callbacks(self, update_view_callback):
        """
        Set the callback that updates the view with changes of the half-spaces.

        Parameters
        ----------
        update_view_callback: function
            This function is called when the checkbox is (de)activated and
            should update/reload the view of the capability region.
        """
        def _create_callback(value_view, cap_region, orientation_tuple):
            def _callback(value):
                if value:
                    slope = value_view.right_entry.get_value()
                    offset = value_view.left_entry.get_value()
                    new_halfspace = HalfSpace(slope=slope, offset=offset)
                else:
                    new_halfspace = None
                active_power, reactive_power = orientation_tuple
                raise_error = False
                try:
                    if active_power is Orientation.RIGHT and \
                            reactive_power is Orientation.TOP:
                        cap_region.rt = new_halfspace
                    elif active_power is Orientation.RIGHT and \
                            reactive_power is Orientation.BOTTOM:
                        cap_region.rb = new_halfspace
                    elif active_power is Orientation.LEFT and \
                            reactive_power is Orientation.TOP:
                        cap_region.lt = new_halfspace
                    elif active_power is Orientation.LEFT and \
                            reactive_power is Orientation.BOTTOM:
                        cap_region.lb = new_halfspace
                    else:
                        raise_error = True
                except ValueError as halfspace_invalid_error:
                    # halfspace is invalid and thus capregion.(l|r)(t|b) = x
                    # raises an error => load the values of the capregion into
                    # the visual again / reset the user's input
                    self._proxy_error_callback(
                        halfspace_invalid_error,
                        undo_callback=self.update_from_capability_region)
                if raise_error:
                    raise ValueError(
                        f"Unhandled case: ({active_power}, {reactive_power}")
                update_view_callback()

            return _callback

        self.lt_half_space.callback = _create_callback(
            self.lt_half_space, self.capability_region,
            (Orientation.LEFT, Orientation.TOP))
        self.lb_half_space.callback = _create_callback(
            self.lb_half_space, self.capability_region,
            (Orientation.LEFT, Orientation.BOTTOM))
        self.rt_half_space.callback = _create_callback(
            self.rt_half_space, self.capability_region,
            (Orientation.RIGHT, Orientation.TOP))
        self.rb_half_space.callback = _create_callback(
            self.rb_half_space, self.capability_region,
            (Orientation.RIGHT, Orientation.BOTTOM))

    def deactivate_all_halfspaces(self):
        """
        Deactivate all checkboxes and, therewith, remove all half-spaces.
        """
        self.lt_half_space.checkbox_value.set(False)
        self.lb_half_space.checkbox_value.set(False)
        self.rt_half_space.checkbox_value.set(False)
        self.rb_half_space.checkbox_value.set(False)

    def update_from_capability_region(self):
        """
        Update the views with the (possibly) changed capability region.
        """
        self.lt_half_space.update_from_capability_region(
            self.capability_region.lt)
        self.lb_half_space.update_from_capability_region(
            self.capability_region.lb)
        self.rt_half_space.update_from_capability_region(
            self.capability_region.rt)
        self.rb_half_space.update_from_capability_region(
            self.capability_region.rb)

    def _proxy_error_callback(self, message, undo_callback=None):
        if self.error_callback:
            # pylint: disable=not-callable
            self.error_callback(message, undo_callback)
        else:
            raise ValueError("Received an error call, "
                             "but no callback is configured.")


class PowerFactorView(tk.ttk.Frame):  # pylint: disable=too-many-ancestors
    """View for setting the power factor limit."""
    def __init__(self, master=None):
        super().__init__(master)
        self.container = tk.Frame(master, padx=0, pady=0, bg="white")
        self._title = tk.Label(self.container,
                               text="Set power factor:",
                               anchor=tk.SW,
                               pady=1,
                               bg="white")
        self._title.grid(row=0, column=0, columnspan=2, sticky=[tk.W, tk.E])
        self._callback = lambda x: x
        self._value = tk.StringVar()
        self._entry = tk.Entry(self.container,
                               textvariable=self._value,
                               bg="white",
                               width=10)
        self._entry.grid(row=1, column=0, padx=(25, 5), sticky=(tk.W, tk.E))

        self._trigger = tk.Button(self.container,
                                  text="Apply",
                                  padx=5,
                                  command=self._proxy_callback,
                                  bg="white",
                                  width=10)
        self._trigger.grid(row=1, column=1, padx=0, pady=0,
                           sticky=(tk.W, tk.E, tk.S, tk.N))

    def _proxy_callback(self):
        value = self._value.get()
        if not value:
            return
        try:
            self._callback(float(value))
        except ValueError:
            _log.warning(value + " is not a float!")
        self._entry.delete(0, tk.END)

    def set_callback(self, callback_function):
        """
        Set the callback for updating the power factor limit.

        Parameters
        ----------
        callback_function: function
            Function that takes the power factor as an argument and updates
            the capability region.
        """
        self._callback = callback_function


class ValueView(tk.ttk.Frame):  # pylint: disable=too-many-ancestors
    """
    Container view for two descriptive entries.

    Furthermore, the value view handles the update of the associated half-space
    (if provided) as well as the error and update callbacks.
    """
    callback = None

    def __init__(self, master=None, name='Unnamed ValueView',
                 right_value_name='Slope:', left_value_name='Offset:',
                 initial_value_tuple=(0, 0), checkbox_state=None):
        super(ValueView, self).__init__(master)
        self.error_callback = None
        if initial_value_tuple:
            left, right = initial_value_tuple
        else:
            left, right = (0.0, 0.0)
        self.container = tk.Frame(master, padx=5, pady=5, bg='white')

        if checkbox_state is None:
            self._title = tk.Label(self.container,
                                   anchor=tk.SW,
                                   text=name,
                                   bg="white")
        else:
            self.checkbox_value = tk.BooleanVar()
            self.checkbox_value.set(checkbox_state)
            self._title = tk.Checkbutton(self.container,
                                         text=name,
                                         variable=self.checkbox_value,
                                         command=self._proxy_callback,
                                         anchor=tk.SW,
                                         bg="white")

        self._title.grid(row=0, column=0, columnspan=2,
                         padx=0, pady=0, sticky=[tk.W, tk.E])

        self.left_entry = DescriptiveEntry(self.container, left_value_name,
                                           alignment=tk.VERTICAL, value=left)
        self.left_entry.container.grid(row=1, column=0, padx=(20, 5), pady=0,
                                       sticky=[tk.W, tk.E])

        self.right_entry = DescriptiveEntry(self.container, right_value_name,
                                            alignment=tk.VERTICAL,
                                            value=right)
        self.right_entry.container.grid(row=1, column=1, padx=(0, 5), pady=0,
                                        sticky=[tk.W, tk.E])

        self.left_entry.error_callback = self._proxy_error_callback
        self.right_entry.error_callback = self._proxy_error_callback

    def _proxy_error_callback(self, message, undo_callback=None):
        if self.error_callback:
            # pylint: disable=not-callable
            self.error_callback(message, undo_callback)
        else:
            raise ValueError("Received an error call, "
                             "but no callback is configured.")

    def _proxy_callback(self):
        if self.callback:
            try:
                # pylint: disable=not-callable
                self.callback(self.checkbox_value.get())
            except ValueError as error:
                self._proxy_error_callback(str(error))
        else:
            raise ValueError("Received a call, but no callback is configured.")

    def update_from_capability_region(self, halfspace):
        """
        Updates this view based on the provided half-space specification.

        Parameters
        ----------
        halfspace: HalfSpace
            The half-space associated with this value view.
        """
        if halfspace:
            left, right = halfspace
            self.left_entry.reset_to_normal_state(round(left, DIGITS))
            self.right_entry.reset_to_normal_state(round(right, DIGITS))
            self.checkbox_value.set(True)
        else:
            self.checkbox_value.set(False)


class DescriptiveEntry(ttk.Frame):  # pylint: disable=too-many-ancestors
    """Container that bundles a label with an input field."""
    VALIDATION_REGEX = compile_regex(r'^[+-]?([0-9]*[.])?[0-9]+$')

    def __init__(self, master=None, name='Label', alignment=tk.HORIZONTAL,
                 value=0.0):
        super(DescriptiveEntry, self).__init__(master)

        self.container = tk.Frame(master, padx=0, pady=0, bg="white")
        self._label = tk.Label(self.container,
                               text=name,
                               anchor=tk.SW,
                               bg="white",
                               width=10)
        self._label.grid(row=0, column=0, padx=0, pady=0)
        self._value = tk.StringVar(value=value)
        self._last_value = value
        self._validator = (self.register(self._validation_callback), '%P')

        self._entry = tk.Entry(self.container,
                               textvariable=self._value,
                               validate="focus",
                               validatecommand=self._validator,
                               bg="white",
                               width=10)

        if alignment is tk.HORIZONTAL:
            self._entry.grid(row=0, column=1, padx=0, pady=0, sticky=tk.W)
        else:
            self._entry.grid(row=1, column=0, padx=0, pady=0, sticky=tk.W)

    def _validation_callback(self, new_text):
        if self.VALIDATION_REGEX.match(new_text):
            return True

        undo = self.error_state()
        message = f"{new_text} is not a valid number!"
        self._proxy_error_callback(message, undo_callback=undo)
        _log.warning(message)
        return False

    def error_state(self, old_value=None):
        """
        Set the foreground to red and return the callback to undo this change.

        Parameters
        ----------
        old_value: float
            If this value is set, then the value of the input component is set
            to this value when this callback is called.

        Returns
        -------
        function
            Callback to undo this change (set the foreground back to black).
        """
        self._entry.configure(foreground='red')
        return lambda: self.reset_to_normal_state(old_value)

    def reset_to_normal_state(self, old_value=None):
        """
        Reset the element to the normal state (black font on white background).

        Parameters
        ----------
        old_value: float
            If this value is set, then the value of the input component is set
            to this value when this callback is called.
        """
        self._entry.configure(foreground='black')
        if old_value:
            self._value.set(old_value)
            self._last_value = old_value

    def _proxy_error_callback(self, message, undo_callback=None):
        if self.error_callback:
            self.error_callback(message, undo_callback)
        else:
            raise ValueError("Received an error call, "
                             "but no callback is configured.")

    def set_callback(self, callback):
        """
        Set a callback that listens for value changes.

        Parameters
        ----------
        callback: function
            The function that should be called when a value has changed.
        """

        def _get_value(*_args):
            try:
                value = float(self._value.get())
                # the order is important as the callback is used to check for
                # conformance of the new value!
                callback(value)
                self._last_value = value
            except ValueError as error:
                undo = self.error_state(old_value=self._last_value)
                self._proxy_error_callback(str(error), undo_callback=undo)

        self._entry.bind("<FocusOut>", _get_value)

    def get_value(self):
        """
        Return the current value of the field.

        Returns
        -------
        float
        """
        try:
            value = float(self._value.get())
        except ValueError:
            value = self._last_value
        return value

    def set_value(self, value):
        """
        Set the value for the field.

        Parameters
        ----------
        value: float or str
        """
        self._value.set(value)
