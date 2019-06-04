#!/usr/bin/env python
#
# util.py - Miscellaneous utility functions.
#
# Author: Paul McCarthy <pauldmccarthy@gmail.com>
#
"""This module contains a collection of miscellaneous utility functions and
constants.
"""


import re
import sys
import enum
import time
import logging
import warnings
import functools
import contextlib

try:
    import resource
except ImportError:
    resource = None

import numpy as np


log = logging.getLogger(__name__)


CTYPES = enum.Enum(
    'CTYPES',
    ['sequence',
     'integer',
     'continuous',
     'categorical_single',
     'categorical_single_non_numeric',
     'categorical_multiple',
     'categorical_multiple_non_numeric',
     'time',
     'date',
     'text',
     'compound',
     'unknown'])
"""The ``CTYPES`` enum defines all the types that ``funpack`` is aware of.
"""


DATA_TYPES = {

    # We have to use floating point for
    # integer types because pandas uses
    # nan to represent missing data.
    CTYPES.integer              : np.float32,
    CTYPES.continuous           : np.float32,
    CTYPES.categorical_single   : np.float32,
    CTYPES.categorical_multiple : np.float32,
    CTYPES.sequence             : np.uint32,
}
"""Internal data type to use for the different variable types. Used
by the :func:`columnTypes` function.
"""


def parseColumnName(name):
    """Parses a UK Biobank column name, returns the components.

    Two column naming formats are supported. The name is expected to be either
    a string of the form::

        variable-visit.instance

    Or a string of the form::

        f.variable.visit.instance

    Some variables have the form::

        f.variable..visit.instance

    For these variables, the visit is interpreted as a negative number.

    If ``name`` does not have one of the above forms, a :exc:`ValueError` is
    raised.

    .. note:: For the vast majority of biobank variables, the second number in
              a column name (``visit`` above) corresponds to the assessment
              visit. However, there are a small number of variables which are
              not associated with a specific visit, and thus for which this
              number does not corresopnd to a visit (e.g. variable 40006), but
              to some other coding.

              Confusingly, the UK Biobank showcase refers to the coding that a
              variable adhers to as an "instancing", whilst also using the
              term "instance" to refer to the columns of multi-valued
              variables - the ``instance`` element of the column name.

              The "instancing" that a variable uses is contained in the
              ``Instancing`` column of the variable table.

    :arg name: Column name
    :returns:  A tuple containing:
                - variable ID
                - visit number
                - instance number
    """

    if name.startswith('f'):
        pat = re.compile(r'f\.([0-9]+)\.(\.)?([0-9]+)\.([0-9]+)')
    else:
        pat = re.compile(r'([0-9]+)-(-)?([0-9]+)\.([0-9]+)')

    parts = pat.fullmatch(name)

    if parts is None:
        raise ValueError('Invalid column name: {}'.format(name))

    parts = parts.groups()

    vid      = int(parts[0])
    visit    = int(parts[2])
    instance = int(parts[3])

    if parts[1] is not None:
        visit = -visit

    return (vid, visit, instance)


def generateColumnName(variable, visit, instance):
    """Generate a column name for the given variable, visit and instance.

    :arg variable: Integer variable ID
    :arg visit:    Visit number
    :arg instance: Instance number
    """
    return '{}-{}.{}'.format(variable, visit, instance)


def parseMatlabRange(r):
    """Parses a string containing a MATLAB-style ``start:stop`` or
    ``start:step:stop`` range, where the ``stop`` is inclusive).

    :arg r:   String containing MATLAB_style range.
    :returns: List of integers in the fully expanded range.
    """
    elems = [int(e) for e in r.split(':')]

    if len(elems) == 3:
        start, step, stop = elems
        if   step > 0: stop += 1
        elif step < 0: stop -= 1

    elif len(elems) == 2:
        start, stop  = elems
        stop        += 1
        step         = 1
    elif len(elems) == 1:
        start = elems[0]
        stop  = start + 1
        step  = 1
    else:
        raise ValueError('Invalid range string: {}'.format(r))

    return list(range(start, stop, step))


@contextlib.contextmanager
def timed(op=None, logger=None, lvl=None, fmt=None, minutes=None):
    """Context manager which times a section of code, and prints a log
    message afterwards.

    :arg op:      Name of operation which is being timed

    :arg logger:  Logger object to use - defaults to :attr:`log`.

    :arg lvl:     Log level - defaults to ``logging.INFO``.

    :arg fmt:     Custom message. If not provided, a default message is used.
                  Must be a ``'%'``-style format string which accepts two
                  parameters: the elapsed time (``%s``), and the memory usage
                  (``%i``)..

    :arg minutes: Deprecated, has no effect.
    """

    if minutes is not None:
        warnings.warn('The "minutes" argument is deprecated and has '
                      'no effect', DeprecationWarning, stacklevel=2)
    if fmt is None:
        fmt = '[{}] completed in %s (%+iMB)'.format(op)

    if logger is None:
        logger = log

    if lvl is None:
        lvl = logging.INFO

    if op is not None:
        logger.log(lvl, 'Running task [%s]', op)

    # ru_maxrss appears to be bytes under
    # macos, and kilobytes under linux
    if sys.platform == 'darwin': memdenom = 1048576.0
    else:                        memdenom = 1024.0

    if resource is not None:
        startmem  = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
    else:
        startmem = 0

    starttime = time.time()

    yield

    endtime = time.time()

    hours   = int( (endtime - starttime) / 3600)
    minutes = int(((endtime - starttime) % 3600) / 60)
    seconds = int(((endtime - starttime) % 3600) % 60)
    timestr = '{:d} seconds'.format(seconds)

    if minutes > 0: timestr = '{} minutes, {}'.format(minutes, timestr)
    if hours   > 0: timestr = '{} hours, {}'  .format(hours,   timestr)

    if resource is not None:
        endmem  = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
    else:
        endmem = 0

    mbytes = (endmem - startmem) / memdenom

    if minutes: logger.log(lvl, fmt, timestr, mbytes)
    else:       logger.log(lvl, fmt, timestr, mbytes)


def deprecated(message):
    """Decorator used to mark a function or method as deprecated """

    def wrapper(func):

        warnings.filterwarnings('default', category=DeprecationWarning)

        def decorator(*args, **kwargs):
            warnings.warn(message, DeprecationWarning, stacklevel=2)
            return func(*args, **kwargs)

        return functools.update_wrapper(decorator, func)

    return wrapper
