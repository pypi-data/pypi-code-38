# coding: utf8
# Copyright (c) 2013, 2017, Combine Control Systems AB
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#     * Redistributions of source code must retain the above copyright
#       notice, this list of conditions and the following disclaimer.
#     * Redistributions in binary form must reproduce the above copyright
#       notice, this list of conditions and the following disclaimer in the
#       documentation and/or other materials provided with the distribution.
#     * Neither the name of the Combine Control Systems AB nor the
#       names of its contributors may be used to endorse or promote products
#       derived from this software without specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
# ARE DISCLAIMED.
# IN NO EVENT SHALL COMBINE CONTROL SYSTEMS AB BE LIABLE FOR ANY
# DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES
# (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
# LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND
# ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
# (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
# SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
"""
Interpolate timeseries to a single timebasis. The new timebasis can
either be an existing timebasis in the adaf-file or a timebasis with a timestep
defined by the user. The timeseries that will be interpolated are selected in a
list. The output file will contain a single system and raster with all the
chosen timeseries.
"""
from __future__ import division, print_function

import collections

import six
import numpy as np
from scipy.interpolate import interp1d as scinterp

from sympathy.api import node_helper
from sympathy.api import node as synode
from sympathy.api.nodeconfig import Port, Ports, Tag, Tags, adjust
from sympathy.api.exceptions import SyDataError, SyConfigurationError, sywarn
from sympathy.api import dtypes
from sympathy.api import qt as qt_compat
QtGui = qt_compat.import_module('QtGui')
QtCore = qt_compat.import_module('QtCore')


_METHODS = ['zero', 'nearest', 'linear', 'quadratic', 'cubic']


def _method_wrapper(f):
    def inner(self, signal):
        dtype = signal.dtype
        if not len(self._source_basis):
            return np.ma.masked_all(self._target_basis.shape, dtype=dtype)
        if dtype.kind in ('m', 'M'):
            signal = signal.astype(float)
        result = f(self, signal)
        if dtype.kind in ('m', 'M'):
            return result.astype(dtype)
        return result
    return inner


