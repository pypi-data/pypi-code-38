#!/usr/bin/env python
#
# processing.py - Cleaning and processing parsing and functions.
#
# Author: Paul McCarthy <pauldmccarthy@gmail.com>
#
"""This module contains functionality for parsing the ``Process`` column of
the processing table, and the ``Clean`` column of the variable
table. Definitions of the available (pre-)processing functions are in the
:mod:`cleaning_functions` and :mod:`.processing_functions` modules.


The :func:`processData` function is also defined here - it executes the
processes defined in the processing table.


Special processing functions can be applied to a variable's data by adding
them to the ``Clean`` and ``Process`` columns of the variable or processing
table respectively.  Processing is specified as a comma-separated list of
process functions - for example::


    process1, process2(), process3('arg1', arg2=1234)


The :func:`parseProcesses` function parses such a line, and returns a list of
:class:`Process` objects which can be used to query the process name and
arguments, and to run each process.
"""


import functools as ft
import itertools as it
import              logging
import              collections

import pyparsing as pp

from . import util
from . import custom


log = logging.getLogger(__name__)


def processData(dtable):
    """Applies all processing specified in the processing table to the data.

    :arg dtable: The :class:`DataTable` instance.
    """

    ptable = dtable.proctable

    for i in ptable.index:

        # refresh the list of all variables
        # in the data on each iteration, as
        # a previously executed process may
        # add/remove variables to/from the
        # data.
        all_vids     = dtable.variables
        all_vids     = [v for v in all_vids if v != 0]

        # For each process, the processing table
        # contains a "process variable type",
        # a list of vids, and the process itself.
        # The pvtype is one of:
        #   - vids:                   apply the process to the specified vids
        #   - all:                    apply the process to all vids
        #   - all_independent:        apply the process independently to all
        #                             vids
        #   - all_except:             apply the process to all vids except the
        #                             specified ones
        #   - all_independent_except: apply the process independently to all
        #                             vids except the specified ones
        pvtype, vids = ptable.loc[i, 'Variable']
        procs        = ptable.loc[i, 'Process']

        # Build a list of lists of vids, with
        # each vid list a group of variables
        # that is to be processed together.

        # apply independently to every variable
        if pvtype in ('all_independent', 'all_independent_except'):
            if pvtype.endswith('except'): exclude = vids
            else:                         exclude = []
            vids = [[v] for v in all_vids if v not in exclude]

        # apply simultaneously to every variable
        elif pvtype in ('all', 'all_except'):
            if pvtype.endswith('except'): exclude = vids
            else:                         exclude = []
            vids = [[v for v in all_vids if v not in exclude]]

        # apply to specified variables
        else:
            vids = [[v for v in vids if dtable.present(v)]]

        vids = [vg for vg in vids if len(vg) > 0]

        if len(vids) == 0:
            continue

        # Run each process
        for proc in procs.values():
            runProcess(proc, dtable, vids)


def runProcess(proc, dtable, vids):
    """Called by :func:`processData`. Runs the given process, and uppates
    the :class:`.DataTable` as needed.

    :arg proc:   :class:`.Process` to run.
    :arg dtable: :class:`.DataTable` containing the data.
    :arg vids:   List of lists, groups of variable IDs to run the process on.
    """

    # We assume that processes which work on more
    # than one variable will manage their own
    # concurrency. Processes which work on just
    # one variable are executed in parallel here.
    runparallel = [vg for vg in vids if len(vg) == 1]
    runserial   = [vg for vg in vids if len(vg)  > 1]

    log.debug('Running process %s on %u variables',
              proc.name, len(list(it.chain(*vids))))

    with util.timed(proc.name, log, logging.DEBUG):

        with dtable.pool() as pool:
            results = list(pool.map(ft.partial(proc.run, dtable), runparallel))

        for vg in runserial:
            results.append(proc.run(dtable, vg))

    remove  = []
    add     = []
    addvids = []
    addmeta = []

    def expand(res, length):
        if res is None: return [None] * length
        else:           return res

    for result in results:
        if result is None:
            continue

        error = ValueError('Invalid return value from '
                           'process {}'.format(proc.name))

        if isinstance(result, tuple):

            # series/vids to add
            if len(result) == 2:
                add    .extend(result[0])
                addvids.extend(expand(result[1], len(result[0])))
                addmeta.extend(expand(None,      len(result[0])))

            # columns to remove, and
            # series/vids to add
            elif len(result) in (3, 4):

                if len(result) == 3:
                    result = list(result) + [None]

                remove .extend(result[0])
                add    .extend(result[1])
                addvids.extend(expand(result[2], len(result[1])))
                addmeta.extend(expand(result[3], len(result[1])))
            else:
                raise error

        # columns to remove
        elif isinstance(result, list):
            remove.extend(result)
        else:
            raise error

    # remove columns first, in case
    # there is a name clash between
    # the old and new columns.
    if len(remove) > 0: dtable.removeColumns(remove)
    if len(add)    > 0: dtable.addColumns(add, addvids, addmeta)


