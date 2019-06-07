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
from .consts import SPSSConsts
import uuid


class SPSSMachineLearningInstance(AIInstance):
    """
    Describes SPSS C&DS instance.

    :param service_credentials: credentials of SPSS C&DS instance
    :type service_credentials: dict

    A way you might use me is:

    >>> credentials = {
    >>>                 "username": "username",
    >>>                 "password": "password",
    >>>                 "url": "url",
    >>> }
    >>>
    >>> client.bindings.add("SPSS C&DS instance A", SPSSMachineLearningInstance(credentials))
    """

    def __init__(self, service_credentials):
        validate_type(service_credentials, 'service_credentials', dict, True)
        validate_type(service_credentials['url'], 'service_credentials.url', str, True)
        validate_type(service_credentials['username'], 'service_credentials.username', str, True)
        validate_type(service_credentials['password'], 'service_credentials.password', str, True)


        #TODO do we need to validate what is inside credentials ??
        AIInstance.__init__(self, str(uuid.uuid4()), service_credentials, SPSSConsts.SERVICE_TYPE)
