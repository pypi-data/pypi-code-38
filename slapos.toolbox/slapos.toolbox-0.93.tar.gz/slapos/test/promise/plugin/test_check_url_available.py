##############################################################################
#
# Copyright (c) 2019 Vifib SARL and Contributors. All Rights Reserved.
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

from slapos.grid.promise import PromiseError
from slapos.test.promise.plugin import TestPromisePluginMixin

from cryptography import x509
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.x509.oid import NameOID
import BaseHTTPServer
import datetime
import ipaddress
import json
import multiprocessing
import os
import ssl
import tempfile
import time
import unittest

SLAPOS_TEST_IPV4 = os.environ.get('SLAPOS_TEST_IPV4', '127.0.0.1')
SLAPOS_TEST_IPV4_PORT = 57965
HTTPS_ENDPOINT = "https://%s:%s/" % (SLAPOS_TEST_IPV4, SLAPOS_TEST_IPV4_PORT)


def createKey():
  key = rsa.generate_private_key(
    public_exponent=65537, key_size=2048, backend=default_backend())
  key_pem = key.private_bytes(
    encoding=serialization.Encoding.PEM,
    format=serialization.PrivateFormat.TraditionalOpenSSL,
    encryption_algorithm=serialization.NoEncryption()
  )
  return key, key_pem


def createCSR(common_name, ip=None):
  key, key_pem = createKey()
  subject_alternative_name_list = []
  if ip is not None:
    subject_alternative_name_list.append(
      x509.IPAddress(ipaddress.ip_address(unicode(ip)))
    )
  csr = x509.CertificateSigningRequestBuilder().subject_name(x509.Name([
     x509.NameAttribute(NameOID.COMMON_NAME, unicode(common_name)),
  ]))

  if len(subject_alternative_name_list):
    csr = csr.add_extension(
      x509.SubjectAlternativeName(subject_alternative_name_list),
      critical=False
    )

  csr = csr.sign(key, hashes.SHA256(), default_backend())
  csr_pem = csr.public_bytes(serialization.Encoding.PEM)
  return key, key_pem, csr, csr_pem


class CertificateAuthority(object):
  def __init__(self, common_name):
    self.key, self.key_pem = createKey()
    public_key = self.key.public_key()
    builder = x509.CertificateBuilder()
    builder = builder.subject_name(x509.Name([
      x509.NameAttribute(NameOID.COMMON_NAME, unicode(common_name)),
    ]))
    builder = builder.issuer_name(x509.Name([
      x509.NameAttribute(NameOID.COMMON_NAME, unicode(common_name)),
    ]))
    builder = builder.not_valid_before(
      datetime.datetime.utcnow() - datetime.timedelta(days=2))
    builder = builder.not_valid_after(
      datetime.datetime.utcnow() + datetime.timedelta(days=30))
    builder = builder.serial_number(x509.random_serial_number())
    builder = builder.public_key(public_key)
    builder = builder.add_extension(
      x509.BasicConstraints(ca=True, path_length=None), critical=True,
    )
    self.certificate = builder.sign(
      private_key=self.key, algorithm=hashes.SHA256(),
      backend=default_backend()
    )
    self.certificate_pem = self.certificate.public_bytes(
      serialization.Encoding.PEM)

  def signCSR(self, csr):
    builder = x509.CertificateBuilder(
      subject_name=csr.subject,
      extensions=csr.extensions,
      issuer_name=self.certificate.subject,
      not_valid_before=datetime.datetime.utcnow() - datetime.timedelta(days=1),
      not_valid_after=datetime.datetime.utcnow() + datetime.timedelta(days=30),
      serial_number=x509.random_serial_number(),
      public_key=csr.public_key(),
    )
    certificate = builder.sign(
      private_key=self.key,
      algorithm=hashes.SHA256(),
      backend=default_backend()
    )
    return certificate, certificate.public_bytes(serialization.Encoding.PEM)


class TestHandler(BaseHTTPServer.BaseHTTPRequestHandler):
  def do_GET(self):
    path = self.path.split('/')[-1]
    if '_' in path:
      response, timeout = path.split('_')
      response = int(response)
      timeout = int(timeout)
    else:
      timeout = 0
      response = int(path)

    time.sleep(timeout)
    self.send_response(response)

    self.send_header("Content-type", "application/json")
    self.end_headers()
    response = {
      'Path': self.path,
    }
    self.wfile.write(json.dumps(response, indent=2))


