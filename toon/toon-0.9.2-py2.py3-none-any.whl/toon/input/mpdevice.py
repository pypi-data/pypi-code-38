import ctypes
import gc
import multiprocessing as mp
import os
import sys
import traceback
from collections import namedtuple
from copy import copy
from itertools import compress
from sys import platform
from toon.input.tsarray import TsArray as TsA
from toon.input.tsarray import vstack

import numpy as np
import psutil

try:  # numpy>=1.16.1, https://github.com/numpy/numpy/pull/12769
    from numpy.ctypeslib import as_ctypes_type

except ImportError:
    ctypes_map = np.ctypeslib._typecodes.copy()
    ctypes_map['|S1'] = ctypes.c_char  # TODO: I have no clue if this is valid
    ctypes_map['|b1'] = ctypes.c_bool

    def as_ctypes_type(ctype):
        return ctypes_map[np.dtype(ctype).str]


def shared_to_numpy(mp_arr, dims, dtype):
    """Convert a :class:`multiprocessing.Array` to a numpy array.
    Helper function to allow use of a :class:`multiprocessing.Array` as a numpy array.
    Derived from the answer at:
    <https://stackoverflow.com/questions/7894791/use-numpy-array-in-shared-memory-for-multiprocessing>
    """
    return np.frombuffer(mp_arr, dtype=dtype).reshape(dims)


