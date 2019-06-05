from spell.api import base_client
from spell.api.utils import url_path_join

LINKS_RESOURCE_URL = "links"


class LinksClient(base_client.BaseClient):
    def create_link(self, resource_path, alias):
        """Create a soft link to a resource.

        Keyword arguments:
        resource_path -- a single file or a directory, relative path
        alias -- name of the symlink to be created, pointing to resource_path

        Returns:
        a dictionary with the following keys: "resource_path" (path of the created link),
        "alias" (alias of the created link), "created_at" (time stamp corresponding to link creation)
        """
        payload = {"resource_path": resource_path, "alias": alias}
        endpoint = url_path_join(LINKS_RESOURCE_URL, self.owner)
        r = self.request("post", endpoint, payload=payload)
        self.check_and_raise(r)
        data = self.get_json(r)
        return data["resource_link"]

    def list_links(self):
        """Get a list of all soft links from the server.

        Returns:
        a list of dictionaries (each dictionary corresponding to a link) with the following keys:
        "resource_path" (path of the created link), "alias" (alias of the created link),
        "created_at" (time stamp corresponding to link creation).

        If no links are found, returns an empty dictionary.
        """
        endpoint = url_path_join(LINKS_RESOURCE_URL, self.owner)
        r = self.request("get", endpoint)
        self.check_and_raise(r)
        data = self.get_json(r)
        return data["resource_links"]

    def get_link(self, alias):
        """Get a specific link with alias ALIAS (or empty list if no links with alias
        ALIAS are found).

        Keyword arguments:
        alias -- name of the symlink to be retrieved

        Returns:
        a dictionary with the following keys: "resource_path" (path of the created link),
        "alias" (alias of the created link), "created_at" (time stamp corresponding to link creation).

        If no links are found, returns an empty dictionary.
        """
        endpoint = url_path_join(LINKS_RESOURCE_URL, self.owner, alias)
        r = self.request("get", endpoint)
        self.check_and_raise(r)
        data = self.get_json(r)
        return data["resource_link"]

    def remove_link(self, alias):
        """Remove a specific link with alias ALIAS.

        Keyword arguments:
        alias -- name of the symlink to be removed
        """
        endpoint = url_path_join(LINKS_RESOURCE_URL, self.owner, alias)
        r = self.request("delete", endpoint)
        self.check_and_raise(r)
