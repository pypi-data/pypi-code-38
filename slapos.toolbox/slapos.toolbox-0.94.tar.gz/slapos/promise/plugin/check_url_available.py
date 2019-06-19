from zope import interface as zope_interface
from slapos.grid.promise import interface
from slapos.grid.promise.generic import GenericPromise

import requests


class RunPromise(GenericPromise):

  zope_interface.implements(interface.IPromise)

  def __init__(self, config):
    GenericPromise.__init__(self, config)
    # SR can set custom periodicity
    self.setPeriodicity(float(self.getConfig('frequency', 2)))

  def sense(self):
    """
      Check if frontend URL is available
    """

    url = self.getConfig('url')
    # make default time a max of 5 seconds, a bit smaller than promise-timeout
    # and in the same time at least 1 second
    default_timeout = max(
      1, min(5, int(self.getConfig('promise-timeout', 20)) - 1))
    timeout = int(self.getConfig('timeout', default_timeout))
    expected_http_code = int(self.getConfig('http_code', '200'))
    ca_cert_file = self.getConfig('ca-cert-file')
    cert_file = self.getConfig('cert-file')
    key_file = self.getConfig('key-file')
    verify = int(self.getConfig('verify', 0))

    if ca_cert_file:
      verify = ca_cert_file
    elif verify:
      verify = True
    else:
      verify = False

    if key_file and cert_file:
      cert = (cert_file, key_file)
    else:
      cert = None

    try:
      result = requests.get(
        url, verify=verify, allow_redirects=True, timeout=timeout, cert=cert)
    except requests.exceptions.SSLError as e:
      if 'certificate verify failed' in str(e.message):
        self.logger.error(
          "ERROR SSL verify failed while accessing %r" % (url,))
      else:
        self.logger.error(
          "ERROR Unknown SSL error %r while accessing %r" % (e, url))
      return
    except requests.ConnectionError as e:
      self.logger.error(
        "ERROR connection not possible while accessing %r" % (url, ))
      return
    except Exception, e:
      self.logger.error("ERROR: %s" % (e,))
      return

    http_code = result.status_code
    check_secure = int(self.getConfig('check-secure', 0))
    ignore_code = int(self.getConfig('ignore-code', 0))

    if http_code == 401 and check_secure == 1:
      self.logger.info("%r is protected (returned %s)." % (url, http_code))
    elif not ignore_code and http_code != expected_http_code:
      self.logger.error("%r is not available (returned %s, expected %s)." % (
        url, http_code, expected_http_code))
    else:
      self.logger.info("%r is available" % (url,))

  def anomaly(self):
    return self._test(result_count=3, failure_amount=3)
