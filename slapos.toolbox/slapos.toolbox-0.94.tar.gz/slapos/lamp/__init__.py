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


import os
import time
import sys
import shutil
import MySQLdb
import sys
import argparse

def run():
  """Start the instance runner. this may run a python script, move or/and rename
  file or directory when dondition is filled. the condition may be when file exist or when an entry
  exist into database.
  """
  parser = argparse.ArgumentParser(description='Lamp instance configurator for SlapOs')
  group = parser.add_mutually_exclusive_group()
  group.add_argument('-f', action='store', dest='file_token',
                     help='The condition is true when file FILE_TOKEN is found', default=None)
  group.add_argument('-d', action='store', dest='token', default='appdb',
                     help="The condition is true when an entry is found in to database TOKEN")
  parser.add_argument('-H', action='store', default="localhost",
                    dest='mysql_host', help='Speficify the MySQL host')
  parser.add_argument('-u', action='store', default="root",
                    dest='mysql_user', help='Speficify the MySQL user')
  parser.add_argument('-P', action='store', default=3306,
                    dest='mysql_port', type=int,
                    help='Speficify the MySQL port')
  parser.add_argument('-p', action='store', default="",
                    dest='mysql_password', help='Speficify the MySQL password')
  parser.add_argument('--target-directory', '-t', action='store', default="",
                    dest='target_directory', help='Specifie the target directory to be used')
  parser.add_argument('--table', '-s', action='store', default="**",
                    dest='table', help='Specifie the table for database TOKEN to use when -d option is used')
  parser.add_argument('--cond', '-c', action='store', default="1", type=str,
                    dest='condition', help='Specifie the SQL condition to use when -d option is used')
  subparsers = parser.add_subparsers(help='commands')
  # A delete command
  delete_parser = subparsers.add_parser('delete', help='Remove file or directory')
  delete_parser.add_argument('delete_target', action='store', help='The list of file or directory to remove',
                             nargs='+')
  # A rename command
  rename_parser = subparsers.add_parser('rename', help='Rename SOURCE to DESTINATION')
  rename_parser.add_argument('source', action='store', help='the source to be rename')
  rename_parser.add_argument('destination', action='store', help='the new name of SOURCE after rename')
  rename_parser.add_argument('--chmod', action='store', help='The Mode to apply after rename file or directory',
                             default=None, dest='mode')
  # A python script command
  script_parser = subparsers.add_parser('run', help='Run python script')
  script_parser.add_argument('script', action='store', help='The path of python script to execute')
  script_parser.add_argument('-v', action='store', help='Other argument to pass to the script', nargs='+', dest='args')

  # A SQL script command
  sql_parser = subparsers.add_parser('sql', help='Run SQL script')
  sql_parser.add_argument('sql_script', action='store', help='The path of python script to execute')
  sql_parser.add_argument('-v', action='store', help='Other argument to pass to the script', nargs='+', dest='args')

  #A chmod command
  chmod_parser = subparsers.add_parser('chmod', help='Set the mode of file or directory')
  chmod_parser.add_argument('mode', action='store', help='the mode to apply to TARGET')
  chmod_parser.add_argument('chmod_target', action='store', help='the file or directory to change mode', nargs='+')

  result = parser.parse_args()
  arguments = dict(result._get_kwargs())
  if arguments['token'] == None and arguments['file_token'] == None:
    print "lampconfigure: Error: Please specify where condition will be taken, use -d or -f option"
    return
  setup(arguments)

def setup(arguments):
  timeout = 5;
  while True:
    if not checkAction(arguments):
      print "Waiting for 3s and retrying"
      time.sleep(3)
      continue
    time.sleep(timeout)
    if arguments.has_key('delete_target'):
      delete(arguments)

    if arguments.has_key('source'):
      rename(arguments)

    if arguments.has_key('script'):
      run_script(arguments)

    if arguments.has_key('sql_script'):
      run_sql_script(arguments)

    if arguments.has_key('chmod_target'):
      chmod(arguments)
    return

def checkAction(arguments):
  """Check if condition is filled. If token is string(that represent a path), the function check if file exist
  otherwise token is a dictionary and mysql_config is used to check condition into database
  """
  if arguments['file_token'] == None:
    try:
      conn = MySQLdb.connect (host = arguments['mysql_host'],
                        port = arguments['mysql_port'],
                        user = arguments['mysql_user'],
                        passwd = arguments['mysql_password'],
                        db = arguments['token'])
    except Exception, ex:
      #Mysql is not ready yet?...
      print ex.message
      return False
    if arguments['table'] == "**":
      #only detect if mysql has been started
      conn.close()
      return True
    cursor = conn.cursor ()
    cursor.execute("SHOW TABLES LIKE '%" + arguments['table'] + "'") #Check if table has been created
    row = cursor.fetchone ()
    if row == None:
      conn.close()
      return True
    else:
      arguments['table'] = row[0]
    cursor.execute ("SELECT * FROM " + arguments['table'] + " WHERE " + arguments['condition'])
    row = cursor.fetchone ()
    conn.close()
    if row == None:
      return True
    else:
      return False
  else:
    return not os.path.exists(os.path.join(arguments['target_directory'], arguments['file_token']))

def rename(arguments):
  source = os.path.join(arguments['target_directory'], arguments['source'])
  destination = os.path.join(arguments['target_directory'], arguments['destination'])
  if not os.path.exists(source):
    print "Error when moving: '%s': no such file or directory" % source
    return
  os.rename(source, destination)
  if arguments['mode'] != None:
    os.chmod(destination, int(arguments['mode'], 8))

def delete(arguments):
  for path in arguments['delete_target']:
    path = os.path.join(arguments['target_directory'], path)
    if not os.path.exists(path):
      print "Error when deleting: '%s': no such file or directory" % path
      continue
    if os.path.isdir(path):
      shutil.rmtree(path)
    else:
      os.remove(path)

def run_script(arguments):
  script = os.path.join(arguments['target_directory'], arguments['script'])
  print 'Running script: %s' % script
  if os.path.exists(script):
    import subprocess
    #run python script with predefined data
    data = [sys.executable, script,
                     str(arguments['mysql_port']), arguments['mysql_host'],
                     arguments['mysql_user'], arguments['mysql_password']]
    if arguments['args'] != None:
      data = data + arguments['args']
    result = subprocess.Popen(data, env={'PYTHONPATH': ':'.join(sys.path)})
    result.wait()
  else:
    print "Error: can not read file '%s'" % script


def run_sql_script(arguments):
  script = os.path.join(arguments['target_directory'], arguments['sql_script'])
  print 'Running SQL script: %s' % script
  if os.path.exists(script):
    conn = MySQLdb.connect(host=arguments['mysql_host'],
                           port=int(arguments['mysql_port']),
                           user=arguments['mysql_user'],
                           passwd=arguments['mysql_password'],
                           # XXX ugly, to simplify
                           db=arguments['args'][0])
    cursor = conn.cursor ()
    with open(script, 'r') as f:
      sql_script = f.read()
      cursor.execute(sql_script)
      conn.close()

  else:
    print "Error: can not read file '%s'" % script



def chmod(arguments):
  for path in arguments['chmod_target']:
    path = os.path.join(arguments['target_directory'], path)
    if not os.path.exists(path):
      print "Error when changing mode: '%s': no such file or directory" % path
      continue
    os.chmod(path, int(arguments['mode'], 8))
