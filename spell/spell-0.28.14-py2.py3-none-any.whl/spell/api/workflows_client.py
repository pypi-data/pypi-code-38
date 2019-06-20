from spell.api import base_client
from spell.api.utils import url_path_join

WORKFLOW_RESOURCE_URL = "workflows"


class WorkflowsClient(base_client.BaseClient):

    def workflow(self, run_req, workspace_specs, github_specs):
        payload = {
            "run": run_req if run_req else None,
            "workspace_specs": workspace_specs,
            "github_specs": github_specs,
        }
        r = self.request("post", url_path_join(WORKFLOW_RESOURCE_URL, self.owner), payload=payload)
        self.check_and_raise(r)
        resp = self.get_json(r)
        return resp["workflow"]

    def get_workflow(self, workflow_id):
        """Get a workflow

        Keyword arguments:
        workflow_id -- the id of the workflow

        Returns:
        a Workflow object
        """
        r = self.request("get", url_path_join(WORKFLOW_RESOURCE_URL, self.owner, workflow_id))
        self.check_and_raise(r)
        return self.get_json(r)["workflow"]
