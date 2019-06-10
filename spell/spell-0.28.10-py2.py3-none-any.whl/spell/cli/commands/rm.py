import sys

import click

from spell.cli.exceptions import api_client_exception_handler, ExitException
from spell.cli.log import logger


@click.command(name="rm",
               short_help="Specify one or more uploaded resources to delete. "
                          "For example: uploads/[directory]")
@click.argument("resources", required=True, nargs=-1)
@click.pass_context
def rm(ctx, resources):
    """
    Remove one or more uploaded resources.

    The removed resources will no longer show up in `ls` or be mountable with `--mount`.
    """
    client = ctx.obj["client"]

    logger.info("Deleting resource={}".format(resources))
    exit_code = 0
    for resource in resources:
        try:
            with api_client_exception_handler():
                if not resource.startswith("uploads/"):
                    raise ExitException("You must specify an uploaded resource.")
                client.remove_dataset(resource[8:])
        except ExitException as e:
            exit_code = 1
            e.show()
    sys.exit(exit_code)
