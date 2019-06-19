##############################################################################
#
# Copyright (c) 2015 Vifib SARL and Contributors. All Rights Reserved.
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
from slapos.networkbench import dnsbench
from slapos.networkbench.ping import ping, ping6
from slapos.networkbench.http import request


DNS_EXPECTED_LIST = ["85.118.38.162", "176.31.129.213"]

class TestDNSBench(unittest.TestCase):

  def test_dnsbench_ok(self):
    """
    Test dns resolution
    """
    info = dnsbench.resolve(
       "eu.web.vifib.com", DNS_EXPECTED_LIST)
  
    self.assertEqual(info[0], 'DNS')
    self.assertEqual(info[1], 'eu.web.vifib.com')
    self.assertEqual(info[2], 200)

    self.assertTrue(info[3] < 1)
    self.assertEqual(info[4], 'OK', 
          "%s != OK, full info: %s" % (info[4], info) )
    self.assertEqual(set(info[5]), set([u'85.118.38.162', u'176.31.129.213']),
          "%s != set([u'85.118.38.162', u'176.31.129.213']), full info: %s" % (set(info[5]), info))
    
  def test_dnsbench_fail(self):
    """ Test dns failure resolution
    """
    info = dnsbench.resolve(
       "thisdomaindontexist.erp5.com")
   
    self.assertEqual(info[0], 'DNS')
    self.assertEqual(info[1], 'thisdomaindontexist.erp5.com')
    self.assertEqual(info[2], 600)

    self.assertTrue(info[3] < 1)
    self.assertEqual(info[4], 'Cannot resolve the hostname')
    self.assertEqual(info[5], [])

  def test_dnsbench_unexpected(self):
    """ Test dns unexpected resolution
    """
    info = dnsbench.resolve(
       "www.erp5.com", [DNS_EXPECTED_LIST[0]])
   
    self.assertEqual(info[0], 'DNS')
    self.assertEqual(info[1], 'www.erp5.com')
    self.assertEqual(info[2], 200)

    self.assertTrue(info[3] < 1)
    self.assertEqual(info[4], 'UNEXPECTED')
    self.assertTrue(info[5].startswith("['85.118.38.162'] (expected) != "))

class TestPing(unittest.TestCase):

  def test_ping_ok(self):
    info = ping("localhost")
    self.assertEqual(info[0], 'PING')
    self.assertEqual(info[1], 'localhost')
    self.assertEqual(info[2], 200)
    self.assertTrue(float(info[3]) < 0.2)
    self.assertEqual(info[4], '0')
    self.assertTrue(info[5].startswith("min"))

  def test_ping_fail(self):
    info = ping("couscous")
    self.assertEqual(info[0], 'PING')
    self.assertEqual(info[1], 'couscous')
    self.assertEqual(info[2], 600)
    self.assertEqual(info[3], 'failed')
    self.assertEqual(info[4], -1)
    self.assertEqual(info[5], 'Fail to parser ping output')


  def test_ping6_ok(self):
    info = ping6("localhost")
    self.assertEqual(info[0], 'PING6')
    self.assertEqual(info[1], 'localhost')
    self.assertEqual(info[2], 200)
    self.assertTrue(float(info[3]) < 0.2)
    self.assertEqual(info[4], '0')
    self.assertTrue(info[5].startswith("min"))

  def test_ping6_fail(self):
    info = ping6("couscous")
    self.assertEqual(info[0], 'PING6')
    self.assertEqual(info[1], 'couscous')
    self.assertEqual(info[2], 600)
    self.assertEqual(info[3], 'failed')
    self.assertEqual(info[4], -1)
    self.assertEqual(info[5], 'Fail to parser ping output')