class CheckUrlAvailableMixin(TestPromisePluginMixin):
  @classmethod
  def setUpClass(cls):
    cls.another_server_ca = CertificateAuthority("Another Server Root CA")
    cls.test_server_ca = CertificateAuthority("Test Server Root CA")
    key, key_pem, csr, csr_pem = createCSR(
      "testserver.example.com", SLAPOS_TEST_IPV4)
    _, cls.test_server_certificate_pem = cls.test_server_ca.signCSR(csr)

    cls.test_server_certificate_file = tempfile.NamedTemporaryFile(
      delete=False
    )

    cls.test_server_certificate_file.write(
        cls.test_server_certificate_pem + key_pem
      )
    cls.test_server_certificate_file.close()

    cls.test_server_ca_certificate_file = tempfile.NamedTemporaryFile(
      delete=False
    )
    cls.test_server_ca_certificate_file.write(
       cls.test_server_ca.certificate_pem)
    cls.test_server_ca_certificate_file.close()

    server = BaseHTTPServer.HTTPServer(
      (SLAPOS_TEST_IPV4, SLAPOS_TEST_IPV4_PORT),
      TestHandler)

    server.socket = ssl.wrap_socket(
      server.socket,
      certfile=cls.test_server_certificate_file.name,
      server_side=True)

    cls.server_process = multiprocessing.Process(
      target=server.serve_forever)
    cls.server_process.start()

  @classmethod
  def tearDownClass(cls):
    cls.server_process.terminate()
    cls.server_process.join()
    for p in [
      cls.test_server_certificate_file.name,
      cls.test_server_ca_certificate_file.name,
    ]:
      try:
        os.unlink(p)
      except Exception:
        pass

  def setUp(self):
    TestPromisePluginMixin.setUp(self)
    self.promise_name = "check-url-available.py"

    self.base_content = """from slapos.promise.plugin.check_url_available import RunPromise

extra_config_dict = {
  'url': '%(url)s',
  'timeout': %(timeout)s,
  'check-secure': %(check_secure)s,
  'ignore-code': %(ignore_code)s,
}
"""

    self.base_content_verify = """from slapos.promise.plugin.check_url_available import RunPromise

extra_config_dict = {
  'url': '%(url)s',
  'timeout': %(timeout)s,
  'check-secure': %(check_secure)s,
  'ignore-code': %(ignore_code)s,
  'verify': %(verify)s,
}
"""

    self.base_content_ca_cert = """from slapos.promise.plugin.check_url_available import RunPromise

extra_config_dict = {
  'url': '%(url)s',
  'timeout': %(timeout)s,
  'check-secure': %(check_secure)s,
  'ignore-code': %(ignore_code)s,
  'ca-cert-file': %(ca_cert_file)r,
}
"""

    self.base_content_http_code = """from slapos.promise.plugin.check_url_available import RunPromise

extra_config_dict = {
  'url': '%(url)s',
  'timeout': %(timeout)s,
  'check-secure': %(check_secure)s,
  'ignore-code': %(ignore_code)s,
  'http_code': %(http_code)s
}
"""

  def tearDown(self):
    TestPromisePluginMixin.tearDown(self)


