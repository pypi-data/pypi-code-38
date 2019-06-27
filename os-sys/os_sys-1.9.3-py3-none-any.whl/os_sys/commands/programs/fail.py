import sys
import os
import warnings as w
import idlelib
import io

__all__ = ['warn_return', 'make_warn', 'print_warn', 'warn_msg', 'warning_msg', 'warn_file_no', 'msg', 'module_warn']
data = str(sys.version).split(' ')
class VersionError(Exception):
    'not the right python version'
int_data = str(data[0]).split('.')
if int(int_data[0]) >= 3 and int(int_data[1]) >= 0:
    pass
else:
    raise VersionError('you need python3 or newer')

def warn_return(message, category=None, stacklevel=1, source=None):
    """Issue a warning, or maybe ignore it or raise an exception."""
    # Check if message is already a Warning object
    if isinstance(message, Warning):
        category = message.__class__
    # Check category argument
    if category is None:
        category = UserWarning
    if not (isinstance(category, type) and issubclass(category, Warning)):
        raise TypeError("category must be a Warning subclass, "
                        "not '{:s}'".format(type(category).__name__))
    # Get context information
    try:
        if stacklevel <= 1 or _is_internal_frame(sys._getframe(1)):
            # If frame is too small to care or if the warning originated in
            # internal code, then do not try to hide any frames.
            frame = sys._getframe(stacklevel)
        else:
            frame = sys._getframe(1)
            # Look for one frame less since the above line starts us off.
            for x in range(stacklevel-1):
                frame = _next_external_frame(frame)
                if frame is None:
                    raise ValueError
    except ValueError:
        globals = sys.__dict__
        lineno = 1
    else:
        globals = frame.f_globals
        lineno = frame.f_lineno
    if '__name__' in globals:
        module = globals['__name__']
    else:
        module = "<string>"
    filename = globals.get('__file__')
    if filename:
        fnl = filename.lower()
        if fnl.endswith(".pyc"):
            filename = filename[:-1]
    else:
        if module == "__main__":
            try:
                filename = sys.argv[0]
            except AttributeError:
                # embedded interpreters don't have sys.argv, see bug #839151
                filename = '__main__'
        if not filename:
            filename = module
    registry = globals.setdefault("__warningregistry__", {})
    lis = filename.split('\\')
    ter = int(len(lis) - 1)
    file = lis[ter]
    return [{'msg': message, 'filepath': filename, 'file': file, 'line': lineno, 'module': module, 'reg': registry, 'globals': globals, 'source': source}, [message, category, filename, lineno, module, registry,
                  globals, source]]
    del globals

def make_warn(message, category=None, stacklevel=1, source=None):
    """Issue a warning, or maybe ignore it or raise an exception."""
    # Check if message is already a Warning object
    if isinstance(message, Warning):
        category = message.__class__
    # Check category argument
    if category is None:
        category = UserWarning
    if not (isinstance(category, type) and issubclass(category, Warning)):
        raise TypeError("category must be a Warning subclass, "
                        "not '{:s}'".format(type(category).__name__))
    # Get context information
    try:
        if stacklevel <= 1 or _is_internal_frame(sys._getframe(1)):
            # If frame is too small to care or if the warning originated in
            # internal code, then do not try to hide any frames.
            frame = sys._getframe(stacklevel)
        else:
            frame = sys._getframe(1)
            # Look for one frame less since the above line starts us off.
            for x in range(stacklevel-1):
                frame = _next_external_frame(frame)
                if frame is None:
                    raise ValueError
    except ValueError:
        globals = sys.__dict__
        lineno = 1
    else:
        globals = frame.f_globals
        lineno = frame.f_lineno
    if '__name__' in globals:
        module = globals['__name__']
    else:
        module = "<string>"
    filename = globals.get('__file__')
    if filename:
        fnl = filename.lower()
        if fnl.endswith(".pyc"):
            filename = filename[:-1]
    else:
        if module == "__main__":
            try:
                filename = sys.argv[0]
            except AttributeError:
                # embedded interpreters don't have sys.argv, see bug #839151
                filename = '__main__'
        if not filename:
            filename = module
    registry = globals.setdefault("__warningregistry__", {})
    lis = filename.split('\\')
    ter = int(len(lis) - 1)
    file = lis[ter]
    return {'msg': message, 'filepath': filename, 'file': file, 'line': lineno, 'module': module, 'mod': 'fail', 'reg': registry, 'globals': globals, 'source': source}
    del globals

warn_ = warn_return
class AError(Exception):
    'a exception was found'
class PingTimeoutError(Exception):
    'timeout'
class Woops_It_Looks_Like_That_Someting_Wents_Wrong_Error(Exception):
    'somting wents wrong'
class WifiError(Exception):
    'a wifi error is found'
class NoInternetAccesError(WifiError):
    'no internet acces'

import sys
class file():
    None

f = sys.stderr
def print_warn(*args#firts message, file, problem, becuse(optional), solution, msg
               ):
    lijst = list(args)
    try:
        values = dict(first=lijst[0],
                      file=lijst[1],
                      problem=lijst[2],
                      becuse=lijst[3],
                      solution=lijst[4],
                      msg=lijst[5],
                      )
    except Exception:
        values = dict(first=lijst[0],
                      file=lijst[1],
                      problem=lijst[2],
                      becuse='something is wrong',
                      solution=lijst[3],
                      msg=lijst[4],
                      )
    f = sys.stderr
    d = file
    print('warning!(from the fail module):', file=f)
    print('  %(first)s(most recent call):' % values, file=f)
    print('     where this warning is form %(file)s:' % values, file=f)
    print('       the problem is %(problem)s:' % values, file=f)
    print('         becuse %(becuse)s:' % values, file=f)
    print('           the solution may be %(solution)s:' % values, file=f)
    print('warning: %(msg)s' % values, file=f)

def warn_msg(msg):
    print('Warning!(from the fail module):
Warning(most recent call):
%s' % msg, file=f)
def warning_msg(first, msg):
    data = msg
    data['first'] = first
    print('Warning!(from the fail module):
 %(first)s(most recent call):
  in file %(file)s:
   in path %(filepath)s:
    in lineno %(line)s:
     from module %(module)s
      registry %(reg)s
       source is %(source)s
Warning: %(msg)s' % data, file=f)

def warn_file_no(first, msg):
    key = msg
    values = dict(msg=key['msg'], filepath=key['filepath'], file=key['file'], line=key['line'], first=first)
    print('Warning!(from the fail module):
\
 %(first)s (most recent call):
\
  from file %(file)s:
\
   in path %(filepath)s
\
    in line %(line)s
\
Warning: %(msg)s' % values, file=f)
def msg(**args):
    values = args
    '''args:
first
file
line
msg
'''
    print('Warning(from fail module):
\
 %(first)s(most recent call):
\
  from file %(file)s:
\
   from line %(line)s
\
Warning: %(msg)s' % values, file=f)


def module_warn(**args):
    values = args
    print('Warning!(from the fail module):
\
 %(first)s(most recent call):
\
  from file %(file)s:
\
   from module %(module)s:
\
Warning: %(msg)s' % values, file=f)

















