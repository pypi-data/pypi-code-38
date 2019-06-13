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

import slapos.slap

import glob
import logging
import os
import subprocess
import sys
import time
import urllib2

UNIT_TEST_ERP5TESTNODE = 'UnitTest'

class ResiliencyTestSuite(object):
  """
  Abstract class supposed to be extended by Resiliency Test Suites.
  """
  def __init__(self,
               server_url, key_file, cert_file,
               computer_id, partition_id, software,
               namebase,
               root_instance_name,
               sleep_time_between_test=900,
               total_instance_count="2",
               type=None):
    self.server_url = server_url
    self.key_file = key_file
    self.cert_file = cert_file
    self.computer_id = computer_id
    self.partition_id = partition_id
    self.software = software
    self.namebase = namebase
    self.total_instance_count = total_instance_count
    self.root_instance_name = root_instance_name
    self.sleep_time_between_test = sleep_time_between_test
    self.test_type = type

    slap = slapos.slap.slap()
    slap.initializeConnection(server_url, key_file, cert_file)
    self.partition = slap.registerComputerPartition(
        computer_guid=computer_id,
        partition_id=partition_id
    )

    self.logger = logging.getLogger('SlaprunnerResiliencyTest')
    self.logger.setLevel(logging.DEBUG)

  def _doTakeover(self, namebase, target_clone):
    """
    Private method.
    Make the specified clone instance takeover the main instance.
    """
    self.logger.info('Replacing main instance by clone instance %s%s...' % (
        self.namebase, target_clone))

    # Request
    root_partition_parameter_dict = self._getPartitionParameterDict()
    takeover_url = root_partition_parameter_dict['takeover-%s-%s-url' % (namebase, target_clone)]
    takeover_password = root_partition_parameter_dict['takeover-%s-%s-password' % (namebase, target_clone)]
    # Connect to takeover web interface
    takeover_page_content = urllib2.urlopen(takeover_url).read()
    # Wait for importer script to be not running
    while 'Importer script(s) of backup in progress: True' in takeover_page_content:
      time.sleep(10)
      takeover_page_content = urllib2.urlopen(takeover_url).read()
    # Do takeover
    takeover_result = urllib2.urlopen('%s?password=%s' % (takeover_url, takeover_password)).read()
    if 'Error' in takeover_result:
      raise Exception('Error while doing takeover: %s' % takeover_result)

    self.logger.info('Done.')

  def generateData(self):
    """
    Generate data that will be used by the test.
    """
    raise NotImplementedError('Overload me, I am an abstract method.')

  def pushDataOnMainInstance(self):
    """
    Push our data to the main instance.
    """
    raise NotImplementedError('Overload me, I am an abstract method.')

  def checkDataOnCloneInstance(self):
    """
    Check that, on the ex-clone, now-main instance, data is the same as
    what we pushed to the ex-main instance.
    """
    raise NotImplementedError('Overload me, I am an abstract method.')

  def deleteTimestamp():
    """
    XXX-Nicolas delete .timestamp in test partition to force the full processing
    by slapgrid, to force the good parameters to be passed to the instances of the tree
    """
    home = os.getenv('HOME')
    timestamp = os.path.join(home, '.timestamp')
    os.remove(timestamp)

  def _getPartitionParameterDict(self):
    """
    Helper.
    Return the partition parameter dict of the main root ("resilient") instance.
    """
    return self.partition.request(
        software_release=self.software,
        software_type='resilient',
        partition_reference=self.root_instance_name
    ).getConnectionParameterDict()
    self.deleteTimestamp()

  def _returnNewInstanceParameter(self, parameter_key, old_parameter_value, force_new=False):
    """
    Helper, can be used inside of checkDataOnCloneInstance.
    Wait for the new parameter (of old-clone new-main instance) to appear.
    Check than it is different from the old parameter
    """
    # if we are inside of a classical erp5testnode: just return the same parameter.
    if self.test_type == UNIT_TEST_ERP5TESTNODE and not force_new:
      return old_parameter_value

    self.logger.info('Waiting for new main instance to be ready...')
    new_parameter_value = None
    while not new_parameter_value or new_parameter_value == 'None' or  new_parameter_value == old_parameter_value:
      self.logger.info('Not ready yet. SlapOS says new parameter value is %s' % new_parameter_value)
      new_parameter_value = self._getPartitionParameterDict().get(parameter_key, None)
      time.sleep(30)
    self.logger.info('New parameter value of instance is %s' % new_parameter_value)
    return new_parameter_value

  def _testClone(self, clone):
    """
    Private method.
    Launch takeover and check for a specific clone.
    """
    # Wait for XX minutes so that replication is done
    self.logger.info(
      'Sleeping for %s seconds before testing clone %s.' % (
          self.sleep_time_between_test,
          clone
        ))
    time.sleep(self.sleep_time_between_test)

    # Before doing takeover we expect the instances to be in a stable state
    if not self._testPromises():
      return False

    self.logger.info('Testing %s%s instance.' % (self.namebase, clone))
    self._doTakeover(self.namebase, clone)

    if self.test_type == UNIT_TEST_ERP5TESTNODE: # Run by classical erp5testnode using slapproxy
      # Run manually slapos node instance
      # XXX hardcoded path
      self.logger.info('Running "slapos node instance"...')
      slapos_configuration_file_path = os.path.join(
          os.path.dirname(sys.argv[0]),
          '..', '..', '..', 'slapos.cfg'
      )
      # Output is huge and we don't want to store it in memory nor print it
      devnull = open('/dev/null', 'w')
      command = [os.path.join(os.environ['HOME'], 'software_release', 'bin', 'slapos'), 'node', 'instance',
                 '--cfg=%s' % slapos_configuration_file_path,
                 '--pidfile=slapos.pid']
      subprocess.Popen(command, stdout=devnull, stderr=devnull).wait()
      subprocess.Popen(command, stdout=devnull, stderr=devnull).wait()
      subprocess.Popen(command, stdout=devnull, stderr=devnull).wait()

    success = self.checkDataOnCloneInstance()

    if success:
      return True

  def _testPromises(self):
    """
    Run promises in all instances (export, PBS, import(s)) and
    check their output. An error at any step of the resilience
    should make at least one of the promises complain.
    """
    for promise_directory in glob.glob(
        os.path.realpath(os.path.join(os.path.dirname(sys.argv[0]), '..', '..', '..', 'inst*', '*', 'etc', 'promise'))):
      self.logger.info("Testing promises of instance's directory : %s", promise_directory)
      promise_list = os.listdir(promise_directory)
      for promise in promise_list:
        # XXX: for the moment ignore monitor promises as they can never succeed
        # in a testnode environment.
        if 'monitor' in promise:
          continue
        try:
          process = subprocess.check_output(os.path.join(promise_directory, promise))
        except subprocess.CalledProcessError as e:
          self.logger.error('ERROR : promise "%s" failed with output :\n%s', promise, e.output)
          return False

    return True

  def runTestSuite(self):
    """
    Generate data to send,
    Push data on main instance,
    Wait for replication to be done,
    For each clone: Do a takeover, Check data.
    """
    self.generateData()

    self.pushDataOnMainInstance()

    # In resilient stack, main instance (example with KVM) is named "kvm0",
    # clones are named "kvm1", "kvm2", ...
    clone_count = int(self.total_instance_count) - 1
    # So first clone starts from 1.
    current_clone = 1

    # In case we have only one clone: test the takeover twice
    # so that we test the reconstruction of a new clone.
    if clone_count == 1:
      return self._testClone(1)
      #for i in range(2):
      #  success = self._testClone(1)
      #  if not success:
      #    return False

    else:
      # Test each clone
      while current_clone <= clone_count:
        success = self._testClone(current_clone)
        if not success:
          return False
        current_clone = current_clone + 1

    # All clones have been successfully tested: success.
    return True