class RasterResampler(object):
    def __init__(self):
        self._has_warned_about_missing_values = False

    def new_raster(self, source_basis, target_basis):
        """Start working on a new raster."""
        # np.interp can't handle some types. Notably it can't handle datetimes.
        self._time_reference = None
        self._source_basis = self._to_float(source_basis)
        self._target_basis = self._to_float(target_basis)

        # Base cache variables used for all interpolation methods:
        self._i = None
        self._left = None
        self._right = None
        self._mask = None
        # Cache variables used for specific interpolation methods:
        self._nearest_i = None
        self._zero_i = None
        self._linear_i = None
        self._linear_alpha = None
        self._higher = False

    def _to_float(self, basis):
        """Convert datetime bases to float."""
        if basis.dtype.kind == 'M':
            if self._time_reference is None:
                self._time_reference = basis[0]
            timeunit = np.timedelta64(1, 'us')
            return (basis - self._time_reference) / timeunit
        return basis

    def get_method(self, signal, selected_methods):
        """
        Return a function that can be used to interpolate signal to the current
        raster.
        """
        bool_method, int_method, float_method = selected_methods

        kind = signal.dtype.kind
        if kind in ('b', 'S', 'U'):
            selected_method = bool_method
        elif kind in ('i', 'u'):
            selected_method = int_method
        else:
            selected_method = float_method

        if self._source_basis.size == 1 and selected_method not in (
                'zero', 'nearest'):
            # Signals with one sample can only be resampled using 'nearest' or
            # 'zero'.
            # sywarn("Can't interpolate signal with one sample using method "
            #        "'{}', falling back to method 'nearest'".format(
            #            selected_method))
            selected_method = 'nearest'

        if selected_method == 'zero':
            return self.zero
        elif selected_method == 'nearest':
            return self.nearest
        elif selected_method == 'linear':
            return self.linear
        elif selected_method == 'quadratic':
            return self.quadratic
        elif selected_method == 'cubic':
            return self.cubic
        else:
            raise ValueError(
                "Unknown interpolation method '{}'".format(selected_method))

    def _interp_indices(self):
        """
        Calculate and cache the common interpolation steps for the current
        raster. Each interpolation method will refine and use these results.
        """
        if self._i is not None:
            return

        LEFT, RIGHT = -1, -2
        old_i = np.arange(len(self._source_basis))
        self._i = np.interp(self._target_basis, self._source_basis, old_i,
                            left=LEFT, right=RIGHT)
        self._left = self._i == LEFT
        self._right = self._i == RIGHT
        self._mask = np.logical_or(self._left, self._right)

        # Set extrapolated values to what is needed in methods zero and
        # nearest. Other methods mask these values anyways.
        self._i[self._left] = 0
        self._i[self._right] = -1

        # Make it easier to check if any values are masked.
        if not np.any(self._left):
            self._left = None
        if not np.any(self._mask):
            self._mask = None

    @_method_wrapper
    def zero(self, signal):
        """Nearest preceding samples."""
        if self._zero_i is None:
            self._interp_indices()
            self._zero_i = self._i.astype(int)
        new_signal = signal[self._zero_i]
        if self._left is None:
            return new_signal
        else:
            return np.ma.MaskedArray(new_signal, mask=self._left)

    @_method_wrapper
    def nearest(self, signal):
        """Nearest neighbor."""
        if self._nearest_i is None:
            self._interp_indices()
            self._nearest_i = self._i.astype(int)
            if self._mask is not None:
                self._nearest_i[~self._mask] = (
                    self._i[~self._mask] + 0.5).astype(int)
        return signal[self._nearest_i]

    @_method_wrapper
    def linear(self, signal):
        """Piecewise linear interpolation."""
        if self._linear_i is None:
            self._interp_indices()
            self._linear_i = self._i.astype(int)
            self._linear_alpha = self._i - self._linear_i

            # Special handling of end point to make it safe to use
            # self._linear_i + 1 in indexing.
            endpoints = self._linear_i + 1 == len(self._source_basis)
            self._linear_i[endpoints] -= 1
            self._linear_alpha[endpoints] = 1

        new_signal = (signal[self._linear_i] * (1 - self._linear_alpha) +
                      signal[self._linear_i + 1] * self._linear_alpha)

        # These should give exactly the same results as the calculations above,
        # but make sure that NaN/masked at self._linear_i or self._linear_i + 1
        # don't pollute the results.
        new_signal[self._linear_alpha == 0] = (
            signal[self._linear_i][self._linear_alpha == 0])
        new_signal[self._linear_alpha == 1] = (
            signal[self._linear_i + 1][self._linear_alpha == 1])

        if self._mask is None:
            return new_signal
        else:
            return np.ma.MaskedArray(new_signal, mask=self._mask)

    @_method_wrapper
    def quadratic(self, signal):
        """Quadratic interpolation."""
        return self._higher_order(signal, kind='quadratic')

    @_method_wrapper
    def cubic(self, signal):
        """Cubic interpolation."""
        return self._higher_order(signal, kind='cubic')

    def _higher_order(self, signal, kind):
        """
        Interpolations based on scipy.interpolation.interp1d.

        This lacks several features of the numpy-based interpolation methods
        such as optimization for interpolating mulitple signals between the
        same rasters, handling of NaNs/masked values etc.
        """
        if self._higher is False:
            self._mask = np.logical_or(
                self._target_basis > np.max(self._source_basis),
                self._target_basis < np.min(self._source_basis))
            self._higher = True
        self._warn_if_missing_values(signal)
        # Use scipy interpolation function
        new_signal = scinterp(self._source_basis, signal,
                              kind=kind, copy=False,
                              bounds_error=False,
                              fill_value=np.NaN)(self._target_basis)
        if self._mask is None:
            return new_signal
        else:
            return np.ma.MaskedArray(new_signal, mask=self._mask)

    def _warn_if_missing_values(self, signal):
        """Warn about using quadratic/cubic interpolation with NaN values."""
        if self._has_warned_about_missing_values:
            return

        if isinstance(signal, np.ma.MaskedArray):
            if np.any(np.ma.getmaskarray(signal) | np.isnan(signal)):
                sywarn("Masked values/NaNs are not supported when "
                       "interpolating with quadratic or cubic method.")
                self._has_warned_about_missing_values = True


