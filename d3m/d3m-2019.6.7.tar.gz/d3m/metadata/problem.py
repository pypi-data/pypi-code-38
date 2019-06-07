import abc
import argparse
import copy
import json
import logging
import math
import os.path
import pprint
import sys
import traceback
import typing
from urllib import parse as url_parse

from . import base
from d3m import deprecate, exceptions, utils

# See: https://gitlab.com/datadrivendiscovery/d3m/issues/66
try:
    from pyarrow import lib as pyarrow_lib  # type: ignore
except ModuleNotFoundError:
    pyarrow_lib = None

__all__ = ('TaskType', 'TaskSubtype', 'PerformanceMetric', 'Problem')

logger = logging.getLogger(__name__)

# Comma because we unpack the list of validators returned from "load_schema_validators".
PROBLEM_SCHEMA_VALIDATOR, = utils.load_schema_validators(base.SCHEMAS, ('problem.json',))

PROBLEM_SCHEMA_VERSION = 'https://metadata.datadrivendiscovery.org/schemas/v0/problem.json'


def sigmoid(x: float) -> float:
    """
    Numerically stable scaled logistic function.

    Maps all values ``x`` to [0, 1]. Values between -1000 and 1000 are
    mapped reasonably far from 0 and 1, after which the function
    converges to bounds.

    Parameters
    ----------
    x : float
        Input.

    Returns
    -------
    float
        Output.
    """

    scale = 1 / 1000

    if x >= 0:
        ex = math.exp(scale * -x)
        return 1 / (1 + ex)
    else:
        ex = math.exp(scale * x)
        return ex / (1 + ex)


class TaskTypeBase:
    @classmethod
    def get_map(cls) -> dict:
        """
        Returns the map between JSON string and enum values.

        Returns
        -------
        dict
            The map.
        """

        return {
            'classification': cls.CLASSIFICATION,  # type: ignore
            'regression': cls.REGRESSION,  # type: ignore
            'clustering': cls.CLUSTERING,  # type: ignore
            'linkPrediction': cls.LINK_PREDICTION,  # type: ignore
            'vertexClassification': cls.VERTEX_CLASSIFICATION,  # type: ignore
            'vertexNomination': cls.VERTEX_NOMINATION,  # type: ignore
            'communityDetection': cls.COMMUNITY_DETECTION,  # type: ignore
            'graphMatching': cls.GRAPH_MATCHING,  # type: ignore
            'timeSeriesForecasting': cls.TIME_SERIES_FORECASTING,  # type: ignore
            'collaborativeFiltering': cls.COLLABORATIVE_FILTERING,  # type: ignore
            'objectDetection': cls.OBJECT_DETECTION,  # type: ignore
            'semiSupervisedClassification': cls.SEMISUPERVISED_CLASSIFICATION,  # type: ignore
            'semiSupervisedRegression': cls.SEMISUPERVISED_REGRESSION,  # type: ignore
        }

    @classmethod
    def parse(cls, name: str) -> 'TaskTypeBase':
        """
        Converts JSON string into enum value.

        Parameters
        ----------
        name : str
            JSON string.

        Returns
        -------
        TaskType
            Enum value.
        """

        return cls.get_map()[name]

    def unparse(self) -> str:
        """
        Converts enum value to JSON string.

        Returns
        -------
        str
            JSON string.
        """

        for key, value in self.get_map().items():
            if self == value:
                return key

        raise exceptions.InvalidStateError("Cannot convert {self}.".format(self=self))


TaskType = utils.create_enum_from_json_schema_enum(
    'TaskType', base.DEFINITIONS_JSON,
    'definitions.problem.properties.task_type.oneOf[*].enum[*]',
    module=__name__, base_class=TaskTypeBase,
)


class TaskSubtypeBase:
    @classmethod
    def get_map(cls) -> dict:
        """
        Returns the map between JSON string and enum values.

        Returns
        -------
        dict
            The map.
        """

        return {
            None: cls.NONE,  # type: ignore
            'binary': cls.BINARY,  # type: ignore
            'multiClass': cls.MULTICLASS,  # type: ignore
            'multiLabel': cls.MULTILABEL,  # type: ignore
            'univariate': cls.UNIVARIATE,  # type: ignore
            'multivariate': cls.MULTIVARIATE,  # type: ignore
            'overlapping': cls.OVERLAPPING,  # type: ignore
            'nonOverlapping': cls.NONOVERLAPPING,  # type: ignore
        }

    @classmethod
    def parse(cls, name: str) -> 'TaskSubtypeBase':
        """
        Converts JSON string into enum value.

        Parameters
        ----------
        name : str
            JSON string.

        Returns
        -------
        TaskSubtype
            Enum value.
        """

        return cls.get_map()[name]

    def unparse(self) -> str:
        """
        Converts enum value to JSON string.

        Returns
        -------
        str
            JSON string.
        """

        for key, value in self.get_map().items():
            if self == value:
                return key

        raise exceptions.InvalidStateError("Cannot convert {self}.".format(self=self))


