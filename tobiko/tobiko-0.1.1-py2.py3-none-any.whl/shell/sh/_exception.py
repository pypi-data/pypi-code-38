# Copyright (c) 2019 Red Hat, Inc.
#
# All Rights Reserved.
#
#    Licensed under the Apache License, Version 2.0 (the "License"); you may
#    not use this file except in compliance with the License. You may obtain
#    a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#    License for the specific language governing permissions and limitations
#    under the License.
from __future__ import absolute_import

import tobiko


class ShellError(tobiko.TobikoException):
    pass


class ShellCommandFailed(ShellError):
    """Raised when shell command exited with non-zero status
    """
    message = ("command '{command}' failed (exit status is {exit_status});\n"
               "stdin:\n{stdin}\n"
               "stdout:\n{stdout}\n"
               "stderr:\n{stderr}")


class ShellTimeoutExpired(ShellError):
    """Raised when shell command timeouts and has been killed before exiting
    """
    message = ("command {command} timed out after {timeout} seconds;\n"
               "stdin:\n{stdin}\n"
               "stdout:\n{stdout}\n"
               "stderr:\n{stderr}")


class ShellProcessTeriminated(ShellError):
    message = ("command '{command}' terminated (exit status is {exit_status})"
               ";\n"
               "stdin:\n{stdin}\n"
               "stdout:\n{stdout}\n"
               "stderr:\n{stderr}")


class ShellProcessNotTeriminated(ShellError):
    message = ("command '{command}' not terminated (time left is {time_left})"
               ";\n"
               "stdin:\n{stdin}\n"
               "stdout:\n{stdout}\n"
               "stderr:\n{stderr}")


class ShellStdinClosed(ShellError):
    message = ("command {command}: STDIN stream closed;\n"
               "stdin:\n{stdin}\n"
               "stdout:\n{stdout}\n"
               "stderr:\n{stderr}")
