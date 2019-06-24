from abc import ABC, abstractmethod
from typing import Dict, List, Set, Optional, Union
from datalogue.models.ontology import OntologyNode
from datalogue.models.organization import User
from uuid import UUID
import itertools

from datalogue.errors import _enum_parse_error, DtlError
from datalogue.utils import _parse_list, _parse_string_list, SerializableStringEnum


class ModelType(SerializableStringEnum):
    cbc = "cbc"
    cfc = "cfc"
    ner = "ner"

    @staticmethod
    def parse_error(s: str) -> DtlError:
        return DtlError(_enum_parse_error("model type", s))


def model_type_from_str(string: str) -> Union[DtlError, ModelType]:
    return SerializableStringEnum.from_str(ModelType)(string)


class TrainingStatusType(SerializableStringEnum):
    success = "success"
    failure = "failure"
    in_progress = "in-progress"
    requested = "requested"

    @staticmethod
    def parse_error(s: str) -> DtlError:
        return DtlError(_enum_parse_error("training status type", s))


def training_status_type_from_str(string: str) -> Union[DtlError, TrainingStatusType]:
    return SerializableStringEnum.from_str(TrainingStatusType)(string)


class OrderList(SerializableStringEnum):
    asc = "asc"
    desc = "desc"

    @staticmethod
    def parse_error(s: str) -> DtlError:
        return DtlError(_enum_parse_error("order list", s))


def order_list_from_str(string: str) -> Union[DtlError, OrderList]:
    return SerializableStringEnum.from_str(OrderList)(string)


class DataRef:
    def __init__(self, node: OntologyNode, path_list: List[List[str]]):
        self.node = node
        self.path_list = path_list


class TrainingEndReason:
    def __init__(self, reasonType: str):
        self.reason_type = reasonType

    def __eq__(self, other: 'TrainingEndReason'):
        if isinstance(self, other.__class__):
            return self.reason_type == other.reason_type
        return False
    
    def _as_payload(self) -> dict:
        """
        Dictionary representation of the object
        :return:
        """
        base = dict()
        base["_type"] = self.reason_type
        return base

    @staticmethod
    def _from_payload(json: dict) -> Union[DtlError, 'TrainingEndReason']:
            """
            Builds a TRainingEndReason object from a dictionary,

            :param json: dictionary parsed from json
            :return:
            """
            reasonType = json.get("_type")
            if not isinstance(reasonType, str):
                return DtlError("An '_type' field is missing")
            
            return TrainingEndReason(reasonType)

class ConfusionMatrix:
    def __init__(self, index: List[str], matrix: List[List[int]]):
        self.index = index
        self.matrix = matrix
    
    def __eq__(self, other: 'ConfusionMatrix'):
        if isinstance(self, other.__class__):
            return self.index == other.index and self.matrix == other.matrix
        return False
    
    def _as_payload(self) -> dict:
        """
        Dictionary representation of the object
        :return:
        """
        base = dict()
        base["index"] = self.index
        base["matrix"] = self.matrix
        return base
    
    @staticmethod
    def _from_payload(json: dict) -> Union[DtlError, 'ConfusionMatrix']:
        """
        Builds a confusion Matrix object from a dictionary,

        :param json: dictionary parsed from json
        :return:
        """
        index = json.get("index")
        if not isinstance(index, List):
            return DtlError("An 'index' field is missing")

        matrix = json.get("matrix")
        if not isinstance(matrix, List):
            return DtlError("An 'matrix' field is missing")

        return ConfusionMatrix(index, matrix)

