import re
import copy

from .constants import WORKFLOW_NODE, NAME, TRIGGER_PATHS, OUTPUT, ANCESTORS, \
    DESCENDENTS, OUTPUT_MAGIC_CHAR
from .pattern import Pattern

def build_workflow(patterns):
    """Builds a workflow dict from a list of provided patterns"""

    if not patterns:
        return (False, None, 'A pattern list was not provided')

    if not isinstance(patterns, list):
        return (False, None, 'The provided patterns were not in a list')

    for pattern in patterns:
        if not isinstance(patterns, Pattern):
            return (False, None, 'Pattern %s was incorrectly formatted'
                    % pattern)

    nodes = {}
    # create all required nodes
    for pattern in patterns:
        workflow_node = copy.deepcopy(WORKFLOW_NODE)
        nodes[pattern[NAME]] = workflow_node
    # populate nodes with ancestors and descendents
    for pattern in patterns:
        input_regex_list = pattern[TRIGGER_PATHS]
        for other_pattern in patterns:
            other_output_dict = other_pattern[OUTPUT]
            for input in input_regex_list:
                for key, value in other_output_dict.items():
                    if re.match(input, value):
                        nodes[pattern[NAME]][ANCESTORS][other_pattern[NAME]] = nodes[other_pattern[NAME]]
                        nodes[other_pattern[NAME]][DESCENDENTS][pattern[NAME]] = nodes[pattern[NAME]]
                    if OUTPUT_MAGIC_CHAR in value:
                        value = value.replace(OUTPUT_MAGIC_CHAR, '.*')
                        if re.match(value, input):
                            nodes[pattern[NAME]][ANCESTORS][other_pattern[NAME]] = nodes[other_pattern[NAME]]
                            nodes[other_pattern[NAME]][DESCENDENTS][pattern[NAME]] = nodes[pattern[NAME]]
    return (True, nodes, '')


def is_valid_workflow(to_test):
    """Validates that a workflow object is correctly formatted"""

    if not to_test:
        return (False, 'A workflow was not provided')

    if not isinstance(to_test, dict):
        return (False, 'The provided workflow was incorrectly formatted')

    for node in to_test.keys():
        for key, value in WORKFLOW_NODE.items():
            message = 'A workflow node %s was incorrectly formatted' % node
            if key not in node.keys():
                return (False, message)
            if not isinstance(node[key], type(value)):
                return (False, message)
    return (True, '')





