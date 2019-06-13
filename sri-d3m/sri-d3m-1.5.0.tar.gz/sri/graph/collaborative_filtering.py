import typing

from d3m import container
from d3m.metadata import base as meta_base
from d3m.metadata import hyperparams as meta_hyperparams
from d3m.primitive_interfaces import base as pi_base
from d3m.primitive_interfaces import transformer as pi_transformer

from sri.common import config
from sri.common import constants
from sri.common import util
from sri.graph.networkx import DiGraph
from sri.graph.networkx import Graph

# TODO(eriq): Pull from dataset meta.
# +1 for Panda's index.
D3MINDEX_INDEX = 1
USER_INDEX = 2
ITEM_INDEX = 3
RATING_INDEX = 4

DEBUG_FAST_SIZE = 850

Inputs = container.Dataset
Outputs = container.List

class CollaborativeFilteringParserHyperparams(meta_hyperparams.Hyperparams):
    # TODO(eriq): These can both be discoverd from data.
    min_rating = meta_hyperparams.Hyperparameter[float](
            default = -10.0,
            semantic_types = ['https://metadata.datadrivendiscovery.org/types/ControlParameter'])

    max_rating = meta_hyperparams.Hyperparameter[float](
            default = 10.0,
            semantic_types = ['https://metadata.datadrivendiscovery.org/types/ControlParameter'])