class TestHTTPBench(unittest.TestCase):

  def test_request_ok(self):
    """ This test is way to badly written as it depends on
        www.erp5.com for now, please replace it
    """
    info = request("https://www.erp5.com", {})

    self.assertEqual(info[0], 'GET')
    self.assertEqual(info[1], 'https://www.erp5.com')
    self.assertEqual(info[2], 200)
    self.assertEqual(len(info[3].split(';')), 5 )
    self.assertEqual(info[4], "OK")

  def test_request_expected_response(self):
    """ This test is way to badly written as it depends on
        www.erp5.com for now, please replace it
    """
    info = request("https://www.erp5.com", {"expected_response": 200})

    self.assertEqual(info[0], 'GET')
    self.assertEqual(info[1], 'https://www.erp5.com')
    self.assertEqual(info[2], 200)
    self.assertEqual(len(info[3].split(';')), 5 )
    self.assertEqual(info[4], "OK")

  def test_request_expected_redirection(self):
    """ This test is way to badly written as it depends on
        www.erp5.com for now, please replace it
    """
    info = request("http://www.erp5.com", {"expected_response": 302})

    self.assertEqual(info[0], 'GET')
    self.assertEqual(info[1], 'http://www.erp5.com')
    self.assertEqual(info[2], 302)
    self.assertEqual(len(info[3].split(';')), 5 )
    self.assertEqual(info[4], "OK")


  def test_request_expected_text(self):
    """ This test is way to badly written as it depends on
        www.erp5.com for now, please replace it
    """
    info = request("https://www.erp5.com", {"expected_text": "ERP5"})

    self.assertEqual(info[0], 'GET')
    self.assertEqual(info[1], 'https://www.erp5.com')
    self.assertEqual(info[2], 200)
    self.assertEqual(len(info[3].split(';')), 5 )
    self.assertEqual(info[4], "OK")


  def test_request_fail(self):
    """ Test unreachable URL
    """
    info = request("http://thisurldontexist.erp5.com", {})

    self.assertEqual(info[0], 'GET')
    self.assertEqual(info[1], 'http://thisurldontexist.erp5.com')
    self.assertEqual(info[2], 0)
    self.assertEqual(len(info[3].split(';')), 5 )
    self.assertEqual(info[4], "FAIL")

  def test_request_unexpected_response(self):
    """ This test is way to badly written as it depends on
        www.erp5.com for now, please replace it
    """
    info = request("http://www.erp5.com", {"expected_response": 200})

    self.assertEqual(info[0], 'GET')
    self.assertEqual(info[1], 'http://www.erp5.com')
    self.assertEqual(info[2], 302)
    self.assertEqual(len(info[3].split(';')), 5 )
    self.assertEqual(info[4], "UNEXPECTED (200 != 302)")

  def test_request_unexpected_text(self):
    """ This test is way to badly written as it depends on
        www.erp5.com for now, please replace it.
    """
    info = request("https://www.erp5.com", {"expected_text": "COUSCOUS"})

    self.assertEqual(info[0], 'GET')
    self.assertEqual(info[1], 'https://www.erp5.com')
    self.assertEqual(info[2], 200)
    self.assertEqual(len(info[3].split(';')), 5 )
    self.assertEqual(info[4], "UNEXPECTED (COUSCOUS not in page content)")



#def request(url, expected_dict):
#  
#  rendering_time = "%s;%s;%s;%s;%s" % \
#    (curl.getinfo(curl.NAMELOOKUP_TIME),
#     curl.getinfo(curl.CONNECT_TIME),
#     curl.getinfo(curl.PRETRANSFER_TIME),
#     curl.getinfo(curl.STARTTRANSFER_TIME),
#     curl.getinfo(curl.TOTAL_TIME))
#  
#  response_code = curl.getinfo(pycurl.HTTP_CODE)
#
#  expected_response = expected_dict.get("expected_response", None)
#  if expected_response is not None and \
#      expected_response != response_code:
#    result = "UNEXPECTED (%s != %s)" % (expected_response, response_code)
#
#  expected_text = expected_dict.get("expected_text", None)
#  if expected_text is not None and \
#      str(expected_text) not in str(body):
#    result = "UNEXPECTED (%s not in page content)" % (expected_text)
#
#
#  info_list = ('GET', url, response_code, rendering_time, result)
#
#  return info_list
#


  
if __name__ == '__main__':
  unittest.main()
