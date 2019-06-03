
#: Default base URL for the Imagine API
DEFAULT_BASE_URL = 'https://imagine.doc.ai'

#: Default version of the Imagine REST API
DEFAULT_IMAGINE_API_VERSION = 'v0'


class ImagineClient:
    """
    Client to connect to the Imagine API.
    """

    def __init__(self, config):
        default_config = {
            "base_url": DEFAULT_BASE_URL,
            "api_version": DEFAULT_IMAGINE_API_VERSION,
            "api_key": None,
            "client_id": None
        }

        self.config = default_config
        self.config.update(config)

        if not self.config['api_key']:
            raise Exception('"api_key" must be specified')

        if not self.config['client_id']:
            raise Exception('"client_id" must be specified')