def resample_file_with_spec(parameter_root, spec, in_adaffile, out_adaffile,
                            progress):
    signals_col = parameter_root['signals_colname'].selected
    dt_col = parameter_root['dt_colname'].selected
    tb_col = parameter_root['tb_colname'].selected
    signals = spec.get_column_to_array(signals_col)
    if dt_col is not None:
        dts = spec.get_column_to_array(dt_col)
    else:
        dts = np.zeros(signals.shape, dtype=float) * np.nan
    if tb_col is not None:
        to_tbs = spec.get_column_to_array(tb_col)
    else:
        to_tbs = np.zeros(signals.shape, dtype=six.text_type)

    dt_to_signals = collections.defaultdict(list)
    tbname_to_signals = collections.defaultdict(list)
    for i, (dt, to_tb, signal) in enumerate(zip(dts, to_tbs, signals)):
        if dt and not np.isnan(dt):
            dt_to_signals[dt].append(signal)
        elif to_tb:
            tbname_to_signals[to_tb].append(signal)
        else:
            raise SyDataError("Row {} in specification table specifies "
                              "neither dt nor a target time basis.".format(i))

    new_timebases = []
    for dt, dt_signals in dt_to_signals.items():
        # Create output system/raster
        new_timebasis, unit = get_new_timebasis(in_adaffile, dt, dt_signals)
        system_name = 'Resampled system'
        raster_name = 'Resampled raster {:.2}'.format(dt)
        new_timebases.append(
            (system_name, raster_name, new_timebasis, unit, dt_signals))
    for tbname, tb_signals in tbname_to_signals.items():
        raster_dict = get_raster_dict(in_adaffile)
        try:
            old_system_name, old_raster_name = raster_dict[tbname]
        except KeyError:
            sywarn('No such system/raster: {}'.format(tbname))
            continue
        old_tb_column = (
            in_adaffile.sys[old_system_name][old_raster_name].basis_column())

        system_name = 'Resampled system'
        raster_name = old_raster_name
        new_timebasis = old_tb_column.value()
        unit = old_tb_column.attr['unit'] or 's'
        new_timebases.append(
            (system_name, raster_name, new_timebasis, unit, tb_signals))

    selected_methods = (parameter_root['bool_interp_method'].selected,
                        parameter_root['int_interp_method'].selected,
                        parameter_root['interpolation_method'].selected)

    resampler = RasterResampler()
    progress_counter = 0
    for system_name, raster_name, new_timebasis, unit, signals in (
            new_timebases):
        if not unit:
            unit = 's'
        if system_name not in out_adaffile.sys.keys():
            new_system = out_adaffile.sys.create(system_name)
        if raster_name not in new_system.keys():
            new_raster = new_system.create(raster_name)
        new_raster.create_basis(new_timebasis, attributes={'unit': unit})

        # Loop over all rasters and resample selected signals in them
        for origin_system_name in in_adaffile.sys.keys():
            origin_system = in_adaffile.sys[origin_system_name]
            for origin_raster_name in origin_system.keys():
                origin_raster = origin_system[origin_raster_name]
                signals_in_this_raster = [
                    signal_name for signal_name in origin_raster.keys()
                    if signal_name in signals]
                if not signals_in_this_raster:
                    continue

                origin_basis = origin_raster.basis_column().value()
                new_basis = new_raster.basis_column().value()

                resampler.new_raster(origin_basis, new_basis)

                # Loop over all signals and resample them
                for signal_name in signals_in_this_raster:
                    progress(100. * progress_counter / len(signals))
                    signal = origin_raster[signal_name]
                    y = signal.y
                    interp = resampler.get_method(y, selected_methods)
                    new_y = interp(y)
                    attrs = dict(signal.signal().attr.items())
                    new_raster.create_signal(signal.name, new_y, attrs)
                    progress_counter += 1


