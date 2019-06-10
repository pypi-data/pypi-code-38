from spell.api import base_client
from spell.api.utils import url_path_join

FEATURE_RESOURCE_URL = "features"


class FeaturesClient(base_client.BaseClient):

    def get_owner_details(self):
        """Get info for an owner"""
        r = self.request("get", url_path_join(FEATURE_RESOURCE_URL, self.owner))
        self.check_and_raise(r)
        return self.get_json(r)["owner"]
