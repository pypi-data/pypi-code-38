##############################################################################
#
# Copyright (c) 2015 Vifib SARL and Contributors. All Rights Reserved.
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

import ConfigParser
import argparse
import collections
import json
import logging
import sys
import traceback
import time
import os
import tempfile

import slapos.slap

from slapos.slap.slap import ConnectionError

from slapos.grid.utils import setRunning, setFinished

from erp5.util.taskdistribution import TaskDistributor
from erp5.util.testnode.Updater import Updater
from erp5.util.testnode.ProcessManager import SubprocessError, ProcessManager, CancellationError



class AutoSTemp(object):
    """
    Create a self-destructing temporary file.
    Uses mkstemp.
    """
    __unlink = os.unlink

    def __init__(self, value):
        fd, self.__name = tempfile.mkstemp()
        os.write(fd, value)
        os.close(fd)

    @property
    def name(self):
        return self.__name

    def __del__(self):
        self.__unlink(self.__name)

from tester import SoftwareReleaseTester

class TestMap(object):
  # tell pytest to skip this class (even if name starts with Test)
  __test__ = False

  def __init__(self, test_dict):
    self.ran_test_set = set()
    self.test_map_dict = collections.OrderedDict()
    for key in test_dict:
      group = test_dict[key].get("group", "default")
      if group not in self.test_map_dict:
        self.test_map_dict[group] = [key]
      else:
        self.test_map_dict[group].append(key)

  def addRanTest(self, test):
    self.ran_test_set.add(test)

  def getExcludeList(self, group):
    exclude_list = []
    for key in self.test_map_dict:
      if key != group:
        exclude_list.extend(self.test_map_dict[key])
    return set(exclude_list + list(self.ran_test_set))

  def getGroupList(self):
    return self.test_map_dict.keys()

  def dropGroup(self, group):
    del self.test_map_dict[group]

  def cleanEmptyGroup(self):
    for key in self.test_map_dict.copy():
      if len(self.test_map_dict[key]) == 0:
        del self.test_map_dict[key]

  def getNextGroup(self, ignore_list):
    for group in self.getGroupList():
      if group not in ignore_list:
        return group

    return None

def loadConfiguration(configuration, logger):
  section_dict = collections.OrderedDict()  
  for section in configuration.sections():
    if section == 'agent':
      continue
    section_dict[section] = section_entry_dict = dict(
        configuration.items(section))
    for key in ('request_kw', ):
      if key in section_entry_dict:
        try:
          if isinstance(section_entry_dict[key], str) or \
               isinstance(section_entry_dict[key], unicode):
            section_entry_dict[key] = json.loads(section_entry_dict[key])
        except Exception:
          logger.error("Fail to load %s on %s" % (key, section_entry_dict))
          raise

    if "group" not in section_entry_dict:
      section_entry_dict["group"] = "default"

  return section_dict

def getLogger(log, verbose):
  formatter = logging.Formatter('%(asctime)s %(message)s')
  logger = logging.getLogger()
  if verbose:
    log_level = logging.DEBUG
  else:
    log_level = logging.INFO
  logger.setLevel(log_level)
  handler = logging.StreamHandler(sys.stdout)
  handler.setFormatter(formatter)
  logger.addHandler(handler)
  log_file = None
  if log:
    handler = logging.FileHandler(log)
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    log_file = open(log)
    log_file.seek(0, 2)

  return logger, log_file

def getAndUpdateFullRevisionList(node_test_suite, working_directory, 
  logger, process_manager, git_binary="git"):
  full_revision_list = []
  base_path = os.path.join(working_directory, 
    node_test_suite.get('test_suite_reference'))
  for vcs_repository in node_test_suite.get('vcs_repository_list', []):
    repository_path = os.path.join(base_path, 
      vcs_repository['buildout_section_id'])

    repository_id = vcs_repository['buildout_section_id']
    branch = vcs_repository.get('branch')
    # Make sure we have local repository
    updater = Updater(repository_path, git_binary=git_binary,
       branch=branch, log=logger.info, process_manager=process_manager,
       working_directory=working_directory,
       url=vcs_repository["url"])

    retry = 10
    while retry:
      try:
        updater.checkout()
      except SubprocessError:
        # Wait a bit and try again
        time.sleep(30)
        retry -= 1
        continue
      finally:
        break 

    revision = "-".join(updater.getRevision())
    full_revision_list.append('%s=%s' % (repository_id, revision))
  node_test_suite['revision'] = ','.join(full_revision_list)
  return full_revision_list

