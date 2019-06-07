##############################################################################
#
# Copyright (c) 2010 ViFiB SARL and Contributors.
# All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.1 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#
##############################################################################

import argparse
import hashlib
import json
import logging
import os
import ssl
import shutil
import sys
import tarfile
import tempfile
import traceback
from base64 import b64encode, decodestring, encodestring
try:
  import configparser
  from http.client import HTTPConnection, HTTPSConnection
  from urllib.error import HTTPError
  from urllib.parse import urlsplit
  from urllib.request import urlopen
  basestring = bytes, str
except ImportError:
  import ConfigParser as configparser
  from httplib import HTTPConnection, HTTPSConnection
  from urllib2 import HTTPError, urlopen
  from urlparse import urlsplit
try:
  from OpenSSL import crypto
except ImportError:
  from . import crypto

# Timeout here is about timeout to CONNECT to the server (socket initialization then server answers actual data), not to retrieve/send informations.
# To be clear: it is NOT about uploading/downloading data, but about time to connect to the server, then time that server takes to start answering.
TIMEOUT = 60
# Same here. We just wait longer that, after having uploaded the file, the server digests it. It can take time.
UPLOAD_TIMEOUT = 60 * 60

logger = logging.getLogger('networkcache')
logger.setLevel(logging.INFO)


class short_exc_info(tuple):

  def __str__(self):
    t, v, tb = self
    filename, lineno, name, line = traceback.extract_tb(tb, 1)[0]
    l = ['%s:%s\n' % (filename, lineno)]
    l += traceback.format_exception_only(t, v)
    return ''.join(l).rstrip()

def strify(input):
  '''Transform every unicode string inside a list or dict into normal strings. '''
  if isinstance(input, dict):
    return dict((strify(key), strify(value)) for key, value in input.items())
  elif isinstance(input, list):
    return map(strify, input)
  elif isinstance(input, unicode):
    return input.encode('utf-8')
  else:
    return input
try:
  unicode
except NameError:
  def strify(input):
    return input

class CheckResponse(object):

  def __init__(self, response, sha512sum):
    self._response = response
    self._expected = sha512sum
    self._sha512sum = hashlib.sha512()

  def __getattr__(self, attr):
    if attr.startswith('_') or 'read' in attr:
      return object.__getattribute__(self, attr)
    return getattr(self._response, attr)

  def read(self, amt=None):
    r = self._response.read(amt)
    self._sha512sum.update(r)
    if (not r if amt else amt is None) and \
        self._expected != self._sha512sum.hexdigest():
      raise NetworkcacheException(
            'Failed to download data to SHACACHE Server: invalid checksum.')
    return r