def resample_file(parameter_root, in_adaffile, out_adaffile, progress):
    dt = parameter_root['dt'].value
    use_dt = parameter_root['use_dt'].value
    new_tb = parameter_root['new_tb'].selected
    resample_all = parameter_root['resample_all_rasters'].value
    chosen_signals = parameter_root['ts'].value_names

    if resample_all:
        signals = in_adaffile.ts.keys()
    else:
        signals = chosen_signals

    # Create output system/raster
    if use_dt:
        system_name = 'Resampled system'
        raster_name = 'Resampled raster'
        new_timebasis, unit = get_new_timebasis(in_adaffile, dt, signals)
    else:
        raster_dict = get_raster_dict(in_adaffile)
        system_name, raster_name = raster_dict[new_tb]
        old_tb_column = (in_adaffile.sys[system_name][raster_name]
                         .basis_column())
        new_timebasis = old_tb_column.value()
        unit = old_tb_column.attr['unit']
    new_system = out_adaffile.sys.create(system_name)
    new_raster = new_system.create(raster_name)

    attributes = {}
    if unit:
        attributes['unit'] = unit
    if use_dt:
        attributes['time step'] = dt

    new_raster.create_basis(new_timebasis, attributes=attributes)
    if parameter_root['only_timebasis'].value:
        return

    selected_methods = (parameter_root['bool_interp_method'].selected,
                        parameter_root['int_interp_method'].selected,
                        parameter_root['interpolation_method'].selected)

    resampler = RasterResampler()
    # Loop over all rasters and resample selected signals in them
    progress_counter = 0
    for origin_system_name in in_adaffile.sys.keys():
        origin_system = in_adaffile.sys[origin_system_name]
        for origin_raster_name in origin_system.keys():
            origin_raster = origin_system[origin_raster_name]
            signals_in_this_raster = [
                signal_name for signal_name in origin_raster.keys()
                if signal_name in signals]
            if not signals_in_this_raster:
                continue

            origin_basis = origin_raster.basis_column().value()
            new_basis = new_raster.basis_column().value()

            resampler.new_raster(origin_basis, new_basis)

            # Loop over all signals and resample them
            for signal_name in signals_in_this_raster:
                progress(100. * progress_counter / len(signals))
                signal = origin_raster[signal_name]
                y = signal.y
                interp = resampler.get_method(y, selected_methods)
                new_y = interp(y)
                attrs = dict(signal.signal().attr.items())
                new_raster.create_signal(signal.name, new_y, attrs)
                progress_counter += 1


def get_new_timebasis(in_adaffile, dt, signals):
    """
    Get new timebasis covering the same range as all the old timebases using
    step size dt.
    """
    if dt <= 0:
        raise SyConfigurationError('Time step must be positive.')

    t_range = None
    basis_kind = None
    basis_units = set()

    # The range of the new time basis should be the superset of all the
    # times in the resampled rasters.
    # TODO: What about reference times here?
    # TODO: I removed the warning when some signals are missing. Does that
    # matter?
    for system_name in in_adaffile.sys.keys():
        system = in_adaffile.sys[system_name]
        for raster_name in system.keys():
            raster = system[raster_name]
            if not set(raster.keys()) & set(signals):
                # No selected signals in this raster
                continue

            old_basis = raster.basis_column()
            basis = old_basis.value()
            unit = old_basis.attr.get('unit', '')

            if basis_kind:
                if basis_kind != basis.dtype.kind and not (
                        basis_kind in 'fiu' and basis.dtype.kind in 'fiu'):
                    raise SyDataError(
                        "All time bases must be of the same type. "
                        "Found both {} and {}.".format(
                            dtypes.typename_from_kind(basis_kind),
                            dtypes.typename_from_kind(basis.dtype.kind)))
            else:
                basis_kind = basis.dtype.kind

            # 'unknown' was the previous default unit so we can treat that as
            # empty.
            if unit and unit != 'unknown':
                basis_units.add(unit)

            if len(basis):
                if t_range is None:
                    t_range = basis[0], basis[-1]
                else:
                    t_range = (min(t_range[0], basis[0]),
                               max(t_range[1], basis[-1]))

    basis_unit = ''
    if len(basis_units) == 1:
        basis_unit = basis_units.pop()
    elif len(basis_units) > 1:
        sywarn("The time bases have different units: {}".format(
            ", ".join(basis_units)))
    if t_range is None:
        # None of the selected signals were present, return empty target basis
        return np.array([]), ''
    if basis_kind == 'M':
        t_range = t_range[0].astype(float), t_range[1].astype(float)
        dt *= 1000000

    # If number of samples fit perfectly, use linspace to always catch both end
    # points, at the expense of sometimes changing dt very slightly.
    sample_count = np.around((t_range[1] - t_range[0]) / dt, 8)
    if sample_count == int(sample_count):
        timebasis_new = np.linspace(t_range[0], t_range[1], sample_count + 1)
    else:
        timebasis_new = np.arange(t_range[0], t_range[1], dt)
    if basis_kind == 'M':
        timebasis_new = timebasis_new.astype('M8[us]')

    return timebasis_new, basis_unit


def get_raster_dict(adaffile):
    if adaffile.is_valid():
        return collections.OrderedDict(
            [('/'.join([system_name, raster_name]), (system_name, raster_name))
             for system_name, system in adaffile.sys.items()
             for raster_name in system.keys()])
    else:
        return {}


