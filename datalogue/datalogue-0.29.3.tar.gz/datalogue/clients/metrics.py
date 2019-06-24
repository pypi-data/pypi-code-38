from typing import Optional
from uuid import UUID, uuid4
from pathlib import Path

from datalogue.models.metrics import ArgoMetrics
from datalogue.clients.http import _HttpClient, HttpMethod
from datalogue.errors import DtlError


class _MetricsClient:
    """
    Client to interact with the Metrics View of a Training

    This is meant to be used by Argo Science Mode users
    as an interface to quickly display their results to customers.
    """

    def __init__(self, http_client: _HttpClient):
        self.http_client = http_client

    def upload(self, ontology_id: UUID, name: str, argo_work_dir: Path, experiment_name: str, class_map_path: str, training_id: Optional[UUID] = None) -> Optional[bool]:
        """
        Processes and pushes via the Argus api to the defined
        ontology.

        :param ontology_id: UUID the ontology you are publishing to
        :param name: str who is pushing this data
        :param argo_work_dir: str Path to the template's work directory (i.e. nightshade/work/cbc)
        :param experiment_name: str Name of the experiment to upload
        :param class_map_path: str
        :return: Error if it fails or True otherwise
        """
        if training_id is None:
            training_id = str(uuid4())

        M = ArgoMetrics(str(argo_work_dir), experiment_name, class_map_path)
        endpoint = f'/yggy/ontology/{ontology_id}/trainings/upload-metrics'
        params = {
            "training-id": f"{training_id}",
            "user-firstname": f"{name}",
            "user-lastname": "SDK",
        }

        res = self.http_client.make_authed_request(endpoint, HttpMethod.PUT, M.payload, params)

        if isinstance(res, DtlError):
            return DtlError("Could not publish request.", res)

        return True
