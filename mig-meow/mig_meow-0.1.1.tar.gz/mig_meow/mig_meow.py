import os
import json
import re
import copy
import ipywidgets as widgets

PATTERNS_DIR = '.workflow_patterns_home'

OBJECT_TYPE = 'object_type'
PERSISTENCE_ID = 'persistence_id'
TRIGGER = 'trigger'
OWNER = 'owner'
NAME = 'name'
INPUT_FILE = 'input_file'
TRIGGER_PATHS = 'trigger_paths'
OUTPUT = 'output'
RECIPES = 'recipes'
VARIABLES = 'variables'
VGRIDS = 'vgrids'

ANCESTORS = 'ancestors'
DESCENDENTS = 'descendents'

OUTPUT_MAGIC_CHAR = '*'

VALID_PATTERN = {
    OBJECT_TYPE: str,
    PERSISTENCE_ID: str,
    TRIGGER: dict,
    OWNER: str,
    NAME: str,
    INPUT_FILE: str,
    TRIGGER_PATHS: list,
    OUTPUT: dict,
    RECIPES: list,
    VARIABLES: dict,
    VGRIDS: str
}


WORKFLOW_NODE = {
    ANCESTORS: {},
    DESCENDENTS: {}
}


def info():
    message = 'ver: 0.1.1' \
              'Managing Event-Oriented Workflows has been imported ' \
              'correctly. \nMEOW is a package used for defining event based ' \
              'workflows. It is designed to work with the MiG system.'
    print(message)
    # return message


def display_widget():
    import_from_vgrid_button = widgets.Button(
        value=False,
        description="Read VGrid",
        disabled=False,
        button_style='',
        tooltip='Here is a tooltip for this button',
        icon='check'
    )

    export_to_vgrid_button = widgets.Button(
        value=False,
        description="Export Workflow",
        disabled=False,
        button_style='',
        tooltip='Here is a tooltip for this button',
        icon='check'
    )

    def on_import_from_vgrid_clicked(button):
        status, patterns, message = retrieve_current_patterns()

        print(message)
        if not status:
            return

        print('Found %d patterns' % len(patterns))
        for pattern in patterns:
            print('%s (%s), inputs: %s, outputs: %s' % (
            pattern[NAME], pattern[PERSISTENCE_ID],
            pattern[TRIGGER_PATHS], pattern[OUTPUT]))

        status, workflow, message = build_workflow(patterns)

        print(message)
        if not status:
            return

        print('displaying nodes:')
        for key, value in workflow.items():
            print('node: %s, ancestors: %s, descendents: %s' % (
            key, value[ANCESTORS].keys(), value[DESCENDENTS].keys()))

    def on_export_to_vgrid_clicked(button):
        print("Goes nowhere, does nothing")

    import_from_vgrid_button.on_click(on_import_from_vgrid_clicked)
    export_to_vgrid_button.on_click(on_export_to_vgrid_clicked)

    items = [import_from_vgrid_button, export_to_vgrid_button]
    return widgets.Box(items)


def build_workflow(patterns):
    """Builds a workflow dict from a list of provided patterns"""

    if not patterns:
        return (False, None, 'A pattern list was not provided')

    if not isinstance(patterns, list):
        return (False, None, 'The provided patterns were not in a list')

    for pattern in patterns:
        valid, _ = __is_valid_pattern(pattern)
        if not valid:
            return (False, None, 'Pattern %s was incorrectly formatted' % pattern)

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


def __is_valid_workflow(to_test):
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


def __is_valid_pattern(to_test):
    """Validates that the workflow pattern object is correctly formatted"""

    if not to_test:
        return (False, 'A workflow pattern was not provided')

    if not isinstance(to_test, dict):
        return (False, 'The workflow pattern was incorrectly formatted')

    message = 'The workflow pattern had an incorrect structure'
    for k, v in to_test.items():
        if k not in VALID_PATTERN:
            return (False, message)
        # TODO alter this so is not producing error
        if not isinstance(v, VALID_PATTERN[k]):
            return (False, message)
    return (True, '')


def retrieve_current_patterns():
    all_patterns = []
    message = ''
    if os.path.isdir(PATTERNS_DIR):
        for path in os.listdir(PATTERNS_DIR):
            file_path = os.path.join(PATTERNS_DIR, path)
            if os.path.isfile(file_path):
                try:
                    with open(file_path) as file:
                        input_dict = json.load(file)
                        valid, _ = __is_valid_pattern(input_dict)
                        if valid:
                            all_patterns.append(input_dict)
                        else:
                            message += '%s did not contain a valid pattern definition.' % path
                except:
                    message += '%s is unreadable, possibly corrupt.' % path
    else:
        return (False, None, 'No patterns found to import.')
    return (True, all_patterns, message)


