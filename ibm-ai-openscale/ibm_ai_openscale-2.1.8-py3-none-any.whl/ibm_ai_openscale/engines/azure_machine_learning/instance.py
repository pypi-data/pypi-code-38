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
from .consts import AzureConsts
import uuid


class AzureMachineLearningInstance(AIInstance):
    """
    Describes Microsoft Azure Machine Learning instance.

    :param service_credentials: credentials of azure machine learning studio instance
    :type service_credentials: dict

    A way you might use me is:

    >>> credentials = {
    >>>                 "tenant": "username",
    >>>                 "client_secret": "password",
    >>>                 "subscription_id": "id",
    >>>                 "client_id": "id"
    >>> }
    >>>
    >>> client.bindings.add("Azure instance A", AzureMachineLearningInstance(credentials))
    """

    def __init__(self, service_credentials):
        validate_type(service_credentials, 'service_credentials', dict, True)
        validate_type(service_credentials['tenant'], 'service_credentials.tenant', str, True)
        validate_type(service_credentials['client_secret'], 'service_credentials.client_secret', str, True)
        validate_type(service_credentials['subscription_id'], 'service_credentials.subscription_id', str, True)
        validate_type(service_credentials['client_id'], 'service_credentials.client_id', str, True)

        #TODO do we need to validate what is inside credentials ???
        AIInstance.__init__(self, str(uuid.uuid4()), service_credentials, AzureConsts.SERVICE_TYPE)
