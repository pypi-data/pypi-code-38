# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""A class for managing ContainerRegistry."""

import collections

from azureml._base_sdk_common.abstract_run_config_element import _AbstractRunConfigElement
from azureml._base_sdk_common.field_info import _FieldInfo


class ContainerRegistry(_AbstractRunConfigElement):
    """A class for managing ContainerRegistry.

    :param address: DNS name or IP address of azure container registry(ACR)
    :type address: str

    :param username: The username for ACR
    :type username: str

    :param password: The password for ACR
    :type password: str
    """

    # This is used to deserialize.
    # This is also the order for serialization into a file.
    _field_to_info_dict = collections.OrderedDict([
        ("address", _FieldInfo(str, "DNS name or IP address of azure container registry(ACR)")),
        ("username", _FieldInfo(str, "The username for ACR")),
        ("password", _FieldInfo(str, "The password for ACR"))
    ])

    def __init__(self):
        """Class ContainerRegistry constructor."""
        super(ContainerRegistry, self).__init__()
        self.address = None
        self.username = None
        self.password = None
        self._initialized = True
