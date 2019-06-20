#!/usr/bin/env python
# vim: set fileencoding=utf-8 :
# Laurent El Shafey <Laurent.El-Shafey@idiap.ch>
# Sun 20 Jan 18:36:00 2013
#
# Copyright (C) 2011-2013 Idiap Research Institute, Martigny, Switzerland
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, version 3 of the License.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.


"""Interface definition for Bob's database driver
"""

from bob.db.base.driver import Interface as AbstractInterface

class Interface(AbstractInterface):
  """Bob Manager interface for the Iris Flower Database"""

  def name(self):
    '''Returns a simple name for this database, w/o funny characters, spaces'''
    return 'wine'

  def files(self):
    '''Returns a python iterable with all auxiliary files needed.

    The values should be take w.r.t. where the python file that declares the
    database is sitting at.
    '''
    return []

  def version(self):
    '''Returns the current version number from Bob's build'''

    import pkg_resources  # part of setuptools
    version = pkg_resources.require("bob.db.wine")[0].version
    return version

  def type(self):
    '''Returns the type of auxiliary files you have for this database

    If you return 'sqlite', then we append special actions such as 'dbshell'
    on 'bob_dbmanage.py' automatically for you. Otherwise, we don't.

    If you use auxiliary text files, just return 'text'. We may provide
    special services for those types in the future.

    Use the special name 'builtin' if this database is an integral part of Bob.
    '''

    return 'builtin'

  def add_commands(self, parser):

    """A few commands this database can respond to."""

    from argparse import SUPPRESS
    from . import __doc__ as docs

    subparsers = self.setup_parser(parser, "Wine dataset", docs)

    # get the "dumplist" action from a submodule
    dump_message = "Dumps the database in comma-separate-value format"
    dump_parser = subparsers.add_parser('dump', help=dump_message)
    dump_parser.add_argument('-c', '--class', dest="cls", default='', help="if given, limits the dump to a particular subset of the data that corresponds to the given class (defaults to '%(default)s')", choices=('setosa', 'versicolor', 'virginica', ''))
    dump_parser.add_argument('--self-test', dest="selftest", default=False,
        action='store_true', help=SUPPRESS)

    from . import __dump__
    dump_parser.set_defaults(func=__dump__)
