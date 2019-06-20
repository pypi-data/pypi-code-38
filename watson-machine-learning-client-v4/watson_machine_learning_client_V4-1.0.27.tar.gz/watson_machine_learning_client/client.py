################################################################################
#
# Licensed Materials - Property of IBM
# (C) Copyright IBM Corp. 2017
# US Government Users Restricted Rights - Use, duplication disclosure restricted
# by GSA ADP Schedule Contract with IBM Corp.
#
################################################################################

from watson_machine_learning_client.log_util import get_logger
from watson_machine_learning_client.utils import version
from watson_machine_learning_client.learning_system import LearningSystem
from watson_machine_learning_client.experiments import Experiments
from watson_machine_learning_client.repository import Repository
from watson_machine_learning_client.models import Models
from watson_machine_learning_client.pipelines import Pipelines
from watson_machine_learning_client.instance import ServiceInstance
from watson_machine_learning_client.deployments import Deployments
from watson_machine_learning_client.training import Training
from watson_machine_learning_client.runtimes import Runtimes
from watson_machine_learning_client.functions import Functions
from watson_machine_learning_client.spaces import Spaces
from watson_machine_learning_client.wml_client_error import NoWMLCredentialsProvided
from watson_machine_learning_client.wml_client_error import WMLClientError

import os

'''
.. module:: WatsonMachineLearningAPIClient
   :platform: Unix, Windows
   :synopsis: Watson Machine Learning API Client.

.. moduleauthor:: IBM
'''


class WatsonMachineLearningAPIClient:

    def __init__(self, wml_credentials, project_id=None):
        self._logger = get_logger(__name__)
        if wml_credentials is None:
            raise NoWMLCredentialsProvided()
        if 'icp' == wml_credentials[u'instance_id'].lower():
            self.ICP = True
            os.environ["DEPLOYMENT_PLATFORM"] = "private"
        else:
            self.ICP = False
        if "token" in wml_credentials:
            self.proceed = True
        else:
            self.proceed = False
        self.wml_credentials = wml_credentials
        self.project_id = project_id
        self.wml_token = None
        self.service_instance = ServiceInstance(self)
        if not self.ICP:
            self.service_instance.details = self.service_instance.get_details()
        #    self.learning_system = LearningSystem(self)
        self.repository = Repository(self)
        self._models = Models(self)
        self.deployments = Deployments(self)
        self.training = Training(self)
        self.spaces = Spaces(self)
        self.experiments = Experiments(self)
        self.runtimes = Runtimes(self)
        self.pipelines = Pipelines(self)
        self._functions = Functions(self)
        self._logger.info(u'Client successfully initialized')
        self.version = version()

    def _get_headers(self, content_type='application/json', no_content_type=False):
        if self.proceed is True:
            token = "Bearer "+ self.wml_credentials["token"]
        else:
            token = "Bearer " + self.service_instance._get_token()
        headers = {
            'Authorization': token,
            'X-WML-User-Client': 'PythonClient'
        }
        if self._is_IAM() or (self.service_instance._is_iam() is None):
            headers['ML-Instance-ID'] = self.wml_credentials['instance_id']
        headers.update({'x-wml-internal-switch-to-new-v4': "true"})
        if not self.ICP:
            #headers.update({'x-wml-internal-switch-to-new-v4': "true"})
            if self.project_id is not None:
                headers.update({'X-Watson-Project-ID': self.project_id})

        if not no_content_type:
            headers.update({'Content-Type': content_type})

        return headers

    def _get_icptoken(self):
        return self.service_instance._create_token()

    def _is_IAM(self):
        if('apikey' in self.wml_credentials.keys()):
            if (self.wml_credentials['apikey'] != ''):
                return True
            else:
                raise WMLClientError('apikey value cannot be \'\'. Pass a valid apikey for IAM token.')

        else:
            return False