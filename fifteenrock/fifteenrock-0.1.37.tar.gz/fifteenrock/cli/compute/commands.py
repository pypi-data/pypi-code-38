from typing import *
import click
from fifteenrock import core
from fifteenrock.core import compute_client
from fifteenrock.lib import util
import os


@click.command()
@click.argument('command', required=True)
@click.option('--project', required=False, help='project name')
@click.option('--function', required=False, help='function name')
@click.option('--url', required=False, help='url to 15Rock cluster')
@click.option('--main_file', type=click.Path(exists=True), required=False,
              help='path to directory containing the main function')
@click.option('--dependencies', multiple=True, required=False,
              help='Files or folders to be placed in the same package at root of package')
@click.option('--requirements_file', type=click.Path(exists=True), required=False, help='Path to requirements.txt')
@click.option('--runtime', required=False, help='e.g. python')
@click.option('--runtime_version', required=False, help='e.g. 3.6')
@click.option('--project_folder', required=False, type=click.Path(exists=True),
              help='Path to the project root. This will also be the package root if specified')
@click.option('--credentials', multiple=True, required=False,
              help='key value pair of the format key=value. This will override --credentials_file')
@click.option('--credentials_file', type=click.Path(exists=True), required=False,
              help="Path to the credentials file. Either this or --credentials should be provided.")
@click.option('--config_file', type=click.Path(exists=True), required=False,
              help="JSON Path to configuration. The values will be overridden by values passed at the terminal. Note, that there won't be any merging of dicts.")
def compute(command, project: str = None, function: str = None, url: str = None, main_file: str = None,
            dependencies: Tuple[str] = None, requirements_file: str = None, runtime: str = None, runtime_version: str
            = None, project_folder: str = None, credentials: Tuple[str] = None, credentials_file: str = None,
            config_file: str = None):
    """Commands for the compute service"""
    # TODO: split credentials by key=value pair
    # TODO: Have a config file too where you can pass all the values?
    result = None
    dep_list = list(dependencies)
    credentials_list = list(credentials)
    credentials_dict = util.text_to_dict(credentials_list)
    fr_compute = compute_client.compute(url=url, credentials=credentials_dict, credentials_file=credentials_file)
    if command == 'deploy':
        util.required('function', function)
        util.required('project', project)
        result = fr_compute.deploy(project, function, main_file=main_file, dependencies=dep_list,
                                   requirements_file=requirements_file, runtime=runtime,
                                   runtime_version=runtime_version, project_folder=project_folder,
                                   config_file=config_file)
        # result = core.deploy(project, function, url=url, main_file=main_file, dependencies=dep_list,
        #                      requirements_file=requirements_file,
        #                      runtime=runtime, runtime_version=runtime_version, project_folder=project_folder,
        #                      credentials=credentials_dict, credentials_file=credentials_file, config_file=config_file)

    elif command == 'list-functions':
        result = fr_compute.list_functions(project=project, function=function)
    elif command == 'delete-function':
        util.required('function', function)
        util.required('project', project)
        result = fr_compute.delete_function(project=project, function=function)
    print(result)
