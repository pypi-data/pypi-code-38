import click
import tempfile
import os

from alfa_sdk.resources import AlgorithmEnvironment
from alfa_sdk.common.helpers import AlfaConfigHelper
from alfa_sdk.common.exceptions import ResourceNotFoundError
from alfa_cli.common.exceptions import AlfaCliError
from alfa_cli.common.utils import zipdir


@click.command()
@click.argument("path", type=str)
@click.option("-i", "--id", "id_", type=str, help="Algorithm id. Overrides config.")
@click.option("-e", "--env", type=str, help="Environment name. Overrides config.")
@click.option("-v", "--version", type=str, help="Release version. Overrides config.")
@click.option("-d", "--desc", type=str, help="Release description. Overrides config.")
@click.option("-n", "--notes", type=str, help="Release notes. Prioritized over --notes-path.")
@click.option("-np", "--notes-path", type=str, help="Path to file with release notes.")
@click.option("-c", "--commit", help="Commit hash to append to release description.")
@click.option("--increment", is_flag=True, help="Enables auto increment of version number.")
@click.pass_obj
def deploy(obj, path, *, increment=False, commit, **kwargs):
    """Deploy a new algorithm release.
    
    The algorithm must be structured in the correct way and contain a valid alfa.yml configuration file.
    Information on the algorithm to deploy will be extracted from the configuration file, but can be overriden.
    If a non existing algorithm environment is specified, it will be created."""

    client = obj["client"]
    conf = AlfaConfigHelper.load(os.path.join(path, "alfa.yml"), is_package=False)

    #

    algorithm_id = kwargs.get("id_") or conf.get("id")
    environment_name = kwargs.get("env") or conf.get("environment")
    version = kwargs.get("version") or conf.get("version")

    if algorithm_id is None:
        raise AlfaCliError(message="No algorithm id found in alfa.yml and arguments.")
    if environment_name is None:
        raise AlfaCliError(message="No environment name found in alfa.yml and arguments.")
    if version is None:
        raise AlfaCliError(message="No release version found in alfa.yml and arguments.")

    #

    description = kwargs.get("desc") or conf.get("description", "")
    if commit is not None:
        description = "{} [{}]".format(description, commit)

    notes = kwargs.get("notes")
    notes_path = kwargs.get("notes_path")
    if not notes and notes_path:
        notes = open(notes_path, "r").read()

    #

    try:
        algorithm = client.get_algorithm(algorithm_id)
    except ResourceNotFoundError:
        raise AlfaCliError(
            message="Algorithm {} not found. You must first create an algorithm through the ALFA Console.".format(
                algorithm_id
            )
        )

    try:
        environment = algorithm.get_environment(environment_name)
    except ResourceNotFoundError:
        environment = algorithm.create_environment(environment_name)

    #

    tmp = tempfile.NamedTemporaryFile(prefix="alfa-deploy-", suffix=".zip")
    zipdir(path, tmp.name, conf=conf)

    res = environment.deploy(
        version, tmp.name, increment=increment, description=description, release_notes=notes
    )
    return obj["logger"].result(res)