TaskSubtype = utils.create_enum_from_json_schema_enum(
    'TaskSubtype', base.DEFINITIONS_JSON,
    'definitions.problem.properties.task_subtype.oneOf[*].enum[*]',
    module=__name__, base_class=TaskSubtypeBase,
)


class PerformanceMetricBase:
    @classmethod
    def get_map(cls) -> dict:
        """
        Returns the map between JSON string and enum values.

        Returns
        -------
        dict
            The map.
        """

        return {
            'accuracy': cls.ACCURACY,  # type: ignore
            'precision': cls.PRECISION,  # type: ignore
            'recall': cls.RECALL,  # type: ignore
            'f1': cls.F1,  # type: ignore
            'f1Micro': cls.F1_MICRO,  # type: ignore
            'f1Macro': cls.F1_MACRO,  # type: ignore
            'rocAuc': cls.ROC_AUC,  # type: ignore
            'rocAucMicro': cls.ROC_AUC_MICRO,  # type: ignore
            'rocAucMacro': cls.ROC_AUC_MACRO,  # type: ignore
            'meanSquaredError': cls.MEAN_SQUARED_ERROR,  # type: ignore
            'rootMeanSquaredError': cls.ROOT_MEAN_SQUARED_ERROR,  # type: ignore
            'meanAbsoluteError': cls.MEAN_ABSOLUTE_ERROR,  # type: ignore
            'rSquared': cls.R_SQUARED,  # type: ignore
            'normalizedMutualInformation': cls.NORMALIZED_MUTUAL_INFORMATION,  # type: ignore
            'jaccardSimilarityScore': cls.JACCARD_SIMILARITY_SCORE,  # type: ignore
            'precisionAtTopK': cls.PRECISION_AT_TOP_K,  # type: ignore
            'objectDetectionAP': cls.OBJECT_DETECTION_AVERAGE_PRECISION,  # type: ignore
            'hammingLoss': cls.HAMMING_LOSS,  # type: ignore
        }

    @classmethod
    def parse(cls, name: str) -> 'PerformanceMetricBase':
        """
        Converts JSON string into enum value.

        Parameters
        ----------
        name : str
            JSON string.

        Returns
        -------
        PerformanceMetric
            Enum value.
        """

        return cls.get_map()[name]

    def unparse(self) -> str:
        """
        Converts enum value to JSON string.

        Returns
        -------
        str
            JSON string.
        """

        for key, value in self.get_map().items():
            if self == value:
                return key

        raise exceptions.InvalidStateError("Cannot convert {self}.".format(self=self))

    def requires_confidence(self) -> bool:
        """
        Returns ``True`` if this metric requires confidence column.

        Returns
        -------
        bool
            ``True`` if this metric requires confidence column.
        """

        return self in {self.ROC_AUC, self.ROC_AUC_MICRO, self.ROC_AUC_MACRO, self.OBJECT_DETECTION_AVERAGE_PRECISION}  # type: ignore

    def best_value(self) -> float:
        """
        The best possible value of the metric.

        Returns
        -------
        float
            The best possible value of the metric.
        """

        return {
            self.ACCURACY: 1.0,  # type: ignore
            self.PRECISION: 1.0,  # type: ignore
            self.RECALL: 1.0,  # type: ignore
            self.F1: 1.0,  # type: ignore
            self.F1_MICRO: 1.0,  # type: ignore
            self.F1_MACRO: 1.0,  # type: ignore
            self.ROC_AUC: 1.0,  # type: ignore
            self.ROC_AUC_MICRO: 1.0,  # type: ignore
            self.ROC_AUC_MACRO: 1.0,  # type: ignore
            self.MEAN_SQUARED_ERROR: 0.0,  # type: ignore
            self.ROOT_MEAN_SQUARED_ERROR: 0.0,  # type: ignore
            self.MEAN_ABSOLUTE_ERROR: 0.0,  # type: ignore
            self.R_SQUARED: 1.0,  # type: ignore
            self.NORMALIZED_MUTUAL_INFORMATION: 1.0,  # type: ignore
            self.JACCARD_SIMILARITY_SCORE: 1.0,  # type: ignore
            self.PRECISION_AT_TOP_K: 1.0,  # type: ignore
            self.OBJECT_DETECTION_AVERAGE_PRECISION: 1.0,  # type: ignore
            self.HAMMING_LOSS: 0.0,  # type: ignore
        }[self]

    def worst_value(self) -> float:
        """
        The worst possible value of the metric.

        Returns
        -------
        float
            The worst possible value of the metric.
        """

        return {
            self.ACCURACY: 0.0,  # type: ignore
            self.PRECISION: 0.0,  # type: ignore
            self.RECALL: 0.0,  # type: ignore
            self.F1: 0.0,  # type: ignore
            self.F1_MICRO: 0.0,  # type: ignore
            self.F1_MACRO: 0.0,  # type: ignore
            self.ROC_AUC: 0.0,  # type: ignore
            self.ROC_AUC_MICRO: 0.0,  # type: ignore
            self.ROC_AUC_MACRO: 0.0,  # type: ignore
            self.MEAN_SQUARED_ERROR: float('inf'),  # type: ignore
            self.ROOT_MEAN_SQUARED_ERROR: float('inf'),  # type: ignore
            self.MEAN_ABSOLUTE_ERROR: float('inf'),  # type: ignore
            self.R_SQUARED: float('-inf'),  # type: ignore
            self.NORMALIZED_MUTUAL_INFORMATION: 0.0,  # type: ignore
            self.JACCARD_SIMILARITY_SCORE: 0.0,  # type: ignore
            self.PRECISION_AT_TOP_K: 0.0,  # type: ignore
            self.OBJECT_DETECTION_AVERAGE_PRECISION: 0.0,  # type: ignore
            self.HAMMING_LOSS: 1.0,  # type: ignore
        }[self]

    def normalize(self, value: float) -> float:
        """
        Normalize the ``value`` for this metric so that it is between 0 and 1,
        inclusive, where 1 is the best score and 0 is the worst.

        Parameters
        ----------
        value : float
            Value of this metric to normalize.

        Returns
        -------
        float
            A normalized metric.
        """

        worst_value = self.worst_value()
        best_value = self.best_value()

        return self._normalize(worst_value, best_value, value)

    @classmethod
    def _normalize(cls, worst_value: float, best_value: float, value: float) -> float:
        assert worst_value <= value <= best_value or worst_value >= value >= best_value, (worst_value, value, best_value)

        if math.isinf(best_value) and math.isinf(worst_value):
            value = sigmoid(value)
            if best_value > worst_value:  # "best_value" == inf, "worst_value" == -inf
                best_value = 1.0
                worst_value = 0.0
            else:  # "best_value" == -inf, "worst_value" == inf
                best_value = 0.0
                worst_value = 1.0
        elif math.isinf(best_value):
            value = sigmoid(value - worst_value)
            if best_value > worst_value:  # "best_value" == inf
                best_value = 1.0
                worst_value = 0.5
            else:  # "best_value" == -inf
                best_value = 0.0
                worst_value = 0.5
        elif math.isinf(worst_value):
            value = sigmoid(best_value - value)
            if best_value > worst_value:  # "worst_value" == -inf
                best_value = 0.5
                worst_value = 1.0
            else:  # "worst_value" == inf
                best_value = 0.5
                worst_value = 0.0

        return (value - worst_value) / (best_value - worst_value)

    def get_class(self) -> typing.Any:
        """
        Returns a function suitable for computing this metric.

        Some functions get extra parameters which should be provided as keyword arguments.

        Returns
        -------
        function
            A function with (y_true, y_pred, **kwargs) signature, returning float.
        """

        # Importing here to prevent import cycle.
        from d3m import metrics

        if self not in metrics.class_map:
            raise exceptions.NotSupportedError("Computing metric {metric} is not supported.".format(metric=self))

        return metrics.class_map[self]  # type: ignore


