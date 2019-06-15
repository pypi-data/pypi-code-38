"""
General processing facilities.

Due to the inheritance from the :mod:`aspecd.processing` module, all processing
steps provided are fully self-documenting, i.e. they add all necessary
information to reproduce each processing step to the
:attr:`trepr.dataset.Dataset.history` attribute of the dataset.

"""


import numpy as np

import aspecd.processing


class Error(Exception):
    """Base class for exceptions in this module."""

    pass


class DimensionError(Error):
    """Exception raised when the dimension isn't zero or one.

    Attributes
    ----------
    message : `str`
        explanation of the error

    """

    def __init__(self, message=''):
        super().__init__()
        self.message = message


class RangeError(Error):
    """Exception raised when the given range is out of the dataset's range.

    Attributes
    ----------
    message : `str`
        explanation of the error

    """

    def __init__(self, message=''):
        super().__init__()
        self.message = message


class UnitError(Error):
    """Exception raised when the unit isn't either 'axsi' or 'index'.

    Attributes
    ----------
    message : `str`
        explanation of the error

    """

    def __init__(self, message=''):
        super().__init__()
        self.message = message


class Averaging(aspecd.processing.ProcessingStep):
    """Averaging of two-dimensional data along a given axis.

    When measuring TREPR data, the resulting spectrum is always
    two-dimensional. To analyse the data it's often necessary to extract a
    one-dimensional spectrum. The one-dimensional spectrum can either be a cut
    along the field or the time axis. To get a representative spectrum, the
    average over several points along the respective axis is calculated.

    All parameters, implicit and explicit, necessary to perform the averaging
    processing step, will be stored in the attribute
    :attr:`trepr.processing.Averaging.parameters`.

    An example for using the averaging processing step may look like this::

        avg = Averaging(dimension=0, avg_range=[4.e-7, 6.e-7], unit='axis')
        dataset.process(avg)

    Parameters
    ----------
    dimension : {0,1}, optional
        Dimension along which the averaging is done. 0 is along the field axis
        and 1 is along the time axis. Default is 0.

    avg_range : list
        Range in which the averaging will take place.

    unit : {'axis', 'index'}, optional
        Unit in which the average range is given. Either 'axis' for axis values
        or 'index' for indices. Default is axis.

    Attributes
    ----------
    parameters : dict
        All Parameters that must be known to reproduce the averaging.

    description : str
        Describes the aim of the class.

    undoable : bool
        Information weather the processing step is undoable or not.

    Raises
    ------
    DimensionError
        Raised if dimension is not in [0, 1].

    UnitError
        Raised if unit is not in ['axis', 'index'].

    RangeError
        Raised if range is not within axis.

    """

    def __init__(self, dimension=0, avg_range=None, unit='axis'):
        super().__init__()
        # public properties
        self.description = 'Averaging'
        self.undoable = True
        self.parameters['dimension'] = dimension
        self.parameters['range'] = avg_range
        self.parameters['unit'] = unit
        # protected properties:
        self._dim = self.parameters['dimension']

    def _perform_task(self):
        """Perform the processing step."""
        avg_range = self._get_avg_range()
        self._execute_averaging(avg_range)

    def _get_avg_range(self):
        """Calculate the range within the averaging will be performed."""
        if self.parameters['unit'] == 'axis':
            start_index = \
                self._get_index(self.dataset.data.axes[self._dim].values,
                                self.parameters['range'][0])
            end_index = \
                self._get_index(self.dataset.data.axes[self._dim].values,
                                self.parameters['range'][-1])
            avg_range = [start_index, end_index]
        else:
            avg_range = self.parameters['range']
        return avg_range

    def _execute_averaging(self, avg_range):
        """Apply the averaging on the given experimental dataset."""
        if self._dim == 0:
            axes = [self.dataset.data.axes[1], self.dataset.data.axes[2]]
            self.dataset.data.data = \
                np.average(self.dataset.data.data[:, avg_range], axis=1)
        else:
            axes = [self.dataset.data.axes[0], self.dataset.data.axes[2]]
            self.dataset.data.data = \
                np.average(self.dataset.data.data[avg_range, :], axis=0)
        self.dataset.data.axes = axes

    @staticmethod
    def _get_index(vector, value):
        return np.abs(vector - value).argmin()

    def _sanitise_parameters(self):
        if self.parameters['dimension'] not in [0, 1]:
            raise DimensionError('Wrong dimension. Choose 0 or 1.')
        if self.parameters['unit'] not in ['index', 'axis']:
            raise UnitError('Wrong unit. Choose "axis" or "index".')
        if self.parameters['unit'] == 'index':
            if self.parameters['range'][0] not in \
                    range(len(self.dataset.data.axes[self._dim].values)):
                raise RangeError('Lower index out of range.')
            if self.parameters['range'][1] not in \
                    range(len(self.dataset.data.axes[self._dim].values)):
                raise RangeError('Upper index out of range.')
        if self.parameters['unit'] == 'axis':
            if not self._value_within_vector_range(
                    self.parameters['range'][0],
                    self.dataset.data.axes[self._dim].values):
                raise RangeError('Lower value out of range.')
            if not self._value_within_vector_range(
                    self.parameters['range'][1],
                    self.dataset.data.axes[self._dim].values):
                raise RangeError('Upper value out of range.')
        if self.parameters['range'][1] < self.parameters['range'][0]:
            raise RangeError('Values need to be ascending.')

    @staticmethod
    def _value_within_vector_range(value, vector):
        return np.amin(vector) <= value <= np.amax(vector)