class MpDevice(object):
    """Creates and manages a process for polling an input device."""

    def __init__(self, device, high_priority=True, buffer_len=None):
        """Create a new MpDevice.

        Parameters
        ----------
        device: object (derived from toon.input.BaseDevice)
            Input device object.
        high_priority: bool
            Whether the priority of the child process should be elevated.
        buffer_len: int, optional
            Overrides the device's sampling_frequency when specifing the size of the
            circular buffer.
        """
        self.device = device
        self.high_priority = high_priority
        self.buffer_len = buffer_len

    def start(self):
        """Start polling from the device on the child process.

        Allocates all resources and creates the child process.

        Notes
        -----
        Prefer using as a context manager over explicitly starting and stopping.

        Raises
        ------
        Will raise an exception if something goes wrong during instantiation
        of the device.
        """
        # For Macs, use spawn (interaction with OpenGL or ??)
        # Windows only does spawn
        if platform == 'darwin' or platform == 'win32':
            try:
                mp.set_start_method('spawn')
            except (AttributeError, RuntimeError):
                pass  # already started a process, or on python2

        n_buffers = 2
        self.shared_locks = []
        # make one lock per buffer
        for i in range(n_buffers):
            self.shared_locks.append(mp.Lock())
        self.remote_ready = mp.Event()  # signal to main process that remote is done setup
        self.kill_remote = mp.Event()  # signal to remote process to die
        self.local_err, remote_err = mp.Pipe(duplex=False)
        self.current_buffer_index = mp.Value(ctypes.c_bool, 0, lock=False)  # shouldn't need a lock

        # figure out number of observations to save between reads
        nrow = 100  # default (100 Hz)
        # if we have a sampling_frequency, allocate 1s worth
        # should be enough wiggle room for 60Hz refresh rate
        if self.device.sampling_frequency:
            nrow = self.device.sampling_frequency
        if self.buffer_len:  # buffer_len overcomes all
            nrow = self.buffer_len
        nrow = max(int(nrow), 1)  # make sure we have at least one row
        _device_obs = self.device.get_obs()
        # use this tuple to return data
        self._return_tuple = self.device.build_named_tuple(_device_obs)
        self.nt = namedtuple('obs', 'time data')
        self._data = [[] for i in range(n_buffers)]  # one set of data per buffer
        # for each observation type, allocate arrays (though note that
        # there's nothing useful in them right now)
        for i in range(n_buffers):
            for obs in _device_obs:
                self._data[i].append(DataGlob(obs.ctype, obs.shape, nrow, self.shared_locks[i]))

        self._res = [None] * len(self._data[0])

        self.device.Returns = None  # Returns isn't picklable, but is restored when the device enters the context manager
        self.device.local = True  # make sure the device can be used remotely
        self.process = mp.Process(target=remote,
                                  args=(self.device, self._data, self.remote_ready,
                                        self.kill_remote, os.getpid(),
                                        self.current_buffer_index, remote_err))
        self.process.daemon = True
        self.process.start()
        self.ps_process = psutil.Process(self.process.pid)
        self.original_nice = self.ps_process.nice()
        self.set_high_priority(self.high_priority)  # lame try to set priority
        for i in range(n_buffers):
            for obs in self._data[i]:
                obs.generate_squeeze()
        self.check_error()
        self.remote_ready.wait()  # pause until the remote says it's ready
        self.device.local = False  # try to prevent local access to device

    def read(self):
        """Retrieve all observations that have occurred since the last read.

        Notes
        -----
        The data is stored in a circular buffer, which means that if the number
        of observations since the last read exceeds the preallocated data, the oldest
        data will be overwritten in favor of the newest. If this behavior is undesirable,
        either bump the sampling_frequency of the Device or the buffer_len of the MpDevice
        up to an adequate number, depending on the sampling rate of the device and how
        often you expect to call read().

        We minimize copies by default (i.e. we return a view of the local data).
        This means that in certain situations, such as appending the data to a list,
        there may be unexpected results (as all elements would be a reference to the
        same object/array). If you run into this, try explicitly `copy()`ing the data.

        If a named tuple is returned, the names are in *alphabetical* order, not the order
        that they are specified in the Device. This may come up if unpacking the read.

        Returns
        -------
        toon.input.TsArray (i.e. a numpy array with a `time` attribute) for a single Observation, or
        named tuple of TsArrays (if multiple types of Observations), where the names match the subclassed
        `Obs`ervations from the Device.

        Raises
        ------
        May raise an exception if one has occurred on the child process since the last read.
        """

        # get the currently used buffer
        # note that the value only changes *if* this function has acquired the
        # lock, so we should always be safe to access w/o lock here

        # check if error, and raise if present
        self.check_error()

        current_buffer_index = int(self.current_buffer_index.value)
        # this *may* block, if the remote is currently writing
        with self._data[current_buffer_index][0].lock:
            for counter, datum in enumerate(self._data[current_buffer_index]):
                local_count = datum.local_count = datum.counter.value
                datum.counter.value = 0  # reset (so that we start writing to top of array)
                if local_count > 0:
                    np.copyto(datum.local_data.time[0:local_count], datum.np_data.time[0:local_count])
                    np.copyto(datum.local_data[0:local_count].T, datum.np_data.data[0:local_count].T)  # allow copying to 1D
                    self._res[counter] = datum.local_data[0:local_count]
                else:
                    self._res[counter] = None
        # if only one Obs, don't stuff into a namedtuple
        if len(self._res) == 1:
            return self._res[0]
        # plug values into namedtuple
        return self._return_tuple(*self._res)

    def stop(self):
        """Stop reading from the device and kill the child process.

        Notes
        -----
        Prefer using as a context manager over explicitly starting and stopping.
        """
        self.set_high_priority(False)
        self.kill_remote.set()
        self.process.join()
        self.device.local = True

    def __enter__(self):
        self.start()
        return self

    def __exit__(self, *args):
        self.stop()

    def check_error(self):
        """See if any exceptions have occurred on the child process, or whether
        the device was already closed.
        """
        if not self.process.is_alive():
            # already closed (e.g. if using start() & stop() manually)
            if self.kill_remote.is_set():
                raise ValueError('MpDevice is closed.')
            # real error at *any* point remotely (device instantiation, shape mismatch, ...)
            exc_traceback = self.local_err.recv()
            exc = self.local_err.recv()
            print('Remote traceback:')
            print(exc_traceback)
            raise exc

    def set_high_priority(self, val=False):
        """Set the priority of the child process.
        Fails unless the user has adquate permissions.
        """
        try:
            if val:
                if psutil.WINDOWS:
                    self.ps_process.nice(psutil.HIGH_PRIORITY_CLASS)
                else:
                    self.ps_process.nice(-10)
            else:
                self.ps_process.nice(self.original_nice)
        except (psutil.AccessDenied, psutil.NoSuchProcess) as e:
            pass

    def clear(self):
        """Discard all pending observations."""
        # check if error, and raise if present
        self.check_error()
        current_buffer_index = int(self.current_buffer_index.value)
        # this *may* block, if the remote is currently writing
        with self._data[current_buffer_index][0].lock:
            for datum in self._data[current_buffer_index]:
                datum.counter.value = 0  # reset (so that we start writing to top of array)


