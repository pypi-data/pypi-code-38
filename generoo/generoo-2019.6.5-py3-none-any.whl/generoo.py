import argparse
import yaml
import os

from pick import pick

from generoo.utils import handle_prompt, convert_to_dashes, convert_to_slashes, convert_to_periods, \
    convert_to_caps_no_spaces, convert_to_caps_with_spaces, render_template_to_directory, render_destination_path, \
    is_valid_input, equals_ignore_case, convert_to_snake, convert_to_camel, yes_no_to_bool, convert_to_lower_with_spaces

generate_options = ['generate', 'gen', 'g']
project_options = ['project', 'proj', 'pro', 'p']
excluded_archetypal_directories = ['common', '__pycache__']
archetype_default = f'{os.path.join(os.path.dirname(os.path.realpath(__file__)))}/archetypes'
project_template_filename = 'project-template-config.json'
template_filename = '-template-config.json'


def create_configuration_directory(args: argparse.Namespace, run_configuration: dict):
    """
    When new projects are created, Generoo will add a configuration file to the root directory of the project. This
    configuration file can be used to prepopulate date in subsequent generoo generation tasks. See documentation on
    github for more information.
    """
    print('Creating generoo configuration directory...')
    generoo_directory = f'{args.name}/.generoo'
    try:
        os.makedirs(generoo_directory)
    except FileExistsError:
        print('Generoo configuration directory already exists.')
    run_configuration_file = open(f'{generoo_directory}/run-configuration.yml', 'w')
    run_configuration_file.write(yaml.safe_dump(run_configuration, indent=4, sort_keys=True))
    run_configuration_file.close()
    print('Successfully created generoo configuration directory.')


def prompt_for_archetype() -> (str, str, str):
    """
    Collects information from the user on the language, framework, and framework version they want to generate sources
    from.

    :return: language, framework, version entered by the user.
    """

    language, _ = pick(get_languages(), "Please choose a language:")
    framework, _ = pick(get_framework(language), "Please choose a framework:")
    version, _ = pick(get_versions(language, framework), "Please choose a version:")
    return language, framework, version


def get_languages() -> list:
    """Traverse templates directory to pull out all of the directories that represent languages. Ignore common.py."""
    root = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'archetypes/')
    return [subdirectory for subdirectory in os.listdir(root) if os.path.isdir(os.path.join(root, subdirectory))
            and subdirectory not in excluded_archetypal_directories]


def get_framework(language: str) -> list:
    """
    Traverse templates/{language} directory to pull out all of the directories that represent archetypes.
    Ignore common.py.
    """
    root = os.path.join(os.path.dirname(os.path.realpath(__file__)), f'archetypes/{language}')
    return [subdirectory for subdirectory in os.listdir(root) if os.path.isdir(os.path.join(root, subdirectory))
            and subdirectory not in excluded_archetypal_directories]


def get_versions(language: str, framework: str) -> list:
    """
    Traverse templates/{language}/{framework} directory to pull out all of the directories that represent versions.
    Ignore common.py.
    """
    root = os.path.join(os.path.dirname(os.path.realpath(__file__)), f'archetypes/{language}/{framework}')
    return [subdirectory for subdirectory in os.listdir(root) if os.path.isdir(os.path.join(root, subdirectory))
            and subdirectory not in excluded_archetypal_directories]


def get_generoo_config(args: argparse.Namespace) -> dict:
    """
    Attempts to load the run configuration from the .generoo file in the root directory. Throws exception if failed to
    find file or failed to load.
    :param args:
    :return:
    """
    if args.run_configuration:
        configuration = open(args.run_configuration)
    else:
        configuration = open(f'{args.name}/.generoo/run-configuration.yml')
    return yaml.safe_load(configuration.read())


def full_scope_name(scope):
    if scope in project_options:
        return project_options[0]


