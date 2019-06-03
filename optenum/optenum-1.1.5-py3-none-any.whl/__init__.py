"""
optenum
==========

A missing python Enum/option lib supports enum code, name, text, even (code, name) tuple list and so on.

Compatible with Python 2.7+ and Python 3.0+.

Features:

  * Code - Enumration/option by different types - e.g. 0, 1, -1 (or 'new', 'running', 'stopped')
  * Name - Name of an enum/option - e.g.  'NEW', 'RUNNING', 'STOPPED'. Support dot access.
  * Text - Meaning or description of the enum/option. support i18n - e.g. _('new'), _('running'), _('stopped')
  * List - Retrieve list of code, name or text `[0, 1, -1]`
  * Dict - Retrieve dict of `{code: name}` mapping. even `{code: text}`, `{name: text}` mapping if required.
  * List of tuples - Retrieve list of `[(code, name), ...]` tuples. Useful in **Django** model.
  * Grouping - Group a set of enums/options. e.g. IN_PROGERSS_STATE = ['STARTING', 'STOPPING'], but 'STARTED' and 'STOPPED' are not belongs to it.
  * Access **name**, **text** by **code**
  * Lookup enum/option by **name**, **code**

"""

from __future__ import absolute_import
from .version import __version__
from .option import Option
from .options import Options, OptionGroup

__all__ = ('Option', 'Options', 'OptionGroup' '__version__')

__copyright__ = "Copyright (c) 2019 Samuel Chen (Chen Wei)"
__license__ = "MIT"
__summary__ = "A missing python Enum/option lib supports enum code, name, text, even (code, name) tuple list and so on."
__uri__ = "https://github.com/samuelchen/optenum.git"