class NetworkcacheClient(object):
  '''
    NetworkcacheClient is a wrapper for httplib.
    It must implement all the required methods to use:
     - SHADIR
     - SHACACHE
  '''
  signature_private_key = None

  def __init__(self, *args, **kw):
    """Initializes shacache object"""
    if isinstance(args[0], basestring) if args else 'config' not in kw:
      self.__old_init(*args, **kw) # BBB
    else:
      self.__new_init(*args, **kw)

  def __old_init(self, shacache, shadir, signature_private_key_file=None,
      signature_certificate_list=None, shacache_ca_file=None,
      shacache_key_file=None, shacache_cert_file=None,
      shadir_ca_file=None, shadir_key_file=None, shadir_cert_file=None):
    self.__new_init({
      'signature-private-key-file': signature_private_key_file,
      'download-cache-url': shacache,
      'upload-cache-url': shacache,
      'shacache-ca-file': shacache_ca_file,
      'shacache-cert-file': shacache_cert_file,
      'shacache-key-file': shacache_key_file,
      'download-dir-url': shadir,
      'upload-dir-url': shadir,
      'shadir-ca-file': shadir_ca_file,
      'shadir-cert-file': shadir_cert_file,
      'shadir-key-file': shadir_key_file,
      }, signature_certificate_list)

  def __new_init(self, config, signature_certificate_list=None):
    if not hasattr(config, 'get'):
      parser = configparser.SafeConfigParser()
      parser.readfp(config)
      config = dict(parser.items('networkcache'))
    self.config = config
    path = config.get('signature-private-key-file')
    if path:
      with open(path) as f:
        self.signature_private_key = crypto.load_privatekey(crypto.FILETYPE_PEM,
                                                            f.read())
    if signature_certificate_list is None:
      signature_certificate_list = config.get('signature-certificate-list')
    if type(signature_certificate_list) is str:
      # If signature_certificate_list is a string, parse it to a list of
      # certificates
      cert_marker = "-----BEGIN CERTIFICATE-----"
      signature_certificate_list = [cert_marker + '\n' + q.strip() \
        for q in signature_certificate_list.split(cert_marker) \
          if q.strip()]
    self.signature_certificate_list = [
      crypto.load_certificate(crypto.FILETYPE_PEM, certificate)
      for certificate in signature_certificate_list or ()]

  # NetworkcacheClient context manager catches all exceptions and logs them
  # with INFO severity. This provides a easy way to use a networkcache safely
  # since most of the time, failures are not fatal.

  def __enter__(self):
    return self

  def __exit__(self, t, v, tb):
    if isinstance(v, Exception):
      if isinstance(v, NetworkcacheException):
        logger.info(*v.args)
      else:
        logger.info("ignored unhandled exception at %s",
                    short_exc_info((t, v, tb)))
      return True

  def _request(self, where, name=None, data=None, headers=None):
    if data is None:
      method = 'GET'
      url = self.config['download-%s-url' % where]
      timeout = TIMEOUT
    else:
      method = 'PUT' if name else 'POST'
      url = self.config['upload-%s-url' % where]
      timeout = UPLOAD_TIMEOUT
    parsed_url = urlsplit(url.rstrip('/') + ('/' + name if name else ''))
    if not headers:
      headers = {}
    if parsed_url.username:
      headers['Authorization'] = 'Basic ' + b64encode('%s:%s' % (
        parsed_url.username, parsed_url.password))
    headers["Connection"] = "close"
    connection_kw = {
      'host': parsed_url.hostname,
      'port': parsed_url.port,
      'timeout': timeout,
    }
    if parsed_url.scheme == 'https':
      connection_kw['cert_file'] = self.config['sha%s-cert-file' % where]
      connection_kw['key_file'] = self.config['sha%s-key-file' % where]
      if hasattr(ssl, 'create_default_context'):
        connection_kw['context'] = ssl.create_default_context(
          cafile=self.config.get('sha%s-ca-file' % where)
        )
      connection = HTTPSConnection(**connection_kw)
    else:
      connection = HTTPConnection(**connection_kw)
    try:
      connection.request(method, parsed_url.path, data, headers)
      r = connection.getresponse()
      if 200 <= r.status < 300:
        return r
    finally:
      connection.close()
    raise HTTPError(url, r.status, r.reason, r.msg, r.fp)

  @staticmethod
  def archive(path):
    # Don't create it to /tmp dir as it can be too small.
    parent, name = os.path.split(path)
    f = tempfile.TemporaryFile(dir=parent)
    with tarfile.open(fileobj=f, mode="w:gz") as tar:
      tar.add(path, arcname=name)
    return f

  @staticmethod
  def extract(path, fileobj):
    path = os.path.dirname(path)
    f = None
    try:
      if not hasattr(fileobj, 'tell'):
        # WKRD: gzip decompressor wants a seekable stream.
        f = tempfile.TemporaryFile(dir=path)
        shutil.copyfileobj(fileobj, f)
        fileobj = f
        f.seek(0)
      with tarfile.open(fileobj=fileobj, mode="r:gz") as tar:
        tar.extractall(path=path)
    finally:
      f is None or f.close()

  def upload(self, file_descriptor, key=None, urlmd5=None, file_name=None,
                                    valid_until=None, architecture=None, **kw):
    ''' Upload the file to the server.
    If key is None it must only upload to SHACACHE.
    Otherwise, it must create a new entry on SHADIR.
    '''
    sha512sum = hashlib.sha512()
    f = None
    try:
      try:
        file_descriptor.seek(0)
      except Exception:
        f = tempfile.TemporaryFile()
        while 1:
            data = file_descriptor.read(65536)
            if not data:
                break
            f.write(data)
            sha512sum.update(data)
        file_descriptor = f
      else:
        while 1:
            data = file_descriptor.read(65536)
            if not data:
                break
            sha512sum.update(data)
      sha512sum = sha512sum.hexdigest()
      try:
        self._request('cache', sha512sum).close()
      except HTTPError:
        size = file_descriptor.tell()
        file_descriptor.seek(0)
        result = self._request('cache', data=file_descriptor, headers={
          'Content-Length': str(size),
          'Content-Type': 'application/octet-stream'})
        data = result.read()
        if result.status != 201 or data != sha512sum.encode():
          raise NetworkcacheException(
            'Failed to upload data to SHACACHE Server.'
            ' Response code: %s. Response data: %s' % (result.status, data))
    finally:
      f is None or f.close()

    if key is not None:
      kw['sha512'] = sha512sum # always update sha512sum
      file_name = kw.pop('file', file_name)
      if file_name is None or urlmd5 is None:
        raise NetworkcacheException(
          'file_name and urlmd5 are required for non-generic upload')
      if valid_until is not None:
        kw['valid-until'] = valid_until
      if architecture is not None:
        kw['architecture'] = architecture
      self.index(key, file=file_name, urlmd5=urlmd5, **kw)

    return sha512sum

  upload_generic = upload # BBB

  def index(self, key, **kw):
    data = json.dumps(kw)
    data = [data, self._getSignatureString(data.encode())]
    result = self._request('dir', key, json.dumps(data), {
      'Content-Type': 'application/json'})
    if result.status != 201:
      raise NetworkcacheException('Failed to upload data to SHADIR Server.'
                                  ' Response code: %s. Response data: %s'
                                  % (result.status, result.read()))

  def download(self, sha512sum):
    ''' Download the file.
    It uses http GET request method.
    '''
    return CheckResponse(self._request('cache', sha512sum), sha512sum)

  def select(self, key, wanted_metadata_dict={}, required_key_list=frozenset()):
    '''Return an iterator over shadir entries that match given criteria
    '''
    required_key_test = frozenset(required_key_list).issubset
    data_list = self.select_generic(key, self.signature_certificate_list)
    for information_json, signature in data_list:
      try:
        information_dict = strify(json.loads(information_json))
      except Exception:
        logger.info('Failed to parse json-in-json response (%r)',
                    information_json)
        continue
      try:
        len(information_dict['sha512'])
      except Exception:
        logger.info('Bad or missing sha512 in directory response (%r)',
                    information_dict)
        continue
      if required_key_test(information_dict):
        for k, v in wanted_metadata_dict.items():
          if information_dict.get(k) != v:
            break
        else:
          yield information_dict

  def select_generic(self, key, filter=True):
    ''' Select trustable entries from shadir.
    '''
    data = self._request('dir', key).read()
    try:
      data_list = json.loads(data.decode())
    except Exception:
      raise NetworkcacheException('Failed to parse json response (%r)' % data)
    if filter:
      return (data for data in data_list
                   if self._verifySignatureInCertificateList(*data))
    return data_list

  def _getSignatureString(self, content):
    """
      Return the signature based on certification file.
    """
    k = self.signature_private_key
    if k is None:
        return ''
    return encodestring(crypto.sign(k, content, 'sha1')).decode()

  def _verifySignatureInCertificateList(self, content, signature_string):
    """
      Returns true if it can find any valid certificate or false if it does not
      find any.
    """
    if signature_string:
      signature = decodestring(signature_string.encode())
      content = content.encode()
      for certificate in self.signature_certificate_list:
        try:
          crypto.verify(certificate, signature, content, 'sha1')
          return True
        except crypto.Error:
          pass
    return False