PerformanceMetric = utils.create_enum_from_json_schema_enum(
    'PerformanceMetric', base.DEFINITIONS_JSON,
    'definitions.performance_metric.oneOf[*].properties.metric.enum[*]',
    module=__name__, base_class=PerformanceMetricBase,
)


class Loader(metaclass=utils.AbstractMetaclass):
    """
    A base class for problem loaders.
    """

    @abc.abstractmethod
    def can_load(self, problem_uri: str) -> bool:
        """
        Return ``True`` if this loader can load a problem from a given URI ``problem_uri``.

        Parameters
        ----------
        problem_uri : str
            A URI to load a problem from.

        Returns
        -------
        bool
            ``True`` if this loader can load a problem from ``problem_uri``.
        """

    @abc.abstractmethod
    def load(self, problem_uri: str, *, problem_id: str = None, problem_version: str = None,
             problem_name: str = None, handle_score_split: bool = True) -> 'Problem':
        """
        Loads the problem at ``problem_uri``.

        Parameters
        ----------
        problem_uri : str
            A URI to load.
        problem_id : str
            Override problem ID determined by the loader.
        problem_version : str
            Override problem version determined by the loader.
        problem_name : str
            Override problem name determined by the loader.
        handle_score_split : bool
            Rename a scoring problem to not have the same name as testing problem
            and update dataset references.

        Returns
        -------
        Problem
            A loaded problem.
        """

    @classmethod
    def get_problem_class(cls) -> 'typing.Type[Problem]':
        return Problem


