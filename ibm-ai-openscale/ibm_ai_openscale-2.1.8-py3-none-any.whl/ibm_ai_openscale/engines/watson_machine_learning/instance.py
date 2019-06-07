# ----------------------------------------------------------------------------------------------------
# IBM Confidential
# OCO Source Materials
# 5900-A3Q, 5737-J33
# Copyright IBM Corp. 2018
# The source code for this program is not published or other-wise divested of its trade 
# secrets, irrespective of what has been deposited with the U.S.Copyright Office.
# ----------------------------------------------------------------------------------------------------

from ibm_ai_openscale.base_classes.instances import AIInstance
from ibm_ai_openscale.utils import *
from ibm_ai_openscale.utils.client_errors import *
from .consts import WMLConsts


class WatsonMachineLearningInstance(AIInstance):
    """
    Describes Watson Machine Learning instance.

    :param service_credentials: credentials of WML instance
    :type service_credentials: dict
    """
    def __init__(self, service_credentials):
        validate_type(service_credentials, 'service_credentials', dict, True)
        validate_type(service_credentials['instance_id'], 'service_credentials.instance_id', str, True)
        validate_type(service_credentials['url'], 'service_credentials.url', str, True)

        # TODO workaround - removed when such check present in config service
        if 'us-south' not in service_credentials['url']:
            UnsupportedEngine.print_msg(operation_name='engine binding', expected_engine='Watson Machine Learning', expected_region='Dallas')

        validate_type(service_credentials['apikey'], 'service_credentials.apikey', str, True)
        validate_type(service_credentials['username'], 'service_credentials.username', str, True)
        validate_type(service_credentials['password'], 'service_credentials.password', str, True)
        AIInstance.__init__(self, service_credentials['instance_id'], service_credentials, WMLConsts.SERVICE_TYPE)
