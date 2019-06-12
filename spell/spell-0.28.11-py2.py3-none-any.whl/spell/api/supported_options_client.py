import yaml

from spell.api import base_client
from spell.api.utils import url_path_join


CONFIG_RESOURCE_URL = "supported_options"


class SupportedOptionsClient(base_client.BaseClient):

    def get_options(self, config_type, cache_path):
        """Get the CLI config options.

        Returns:
        a list of config options, default first (if applicable)
        """
        r = self.request("get", url_path_join(CONFIG_RESOURCE_URL, self.owner, config_type))
        self.check_and_raise(r)
        resp = self.get_json(r)

        opts = resp["options"]
        try:
            with open(cache_path) as cache_file:
                cache = yaml.safe_load(cache_file)
        except IOError:
            cache = {}
        with open(cache_path, 'w') as cache_file:
            cache[config_type] = {
                "values": opts['values'],
                "default": opts.get('default'),
            }
            yaml.safe_dump(cache, cache_file, default_flow_style=False)
        return opts
