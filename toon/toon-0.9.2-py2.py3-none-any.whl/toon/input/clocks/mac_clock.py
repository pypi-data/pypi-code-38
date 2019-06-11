"""
  Copyright 2014, 2015, 2016 Ori Livneh <ori@wikimedia.org>
  Licensed under the Apache License, Version 2.0 (the "License");
  you may not use this file except in compliance with the License.
  You may obtain a copy of the License at
    http://www.apache.org/licenses/LICENSE-2.0
  Unless required by applicable law or agreed to in writing, software
  distributed under the License is distributed on an "AS IS" BASIS,
  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
  See the License for the specific language governing permissions and
  limitations under the License.
"""

# copied from https://github.com/atdt/monotonic
# under the Apache License 2.0
# starting from
# https://github.com/atdt/monotonic/blob/5bd1bf90e5e49d4ce4f5a90b9c97de6934b9503c/monotonic.py#L56
# until the end of the `if sys.platform == 'darwin'` block (~line 76)
# pragma: no cover
import ctypes

libc = ctypes.CDLL('/usr/lib/libc.dylib', use_errno=True)


class mach_timebase_info_data_t(ctypes.Structure):
    _fields_ = (('numer', ctypes.c_uint32), ('denom', ctypes.c_uint32))


mach_absolute_time = libc.mach_absolute_time
mach_absolute_time.restype = ctypes.c_uint64


class MonoClock(object):
    def __init__(self):
        self._reference_counter = self.get_ticks()
        timebase = mach_timebase_info_data_t()
        libc.mach_timebase_info(ctypes.byref(timebase))
        self.frequency = timebase.numer / timebase.denom * 1.0e9

    def get_ticks(self):
        return mach_absolute_time()

    def get_time(self):
        return (self.get_ticks() - self._reference_counter) / self.frequency

    def getTime(self):
        return self.get_time()

    @property
    def start_time(self):
        return self._reference_counter / self.frequency