def timebasis_only_parameter(parameters):
    parameters.set_boolean(
        'only_timebasis', label='Export time basis only', value=False,
        description='Choose to only export the time basis')
    return parameters


class SuperNode(synode.Node):
    author = 'Helena Olen <helena.olen@combine.se'
    copyright = '(C) 2013 Combine Control Systems AB'
    version = '2.0'
    icon = 'interpolate.svg'
    tags = Tags(Tag.Analysis.SignalProcessing)

    parameters = synode.parameters()
    parameters.set_boolean(
        'resample_all_rasters', value=True, label="Resample all signals",
        description='Apply resampling to all signals')
    ts_editor = synode.Util.multilist_editor(edit=True)
    ts_editor.set_attribute('filter', True)
    parameters.set_list(
        'ts', label="Choose signals",
        description='Choose signals to interpolate', editor=ts_editor)
    parameters.set_float(
        'dt', label='Time step',
        description=('Time step in new timebasis. If old timebasis is of '
                     'type datetime this is considered to be in seconds.'))
    parameters.set_list(
        'new_tb', label='Timebasis to use for interpolation',
        description=('Timebasis to use as new timebasis '
                     'for selected timeseries'),
        editor=synode.Util.combo_editor(filter=True))
    parameters.set_boolean(
        'use_dt', label='Time step approach', value=True,
        description='Choose between a custom time step and using an existing.')
    parameters = timebasis_only_parameter(parameters)
    parameters.set_list(
        'bool_interp_method', plist=['zero', 'nearest'], value=[1],
        description=('Method used to interpolate boolean, text, and '
                     'byte string data'),
        editor=synode.Util.combo_editor())
    parameters.set_list(
        'int_interp_method', plist=_METHODS, value=[_METHODS.index('nearest')],
        description='Method used to interpolate integer data',
        editor=synode.Util.combo_editor())
    parameters.set_list(
        'interpolation_method', plist=_METHODS,
        value=[_METHODS.index('linear')],
        description='Method used to interpolate other data types',
        editor=synode.Util.combo_editor())


class InterpolateADAF(SuperNode):
    """
    Interpolation of timeseries in an ADAF.

    :Ref. nodes: :ref:`Interpolate ADAFs`
    """

    name = 'Interpolate ADAF'
    description = 'Interpolation of data'
    nodeid = 'org.sysess.sympathy.data.adaf.interpolateadaf'

    inputs = Ports([Port.ADAF('Input ADAF', name='port1')])
    outputs = Ports([Port.ADAF('Interpolated ADAF', name='port1')])

    def adjust_parameters(self, node_context):
        adjust(node_context.parameters['new_tb'],
               node_context.input['port1'],
               kind='rasters')
        adjust(node_context.parameters['ts'],
               node_context.input['port1'],
               kind='ts')

    def exec_parameter_view(self, node_context):
        parameter_root = node_context.parameters
        return InterpolationWidget(parameter_root)

    def execute(self, node_context):
        in_adaffile = node_context.input['port1']
        out_adaffile = node_context.output['port1']
        parameter_root = node_context.parameters
        if in_adaffile.is_empty():
            return
        out_adaffile.meta.from_table(in_adaffile.meta.to_table())
        out_adaffile.res.from_table(in_adaffile.res.to_table())
        resample_file(parameter_root, in_adaffile, out_adaffile,
                      progress=self.set_progress)


InterpolateADAFs = node_helper.list_node_factory(
    InterpolateADAF, ['port1'], ['port1'])