class D3MProblemLoader(Loader):
    """
    A class for loading of D3M problems.

    Loader support only loading from a local file system.
    URI should point to the ``problemDoc.json`` file in the D3M problem directory.
    """

    SUPPORTED_VERSIONS = {'3.0', '3.1', '3.1.1', '3.1.2', '3.2.0', '3.2.1', '3.3.0', '3.3.1'}

    def can_load(self, dataset_uri: str) -> bool:
        try:
            parsed_uri = url_parse.urlparse(dataset_uri, allow_fragments=False)
        except Exception:
            return False

        if parsed_uri.scheme != 'file':
            return False

        if parsed_uri.netloc not in ['', 'localhost']:
            return False

        if not parsed_uri.path.startswith('/'):
            return False

        if os.path.basename(parsed_uri.path) != 'problemDoc.json':
            return False

        return True

    def load(self, problem_uri: str, *, problem_id: str = None, problem_version: str = None,
             problem_name: str = None, handle_score_split: bool = True) -> 'Problem':
        assert self.can_load(problem_uri)

        parsed_uri = url_parse.urlparse(problem_uri, allow_fragments=False)

        problem_doc_path = parsed_uri.path

        try:
            with open(problem_doc_path, 'r', encoding='utf8') as problem_doc_file:
                problem_doc = json.load(problem_doc_file)
        except FileNotFoundError as error:
            raise exceptions.ProblemNotFoundError(
                "D3M problem '{problem_uri}' cannot be found.".format(problem_uri=problem_uri),
            ) from error

        problem_schema_version = problem_doc.get('about', {}).get('problemSchemaVersion', '3.3.0')
        if problem_schema_version not in self.SUPPORTED_VERSIONS:
            logger.warning("Loading a problem with unsupported schema version '%(version)s'. Supported versions: %(supported_versions)s", {
                'version': problem_schema_version,
                'supported_versions': self.SUPPORTED_VERSIONS,
            })

        # To be compatible with problem descriptions which do not adhere to the schema and have only one entry for data.
        if not isinstance(problem_doc['inputs']['data'], list):
            problem_doc['inputs']['data'] = [problem_doc['inputs']['data']]

        performance_metrics = []
        for performance_metric in problem_doc['inputs']['performanceMetrics']:
            params = {}

            if 'posLabel' in performance_metric:
                params['pos_label'] = performance_metric['posLabel']

            if 'K' in performance_metric:
                params['k'] = performance_metric['K']

            performance_metrics.append({
                'metric': PerformanceMetric.parse(performance_metric['metric']),
            })

            if params:
                performance_metrics[-1]['params'] = params

        inputs = []
        for data in problem_doc['inputs']['data']:
            targets = []
            for target in data['targets']:
                targets.append({
                    'target_index': target['targetIndex'],
                    'resource_id': target['resID'],
                    'column_index': target['colIndex'],
                    'column_name': target['colName'],
                })

                if 'numClusters' in target:
                    targets[-1]['clusters_number'] = target['numClusters']

            privileged_data_columns = []
            for privileged_data in data.get('privilegedData', []):
                privileged_data_columns.append({
                    'privileged_data_index': privileged_data['privilegedDataIndex'],
                    'resource_id': privileged_data['resID'],
                    'column_index': privileged_data['colIndex'],
                    'column_name': privileged_data['colName'],
                })

            problem_input = {
                'dataset_id': data['datasetID'],
            }

            if targets:
                problem_input['targets'] = targets

            if privileged_data_columns:
                problem_input['privileged_data'] = privileged_data_columns

            inputs.append(problem_input)

        document_problem_id = problem_doc['about']['problemID']
        # Handle a special case for SCORE dataset splits (those which have "targets.csv" file).
        # They are the same as TEST dataset splits, but we present them differently, so that
        # SCORE dataset splits have targets as part of data. Because of this we also update
        # corresponding problem ID.
        # See: https://gitlab.com/datadrivendiscovery/d3m/issues/176
        if handle_score_split and os.path.exists(os.path.join(os.path.dirname(problem_doc_path), '..', 'targets.csv')) and document_problem_id.endswith('_TEST'):
            document_problem_id = document_problem_id[:-5] + '_SCORE'

            # Also update dataset references.
            for data in problem_doc.get('inputs', {}).get('data', []):
                if data['datasetID'].endswith('_TEST'):
                    data['datasetID'] = data['datasetID'][:-5] + '_SCORE'

        # "dataSplits" is not exposed as a problem description. One should provide splitting
        # configuration to a splitting pipeline instead. Similarly, "outputs" are not exposed either.
        description = {
            'schema': PROBLEM_SCHEMA_VERSION,
            'id': problem_id or document_problem_id,
            'version': problem_version or problem_doc['about'].get('problemVersion', '1.0'),
            'name': problem_name or problem_doc['about']['problemName'],
            'location_uris': [
                # We reconstruct the URI to normalize it.
                utils.fix_uri(problem_doc_path),
            ],
            'problem': {
                'task_type': TaskType.parse(problem_doc['about']['taskType']),
                'task_subtype': TaskSubtype.parse(problem_doc['about'].get('taskSubType', None)),
            },
        }

        if performance_metrics:
            description['problem']['performance_metrics'] = performance_metrics  # type: ignore

        if problem_doc['about'].get('problemDescription', None):
            description['description'] = problem_doc['about']['problemDescription']  # type: ignore

        if problem_doc['about'].get('problemURI', None):
            typing.cast(typing.List[str], description['location_uris']).append(problem_doc['about']['problemURI'])

        if inputs:
            description['inputs'] = inputs  # type: ignore

        if 'dataAugmentation' in problem_doc:
            description['data_augmentation'] = problem_doc['dataAugmentation']

        problem_class = self.get_problem_class()

        description['digest'] = utils.compute_digest(utils.to_json_structure(problem_class._canonical_problem_description(description)))

        return problem_class(description)


