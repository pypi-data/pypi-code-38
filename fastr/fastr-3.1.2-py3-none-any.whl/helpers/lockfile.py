# Copyright 2011-2014 Biomedical Imaging Group Rotterdam, Departments of
# Medical Informatics and Radiology, Erasmus MC, Rotterdam, The Netherlands
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""
A module implenting a lock that ensures a directory is only being used
by a single fastr run.
"""

import os
import pathlib

from ..exceptions import FastrLockNotAcquired


class DirectoryLock:
    """
    A lock for a directory, it creates a directory to set the locked state and
    if successful writes the pid in a file inside that directory to claim the
    lock
    """
    lock_dir_name = '.fastr.lock'
    pid_file_name = 'pid'

    def __init__(self, directory):
        self._directory = pathlib.Path(directory)
        self._acquired = False

    @property
    def lock_dir(self):
        return self._directory / self.lock_dir_name

    @property
    def pid_file(self):
        return self.lock_dir / self.pid_file_name


    def acquire(self):
        # If acquired, validate lock is still in place
        if self._acquired:
            try:
                lock_pid = int(self.pid_file.read_text())
            except (FileNotFoundError, ValueError):
                self.release()
                return False

            if lock_pid == os.getpid():
                return True
            else:
                self.release()
                return False

        # Try to create a lock directory and make sure it does not exist
        if self.lock_dir.exists():
            return False

        if self.lock_dir.is_dir():
            return False

        try:
            self.lock_dir.mkdir(parents=False, exist_ok=False)
        except FileExistsError:
            return False

        # Register creating PID in file in lock dir
        self.pid_file.write_text(str(os.getpid()))

        self._acquired = True

        return True

    def release(self):
        if not self._acquired:
            return

        try:
            lock_pid = int(self.pid_file.read_text())
        except (FileNotFoundError, ValueError):
            # Lock is not valid, mark it for deletion
            lock_pid = None

        if lock_pid is None or lock_pid == os.getpid():
            try:
               self.pid_file.unlink()
            except FileNotFoundError:
                pass

            try:
                self.lock_dir.rmdir()
            except FileNotFoundError:
                pass

        self._acquired = False

    def __enter__(self):
        if not self.acquire():
            raise FastrLockNotAcquired(self._directory)

    def __exit__(self, type, value, traceback):
        self.release()

    def __del__(self):
        self.release()