def remote(dev, shared_data,
           # extras
           remote_ready, kill_remote, parent_pid,  # don't include in coverage, implicitly tested
           current_buffer_index, remote_err):  # pragma: no cover
    """Poll the device for data."""

    def process_data(shared, datum):
        if shared.counter.value < shared.nrow:  # haven't filled buffer yet, so next available row
            next_index = shared.counter.value
            shared.np_data.time[next_index] = datum.time
            shared.np_data.data[next_index, :] = datum.data
        else:  # rolling buffer, had cursed my bedroom
            np.copyto(shared.np_data.time, np.roll(shared.np_data.time, -1, axis=0))
            shared.np_data.time[-1] = datum.time
            np.copyto(shared.np_data.data, np.roll(shared.np_data.data, -1, axis=0))
            shared.np_data.data[-1, :] = datum.data
        # successful read, increment the indexing counter for this stream of data
        shared.counter.value += 1

    try:
        gc.disable()
        # instantiate the device

        for i in shared_data:
            for j in i:
                j.generate_np_version()

        with dev:
            remote_ready.set()  # signal to the local process that remote is ready to go
            while not kill_remote.is_set() and psutil.pid_exists(parent_pid):
                data = dev.do_read()  # get observation(s) from device
                buffer_index = int(current_buffer_index.value)  # can only change later
                if isinstance(data, list):  # if a list of observations, rather than a single one
                    inds = [[d is not None for d in l] for l in data]
                    flag = any([any(d) for d in inds])
                    is_list = True
                else:
                    inds = [d is not None for d in data]
                    flag = any(inds)
                    is_list = False
                if flag:  # any data at all (otherwise, don't bother acquiring locks)
                    # test whether the current buffer is accessible
                    lck = shared_data[buffer_index][0].lock
                    success = lck.acquire(block=False)
                    if not success:  # switch to the other buffer (the local process is in the midst of reading)
                        current_buffer_index.value = not current_buffer_index.value
                        buffer_index = int(current_buffer_index.value)
                        lck = shared_data[buffer_index][0].lock
                        lck.acquire()
                    try:
                        if is_list:
                            for dat, ind in zip(data, inds):
                                for counter, datum in zip(np.where(ind)[0], compress(dat, ind)):
                                    process_data(shared_data[buffer_index][counter], datum)
                        else:
                            for counter, datum in zip(np.where(inds)[0], compress(data, inds)):
                                process_data(shared_data[buffer_index][counter], datum)
                    finally:
                        lck.release()
    except Exception as e:
        exc_type, exc_value, exc_traceback = sys.exc_info()
        fmt_traceback = ''.join(traceback.format_tb(exc_traceback))
        remote_err.send(fmt_traceback)
        remote_err.send(e)
        gc.enable()
        remote_err.close()
    finally:
        remote_ready.set()


# make sure this is visible for pickleability
obs = namedtuple('obs', 'time data')


class DataGlob(object):
    def __init__(self, ctype, shape, nrow, lock):
        self.new_dims = (nrow,) + shape
        if issubclass(ctype, ctypes.Structure):
            self.ctype = ctype
        else:
            self.ctype = as_ctypes_type(ctype)
        self.shape = shape
        self.is_scalar = self.shape == (1,)
        self.lock = lock
        prod = int(np.prod(self.new_dims))
        # don't touch (usually)
        self.nrow = int(nrow)
        self._mp_data = obs(time=mp.Array(ctypes.c_double, self.nrow, lock=False),
                            data=mp.Array(self.ctype, prod, lock=False))
        self.counter = mp.Value(ctypes.c_uint, 0, lock=False)
        self.generate_np_version()
        self.generate_local_version()

    def generate_np_version(self):
        self.np_data = obs(time=shared_to_numpy(self._mp_data.time, (self.nrow,), ctypes.c_double),
                           data=shared_to_numpy(self._mp_data.data, self.new_dims, self.ctype))

    def generate_local_version(self):
        self.local_count = 0
        self.local_data = TsA(self.np_data.data.copy(), time=self.np_data.time.copy())

    def generate_squeeze(self):
        # if scalar data, give the user a 1D array (rather than 2D)
        if self.is_scalar:
            self.local_data = TsA(np.squeeze(self.np_data.data.copy()),
                                  time=self.np_data.time.copy())
        # special case for buffer size of 1 and scalar data
        if self.local_data.shape == ():
            self.local_data.shape = (1,)


def stack(returns):
    # stack a list of copied Returns, e.g.
    # from toon.input import stack
    # datae = []
    # while True:
    #     data = dev.read()
    #     if data.any():
    #         datae.append(data.copy()) # NB: data must be copied, else you get views...
    # stacked_datae = stack(datae) # plugs back into a new Returns tuple

    # start with list of Returns
    # want to get to list per Obs (i.e. TsArray), which we can then vstack
    intermediate = [list() for x in returns[0]]
    # iterate through all returns, append to appropriate list within output
    for rets in returns:
        for obs, out in zip(rets, intermediate):
            if obs is not None:
                out.append(obs)

    output = []
    for out in intermediate:
        if out == []:
            output.append(None)
        else:
            output.append(vstack(out))
    return returns[0].__class__(*output)