class PretriggerOffsetCompensation(aspecd.processing.ProcessingStep):
    """
    Pretrigger offset compensation.

    One of the first processing steps after measuring TREPR data is to set the
    average of the pretrigger time trace to zero. The so-called pretrigger
    offset compensation.

    All parameters, implicit and explicit, necessary to perform the averaging
    processing step, will be stored in the attribute
    :attr:`trepr.processing.PretriggerOffsetCompensation.parameters`.

    An example for using the pretrigger offset compensation processing step may
    look like this::

        poc = PretriggerOffsetCompensation()
        dataset.process(poc)

    Attributes
    ----------
    description : str
        Describes the aim of the class.

    undoable : bool
        Information weather the processing step is undoable or not.

    """

    def __init__(self):
        super().__init__()
        # public properties:
        # Note: self.parameters inherited
        self.description = 'Pretrigger offset compensation'
        self.undoable = True

    def _perform_task(self):
        """Perform the processing step and return the processed data."""
        self._get_zeropoint_index()
        self._execute_compensation(self.parameters['zeropoint_index'])

    def _get_zeropoint_index(self):
        """Get the index of the last time value before the trigger."""
        zeropoint_index = \
            np.argmin(np.cumsum(self.dataset.data.axes[0].values))
        self.parameters['zeropoint_index'] = int(zeropoint_index)

    def _execute_compensation(self, range_end):
        """Execute the pretrigger offset compensation."""
        for field_point, time_trace in enumerate(self.dataset.data.data):
            pretrig_avg = self._get_pretrigger_average(time_trace, range_end)
            self.dataset.data.data[field_point] = time_trace - pretrig_avg

    @staticmethod
    def _get_pretrigger_average(time_trace, range_end=1):
        """Calculate the average of the time trace before triggering."""
        array = time_trace[0:range_end]
        return np.average(array)


class Normalise(aspecd.processing.ProcessingStep):

    def __init__(self):
        super().__init__()
        self.description = 'Normalise data in dataset.'
        self.parameters['type'] = 'area'

    def _perform_task(self):
        if self.parameters['type'] == "area":
            self.dataset.data.data = self.dataset.data.data / \
                                     sum(abs(self.dataset.data.data))
        elif self.parameters['type'] == "maximum":
            self.dataset.data.data = self.dataset.data.data / \
                                     max(abs(self.dataset.data.data))
        else:
            self.dataset.data.data = self.dataset.data.data / \
                                     sum(abs(self.dataset.data.data))



if __name__ == '__main__':
    import trepr.io

    PATH = '../../Daten/messung17/'
    importer = trepr.io.SpeksimImporter(source=PATH)
    dataset = aspecd.dataset.Dataset()
    dataset.import_from(importer)

    pretrigger = PretriggerOffsetCompensation()
    process1 = importer.dataset.process(pretrigger)
    print(importer.dataset.history[0].processing.parameters)

    avg = Averaging(dimension=1, avg_range=[2900, 2904], unit='axis')
    process2 = dataset.process(avg)
    print(importer.dataset.history[1].processing.parameters)
