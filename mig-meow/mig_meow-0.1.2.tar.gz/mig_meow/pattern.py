
from .constants import DEFAULT_JOB_NAME, VALID_PATTERN, NAME, INPUT_FILE, \
    TRIGGER_PATHS, OUTPUT, RECIPES, VARIABLES
from .input import check_input


class Pattern:
    def __init__(self, input):
        """Constructor for new pattern object. Used within MEOW as a more
        user friendly and controllable way of creating and manipulating
        patterns, as opposed to a raw dict

        Takes a single input. This can be either a string, which is used as
        the patterns name when defining a new pattern, or can be a dict which
        already expresses a complete pattern. The dict option is used during
        the importing of data from the mig and should only be used by expert
        users."""
        # if given only a string use this as a name, it is the basis of a
        # completely new pattern
        if isinstance(input, str):
            self.name = input
            self.input_file = None
            self.trigger_paths = []
            self.outputs = {}
            self.recipes = []
            self.variables = {}
            return
        # if given dict we are importing from a stored pattern object
        if isinstance(input, dict):
            valid, _ = is_valid_pattern_dict(input)
            self.name = input[NAME]
            self.input_file = input[INPUT_FILE]
            self.trigger_paths = input[TRIGGER_PATHS]
            self.outputs = input[OUTPUT]
            self.recipes = input[RECIPES]
            self.variables = input[VARIABLES]
            return
        raise Exception('Pattern requires either a str input as a name for a '
                        'new pattern, or a dict defining a complete pattern')

    def integrity_check(self):
        """Performs some basic checks on the data within a pattern to check
        that all required fields have been filled out as it is currently very
        possible to create incomplete patterns.

        This takes no input and only raises warnings rather than Exceptions
        so that multiple problems may easily be identified at once"""
        warning = ''
        if self.input_file is None:
            return (False, "An input file must be defined. This is the file "
                           "that is used to trigger any processing and can be "
                           "defined using the methods '.add_single_input' or "
                           "'add_multiple_input")
        if len(self.trigger_paths) == 0:
            return (False, "At least one input path must be defined. This is "
                           "the path to the file that is used to trigger any "
                           "processing and can be defined using the methods "
                           "'.add_single_input' or 'add_multiple_input")
        if len(self.outputs) == 0:
            warning += '\n No output has been set, meaning no resulting ' \
                       'data will be copied back into the vgrid. ANY OUTPUT ' \
                       'WILL BE LOST.'
        if len(self.recipes) == 0:
            return (False, "No recipes have been defined")
        return (True, warning)

    def add_single_input(self, input_file, regex_path, output_path=None):
        """
        Defines a single input for a pattern. That is, a path that when a
        single file is either created or modified and matches said path, the
        recipe will be triggered taking that file as input.

        Takes 2 mandatory inputs. 'input_file' is the variable name used to
        refer to the triggering file within the recipe. 'regex_path' is path
        within the mig against which any file creation or modification events
        are compared. The path should be given relative to the vgrid home
        directory so the path 'dir/file.txt' would match the file 'file.txt'
        within the directory 'dir' that is contained within the vgrid folder
        itself. Paths can, and should be expressed using regular expressions
        in order to match multiple files and so create a dynamic workflow.
        For example:

        initial_data/.*\\.hdf5

        This would match any hdf5 files contained within the directory initial
        data. Note that as string expression of regular expression normal use
        of escape characters and the like apply.

        'output_path' may also be defined. If done so, this will be the path
        where the input file will be copied. This is useful if some data
        processing is taking place on the input and you require that data, as
        the triggering file itself will remain unchanged. Note that this is a
        regular string path and can be hard coded such as 'dir/file.txt'
        which will always write to the same location. Alternatively the '*'
        character can be used to take the name of the triggering file.
        For example:

        'output_dir/*.hdf5'

        When triggered by a file called 'filename.txt' this would copy the
        output to output_dir/filename.hdf5
        """

        check_input(input_file, str)
        check_input(regex_path, str)
        check_input(output_path, str, or_none=True)

        if len(self.trigger_paths) == 0:
            self.input_file = input_file
            self.trigger_paths = [regex_path]
            if output_path:
                self.add_output(input_file, output_path)
            else:
                self.add_variable(input_file, input_file)
        else:
            raise Exception('Could not create single input %s, as input '
                            'already defined' % input_file)

    def add_gathering_input(self, input_file, path_list, output_path=None):
        """
        Defines a gathering input for a pattern. That is, a collection of
        paths that when each individiual path is either created or modified,
        a buffer file containing all the specificed paths is updated. Once all
        files are present in the buffer then the recipe is triggered by it
        according to the single input trigger, with the buffer as the trigger.

        Takes 2 mandatory inputs. 'input_file' is the variable name used to
        refer to the triggering file within the recipe. 'path_list' is a list
        of paths which will be combined into a single buffer file as so used
        to trigger a job. Note that these paths are hard coded as paths and
        are not evaluated as regular expressions

        'output_path' may also be defined. If done so, this will be the path
        where the input file will be copied. This is useful if some data
        processing is taking place on the input and you require that data, as
        the triggering file itself will remain unchanged. Note that this is a
        regular string path and can be hard coded such as 'dir/file.txt'
        which will always write to the same location. Alternatively the '*'
        character can be used to take the name of the triggering file.
        For example:

        'output_dir/*.hdf5'

        When triggered by a file called 'filename.txt' this would copy the
        output to output_dir/filename.hdf5
        """
        check_input(input_file, str)
        check_input(path_list, list)
        for entry in path_list:
            check_input(entry, str)
        check_input(output_path, str, or_none=True)

        if len(self.trigger_paths) == 0:
            if output_path:
                self.add_output(input_file, output_path)
            else:
                self.add_variable(input_file, input_file)
            for path in path_list:
                self.trigger_paths.append(path)
        else:
            raise Exception('Could not create gathering input %s, as input '
                            'already defined' % input_file)

    def add_output(self, output_name, output_location):
        """
        Adds output to the pattern. That is, defines some file that is copied
        as output from the job processing. If any file is created by the
        recipe at runtime is should be added as output using this method or
        else it may be lost.

        Takes two inputs, 'output_name' is the variable name used within the
        recipe to refer to the output file, whilst 'output_location' is the
        path where the file will be copied on job completion. Note that this
        is a string path and can be hard coded such as 'dir/file.txt'
        which will always write to the same location. Alternatively the '*'
        character can be used to take the name of the triggering file.
        For example:

        'output_dir/*.hdf5'

        When triggered by a file called 'filename.txt' this would copy the
        output to output_dir/filename.hdf5
        """
        check_input(output_name, str)
        check_input(output_location, str)

        if output_name not in self.outputs.keys():
            self.outputs[output_name] = output_location
            self.add_variable(output_name, output_name)
        else:
            raise Exception('Could not create output %s as already defined'
                            % output_name)

    def return_notebook(self, output_location):
        """
        Adds the notebook used to run the job as output. 'output_location' is
        the path where the file will be copied on job completion. Note that
        this is a string path and can be hard coded such as 'dir/file.txt'
        which will always write to the same location. Alternatively the '*'
        character can be used to take the name of the triggering file.
        For example:

        'output_dir/*.hdf5'

        When triggered by a file called 'filename.txt' this would copy the
        output to output_dir/filename.hdf5
        """
        check_input(output_location, str)
        self.add_output(DEFAULT_JOB_NAME, output_location)

    def add_recipe(self, recipe):
        """
        Adds a recipe to the pattern. This is the code that runs as part of a
        workflow job, and is triggered by the patterns specified trigger.
        """
        check_input(recipe, str)
        self.recipes.append(recipe)

    def add_variable(self, variable_name, variable_value):
        """
        Adds a variable to the pattern, which will be passed to the recipe
        notebook using papermill as parameters.

        Takes two arguments. 'variable_name' is the name of the variable and
        must be a string, 'variable_value' can be any valid python variable
        """
        check_input(variable_name, str)
        if variable_name not in self.variables.keys():
            self.variables[variable_name] = variable_value
        else:
            raise Exception('Could not create variable %s as it is already '
                            'defined' % variable_name)


def is_valid_pattern_dict(to_test):
    """Validates that the passed dictionary expresses a pattern object"""

    if not to_test:
        return (False, 'A workflow pattern was not provided')

    if not isinstance(to_test, dict):
        return (False, 'The workflow pattern was incorrectly formatted')

    message = 'The workflow pattern had an incorrect structure'
    for key, value in to_test.items():
        if key not in VALID_PATTERN:
            message += ' Is missing key %s' % key
            return (False, message)
        if not isinstance(value, VALID_PATTERN[key]):
            message += ' %s is expected to have type %s but actually has %s' \
                       % (value, VALID_PATTERN[key], type(value))
            return (False, message)
    return (True, '')