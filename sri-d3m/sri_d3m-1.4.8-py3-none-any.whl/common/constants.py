import os

DEBUG_OPTION_LOGGING_LEVEL = 'logging_level'
DEBUG_OPTION_RUN_FAST = 'run_fast'

D3M_INDEX = 'd3mIndex'
CONFIDENCE_COLUMN = 'confidence'
D3M_TABLE_KEY = 'learningData'

SEMANTIC_TYPE_PK = 'https://metadata.datadrivendiscovery.org/types/PrimaryKey'
SEMANTIC_TYPE_TARGET = 'https://metadata.datadrivendiscovery.org/types/PredictedTarget'
SEMANTIC_TYPE_CONFIDENCE = 'https://metadata.datadrivendiscovery.org/types/Confidence'

# PSL-related constants.

PSL_CLI_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'psl', 'cli'))
PSL_CLI_JAR = os.path.abspath(os.path.join(PSL_CLI_DIR, 'psl-cli-2.1.0-SNAPSHOT-965bfc32.jar'))
RUN_OUT_DIRNAME = 'psl-out'

DATA_DIR_SUB = '{data_dir}'

DEFAULT_MEMORY_PERCENT = 0.75

LINK_PREDICATE = 'LINK'

GRAPH1_PREDICATE_FILENAME = 'graph1_obs.txt'
GRAPH2_PREDICATE_FILENAME = 'graph2_obs.txt'
EDGE1_PREDICATE_FILENAME = 'edge1_obs.txt'
EDGE2_PREDICATE_FILENAME = 'edge2_obs.txt'
LINK_PRIOR_PREDICATE_FILENAME = 'link_prior_obs.txt'
LINK_PREDICATE_OBS_FILENAME = 'link_obs.txt'
LINK_PREDICATE_TARGET_FILENAME = 'link_target.txt'
BLOCK_PREDICATE_FILENAME = 'block_obs.txt'

NODE_ID_LABEL = 'nodeID'

NODE_MODIFIER_SOURCE = -1
NODE_MODIFIER_TARGET = +1

# Keys for properties on nodes and edges.
SOURCE_GRAPH_KEY = 'sourceGraph'
WEIGHT_KEY = 'weight'
EDGE_TYPE_KEY = 'edgeType'
OBSERVED_KEY = 'observed'
INFERRED_KEY = 'inferred'
TARGET_KEY = 'inferenceTarget'

# We call edges between nodes in the same graph "edges".
EDGE_TYPE_EDGE = 'edge'
# We call edges between nodes in different graphs "links".
EDGE_TYPE_LINK = 'link'

COMPUTED_SOURCE_COSINE = 'computed_cosine'
COMPUTED_SOURCE_LOCAL_SIM = 'computed_localsim'
COMPUTED_SOURCE_MEAN = 'computed_mean'

# Graph hints that upstream graph constructors can pass to the graph transformer.

# Compute the local (feature-based) similarity between graphs for link priors.
GRAPH_HINT_LINK_LOCAL_SIM = 'linkPriorLocalSim'
# Compute link priors using the mean of all other links the source/dest nodes participate in.
GRAPH_HINT_LINK_MEAN = 'linkPriorMean'
# Compute edges (weights for non-existant edges) using the cosine similairty based off of the links the nodes participate in.
GRAPH_HINT_EDGE_COSINE = 'edgeCosine'

GRAPH_MATCHING_DATASET_TABLE_INDEX = D3M_TABLE_KEY
