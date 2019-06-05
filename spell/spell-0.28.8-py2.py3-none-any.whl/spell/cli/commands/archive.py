import sys

import click

from spell.cli.exceptions import api_client_exception_handler, ExitException
from spell.cli.log import logger


@click.command(name="archive",
               short_help="Specify one or more Run IDs to archive")
@click.argument("run_ids", required=True, type=int, nargs=-1)
@click.pass_context
def archive(ctx, run_ids):
    """
    Archive one or more runs.
    Use to remove a finished or failed run by specifying its RUN_ID.

    The removed runs will no longer show up in `ps`. The outputs of removed runs
    and removed uploads will no longer appear in `ls` or be mountable on
    another run with `--mount`.
    """
    client = ctx.obj["client"]

    logger.info("Archiving runs={}".format(run_ids))
    exit_code = 0
    archived_runs = []
    for run_id in run_ids:
        try:
            with api_client_exception_handler():
                client.remove_run(run_id)
            archived_runs.append(run_id)
        except ExitException as e:
            exit_code = 1
            e.show()
    if len(archived_runs) > 0:
        click.echo("Run{} {} archived".format(
            "s" if len(archived_runs) > 1 else "",
            ", ".join(str(a) for a in archived_runs)))
    sys.exit(exit_code)
