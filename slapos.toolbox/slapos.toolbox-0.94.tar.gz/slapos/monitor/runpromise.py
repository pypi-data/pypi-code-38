#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import os
import subprocess
import json
import psutil
import time
from datetime import datetime
from shutil import copyfile
import glob
import argparse
import traceback
import logging
import ConfigParser
from slapos.grid.promise import PromiseLauncher, PromiseQueueResult, PromiseError
from slapos.grid.promise.generic import PROMISE_LOG_FOLDER_NAME
from slapos.util import mkdir_p

# Promise timeout after 20 seconds by default
promise_timeout = 20

def getArgumentParser():
  """
  Parse arguments for monitor collector instance.
  """
  parser = argparse.ArgumentParser()
  parser.add_argument('-c', '--config', dest='config_file',
                      help='The Path of configuration file to load.')
  parser.add_argument('-p', '--partition-folder',
                      help='Base path of the partition.')
  parser.add_argument('-L', '--log-folder',
                      help='Folder where promises will write logs.')
  parser.add_argument('--console',
                      help='Log to console too',
                      default=False, action='store_true')
  parser.add_argument('-a', '--check-anomaly',
                      help='Enable check of anomaly on promises.',
                      default=False, action='store_true')
  parser.add_argument('-D', '--debug',
                      help='Configure loggin in debug mode.',
                      default=False, action='store_true')
  parser.add_argument('--master-url',
                      help='SlapOS Master Service URL.')
  parser.add_argument('--partition-cert',
                      help='Computer partition certificate file path.')
  parser.add_argument('--partition-key',
                      help='Computer partition key file path.')
  parser.add_argument('--partition-id',
                      help='Computer partition ID.')
  parser.add_argument('--computer-id',
                      help='Computer ID.')
  parser.add_argument('--pid-path',
                      help='Path where the pid of this process will be writen.')
  parser.add_argument('--run-only',
                      help='List of python promises to run separates by space.',
                      default="")
  parser.add_argument('-f', '--force',
                      help='Force to run promise without consider the periodicity.',
                      default=False, action='store_true')
  parser.add_argument('--dry-run',
                      help='Only run promise without save result.',
                      default=False, action='store_true')
  parser.add_argument('--promise-timeout', default=20, type=int,
                      help='Maximum promise execution time.')

  return parser


class MonitorPromiseLauncher(object):

  def __init__(self, config_parser):
    self.config = config_parser
    if self.config.config_file:
      self._loadConfigFromFile(self.config.config_file)
    self.logger = logging.getLogger("Monitor")
    self.logger.setLevel(logging.DEBUG if self.config.debug else logging.INFO)

    if not self.config.log_folder or self.config.console:
      if len(self.logger.handlers) == 0 or \
          not isinstance(self.logger.handlers[0], logging.StreamHandler):
        handler = logging.StreamHandler()
        handler.setFormatter(logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s"))
        self.logger.addHandler(handler)
    if self.config.log_folder:
      log_file = os.path.join(self.config.log_folder,
        '%s.log' % self.config.title.replace(' ', '_'))
      file_handler = logging.FileHandler(log_file)
      file_handler.setFormatter(logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s"))
      self.logger.addHandler(file_handler)


  def _loadConfigFromFile(self, config_file):
    config = ConfigParser.ConfigParser()
    config.read([config_file])
    known_key_list = ['partition-cert', 'partition-key', 'partition-id',
                      'pid-path', 'computer-id', 'check-anomaly',
                      'master-url', 'partition-folder', 'promise-timeout']
 
    if config.has_section('promises'):
      for key, value in config.items('promises'):
        key_add = key.replace('-', '_')
        if key in known_key_list and \
            getattr(self.config, key_add, None) is None:
          setattr(self.config, key_add, value)

  def start(self):
    """
      run all promises in sequential ways
    """
    if self.config.pid_path:
      if os.path.exists(self.config.pid_path):
        # Check if another run promise is running
        with open(self.config.pid_path) as fpid:
          try:
            pid = int(fpid.read(6))
          except ValueError:
            pid = None
          if pid and os.path.exists("/proc/" + str(pid)):
            self.logger.warning("A process is already running with pid " + str(pid))
            return []

      with open(self.config.pid_path, 'w') as fpid:
        fpid.write(str(os.getpid()))

    if not self.config.partition_folder:
      raise ValueError("Partition folder is not specified")

    parameter_dict = {
      'promise-timeout': self.config.promise_timeout or promise_timeout,
      'promise-folder': os.path.join(self.config.partition_folder, 'etc', 'plugin'),
      'legacy-promise-folder': os.path.join(self.config.partition_folder, 'etc', 'promise'),
      'partition-folder': self.config.partition_folder,
      'master-url': self.config.master_url,
      'partition-cert': self.config.partition_cert,
      'partition-key': self.config.partition_key,
      'partition-id': self.config.partition_id,
      'computer-id': self.config.computer_id,
      'debug': self.config.debug,
      'check-anomaly': self.config.check_anomaly,
      'force': self.config.force,
      'run-only-promise-list': [x for x in self.config.run_only.split(' ') if x]
    }
    if self.config.log_folder:
      parameter_dict['log-folder'] = self.config.log_folder
    else:
      parameter_dict['log-folder'] = os.path.join(self.config.partition_folder,
                                                  PROMISE_LOG_FOLDER_NAME)
      mkdir_p(parameter_dict['log-folder'])

    promise_launcher = PromiseLauncher(
      config=parameter_dict,
      logger=self.logger,
      dry_run=self.config.dry_run
    )

    self.logger.info("Checking promises...")
    exit_code = 0
    try:
      promise_launcher.run()
    except PromiseError, e:
      # error was already logged
      exit_code = 1
    os.remove(self.config.pid_path)
    self.logger.info("Finished promises.")
    return exit_code

def main():
  arg_parser = getArgumentParser()
  promise_runner = MonitorPromiseLauncher(arg_parser.parse_args())
  sys.exit(promise_runner.start())