class InterpolateADAFsFromTable(synode.Node):
    """
    Interpolation of timeseries in ADAFs using a specification table. The
    specification table should have two to three columns. It must have a column
    with the names of the signals that should be interpolated. Furthermore it
    should have either a column with resampling rate for each signal or a
    column with the names of the signals to whose time basis it should
    interpolate each signal. It can also have both columns and if both of them
    have values for the same row it will use the resample rate.

    :Ref. nodes: :ref:`Interpolate ADAF`
    """

    name = 'Interpolate ADAFs with Table'
    description = 'Interpolation of data'
    nodeid = 'org.sysess.sympathy.data.adaf.interpolateadafswithtable'
    version = '1.0'
    copyright = '(C) 2015 Combine Control Systems AB'
    author = 'Magnus Sandén <magnus.sanden@combine.se>'
    icon = 'interpolate.svg'
    tags = Tags(Tag.Analysis.SignalProcessing)

    inputs = Ports([Port.Table('Specification Table', name='spec'),
                    Port.ADAFs('Input ADAFs', name='port1')])
    outputs = Ports([Port.ADAFs('Interpolated ADAFs', name='port1')])

    parameters = synode.parameters()
    parameters.set_list(
        'signals_colname', label='Column with signal names',
        description='Resample the timeseries in this column.',
        editor=synode.editors.combo_editor(edit=True, filter=True))
    parameters.set_list(
        'dt_colname', label='Column with sample rates',
        description=('The selected column should contain sample rates to '
                     'which the selected signals will be resampled. '
                     'At least one of this parameter and the time bases '
                     'parameter must be specified.'),
        editor=synode.editors.combo_editor(
            include_empty=True, edit=True, filter=True))
    parameters.set_list(
        'tb_colname', label='Column with time bases',
        description=('The selected column should contain existsing time bases '
                     'to which the selected signals will be resampled. '
                     'At least one of this parameter and the time bases '
                     'parameter must be specified.'),
        editor=synode.editors.combo_editor(
            include_empty=True, edit=True, filter=True))
    parameters = timebasis_only_parameter(parameters)
    parameters.set_list(
        'bool_interp_method',
        plist=['zero', 'nearest'], value=[1],
        description=('Method used to interpolate boolean, text, and '
                     'byte string data'),
        editor=synode.Util.combo_editor())
    parameters.set_list(
        'int_interp_method',
        plist=_METHODS, value=[_METHODS.index('nearest')],
        description='Method used to interpolate integer data',
        editor=synode.Util.combo_editor())
    parameters.set_list(
        'interpolation_method', plist=_METHODS,
        value=[_METHODS.index('linear')],
        description='Method used to interpolate other data types',
        editor=synode.Util.combo_editor())

    def update_parameters(self, parameters):
        # Older versions (before sympathy 1.4.4) specified the empty element
        # explicitly in adjust_parameters. In 1.4.4 the empty element went
        # missing. From 1.4.5 we add it with 'include_empty' instead.
        parameters['dt_colname'].editor['include_empty'] = True
        parameters['tb_colname'].editor['include_empty'] = True

    def adjust_parameters(self, node_context):
        pnames = ['signals_colname', 'dt_colname', 'tb_colname']
        for pname in pnames:
            adjust(node_context.parameters[pname], node_context.input['spec'])

    def exec_parameter_view(self, node_context):
        parameter_root = node_context.parameters
        tab_widget = QtGui.QTabWidget()
        methods_tab = MethodsTab(parameter_root)
        choose_spec_cols_tab = ChooseSpecColsTab(parameter_root)
        tab_widget.addTab(choose_spec_cols_tab, 'Specification table')
        tab_widget.addTab(methods_tab, 'Interpolation method')
        return tab_widget

    def execute(self, node_context):
        input_adafs = node_context.input['port1']
        spec = node_context.input['spec']
        if spec.is_empty():
            return
        output_adafs = node_context.output['port1']
        parameter_root = node_context.parameters

        def interpolate_adafs_w_table(input_adaf, output_adaf, set_progress):
            output_adaf.meta.from_table(input_adaf.meta.to_table())
            output_adaf.res.from_table(input_adaf.res.to_table())
            resample_file_with_spec(parameter_root, spec, input_adaf,
                                    output_adaf, progress=set_progress)
        synode.map_list_node(interpolate_adafs_w_table,
                             input_adafs, output_adafs, self.set_progress)


class ChooseSpecColsTab(QtGui.QWidget):
    def __init__(self, parameter_root):
        super(ChooseSpecColsTab, self).__init__()
        layout = QtGui.QVBoxLayout()
        layout.addWidget(parameter_root['signals_colname'].gui())
        layout.addWidget(parameter_root['dt_colname'].gui())
        layout.addWidget(parameter_root['tb_colname'].gui())

        layout.addStretch(0)
        self.setLayout(layout)