class NetworkcacheException(Exception):
  pass

DirectoryNotFound = UploadError = NetworkcacheException # BBB


def _newArgumentParser(url_help):
  parser = argparse.ArgumentParser()
  parser.add_argument('--config', type=argparse.FileType('r'), required=True,
    help='SlapOS configuration file.')
  parser.add_argument('--prefix-key', default='')
  parser.add_argument('--suffix-key', default='')
  parser.add_argument('--url', help=url_help
    + " The key will be concatenation of PREFIX_KEY, md5(URL) and SUFFIX_KEY."
    " If not given, the uploaded data is not indexed.")
  return parser

def cmd_upload(*args):
  parser = _newArgumentParser("Upload data pointed to by this argument,"
    " unless --file is specified. If argument is not a local path, contents"
    " is first downloaded in a temporary file.")
  parser.add_argument('--file',
    help="Upload the contents of this file, overriding --url")
  parser.add_argument('meta', nargs='*', metavar='KEY=VALUE',
    help="Extra metadata.")
  args = parser.parse_args(args or sys.argv[1:])
  nc = NetworkcacheClient(args.config)
  f = None
  try:
    if args.file:
      f = open(args.file, 'rb')
      if not args.url:
        nc.upload(f)
        return
    elif args.url:
      parser.error('either --file or --url is required')
    elif os.path.isdir(args.url):
      f = nc.archive(args.url)
    else:
      f = urlopen(args.url)
    urlmd5 = hashlib.md5(args.url.encode()).hexdigest()
    nc.upload(f, args.prefix_key + urlmd5 + args.suffix_key, urlmd5=urlmd5,
              file_name=os.path.basename(args.url) or "file",
              **dict(x.split('=', 1) for x in args.meta))
  finally:
    f is None or f.close()

def cmd_download(*args):
  parser = _newArgumentParser("URL of data to download.")
  args = parser.parse_args(args or sys.argv[1:])
  nc = NetworkcacheClient(args.config)
  urlmd5 = hashlib.md5(args.url.encode()).hexdigest()
  key = args.prefix_key + urlmd5 + args.suffix_key
  f = sys.stdout
  shutil.copyfileobj(nc.download(next(nc.select(key))['sha512']),
                     getattr(f, 'buffer', f))
