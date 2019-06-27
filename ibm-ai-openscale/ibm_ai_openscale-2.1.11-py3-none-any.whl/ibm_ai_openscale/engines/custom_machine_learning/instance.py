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
from .consts import CustomConsts
import uuid
import random
import hashlib


class CustomMachineLearningInstance(AIInstance):
    """
    Describes Custom Machine Learning instance.

    :param service_credentials: credentials of custom instance containing: "url" to list deployments endpoint and optionally "username", "password", "request_headers"
    :type service_credentials: dict

    A way you might use me is:

    >>> credentials = {
    >>>                 "url": "hostname:port",
    >>>                 "username": "username",
    >>>                 "password": "password",
    >>>                 "request_headers": {}
    >>> }
    >>>
    >>> client.bindings.add("Custom instance A", CustomMachineLearningInstance(credentials))
    """

    def __init__(self, service_credentials):
        validate_type(service_credentials, 'service_credentials', dict, True)
        validate_meta_prop(service_credentials, 'url', str, True)
        validate_meta_prop(service_credentials, 'username', str, False)
        validate_meta_prop(service_credentials, 'password', str, False)
        validate_meta_prop(service_credentials, 'request_headers', dict, False)

        #TODO do we need to validate what is inside credentials ???

        if 'instance_id' in service_credentials:
            source_uid = service_credentials['instance_id']
        elif len(service_credentials.keys()) > 0:
            seed = ','.join(list(map(lambda x: str(service_credentials[x]), sorted(service_credentials.keys()))))
            hash_object = hashlib.md5(seed.encode('utf-8'))
            random.seed(int(hash_object.hexdigest(), 16))
            a = "%32x" % random.getrandbits(128)
            rd = a[:12] + '4' + a[13:16] + 'a' + a[17:]
            source_uid = str(uuid.UUID(rd))
        else:
            print("Warning: It is recommended to provide service_credentials content or at least `instance_id` in the service_credentials to mak sure that instance_id for your ml service is correctly set.")
            source_uid = str(uuid.uuid4())
        AIInstance.__init__(self, source_uid, service_credentials.copy(), CustomConsts.SERVICE_TYPE)
