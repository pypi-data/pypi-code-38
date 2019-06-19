# -*- coding: utf-8 -*-
##############################################################################
#
# Copyright (c) 2013 Vifib SARL and Contributors. All Rights Reserved.
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

from .resiliencytestsuite import ResiliencyTestSuite

import logging
import random
import string
import time
import urllib

logger = logging.getLogger('KVMResiliencyTest')

def fetchKey(ip):
  """
  Fetch the key that had been set on original virtual hard drive.
  If doesn't exist (503), fail. If other error: retry after a few minutes,
  fail after XX (2?) hours.
  """
  new_key = None
  for i in range(0, 10):
    try:
      new_key = urllib.urlopen('http://%s:10080/get' % ip).read().strip()
      break
    except IOError:
      logger.error('Server in new KVM does not answer.')
      time.sleep(60)

  if not new_key:
    raise Exception('Server in new KVM does not answer for too long.')

  return new_key

class KVMTestSuite(ResiliencyTestSuite):
  """
  Run KVM Resiliency Test.
  Requires a specific KVM environment (virtual hard drive), see KVM SR for more
  informations.

  Scenario:
  1/ Boot from a custom image
  2/ The VM from the main instance starts a simple get/set server. It will receive a random number sent from the resiliency test. The VM will store this number, and the test suite will store the number as well.
  3/ Resilience is done, wait XX seconds
  4/ For each clone: do a takeover. Check that IPv6 of new main instance is different. Check, when doing a http request to the new VM that will fetch the stored random number, that the sent number is the same.

  Note: disk image is a simple debian with gunicorn and flask installed:
    apt-get install python-setuptools; easy_install gunicorn flask
  With the following python code running at boot in /root/number.py:

  import os

  from flask import Flask, abort, request
  app = Flask(__name__)

  storage = 'storage.txt'

  @app.route("/")
  def greeting_list(): # 'cause there are several greetings, and plural is forbidden.
    return "Hello World"

  @app.route("/get")
  def get():
    return open(storage, 'r').read()

  @app.route("/set")
  def set():
    #if os.path.exists(storage):
    #  abort(503)
    open(storage, 'w').write(request.args['key'])
    return "OK"

  if __name__ == "__main__":
    app.run(host='0.0.0.0', port=80)


  Then create the boot script:
  echo "cd /root; /usr/local/bin/gunicorn number:app -b 0.0.0.0:80 -D --error-logfile /root/error_log --access-logfile /root/access_log" > /etc/init.d/gunicorn-number
  chmod +x /etc/init.d/gunicorn-number
  update-rc.d gunicorn-number defaults


  There also is a script that randomly generates I/O in /root/io.sh:

  #!/bin/sh
  # Randomly generates high I/O on disk. Goal is to write on disk so that
  # it flushes at the same time that snapshot of disk image is done, to check if
  # it doesn't corrupt image.
  # Ayayo!
  while [ 1 ]; do
    dd if=/dev/urandom of=random count=2k
    sync
    sleep 0.2
  done

  Then create the boot script:
  echo "/bin/sh /root/io.sh &" > /etc/init.d/io
  chmod +x /etc/init.d/io
  update-rc.d io defaults

  """

  def _getPartitionParameterDict(self):
    """
    Overload default method.
    """
    return self.partition.request(
        software_release=self.software,
        software_type='kvm-resilient',
        partition_reference=self.root_instance_name).getConnectionParameterDict()

  def generateData(self):
    """
    Set a random key that will be stored inside of the virtual hard drive.
    """
    self.key = ''.join(random.SystemRandom().sample(string.ascii_lowercase, 20))
    self.logger.info('Generated key is: %s' % self.key)

  def pushDataOnMainInstance(self):
    self.logger.info('Getting the KVM IP...')
    self.ip = self._getPartitionParameterDict()['ipv6']
    logger.info('KVM IP is %s.' % self.ip)

    for i in range(0, 60):
      failure = False
      try:
        connection = urllib.urlopen('http://%s:10080/set?key=%s' % (self.ip, self.key))
        if connection.getcode() is 200:
          break
        else:
          failure = True
      except IOError:
        failure = True
      finally:
        if failure:
          logger.info('Impossible to connect to virtual machine to set key. sleeping...')
          time.sleep(60)
      if i is 59:
        raise Exception('Bad return code when setting key in main instance, after trying for 60 minutes.')

    logger.info('Key uploaded to KVM main instance.')

  def checkDataOnCloneInstance(self):
    self.ip = self._returnNewInstanceParameter(
        parameter_key='ipv6',
        old_parameter_value=self.ip
    )

    new_key = fetchKey(self.ip)
    logger.info('Key on this new instance is %s' % new_key)

    # Compare with original key. If same: success.
    if new_key == self.key:
      self.logger.info('Data are the same: success.')
      return True
    else:
      self.logger.info('Data are different: failure.')


def runTestSuite(*args, **kwargs):
  """
  Run KVM Resiliency Test.
  """
  return KVMTestSuite(*args, **kwargs).runTestSuite()
