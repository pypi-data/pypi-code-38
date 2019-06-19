# -*- coding: utf-8 -*-
##############################################################################
#
# Copyright (c) 2010, 2015 Nexedi SA and Contributors. All Rights Reserved.
#                    Nicolas Delaby <nicolas@nexedi.com>
#                    Romain Courteaud <romain@nexedi.com>
#
# WARNING: This program as such is intended to be used by professional
# programmers who take the whole responsability of assessing all potential
# consequences resulting from its eventual inadequacies and bugs
# End users who are looking for a ready-to-use solution with commercial
# garantees and support are strongly adviced to contract a Free Software
# Service Company
#
# This program is Free Software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
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
import os
import shutil
import sys
import re
import shlex
from subprocess import Popen, PIPE, STDOUT
import logging
from datetime import datetime

_MARKER = []
WGET = 'wget'
WGET_ARGS = '-r -nc --retry-connrefused --save-headers'
# WGET_ARGS = '-r -nc --retry-connrefused --save-headers --header "Host: example.org" --no-check-certificate'
# WGET_FILL_CACHE_ARGS = '-q -O /dev/null  --header="Accept-Encoding: gzip, deflate"'

class ProcessTimeoutException(Exception):
  pass

def alarm_handler(signum, frame):
  raise ProcessTimeoutException

class HTTPCacheCheckerTestSuite(object):

  URL_CODE = 'url'
  STATUS_CODE = 'status'
  FILE_PATH_CODE = 'path'
  ERROR_CODE = 'error'
  OTHER_CODE = 'other'

  LOG_LEVEL_DICT = {'debug': logging.DEBUG,
                    'info': logging.INFO,
                    'warning': logging.WARNING,
                    'error': logging.ERROR,
                    'critical': logging.CRITICAL}

  REGEXP_URL_SEARCH = re.compile('^--\d{4}.*--\s+(?P<%s>.*)$' % URL_CODE)
  REGEXP_STATUS_SEARCH = re.compile(
    '^HTTP request sent, awaiting response\.\.\. (?P<%s>\d+).+$' % STATUS_CODE
  )
  REGEXP_SAVE_FILE = re.compile("^Saving to: '(?P<%s>.*)'" % FILE_PATH_CODE)
  REGEXP_ERROR = re.compile("^(ERROR|wget): (?P<%s>.*)" % ERROR_CODE)

  REGEXP_HEADER_CACHE = re.compile("Via: .*ApacheTrafficServer/.*\[(?P<hit>c.s.f.)\]", re.MULTILINE)
  generic_header_search_regex = '%s:\s(.*)\s$'

  ACCEPTABLE_STATUS_LIST = ('200', '304', '301', '302')

  def __init__(self, root_url, working_directory,
               header_list,
               debug_level, file_log_path, conditional_header_dict,
               no_header_dict, traffic_server_cache_list):
    """
      root_url : website to check
      working_directory : where fetched data will be downloaded
      header_list : Key == Header id.
                    value: if equals True means header
                             needs to be present in RESPONSE
                           if this is tuple, the Header value must sastify
                             at least one of the proposed values
      debug_level : log level of this utility (debug =>very verbose,
                                               info=>normal,
                                               warning=> nothing)
      file_log_path: path to log file
      conditional_header_dict : Key  == Section id (like 'header url='.*/login')
                                value: the configuration lines in this sction
                                       (config format is same as header_list)
      no_header_dict : Key == Section id (like 'no_header url=.*/sitemap')
                       value: = not exsiting headers
      traffic_server_cache_list: list of accepted traffic server cache result
    """
    self.root_url = root_url
    self.working_directory = working_directory
    self.header_list = header_list
    self.conditional_header_dict = conditional_header_dict
    self.no_header_dict = no_header_dict
    self.traffic_server_cache_list = traffic_server_cache_list
    level = self.LOG_LEVEL_DICT.get(debug_level, logging.INFO)
    logging.basicConfig(filename=file_log_path, level=level)
    self.report_dict = {}

  def _initFolder(self):
    """Delete and create workgin directory
    """
    if os.path.isdir(self.working_directory):
      logging.debug('Re-creating folder:%r' % self.working_directory)
      shutil.rmtree(self.working_directory)
    else:
      logging.debug('Creating folder:%r' % self.working_directory)
    os.mkdir(self.working_directory)

  def _runSpider(self):
    """Run wget in working_directory with headers in result
    """
    wget_command_string = '%s %s %s' % (WGET, WGET_ARGS, self.root_url)
    logging.debug('wget command:%r' % wget_command_string)
    wget_argument_list = shlex.split(wget_command_string)
    wget_process = Popen(wget_argument_list, stdin=PIPE,
                         stdout=PIPE, stderr=STDOUT,
                         env={'LANG': 'en_EN'}, # Force output messages
                                                # in English
                         universal_newlines=True,
                         cwd=self.working_directory) # working directory
    stdout, stderr = wget_process.communicate()
    return stdout

