from __future__ import print_function

from fabric.tasks import WrappedCallableTask as _WrappedCallableTask

class WrappedCallableTask(_WrappedCallableTask):
    """
    A modified version of Fabric's WrappedCallableTask that sets a global
    dryrun variable from a task call.

    The variable is then removed from the function call, allowing all wrapped
    function calls to implicitly use the keyword argument.
    """

    def __init__(self, *args, **kwargs):
        real_module = kwargs.pop('real_module', None)
        super(WrappedCallableTask, self).__init__(*args, **kwargs)
        if real_module:
            self.__module__ = real_module

    def __call__(self, *args, **kwargs):
        from burlap.common import set_dryrun, set_verbose
        if 'dryrun' in kwargs:
            set_dryrun(kwargs['dryrun'])
            del kwargs['dryrun']
        if 'verbose' in kwargs:
            set_verbose(kwargs['verbose'])
            del kwargs['verbose']
        return self.run(*args, **kwargs)

    def run(self, *args, **kwargs):
        from burlap.common import set_dryrun, set_verbose
        if 'dryrun' in kwargs:
            set_dryrun(kwargs['dryrun'])
            del kwargs['dryrun']
        if 'verbose' in kwargs:
            set_verbose(kwargs['verbose'])
            del kwargs['verbose']
        return self.wrapped(*args, **kwargs)
