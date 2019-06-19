# Copyright (c) 2013, Combine Control Systems AB
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
import errno
import os
import time
import sys


class TimeoutError(Exception):
    pass


def pid_exists(pid):
    try:
        import psutil
        return psutil.pid_exists(pid)
    except ImportError:
        if sys.platform == 'cygwin':
            try:
                os.kill(pid, 0)
            except OSError:
                return False
            return True


def age(filename):
    try:
        return time.time() - os.path.getmtime(filename)
    except:
        return 0


def expire(filename, lifetime):
    """
    Expire locks that have exceeded their lifetime that have no running
    process.
    """
    duration = 0
    now = time.time()
    mtime = now
    try:
        mtime = os.path.getmtime(filename)
        duration = now - mtime
    except OSError:
        pass
    else:
        if duration > lifetime:
            try:
                pid = -1
                with open(filename, 'rb') as f:
                    pid = int(f.read())
                if (not pid_exists(pid) and
                        mtime == os.path.getmtime(filename)):
                    # File is older than lifetime, and process creating
                    # it is not running.
                    os.remove(filename)
                    return True
            except:
                pass
    return False


class Lock(object):
    """
    File based lock for synchronizing processes, implemented using methods from
    os. The file located at 'filename' will be used for synchronization.

    If the lock cannot be acquired directly, the process will wait for 'wait'
    seconds before retrying, repeating the process until the lock is acquired
    or until 'timeout' seconds has elapsed. If 'timeout' is None then the
    process will try acquring the lock until it is acquired.

    Preferably used in a with statement.
    """

    def __init__(self, filename, timeout=10, wait=0.01, lifetime=30):
        self.__file = None
        self.filename = filename
        self.timeout = timeout
        self.wait = wait
        self.lifetime = lifetime

    def acquire(self):
        """Acquire the lock."""
        if self.__file:
            return

        expire(self.filename, self.lifetime)

        start = time.time()
        while time.time() - start < self.timeout or self.timeout is None:
            try:
                self.__file = os.open(
                    self.filename, os.O_CREAT | os.O_EXCL | os.O_RDWR)
                os.write(self.__file, str(os.getpid()).encode('ascii'))
                os.fsync(self.__file)
                os.close(self.__file)
                return
            except OSError as e:
                if e.errno == errno.EEXIST:
                    time.sleep(self.wait)

        raise TimeoutError(
            'Lock on {0} could not be acquired.'.format(self.filename))

    def release(self):
        """Release the lock."""
        if self.__file:
            os.remove(self.filename)
            self.__file = None

    def __enter__(self):
        self.acquire()

    def __exit__(self, *args):
        self.release()

    def __del__(self):
        self.release()
