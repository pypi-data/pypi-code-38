#!/usr/bin/env python
# -*- coding: utf-8 -*-

import argparse
import csv
import datetime
import json
import httplib
import os
import shutil
import socket
import subprocess
import sys
import time
import traceback
import urllib2
import urlparse
import uuid

def createStatusItem(item_directory, instance_name, callback, date, link, status):
  global app
  callback_short_name = os.path.basename(callback)
  content = json.dumps({
    'title': '%s-PBS %s : %s' % (instance_name, callback_short_name, status),
    'description': '%s run at %s' % (callback_short_name, datetime.datetime.fromtimestamp(date).isoformat()),
    'pubDate': date,
    'link': link,
  })

  item_path = os.path.join(item_directory, "status_%s" % time.time())
  with open(item_path, 'w') as file:
    file.write(content)


def main():
  parser = argparse.ArgumentParser()
  parser.add_argument('-l', '--log', nargs=1, required=True,
                      dest='logfile', metavar='logfile',
                      help="Logging file")
  parser.add_argument('-t', '--title', nargs=1, required=True,
                      help="Entry title.")
  parser.add_argument('-f', '--feed', nargs=1, required=True,
                      dest='feed_url', help="Url of the feed.")
  parser.add_argument('--notification-url', dest='notification_url',
                      nargs='*', required=True,
                      help="Notification url")
  parser.add_argument('--executable', nargs=1, dest='executable',
                      help="Executable to wrap")
  parser.add_argument('--transaction-id', nargs=1, dest='transaction_id',
                      type=int, required=False,
                      help="Additional parameter for notification-url")
  parser.add_argument('--max-run', dest='max_run',
                      type=int, default=1, required=False,
                      help="Run executable until it ends correctly, in a limit of max-run times")

  # Verbose mode
  parser.add_argument('--instance-root-name', dest='instance_root_name',
                      type=str, required=False,
                      help="Path to config file containing info on instance")
  parser.add_argument('--log-url', required=False, dest='log_url',
                      help="URL where the log file will be accessible")
  parser.add_argument('--status-item-directory', dest='status_item_directory',
                      required=False, default='', type=str,
                      help="Directory containing PBS status to publish as feed.")

  args = parser.parse_args()

  if args.instance_root_name and args.log_url and args.status_item_directory:
    # Verbose mode
    saveStatus = lambda status: createStatusItem(args.status_item_directory,
                                  args.instance_root_name,
                                  args.executable[0],
                                  time.time(),
                                  args.log_url,
                                  status)
  else:
    saveStatus = lambda status: None

  saveStatus('STARTED')

  if args.max_run <= 0:
    print "--max-run argument takes a strictely positive number as argument"
    sys.exit(-1)

  while args.max_run > 0:
    try:
      content = subprocess.check_output(
          args.executable[0],
          stderr=subprocess.STDOUT
      )
      exit_code = 0
      content = ("OK</br><p>%s ran successfully</p>"
                    "<p>Output is: </p><pre>%s</pre>" % (
            args.executable[0],
            content.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')
        ))
      saveStatus('FINISHED')
      break
    except subprocess.CalledProcessError as e:
      args.max_run -= 1
      saveStatus('ERROR')
      content = e.output
      exit_code = e.returncode
      content = ("FAILURE</br><p>%s Failed with returncode <em>%d</em>.</p>"
                    "<p>Output is: </p><pre>%s</pre>" % (
            args.executable[0],
            exit_code,
            content.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')
        ))

  print content

  # Write feed safely
  error_message = ""
  temp_file = args.logfile[0] + '.tmp'
  try:
    shutil.copy2(args.logfile[0], temp_file)
  except IOError:
    # previous feed can be rotated, only pass
    pass
  try:
    with open(temp_file, 'a') as file_:
      csvfile = csv.writer(file_)
      csvfile.writerow([
        int(time.time()),
        args.title[0],
        content,
        'slapos:%s' % uuid.uuid4(),
      ])
    os.rename(temp_file, args.logfile[0])
  except Exception, e:
    error_message = "ERROR ON WRITING FEED - %s" % str(e)
  finally:
    try:
      os.remove(temp_file)
    except OSError:
      pass

  if error_message:
    saveStatus(error_message)
    exit_code = 1

  if exit_code != 0:
    sys.exit(exit_code)

  print 'Fetching %s feed...' % args.feed_url[0]

  feed = urllib2.urlopen(args.feed_url[0])
  body = feed.read()

  some_notification_failed = False
  for notif_url in args.notification_url:
    notification_url = urlparse.urlparse(notif_url)

    notification_port = notification_url.port
    if notification_port is None:
      notification_port = socket.getservbyname(notification_url.scheme)

    notification_path = notification_url.path
    if not notification_path.endswith('/'):
      notification_path += '/'

    transaction_id = args.transaction_id[0] if args.transaction_id else int(time.time()*1e6)
    notification_path += str(transaction_id)

    headers = {'Content-Type': feed.info().getheader('Content-Type')}
    try:
      notification = httplib.HTTPConnection(notification_url.hostname,
                                            notification_port)
      notification.request('POST', notification_path, body, headers)
      response = notification.getresponse()
      if not (200 <= response.status < 300):
        error_message = ("The remote server at %s didn't send a successful reponse.\n"
                         "Its response was %r\n" % (notif_url, response.reason))
        some_notification_failed = True
    except socket.error as exc:
      error_message = "Connection with remote server at %s failed:\n" % notif_url
      error_message += traceback.format_exc(exc)
      some_notification_failed = True
    finally:
      if error_message:
        sys.stderr.write(error_message)
        saveStatus('ERROR ON NOTIFYING : %s' % error_message)

  if some_notification_failed:
    sys.exit(1)

  saveStatus('OK')

if __name__ == '__main__':
  main()

