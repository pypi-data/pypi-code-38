import os
import random
import tempfile
import typing

from common_primitives import base as cp_base
from d3m import container
from d3m.metadata import base as meta_base
from d3m.metadata import hyperparams as meta_hyperparams
from d3m.metadata import params as meta_params
from d3m.primitive_interfaces import base as pi_base

from sri.common import config

# A list of test folds.
Inputs = container.List  # container.List[int]
Outputs = container.List  # container.List[container.Dataset]

class GraphNodeSplitterHyperparams(meta_hyperparams.Hyperparams):
    number_of_folds = meta_hyperparams.Bounded(
            description = 'The number of folds in k-fold cross-validation.',
            default = 5,
            lower = 2,
            upper = None,
            semantic_types = ['https://metadata.datadrivendiscovery.org/types/ControlParameter']
    )
    delete_recursive = meta_hyperparams.Hyperparameter[bool](
            default = True,
            semantic_types = ['https://metadata.datadrivendiscovery.org/types/ControlParameter'],
            description = 'Ignored for graph sampling.',
    )
    # TODO(eriq): We may be able to implement this, but it will be tough because nodes are not always classed.
    stratified = meta_hyperparams.Hyperparameter[bool](
            default = False,
            semantic_types = ['https://metadata.datadrivendiscovery.org/types/ControlParameter'],
            description = 'Ignored for graph sampling.',
    )
    # Currently unused for graphs.
    shuffle = meta_hyperparams.UniformBool(
            default = False,
            semantic_types = ['https://metadata.datadrivendiscovery.org/types/ControlParameter'],
            description = "Whether to shuffle the data before splitting into batches.",
    )
    # Caused the pipeline validator to barf.  Does not seem to be used anywhere.
    # file_output_path = meta_hyperparams.Hyperparameter[str](
    #         default = os.path.join(tempfile.gettempdir(), 'graph_node_splitter'),
    #         semantic_types = ['https://metadata.datadrivendiscovery.org/types/ControlParameter'],
    #         description = 'A place on disk were we can store the split graphs.',
    # )

class GraphNodeSplitterParams(meta_params.Params):
    base_dataset: container.Dataset
    folds: typing.Dict