class MetricsDetails:
    def __init__(self, timestamp: str, metrics_type: str, epoch: int, loss: float, accuracy: float, precision: Dict[str, float], recall: Dict[str, float], f1_score: Dict[str, float], tpr: Optional[float] = None, fpr: Optional[float] = None,  conf_matrix: Optional[ConfusionMatrix] = None):
        self.tpr = tpr
        self.fpr = fpr
        self.timestamp = timestamp
        self.metrics_type = metrics_type
        self.epoch = epoch
        self.loss = loss
        self.accuracy = accuracy
        self.precision = precision
        self.recall = recall
        self.f1_score = f1_score
        self.conf_matrix = conf_matrix
    
    def __eq__(self, other: 'MetricsDetails'):
        if isinstance(self, other.__class__):
            return self.tpr == other.tpr and self.fpr == other.fpr and self.timestamp == other.timestamp and self.metrics_type == other.metrics_type and self.epoch == other.epoch and self.loss == other.loss and self.accuracy == other.accuracy and self.precision == other.precision and self.recall == other.recall and self.f1_score == other.f1_score and self.conf_matrix == other.conf_matrix
        return False

    def _as_payload(self) -> dict:
        """
        Dictionary representation of the object
        :return:
        """
        base = dict()
        base["tpr"] = self.tpr
        base["fpr"] = self.fpr
        base["timestamp"] = self.timestamp
        base["metricsType"] = self.metrics_type
        base["epoch"] = self.epoch
        base["loss"] = self.loss
        base["accuracy"] = self.accuracy
        base["precision"] = self.precision._as_payload()
        base["recall"] = self.recall._as_payload()
        base["f1Score"] = self.f1_score._as_payload()

        if self.conf_matrix is not None:
            base["confusionMatrix"] = self.conf_matrix._as_payload()
        else:
            base["confusionMatrix"] = None
        return base

    @staticmethod
    def _from_payload(json: dict) -> Union[DtlError, 'MetricsDetails']:
        """
        Builds a MetricsDetails object from a dictionary,

        :param json: dictionary parsed from json
        :return:
        """

        tpr = json.get("tpr")
        if not isinstance(tpr, int):
            tpr = None
        
        fpr = json.get("fpr")
        if not isinstance(fpr, int):
            fpr = None

        timestamp = json.get("timestamp")
        if not isinstance(timestamp, str):
            return DtlError("A 'timestamp' field is missing")
        
        metrics_type = json.get("type")
        if not isinstance(metrics_type, str):
            return DtlError("A 'type' field is missing")
        
        epoch = json.get("epoch")
        if not isinstance(epoch, int):
            epoch = None
        
        loss = json.get("loss")
        if not isinstance(loss, float):
            return DtlError("A 'loss' field is missing")

        accuracy = json.get("accuracy")
        if not isinstance(accuracy, float):
            return DtlError("An 'accuracy' field is missing")
        
        precision = json.get("precision")        
        if precision is None:
            return DtlError("'Precision' field is missing")
        elif not isinstance(precision, dict):
            return DtlError("'Precision' contains wrong data type it should be dictionary")
        
        recall = json.get("recall")
        if recall is None:
            return DtlError("'Recall' field is missing")
        elif not isinstance(recall, dict):
            return DtlError("'Recall' contains wrong data type it should be dict")
        
        f1_score = json.get("f1Score")
        if f1_score is None:
            return DtlError("'F1Score' field is missing")
        elif not isinstance(f1_score, dict):
            return DtlError("'F1Score' contains wrong data type it should be dict")
        
        conf_matrix = json.get("confusionMatrix")
        if conf_matrix is not None:
            conf_matrix = ConfusionMatrix._from_payload(conf_matrix)
            if isinstance(conf_matrix, DtlError):
                return conf_matrix
            
        
        return MetricsDetails(timestamp, metrics_type, epoch, loss, accuracy, precision, recall, f1_score, tpr, fpr, conf_matrix)

class Epoch:
    def __init__(self, epoch_number: int, metrics: List[MetricsDetails]):
        self.epoch_number = epoch_number
        self.metrics = metrics

    def __eq__(self, other: 'Epoch'):
        if isinstance(self, other.__class__):
            return self.epoch_number == other.epoch_number and self.metrics == other.metrics
        return False

    def _as_payload(self) -> dict:
        """
        Dictionary representation of the object
        :return:
        """
        base = dict()
        base["epochNo"] = self.epoch_number
        base["metrics"] = list(map(lambda m: m._as_payload(), self.metrics))
        return base

    @staticmethod
    def _from_payload(json: dict) -> Union[DtlError, 'Epoch']:
        """
        Builds an Epoch object from a dictionary,

        :param json: dictionary parsed from json
        :return:
        """

        epoch_number = json.get("epochNo")
        if not isinstance(epoch_number, int):
            return DtlError("An 'epochNo' field is missing")

        metrics = json.get("metrics")
        if metrics is not None:
            metrics = _parse_list(MetricsDetails._from_payload)(metrics)
            if isinstance(metrics, DtlError):
                return metrics
        else:
            metrics = list()

        return Epoch(epoch_number, metrics)

