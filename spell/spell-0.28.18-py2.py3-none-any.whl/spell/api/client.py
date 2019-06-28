from spell.api.runs_client import RunsClient
from spell.api.feedback_client import FeedbackClient
from spell.api.keys_client import KeysClient
from spell.api.resources_client import ResourcesClient
from spell.api.model_server_client import ModelServerClient
from spell.api.supported_options_client import SupportedOptionsClient
from spell.api.user_client import UserClient
from spell.api.user_datasets_client import UserDatasetsClient
from spell.api.workspaces_client import WorkspacesClient
from spell.api.workflows_client import WorkflowsClient
from spell.api.links_client import LinksClient
from spell.api.cluster_client import ClusterClient
from spell.api.features_client import FeaturesClient
from spell.api.jupyter_workspaces_client import JupyterWorkspacesClient


class APIClient(ClusterClient,
                FeaturesClient,
                FeedbackClient,
                KeysClient,
                LinksClient,
                ModelServerClient,
                ResourcesClient,
                RunsClient,
                SupportedOptionsClient,
                UserClient,
                UserDatasetsClient,
                WorkflowsClient,
                WorkspacesClient,
                JupyterWorkspacesClient):
    def __init__(self,  **kwargs):
        super(APIClient, self).__init__(**kwargs)