class CollaborativeFilteringParser(pi_transformer.TransformerPrimitiveBase[Inputs, Outputs, CollaborativeFilteringParserHyperparams]):
    """
    A primitive that transforms collaborative filtering problems into a series of graphs.
    """

    def __init__(self, *, _debug_options: typing.Dict = {}, hyperparams: CollaborativeFilteringParserHyperparams, random_seed: int = 0) -> None:
        super().__init__(hyperparams = hyperparams, random_seed = random_seed)

        self._logger = util.get_logger(__name__)
        self._debug_run_fast = False

        self._set_debug_options(_debug_options)

    def _set_debug_options(self, _debug_options):
        if (constants.DEBUG_OPTION_RUN_FAST in _debug_options):
            self._debug_run_fast = _debug_options[constants.DEBUG_OPTION_RUN_FAST]

        if (constants.DEBUG_OPTION_LOGGING_LEVEL in _debug_options):
            util.set_logging_level(_debug_options[constants.DEBUG_OPTION_LOGGING_LEVEL])

    def produce(self, *, inputs: Inputs, timeout: float = None, iterations: int = None) -> pi_base.CallResult[Outputs]:
        self._logger.debug("Starting produce")

        ratings = self._validate_inputs(inputs)
        result = self._process_data(ratings)

        outputs: container.List = container.List(result, generate_metadata=True)

        metaInfo = {
            'schema': meta_base.CONTAINER_SCHEMA_VERSION,
            'structural_type': type(outputs),
            'dimension': {
                'length': len(outputs)
            }
        }
        metadata = meta_base.DataMetadata(metaInfo).generate(outputs)
        metadata = metadata.update((meta_base.ALL_ELEMENTS,), {'structural_type': Graph})
        outputs.metadata = metadata

        return pi_base.CallResult(outputs)

    def _validate_inputs(self, inputs: Inputs):
        if (len(inputs) != 1):
            raise ValueError("Dataset does not have one element. Found %s." % (len(inputs)))

        ratings = inputs[constants.D3M_TABLE_KEY]

        count = 0
        for row in ratings.itertuples():
            # One extra column for the index.
            if (len(row) != 5):
                raise ValueError("Row %d does not have four columns, found: (%s)." % (count, row))

            # We can't assign back into our Panda's frame, but we can check a failed conversion.
            int(row[2])
            int(row[3])

            if (row[4] != ''):
                val = float(row[4])
                if (val < -10.0 or val > 10.0):
                    raise ValueError("Row %d is out of range, found: (%s)." % (count, val))

            count += 1

        return ratings

    def _process_data(self, ratings):
        self._logger.debug("Processing data")

        user_graph = self._build_source_graph(ratings, USER_INDEX, constants.NODE_MODIFIER_SOURCE)
        item_graph = self._build_source_graph(ratings, ITEM_INDEX, constants.NODE_MODIFIER_TARGET)
        rating_graph = self._build_target_graph(ratings)

        # Add in some hints 

        # We know that it makes sense to compute the mean link prior
        rating_graph.metadata = rating_graph.metadata.update([], {
            'schema': meta_base.CONTAINER_SCHEMA_VERSION,
            'structural_type': Graph,
            'hints': {
                constants.GRAPH_HINT_LINK_MEAN: True
            }
        })

        # We know that computing the cosine similarity for edges make sense.
        metadata = {
            'schema': meta_base.CONTAINER_SCHEMA_VERSION,
            'structural_type': Graph,
            'hints': {
                constants.GRAPH_HINT_EDGE_COSINE: True
            }
        }

        user_graph.metadata = user_graph.metadata.update([], metadata)
        item_graph.metadata = item_graph.metadata.update([], metadata)

        return [user_graph, item_graph, rating_graph]

    def _build_source_graph(self, ratings, index, node_modifier):
        graph = Graph()
        elements = set()

        for row in ratings.itertuples():
            elements.add(int(row[index]))

        for element in elements:
            label = util.computeNodeLabel(element, node_modifier)

            attributes = {
                constants.SOURCE_GRAPH_KEY: node_modifier,
                constants.NODE_ID_LABEL: element
            }
            graph.add_node(label, **attributes)

        return graph

    def _build_target_graph(self, ratings):
        graph = DiGraph()

        min_rating = self.hyperparams['min_rating']
        max_rating = self.hyperparams['max_rating']

        for row in ratings.itertuples():
            d3m_index = int(row[D3MINDEX_INDEX])
            user = int(row[USER_INDEX])
            item = int(row[ITEM_INDEX])
            rating = row[RATING_INDEX]

            if (rating == None or rating == ''):
                rating = None
            else:
                rating = float(rating)

            source_label = util.computeNodeLabel(user, constants.NODE_MODIFIER_SOURCE)
            attributes = {
                constants.SOURCE_GRAPH_KEY: constants.NODE_MODIFIER_SOURCE,
                constants.NODE_ID_LABEL: user
            }
            graph.add_node(source_label, **attributes)

            target_label = util.computeNodeLabel(item, constants.NODE_MODIFIER_TARGET)
            attributes = {
                constants.SOURCE_GRAPH_KEY: constants.NODE_MODIFIER_TARGET,
                constants.NODE_ID_LABEL: item
            }
            graph.add_node(target_label, **attributes)

            attributes = {
                constants.EDGE_TYPE_KEY: constants.EDGE_TYPE_LINK,
                constants.D3M_INDEX: d3m_index,
            }

            # If we have a rating, then this is an observed link.
            # Otherwise, this is a target.
            if (rating is not None):
                # Normalize ratings to [0, 1]
                rating = (rating - min_rating) / (max_rating - min_rating)
                attributes['weight'] = rating
                attributes[constants.OBSERVED_KEY] = True
            else:
                attributes[constants.TARGET_KEY] = True
                attributes[constants.OBSERVED_KEY] = False

            graph.add_edge(source_label, target_label, **attributes)

        return graph

    metadata = meta_base.PrimitiveMetadata({
        # Required
        'id': 'fdc99781-08d0-4cc0-b41a-2d17adcfaa1e',
        'version': config.VERSION,
        'name': 'Collaborative Filtering Parser',
        'description': 'Transform "collaborative filtering"-like problems into pure graphs.',
        'python_path': 'd3m.primitives.data_transformation.collaborative_filtering_parser.CollaborativeFilteringParser',
        'primitive_family': meta_base.PrimitiveFamily.DATA_TRANSFORMATION,
        'algorithm_types': [
            meta_base.PrimitiveAlgorithmType.DATA_CONVERSION,
        ],
        'source': config.SOURCE,

        # Optional
        'keywords': [ 'preprocessing', 'primitive', 'graph', 'dataset', 'transformer', 'collaborativeFiltering' ],
        'installation': [ config.INSTALLATION ],
        'location_uris': [],
        'preconditions': [ meta_base.PrimitiveEffect.NO_MISSING_VALUES ],
        'effects': [ meta_base.PrimitiveEffect.NO_MISSING_VALUES ],
        'hyperparms_to_tune': []
    })