def get_template_configuration_metadata(args: argparse.Namespace) -> (str, str):
    """
    Resolves the configuration file location and the directory in which templates are located.

    If the directory provided is the archetype directory, then additional prompts will be given to the user to determine
    the language, framework, and version they desire to use.

    If no directory is provided, then the directory where the configuration file is
    located will be used.

    :param args:
    :return:
    """
    config = args.template_config
    directory = args.template
    scope = args.scope

    if directory == archetype_default:
        language, framework, version = prompt_for_archetype()
        directory = f'{directory}/{language}/{framework}/{version}/'
        if not config:
            config = f'{directory}{full_scope_name(scope)}{template_filename}'
    elif directory is None:
        directory = os.path.dirname(config)
    return directory, config


def resolve_variables(template_configuration: dict) -> dict:
    """
    The first step of the lifecycle is to collect the variables provided in the configuration.

    This will add the name and value of each variable to the run-configuration.

    :param template_configuration:
    :return:
    """
    run_configuration = {}
    variables = template_configuration.get('variables')
    if variables:
        for variable in variables:
            if variable['name']:
                run_configuration[variable['name']] = variable['value']
            else:
                raise AttributeError
    return run_configuration


def process_follow_ups(prompt_response: str, prompt: dict, run_configuration: dict, auto_configure: bool):
    """
    Recursively handles follow up prompts.

    Checks if the follow up question has a condition. If it does have a condition, then the condition is evaluated
    against the response of the parent prompt.

    :param prompt_response:
    :param prompt:
    :param run_configuration:
    :param auto_configure:
    :return:
    """
    follow_ups = prompt.get('follow_ups')
    if follow_ups:
        for follow_up in follow_ups:
            conditions = follow_up.get('conditions')
            if conditions:
                if is_valid_input(prompt_response, conditions):
                    process_prompt(follow_up, run_configuration, auto_configure)


def resolve_prompts(run_configuration: dict, template_configuration: dict, auto_configure: bool) -> dict:
    """
    The second step of the lifecycle is to collect the user inputs via the prompts. The values will also be written to
    the run configuration.

    :param run_configuration:
    :param template_configuration:
    :param auto_configure:
    :return:
    """
    prompts = template_configuration['prompts']
    if prompts:
        for prompt in prompts:
            if prompt['name'] and prompt['text']:
                process_prompt(prompt, run_configuration, auto_configure)
            else:
                raise AttributeError
    return run_configuration


def process_prompt(prompt, run_configuration, auto_configure):
    """
    Processes a prompt for a user.

    If being generated in a directory that already has a run_configuration file and with
    the auto configure flag set to true, this function will apply the run_configuration value for the prompt as the
    default value.

    If the run configuration exists and the application is running without the no configuration flag, then the default
    value will be overridden and the user will be able to easily use that default.

    After taking in each prompt, the transformations for that prompt will be applied and the follow up prompts will be
    evaluated.

    :param prompt:
    :param run_configuration:
    :param auto_configure:
    :return:
    """
    override = prompt.get('override')
    if auto_configure and override:
        value = prompt['default']
    else:
        value = handle_prompt(prompt)
    name = prompt['name']
    run_configuration[name] = value
    resolve_transformations(name, prompt.get('transformations'), run_configuration)
    process_follow_ups(value, prompt, run_configuration, auto_configure)


def resolve_transformations(reference: str, transformations: dict, run_configuration: dict) -> dict:
    """
    Prompts accept transformations, which are meant to take the input and then convert it to a different format.

    The transformation types can be found below or in the README.

    :param reference
    :param run_configuration:
    :param transformations:
    :return:
    """
    if transformations:
        for transformation in transformations:
            name = transformation['name']
            transformation_type = transformation['transformation']
            if equals_ignore_case(transformation_type, 'SNAKE'):
                run_configuration[name] = convert_to_snake(run_configuration[reference])
            elif equals_ignore_case(transformation_type, 'DASHES'):
                run_configuration[name] = convert_to_dashes(run_configuration[reference])
            elif equals_ignore_case(transformation_type, 'SLASHES'):
                run_configuration[name] = convert_to_slashes(run_configuration[reference])
            elif equals_ignore_case(transformation_type, 'PERIODS'):
                run_configuration[name] = convert_to_periods(run_configuration[reference])
            elif equals_ignore_case(transformation_type, 'LOWER'):
                run_configuration[name] = convert_to_lower_with_spaces(run_configuration[reference])
            elif equals_ignore_case(transformation_type, 'CAMEL'):
                run_configuration[name] = convert_to_camel(run_configuration[reference])
            elif equals_ignore_case(transformation_type, 'CAPITALIZED'):
                run_configuration[name] = convert_to_caps_no_spaces(run_configuration[reference])
            elif equals_ignore_case(transformation_type, 'CAPITALIZED_WITH_SPACES'):
                run_configuration[name] = convert_to_caps_with_spaces(run_configuration[reference])
            else:
                raise AttributeError(f'Did not recognize the transformation type provided: {transformation_type}')
    return run_configuration


