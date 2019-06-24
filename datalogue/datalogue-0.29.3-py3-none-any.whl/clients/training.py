from typing import Optional, Union, List
from datalogue.clients.http import _HttpClient, HttpMethod
from datalogue.models.ontology import Ontology, OntologyNode, DataRef
from datalogue.models.training import Training, ModelType, TrainingStatusType, OrderList, TrainingState, training_status_type_from_str
from datalogue.errors import DtlError
from datalogue.models.organization import User
from datalogue.utils import _parse_list
from uuid import UUID
from datalogue.clients.user import _UserClient

class _DataClient:
    """
    Client to interact with TrainingData
    """
    def __init__(self, http_client: _HttpClient):
        self.http_client = http_client

    def add(self, store_id: UUID, store_name: str, refs: List[DataRef]) -> Union[DtlError, List[UUID]]:
        """
        Attaches paths in the given `store_id` to the the nodes of the ontology.

        :param store_id: Id of the datastore that it going to be read
        :param store_name: Name of the datastore that it going to be read
        :param refs: List of data references to show which paths are going to be attached which ontology nodes
        :return: List of stream ids which are the jobs that is transferring data from datastore to Themis
        """
        stream_ids = []

        for dataRef in refs:
            for path in dataRef.path_list:

                # Creates a dataset per attachment as UI does.
                dataset_id = self.__create_dataset(store_name)
                if isinstance(dataset_id, DtlError):
                    return dataset_id
                
                stream_id = self.__transfer_data_from_datastore(store_id, dataset_id, dataRef.node.node_id, path)
                if isinstance(dataset_id, DtlError):
                    return stream_id

                self.__update_node(dataRef.node.node_id, path, dataset_id, stream_id)
                stream_ids.append(stream_id)
        return stream_ids

    def __create_dataset(self, store_name: str) -> Union[DtlError, UUID]:
        payload = {
            "title": store_name,
            "tags": [],
            "label_map": {}
        }

        res = self.http_client.make_authed_request('/themis/dataset', HttpMethod.POST, body = payload)
        dataset_id = UUID(res.get("id"))

        if dataset_id is None:
            return DtlError("There is no dataset id in response!")
        return dataset_id

    def __transfer_data_from_datastore(self, store_id: UUID, dataset_id: UUID, node_id: UUID, path: List[str]) -> UUID:
        path_param = "&".join(map(lambda s: f"path={s}", path))
        url = f"/scout/run/training-data?sourceId={store_id}&{path_param}&trainingDataId={dataset_id}&class={str(node_id)}"

        res = self.http_client.make_authed_request(url, HttpMethod.POST)

        stream_id = UUID(res["streamId"])
        return stream_id

    def __update_node(self, node_id: UUID, path: List[str], dataset_id: UUID, stream_id: UUID) -> None:
        #TODO We should remove this part when we move training data adding functionality out of Yggy
        entity_res = self.http_client.make_authed_request(f"/yggy/entity/{node_id}", HttpMethod.GET)
        training_data_list = entity_res.get("trainingDataInfo")
        if training_data_list is None:
            training_data_list = []

        training_data_list.append({
            "datasetId": str(dataset_id),
            "nodePath": path,
            "streamId": str(stream_id)
        })

        self.http_client.make_authed_request(f"/yggy/entity/{node_id}", HttpMethod.POST,
            body={"trainingDataInfo": training_data_list})
        

class _TrainingClient:
    """
    Client to interact with the Trainings
    """
    def __init__(self, http_client: _HttpClient):
        self.http_client = http_client
        self.data = _DataClient(http_client)

    def deploy(self, training_id: UUID, ontology_id: UUID) -> Union[DtlError, bool]:
        """
        Deploy :class:`Training` based on the given training_id and ontology_id
        :return: True if successful, else returns :class:`DtlError`
        """
        res = self.http_client.make_authed_request(
            f'/yggy/ontology/{str(ontology_id)}/trainings/{str(training_id)}/deploy', 
            HttpMethod.POST, {})

        if isinstance(res, DtlError):
            return res
        else:
            return True

    #TODO API is not returning a training object, we should change this when the API returns training
    def run(self, ontology_id: UUID) -> Union[DtlError, bool]:
        """
        Starts training for a given ontology_id

        :param ontology_id:
        :return: Either a :class:`DtlError` if any error occurs or :class:`True` if training is requested successfully.
        """
        res = self.http_client.make_authed_request(f"/yggy/ontology/{ontology_id}/train", HttpMethod.POST)

        if isinstance(res, DtlError):
            return res
        return True

    def get_trainings(self, ontology_id: UUID, model_type: Optional[ModelType] = None, status_type: Optional[TrainingStatusType] = None, sort: Optional[OrderList] = OrderList.desc, limit: Optional[int] = 20) -> Union[DtlError, List[TrainingState]]:
        """
        Get :class:`Trainings` based on the given ontology_id
        
        :param ontology_id:
        :return: List of trainings if successful, else returns :class:`DtlError`
        """

        params = {}

        if limit is not None:
            if not isinstance(limit, int) or limit < 0:
                return DtlError("limit should be a positive integer")
            params["limit"] = limit

        if model_type is not None:
            params["model-type"] = model_type.value
        
        if status_type is not None:
            params["status-type"] = status_type.value
        
        if sort is not None:
            params["sort"] = sort.value
        
        res = self.http_client.make_authed_request(
            f'/yggy/ontology/{str(ontology_id)}/trainings',
            HttpMethod.GET, params=params)
        
        if isinstance(res, DtlError):
            return res
        else:
            return _parse_list(TrainingState._from_payload)(res)

    def cancel(self, training_id: UUID) -> Union[DtlError, bool]:
        """
        Cancel training given a training_id

        :param training_id:
        :return: status of the training if successful, else returns :class:`DtlError`
        """

        res = self.http_client.make_authed_request(
            f'/argus/trainings/{str(training_id)}/cancel',
            HttpMethod.POST)

        if isinstance(res, DtlError):
            return res
        else:
            return True


def get_training_history(self, ontology_id: UUID, limit: Optional[int] = 20) -> Union[DtlError, List[Training]]:
        """
        Get :class:`Training` history based on the given ontology_id
        
        :param ontology_id:
        :return: List of trainings if successful, else returns :class:`DtlError`
        """

        params = {}
        if limit is not None:
            if not isinstance(limit, int) or limit < 0:
                return DtlError("limit should be a positive integer")
            params["limit"] = limit
        
        res = self.http_client.make_authed_request(
            f'/yggy/ontology/{str(ontology_id)}/trainings/history',
            HttpMethod.GET, params=params)
        
        if isinstance(res, DtlError):
            return res
        else:
           return _parse_list(Training._from_payload)(res)