class TrainingState:
    def __init__(self, training_id: UUID, ontology_id: UUID, startTime: str, endTime: str, status: str, userId: UUID, details: str, numberOfEpochs: int, modelType: str, epochs: List[Epoch], test_metrics: Optional[MetricsDetails] = None, endReason: Optional[TrainingEndReason] = None, requestedBy: Optional[User] = None):
        self.start_time = startTime
        self.end_time = endTime
        self.end_reason = endReason
        self.status = status
        self.requested_by = requestedBy
        self.user_id = userId
        self.details = details
        self.number_of_epochs = numberOfEpochs
        self.model_type = modelType
        self.epochs = epochs
        self.test_metrics = test_metrics
        self.ontology_id = ontology_id
        self.training_id = training_id

    def __eq__(self, other: 'TrainingState'):
        if isinstance(self, other.__class__):
            return self.training_id == other.training_id and self.ontology_id == other.ontology_id and self.start_time == other.start_time and self.end_reason == other.end_reason and self.end_time == other.end_time and self.status == other.status and self.requested_by == other.requested_by and self.user_id == other.user_id and self.details == other.details and self.number_of_epochs == other.number_of_epochs and self.model_type == other.model_type and self.epochs == other.epochs and self.test_metrics == other.test_metrics
        return False

    def _as_payload(self) -> dict:
        """
        Dictionary representation of the object
        :return:
        """
        base = dict()
        base["startTime"] = self.start_time
        base["endTime"] = self.end_time
        base["endReason"] = self.end_reason
        base["requestedBy"] = self.requested_by
        base["userId"] = self.user_id
        base["numberOfEpochs"] = self.number_of_epochs
        base["epochs"] = list(map(lambda e: e._as_payload(), self.epochs))
        base["modelType"] = self.model_type
        base["testMetrics"] = self.test_metrics
        base["ontology_id"] = self.ontology_id
        base["id"] = self.training_id
        return base

    @staticmethod
    def _from_payload(json: dict) -> Union[DtlError, 'TrainingState']:
        """
        Builds a TrainingState object from a dictionary,

        :param json: dictionary parsed from json
        :return:
        """

        end_time = json.get("endTime")
        if not isinstance(end_time, str):
            end_time = None
     
        end_reason = json.get("endReason")
        if end_reason is not None:
            end_reason = TrainingEndReason._from_payload(end_reason)
            if isinstance(end_reason, DtlError):
                return end_reason
   
        epochs = json.get("epochs")
        if epochs is not None:
            epochs = _parse_list(Epoch._from_payload)(epochs)
            if isinstance(epochs, DtlError):
                return epochs
        else:
            epochs = list()

        model_type = json.get("modelType")
        if not isinstance(model_type, str):
            return DtlError("A 'modelType' field is missing")
        
        number_of_epochs = json.get("numberOfEpochs")
        if not isinstance(number_of_epochs, int):
            return DtlError("A 'numberOfEpochs' field is missing")
        
        ontology_id = json.get("ontologyId")
        if not isinstance(ontology_id, str):
            return DtlError("A 'ontologyId' field is missing")
        
        training_id = json.get("id")
        if not isinstance(training_id, str):
            return DtlError("An 'id' field is missing")
        
        start_time = json.get("startTime")
        if not isinstance(start_time, str):
            return DtlError("A 'startTime' field is missing")

        status = json.get("status")
        if not isinstance(status, str):
            return DtlError("A 'status' field is missing")

        test_metrics = json.get("testMetrics")
        if test_metrics is not None:
            test_metrics = MetricsDetails._from_payload(test_metrics)
            if isinstance(test_metrics, DtlError):
                return test_metrics
        else:
            test_metrics = None
        
        user_id = json.get("userId")
        if not isinstance(user_id, str):
            return DtlError("A 'userId' field is missing")
        
        details = json.get("details")
        if details is not None: 
            if not isinstance(details, str):
                return DtlError("A 'details' field is missing")

        return TrainingState(UUID(training_id), UUID(ontology_id), start_time, end_time, status, UUID(user_id), details, number_of_epochs, model_type, epochs, test_metrics, end_reason, None)


class Training:
    def __init__(self, training_id: UUID, states: List[TrainingState]):
        self.training_id = training_id
        self.states = states

    def _as_payload(self) -> dict:
        """
        Dictionary representation of the object
        :return:
        """
        base = dict()
        base["training_id"] = self.training_id
        base["states"] = list(map(lambda s: s._as_payload(), self.states))
        return base
    
    @staticmethod
    def _from_payload(payload: dict) -> Union[DtlError, "Training"]:
        training_id = payload.get("trainingId")
        states = payload.get("states")

        if states is not None:
            states = _parse_list(TrainingState._from_payload)(states)
            if isinstance(states, DtlError):
                return states
        else:
            states = list()
        return Training(training_id=training_id, states=states)
