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
import socket
from slapos.promise.is_local_tcp_port_opened import isLocalTcpPortOpened


class TestLocalTcpPortOpened(unittest.TestCase):

  def test_port_is_not_open(self):
    self.assertEqual(isLocalTcpPortOpened("127.0.0.1",65550), False)

  def test_port6_is_not_open(self):
    self.assertEqual(isLocalTcpPortOpened("::1",65550), False)
 
  def test_port_is_open(self):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
      s.bind(("127.0.0.1", 0))
      s.listen(1)
      port = s.getsockname()[1]
      self.assertEqual(isLocalTcpPortOpened("127.0.0.1",port), True)
    finally:
      s.close()

  def test_port6_is_open(self):
    s = socket.socket(socket.AF_INET6, socket.SOCK_STREAM)
    try:
      s.bind(("::1", 0))
      s.listen(1)
      port = s.getsockname()[1]
      self.assertEqual(isLocalTcpPortOpened("::1",port), True)
    finally:
      s.close()

    
  
if __name__ == '__main__':
  unittest.main()
