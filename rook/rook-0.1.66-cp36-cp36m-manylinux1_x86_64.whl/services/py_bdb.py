"""Debugger basics"""

import fnmatch
import sys
import os
import types
import threading
import inspect
from six import print_
from collections import defaultdict

from rook.logger import logger

__all__ = ["BdbQuit", "Bdb", "Breakpoint"]


class BdbQuit(Exception):
    """Exception to give up completely"""


class Bdb:

    """Generic Python debugger base class.

    This class takes care of details of the trace facility;
    a derived class should implement user interaction.
    The standard debugger class (pdb.Pdb) is an example.
    """

    _ROOKOUT_TRACE = "__ROOKOUT_TRACE"

    def __init__(self, skip=None):
        self.skip = set(skip) if skip else None
        self.breaks = {}
        self.fncache = {}
        self.canonic_names = {}
        self.aug_ids = {}
        self.positions = defaultdict(list)
        self.last_file_id = 0

        self._disabled = False

        self.thread_local = threading.local()
        self.trace_through = False

        self.user_line = None
        self.user_call = None
        self.user_return = None
        self.user_exception = None

        self.sys_settrace = sys.settrace
        self.sys_gettrace = sys.gettrace
        self.threading_settrace = threading.settrace
        self.threading_tracefunc = None

    def update_activity(self):
        self._disabled = not(bool(self.breaks) or bool(self.trace_through))

    def ignore_current_thread(self):
        # If gevent has patched away threads, don't ignore current thread (as they are all the same thread)
        try:
            import gevent.monkey

            if gevent.monkey.is_module_patched('threading'):
                return

        except ImportError:
            pass

        if not self.trace_through and self.sys_gettrace() == self.trace_dispatch:
            self.sys_settrace(None)

    def _get_thread_trace_func(self):
        try:
            return self.thread_local._rookout_tracefunc
        except AttributeError:
            return None

    def _get_frame_trace_func(self, frame):
        try:
            return frame.f_locals[self._ROOKOUT_TRACE]
        except KeyError:
            return None

    def _set_thread_trace_func(self, tracefunc):
        self.thread_local._rookout_tracefunc = tracefunc

    def _set_frame_trace_func(self, tracefunc, frame):
        frame.f_locals[self._ROOKOUT_TRACE] = tracefunc

    def sys_settrace_hook(self, tracefunc):
        if threading.current_thread().name.startswith("rookout-"):
            # ignore our threads
            return

        # Check we are resetting our own trace_dispatch
        # This probably means we are being called by threading for a new thread
        if tracefunc == self.trace_dispatch:
            self.sys_settrace(self.trace_dispatch)

            # Install the additional threading tracefunc
            if self.threading_tracefunc:
                self.sys_settrace_hook(self.threading_tracefunc)
            return

        # Enable trace through
        if tracefunc:
            self.trace_through = True
        self.update_activity()

        # Store function
        self._set_thread_trace_func(tracefunc)

    def sys_gettrace_hook(self):
        return self._get_thread_trace_func()

    def threading_settrace_hook(self, tracefunc):
        self.threading_tracefunc = tracefunc

        # Enable trace through
        if tracefunc:
            self.trace_through = True
        self.update_activity()

    def canonic(self, filename):
        # We let everybody think it is still the file name
        if isinstance(filename, int):
            return filename

        # Try to convert filename to file_id
        file_id = self.fncache.get(filename)
        if not file_id:
            # If there's no file id, get file canonic name
            if filename[0] == "<" and filename[-1] == ">":
                canonic_name = filename
            else:
                canonic_name = os.path.abspath(filename)
                canonic_name = os.path.normpath(canonic_name)

            # Check if canonic name has an id
            file_id = self.canonic_names.get(canonic_name)
            if not file_id:
                # If no id so far, create a new one
                file_id = self.last_file_id = self.last_file_id + 1
                self.canonic_names[canonic_name] = file_id
                # If sources are not available, keep only the file name.
                if not os.path.isfile(canonic_name):
                    logger.warning("Source file could not be resolved: %s", canonic_name)
                    self.canonic_names[os.path.basename(canonic_name)] = file_id

            # Cache filename to id conversion
            self.fncache[filename] = file_id

        return file_id

    def reset(self):
        import linecache
        linecache.checkcache()
        self.botframe = None

    def trace_dispatch(self, frame, event, arg):
        if self._disabled:
            return None

        if not os or not os.path:
            return None

        if event == 'line':
            # This if is a 'flattened' version of dispatch_line to optimize performance
            # Original version:
            # if self.break_here(frame):
            #    if self.user_line:
            #        self.user_line(frame)
            # return self.trace_dispatch
            filename = frame.f_code.co_filename

            # Try to convert filename to file_id
            file_id = self.fncache.get(filename)
            if not file_id:
                # If there's no file id, get file canonic name
                if filename[0] == "<" and filename[-1] == ">":
                    canonic_name = filename
                else:
                    canonic_name = os.path.abspath(filename)
                    canonic_name = os.path.normcase(canonic_name)

                # Check if canonic name has an id
                file_id = self.canonic_names.get(canonic_name)
                if not file_id:
                    # If no id so far, create a new one
                    file_id = self.last_file_id = self.last_file_id + 1
                    self.canonic_names[canonic_name] = file_id

                # Cache filename to id conversion
                self.fncache[filename] = file_id

            file_breaks = self.breaks.get(file_id)
            if file_breaks and frame.f_lineno in file_breaks:
                if self.user_line:
                    # this loop used to exist in user_line's implementation which would
                    # find all breakpoints on this filename and line, but user_line
                    # now finds BPs by aug_id
                    for aug_id in self.positions[(file_id, frame.f_lineno)]:
                        self.user_line(frame, filename, aug_id)

            if self.trace_through:
                tracefunc = self._get_frame_trace_func(frame)
                if tracefunc:
                    tracefunc_ret = tracefunc(frame, event, arg)
                    if tracefunc_ret:
                        self._set_frame_trace_func(tracefunc_ret, frame)

            return self.trace_dispatch

        if event == 'call':
            # This if is a 'flattened' version of dispatch_call to optimize performance
            # Original version:
            # if self.break_anywhere(frame):
            #     return self.trace_dispatch
            # else:
            #    return self.trace_dispatch_default
            retval = None

            filename = frame.f_code.co_filename

            # Try to convert filename to file_id
            file_id = self.fncache.get(filename)
            if not file_id:
                # If there's no file id, get file canonic name
                if filename[0] == "<" and filename[-1] == ">":
                    canonic_name = filename
                else:
                    canonic_name = os.path.abspath(filename)
                    canonic_name = os.path.normcase(canonic_name)

                # Check if canonic name has an id
                file_id = self.canonic_names.get(canonic_name)
                if not file_id:
                    file_id = self.canonic_names.get(os.path.basename(canonic_name))
                    if not file_id:
                        # If no id so far, create a new one
                        file_id = self.last_file_id = self.last_file_id + 1
                        self.canonic_names[canonic_name] = file_id

                # Cache filename to id conversion
                self.fncache[filename] = file_id

            # If file in breaks
            if file_id in self.breaks:
                file_breaks = self.breaks.get(file_id)

                # Check if code contains one of the lines we are looking for
                if frame.f_code.co_firstlineno and frame.f_code.co_lnotab:
                    current_line = frame.f_code.co_firstlineno
                    if current_line in file_breaks:
                        retval = self.trace_dispatch
                    else:
                        for incr in frame.f_code.co_lnotab[1::2]:
                            if isinstance(incr, int):
                                current_line += incr
                            else:
                                current_line += ord(incr)
                            if current_line in file_breaks:
                                retval = self.trace_dispatch
                                break

            if self.trace_through:
                tracefunc = self._get_thread_trace_func()
                if tracefunc:
                    tracefunc_ret = tracefunc(frame, event, arg)
                    if tracefunc_ret:
                        retval = self.trace_dispatch
                    self._set_frame_trace_func(tracefunc_ret, frame)

            return retval

        if event == 'return':
            if self.trace_through:
                tracefunc = self._get_frame_trace_func(frame)
                if tracefunc:
                    tracefunc(frame, event, arg)
            return None

        if event == 'exception':
            if self.trace_through:
                tracefunc = self._get_frame_trace_func(frame)
                if tracefunc:
                    tracefunc(frame, event, arg)
            return None

        if event == 'c_call':
            if self.trace_through:
                tracefunc = self._get_thread_trace_func(frame)
                if tracefunc:
                    tracefunc_ret = tracefunc(frame, event, arg)
                    if tracefunc_ret:
                        retval = self.trace_dispatch
                    self._set_frame_trace_func(tracefunc_ret, frame)
            return None

        if event == 'c_exception':
            if self.trace_through:
                tracefunc = self._get_frame_trace_func(frame)
                if tracefunc:
                    tracefunc = tracefunc(frame, event, arg)
            return None
        if event == 'c_return':
            if self.trace_through:
                tracefunc = self._get_frame_trace_func(frame)
                if tracefunc:
                    tracefunc = tracefunc(frame, event, arg)
            return None

        print_('bdb.Bdb.dispatch: unknown debugging event:', repr(event))
        if self.trace_through:
            tracefunc = self._get_thread_trace_func(frame)
            if tracefunc:
                tracefunc = tracefunc(frame, event, arg)
        return self.trace_dispatch

    def dispatch_line(self, frame):
        if self.break_here(frame):
            if self.user_line:
                self.user_line(frame)
        return self.trace_dispatch

    def dispatch_call(self, frame):
        if self.break_anywhere(frame):
             return self.trace_dispatch
        else:
            return self.trace_dispatch_default

    def dispatch_return(self, frame, arg):
        if self.user_return:
            self.user_return(frame, arg)
        return self.trace_dispatch

    def dispatch_exception(self, frame, arg):
        if self.user_exception:
            self.user_exception(frame, arg)
        return self.trace_dispatch

    # Normally derived classes don't override the following
    # methods, but they may if they want to redefine the
    # definition of stopping and breakpoints.

    def is_skipped_module(self, module_name):
        for pattern in self.skip:
            if fnmatch.fnmatch(module_name, pattern):
                return True
        return False

    def break_here(self, frame):
        filename = self.canonic(frame.f_code.co_filename)
        if not filename in self.breaks:
            return False
        lineno = frame.f_lineno
        if not lineno in self.breaks[filename]:
            return False

        return True

    def break_anywhere(self, frame):
        return self.canonic(frame.f_code.co_filename) in self.breaks

    def set_trace(self):
        # Make sure we are not called twice
        tracefunc = self.sys_gettrace()
        if tracefunc == self.trace_dispatch:
            raise RuntimeError("Cannot trace with two bdb instance at once!")

        # Backup active dispatcher
        self.sys_settrace_hook(tracefunc)
        self.threading_settrace_hook(threading._trace_hook)

        # Hook methods
        sys.settrace = self.sys_settrace_hook
        sys.gettrace = self.sys_gettrace_hook
        threading.settrace = self.threading_settrace_hook

        # Setup our own dispatchers
        self.sys_settrace(self.trace_dispatch)
        self.threading_settrace(self.trace_dispatch)

    def close(self):
        # Remove hooks
        sys.settrace = self.sys_settrace
        sys.gettrace = self.sys_gettrace
        threading.settrace = self.threading_settrace

        # Reset to other dispatcher (if exists)
        self.sys_settrace(self.sys_gettrace_hook())
        self.threading_settrace(self.threading_tracefunc)

    # Derived classes and clients can call the following methods
    # to manipulate breakpoints.  These methods return an
    # error message is something went wrong, None if all is well.
    # Set_break prints out the breakpoint line and file:lineno.
    # Call self.get_*break*() to see the breakpoints or better
    # for bp in Breakpoint.bpbynumber: if bp: bp.bpprint().

    def set_break(self, module, filename, lineno, aug_id, temporary=0, cond = None,
                  funcname=None):
        filename = self.canonic(filename)

        # TODO - reenable this test in the future
        #import linecache # Import as late as possible
        #line = linecache.getline(filename, lineno)
        #if not line:
        #    return 'Line %s:%d does not exist' % (filename,
        #                           lineno)

        if not filename in self.breaks:
            self.breaks[filename] = []
        list = self.breaks[filename]
        if not lineno in list:
            list.append(lineno)
        self.aug_ids[aug_id] = (filename, lineno)
        self.positions[(filename, lineno)].append(aug_id)
        bp = Breakpoint(filename, lineno, temporary, cond, funcname)

        self.update_activity()

    def _prune_breaks(self, filename, lineno):
        if (filename, lineno) not in Breakpoint.bplist:
            self.breaks[filename].remove(lineno)
        if not self.breaks[filename]:
            del self.breaks[filename]

    def clear_break(self, aug_id):
        filename, lineno = self.aug_ids[aug_id]
        filename = self.canonic(filename)
        if not filename in self.breaks:
            return 'There are no breakpoints in %s' % filename
        if lineno not in self.breaks[filename]:
            return 'There is no breakpoint at %s:%d' % (filename,
                                    lineno)
        # If there's only one bp in the list for that file,line
        # pair, then remove the breaks entry
        for bp in Breakpoint.bplist[filename, lineno][:]:
            bp.deleteMe()
        self._prune_breaks(filename, lineno)
        del self.aug_ids[aug_id]
        self.positions[(filename, lineno)].remove(aug_id)

        self.update_activity()

    def clear_all_breaks(self):
        if not self.breaks:
            return 'There are no breakpoints'
        for bp in Breakpoint.bpbynumber:
            if bp:
                bp.deleteMe()
        self.breaks = {}
        self.aug_ids = {}
        self.positions = defaultdict(list)
        self.update_activity()


