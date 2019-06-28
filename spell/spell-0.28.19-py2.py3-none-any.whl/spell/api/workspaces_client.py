from spell.api import base_client
from six.moves import urllib

from spell.api.utils import url_path_join


WORKSPACES_RESOURCE_URL = "workspaces"


class WorkspacesClient(base_client.BaseClient):

    def new_workspace(self, root_commit, name, description):
        """Create a new workspace.

        Keyword arguments:
        name -- the name of the workspace
        description -- the description of the workspace

        Returns:
        a Workspace object for the created workspace

        """
        payload = {
            "root_commit": root_commit,
            "name": name,
            "description": description,
        }
        r = self.request("put", url_path_join(WORKSPACES_RESOURCE_URL, self.owner), payload=payload)
        self.check_and_raise(r)
        return self.get_json(r)["workspace"]

    def get_workspaces(self):
        """Get a list of workspaces.

        Returns:
        a list of Workspace objects for this user

        """
        r = self.request("get", url_path_join(WORKSPACES_RESOURCE_URL, self.owner))
        self.check_and_raise(r)
        return self.get_json(r)["workspaces"]

    def get_workspaces_by_name(self, name):
        """Get a list of workspaces.

        Keyword arguments:
        name -- the name of the workspace

        Returns:
        a list of Workspace objects for this user

        """
        url = url_path_join(WORKSPACES_RESOURCE_URL, self.owner)
        r = self.request("get", url + "?" + urllib.parse.urlencode({'name': name}))
        self.check_and_raise(r)
        return self.get_json(r)["workspaces"]

    def get_workspace(self, ws_id):
        """Get a workspace.

        Keyword arguments:
        ws_id -- the id of the workspace

        Returns:
        a Workspace object
        """
        r = self.request("get", url_path_join(WORKSPACES_RESOURCE_URL, self.owner, str(ws_id)))
        self.check_and_raise(r)
        return self.get_json(r)["workspace"]

    def delete_workspace(self, ws_id):
        """Delete a workspace.

        Keyword arguments:
        ws_id -- the id of the workspace
        """
        r = self.request("delete", url_path_join(WORKSPACES_RESOURCE_URL, self.owner, str(ws_id)))
        self.check_and_raise(r)
