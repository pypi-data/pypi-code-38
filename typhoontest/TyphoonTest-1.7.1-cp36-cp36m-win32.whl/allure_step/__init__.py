"""
Custom step implementation
PR:

"""
from __future__ import unicode_literals
from __future__ import print_function
from __future__ import division
from __future__ import absolute_import
from builtins import map
from future import standard_library
standard_library.install_aliases()
from builtins import object
import sys
import six
import pandas


def represent(item):
    if sys.version_info.major < 3 and isinstance(item, str):
        try:
            item = item.decode(encoding='UTF-8')
        except UnicodeDecodeError:
            pass

    if isinstance(item, six.text_type):
        return u'\'%s\'' % item
    elif isinstance(item, (bytes, bytearray)):
        return repr(type(item))
    elif isinstance(item, pandas.Series):
        return item.name
    else:
        return repr(item)


import allure_commons.utils as utils
utils.represent = represent


from allure_commons._core import plugin_manager
from allure_commons.utils import uuid4
from allure_commons.utils import func_parameters
from functools import wraps
import allure


def step(dest=None, flatten=False, force=False):
    if callable(dest):
        return StepContext(dest.__name__, {}, flatten, force)(dest)
    else:
        return StepContext(dest, {}, flatten, force)


class StepContext(object):

    _flatten_active_steps = []
    _flattened_steps = []

    def __init__(self, title, params, flatten=False, force=False):
        self.title = title
        self.params = params
        self.uuid = uuid4()
        self.flatten = flatten
        self.force = force

    def __enter__(self):
        if (not self._flatten_active_steps) or self.force:
            plugin_manager.hook.start_step(uuid=self.uuid, title=self.title, params=self.params)
            if self.flatten:
                # skip child ones until step finishes
                self._flatten_active_steps.append(self.uuid)
        else:
            # skip
            self._flattened_steps.append(self.uuid)

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.uuid in self._flattened_steps:
            self._flattened_steps.remove(self.uuid)
        else:
            if self.uuid in self._flatten_active_steps:
                self._flatten_active_steps.remove(self.uuid)
            plugin_manager.hook.stop_step(uuid=self.uuid, title=self.title, exc_type=exc_type, exc_val=exc_val,
                                          exc_tb=exc_tb)

    def __call__(self, func):
        if self.title is None:
            self.title = func.__name__

        @wraps(func)
        def impl(*a, **kw):
            __tracebackhide__ = True
            params = func_parameters(func, *a, **kw)
            args = list(map(lambda x: represent(x), a))
            with StepContext(self.title.format(*args, **params), params, self.flatten, self.force):
                return func(*a, **kw)
        return impl


allure.step = step
