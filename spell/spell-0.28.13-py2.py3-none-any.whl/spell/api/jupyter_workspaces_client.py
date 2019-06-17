from spell.api import base_client
from spell.api.utils import url_path_join


JUPYTER_WORKSPACES_RESOURCE_URL = "jupyter_workspaces"


class JupyterWorkspacesClient(base_client.BaseClient):

    def new_jupyter_workspace(self, name, description, machine_type, lab, attached_resources, environment,
                              github_url, github_ref, commit_hash, workspace_id):
        """Create a Jupyter workspace.

        Arguments:
        name -- Jupyter workspace name (str)
        description -- Jupyter workspace description (str)
        machine_type -- valid machine type  (str)
        lab -- use Jupyter lab instead of Notebook (bool)
        attached_resources -- attached resources (dict of the form: <resource> -> {"mount_point": <mount_point>})
        environment -- an environment (spell.api.models.Environment object)
        github_url -- GitHub URL (str)
        github_ref -- GitHub reference (str)
        commit_hash -- commit hash (str)
        workspace_id --  workspace_id (int)

        Returns:
        a JupyterWorkspace object
        """
        payload = {
            "name": name,
            "description": description,
            "config": {
                "gpu": machine_type,
                "is_lab": lab,
                "attached_resources": attached_resources,
                "environment": environment,
            },
            "init_spec": {
                "github_url": github_url,
                "github_ref": github_ref,
                "git_commit_hash": commit_hash,
                "workspace_id": workspace_id,
            }
        }
        r = self.request("post", url_path_join(JUPYTER_WORKSPACES_RESOURCE_URL, self.owner), payload=payload)
        self.check_and_raise(r)
        resp = self.get_json(r)
        return resp["jupyter_workspace"]
