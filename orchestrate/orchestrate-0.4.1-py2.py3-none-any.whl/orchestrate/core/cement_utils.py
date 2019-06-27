from cement.ext.ext_argparse import ArgparseArgumentHandler as _ArgparseArgumentHandler
from cement.ext.ext_argparse import expose as _expose

from orchestrate.common import safe_format


# NOTE(taylor): `ignore_unknown_arguments` is passed to `ArgparseArgumentHandler`
# using the default implementation of `expose`. An issue arises when the argument handler
# is a subparser, because the root parser does not ignore unknown arguments.
# This is corrected by making the root parser ignore unknown arguments and raising
# an error for exposed methods that do not specify `ignore_unknown_arguments`.

class ArgparseArgumentHandler(_ArgparseArgumentHandler):
  class Meta(_ArgparseArgumentHandler.Meta):
    ignore_unknown_arguments = True

class expose(_expose):
  def __init__(self, ignore_unknown_arguments=False, **expose_kwargs):
    super(expose, self).__init__(**expose_kwargs)
    self.ignore_unknown_arguments = ignore_unknown_arguments

  def __call__(self, func):
    func = super(expose, self).__call__(func)
    if self.ignore_unknown_arguments:
      return func
    else:

      def impl(self, *args, **kwargs):
        if self.app.args.unknown_args:
          self.app.args.error(safe_format(
            'unrecognized arguments: {}',
            self.app.args.unknown_args,
          ))
        else:
          return func(self, *args, **kwargs)

      impl.__cement_meta__ = func.__cement_meta__
      return impl