#   def _fillCache(self):
#     """Run wget to fill frontend cache
#     """
#     wget_command_string = '%s %s %s' % (WGET, WGET_ARGS, self.root_url)
#     logging.debug('wget command:%r' % wget_command_string)
#     wget_argument_list = shlex.split(wget_command_string)
#     wget_process = Popen(wget_argument_list, stdin=PIPE,
#                          stdout=PIPE, stderr=STDOUT,
#                          env={'LANG': 'en_EN'}, # Force output messages
#                                                 # in English
#                          universal_newlines=True,
#                          cwd=self.working_directory) # working directory
#     stdout, stderr = wget_process.communicate()
#     return stdout

  def _getHeaderPolicyList(self, url, fetched_data):
    """
    create the header checking policy list by the url, and the header

    [header_list]
    Last-Modified = True
    Vary = Accept-Language, Cookie, Accept-Encoding
    Cache-Control = max-age=300
    max-age=3600
    [header url=.*/contact_form]
    Last-Modified = True

    [no-header content-type=(image/.*|.*/javascript)]
    Vary = False

    [erp5_extension_list]
    prohibited_folder_name_list = web_page_module
    document_module
    prohibited_file_name_list = WebSection_viewAsWeb
    Base_viewHistory
    list
    """
    def getNoCheckHeaderList(url, fetched_data):
      """
        create no check header list
      """
      pick_content_type = re.compile('^no_header\s*content-type=(.*)')
      pick_url = re.compile('^no_header\s*url=(.*)')
      section_list = self.no_header_dict.keys()
      no_check_header_list = []
      for section in section_list:
        content_type_regex_str_match = pick_content_type.match(section)
        url_regex_str_match = pick_url.match(section)
        if content_type_regex_str_match is not None:
          content_type_regex_str = content_type_regex_str_match.group(1)
          content_type_regex = \
            re.compile('Content-Type:\s%s' % content_type_regex_str,
                       re.MULTILINE | re.IGNORECASE)
          if content_type_regex.search(fetched_data) is not None:
            for header, value in self.no_header_dict[section]:
              no_check_header_list.append(header)
          continue
        if url_regex_str_match is not None:
          url_regex_str = url_regex_str_match.group(1)
          if re.compile(url_regex_str).match(url) is not None:
            for header, value in self.no_header_dict[section]:
              no_check_header_list.append(header)
      return no_check_header_list

    def getConditionalHeaderDict(url, fetched_data):
      """ create header policy by the url and header"""
      conditional_header_dict = {}
      section_list = self.conditional_header_dict.keys()
      pick_content_type = re.compile('header\s*content-type=(.*)')
      pick_url = re.compile('header\s*url=(.*)')
      for section in section_list:
        content_type_regex_str_match = pick_content_type.match(section)
        url_regex_str_match = pick_url.match(section)
        if content_type_regex_str_match is not None:
          content_type_regex_str = content_type_regex_str_match.group(1)
          content_type_regex = \
            re.compile('Content-Type:\s%s' % content_type_regex_str,
                       re.MULTILINE | re.IGNORECASE)
          if content_type_regex.search(fetched_data) is not None:
            for header, value in self.conditional_header_dict[section]:
              conditional_header_dict[header] = _formatConfiguration(value)
          continue
        if url_regex_str_match is not None:
          url_regex_str = url_regex_str_match.group(1)
          if re.compile(url_regex_str).match(url) is not None:
            for header, value in self.conditional_header_dict[section]:
              conditional_header_dict[header] = _formatConfiguration(value)
      return conditional_header_dict

    validator_dict = {}
    no_header_list = getNoCheckHeaderList(url, fetched_data)
    conditional_header_dict = getConditionalHeaderDict(url, fetched_data)
    conditional_header_list = conditional_header_dict.keys()
    global_header_list = self.header_list.keys()
    header_policy_list = []
    if conditional_header_list:
      conditional_check_header_set = (set(conditional_header_list)
                                      - set(no_header_list))
      for header in conditional_check_header_set:
        header_policy_list.append((header, conditional_header_dict[header]))
    else:
      global_check_header_set = (set(global_header_list)
                                 - set(no_header_list))
      for header in global_check_header_set:
        header_policy_list.append((header, self.header_list[header]))
    # return items
    return header_policy_list

  def _validateHeader(self, url, header, reference_value, fetched_data):
    """validate header with the header policy"""
    re_compiled = re.compile(self.generic_header_search_regex % header,
                             re.MULTILINE | re.IGNORECASE)
    match_object = re_compiled.search(fetched_data)
    if match_object is None:
      message = 'header:%r not found' % (header)
      self.report_dict.setdefault(url, []).append(message)
    else:
      read_value = match_object.group(1)
      if reference_value is True and not read_value:
        message = 'value of header:%r not found' % (header)
        self.report_dict.setdefault(url, []).append(message)
      elif isinstance(reference_value, (tuple,list)):
        if read_value not in reference_value:
          message = 'value of header:%r does not match'\
                    ' (%r not in %r)' %\
                                    (header, read_value, reference_value)
          self.report_dict.setdefault(url, []).append(message)

  def _isSameUrl(self, url):
    """
      Return whether the url is already checked or not.

      Example case):
      http://example.com/login_form
      http://example.com/login_form/
    """
    if url in (None, ''):
      return False
    same_url = None
    if url.endswith('/'):
      same_url = url.rstrip('/')
    else:
      same_url = '%s/' % url
    if same_url in self.report_dict:
      return True
    return False

  def _parseWgetLine(self, line):
    """return tuple (code, value)
    code: 'url' means this is requested url
          'status' means we can read status code
          'other' something we can discard
    """
    for regexp, code in [
      (self.REGEXP_URL_SEARCH, self.URL_CODE),
      (self.REGEXP_STATUS_SEARCH, self.STATUS_CODE),
      (self.REGEXP_SAVE_FILE, self.FILE_PATH_CODE),
      (self.REGEXP_ERROR, self.ERROR_CODE)
      ]:
      match_object = regexp.search(line)
      if match_object is not None:
        return code, match_object.group(code)
    return self.OTHER_CODE, line

  def _parseWgetLogs(self, wget_log_file, discarded_url_list=_MARKER,
                     prohibited_file_name_list=None,
                     prohibited_folder_name_list=None):
    """read wget logs and test Caching configuration
    """
    if discarded_url_list is _MARKER:
      first_pass = True
    else:
      first_pass = False
    x_varnish_reference_list = []

    discarded = True
    for line in wget_log_file.splitlines():
      logging.debug('wget output:%r' % line)
      code, value = self._parseWgetLine(line)
      if code == self.URL_CODE:
        # This is the first Line by URL checked in wget stdout
        url = value
        logging.debug('url:%r' % url)
        discarded = False
        if not first_pass and url in discarded_url_list:
          # URL already checked during first pass
          logging.debug('%r Discarded' % url)
          discarded = True
        elif self._isSameUrl(url):
          discarded = True

      if discarded:
        # keep reading wget process without doing anything
        continue

      if code == self.ERROR_CODE:
        message = 'Page in error:%r' % (value)
        self.report_dict.setdefault(url, []).append(message)

      if code == self.STATUS_CODE:
        if value not in self.ACCEPTABLE_STATUS_LIST:
          message = 'Page in error status:%r' % (value)
          self.report_dict.setdefault(url, []).append(message)

      if code == self.FILE_PATH_CODE:
        logging.debug('checking:%r' % value)
        # Here we check if Response was cached
        file_path = os.path.sep.join((self.working_directory, value))
        folder_path , filename = os.path.split(file_path)
        if prohibited_file_name_list:
          if '?' in filename:
            filename = filename.rpartition('?')[0]
          if filename in prohibited_file_name_list:
            # Error
            message = '%r is prohibited as filename' % filename
            self.report_dict.setdefault(url, []).append(message)
        if prohibited_folder_name_list:
          for prohibited_folder_name in prohibited_folder_name_list:
            if prohibited_folder_name in folder_path.split(os.path.sep):
              message = '%r is prohibited as folder name' % prohibited_folder_name
              self.report_dict.setdefault(url, []).append(message)
              break
        file_object = None
        try:
          file_object = open(file_path, 'r')
        except IOError:
          # This is probably a folder try with /index.html
          index_file_path = file_path + os.path.sep + 'index.html'
          try:
            file_object = open(index_file_path, 'r')
          except IOError:
           # sometimes this is appended with .1
           number_file_path = file_path + '.1'
           try:
             file_object = open(number_file_path, 'r')
           except IOError:
             logging.info('File not found for url:%r %r' %\
                        (url, (file_path, index_file_path, number_file_path),))
             continue
        fetched_data = file_object.read()
        file_object.close()

        x_cache_header_match_object = \
          self.REGEXP_HEADER_CACHE.search(fetched_data)
        if x_cache_header_match_object is None:
          # This RESPONSE is not cached by Varnish
          message = 'Via cache header not found'
          self.report_dict.setdefault(url, []).append(message)
        else:
          # http://labs.omniti.com/people/mark/ats_sa/slides.html#slide-18
          cached = False
          for traffic_server_cache in self.traffic_server_cache_list:
            if (x_cache_header_match_object.group('hit').startswith(traffic_server_cache)):
              cached = True
              break

          if cached:
            # This is a cached content with a positive hit value
            # dot not check this url in second pass
            logging.debug('will be discarded:%r' % url)
            discarded_url_list.append(url)
          else:
            message = 'Not a cache hit! (got %s) (expect %s)' % (
              x_cache_header_match_object.group('hit'),
              self.traffic_server_cache_list
            )
            self.report_dict.setdefault(url, []).append(message)

        # parse the web checker configuration file and run the header
        # validation method
        for header, reference_value in self._getHeaderPolicyList(
                                              url, fetched_data):
          self._validateHeader(url, header, reference_value, fetched_data)

    return x_varnish_reference_list, discarded_url_list[:]

  def start(self, prohibited_file_name_list=None,
            prohibited_folder_name_list=None):
    """Run test suite
    return errors
    """
    logging.info('#' * 52)
    logging.info('date:%r' % datetime.now().isoformat())
    logging.info('#' * 52)

    self._initFolder()
    logging.info('Starting pass:%r' % self.root_url)
    wget_log_file = self._runSpider()
    x_varnish_reference_list, discarded_url_list =\
                           self._parseWgetLogs(wget_log_file,
                       prohibited_file_name_list=prohibited_file_name_list,
                       prohibited_folder_name_list=prohibited_folder_name_list)
    logging.info('End of second pass\n')

    if self.report_dict:
      report_message_list = ['*Errors*:']
      for url, message_list in self.report_dict.iteritems():
        unique_message_list = []
        for message in message_list:
          if message not in unique_message_list:
            unique_message_list.append(message)
        report_message_list.append('\n')
        report_message_list.append(url)
        report_message_list.extend(['\t%s' % message for message\
                                                       in unique_message_list])
      report_message = '\n'.join(report_message_list)
      signal = 'PROBLEM'
    else:
      report_message = 'No errors'
      signal = 'OK'
    subject = '%r:HTTP Cache checker results for %s' % (signal, self.root_url)
    return subject + '\n' + report_message


