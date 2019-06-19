# -*- coding: utf-8 -*-
##############################################################################
#
# Copyright (c) 2014 Vifib SARL and Contributors. All Rights Reserved.
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

from .slaprunner import SlaprunnerTestSuite

import json
import random
import string
import time
import requests

class NotHttpOkException(Exception):
  pass

class GitlabTestSuite(SlaprunnerTestSuite):
  """
  Run Gitlab inside Slaprunner Resiliency Test.
  Note: requires specific kernel allowing long shebang paths.
  """

  def _setGitlabInstanceParameter(self):
    """
    Set inside of slaprunner the instance parameter to use to deploy gitlab instance.
    """
    self.logger.info('Updating instance parameter to use to deploy gitlab instance...')
    self._connectToSlaprunner(
        resource='saveParameterXml',
        data='software_type=gitlab-test&parameter=%3C%3Fxml%20version%3D%221.0%22%20encoding%3D%22utf-8%22%3F%3E%0A%3Cinstance%3E%0A%3C%2Finstance%3E'
    )

  def _connectToGitlab(self, path='', post_data=None, url='', parameter_dict={}):
    request_url = self.backend_url
    if url:
      request_url = url
    if path:
      request_url += '/' + path
    headers = {"PRIVATE-TOKEN" : self.private_token}
    if post_data is None:
      response = requests.get(request_url, params=parameter_dict,
                              headers=headers, verify=False)
    elif post_data == {}:
      response = requests.post(request_url, params=parameter_dict,
                                headers=headers, verify=False)
    else:
      response = requests.post(request_url, params=parameter_dict,
                                headers=headers, data=post_data, verify=False)
    if not response.ok:
      raise Exception("ERROR connecting to Gitlab: %s: %s \n%s" % (
        response.status_code, response.reason, response.text))
    return response.text

  def _createNewProject(self, name, namespace='open'):
    uri = 'api/v3/projects'
    parameter_dict = {'name': name, 'namespace': namespace}
    return self._connectToGitlab(uri, post_data={}, parameter_dict=parameter_dict)

  def _listProjects(self):
    path = 'api/v3/projects'
    return json.loads(self._connectToGitlab(path=path))

  def _setGitlabConnectionParameter(self):
    """
    set parameters of gitlab instance.
    Note: it is not connection parameter of slaprunner,
    but connection parameter of what is inside of webrunner.
    """
    data = self._connectToSlaprunner(
        resource='getConnectionParameter/slappart0'
    )
    parameter_dict = json.loads(data)
    self.backend_url = parameter_dict['backend_url']
    self.password = parameter_dict['password']
    self.private_token = parameter_dict['private-token']
    self.file_uri = parameter_dict['latest-file-uri']

  def _getRootPassword(self):
    data = self._connectToSlaprunner(
        resource='getConnectionParameter/slappart0'
    )
    password = json.loads(json.loads(data)['_'])['password']
    self.logger.info('Retrieved gitlab root password is:\n%s' % password)
    return password

  def generateData(self):
    self.slaprunner_password = ''.join(
        random.SystemRandom().sample(string.ascii_lowercase, 8)
    )
    self.slaprunner_user = 'slapos'
    self.logger.info('Generated slaprunner user is: %s' % self.slaprunner_user)
    self.logger.info('Generated slaprunner password is: %s' % self.slaprunner_password)

  def pushDataOnMainInstance(self):
    """
    Create a dummy Software Release,
    Build it,
    Wait for build to be successful,
    Deploy instance,
    Wait for instance to be started.
    Store the main IP of the slaprunner for future use.
    """

    self.logger.debug('Getting the backend URL...')
    parameter_dict = self._getPartitionParameterDict()
    self.slaprunner_backend_url = parameter_dict['backend-url']
    self.logger.info('backend_url is %s.' % self.slaprunner_backend_url)
    self.slaprunner_user = parameter_dict['init-user']
    self.slaprunner_password = parameter_dict['init-password']

    self._login()
    time.sleep(10)

    self._gitClone()
    self._openSoftwareRelease('gitlab')
    self._setGitlabInstanceParameter()

    self.logger.info('Waiting for 1 minutes...')
    # Debug, remove me.
    time.sleep(60)

    self._buildSoftwareRelease()
    self._deployInstance()
    # wait for unicorn to start then run instance again to install gitlab backup
    self.logger.info('wait 1 minute for unicorn to start then run instance...')
    time.sleep(60)
    self._deployInstance()
    self._deployInstance()
    # Stop all services because we want to restart gitlab (safe)
    self.logger.info('Stop all services because we want to restart gitlab..')
    self._connectToSlaprunner('/stopAllPartition')
    self._deployInstance()

    self._setGitlabConnectionParameter()
    self.logger.info('Retrieved gitlab url is:\n%s' % self.backend_url)
    self.logger.info('Gitlab root password is:\n%s' % self.password)
    self.logger.info('Gitlab private token is:\n%s' % self.private_token)

    self.logger.info('Waiting 90 seconds so that gitlab can be started...')
    time.sleep(90)

    self.logger.info('Trying to connect to gitlab backend URL...')
    loop = 0
    while loop < 3:
      try:
        self._connectToGitlab(url=self.backend_url)
      except Exception, e:
        if loop == 2:
          raise
        self.logger.warning(str(e))
        self.logger.info('Retry connection in 60 seconds...')
        loop += 1
        time.sleep(60)
      else:
        self.logger.info('success!')
        break

    self.logger.info(self._createNewProject('sample.test'))
    project_list = self._listProjects()
    self.default_project_list = []
    for project in project_list:
      self.default_project_list.append(project['name_with_namespace'])

    self.logger.info('Gitlab project list is:\n%s' % self.default_project_list)
    self.logger.info('Getting test file at url: %s' % self.file_uri)
    self.sample_file = self._connectToGitlab(url=self.file_uri)

    self.logger.info('Wait 10 minutes for main instance to have backup of gitlab...')
    time.sleep(600)

    # in erp5testnode, we have only one IP, so we can't run at the same time
    # gitlab in webrunner of main instance, and other services in import script of clone instance
    # So we stop main instance processes.
    self._connectToSlaprunner('/stopAllPartition')

    self.logger.info('Wait half an hour for clone to have compiled Gitlab SR...')
    #time.sleep(3600 / 2)
    time.sleep(600)

  def checkDataOnCloneInstance(self):
    """
    Check that:
      * backend_url is different
      * Software Release profile is the same,
      * Software Release is built and is the same,
      * Instance is deployed and is the same (contains same new data).
    """
    old_slaprunner_backend_url = self.slaprunner_backend_url
    self.slaprunner_backend_url = self._returnNewInstanceParameter(
        parameter_key='backend-url',
        old_parameter_value=old_slaprunner_backend_url,
        force_new=True,
    )
    self._login()
    self._waitForSoftwareBuild()
    self._deployInstance()
    time.sleep(60)

    project_list = self._listProjects()
    success = True
    for project in project_list:
      success = success and (project['name_with_namespace'] in self.default_project_list)

    if success:
      file_content = self._connectToGitlab(url=self.file_uri)
      success = success and (file_content == self.sample_file)

    if success:
      self.logger.info('Data are the same: success.')
      return True
    else:
      self.logger.info('Data are different: failure.')
      return False


def runTestSuite(*args, **kwargs):
  """
  Run Slaprunner Resiliency Test.
  """
  return GitlabTestSuite(*args, **kwargs).runTestSuite()

