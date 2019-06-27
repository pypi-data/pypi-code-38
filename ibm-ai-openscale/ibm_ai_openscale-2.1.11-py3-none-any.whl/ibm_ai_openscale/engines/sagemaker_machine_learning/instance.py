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
from .consts import SageMakerConsts
import uuid


class SageMakerMachineLearningInstance(AIInstance):
    """
    Describes Amazon SageMaker Machine Learning instance.

    :param service_credentials: credentials of sagemaker machine learning instance
    :type service_credentials: dict

    A way you might use me is:

    >>> credentials = {
    >>>                 "access_key_id": "id",
    >>>                 "secret_access_key": "key",
    >>>                 "region": "region",
    >>> }
    >>>
    >>> client.bindings.add("SageMaker instance S", SageMakerMachineLearningInstance(credentials))
    """

    def __init__(self, service_credentials):
        validate_type(service_credentials, 'service_credentials', dict, True)
        validate_type(service_credentials['access_key_id'], 'service_credentials.access_key_id', str, True)
        validate_type(service_credentials['secret_access_key'], 'service_credentials.secret_access_key', str, True)
        validate_type(service_credentials['region'], 'service_credentials.region', str, True)

        AIInstance.__init__(self, str(uuid.uuid4()), service_credentials, SageMakerConsts.SERVICE_TYPE)
