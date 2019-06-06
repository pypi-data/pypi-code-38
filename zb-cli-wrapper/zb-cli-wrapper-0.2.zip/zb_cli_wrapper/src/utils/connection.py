#
# Copyright (c) 2019, Nordic Semiconductor ASA
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without modification,
# are permitted provided that the following conditions are met:
#
# 1. Redistributions of source code must retain the above copyright notice, this
#    list of conditions and the following disclaimer.
#
# 2. Redistributions in binary form, except as embedded into a Nordic
#    Semiconductor ASA integrated circuit in a product or a software update for
#    such product, must reproduce the above copyright notice, this list of
#    conditions and the following disclaimer in the documentation and/or other
#    materials provided with the distribution.
#
# 3. Neither the name of Nordic Semiconductor ASA nor the names of its
#    contributors may be used to endorse or promote products derived from this
#    software without specific prior written permission.
#
# 4. This software, with or without modification, must only be used with a
#    Nordic Semiconductor ASA integrated circuit.
#
# 5. Any software provided in binary form under this license must not be reverse
#    engineered, decompiled, modified and/or disassembled.
#
# THIS SOFTWARE IS PROVIDED BY NORDIC SEMICONDUCTOR ASA "AS IS" AND ANY EXPRESS
# OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES
# OF MERCHANTABILITY, NONINFRINGEMENT, AND FITNESS FOR A PARTICULAR PURPOSE ARE
# DISCLAIMED. IN NO EVENT SHALL NORDIC SEMICONDUCTOR ASA OR CONTRIBUTORS BE
# LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR
# CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE
# GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION)
# HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT
# LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT
# OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

import os
import sys
import serial
import subprocess
import time
import signal

from pynrfjprog.MultiAPI import MultiAPI
from pynrfjprog.API import APIError, DeviceFamily


class TimeoutError(Exception):
    pass


class Connection(object):

    def open(self):
        raise NotImplementedError

    def close(self):
        raise NotImplementedError

    def read(self, size):
        raise NotImplementedError

    def write(self, data, timeout):
        raise NotImplementedError


class AsciiConnection(Connection):

    def __init__(self, conn):
        self._conn = conn

    def __del__(self):
        del self._conn
        self._conn = None

    def open(self):
        self._conn.open()

    def close(self):
        self._conn.close()

    def read(self, size):
        data = self._conn.read(size)
        return data.decode("utf-8", "ignore")

    def write(self, data, timeout=5.0):
        return self._conn.write(data.encode("utf-8", "ignore"), timeout)

    def __repr__(self):
        return self._conn.__repr__()


class RttConnection(Connection):

    def __init__(self, jlink_snr, dev_family=DeviceFamily.NRF52,
                       rtt_channel=0, rtt_timeout=3.0, jlink_speed_khz=500,
                       name=None):
        super(RttConnection, self).__init__()

        self._jlink_snr = jlink_snr
        self._dev_family = dev_family
        self._rtt_channel = rtt_channel
        self._rtt_timeout = rtt_timeout
        self._jlink_speed_khz = jlink_speed_khz
        self._name = name
        self._api = None

    def __del__(self):
        if self._api is None:
            return

        self.close()

    def set_rtt_channel(self, rtt_channel):
        self._rtt_channel = rtt_channel

    def open(self):
        if self._api is not None:
            return

        self._api = MultiAPI(self._dev_family)
        self._api.open()

        if self._name:
            self._api._runner_process.name += "_{}".format(self._name)

        self._api.connect_to_emu_with_snr(self._jlink_snr, self._jlink_speed_khz)
        self._api.connect_to_device()
        self._api.rtt_start()

        timeout_time = time.time() + self._rtt_timeout
        try:
            while True:
                if self._api.rtt_is_control_block_found():
                    break

                if time.time() > timeout_time:
                    raise TimeoutError("Could not find RTT control block.")
                time.sleep(0.01)
    
        except APIError as e:
            print(e)

    def close(self):
        if self._api is None:
            return

        try:
            if self._api.is_rtt_started():
                self._api.rtt_stop()

            if self._api.is_connected_to_device():
                self._api.disconnect_from_device()

            if self._api.is_connected_to_emu():
                self._api.disconnect_from_emu()

        except APIError as e:
            print(e)

        finally:
            self._api.close()
            self._api.terminate()

            del self._api
            self._api = None

    def read(self, size=64):
        if self._api is None:
            return bytes([])

        return bytes(self._api.rtt_read(self._rtt_channel, size, encoding=None))

    def write(self, data, timeout=5.0):
        if self._api is None:
            return -1

        return self._api.rtt_write(self._rtt_channel, data, encoding=None)

    def __repr__(self):
        s = "{}:".format(self._name) if self._name else ""
        return s + "RTT@{}".format(self._jlink_snr)