def fill_in_templates(args: argparse.Namespace, template_path: str, template_configurations: dict, run_configurations: dict):
    """
    Apply the run configuration to the templates in the provided template directory.

    Templates can be provided through the mapping field in the template configuration. If the mapping destination is a
    directory, then it is assumed that the directory is structured in the way the output should be structured, and all
    replacements will happen in place with the given structure.

    If no mappings are provided, then the assumption is that the provided template directory is structured in the way
    the output should be structured, and all replacements will happen in place with the given structure.

    :param args:
    :param template_path:
    :param template_configurations:
    :param run_configurations:
    :return:
    """
    mappings = template_configurations.get('mappings')
    if mappings:
        for mapping in mappings:
            template = mapping['template']
            destination = mapping['destination']
            if template and destination:
                if os.path.isdir(template):
                    if os.path.isdir(destination):
                        recursively_fill_template_in_dir(args, template, destination, run_configurations)
                    else:
                        raise AttributeError(f'{template} is a directory. {destination} must be a directory.')
                else:
                    os.makedirs(template_path, exist_ok=True)
                    render_template_to_directory(render_destination_path(destination, run_configurations), os.path.join(template_path, template), run_configurations)
    else:
        if os.path.isdir(template_path):
            recursively_fill_template_in_dir(args, template_path, os.curdir, run_configurations)
        else:
            render_template_to_directory(os.path.join(args.name, os.path.basename(template_path)), template_path, run_configurations)


def recursively_fill_template_in_dir(args: argparse.Namespace, template_dir: str, destination: str, run_configurations: dict):
    """
    Walk the non-flat template directory and render both the template content as well as the destination path.

    :param args:
    :param template_dir:
    :param destination:
    :param run_configurations:
    :return:
    """
    template_dir_len = len(template_dir)
    for root, dirs, files in os.walk(template_dir, topdown=False):
        for name in files:
            file_destination = os.path.join(args.name, destination, root[template_dir_len:], name)
            if len(file_destination) > 0:
                file_destination, passes = evaluate_filepath_conditions(file_destination, run_configurations)
                if passes:
                    print(file_destination)
                    render_template_to_directory(render_destination_path(file_destination, run_configurations), os.path.join(root, name), run_configurations)


def evaluate_filepath_conditions(file_destination: str, run_configurations: dict) -> (str, bool):
    """
    File paths passed will be checked for partial Mustache syntax for sections. If a section tag is provided ({{#section}},
    then the run configuration is checked for the tag.

    If the condition is met, then the destination path will be cleaned
    of the section tags and a true value will be returned.

    If the condition is not met, then the string as it is currently
    being processed at the time of failure is returned, and a false value is returned with it.

    :param file_destination:
    :param run_configurations:
    :return:
    """
    conditional_tag = '{{#'
    tag_close = '}}'
    conditional_tag_len = len(conditional_tag)
    tag_close_len = len(tag_close)
    conditional_tag_index = file_destination.find(conditional_tag)
    while conditional_tag_index >= 0:
        tag_close_index = file_destination.find(tag_close, conditional_tag_index)
        tag_start_index = conditional_tag_index + conditional_tag_len
        tag_key = file_destination[tag_start_index:tag_close_index]
        if tag_key not in run_configurations or not yes_no_to_bool(run_configurations[tag_key]):
            return file_destination, False
        file_destination = file_destination[:conditional_tag_index] + file_destination[tag_close_index+tag_close_len:]
        conditional_tag_index = file_destination.find(conditional_tag, tag_close_index + tag_close_len)
    return file_destination, True


