import abc
import six
from toon.input.clock import mono_clock

@six.add_metaclass(abc.ABCMeta)
class BaseInput():
    """Abstract base class for input devices."""
    @abc.abstractmethod
    def __init__(self, clock=mono_clock.get_time, **kwargs):
        """
        Args:
            clock: A function that returns the current time. Defaults to :obj:`toon.input.clock.mono_clock.get_time`.
            **kwargs: Device-specific keyword arguments. These can also be used to infer the sampling frequency,
                shape of the data, and type of data.
        """
        self.clock = clock

    @abc.abstractmethod
    def __enter__(self):
        """Start communication with the device here."""
        pass

    @abc.abstractmethod
    def __exit__(self, *args):
        """Gracefully clean up the device here (if necessary)."""
        pass

    @abc.abstractmethod
    def read(self):
        """Read a single measurement from the input device.

        Returns:
            (timestamp, data) tuple. See examples for details.
        """
        pass

    @abc.abstractmethod
    def samp_freq(**kwargs):
        """Infer the sampling frequency from keyword arguments."""
        pass

    @abc.abstractmethod
    def data_shapes(**kwargs):
        """Infer the shape of the data from keyword arguments.

        Must be a list of lists, e.g. [[2, 3], [8]] or [[5]].
        """
        pass

    @abc.abstractmethod
    def data_types(**kwargs):
        """Infer the type of the data from keyword arguments.

        Please use types from :obj:`ctypes`.

        Must be a list, e.g. [ctypes.c_int32, ctypes.c_double] or [ctypes.c_char].
        """
        pass
