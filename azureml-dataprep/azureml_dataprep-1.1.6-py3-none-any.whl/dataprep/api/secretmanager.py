# Copyright (c) Microsoft Corporation. All rights reserved.
from .engineapi.typedefinitions import Secret, RegisterSecretMessageArguments
from .engineapi.api import get_engine_api
from typing import Dict, List
import uuid


def register_secrets(secrets: Dict[str, str]) -> List[Secret]:
    """
    Registers a set of secrets to be used during execution.

    :param secrets: Dictionary of secret id to secret value.
    """
    return [register_secret(value, sid) for sid, value in secrets.items()]


def register_secret(value: str, id: str = None) -> Secret:
    """
    Registers a secret to be used during execution.

    :param value: Value to keep secret. This won't be persisted with the package.
    :param id: (Optional) Secret id to use. This will be persisted in the package. Default value is new Guid.
    """
    id = id if id is not None else str(uuid.uuid4())
    return get_engine_api().register_secret(RegisterSecretMessageArguments(id, value))


def create_secret(id: str) -> Secret:
    """
    Creates a Secret. Secrets are used in remote data sources like :class:`azureml.dataprep.MSSQLDataSource`.
    
    .. remarks..

        In order for execution to succeed, you will need to call `register_secret()` first, providing the same `id` and secret `value` to use during execution.

    :param id: Secret id to use. This will be persisted in package. 
    """
    return Secret(id)