class NoSuchProcessError(Exception):
    """Exception raised by the :class:`Process` class when an unknown
    process name is specified.
    """
    pass


class Process(object):
    """Simple class which represents a single processing step. The :meth:`run`
    method can be used to run the process on the data for a specific variable.
    """


    def __init__(self, ptype, name, args, kwargs):
        """Create a ``Process``.

        :arg ptype: Process type - either ``cleaner`` or ``processor``
                    (see the :mod:`.custom` module).
        :arg name:  Process name
        :arg args:  Positional arguments to pass to the process function.
        :arg args:  Keyword arguments to pass to the process function.
        """

        # cleaner functions are not
        # defined in processing_functions,
        # so in this case func will be None.
        self.__ptype    = ptype
        self.__name     = name
        self.__args     = args
        self.__kwargs   = kwargs
        self.__metaproc = kwargs.pop('metaproc', None)


    def __repr__(self):
        """Return a string representation of this ``Process``."""
        args    = ','.join([str(v) for v in self.__args])
        kwargs  = ','.join(['{}={}'.format(k, v) for k, v in
                           self.__kwargs.items()])

        allargs = [args, kwargs]
        allargs = [a for a in allargs if a != '']
        allargs = ', '.join(allargs)
        return '{}[{}]({})'.format(self.__name, self.__ptype, allargs)


    @property
    def name(self):
        """Returns the name of this ``Process``. """
        return self.__name


    @property
    def args(self):
        """Returns the positional arguments for this ``Process``. """
        return self.__args


    @property
    def kwargs(self):
        """Returns the keyword arguments for this ``Process``. """
        return self.__kwargs


    def run(self, *args):
        """Run the process on the data, passing it the given arguments,
        and any arguments that were passed to :meth:`__init__`.
        """
        result = custom.run(self.__ptype,
                            self.__name,
                            *args,
                            *self.__args,
                            **self.__kwargs)

        if self.__metaproc is not None and \
           isinstance(result, tuple)   and \
           len(result) == 4:

            meta  = result[3]
            mproc = self.__metaproc

            try:
                meta = [custom.runMetaproc(mproc, m) for m in meta]
            except Exception as e:
                log.warning('Metadata processing function failed: %s', e)

            result = tuple(list(result[:3]) + [meta])

        return result


def parseProcesses(procs, ptype):
    """Parses the given string containing one or more comma-separated process
    calls, as defined in the processing table. Returns a list of
    :class:`Process` objects.

    :arg procs: String containing one or more comma-separated (pre-)processing
                steps.

    :arg ptype: either ``cleaner`` or ``processor``

    :returns:   A list of :class:`Process` objects.

    """

    def makeProcess(toks):
        name = toks[0]

        args   = ()
        kwargs = {}

        if len(toks) == 2:
            if isinstance(toks[1], tuple):
                args   = toks[1]
            elif isinstance(toks[1], dict):
                kwargs = toks[1]
        elif len(toks) == 3:
            args, kwargs = toks[1:]

        if not custom.exists(ptype, name):
            raise NoSuchProcessError(name)

        return Process(ptype, name, args, kwargs)

    parser = pp.delimitedList(makeParser().setParseAction(makeProcess))

    try:
        parsed = parser.parseString(procs, parseAll=True)
    except Exception as e:
        log.error('Error parsing process list "{}": {}'.format(procs, e))
        raise e

    return list(parsed)


@ft.lru_cache()
def makeParser():
    """Generate a ``pyparsing`` parser which can be used to parse a single
    process call in the processing table.
    """

    lparen   = pp.Literal('(').suppress()
    rparen   = pp.Literal(')').suppress()

    def convertBoolean(tok):
        tok = tok[0]
        if   tok == 'True':  return True
        elif tok == 'False': return False
        else:                return tok

    def parseArgs(toks):
        return [tuple(toks)]

    def parseKwargs(toks):
        kwargs = collections.OrderedDict()
        for i in range(0, len(toks), 2):
            kwargs[toks[i]] = toks[i + 1]
        return kwargs

    funcName = pp.pyparsing_common.identifier
    argval   = (pp.QuotedString('"')                                       ^
                pp.QuotedString("'")                                       ^
                pp.pyparsing_common.number                                 ^
                pp.oneOf(['True', 'False']).setParseAction(convertBoolean) ^
                pp.Literal('None').setParseAction(pp.replaceWith(None)))
    kwargs   = (pp.pyparsing_common.identifier +
                pp.Literal('=').suppress() +
                argval)
    posargs  = pp.delimitedList(argval).setParseAction(parseArgs)
    kwargs   = pp.delimitedList(kwargs).setParseAction(parseKwargs)
    allargs  = pp.delimitedList(pp.Optional(posargs) + pp.Optional(kwargs))
    allargs  = lparen   + pp.Optional(allargs) + rparen
    function = funcName + pp.Optional(allargs)

    return function
