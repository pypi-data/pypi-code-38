# ----------------------------------------------------------------------------------------------------
# IBM Confidential
# OCO Source Materials
# 5900-A3Q, 5737-J33
# Copyright IBM Corp. 2018
# The source code for this program is not published or other-wise divested of its trade 
# secrets, irrespective of what has been deposited with the U.S.Copyright Office.
# ----------------------------------------------------------------------------------------------------

import copy
from types import ModuleType
from ibm_ai_openscale.base_classes.clients import Client, KnownServiceClient
from ibm_ai_openscale.engines.watson_machine_learning.consts import WMLConsts
from ibm_ai_openscale.engines.watson_machine_learning.client import WMLClient
from ibm_ai_openscale.engines.sagemaker_machine_learning.sagemaker_client import SageMakerClient
from ibm_ai_openscale.engines.sagemaker_machine_learning.consts import SageMakerConsts
from ibm_ai_openscale.engines.custom_machine_learning.custom_client import CustomClient
from ibm_ai_openscale.engines.custom_machine_learning.consts import CustomConsts
from ibm_ai_openscale.engines.azure_machine_learning.consts import AzureConsts
from ibm_ai_openscale.engines.azure_machine_learning.azure_client import AzureClient
from ibm_ai_openscale.engines.spss_machine_learning.consts import SPSSConsts
from ibm_ai_openscale.engines.spss_machine_learning import SPSSClient
from .utils.client_errors import ClientError
from .utils import validate_type, logging_class
from .bindings import Bindings
from concurrent.futures import ThreadPoolExecutor


def find_client_classes(module_obj, max_depth=5):
    elements = []

    if max_depth < 0:
        return []

    for el in module_obj.__dict__.values():
        if type(el) is ModuleType:
            elements.extend(find_client_classes(el, max_depth-1))
        elif type(el) is type:
            if issubclass(el, Client) and el is not Client and el is not KnownServiceClient:
                elements.append(el)

    return list(set(elements))


# these are classes against which instance type will be checked to create client object for this instance
_client_classes = find_client_classes(__import__('ibm_ai_openscale'))


@logging_class
class ClientsManager:
    def __init__(self, bindings):
        validate_type(bindings, "bindings", Bindings, True)

        self.bindings = bindings

    def get_all(self):
        with ThreadPoolExecutor(max_workers=10) as executor:
            binding_uids = [(c['metadata']['guid']) for c in self.bindings.get_details()['service_bindings']]
            raw_clients = executor.map(self.get_client, binding_uids)
        clients = {item[0]: item[1] for item in zip(binding_uids, raw_clients)}

        return clients

    def get_client(self, binding_uid):
        validate_type(binding_uid, "binding_uid", str, True)

        details = self.bindings.get_details(binding_uid)
        service_type = details['entity']['service_type']

        if service_type == AzureConsts.SERVICE_TYPE:
            client = AzureClient(binding_uid, self.bindings._ai_client)
            return client
        elif service_type == SageMakerConsts.SERVICE_TYPE:
            client = SageMakerClient(binding_uid, self.bindings._ai_client)
            return client
        elif service_type == CustomConsts.SERVICE_TYPE:
            client = CustomClient(binding_uid, self.bindings._ai_client)
            return client
        elif service_type == SPSSConsts.SERVICE_TYPE:
            client = SPSSClient(binding_uid, self.bindings._ai_client)
            return client
        elif service_type == WMLConsts.SERVICE_TYPE and 'url' not in details['entity']['credentials']: # ICP
            service_credentials = copy.copy(self.bindings._ai_client._service_credentials)
            service_credentials['instance_id'] = 'icp'
            url = service_credentials['url']
            service_credentials['url'] = ':'.join(url.split(':')[0:-1]) if url.count(':') == 2 else url
            client = WMLClient(binding_uid, self.bindings._ai_client, service_credentials=service_credentials)
            return client

        for client_class in _client_classes:
            if details['entity']['service_type'] == client_class.service_type:
                client = client_class(binding_uid, self.bindings._ai_client, details['entity']['credentials'])
                return client

        raise ClientError('Invalid service name. Cannot create specific client: {}'.format(details['entity']['service_type']))