from optparse import OptionParser
import ConfigParser

def _formatConfiguration(configuration):
  """ format the configuration"""
  if configuration in ('True', 'true', 'yes'):
    return True
  return configuration.splitlines()

def web_checker_utility():
  usage = "usage: %prog [options] config_path"
  parser = OptionParser(usage=usage)
  parser.add_option('-o', '--output_file',
                    dest='output_file')

  (options, args) = parser.parse_args()
  if len(args) != 1 :
    print parser.print_help()
    parser.error('incorrect number of arguments')
  config_path = args[0]

  config = ConfigParser.RawConfigParser()
  config.read(config_path)

  working_directory = config.get('web_checker', 'working_directory')
  url = config.get('web_checker', 'url')
  debug_level = config.get('web_checker', 'debug_level')

  file_log_path = 'web_checker.log'
  if config.has_option('web_checker', 'file_log_path'):
    file_log_path = config.get('web_checker', 'file_log_path')

  if config.has_option('web_checker', 'traffic_server_cache'):
    traffic_server_cache_list = config.get('web_checker', 'traffic_server_cache').splitlines()
  else:
    traffic_server_cache_list = ['cHs']

  header_list = {}
  for header, configuration in config.items('header_list'):
    if header in config.defaults().keys():
      # defaults are shared for all sections.
      # so discard them from header_list
      continue
    value = _formatConfiguration(configuration)
    header_list[header] = value
  conditional_header_dict = {}
  no_header_dict = {}

  for section in config.sections():
    item_list = config.items(section)
    if re.compile("^header\s.*").match(section) is not None:
      conditional_header_dict.setdefault(section, []).extend(item_list)
    if re.compile("^no_header\s.*").match(section) is not None:
      no_header_dict.setdefault(section, []).extend(item_list)

  if config.has_section('erp5_extension_list'):
    prohibited_file_name_list = config.get('erp5_extension_list',
                                      'prohibited_file_name_list').splitlines()
    prohibited_folder_name_list = config.get('erp5_extension_list',
                                    'prohibited_folder_name_list').splitlines()
  else:
    prohibited_file_name_list = prohibited_folder_name_list = []

  instance = HTTPCacheCheckerTestSuite(url,
                                       working_directory,
                                       header_list,
                                       debug_level,
                                       file_log_path,
                                       conditional_header_dict,
                                       no_header_dict,
                                       traffic_server_cache_list)

  result = instance.start(prohibited_file_name_list=prohibited_file_name_list,
                       prohibited_folder_name_list=prohibited_folder_name_list)
  if options.output_file:
    file_object = open(options.output_file, 'w')
    file_object.write(result)
    file_object.close()
  else:
    print result

if __name__ == '__main__':
  sys.exit(web_checker_utility())
