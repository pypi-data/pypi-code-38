
import ipywidgets as widgets
from shutil import copyfile
import os
import json

from .input import check_input
from .constants import PATTERNS_DIR, RECIPES_DIR, EXPORT_DIR, ANCESTORS, \
    DESCENDENTS, NAME, PERSISTENCE_ID, TRIGGER_PATHS, OUTPUT, \
    NOTEBOOK_EXTENSION, PATTERN_EXTENSION, FILES_DIR
from .workflows import build_workflow
from .pattern import Pattern
from .recipe import is_valid_recipe_dict


def is_in_vgrid():
    """
    Throws an exception if the current notebook is not in an expected vgrid
    structure.
    """
    # TODO implement this in a more robust way
    message = 'Notebook is not currently in a recognised vgrid. Notebook ' \
              'should be in the top vgrid directory for correct functionality.'

    path = os.getcwd().split(os.sep)

    if len(path) < 2:
        raise Exception(message + ' Current working path is not long enough '
                                  'to be correct.')

    possible_vgrid_files_home = path[len(path)-2]

    if possible_vgrid_files_home != FILES_DIR:
        print(possible_vgrid_files_home)
        print(FILES_DIR)
        raise Exception(message + ' Notebook is not contained in correct '
                                  'directory')

    return True


def __check_export_location(location, source, type):
    if os.path.exists(location):
        file_name = location.replace(EXPORT_DIR +  os.path.sep, '')
        raise Exception('Another export sharing the same name %s currently is '
                        'waiting to be imported into the MiG. Either rename '
                        'the %s to create a different %s, or wait '
                        'for the existing import to complete. If the problem '
                        'persists, please check the MiG is still running '
                        'correctly' % (file_name, source, type))


def __prepare_recipe_export(notebook):
    """
    Checks that a recipe note book exists and is not already staged for
    import into the mig.

    Takes 1 argument, 'notebook' being the path to a jupyter notebook. File
    extension does not need to be included.

    Returns the filename of the notebook and the destination for the notebook
    to be copied to.
    """
    if NOTEBOOK_EXTENSION not in notebook:
        if '.' in notebook:
            extension = notebook[notebook.rfind('.'):]
            raise Exception('%s is not a supported format. Only jupyter '
                            'notebooks may be exported as recipes.'
                            % extension)
        notebook += NOTEBOOK_EXTENSION

    if not os.path.exists(notebook):
        raise Exception('Notebook was identified as %s, but this '
                        'appears to not exist' % notebook)

    if not os.path.exists(EXPORT_DIR):
        os.mkdir(EXPORT_DIR)

    recipe_name = notebook
    if os.path.sep in notebook:
        recipe_name = notebook[notebook.rfind(os.path.sep)+1:]

    destination = os.path.join(EXPORT_DIR, recipe_name)
    __check_export_location(destination, 'notebook', 'recipe')

    return recipe_name, destination


def export_recipe(notebook):
    """
    Sends a copy of the given notebook to the MiG. This will only run
    if there is not already a file awaiting import of the same name.

    Takes 1 argument, 'notebook' which is the path to a jupyter notebook.
    File extension does not need to be included.
    """
    is_in_vgrid()
    check_input(notebook, str)
    name, destination = __prepare_recipe_export(notebook)
    copyfile(notebook, destination)


def export_recipes(notebooks):
    """
    Sends a copy of the given notebooks to the MiG. This will only run
    if there is not already a file awaiting import of the same name.

    Takes 1 argument, 'notebooks' which is a list of paths to jupyter
    notebooks. File extensions do not need to be included.
    """
    is_in_vgrid()
    check_input(notebooks, list)
    valid_notebooks = []
    for notebook in notebooks:
        check_input(notebook, str)
        name, destination = __prepare_recipe_export(notebook)
        for valid_name, _ in valid_notebooks:
            if valid_name == name:
                raise Exception('Attempting to copy multiple recipes of the '
                                'same name :%s' % name)
        valid_notebooks.append((notebook, destination))

    for notebook, destination in valid_notebooks:
        copyfile(notebook, destination)


def export_pattern(pattern):
    """
    Sends a patterns to the MiG. This will only run if the MiG
    is not currently waiting to process an existing pattern definition.

    Takes 1 argument, 'pattern' which is a pattern object.
    """
    is_in_vgrid()
    check_input(pattern, Pattern)
    status, message = pattern.integrity_check()

    if not status:
        raise Exception('Pattern %s is incomplete. %s' % (pattern, message))
    if message:
        print(message)

    if not os.path.exists(EXPORT_DIR):
        os.mkdir(EXPORT_DIR)

    destination = os.path.join(EXPORT_DIR, pattern.name + PATTERN_EXTENSION)
    __check_export_location(destination, 'pattern', 'pattern')

    pattern_as_json = json.dumps(pattern.__dict__)
    with open(destination, 'w') as json_file:
        json_file.write(pattern_as_json)


def export_patterns(patterns):
    """
    Sends multiple patterns to the MiG.
    
    Takes 1 argument, 'patterns', that being a dict of patterns.
    """
    is_in_vgrid()
    check_input(patterns, dict)
    for pattern in patterns.values():
        export_pattern(pattern)


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


def list_current_recipes():
    """
    Returns a list of the names of all currently registered recipes in a vgrid
    """
    all_recipes = retrieve_current_recipes()
    return all_recipes.keys()


def list_current_patterns():
    """
    Returns a list of the names of all currently registered patterns in a vgrid
    """
    all_patterns = retrieve_current_patterns()
    return all_patterns.keys()


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
            print('%s (%s), inputs: %s, outputs: %s'
                  % (pattern[NAME], pattern[PERSISTENCE_ID],
                     pattern[TRIGGER_PATHS], pattern[OUTPUT]))

        status, workflow, message = build_workflow(patterns)

        print(message)
        if not status:
            return

        print('displaying nodes:')
        for key, value in workflow.items():
            print('node: %s, ancestors: %s, descendents: %s'
                  % (key, value[ANCESTORS].keys(), value[DESCENDENTS].keys()))

    def on_export_to_vgrid_clicked(button):
        print("Goes nowhere, does nothing")

    import_from_vgrid_button.on_click(on_import_from_vgrid_clicked)
    export_to_vgrid_button.on_click(on_export_to_vgrid_clicked)

    items = [import_from_vgrid_button, export_to_vgrid_button]
    return widgets.Box(items)
