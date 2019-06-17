import logging

import pandas
from d3m import container
from d3m.metadata import base as meta_base
from d3m.base import utils as base_utils

from sri.common import constants

# Keep track of loggers so we can change their level globally.
_loggers = {}
_current_log_level = logging.INFO


# Returns keys of dataset resources that have all of the indicated types.
def _get_resources_with_types(dataset, types):
    resources = []

    for key in dataset:
        has_types = True
        for type in types:
            if (not dataset.metadata.has_semantic_type((key,), type)):
                has_types = False
                break

        if (has_types):
            resources.append(key)

    return sorted(resources)

# Get keys for top-level graph datatypes in the dataset.
def get_graph_keys(dataset):
    return _get_resources_with_types(dataset, (constants.GRAPH_TYPE,))

def get_edge_list_keys(dataset):
    return _get_resources_with_types(dataset, (constants.EDGE_LIST_TYPE,))

# Get the key of the unique training table resource
def get_learning_data_key(dataset):
    keys = _get_resources_with_types(dataset, (constants.ENTRY_POINT_TYPE, constants.TABLE_TYPE))
    if len(keys) != 1:
        raise ValueError("Found more than one dataset entry point")
    return keys[0]

# Get all columns for which a Boolean test is true
# The test is given the metadata hash for the respective column
def _get_columns(dataset, resource, test):
    selector = (resource, meta_base.ALL_ELEMENTS)
    return [e for e in dataset.metadata.get_elements(selector) if test(dataset.metadata.query(selector + (e,)))]


# Finds the indexes of columns in learning_resource with references into graph_resource
def get_node_columns(dataset, learning_resource, graph_resource):
    if dataset.metadata.has_semantic_type((graph_resource,), constants.EDGE_LIST_TYPE):
        # Edge lists have foreign references to table columns that are unique keys
        graph_selector = (graph_resource, meta_base.ALL_ELEMENTS)
        referenced_names = set()
        for element in dataset.metadata.get_elements(graph_selector):
            element_mdata = dataset.metadata.query(graph_selector + (element,))
            try:
                key_info = element_mdata['foreign_key']
                if key_info['resource_id'] == learning_resource:
                    referenced_names |= { key_info['column_name'] }
            except KeyError:
                continue

        def is_node_column(element_mdata):
            return element_mdata['name'] in referenced_names

        return _get_columns(dataset, learning_resource, is_node_column)
    else:
        # Simple graph. Find the columns with foreign keys of type NODE
        def is_node_column(element_mdata):
            try:
                key_info = element_mdata['foreign_key']
                if key_info['type'] == 'NODE' and key_info['resource_id'] == graph_resource:
                    return True
            except KeyError:
                return False
            return False

        return _get_columns(dataset, learning_resource, is_node_column)

def _get_referential_columns(dataset, resource):

    def is_reference(mdata):
        return 'foreign_key' in mdata

    return _get_columns(dataset, resource, is_reference)

# Find the index of the column representing the source node in an edgelist resource
def get_edgelist_source_column(dataset, resource):
    columns = dataset.metadata.get_columns_with_semantic_type(constants.EDGE_SOURCE_TYPE, at=(resource,))
    if len(columns) == 0:
        # Uff, maybe they forgot to add the semantic types.  Before we give up, let's try looking for foreign key
        # references.  If there are precisely two, we'll call the first source and the second target.
        columns = _get_referential_columns(dataset, resource)
        if len(columns) == 2:
            return columns[0]
        else:
            raise ValueError("Missing source/target node semantic types in data source")
    if len(columns) > 1:
        raise ValueError("Found more than one source node in an edge list")
    return columns[0]

# Find the index of the column representing the target node in an edgelist resource
def get_edgelist_target_column(dataset, resource):
    columns = dataset.metadata.get_columns_with_semantic_type(constants.EDGE_TARGET_TYPE, at=(resource,))
    if len(columns) == 0:
        # See above.
        columns = _get_referential_columns(dataset, resource)
        if len(columns) == 2:
            return columns[1]
        else:
            raise ValueError("Missing source/target node semantic types in data source")
    if len(columns) > 1:
        raise ValueError("Found more than one target node in an edge list")
    return columns[0]

# Find the weight column in an edgelist, if any.  Return None if none can be found
def get_edgelist_weight_column(dataset, resource):

    def is_weight_column(mdata):
        stypes = mdata['semantic_types']
        if constants.ATTRIBUTE_TYPE not in stypes:
            return False
        if constants.SUGGESTED_TARGET_TYPE in stypes:
            return False
        if constants.TRUE_TARGET_TYPE in stypes:
            return False
        if constants.UNIQUE_KEY_TYPE in stypes:
            return False
        if constants.EDGE_SOURCE_TYPE in stypes:
            return False
        if constants.EDGE_TARGET_TYPE in stypes:
            return False
        if 'foreign_key' in mdata:
            return False
        return True

    columns = _get_columns(dataset, resource, is_weight_column)
    if len(columns) == 0:
        return None
    if len(columns) > 1:
        raise ValueError("Found multiple candidate weight columns")
    return columns[0]

# Find index of the column marked target.  Tries for TrueTarget, but falls back to SuggestedTarget
def get_target_column(dataset, resource):
    columns = dataset.metadata.get_columns_with_semantic_type(constants.TRUE_TARGET_TYPE, at=(resource,))
    if len(columns) == 0:
        columns = dataset.metadata.get_columns_with_semantic_type(constants.SUGGESTED_TARGET_TYPE, at=(resource,))
    if len(columns) == 0:
        raise ValueError("Failed to find a target column")
    if len(columns) > 1:
        raise ValueError("Expected a single target column, but found multiple")
    return columns[0]