class GraphNodeSplitter(cp_base.DatasetSplitPrimitiveBase[GraphNodeSplitterParams, GraphNodeSplitterHyperparams]):
    """
    Take in a graph-based dataset and produce multiple train/test splits over the graph.
    This is achieved by sampling nodes in the graph.
    The output will be a DataFrame with two columns: "train" and "test", each containing a full container.Dataset.
    Each row will be one of these train/test splits.,
    """

    def __init__(self, *, hyperparams: GraphNodeSplitterHyperparams, random_seed: int = 0) -> None:
        super().__init__(hyperparams = hyperparams, random_seed = random_seed)

        self._base_dataset = None
        # {graphDatasetIndex: [[nodeId, ...], ...], ...}
        self._folds = None

    def set_training_data(self, *, dataset: container.Dataset) -> None:
        self._base_dataset = dataset

    def fit(self, *, timeout: float = None, iterations: int = None) -> pi_base.CallResult[None]:
        """
        Compute the folds.
        """

        self._folds = {}
        random.seed(self.random_seed)

        for data_element in self._base_dataset:
            # We only care about graphs.
            if ('https://metadata.datadrivendiscovery.org/types/Graph' not in self._base_dataset.metadata.query((data_element,))['semantic_types']):
                continue

            folds = self._get_folds(self._base_dataset[data_element])
            self._folds[data_element] = folds

        return pi_base.CallResult(None)

    def fit_multi_produce(self, *, produce_methods: typing.Sequence[str], dataset: container.Dataset, inputs: cp_base.DatasetSplitInputs, timeout: float = None, iterations: int = None) -> pi_base.MultiCallResult:
        raise NotImplementedError("Multiple produce not support for graph splitting.")

    def _get_folds(self, graph):
        folds = []

        nodes = list(graph.nodes())
        random.shuffle(nodes)

        size = int(len(nodes) / self.hyperparams['number_of_folds']) + 1
        for i in range(self.hyperparams['number_of_folds']):
            folds.append(nodes[i * size : (i + 1) * size])

        return folds

    def produce(self, *, inputs: cp_base.DatasetSplitInputs, timeout: float = None, iterations: int = None) -> pi_base.CallResult[cp_base.DatasetSplitOutputs]:
        """
        Produce the training splits from the provided test fold specifications.

        Returns
        -------
        List[Dataset]
            A list of dataset where each dataset is a train dataset obtained from all the folds minus the given test fold.
            For example, if we have number_of_folds = 5 and [1, 3] is specified, then [Dataset(2, 3, 4, 5) and Dataset(1, 2, 4, 5)]
            will be produced.
        """

        include_folds = []
        for test_fold in inputs:
            fold_config = list(range(self.hyperparams['number_of_folds']))
            fold_config.remove(test_fold)
            include_folds.append(fold_config)

        datasets = self._produce(include_folds)
        return pi_base.CallResult(container.List(datasets, generate_metadata=True))

    def produce_score_data(self, *, inputs: cp_base.DatasetSplitInputs, timeout: float = None, iterations: int = None) -> pi_base.CallResult[cp_base.DatasetSplitOutputs]:
        """
        Produce the test splits from the provided test fold specifications.

        Returns
        -------
        List[Dataset]
            A list of dataset where each dataset is a test dataset obtained from the given test fold.
            For example, if we have number_of_folds = 5 and [1, 3] is specified, then [Dataset(1) and Dataset(3)]
            will be produced.
        """

        include_folds = [[test_fold] for test_fold in inputs]

        datasets = self._produce(include_folds)
        return pi_base.CallResult(container.List(datasets, generate_metadata=True))

    # include_folds: [[foldToInclude, ...], ...]
    def _produce(self, include_folds):
        datasets = []

        # We will need to update the node count for each graph.
        base_metadata = self._base_dataset.metadata

        for fold_config in include_folds:
            resources = {}
            metadata = base_metadata

            for data_element in self._base_dataset:
                # TODO(eriq): Do we need to worry about supplimentary tables?
                if (data_element not in self._folds):
                    resources[data_element] = self._base_dataset[data_element]
                    continue

                folds = self._folds[data_element]

                nodes = []
                for fold_index in range(self.hyperparams['number_of_folds']):
                    if (fold_index not in fold_config):
                        continue
                    nodes += folds[fold_index]

                graph = self._base_dataset[data_element].subgraph(nodes)

                resources[data_element] = graph
                metadata = metadata.update((data_element,), {'dimension': {'length': graph.number_of_nodes()}})

            metadata.check(resources)
            dataset = container.Dataset(resources, metadata, generate_metadata=True)
            datasets.append(dataset)

        return datasets

    def get_params(self) -> GraphNodeSplitterParams:
        return GraphNodeSplitterParams({
            'base_dataset': self._base_dataset,
            'folds': self._folds,
        })

    def set_params(self, *, params: GraphNodeSplitterParams) -> None:
        self._base_dataset = params['base_dataset']
        self._folds = params['folds']

    metadata = meta_base.PrimitiveMetadata({
        # Required
        'id': '0a934c8d-610f-44ab-9c44-6ced17194d4c',
        'version': config.VERSION,
        'name': 'Graph Node Splitter',
        'description': 'Take in a graph-based dataset and produce multiple train/test splits over the graph. This is achieved by sampling nodes in the graph.',
        'python_path': 'd3m.primitives.data_transformation.graph_node_splitter.GraphNodeSplitter',
        'primitive_family': meta_base.PrimitiveFamily.DATA_TRANSFORMATION,
        'algorithm_types': [
            meta_base.PrimitiveAlgorithmType.DATA_CONVERSION,
        ],
        'source': config.SOURCE,

        # Optional
        'keywords': [ 'dataset', 'graph', 'sampling', 'evaluation', 'splits' ],
        'installation': [ config.INSTALLATION ],
        'location_uris': [],
        'hyperparms_to_tune': []
    })
