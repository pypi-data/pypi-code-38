"""
The CLI for the EHub Model.

The options for running the model are set in the `config.yaml` file or as
command-line arguments. See the `config.yaml` file for more information about
the `yaml` format.

Given the config.yaml file, solving the model is easy:

    $ python run.py

The program will then print out the output of whatever solver is configured in
the config.yaml file and then the solved variables, parameters, constraints,
etc..

If you want to learn how to use `run.py` as a command-line tool, run

    $ python run.py -h

to learn more about the arguments.

Note: You can use both the `config.yaml` and the command-line arguments
together in certain situations.
"""
import argparse
import os
import pickle
import yaml

from pyehub.energy_hub.ehub_model import EHubModel
from pyehub.logger import create_logger
from pyehub.outputter import pretty_print, output_excel, print_capacities, print_section, print_warning, stream_info
from pyehub.energy_hub.utils import constraint



DEFAULT_CONFIG_FILE = 'config.yaml'
DEFAULT_LOG_FILE = 'logs.log'

class CarbonEHubModel(EHubModel):
    """Modified EHubModel to minimize cost with a max carbon cap."""
    MAX_CARBON = 0

    def __init__(self, *, excel=None, request=None, max_carbon=0, big_m=99999):
        super().__init__(excel=excel, request=request, big_m=big_m)
        if max_carbon is not None:
            self.MAX_CARBON = max_carbon

    @constraint()
    def max_carbon_level(self):
        """Constraint to set a max carbon cap."""
        return self.total_carbon <= float(self.MAX_CARBON)


def main():
    """The main function for the CLI."""
    create_logger(DEFAULT_LOG_FILE)

    arguments = get_command_line_arguments()
    settings = parse_arguments(arguments)

    if settings['carbon']:
        model = CarbonEHubModel(excel=settings['input_file'], max_carbon=settings['max_carbon'], big_m=settings['big_m'])
    else:
        model = EHubModel(excel=settings['input_file'], big_m=settings['big_m'])

    # Printing out model prior to solving in the same format as after solving
    if settings['verbose']:
        print_section('Before_Solving', model._public_attributes())

    results = model.solve(settings['solver'], is_verbose=settings['verbose'])

    if not settings['quiet']:
        pretty_print(results)

    output_excel(results['solution'], settings['output_file'],
                 time_steps=len(model.time), sheets=['other', 'capacity_storage', 'capacity_tech'])

    # Outputs all the capacities form the results
    if settings['verbose']:
        print_capacities(results)

    # Prints error at the end if the model burns energy(energy from storage and energy to storage at the same time step)
    print_warning(results)

    # Outputs additional sheets for each stream with information about storages and about the stream
    if settings['output_format']:
        stream_info(results, settings['output_file'])


def get_command_line_arguments() -> dict:
    """
    Get the arguments from the command-line and return them as a dictionary.

    Returns:
        A dictionary holding all the arguments
    """
    parser = argparse.ArgumentParser()

    group = parser.add_mutually_exclusive_group()
    group.add_argument('-q', '--quiet', help='Suppresses all output',
                       action='store_true', dest='is_quiet')
    group.add_argument('-v', '--verbose', help='Output everything',
                       action='store_true', dest='is_verbose')

    parser.add_argument('--model', help='The Excel file of the model to solve',
                        dest='input_file')
    parser.add_argument('--config',
                        help=f'The path to the config file to use. Defaults '
                             f'to `{DEFAULT_CONFIG_FILE}` in the current '
                             f'directory. This is only used if the relevant '
                             f'command-line argument is not given.',
                        default=DEFAULT_CONFIG_FILE, dest='config_file')
    parser.add_argument('--output', help='The file to output the results in',
                        dest='output_file')
    parser.add_argument('--carbon', help='Add a maximum value to the carbon', action='store_true')
    parser.add_argument('--max_carbon', default=0, type=int,
                        help='The maximum value that carbon can have if the --carbon switch is used.\nDefault is 0')

    parser.add_argument('--solver_options', help='The rest of the arguments '
                                                 'are arguments to the solver',
                        action='store_true')
    parser.add_argument('--solver', help='The solver to use',
                        choices=['glpk', 'cplex'], dest='solver')

    parser.add_argument('--output_format', help='Outputs the results in a different format, grouped info about streams',
                        action='store_true')

    known, unknown = parser.parse_known_args()
    print(known, unknown)
    if not known.solver_options and unknown:
        raise ValueError('Unknown arguments. Must specify `--solver_options` '
                         'to allow extra arguments.')

    known = known.__dict__
    known['unknown'] = {}
    for key, value in zip(unknown[::2], unknown[1::2]):
        key = key.split('--')[-1]

        if key not in known['unknown']:
            known['unknown'][key] = value
        else:
            raise ValueError

    # Combine two dictionaries into one
    return known


def parse_arguments(arguments: dict) -> dict:
    """
    Parse the command-line arguments along with the config file.

    Args:
        arguments: The dictionary containing the command-line arguments

    Returns:
        A dictionary with the command-line arguments combined with the config
        file's settings
    """
    with open(arguments['config_file'], 'r') as file:
        config_settings = yaml.safe_load(file)

    if not arguments['input_file']:
        input_file = config_settings['input_file']
    elif arguments['input_file']:
        input_file = arguments['input_file']
    else:
        raise ValueError('Must specify a model to solve')

    if arguments['output_file']:
        output_file = arguments['output_file']
    else:
        output_file = config_settings['output_file']

    if arguments['solver']:
        solver_name = arguments['solver']
    else:
        solver_name = config_settings['solver']['name']

    if arguments['solver_options']:
        solver_options = arguments['unknown']
    else:
        solver_options = config_settings['solver']['options']

    big_m = config_settings['BIG_M']

    return {
        'input_file': input_file,
        'output_file': output_file,
        'verbose': arguments['is_verbose'],
        'quiet': arguments['is_quiet'],
        'solver': {
            'name': solver_name,
            'options': solver_options,
        },
        'carbon': arguments['carbon'],
        'max_carbon': arguments['max_carbon'],
        'output_format': arguments['output_format'],
        'big_m': big_m
    }


if __name__ == "__main__":
    main()