def extract_run_configuration(template_configuration: dict, auto_configure: bool) -> dict:
    """
    Runs the lifecycle events for loading the template file. Returns a run configuration.

    :param template_configuration:
    :param auto_configure:
    :return:
    """
    run_configuration = resolve_variables(template_configuration)
    run_configuration = resolve_prompts(run_configuration, template_configuration, auto_configure)
    return run_configuration


def override_defaults(template_configuration, run_configuration):
    """
    Pre-processing step that will go through each prompt and replace the default value of that prompt with the value,
    if present, from the run configuration.

    :param template_configuration:
    :param run_configuration:
    :return:
    """
    prompts = template_configuration['prompts']
    if prompts:
        for prompt in prompts:
            override_default(prompt, run_configuration)
    return template_configuration


def override_default(prompt, run_configuration):
    """
    Replaces the default value of the given prompt with its value from the run configuration, if present.

    :param prompt:
    :param run_configuration:
    :return:
    """
    if prompt['name'] in run_configuration:
        prompt['default'] = run_configuration[prompt['name']]
        prompt['override'] = True
        follow_ups = prompt.get('follow_ups')
        if follow_ups:
            for follow_up in follow_ups:
                override_default(follow_up, run_configuration)


def load_template_configuration(template_file) -> dict:
    """
    Opens the template file in YAML or JSON format and loads it into a python dict.

    Will raise an error if any of the steps fail.

    :param template_file:
    :return:
    """
    raw_configuration = open(template_file)
    template_configuration = yaml.safe_load(raw_configuration.read())
    raw_configuration.close()
    return template_configuration


def generate_project(args: argparse.Namespace):
    """
    Generates a project based on the command line arguments given.
    :param args:
    :return:
    """
    template_directory, template_file = get_template_configuration_metadata(args)
    template_configuration = load_template_configuration(template_file)
    try:
        if not args.no_config:
            run_configuration = get_generoo_config(args)
            template_configuration = override_defaults(template_configuration, run_configuration)
        run_configuration = extract_run_configuration(template_configuration, args.auto_config)
    except IOError:
        run_configuration = extract_run_configuration(template_configuration, args.auto_config)
    create_configuration_directory(args, run_configuration)
    fill_in_templates(args, template_directory, template_configuration, run_configuration)


def run(args: argparse.Namespace):
    if args.goal in generate_options:
        if args.scope in project_options:
            generate_project(args)


def generoo():
    parser = argparse.ArgumentParser(description='Generate code from templates.')

    # Positional Arguments
    parser.add_argument('goal', help='A generator goal. Examples: generate, config')
    parser.add_argument('scope', help='A generator scope. Examples: project, resource')
    parser.add_argument('name', help='The name for the scope. Example: test, pet, inventory')

    # Flag Arguments
    parser.add_argument('-n', '--no-config', action='store_true',
                        help='Will run generoo without a pre-existing configuration.')
    parser.add_argument('-a', '--auto-config', action='store_true',
                        help='Will run generoo using the pre-existing configuration'
                             'and only prompt for values not present in the configuration.')

    # Keyword Arguments
    parser.add_argument('-c', '--template-config',
                        help='Points to a location on the system that contains a custom template config.')
    parser.add_argument('-t', '--template', default=archetype_default,
                        help='Points to a directory on the system that contains templates for a corresponding '
                             'template config')
    parser.add_argument('-r', '--run-configuration',
                        help='Points to a file on the system that contains a run configuration for a corresponding '
                             'template config')

    arguments = parser.parse_args()
    run(arguments)


if __name__ == "__main__":
    generoo()
