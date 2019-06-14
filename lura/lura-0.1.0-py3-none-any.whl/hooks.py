import sys
import traceback
from lura import logs

class Hooks:

  log = logs.get_logger(f'{__module__}.Hooks')

  def __init__(
    self,
    hooks = None,
  ):
    super().__init__()
    self.log.noise('__init__()')
    self.hooks = []
    if hooks:
      self.hooks.extend(hooks)

  def __iter__(self):
    self.log.noise('__iter__()')
    return self.hooks.__iter__()

  def handler(self, source, hook, signal, ev):
    self.log.noise(f'handler({source}, {signal}, {ev})')
    return getattr(hook, signal, None)

  def format_error(self, source, hook, signal, ev):
    self.log.noise('format_error()')
    msg = msg = "Hook '{}' raised exception for signal '{}', event '{}'"
    return msg.format(hook, signal, ev)

  def error(self, source, hook, signal, ev):
    self.log.noise('error()')
    print(self.format_error(source, hook, signal, ev), file=sys.stderr)
    traceback.print_exc()

  def missing(self, source, hook, signal, ev):
    self.log.noise(f'missing({source}, {hook}, {signal}, {ev})')
    # noop

  def __getattr__(self, signal):
    self.log.noise(f'__getattr__({signal})')
    def dispatch(source, ev, *args, **kwargs):
      self.log.noise(f'dispatch({source}, {ev})')
      for hook in self.hooks:
        fn = self.handler(source, hook, signal, ev)
        if not fn:
          self.missing(source, hook, signal, ev)
          continue
        try:
          fn(source, ev, *args, **kwargs)
        except Exception:
          self.error(source, hook, signal, ev)
    return dispatch

  def add(self, hook):
    self.log.noise(f'add({hook})')
    if hook not in self.hooks:
      self.hooks.append(hook)

  def remove(self, hook):
    self.log.noise(f'remove({hook})')
    if hook in self.hooks:
      self.hooks.remove(hook)

  def clear(self):
    self.log.noise('clear()')
    self.hooks.clear()
