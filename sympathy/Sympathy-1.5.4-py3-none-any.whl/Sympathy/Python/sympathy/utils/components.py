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
# TODO(erik):
# Future imports cannot be used with eval, replace eval.
# from __future__ import (print_function, division, unicode_literals,
#                         absolute_import)
import os
import sys
import fnmatch
import inspect
from collections import defaultdict, OrderedDict

import six

from . prim import containing_dirs
from .. platform import state, exceptions


FILE_ENVS = {}
COMPONENTS = defaultdict(lambda: defaultdict(list))


class IComponent(object):
    """
    Base class for discoverable components.
    Specific interface for a particular kind of components should be determined
    by creating a subclass of IComponent.
    """
    pass


def get_support_dirs(dirs=None):
    """
    Return list of support directories to scan for components.
    The method relies on state.node_state().settings having following fields:
        'support_dirs'
        'library_dirs'
    These are normally setup by worker_subprocess.worker.
    """
    if not dirs:
        library = [
            path
            for path in state.node_state().settings['library_dirs'] or []]

        commons = [os.path.join(path, 'Common')
                   for path in library]
        dirs = library + commons
    return containing_dirs(dirs)


def get_file_env(filename, no_raise=False):
    """
    Return the environment resulting from executing the file in an empty
    environment.
    """
    if filename in FILE_ENVS:
        return FILE_ENVS[filename]

    env = OrderedDict()
    FILE_ENVS[filename] = env
    env['__file__'] = filename
    safe_filename = filename.encode('ascii', 'replace')
    try:
        with open(filename) as f:
            full_code_string = f.read()
    except Exception as e:
        if no_raise:
            import traceback
            six.print_(u'Error compiling {}'.format(filename), file=sys.stderr)
            traceback.print_exc()
        else:
            raise exceptions.SyDataError(
                "Could not read source file.",
                details=six.text_type(e))
    try:
        compiled = compile(full_code_string, safe_filename, 'exec')
        eval(compiled, env, env)
    except Exception as e:
        if no_raise:
            import traceback
            six.print_(u'Error compiling {}'.format(filename), file=sys.stderr)
            traceback.print_exc()
        else:
            raise exceptions.SyUserCodeError(exc_info=sys.exc_info())
    return env


def get_classes_env(env):
    """Return the class instances in env."""
    return OrderedDict((key, value) for key, value in env.items()
                       if inspect.isclass(value))


def get_subclasses_env(env, baseclass):
    """Return the class instances in env that are subclasses of baseclass."""
    res = OrderedDict()

    for key, value in env.items():
        if (inspect.isclass(value) and issubclass(value, baseclass)
                and value is not baseclass):
            # TODO(erik): Hack, pass filename in a less nasty way.
            # Importing instead of evaluating would result in a better
            # behavior with __file__ already set on the MODULE.
            value.__file__ = env['__file__']
            res[key] = value
    return res


def scan_components(pattern, kind, dirs=None):
    """
    Scan python path for available components matching pattern and kind.
    Pattern is a glob pattern matched against the filename and kind is the base
    class for a group of components.
    """
    matches = []
    for path in get_support_dirs(dirs):
        for root, dirs, files in os.walk(path):
            matches.extend([os.path.abspath(os.path.join(root, f))
                            for f in fnmatch.filter(files, pattern)])
    return [value
            for match in matches
            for value in get_subclasses_env(
                get_file_env(match, no_raise=True), kind).values()]


def get_components(pattern, kind, dirs=None):
    """
    Get list of components for the given kind.
    If no components are found, a scan is performed.
    """
    result = COMPONENTS[six.text_type(kind)]
    if result:
        return result
    else:
        result = scan_components(pattern, kind, dirs)
        COMPONENTS[six.text_type(kind)] = result
    return result