class UartConnection(Connection):

    def __init__(self, port, baudrate, name=None):
        super(UartConnection, self).__init__()

        self._port = port
        self._baudrate = baudrate

        self._serial = None
        self.name = name

    def __del__(self):
        if self._serial is None:
            return

        self.close()

    def open(self):
        self._serial = serial.Serial(timeout=0, write_timeout=1.0)
        # Workaround to avoid serial communication failures
        # DTR - Data Terminal Ready
        # DSR - Data Set Ready
        # RTS - Request To Send
        # CTS - Clear To Send
        self._serial.dtr = True
        self._serial.rtscts = True
        self._serial.dsrdtr = True
        self._serial.port = self._port
        self._serial.baudrate = self._baudrate

        self._serial.open()

    def close(self):
        if self._serial is None:
            return

        self._serial.close()
        self._serial = None

    def read(self, size):
        if self._serial is None:
            raise RuntimeError("Trying to read data from closed {}".format(self))

        return self._serial.read(size)

    def write(self, data, timeout=5.0):
        if self._serial is None:
            raise RuntimeError("Trying to write data to closed {}".format(self))

        sent_count = 0

        timeout_time = time.time() + timeout
        while sent_count < len(data) and time.time() < timeout_time:
            sent_count += self._serial.write(data[sent_count:])
            self._serial.flush()

        return sent_count

    def __repr__(self):
        if self.name is not None:
            return f"{self.name}@{self._port}"
        else:
            return f"UartConn: {self._port}@{self._baudrate}"


class ProcessConnection(Connection):

    def __init__(self, args, cwd):
        self._args = args
        self._cwd = cwd

        self._proc = None

    def __del__(self):
        if self._proc is None:
            return

        self.close()

    def open(self):
        # Popen is unhappy if creationflags argument is provided on Linux.
        # To solve this, pass args by unpacking a dictionary and include
        # creationflags only on Windows.
        kargs = {
            'args': self._args,
            'stdin': subprocess.PIPE,
            'stdout': subprocess.PIPE,
            'stderr': subprocess.PIPE,
            'cwd': self._cwd,
            'bufsize': 0,
            'shell': False
        }
        if not sys.platform.startswith('linux'):
            kargs['creationflags'] = subprocess.CREATE_NEW_PROCESS_GROUP
        else:
            kargs['preexec_fn'] = os.setpgrp
        
        self._proc = subprocess.Popen(**kargs)

    def close(self):
        if not sys.platform.startswith('linux'):
            # Send CTRL+BREAK signal to a process group. We need to do that
            # to make sure that subprocesses spawned by _proc are killed.
            # This can be a case when, for example, _proc is a batch file which
            # executes external programs.
            #
            # We can't use CTRL+C as Windows doesn't allow this for process
            # groups (see  http://msdn.microsoft.com/en-us/library/ms683155%28v=vs.85%29.aspx)
            self._proc.send_signal(signal.CTRL_BREAK_EVENT)
        else:
            # Based on disscussion in https://stackoverflow.com/a/4791612
            os.killpg(os.getpgid(self._proc.pid), signal.SIGKILL)

        # Kill _proc. One might think that sending CTRL+BREAK to a process group
        # kills everyone including parent. Nope. If parent is a batch file then,
        # after sending CTRL+BREAK, a "Terminate batch job (Y/N)?" dialog is displayed,
        # hence _proc.kill() is still needed.
        if (self._proc.poll() == None):
            self._proc.kill()

        self._proc.wait()

        del self._proc
        self._proc = None

    def read(self, size):
        if self._proc is None:
            return bytes([])

        return self._proc.stdout.read(size)

    def write(self, data, timeout=5.0):
        if self._proc is None:
            return -1

        sent_count = 0

        timeout_time = time.time() + timeout

        while sent_count < len(data) and time.time() < timeout_time:
            sent_count += self._proc.stdin.write(data[sent_count:])
            self._proc.stdin.flush()

        return sent_count

    def __repr__(self):
        return "ProcConn: {}".format((" ".join(self._args)[:16] + "..."))
