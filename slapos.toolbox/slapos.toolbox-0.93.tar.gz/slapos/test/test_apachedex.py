##############################################################################
#
# Copyright (c) 2017 Vifib SARL and Contributors. All Rights Reserved.
#
# WARNING: This program as such is intended to be used by professional
# programmers who take the whole responsibility of assessing all potential
# consequences resulting from its eventual inadequacies and bugs
# End users who are looking for a ready-to-use solution with commercial
# guarantees and support are strongly adviced to contract a Free Software
# Service Company
#
# This program is Free Software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 3
# of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA  02111-1307, USA.
#
##############################################################################

import unittest
import os.path
import tempfile
import shutil
from datetime import date

from slapos.apachedex import build_command

class TestApachedexCommand(unittest.TestCase):
  def setUp(self):
    self.apachedex = "/bin/apachedex"
    self.today = date.today().strftime("%Y-%m-%d")
    _, self.acesslog1 = tempfile.mkstemp()
    _, self.acesslog2 = tempfile.mkstemp()

  def test_simpleCommand(self): 
    
    command = build_command(self.apachedex,
                            'foo.html',
                            [self.acesslog1, self.acesslog2],
                            '--default foo')
    self.assertEqual(command, ['/bin/apachedex',
                               '--js-embed',
                               '--out', 'foo.html',
                               '--default', 'foo',
                               '--error-detail', self.acesslog1, self.acesslog2 ])
 
  def test_complexCommand(self):
    command = build_command(self.apachedex,
                            'bar.html',
                            [self.acesslog1, self.acesslog2],
                            '--base bar foo --default foo')

    self.assertEqual(command, ['/bin/apachedex',
                               '--js-embed',
                               '--out', 'bar.html',
                               '--base', 'bar', 'foo',
                               '--default', 'foo',
                               '--error-detail', self.acesslog1, self.acesslog2 ])
  def test_raiseErro(self):
    self.assertRaises(ValueError, build_command, self.apachedex, 'foo.html', [])
if __name__ == '__main__':
  unittest.main()