class Breakpoint:

    """Breakpoint class

    Implements temporary breakpoints, ignore counts, disabling and
    (re)-enabling, and conditionals.

    Breakpoints are indexed by number through bpbynumber and by
    the file,line tuple using bplist.  The former points to a
    single instance of class Breakpoint.  The latter points to a
    list of such instances since there may be more than one
    breakpoint per line.

    """

    # XXX Keeping state in the class is a mistake -- this means
    # you cannot have more than one active Bdb instance.

    next = 1        # Next bp to be assigned
    bplist = {}     # indexed by (file, lineno) tuple
    bpbynumber = [None] # Each entry is None or an instance of Bpt
                # index 0 is unused, except for marking an
                # effective break .... see effective()

    def __init__(self, file, line, temporary=0, cond=None, funcname=None):
        self.funcname = funcname
        # Needed if funcname is not None.
        self.func_first_executable_line = None
        self.file = file    # This better be in canonical form!
        self.line = line
        self.temporary = temporary
        self.cond = cond
        self.enabled = 1
        self.ignore = 0
        self.hits = 0
        self.number = Breakpoint.next
        Breakpoint.next = Breakpoint.next + 1
        # Build the two lists
        self.bpbynumber.append(self)
        if (file, line) in self.bplist:
            self.bplist[file, line].append(self)
        else:
            self.bplist[file, line] = [self]


    def deleteMe(self):
        index = (self.file, self.line)
        self.bpbynumber[self.number] = None   # No longer in list
        self.bplist[index].remove(self)
        if not self.bplist[index]:
            # No more bp for this f:l combo
            del self.bplist[index]

    def enable(self):
        self.enabled = 1

    def disable(self):
        self.enabled = 0

    def bpprint(self, out=None):
        if out is None:
            out = sys.stdout
        if self.temporary:
            disp = 'del  '
        else:
            disp = 'keep '
        if self.enabled:
            disp = disp + 'yes  '
        else:
            disp = disp + 'no   '
        print >>out, '%-4dbreakpoint   %s at %s:%d' % (self.number, disp,
                                                       self.file, self.line)
        if self.cond:
            print >>out, '\tstop only if %s' % (self.cond,)
        if self.ignore:
            print >>out, '\tignore next %d hits' % (self.ignore)
        if (self.hits):
            if (self.hits > 1): ss = 's'
            else: ss = ''
            print >>out, ('\tbreakpoint already hit %d time%s' %
                          (self.hits, ss))

# -----------end of Breakpoint class----------
