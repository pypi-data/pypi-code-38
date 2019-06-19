#!/usr/bin/env python

import sys
import os
import re
import jinja2
import json
import argparse
import subprocess
from datetime import datetime
import time


def parseArguments():
  """
  Parse arguments for monitor instance.
  """
  parser = argparse.ArgumentParser()
  parser.add_argument('--config_folder',
                      help='Path where json configuration/document will be read and write')
  parser.add_argument('--htpasswd_bin',
                      help='Path apache htpasswd binary. Needed to write htpasswd file.')
  parser.add_argument('--output_cfg_file',
                      help='Ouput parameters in cfg file.')
  parser.add_argument('--monitor_https_cors',
                      help='Path to the CORS httpd template.')

  return parser.parse_args()

class MonitorConfigWrite(object):

  def __init__(self, config_json_file, htpasswd_bin, output_cfg_file="", monitor_https_cors=""):
    self.config_json_file = config_json_file
    self.output_cfg_file = output_cfg_file
    self.htpasswd_bin = htpasswd_bin
    self.monitor_https_cors = monitor_https_cors

  def _fileWrite(self, file_path, content):
    try:
      with open(file_path, 'w') as wf:
        print file_path, content
        wf.write(content.strip())
        return True
    except OSError, e:
      print "ERROR while writing changes to %s.\n %s" % (file_path, str(e))
      return False

  def _htpasswdWrite(self, htpasswd_bin,  parameter_dict, value):
    command = [htpasswd_bin, '-cb', parameter_dict['htpasswd'], parameter_dict['user'], value]
    process = subprocess.Popen(
      command,
      stdin=None,
      stdout=subprocess.PIPE,
      stderr=subprocess.PIPE
    )
    result = process.communicate()[0]
    if process.returncode != 0:
      print result
      return False
    with open(parameter_dict['file'], 'w') as pfile:
      pfile.write(value)
    return True

  def _httpdCorsDomainWrite(self, httpd_cors_file, httpd_gracefull_bin, cors_domain):
    cors_string = ""
    cors_domain_list = cors_domain.split()
    old_httpd_cors_file = os.path.join(
      os.path.dirname(httpd_cors_file),
      'prev_%s' % os.path.basename(httpd_cors_file)
    )
    if os.path.exists(old_httpd_cors_file) and os.path.isfile(old_httpd_cors_file):
      try:
        with open(old_httpd_cors_file, 'r') as cors_file:
          if cors_file.read() == cors_domain:
            if os.path.exists(httpd_cors_file) and (os.stat(httpd_cors_file).st_size > 0
              or (cors_domain == "" and os.stat(httpd_cors_file).st_size == 0)):
              # Skip if cors file is not empty
              return True
      except OSError, e:
        print "Failed to open file at %s. \n%s" % (old_httpd_cors_file, str(e))
    try:
      with open(self.monitor_https_cors, 'r') as cors_template:
        template = jinja2.Template(cors_template.read())
        rendered_string = template.render(domain=cors_domain)
      with open(httpd_cors_file, 'w') as file:
        file.write(rendered_string)
    except OSError, e:
      print "ERROR while writing CORS changes to %s.\n %s" % (httpd_cors_file, str(e))
      return False

    # Save current cors domain list
    try:
      with open(old_httpd_cors_file, 'w') as cors_file:
        cors_file.write(cors_domain)
    except OSError, e:
      print "Failed to open file at %s. \n%s" % (old_httpd_cors_file, str(e))
      return False

    # Restart httpd process
    try:
      subprocess.call(httpd_gracefull_bin)
    except OSError, e:
      print "Failed to execute command %s.\n %s" % (httpd_gracefull_bin, str(e))
      return False
    return True

  def applyConfigChanges(self):
    parameter_config_file = os.path.join(
      os.path.dirname(self.config_json_file),
      'config.parameters.json'
    )
    if not os.path.exists(self.config_json_file) or not os.path.isfile(self.config_json_file):
      #print "ERROR: Config file doesn't exist... Exiting"
      return {}

    new_parameter_list = []
    parameter_list = []
    description_dict = {}
    result_dict = {}

    try:
      with open(self.config_json_file) as tmpfile:
        new_parameter_list = json.loads(tmpfile.read())
    except ValueError:
      print "Error: Couldn't parse json file %s" % self.config_json_file

    with open(parameter_config_file) as tmpfile:
      description_dict = json.loads(tmpfile.read())

    for i in range(0, len(new_parameter_list)):
      key = new_parameter_list[i]['key']
      if key != '':
        description_entry = description_dict[key]
        if description_entry['type'] == 'file':
          result_dict[key] = self._fileWrite(
            description_entry['file'],
            new_parameter_list[i]['value']
          )
        elif description_entry['type'] == 'htpasswd':
          result_dict[key] = self._htpasswdWrite(
            self.htpasswd_bin,
            description_entry,
            new_parameter_list[i]['value']
          )
        elif description_entry['type'] == 'httpdcors':
          result_dict[key] = self._httpdCorsDomainWrite(
            description_entry['cors_file'],
            description_entry['gracefull_bin'],
            new_parameter_list[i]['value']
          )

    if (self.output_cfg_file):
      try:
        with open(self.output_cfg_file, 'w') as pfile:
          pfile.write('[public]\n')
          for parameter in new_parameter_list:
            if parameter['key']:
              pfile.write('%s = %s\n' % (parameter['key'], parameter['value']))
      except OSError, e:
        print "Error failed to create file %s" % self.output_cfg_file
        pass

    return result_dict


def main():
  parser = parseArguments()
  parameter_tmp_file = os.path.join(parser.config_folder, 'config.tmp.json')
  config_file = os.path.join(parser.config_folder, 'config.json')

  # Run 4 times with sleep
  run_counter = 1
  max_runn = 4
  sleep_time = 15

  instance = MonitorConfigWrite(
    parameter_tmp_file,
    parser.htpasswd_bin,
    parser.output_cfg_file,
    parser.monitor_https_cors)

  while True:
    result_dict = instance.applyConfigChanges()
    if result_dict != {}:
      status = True
      for key in result_dict:
        if not result_dict[key]:
          status = False
    
      if status and os.path.exists(parameter_tmp_file):
        try:
          os.unlink(config_file)
        except OSError, e:
          print "ERROR cannot remove file: %s" % parameter_tmp_file
        else:
          os.rename(parameter_tmp_file, config_file)
    if run_counter == max_runn:
      break
    else:
      run_counter += 1
      time.sleep(sleep_time)
