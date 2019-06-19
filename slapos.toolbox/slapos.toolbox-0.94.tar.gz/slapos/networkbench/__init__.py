import socket
import logging
import time
import logging.handlers
import subprocess
import re
import sys
import shutil
import netifaces
import random
import pycurl
import argparse
import json
from StringIO import StringIO
from ping import ping, ping6
from dnsbench import resolve
from http import get_curl, request
import textwrap

class HelpFormatter(argparse.ArgumentDefaultsHelpFormatter):

    def _get_help_string(self, action):
        return super(HelpFormatter, self)._get_help_string(action) \
            if action.default else action.help

    def _split_lines(self, text, width):
        """Preserves new lines in option descriptions"""
        lines = []
        for text in text.splitlines():
            lines += textwrap.wrap(text, width)
        return lines

    def _fill_text(self, text, width, indent):
        """Preserves new lines in other descriptions"""
        kw = dict(width=width, initial_indent=indent, subsequent_indent=indent)
        return '\n'.join(textwrap.fill(t, **kw) for t in text.splitlines())

botname = socket.gethostname()

date_reg_exp = re.compile('\d{4}[-/]\d{2}[-/]\d{2}')

def _get_network_gateway(self):
  return netifaces.gateways()["default"][netifaces.AF_INET][0]

def load_configuration(config_path):
  if config_path.startswith("http://") or \
      config_path.startswith("ftp://") or \
      config_path.startswith("https://") or \
      config_path.startswith("file://"):
    return download_external_configuration(config_path)

  with open(config_path, "r") as f:
    return json.load(f)

def download_external_configuration(url):
  buffer = StringIO()
  curl, _ = get_curl(buffer, url)

  response_code = curl.getinfo(pycurl.HTTP_CODE)
  
  if response_code in (200, 0):
    try:
      return json.loads(buffer.getvalue())
    except ValueError:
      print "Unable to parse external configuration, error:"
      import traceback
      traceback.print_exc(file=sys.stderr)
      sys.stderr.flush()
      print "Ignoring external configuration"
    finally:
      curl.close()

  return {}

def is_rotate_log(log_file_path):
  try:
    log_file = open(log_file_path, 'r')
  except IOError:
    return False

  # Handling try-except-finally together.
  try:
    try:
      log_file.seek(0, 2)
      size = log_file.tell()
      log_file.seek(-min(size, 4096), 1)
      today = time.strftime("%Y-%m-%d")
      
      for line in reversed(log_file.read().split('\n')):
        if len(line.strip()):
          match_list = date_reg_exp.findall(line)
          if len(match_list):
            if match_list[0] != today:
              return ValueError(match_list[0])
            break

    except IOError:
      return False
  finally:
    log_file.close()

def rotate_logfile(handler, log_file):
  last_date = is_rotate_log(log_file)
  if last_date: 
    handler.doRollover()
    today = time.strftime("%Y-%m-%d")
    shutil.move("%s.%s" % (log_file, today),
                "%s.%s" % (log_file, last_date))
    # The simpler the better
    sp = subprocess.Popen("gzip %s.%s" % (log_file, last_date),
               stdout=subprocess.PIPE, stdin=subprocess.PIPE, shell=True)
    sp.communicate()

def create_logger(name, log_folder, verbose):
  new_logger = logging.getLogger(name)

  new_logger.setLevel(logging.DEBUG)
  log_file = '%s/network_bench.%s.log' % (log_folder, name)
  handler = logging.handlers.TimedRotatingFileHandler(
                     log_file, when="D",
                     backupCount=1000)

  rotate_logfile(handler, log_file)

  format = "%%(asctime)-16s;%s;%%(message)s" % botname
  handler.setFormatter(logging.Formatter(format))
  new_logger.addHandler(handler)

  if verbose:
    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(logging.Formatter(format))
    new_logger.addHandler(handler)
  return new_logger

def run_all(config_dict, log_folder, verbose):
  dns_logger = create_logger("dns", log_folder, verbose)
  name_dict = config_dict.get("dns", {})
  for name in name_dict:
    expected = name_dict[name].get("expected")
    dns_logger.info(';'.join(str(x) for x in resolve(name, expected)))

  ping_logger = create_logger("ping", log_folder, verbose)
  for host in config_dict.get("ping",[]):
    ping_logger.info(';'.join(str(x) for x in ping(host)))

  ping6_logger = create_logger("ping6", log_folder, verbose)
  for host in config_dict.get("ping6", []):
    ping6_logger.info(';'.join(str(x) for x in ping6(host)))

  http_logger = create_logger("http", log_folder, verbose)
  url_dict = config_dict.get("url", {})
  for url in url_dict:
    http_logger.info(';'.join(str(x) for x in request(url, url_dict[url])))

def main():
  parser = argparse.ArgumentParser(
        description="Run network benchmarch.",
        )
  _ = parser.add_argument
  _('-l', '--logdir', default=".",
                      help="Directory where the logs are going to be placed.")
  _('-c', '--conf', help="Path to the configuration json file.")
  _('-v', '--verbose', action='store_true', 
                       help="Show the results on stdout.")
  _('-d', '--delay', default=random.randint(0, 30), 
                     help="Delay before start to run," \
                          "as this script can be called on cron.")

  config = parser.parse_args()

  print("Downloading %s..." % config.conf.strip())
  config_dict = load_configuration(config.conf)

  print("Waiting %s before start..." % config.delay)
  time.sleep(float(config.delay))

  run_all(config_dict, 
          log_folder=config.logdir, 
          verbose=config.verbose)