# Returns indexes of all columns with semantic type Attribute, excluding the target column and node references
def get_attribute_columns(dataset, resource):

    def is_attribute(mdata):
        stypes = mdata['semantic_types']
        if constants.ATTRIBUTE_TYPE not in stypes:
            return False
        if constants.SUGGESTED_TARGET_TYPE in stypes:
            return False
        if constants.TRUE_TARGET_TYPE in stypes:
            return False
        if constants.UNIQUE_KEY_TYPE in stypes:
            return False
        if 'foreign_key' in mdata:
            return False
        return True

    return _get_columns(dataset, resource, is_attribute)

def computeNodeLabel(nodeID, nodeModifier):
    if (nodeModifier != constants.NODE_MODIFIER_SOURCE and nodeModifier != constants.NODE_MODIFIER_TARGET):
        raise ValueError("Node modifier must be NODE_MODIFIER_SOURCE/NODE_MODIFIER_TARGET, found: %s" % (nodeModifier))

    # If the target node id is an alphanumeric we convert it to a base 36 integer
    if not isinstance(nodeID, int):
        nodeID = int(nodeID, 36)

    return (int(nodeID) + 1) * nodeModifier

def write_tsv(path, rows):
    with open(path, 'w') as file:
        # TODO(eriq): Batch
        for row in rows:
            file.write("\t".join(map(str, row)) + "\n")

def get_logger(name):
    if (len(_loggers) == 0):
        logging.basicConfig(
                level = _current_log_level,
                format = '%(asctime)s [%(levelname)s] %(name)s -- %(message)s')

    if (name in _loggers):
        return _loggers[name]

    logger = logging.getLogger(name)
    logger.setLevel(_current_log_level)

    _loggers[name] = logger
    return logger

def set_logging_level(level = logging.INFO):
    _current_log_level = level
    for name in _loggers:
        _loggers[name].setLevel(level)

# Prepare the frame to be output as predictions by:
#  - Re-ordering by the d3m index order.
#  - Removing extra rows.
#  - Adding missing rows.
#  - Attatching the correct semantic types.
# If |increment_missing| is True, then the missing values will all get different, incremented values
# (which will start at 0 or |missing_value| (if present)).
def prep_predictions(predictions, d3m_indexes, metadata_source = None, missing_value = None, increment_missing = False):
    # First add in the proper ordering of the rows.
    order = [[int(d3m_indexes[i]), i] for i in range(len(d3m_indexes))]
    order_frame = container.DataFrame(order, columns = [constants.D3M_INDEX, 'order'])

    data_columns = list(predictions.columns)
    data_columns.remove(constants.D3M_INDEX)

    predictions[constants.D3M_INDEX] = pandas.to_numeric(predictions[constants.D3M_INDEX], downcast = 'integer')

    # Join in the ordering and use a right join to drop extra rows.
    predictions = predictions.merge(order_frame, on = constants.D3M_INDEX, how = 'right')

    # Replace missing values.
    if (not increment_missing):
        replacements = dict([(col, missing_value) for col in data_columns])
        predictions.fillna(replacements, inplace = True)
    else:
        value = 0
        if (missing_value is not None):
            value = missing_value

        for data_col in data_columns:
            for i in range(len(predictions)):
                if (pandas.np.isnan(predictions[data_col][i])):
                    predictions.loc[i, data_col] = value
                    value += 1

    # Sort
    predictions.sort_values(by = ['order'], inplace = True)

    # Drop extra columns.
    predictions.drop(columns = ['order'], inplace = True)

    # Reorder columns,
    ordered_columns = data_columns.copy()

    if (constants.CONFIDENCE_COLUMN in ordered_columns):
        ordered_columns.remove(constants.CONFIDENCE_COLUMN)
        ordered_columns.append(constants.CONFIDENCE_COLUMN)

    ordered_columns.insert(0, constants.D3M_INDEX)

    predictions = predictions[ordered_columns]

    # Attach semantic types.
    for i in range(len(ordered_columns)):
        column = ordered_columns[i]

        semantic_type = None
        if (i == 0):
            semantic_type = constants.SEMANTIC_TYPE_PK
        elif (column == constants.CONFIDENCE_COLUMN):
            semantic_type = constants.SEMANTIC_TYPE_CONFIDENCE
        else:
            semantic_type = constants.SEMANTIC_TYPE_TARGET

        predictions.metadata = predictions.metadata.add_semantic_type((meta_base.ALL_ELEMENTS, i), semantic_type)

    return predictions

def load_dataset_set_target(url):
    dataset = container.Dataset.load(url)
    resource_id, resource = base_utils.get_tabular_resource(dataset, None)
    # Adopt the suggested target as the true target.
    # Ensure that the column marked as target does not have the attribute type.
    for index, feature in enumerate(dataset[resource_id].columns):
        selector = (resource_id, meta_base.ALL_ELEMENTS, index)
        if dataset.metadata.has_semantic_type(selector, constants.SUGGESTED_TARGET_TYPE):
            if not dataset.metadata.has_semantic_type(selector, constants.TRUE_TARGET_TYPE):
                dataset.metadata = dataset.metadata.add_semantic_type(selector, constants.TRUE_TARGET_TYPE)
        if dataset.metadata.has_semantic_type(selector, constants.TRUE_TARGET_TYPE):
            dataset.metadata = dataset.metadata.remove_semantic_type(selector, constants.ATTRIBUTE_TYPE)
    return dataset

def rename_dataframe_column(df, from_name, to_name):
    """
    Rename the column in a dataframe with metadata (which also is updated).
    Returns the dataframe.
    """
    index = df.columns.get_loc(from_name)
    df.rename(columns={from_name: to_name}, inplace=True)
    df.metadata = df.metadata.update((meta_base.ALL_ELEMENTS, index), {'name': to_name})
    return df