def main():
  """
  Note: This code does not test as much as it monitors.
  The goal is to regularily try to build & instantiate a software release
  on several machines, to monitor vifib stability and SR stability as time
  passes (and things once available online become unavailable).
  Part of this function could be reused to make an actual test bot, testing
  only when actual changes are committed to a software release, to look for
  regressions.

  Note: This code does not connect to any instantiated service, it relies on
  the presence of a promise section to make instantiation fail until promise
  is happy.
  """
  parser = argparse.ArgumentParser()
  parser.add_argument('--pidfile', '-p', help='pidfile preventing parallel '
      'execution.')
  parser.add_argument('--log', '-l', help='Log file path.')
  parser.add_argument('--verbose', '-v', help='Be verbose.',
      action='store_true')
  parser.add_argument('configuration_file', type=argparse.FileType(),
      help='Slap Test Agent configuration file.')
  key_file_dict = {}
  args = parser.parse_args()

  log = args.log

  logger, log_file = getLogger(log, args.verbose)

  configuration = ConfigParser.SafeConfigParser()
  configuration.readfp(args.configuration_file)

  pidfile = args.pidfile
  if pidfile:
    setRunning(logger=logger, pidfile=pidfile)
  try:
    while True:

      section_dict = loadConfiguration(configuration, logger)
 
      agent_parameter_dict = dict(configuration.items('agent'))

      task_distributor = TaskDistributor(agent_parameter_dict['report_url'],
                                         logger=logger)

      task_distributor.subscribeNode(
          node_title=agent_parameter_dict['node_title'], 
          computer_guid="None")

      test_suite_data = task_distributor.startTestSuite(
          node_title=agent_parameter_dict['node_title'], 
          computer_guid="None")

      if type(test_suite_data) == str:
         # Backward compatiblity
         test_suite_data = json.loads(test_suite_data) 
      
      slap_account_key = task_distributor.getSlaposAccountKey()
      slap_certificate = task_distributor.getSlaposAccountCertificate() 
      master_url = task_distributor.getSlaposUrl()

      key_file_dict = {}
      def asFilenamePair(key, cert):
          # Note: python's ssl support only supports fetching key & cert data
          # from on-disk files. This is why we need to "convert" direct data
          # into file paths, using temporary files.
          cert = cert.strip()
          try:
              temp_key, temp_cert = key_file_dict[cert]
          except KeyError:
              temp_key = AutoSTemp(key.strip())
              temp_cert = AutoSTemp(cert)
              key_file_dict[cert] = (temp_key, temp_cert)
          return temp_key.name, temp_cert.name

      key_file, cert_file = asFilenamePair(slap_account_key, 
        slap_certificate) 


      process_manager = ProcessManager(logger.info)

      for test_suite in test_suite_data:

        full_revision_list = getAndUpdateFullRevisionList(test_suite, 
            agent_parameter_dict["working_directory"], logger, process_manager)
        unit_test_dict = task_distributor.generateConfiguration(
          test_suite['test_suite_title'])

        if not len(full_revision_list):
          # We don't watch git revision but we periodically
          # run the test, once a day.
          full_revision_list = ["day=%s" % time.strftime('%Y/%m/%d', time.gmtime())] 

        if type(unit_test_dict) == str:
          # Backward compatiblity
          unit_test_dict = json.loads(unit_test_dict)
    
        test_result = task_distributor.createTestResult(
          revision=','.join(full_revision_list),
          test_name_list=unit_test_dict.keys(),
          node_title=agent_parameter_dict['node_title'],
          allow_restart=False,
          test_title=test_suite['test_suite_title'],
          project_title=agent_parameter_dict['project_title'],
        )
        if test_result is None:
          # We already have a test result
          logger.info('Skiping test for %s, result already available (%s)' % 
            (test_suite['test_suite_title'], ','.join(full_revision_list)))
          continue

        test_result.watcher_period = 120
        assert test_result is not None
    
        if log_file is not None:
          test_result.addWatch(log, log_file, max_history_bytes=10000)
    
        logger.info("Starting to run for %s" % test_result )
    
        test_mapping = TestMap(unit_test_dict)
        logger.info("Running %s tests in parallel." % \
                      len(test_mapping.getGroupList()))
    
        assert master_url.startswith('https:')
        slap = slapos.slap.slap()
        retry = 0
        while True:
          if retry > 100:
             break
          # wait until _hateoas_navigator is loaded.
          slap.initializeConnection(
            master_url, key_file, cert_file, timeout=120)

          if getattr(slap, '_hateoas_navigator', None) is None:
             logger.info("Fail to load _hateoas_navigator waiting a bit and retry.")
             time.sleep(30)
          else:
             break

        if getattr(slap, '_hateoas_navigator', None) is None:
          raise ValueError("Fail to load _hateoas_navigator")
    
        supply = slap.registerSupply()
        order = slap.registerOpenOrder()
    
        running_test_dict = {}
    
        logger.info('Starting Test Agent run %s ' % agent_parameter_dict['node_title'])
        while True:
          # Get up to parallel_task_count tasks to execute
          while len(running_test_dict) < len(test_mapping.getGroupList())\
                and (len(test_mapping.getGroupList()) > 0):
    
            test_mapping.cleanEmptyGroup()
            
            # Select an unused computer to run the test.
            group = test_mapping.getNextGroup(
              ignore_list = [group for _, _, group in \
                           running_test_dict.itervalues()])
    
            # Select a test 
            test_line = test_result.start(
                exclude_list=list(test_mapping.getExcludeList(group)))
    
            logger.info("Test Line: %s " % test_line)
            logger.info("Ran Test Set: %s " % test_mapping.ran_test_set)
            logger.info("Running test dict: %s " % running_test_dict)
            logger.info("Group: %s " % group)
    
            if test_line is None:
              logger.info("Removing Group (empty test line): %s " % group)
              test_mapping.dropGroup(group)
              continue
    
            test_name = test_line.name
            try:
              section_entry_dict = unit_test_dict[test_name]
            except KeyError:
              # We don't know how to execute this test. Assume it doesn't
              # exist anymore, and fail it in result.
              test_line.stop(stderr='This test does not exist on test '
                  'node %s' % (agent_parameter_dict['node_title'], ))
              continue
    
            general_timeout = agent_parameter_dict.get('timeout', 3600) 
            tester = SoftwareReleaseTester(
                test_name + time.strftime('_%Y/%m/%d_%H:%M:%S_+0000', time.gmtime()),
                logger,
                slap,
                order,
                supply,
                section_entry_dict['url'],
                section_entry_dict.get('supply_computer'),
                section_entry_dict.get('request_kw'),
                agent_parameter_dict.get('software_timeout', general_timeout),
                agent_parameter_dict.get('instance_timeout', general_timeout)
            )
            test_mapping.addRanTest(test_name)
            running_test_dict[test_name] = (test_line, tester, group)
    
          if not running_test_dict:
            logger.info('No more tests to run...')
            break
    
          now = time.time()
          # Synchronise refreshes on watcher period, so it doesn't report a
          # stalled test node where we are actually still sleeping.
          # Change test_result.watcher_period outside this loop if you wish
          # to change sleep duration.
          next_deadline = now + test_result.watcher_period
    
          for section, (test_line, tester, group) in running_test_dict.items():
            logger.info('Checking %s: %r...', section, tester)
            try:
              deadline = tester.tic(now)
            except ConnectionError:
              logger.exception('Test execution ConnectionError for  %s' % (section))
              deadline = next_deadline

            except Exception:
              logger.exception('Test execution fail for  %s' % (section))
              test_line.stop(test_count=1, error_count=1, failure_count=0,
                   skip_count=0, command=tester.getInfo(), 
                   stdout=tester.getFormatedLastMessage(), 
                   stderr=traceback.format_exc())
    
              del running_test_dict[section]
              try:
                tester.teardown()
              except slapos.slap.NotFoundError:
                # This exception is ignored because we cannot
                # Teardown if SR URL do not exist.
                logger.exception('Fail and not found')
                pass
              except Exception:
                logger.exception('teardown failed, human assistance needed for cleanup')
                raise
    
            else:
              logger.info('%r' % tester)
              if deadline is None:
                # TODO: report how long each step took.
                logger.info('Test execution finished for  %s' % (section))
                test_line.stop(test_count=1, error_count=0, failure_count=0,
                          skip_count=0, command=tester.getInfo(), stdout=tester.getFormatedLastMessage())
    
                del running_test_dict[section]
                try:
                  pass #tester.teardown()
                except slapos.slap.NotFoundError:
                  # This exception is ignored because we cannot
                  # Teardown if SR URL do not exist.
                  logger.exception('Fail and not found')
                  pass
                except Exception:
                  logger.exception('teardown failed, human assistance needed for cleanup')
                  raise
    
              else:
                next_deadline = min(deadline, next_deadline)
    
          if running_test_dict:
            to_sleep = next_deadline - time.time()
            if to_sleep > 0:
              logger.info('Sleeping %is...', to_sleep)
              time.sleep(to_sleep)
            if not test_result.isAlive():
              for _, tester, computer_id in running_test_dict.itervalues():
                tester.teardown()

      time.sleep(300)    
  finally:
    if pidfile:
        setFinished(pidfile)
    key_file_dict.clear()
  
if __name__ == '__main__':
  main()