P = typing.TypeVar('P', bound='Problem')


# TODO: It should be probably immutable.
class Problem(dict):
    """
    A class representing a problem.
    """

    def __init__(self, problem_description: typing.Dict = None) -> None:
        super().__init__(problem_description)

        PROBLEM_SCHEMA_VALIDATOR.validate(self)

    loaders: typing.List[Loader] = [
        D3MProblemLoader(),
    ]

    @classmethod
    def load(cls, problem_uri: str, *, problem_id: str = None, problem_version: str = None,
             problem_name: str = None, handle_score_split: bool = True) -> 'Problem':
        """
        Tries to load problem from ``problem_uri`` using all registered problem loaders.

        Parameters
        ----------
        problem_uri : str
            A URI to load.
        problem_id : str
            Override problem ID determined by the loader.
        problem_version : str
            Override problem version determined by the loader.
        problem_name : str
            Override problem name determined by the loader.
        handle_score_split : bool
            Rename a scoring problem to not have the same name as testing problem
            and update dataset references.

        Returns
        -------
        Problem
            A loaded problem.
        """

        for loader in cls.loaders:
            if loader.can_load(problem_uri):
                return loader.load(
                    problem_uri, problem_id=problem_id, problem_version=problem_version,
                    problem_name=problem_name, handle_score_split=handle_score_split,
                )

        raise exceptions.ProblemUriNotSupportedError(
            "No known loader could load problem from '{problem_uri}'.".format(problem_uri=problem_uri)
        )

    # TODO: Allow one to specify priority which would then insert loader at a different place and not at the end?
    @classmethod
    def register_loader(cls, loader: Loader) -> None:
        """
        Registers a new problem loader.

        Parameters
        ----------
        loader : Loader
            An instance of the loader class implementing a new loader.
        """

        cls.loaders.append(loader)

    def __repr__(self) -> str:
        return self.__str__()

    def _get_description_keys(self) -> typing.Sequence[str]:
        return 'id', 'name', 'location_uris'

    def __str__(self) -> str:
        return '{class_name}({description})'.format(
            class_name=type(self).__name__,
            description=', '.join('{key}=\'{value}\''.format(key=key, value=self[key]) for key in self._get_description_keys() if key in self),
        )

    def copy(self: P) -> P:
        return copy.deepcopy(self)

    @classmethod
    def _canonical_problem_description(cls: typing.Type[P], problem_description: typing.Dict) -> P:
        """
        Before we compute digest of the problem description, we have to convert it to a
        canonical structure.

        Currently, this is just removing any local URIs the description might have.
        """

        # Making a copy.
        problem_description = dict(problem_description)

        utils.filter_local_location_uris(problem_description)

        return cls(problem_description)

    def to_simple_structure(self, *, canonical: bool = False) -> typing.Dict:
        problem_description = self

        if canonical:
            problem_description = self._canonical_problem_description(problem_description)

        return dict(problem_description)

    def to_json_structure(self, *, canonical: bool = False) -> typing.Dict:
        problem_description = utils.to_json_structure(self.to_simple_structure(canonical=canonical))

        PROBLEM_SCHEMA_VALIDATOR.validate(problem_description)

        return problem_description