class MethodsTab(QtGui.QWidget):
    def __init__(self, parameter_root):
        super(MethodsTab, self).__init__()
        layout = QtGui.QVBoxLayout()
        layout.addWidget(QtGui.QLabel(
            "Choose interpolation methods for different data types."))
        self._form_layout = QtGui.QFormLayout()

        categories = ['Boolean, text, and byte string', 'Integer',
                      'Float, datetime, and timedelta']
        parameters = ['bool_interp_method', 'int_interp_method',
                      'interpolation_method']
        for category, parameter in zip(categories, parameters):
            widget = parameter_root[parameter].gui()
            self._form_layout.addRow(category, widget)

        layout.addLayout(self._form_layout)

        self._only_timebasis = parameter_root['only_timebasis'].gui()
        layout.addWidget(self._only_timebasis)
        layout.addStretch(0)
        self.setLayout(layout)

        self._only_timebasis.stateChanged.connect(
            self._only_timebasis_changed)
        self._only_timebasis_changed()

    def _only_timebasis_changed(self):
        disabled = (
            self._only_timebasis.editor().checkState() != QtCore.Qt.Checked)
        for i in range(self._form_layout.count()):
            self._form_layout.itemAt(i).widget().setEnabled(disabled)


class InterpolationWidget(QtGui.QWidget):
    """A widget containing a TimeBasisWidget and a ListSelectorWidget."""

    def __init__(self, parameter_root, parent=None):
        super(InterpolationWidget, self).__init__()
        self._parameter_root = parameter_root
        self._init_gui()

    def _init_gui(self):
        # Create widgets and add to layout
        tab_widget = QtGui.QTabWidget()
        tb_tab = self._init_tb_tab()
        tab_widget.addTab(tb_tab, 'New time basis')
        methods_tab = MethodsTab(self._parameter_root)
        tab_widget.addTab(methods_tab, 'Interpolation method')
        signals_tab = self._init_signals_tab()
        tab_widget.addTab(signals_tab, 'Signals')

        layout = QtGui.QVBoxLayout()
        layout.addWidget(tab_widget)
        self.setLayout(layout)
        self._init_gui_from_parameters()

    def _init_tb_tab(self):
        # Create radio button group
        self._dt_or_tb = QtGui.QButtonGroup()
        self._dt_or_tb.setExclusive(True)

        self._custom_dt_button = QtGui.QRadioButton('Use custom timestep')
        self._use_tb_button = QtGui.QRadioButton(
            'Interpolate using existing timebasis')

        # Add buttons to group
        self._dt_or_tb.addButton(self._custom_dt_button)
        self._dt_or_tb.addButton(self._use_tb_button)

        self._new_tb = self._parameter_root['new_tb'].gui()
        self._dt = self._parameter_root['dt'].gui()

        tb_ts_vlayout = QtGui.QVBoxLayout()
        tb_ts_vlayout.addWidget(self._custom_dt_button)
        tb_ts_vlayout.addWidget(self._dt)

        tb_ts_vlayout.addWidget(self._use_tb_button)
        tb_ts_vlayout.addWidget(self._new_tb)
        tb_ts_vlayout.addStretch(0)

        tb_tab = QtGui.QWidget()
        tb_tab.setLayout(tb_ts_vlayout)

        self._dt_or_tb.buttonClicked.connect(self._button_changed)

        return tb_tab

    def _init_signals_tab(self):
        signals_tab = QtGui.QWidget()

        self._ts_selection = self._parameter_root['ts'].gui()
        self._resample_all_signals = (
            self._parameter_root['resample_all_rasters'].gui())

        signals_vlayout = QtGui.QVBoxLayout()
        signals_vlayout.addWidget(self._resample_all_signals)
        signals_vlayout.addWidget(self._ts_selection)

        self._resample_all_signals.editor().toggled.connect(
            self._ts_selection.set_disabled)
        self._ts_selection.set_disabled(
            self._parameter_root['resample_all_rasters'].value)

        signals_tab.setLayout(signals_vlayout)
        return signals_tab

    def _init_gui_from_parameters(self):
        dt_checked = self._parameter_root['use_dt'].value
        self._custom_dt_button.setChecked(dt_checked)
        self._use_tb_button.setChecked(not dt_checked)
        self._use_tb_button.setChecked(not dt_checked)
        self._dt.setEnabled(dt_checked)
        self._new_tb.setEnabled(not dt_checked)

    def _button_changed(self, button):
        """
        Radiobuttton clicked. Enable/disable custom coefficient edits or
        predefined filter widgets depedning on which button that is pressed.
        """
        if button == self._custom_dt_button:
            self._dt.setEnabled(True)
            self._new_tb.setEnabled(False)
            self._parameter_root['use_dt'].value = True
        else:
            self._dt.setEnabled(False)
            self._new_tb.setEnabled(True)
            self._parameter_root['use_dt'].value = False
