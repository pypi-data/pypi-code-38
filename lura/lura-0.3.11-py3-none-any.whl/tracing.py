import inspect
import sys
import threading
from lura.hooks import Hooks
from io import StringIO

def trace(frame, ev, arg):
  if ev == 'call':
    trace.hooks.call(trace, 'call', frame, ev, arg)
  elif ev == 'exception':
    trace.hooks.exc(trace, 'exc', frame, ev, arg)

trace.hooks = Hooks()

def set_trace(enabled):
  if enabled:
    if sys.gettrace() != trace:
      sys.settrace(trace)
    if threading._trace_hook != trace:
      threading.settrace(trace)
  else:
    if sys.gettrace() == trace:
      sys.settrace(None)
    if threading._trace_hook == trace:
      threading.settrace(None)

trace.set_trace = set_trace

def get_trace():
  return sys.gettrace() == trace

trace.get_trace = get_trace

class TraceHook:

  def __init__(self, module_prefix):
    super().__init__()
    self.module_prefix = module_prefix

  def echo(self, msg):
    print(msg, file=sys.stderr)

  def get_call_data_(self, frame):
    funcname = frame.f_code.co_name
    arginfo = inspect.getargvalues(frame)
    module = None
    cls = None
    args = []
    varargs = []
    kwargs = []
    if arginfo.args:
      argnames = list(arginfo.args)
      if argnames[0] == 'self':
        _ = type(arginfo.locals['self'])
        module = _.__module__
        cls = _.__name__
        del argnames[0]
      elif argnames[0] == 'cls':
        _ = arginfo.locals['cls']
        module = _.__module__
        cls = _.__name__
        del argnames[0]
      args = [f'{_}={repr(arginfo.locals[_])}' for _ in argnames]
    if arginfo.varargs is not None:
      varargs = [repr(_) for _ in arginfo.locals[arginfo.varargs]]
    if arginfo.keywords is not None:
      kwargs = [
        f'{repr(k)}: {repr(v)}'
        for k, v in arginfo.locals[arginfo.keywords].items()
      ]
    if module is None:
      module = inspect.getmodule(frame.f_code)
      module = '__none__' if module is None else module.__name__
    return module, cls, funcname, args, varargs, kwargs

  def format_call_data_(self, module, cls, funcname, args, varargs, kwargs):
    buf = StringIO()
    w = buf.write
    if cls:
      w(f'{module}.{cls}.{funcname}(')
    else:
      w(f'{module}.{funcname}(')
    if args:
      w(', '.join(args))
    if varargs:
      if args:
        w(', ')
      w(f'*args=({", ".join(varargs)})')
    if kwargs:
      if args or varargs:
        w(', ')
      w(f'**kwargs={{{", ".join(kwargs)}}}')
    w(')')
    result = buf.getvalue()
    buf.close()
    return result

  def filter_call(self, frame, ev, arg):
    module = inspect.getmodule(frame.f_code)
    if module is None:
      return True
    modname = module.__name__
    prefix = self.module_prefix
    if isinstance(prefix, str):
      prefix = [prefix]
    return not any(modname.startswith(_) for _ in prefix)


  def call(self, o, e, frame, ev, arg):
    if self.filter_call(frame, ev, arg):
      return
    data = self.get_call_data_(frame)
    msg = self.format_call_data_(*data)
    self.echo(msg)

  def exc(self, o, e, frame, ev, arg):
    pass

trace.TraceHook = TraceHook
