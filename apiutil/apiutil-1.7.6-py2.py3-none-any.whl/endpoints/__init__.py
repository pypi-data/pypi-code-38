# encoding: utf-8

# Best simple definition i've seen:
#   An endpoint is a URL pattern used to communicate with an API

from . import config

from ._constants import (ENVIRONMENT_CONFIG,
                         API_CONFIG,
                         HOST_CONFIG,
                         ENDPOINT_CONFIG,
                         HostKeysConstant,
                         EndpointKeysConstant,
                         APIKeysConstant,
                         EnvironmentKeysConstant)

from .hosts import (Hosts,
                    Host)

from .endpoints import (Endpoints,
                        Endpoint)

from .apis import (APIS,
                   API)

from .environments import (Environments,
                           Environment)

from .api_config import APIConfig
