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
import os
import argparse
import subprocess
import psutil
import glob

def getAgumentParser():
  """
  Return argument parser for secure delete script.
  """
  parser = argparse.ArgumentParser()
  parser.add_argument('-n', '--iterations', default=1, type=int,
                      help='overwrite N times instead of the default (1)')
  parser.add_argument('-u', '--remove', action='store_true',
                      help='truncate and remove file after overwriting.')
  parser.add_argument('-z', '--zero', action='store_true',
                      help='add a final overwrite with zeros to hide shredding.')
  parser.add_argument('-s', '--check-exist', action='store_true',
                      default=False,
                      help='Check if files exist. If a file don\t exists, skip instead of raise.')
  parser.add_argument('--file', dest='file_list',
                      required=True, nargs='+', metavar='FILE',
                      help='File(s) to overwrite and remove if -u is used.')
  parser.add_argument('-p', '--check-pid', type=int, metavar="PID",
                      help='If process is running with PID, abort command. ' \
                           'This is to prevent delete files used by a process.')
  parser.add_argument('--check-pid-file', metavar="PID_FILE",
                      help='Same as "check-pid" option but read PID from PID_FILE')
  parser.add_argument('--shred-bin', default="/usr/bin/shred",
                      help='Path of shred binary used to wipe files. Default: %(default)s')

  return parser

def getFileList(source_file_list, check_exist):
  file_list = []
  for file_path in source_file_list:
    if file_path.find('*') != -1 or file_path.find('?') != -1:
      sub_list = glob.glob(file_path)
    else:
      sub_list = [file_path]
    for file in sub_list:
      if check_exist and not os.path.exists(file):
        continue
      file_list.append(file)
      if os.path.islink(file):
        # remove the link target file
        file_list.append(os.path.realpath(file))
  return file_list

def shred(options):
  # Overwrite the specified FILE(s) repeatedly, in order to make it harder
  # for even very expensive hardware probing to recover the data.
  # using Linux `shred` utility

  check_pid = None
  if options.check_pid_file:
    with open(options.check_pid_file, 'r') as fpid:
      check_pid = int(fpid.read())
  else:
    check_pid = options.check_pid
  if check_pid and psutil.pid_exists(check_pid):
    return "check-pid is enabled and process with pid %s is running. Cannot " \
      "wipe file(s) while the process is running." % check_pid

  arg_list = [options.shred_bin, '-n', str(options.iterations), '-v']
  if options.remove:
    arg_list.append('-u')
  if options.zero:
    arg_list.append('-z')
  arg_list.extend(getFileList(options.file_list, options.check_exist))

  pshred = subprocess.Popen(arg_list, stdout=subprocess.PIPE,
                            stderr=subprocess.STDOUT)
  result, stderr = pshred.communicate()
  if pshred.returncode is None:
    pshred.kill()
  if pshred.returncode != 0:
    raise RuntimeError('Command %r failed, with output:\n%s\n%s' % (
      ' '.join(arg_list), result, stderr or ''))
  return result

def main():
  arg_parser = getAgumentParser()
  output = shred(arg_parser.parse_args())
  print output
