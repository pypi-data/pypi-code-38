
import ipywidgets as widgets
from IPython.display import Javascript
from shutil import copyfile
import os
import json

from .input import check_input
from .constants import PATTERNS_DIR, RECIPES_DIR, EXPORT_DIR, ANCESTORS, \
    DESCENDENTS, NAME, PERSISTENCE_ID, TRIGGER_PATHS, OUTPUT, PLACEHOLDER
from .workflows import build_workflow
from .pattern import Pattern
from .recipe import is_valid_recipe_dict


def is_in_vgrid():
    """
    Throws an exception if the current notebook is not in an expected vgrid
    """
    # TODO implement this
    in_vgrid = True

    if not in_vgrid:
        raise Exception('Notebook is not currently in a recognised vgrid. '
                        'Notebook should be in the top vgrid directory for '
                        'correct functionality')


def export_current_notebook():
    """
    Sends a copy of the current saved notebook to the MiG. This will only run
    if there is not already a file awaiting import.
    """
    is_in_vgrid()

    if not os.path.exists(EXPORT_DIR):
        os.mkdir(EXPORT_DIR)

    current_notebook = PLACEHOLDER
    Javascript('IPython.notebook.kernel.execute('
               '"current_notebook = '
               '" + "\'"+IPython.notebook.notebook_name+"\'");')

    if current_notebook == PLACEHOLDER:
        raise Exception('Could not find name of current notebook. '
                        'Is the kernel running?')

    if not os.path.exists(current_notebook):
        raise Exception('Current notebook was identified as %s, but this '
                        'appears to not exist' % current_notebook)

    destination = os.path.join(EXPORT_DIR, current_notebook)
    if os.path.exists(destination):
        print('Another export sharing the same name currently is waiting to '
              'be imported into the MiG. Either rename the current notebook '
              'to create a different recipe, or wait for the existing import '
              'to complete. If the problem persists, please check the MiG is '
              'still running correctly')

    copyfile(current_notebook, destination)


def retrieve_current_recipes(debug=False):
    """
    Will looking within the expected workflow recipe directory and return a
    dict of all found recipes. If debug is set to true will also output any
    warning messages.

    Note that recipes are only listed as dicts as they are not meant to be
    manipulated within the notebooks, they are the notebooks.
    """
    is_in_vgrid()
    check_input(debug, bool)

    all_recipes = {}
    message = ''
    if os.path.isdir(RECIPES_DIR):
        print('%s is a dir' % RECIPES_DIR)
        for path in os.listdir(RECIPES_DIR):
            file_path = os.path.join(RECIPES_DIR, path)
            print('considering path %s' % file_path)
            if os.path.isfile(file_path):
                print('is a file')
                try:
                    with open(file_path) as file:
                        input_dict = json.load(file)
                        status, _ = is_valid_recipe_dict(input_dict)
                        print('is valid')
                        if status:
                            all_recipes[input_dict[NAME]] = input_dict
                except:
                    message += '%s is unreadable, possibly corrupt.' % path
    else:
        if debug:
            return ({}, 'No recipes found to import. Is the notebook in the '
                        'top vgrid directory?')
        return {}
    if debug:
        return (all_recipes, message)
    return all_recipes


def retrieve_current_patterns(debug=False):
    """
    Will look within the expected workflow pattern directory and return a
    dict of all found patterns. If debug is set to true will also output
    warning messages.
    """
    is_in_vgrid()
    check_input(debug, bool)

    all_patterns = {}
    message = ''
    if os.path.isdir(PATTERNS_DIR):
        for path in os.listdir(PATTERNS_DIR):
            file_path = os.path.join(PATTERNS_DIR, path)
            if os.path.isfile(file_path):
                try:
                    with open(file_path) as file:
                        input_dict = json.load(file)
                        pattern = Pattern(input_dict)
                        all_patterns[pattern.name] = pattern
                except:
                    message += '%s is unreadable, possibly corrupt.' % path
    else:
        if debug:
            return ({}, 'No patterns found to import. Is the notebook in the '
                        'top vgrid directory?')
        return {}
    if debug:
        return (all_patterns, message)
    return all_patterns


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
