import multiprocessing as mp
import ctypes
import gc
import os
import psutil
import numpy as np
from toon.input.helper import check_and_fix_dims, shared_to_numpy


class MultiprocessInput(object):
    def __init__(self, device=None,
                 high_priority=True, use_gc=False,
                 nrow=None, **kwargs):
        """
        Args:
            device: A class that inherits from `toon.input.base_input.BaseInput` (not an object).
            high_priority (bool): Whether the remote process should run at high priority.
                Silently fails if permissions are insufficient.
            use_gc (bool): Optionally disable garbage collection on the remote process.
            nrow: Override the inferred number of rows to store.
                If `None`, defaults to 10x the amount expected from a single frame.
            **kwargs: Passed to the device during instantiation.
        """
        self.device = device
        self.device_args = kwargs
        self.nrow = nrow
        self.high_priority = high_priority
        self.use_gc = use_gc

    def start(self):
        # Use spawn, rather than fork, when possible (for Macs)
        try:
            mp.set_start_method('spawn')
        except (AttributeError, RuntimeError):
            pass
        self.shared_lock = mp.RLock()
        self.remote_ready = mp.Event()
        self.kill_remote = mp.Event()
        self.sample_count = mp.Value(
            ctypes.c_uint32, 0, lock=self.shared_lock)  # sample counter
        data_dims = check_and_fix_dims(
            self.device.data_shapes(**self.device_args))
        # TODO: unclear, change later
        self.not_time_axis = [
            tuple(range(-1, -(len(dd) + 1), -1)) for dd in data_dims]
        # if not manually overridden, preallocate 10*whatever we would expect in a single frame
        nrow = self.nrow
        if not nrow:
            nrow = int(np.ceil(self.device.samp_freq(
                **self.device_args) / 60.0) * 10)

        # preallocate data arrays (shared arrays, numpy equivalents, and local copies)
        data_types = self.device.data_types(**self.device_args)
        self.mp_data_arrays = []
        self.np_data_arrays = []
        self.local_data_arrays = []
        for counter, data_dim in enumerate(data_dims):
            data_dim.insert(0, nrow)  # make axis 0 time
            prod = int(np.prod(data_dim))
            data_type = data_types[counter]
            self.mp_data_arrays.append(mp.Array(data_type,
                                                prod,
                                                lock=self.shared_lock))
            self.np_data_arrays.append(shared_to_numpy(
                self.mp_data_arrays[counter], data_dim, data_type))
            self.np_data_arrays[counter].fill(np.nan)
            self.local_data_arrays.append(
                np.copy(self.np_data_arrays[counter]))

        # preallocate time array
        self.mp_time_array = mp.Array(
            ctypes.c_double, nrow, lock=self.shared_lock)
        self.np_time_array = shared_to_numpy(
            self.mp_time_array, nrow, ctypes.c_double)
        self.np_time_array.fill(np.nan)
        self.local_time_array = np.copy(self.np_time_array)

        #
        self.process = mp.Process(target=worker,
                                  args=(self.device,
                                        self.device_args,
                                        self.shared_lock,
                                        self.remote_ready,
                                        self.kill_remote,
                                        self.mp_time_array,
                                        self.mp_data_arrays,
                                        nrow, data_dims, data_types, self.use_gc,
                                        self.sample_count,
                                        os.getpid()))
        self.process.daemon = True
        self.process.start()
        self.ps_process = psutil.Process(self.process.pid)
        self.original_nice = self.ps_process.nice()
        self.set_high_priority(self.high_priority)
        self.remote_ready.wait()

    def read(self):
        """

        Returns:
            A (time, data) tuple, where time is a 1-D numpy array of timestamps, and
                data is either a N-D array (where the 0th axis is time), or a list of
                N-D arrays. If there is no data, returns (None, None).
        """
        with self.shared_lock:
            count = self.sample_count.value
            self.sample_count.value = 0
            np.copyto(self.local_time_array, self.np_time_array)
            for local_data, remote_data in zip(self.local_data_arrays, self.np_data_arrays):
                np.copyto(local_data, remote_data)
        if not count:
            return None, None
        dims = self.not_time_axis
        time = self.local_time_array[0:count]
        if len(dims) == 1:
            data = self.local_data_arrays[0][0:count, :]
        else:
            data = [local_data[0:count, :]
                    for local_data, dim in zip(self.local_data_arrays, dims)]
        return time, data

    def stop(self, *args):
        self.set_high_priority(False)
        self.kill_remote.set()

    def set_high_priority(self, val):
        try:
            if val:
                if psutil.WINDOWS:
                    self.ps_process.nice(psutil.HIGH_PRIORITY_CLASS)
                else:
                    self.ps_process.nice(-10)
            else:
                self.ps_process.nice(self.original_nice)
        except (psutil.AccessDenied, psutil.NoSuchProcess):
            pass

    def __enter__(self):
        self.start()
        return self

    def __exit__(self, *args):
        self.stop()


def worker(device, device_args, shared_lock, remote_ready,
           kill_remote, mp_time_array, mp_data_arrays,
           nrow, data_dims, data_types, use_gc, sample_count,
           parent_pid):
    if not use_gc:
        gc.disable()
    dev = device(**device_args)
    np_time_array = shared_to_numpy(mp_time_array, nrow, ctypes.c_double)
    np_data_arrays = []
    for data, dims, types in zip(mp_data_arrays, data_dims, data_types):
        np_data_arrays.append(shared_to_numpy(data, dims, types))
    with dev as d:
        remote_ready.set()
        while not kill_remote.is_set() and psutil.pid_exists(parent_pid):
            timestamp, data = d.read()
            if timestamp is not None:
                with shared_lock:
                    if sample_count.value < nrow:  # nans to fill in
                        next_index = sample_count.value
                        if isinstance(data, list):
                            for np_data, new_data in zip(np_data_arrays, data):
                                np_data[next_index, :] = new_data
                        else:
                            np_data_arrays[0][next_index, :] = data
                        np_time_array[next_index] = timestamp
                    else:  # replace oldest data with newest data
                        if isinstance(data, list):
                            for np_data, new_data in zip(np_data_arrays, data):
                                np_data[:] = np.roll(np_data, -1, axis=0)
                                np_data[-1, :] = new_data
                        else:
                            np_data_arrays[0][:] = np.roll(
                                np_data_arrays[0], -1, axis=0)
                            np_data_arrays[0][-1, :] = data
                        np_time_array[:] = np.roll(np_time_array, -1, axis=0)
                        np_time_array[-1] = timestamp
                    sample_count.value += 1