@deprecate.function(message="use Problem.load class method instead")
def parse_problem_description(problem_doc_path: str) -> Problem:
    """
    Parses problem description according to ``problem.json`` metadata schema.

    It converts constants to enumerations when suitable.

    Parameters
    ----------
    problem_doc_path : str
        File path to the problem description (``problemDoc.json``).

    Returns
    -------
    Problem
        A parsed problem.
    """

    return Problem.load(problem_uri=utils.fix_uri(problem_doc_path))


def problem_serializer(obj: Problem) -> dict:
    data: typing.Dict = {
        'problem': dict(obj),
    }

    if type(obj) is not Problem:
        data['type'] = type(obj)

    return data


def problem_deserializer(data: dict) -> Problem:
    problem = data.get('type', Problem)(data['problem'])
    return problem


if pyarrow_lib is not None:
    pyarrow_lib._default_serialization_context.register_type(
        Problem, 'd3m.problem',
        custom_serializer=problem_serializer,
        custom_deserializer=problem_deserializer,
    )


def get_problem(problem_uri: str) -> Problem:
    problem_uri = utils.fix_uri(problem_uri)

    return Problem.load(problem_uri)


def describe_handler(
    arguments: argparse.Namespace, *, problem_resolver: typing.Callable = None,
) -> None:
    if problem_resolver is None:
        problem_resolver = get_problem

    has_errored = False

    for problem_path in arguments.problems:
        if getattr(arguments, 'list', False):
            print(problem_path)

        try:
            problem = problem_resolver(problem_path)
        except Exception as error:
            if getattr(arguments, 'continue', False):
                traceback.print_exc(file=sys.stdout)
                print(f"Error parsing problem: {problem_path}")
                has_errored = True
                continue
            else:
                raise Exception(f"Error parsing problem: {problem_path}") from error

        try:
            problem_description = problem.to_json_structure(canonical=True)

            if getattr(arguments, 'print', False):
                pprint.pprint(problem_description)
            else:
                json.dump(
                    problem_description,
                    sys.stdout,
                    indent=(getattr(arguments, 'indent', 2) or None),
                    sort_keys=getattr(arguments, 'sort_keys', False),
                    allow_nan=False,
                )  # type: ignore
                sys.stdout.write('\n')
        except Exception as error:
            if getattr(arguments, 'continue', False):
                traceback.print_exc(file=sys.stdout)
                print(f"Error describing problem: {problem_path}")
                has_errored = True
                continue
            else:
                raise Exception(f"Error describing problem: {problem_path}") from error

    if has_errored:
        sys.exit(1)


def main(argv: typing.Sequence) -> None:
    raise exceptions.NotSupportedError("This CLI has been removed. Use \"python3 -m d3m problem describe\" instead.")


if __name__ == '__main__':
    main(sys.argv)
