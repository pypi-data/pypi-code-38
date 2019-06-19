import re

from .input import check_input, valid_string
from .constants import WORKFLOW_NODE, OUTPUT_MAGIC_CHAR
from .pattern import Pattern
from graphviz import Digraph


def build_workflow(patterns):
    """
    Builds a workflow dict from a dict of provided patterns. Workflow is a
    dictionary of different nodes each with a set of descendents.
    """

    if not patterns:
        raise Exception('A pattern dict was not provided')

    if not isinstance(patterns, dict):
        raise Exception('The provided patterns were not in a dict')

    for pattern in patterns.values():
        if not isinstance(pattern, Pattern):
            raise Exception('Pattern %s was incorrectly formatted. Expected '
                            '%s but got %s'
                            % (pattern, Pattern, type(pattern)))

    nodes = {}
    # create all required nodes
    for pattern in patterns.values():
        nodes[pattern.name] = set()
    # populate nodes with ancestors and descendents
    for pattern in patterns.values():
        input_regex_list = pattern.trigger_paths
        for other_pattern in patterns.values():
            other_output_dict = other_pattern.outputs
            for input in input_regex_list:
                for key, value in other_output_dict.items():
                    if re.match(input, value):
                        nodes[other_pattern.name].add(pattern.name)
                    if OUTPUT_MAGIC_CHAR in value:
                        value = value.replace(OUTPUT_MAGIC_CHAR, '.*')
                        if re.match(value, input):
                            nodes[other_pattern.name].add(pattern.name)
    return nodes


def display_workflow(workflow, filename=None):
    """
    Displays a workflow using graphviz. Takes as input a dictionary or
    workflow nodes, each containing a set of descendent nodes.

    optional file_name may be provided. This is the name of the .gv and .pdf
    file created by graphviz.
    """
    if not workflow:
        raise Exception('A workflow dict was not provided')

    if not isinstance(workflow, dict):
        raise Exception('The provided workflow was not a dict')

    for descendents in workflow.values():
        if not isinstance(descendents, set):
            raise Exception('A provided patterns were not formatted correctly.'
                            ' Is expected to contain %s, but instead is %s'
                            % (type(set()), type(descendents)))
        for descendent in descendents:
            print('inspecting descendet %s' % descendent)
            if descendent not in workflow.keys():
                raise Exception('Phantom descendent %s has no connecting '
                                'node' % descendent)

    if filename:
        check_input(filename, str)
        valid_string(filename)
    else:
        filename = 'workflow'

    dot = Digraph(comment='Workflow')

    for pattern, descendents in workflow.items():
        dot.node(pattern, pattern)
        for descendent in descendents:
            dot.edge(pattern, descendent)

    dot.render(filename, view=True)


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





