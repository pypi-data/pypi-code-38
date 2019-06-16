# -*- coding: utf-8; -*-
################################################################################
#
#  Rattail -- Retail Software Framework
#  Copyright © 2010-2019 Lance Edgar
#
#  This file is part of Rattail.
#
#  Rattail is free software: you can redistribute it and/or modify it under the
#  terms of the GNU General Public License as published by the Free Software
#  Foundation, either version 3 of the License, or (at your option) any later
#  version.
#
#  Rattail is distributed in the hope that it will be useful, but WITHOUT ANY
#  WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
#  FOR A PARTICULAR PURPOSE.  See the GNU General Public License for more
#  details.
#
#  You should have received a copy of the GNU General Public License along with
#  Rattail.  If not, see <http://www.gnu.org/licenses/>.
#
################################################################################
"""
Utilities
"""

from __future__ import unicode_literals, absolute_import
from __future__ import division

import sys
import datetime
import decimal
import subprocess

import six
from pkg_resources import iter_entry_points

try:
    from collections import OrderedDict
except ImportError: # pragma no cover
    from ordereddict import OrderedDict


# generic singleton to indicate an arg which isn't set etc.
NOTSET = object()


def capture_output(command):
    """
    Runs ``command`` and returns any output it produces.
    """
    # We *need* to pipe ``stdout`` because that's how we capture the output of
    # the ``hg`` command.  However, we must pipe *all* handles in order to
    # prevent issues when running as a GUI but *from* the Windows console.  See
    # also: http://bugs.python.org/issue3905
    kwargs = dict(stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    output = subprocess.Popen(command, **kwargs).communicate()[0]
    return output


def data_diffs(local_data, host_data, fields=None):
    """
    Find all (relevant) fields which differ between the host and local data
    values for a given record.
    """
    if fields is None:
        fields = list(local_data)
    diffs = []
    for field in fields:
        if local_data[field] != host_data[field]:
            diffs.append(field)
    return diffs


def import_module_path(module_path):
    """
    Import an arbitrary Python module.

    :param module_path: String referencing a module by its "dotted path".

    :returns: The referenced module.
    """
    if module_path in sys.modules:
        return sys.modules[module_path]
    module = __import__(module_path)

    def last_module(module, module_path):
        parts = module_path.split('.')
        parts.pop(0)
        child = getattr(module, parts[0])
        if len(parts) == 1:
            return child
        return last_module(child, '.'.join(parts))

    return last_module(module, module_path)


def get_object_spec(obj):
    """
    Returns the "object spec" string for the given object.
    """
    # TODO: this only handles a class *instance* currently
    return '{}:{}'.format(obj.__module__, obj.__class__.__name__)


def load_object(specifier):
    """
    Load an arbitrary object from a module, according to a specifier.

    The specifier string should contain a dotted path to an importable module,
    followed by a colon (``':'``), followed by the name of the object to be
    loaded.  For example:

    .. code-block:: none

       rattail.files:overwriting_move

    You'll notice from this example that "object" in this context refers to any
    valid Python object, i.e. not necessarily a class instance.  The name may
    refer to a class, function, variable etc.  Once the module is imported, the
    ``getattr()`` function is used to obtain a reference to the named object;
    therefore anything supported by that method should work.

    :param specifier: Specifier string.

    :returns: The specified object.
    """
    module_path, name = specifier.split(':')
    module = import_module_path(module_path)
    return getattr(module, name)


def load_entry_points(group):
    """
    Load a set of ``setuptools``-style entry points.

    This is a convenience wrapper around ``pkg_resources.iter_entry_points()``.

    :param group: The group of entry points to be loaded.

    :returns: A dictionary whose keys are the entry point names, and values are
       the loaded entry points.
    """
    entry_points = {}
    for entry_point in iter_entry_points(group):
        entry_points[entry_point.name] = entry_point.load()
    return entry_points


def prettify(text):
    """
    Return a "prettified" version of text.
    """
    text = text.replace('_', ' ')
    text = text.replace('-', ' ')
    words = text.split()
    return ' '.join([x.capitalize() for x in words])


def pretty_boolean(value):
    """
    Returns ``'Yes'`` or ``'No'`` or empty string if value is ``None``
    """
    if value is None:
        return ""
    return "Yes" if value else "No"


def hours_as_decimal(hours, places=2):
    """
    Convert the given ``datetime.timedelta`` object into a Decimal whose
    value is in terms of hours.
    """
    if hours is None:
        return
    minutes = (hours.days * 1440) + (hours.seconds // 60)
    fmt = '{{:0.{}f}}'.format(places)
    return decimal.Decimal(fmt.format(minutes / 60.0))


def pretty_hours(hours=None, seconds=None):
    """
    Format the given ``hours`` value (which is assumed to be a
    ``datetime.timedelta`` object) as HH:MM.  Note that instead of providing
    that, you can provide ``seconds`` instead and a delta will be generated.
    """
    if hours is None and seconds is None:
        return ''
    if hours is None:
        hours = datetime.timedelta(seconds=seconds)

    # determine if hours value is positive or negative.  seems like some of the
    # math can be "off" if negative values are involved, in which case we'll
    # convert to positive for sake of math and then prefix result with a hyphen
    negative = False

    if isinstance(hours, decimal.Decimal):
        if hours < 0:
            negative = True
            hours = -hours
        hours = datetime.timedelta(seconds=int(hours * 3600))

    minutes = (hours.days * 1440) + (hours.seconds / 60)
    rendered = "{}:{:02d}".format(int(minutes // 60), int(minutes % 60))
    if negative:
        rendered = "-{}".format(rendered)
    return rendered


def pretty_quantity(value, empty_zero=False):
    """
    Return a "pretty" version of the given value, as string.  This is meant primarily
    for use with things like order quantities, so that e.g. 1.0000 => 1
    """
    if value is None:
        return ''
    if int(value) == value:
        value = int(value)
        if empty_zero and value == 0:
            return ''
        return six.text_type(value)
    return six.text_type(value).rstrip('0')


def progress_loop(func, items, factory, *args, **kwargs):
    """
    This will iterate over ``items`` and call ``func`` for each.  If a progress
    ``factory`` kwarg is provided, then a progress instance will be created and
    updated along the way.
    """
    message = kwargs.pop('message', None)
    count = kwargs.pop('count', None)
    allow_cancel = kwargs.pop('allow_cancel', False)
    if count is None:
        try:
            count = len(items)
        except TypeError:
            count = items.count()
    if not count:
        return True

    prog = None
    if factory:
        prog = factory(message, count)

    canceled = False
    for i, item in enumerate(items, 1):
        func(item, i, *args, **kwargs)
        if prog and not prog.update(i):
            canceled = True
            break
    if prog:
        prog.finish()
    if canceled and not allow_cancel:
        raise RuntimeError("Operation was canceled")
    return not canceled
