from cdislogging import get_logger
import click
import logging

from .validation import validate_user_yaml
from .conversion import convert_old_user_yaml_to_new_user_yaml


logger = get_logger("gen3users", None, "info")
logging.basicConfig()


@click.group()
def main():
    """Utils for Gen3 commons user management."""


@main.command()
@click.argument("files", type=str, nargs=-1, required=True)
def validate(files):
    """Validate one or more user.yaml FILES."""

    failed_validation = False
    for file_name in files:
        try:
            with open(file_name, "r") as f:
                user_yaml = f.read()
                validate_user_yaml(user_yaml, file_name)
        except Exception as e:
            logger.error("{}: {}".format(type(e).__name__, e))
            failed_validation = True
    if failed_validation:
        raise AssertionError(
            "user.yaml validation failed. See errors in previous logs."
        )


@main.command()
@click.argument("file", type=str, nargs=1, required=True)
@click.argument("destination", type=str, nargs=1, required=False)
def convert(file, destination):
    """Convert a user.yaml FILE to the new format. If a DESTINATION is provided, saves the result as a file. Otherwise, print the result."""

    with open(file, "r") as f:
        user_yaml = f.read()
        convert_old_user_yaml_to_new_user_yaml(user_yaml, destination)


if __name__ == "__main__":
    main()