class TestCheckUrlAvailable(CheckUrlAvailableMixin):

  def test_check_url_bad(self):
    content = self.base_content % {
      'url': 'https://',
      'timeout': 10,
      'check_secure': 0,
      'ignore_code': 0,
    }
    self.writePromise(self.promise_name, content)
    self.configureLauncher()
    with self.assertRaises(PromiseError):
      self.launcher.run()
    result = self.getPromiseResult(self.promise_name)
    self.assertEqual(result['result']['failed'], True)
    self.assertEqual(
      result['result']['message'],
      "ERROR: Invalid URL u'https://': No host supplied"
    )

  def test_check_url_malformed(self):
    content = self.base_content % {
      'url': '',
      'timeout': 10,
      'check_secure': 0,
      'ignore_code': 0,
    }
    self.writePromise(self.promise_name, content)
    self.configureLauncher()
    with self.assertRaises(PromiseError):
      self.launcher.run()
    result = self.getPromiseResult(self.promise_name)
    self.assertEqual(result['result']['failed'], True)
    self.assertEqual(
      result['result']['message'],
      "ERROR: Invalid URL '': No schema supplied. Perhaps you meant http://?"
    )

  def test_check_url_site_off(self):
    content = self.base_content % {
      'url': 'https://localhost:56789/site',
      'timeout': 10,
      'check_secure': 0,
      'ignore_code': 0,
    }
    self.writePromise(self.promise_name, content)
    self.configureLauncher()
    with self.assertRaises(PromiseError):
      self.launcher.run()
    result = self.getPromiseResult(self.promise_name)
    self.assertEqual(result['result']['failed'], True)
    self.assertEqual(
      result['result']['message'],
      "ERROR connection not possible while accessing "
      "'https://localhost:56789/site'"
    )

  def test_check_200(self):
    url = HTTPS_ENDPOINT + '200'
    content = self.base_content % {
      'url': url,
      'timeout': 10,
      'check_secure': 0,
      'ignore_code': 0,
    }
    self.writePromise(self.promise_name, content)
    self.configureLauncher()
    self.launcher.run()
    result = self.getPromiseResult(self.promise_name)
    self.assertEqual(result['result']['failed'], False)
    self.assertEqual(
      result['result']['message'],
      "%r is available" % (url,)
    )

  def test_check_200_verify(self):
    url = HTTPS_ENDPOINT + '200'
    content = self.base_content_verify % {
      'url': url,
      'timeout': 10,
      'check_secure': 0,
      'ignore_code': 0,
      'verify': 1,
    }
    try:
      old = os.environ.get('REQUESTS_CA_BUNDLE')
      # simulate system provided CA bundle
      os.environ[
        'REQUESTS_CA_BUNDLE'] = self.test_server_ca_certificate_file.name
      self.writePromise(self.promise_name, content)
      self.configureLauncher()
      self.launcher.run()
    finally:
      if old is None:
        del os.environ['REQUESTS_CA_BUNDLE']
      else:
        os.environ['REQUESTS_CA_BUNDLE'] = old

    result = self.getPromiseResult(self.promise_name)
    self.assertEqual(result['result']['failed'], False)
    self.assertEqual(
      result['result']['message'],
      "%r is available" % (url,)
    )

  def test_check_200_verify_fail(self):
    url = HTTPS_ENDPOINT + '200'
    content = self.base_content_verify % {
      'url': url,
      'timeout': 10,
      'check_secure': 0,
      'ignore_code': 0,
      'verify': 1,
    }
    self.writePromise(self.promise_name, content)
    self.configureLauncher()
    with self.assertRaises(PromiseError):
      self.launcher.run()
    result = self.getPromiseResult(self.promise_name)
    self.assertEqual(result['result']['failed'], True)
    self.assertEqual(
      result['result']['message'],
      "ERROR SSL verify failed while accessing %r" % (url,)
    )

  def test_check_200_verify_own(self):
    url = HTTPS_ENDPOINT + '200'
    content = self.base_content_ca_cert % {
      'url': url,
      'timeout': 10,
      'check_secure': 0,
      'ignore_code': 0,
      'ca_cert_file': self.test_server_ca_certificate_file.name
    }
    self.writePromise(self.promise_name, content)
    self.configureLauncher()
    self.launcher.run()
    result = self.getPromiseResult(self.promise_name)
    self.assertEqual(result['result']['failed'], False)
    self.assertEqual(
      result['result']['message'],
      "%r is available" % (url,)
    )

  def test_check_401(self):
    url = HTTPS_ENDPOINT + '401'
    content = self.base_content % {
      'url': url,
      'timeout': 10,
      'check_secure': 0,
      'ignore_code': 0,
    }
    self.writePromise(self.promise_name, content)
    self.configureLauncher()
    with self.assertRaises(PromiseError):
      self.launcher.run()
    result = self.getPromiseResult(self.promise_name)
    self.assertEqual(result['result']['failed'], True)
    self.assertEqual(
      result['result']['message'],
      "%r is not available (returned 401, expected 200)." % (url,)
    )

  def test_check_401_ignore_code(self):
    url = HTTPS_ENDPOINT + '401'
    content = self.base_content % {
      'url': url,
      'timeout': 10,
      'check_secure': 0,
      'ignore_code': 1,
    }
    self.writePromise(self.promise_name, content)
    self.configureLauncher()
    self.launcher.run()
    result = self.getPromiseResult(self.promise_name)
    self.assertEqual(result['result']['failed'], False)
    self.assertEqual(
      result['result']['message'],
      "%r is available" % (url,)
    )

  def test_check_401_check_secure(self):
    url = HTTPS_ENDPOINT + '401'
    content = self.base_content % {
      'url': url,
      'timeout': 10,
      'check_secure': 1,
      'ignore_code': 0,
    }
    self.writePromise(self.promise_name, content)
    self.configureLauncher()
    self.launcher.run()
    result = self.getPromiseResult(self.promise_name)
    self.assertEqual(result['result']['failed'], False)
    self.assertEqual(
      result['result']['message'],
      "%r is protected (returned 401)." % (url,)
    )

  def test_check_512_http_code(self):
    url = HTTPS_ENDPOINT + '512'
    content = self.base_content_http_code % {
      'url': url,
      'timeout': 10,
      'check_secure': 0,
      'ignore_code': 0,
      'http_code': 512,
    }
    self.writePromise(self.promise_name, content)
    self.configureLauncher()
    self.launcher.run()
    result = self.getPromiseResult(self.promise_name)
    self.assertEqual(result['result']['failed'], False)
    self.assertEqual(
      result['result']['message'],
      "%r is available" % (url,)
    )


class TestCheckUrlAvailableTimeout(CheckUrlAvailableMixin):
  def test_check_200_timeout(self):
    url = HTTPS_ENDPOINT + '200_5'
    content = self.base_content % {
      'url': url,
      'timeout': 1,
      'check_secure': 0,
      'ignore_code': 0,
    }
    self.writePromise(self.promise_name, content)
    self.configureLauncher()
    with self.assertRaises(PromiseError):
      self.launcher.run()
    result = self.getPromiseResult(self.promise_name)
    self.assertEqual(result['result']['failed'], True)
    self.assertEqual(
      result['result']['message'],
      "Error: Promise timed out after 0.5 seconds",
    )


if __name__ == '__main__':
  unittest.main()
