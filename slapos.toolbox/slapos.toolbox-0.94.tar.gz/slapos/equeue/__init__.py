# -*- coding: utf-8 -*-
##############################################################################
#
# Copyright (c) 2010 Vifib SARL and Contributors. All Rights Reserved.
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

import argparse
import errno
import gdbm
import json
from lockfile import LockFile
import logging
import logging.handlers
import os
import signal
import socket
import subprocess
import sys
import SocketServer
import StringIO
import threading

# Copied from erp5.util:erp5/util/testnode/ProcessManager.py
def subprocess_capture(p, log, log_prefix, get_output=True):
  def readerthread(input, output, buffer):
    while True:
      data = input.readline()
      if not data:
        break
      if get_output:
        buffer.append(data)
      if log_prefix:
        data = "%s : " % log_prefix +  data
      data = data.rstrip('\n')
      output(data)
  if p.stdout:
    stdout = []
    stdout_thread = threading.Thread(target=readerthread,
                                     args=(p.stdout, log, stdout))
    stdout_thread.daemon = True
    stdout_thread.start()
  if p.stderr:
    stderr = []
    stderr_thread = threading.Thread(target=readerthread,
                                     args=(p.stderr, log, stderr))
    stderr_thread.daemon = True
    stderr_thread.start()
  p.wait()
  if p.stdout:
    stdout_thread.join()
  if p.stderr:
    stderr_thread.join()
  return (p.stdout and ''.join(stdout),
          p.stderr and ''.join(stderr))

class EqueueServer(SocketServer.ThreadingUnixStreamServer):

  daemon_threads = True

  def __init__(self, *args, **kw):
    self.options = kw.pop('equeue_options')
    SocketServer.ThreadingUnixStreamServer.__init__(self,
                                                    RequestHandlerClass=None,
                                                    *args, **kw)
    # Equeue Specific elements
    self.setLogger(self.options.logfile[0], self.options.loglevel[0])
    self.setDB(self.options.database[0])
    if getattr(self.options, 'takeover_triggered_file_path', None):
      self.takeover_triggered_file_path = self.options.takeover_triggered_file_path[0]
    # Lock to only have one command running at the time
    self.thread_lock = threading.Lock()
    # Lockfile is used by other commands to know if an import is ongoing.
    self.lockfile = LockFile(self.options.lockfile)
    self.lockfile.break_lock()

  def setLogger(self, logfile, loglevel):
    self.logger = logging.getLogger("EQueue")
    handler = logging.handlers.WatchedFileHandler(logfile, mode='a')
    # Natively support logrotate
    level = logging._levelNames.get(loglevel, logging.INFO)
    self.logger.setLevel(level)
    formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
    handler.setFormatter(formatter)
    self.logger.addHandler(handler)

  def setDB(self, database):
    self.db = gdbm.open(database, 'cs', 0700)

  def _hasTakeoverBeenTriggered(self):
    if hasattr(self, 'takeover_triggered_file_path') and \
       os.path.exists(self.takeover_triggered_file_path):
      return True
    return False

  def _runCommandIfNeeded(self, command, timestamp):
    with self.thread_lock as thread_lock, self.lockfile as lockfile:
      if self._hasTakeoverBeenTriggered():
        self.logger.info('Takeover has been triggered, preventing to run import script.')
        return
      cmd_list = command.split('\0')
      cmd_readable = ' '.join(cmd_list)
      cmd_executable = cmd_list[0]

      if cmd_executable in self.db and timestamp <= int(self.db[cmd_executable]):
        self.logger.info("%s already run.", cmd_readable)
        return

      self.logger.info("Running %s, %s with output:", cmd_readable, timestamp)
      try:
        sys.stdout.flush()
        p = subprocess.Popen(cmd_list, stdout=subprocess.PIPE,
                             stderr=subprocess.PIPE)
        subprocess_capture(p, self.logger.info, '', True)
        if p.returncode == 0:
          self.logger.info("%s finished successfully.", cmd_readable)
          self.db[cmd_executable] = str(timestamp)
        else:
          self.logger.warning("%s exited with status %s." % (cmd_readable, p.returncode))
      except subprocess.CalledProcessError as e:
        self.logger.warning("%s exited with status %s. output is: \n %s" % (
            cmd_readable,
            e.returncode,
            e.output,
        ))

  def process_request_thread(self, request, client_address):
    # Handle request
    self.logger.debug("Connection with file descriptor %d", request.fileno())
    request.settimeout(self.options.timeout)
    request_string = StringIO.StringIO()
    segment = None
    try:
      while segment != '':
        segment = request.recv(1024)
        request_string.write(segment)
    except socket.timeout:
      pass

    command = '127'
    try:
      request_parameters = json.loads(request_string.getvalue())
      timestamp = request_parameters['timestamp']
      command = str(request_parameters['command'])
      self.logger.info("New command %r at %s", command, timestamp)

    except (ValueError, IndexError) :
      self.logger.warning("Error during the unserialization of json "
                          "message of %r file descriptor. The message "
                          "was %r", request.fileno(), request_string.getvalue())

    try:
      request.send(command)
    except:
      self.logger.warning("Couldn't respond to %r", request.fileno())
    self.close_request(request)
    self._runCommandIfNeeded(command, timestamp)
# Well the following function is made for schrodinger's files,
# It will work if the file exists or not
def remove_existing_file(path):
  try:
    os.remove(path)
  except OSError, e:
    if e.errno != errno.ENOENT:
      raise

def main():
  parser = argparse.ArgumentParser(
    description="Run a single threaded execution queue.")
  parser.add_argument('--database', nargs=1, required=True,
                      help="Path to the database where the last "
                      "calls are stored")
  parser.add_argument('--loglevel', nargs=1,
                      default='INFO',
                      choices=[i for i in logging._levelNames
                               if isinstance(i, str)],
                      required=False)
  parser.add_argument('-l', '--logfile', nargs=1, required=True,
                      help="Path to the log file.")
  parser.add_argument('-t', '--timeout', nargs=1, required=False,
                      dest='timeout', type=int, default=3)
  parser.add_argument('--lockfile',
                      help="Path to the lock file created when a command is run")
  parser.add_argument('--takeover-triggered-file-path', nargs=1, required=False,
                      help="Path to the file created by takeover script to state that it has been triggered.")
  parser.add_argument('socket', help="Path to the unix socket")

  args = parser.parse_args()

  socketpath = args.socket

  signal.signal(signal.SIGHUP, lambda *args: sys.exit(-1))
  signal.signal(signal.SIGTERM, lambda *args: sys.exit())

  remove_existing_file(socketpath)
  try:
    server = EqueueServer(socketpath, **{'equeue_options':args})
    server.logger.info("Starting server on %r", socketpath)
    server.serve_forever()
  finally:
    remove_existing_file(socketpath)
    os.kill(0, 9)

if __name__ == '__main__':
  main()
