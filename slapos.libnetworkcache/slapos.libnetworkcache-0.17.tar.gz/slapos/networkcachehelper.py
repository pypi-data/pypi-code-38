##############################################################################
#
# Copyright (c) 2012 ViFiB SARL and Contributors.
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

# BBB: Deprecated. This file is ugly and must disappear.
#      DO NOT EXTEND IT. Add methods to NetworkcacheClient class instead.

import os
import shutil
from slapos.libnetworkcache import NetworkcacheClient, logger

def __upload_network_cached(dir_url, cache_url,
    file_descriptor, directory_key,
    signature_private_key_file, shacache_ca_file, shacache_cert_file,
    shacache_key_file, shadir_ca_file, shadir_cert_file,
    shadir_key_file, metadata_dict={}):
  """
  Upload content of a file descriptor to a network cache server using
  shacache/shadir API.
  It will upload file_descriptor content to server using directory_key as
  shacache key, and metadata_dict as shadir metadata if specified.

  Return True if successfull, False otherwise.
  """
  if not (dir_url and cache_url):
    return False

  # backward compatibility
  metadata_dict.setdefault('file', 'notused')
  metadata_dict.setdefault('urlmd5', 'notused')

  # convert '' into None in order to call nc nicely
  with NetworkcacheClient(cache_url, dir_url,
        signature_private_key_file=signature_private_key_file or None,
        shacache_ca_file=shacache_ca_file or None,
        shacache_cert_file=shacache_cert_file or None,
        shacache_key_file=shacache_key_file or None,
        shadir_ca_file=shadir_ca_file or None,
        shadir_cert_file=shadir_cert_file or None,
        shadir_key_file=shadir_key_file or None,
      ) as nc:
    return nc.upload(file_descriptor, directory_key, **metadata_dict)

def helper_upload_network_cached_from_directory(dir_url, cache_url,
    path, directory_key, metadata_dict,
    signature_private_key_file, shacache_ca_file, shacache_cert_file,
    shacache_key_file, shadir_ca_file, shadir_cert_file, shadir_key_file):
  """
  Create a tar from a given directory (path) then upload it to networkcache.
  """
  return __upload_network_cached(dir_url, cache_url,
      NetworkcacheClient.archive(path.rstrip(os.sep)), directory_key,
      signature_private_key_file, shacache_ca_file, shacache_cert_file,
      shacache_key_file, shadir_ca_file, shadir_cert_file, shadir_key_file,
      metadata_dict)


def helper_download_network_cached(dir_url, cache_url,
    signature_certificate_list,
    directory_key, wanted_metadata_dict={}, required_key_list=[],
    strategy=None):
  """
  Downloads from a network cache provider.
  Select from shadir directory_key entry matching (at least)
  wanted_metadata_dict and with all metadata keys in required_key_list defined
  and not null.

  if a "strategy" function is given as parameter, use it to choose the best
  entry between list of matching entries. Otherwise, choose the first.
  This strategy function takes a list of entries as parameter, and should
  return the best entry.

  If something fails (providor be offline, or hash_string fail), we ignore
  network cached index.

  return (file_descriptor, metadata) if succeeded, False otherwise.
  """
  if not (dir_url and cache_url):
    return
  with NetworkcacheClient(cache_url, dir_url,
      signature_certificate_list=signature_certificate_list) as nc:
    logger.info('Downloading %s...', directory_key)
    result = nc.select(directory_key, wanted_metadata_dict, required_key_list)
    if strategy:
      entry = None
      result = list(result)
      if result:
        entry = strategy(result)
        if not entry: # XXX: this should be the choice of 'strategy' function
          logger.info("Can't find best entry matching strategy, selecting "
              "random one between acceptable ones.")
          entry = result[0]
    else:
      entry = next(result, None)
    if entry:
      return nc.download(entry['sha512']), entry
    else:
      logger.info('No matching entry to download %s', directory_key)

def helper_download_network_cached_to_file(dir_url, cache_url,
    signature_certificate_list,
    directory_key, path, wanted_metadata_dict={}, required_key_list=[],
    strategy=None):
  """
  Download a file from network cache. It is the responsibility of caller method
  to check md5.
  """
  result = helper_download_network_cached(dir_url, cache_url,
      signature_certificate_list,
      directory_key, wanted_metadata_dict, required_key_list, strategy)
  if result:
    # XXX check if nc filters signature_certificate_list!
    # Creates a file with content to desired path.
    file_descriptor, metadata_dict = result
    f = open(path, 'w+b')
    try:
      shutil.copyfileobj(file_descriptor, f)
      # XXX method should check MD5.
      return metadata_dict
    finally:
      f.close()
      file_descriptor.close()
  return False

def helper_download_network_cached_to_directory(dir_url, cache_url,
    signature_certificate_list,
    directory_key, path, wanted_metadata_dict={}, required_key_list=[],
    strategy=None):
  """
  Download a tar file from network cache and untar it to specified path.
  """
  result = helper_download_network_cached(dir_url, cache_url,
      signature_certificate_list,
      directory_key, wanted_metadata_dict, required_key_list, strategy)
  if result:
    file_descriptor, metadata_dict = result
    try:
      NetworkcacheClient.extract(path.rstrip('/'), file_descriptor)
      return metadata_dict
    finally:
      file_descriptor.close()
