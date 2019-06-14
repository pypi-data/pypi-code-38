import click

from spell.cli.exceptions import (
    api_client_exception_handler,
)
from spell.cli.log import logger


@click.command(name="kill",
               short_help="Kill a current run.")
@click.argument("run_ids", nargs=-1, required=True, type=int)
@click.option("-q", "--quiet", is_flag=True,
              help="Suppress logging")
@click.pass_context
def kill(ctx, run_ids, quiet):
    """
    Kill a current run specified by RUN_ID. To batch kill, input multiple RUN_IDs
    separated by spaces.

    A killed run is sent a kill signal that ends current execution and immediately
    transitions to the "Killed" state once the signal has been received. Killed
    runs do not execute any steps after being killed, so a killed run will not,
    for example, execute the "Pushing" or "Saving" steps if killed when
    in the "Running" status.
    """
    client = ctx.obj["client"]

    run_ids = [i for i in run_ids if i > 0]
    if len(run_ids) <= 0:
        logger.info("No valid run ids specified")
    elif len(run_ids) == 1:
        run_id = run_ids[0]
        with api_client_exception_handler():
            logger.info("Killing run {}".format(run_id))
            client.kill_run(run_id)

        logger.info("Successfully killed run {}".format(run_id))
        if not quiet:
            click.echo(run_id)
    else:
        click.echo("Executing batch kill...")
        with api_client_exception_handler():
            logger.info("Killing runs (batch) {}".format(run_ids))
            data = client.kill_runs(run_ids)
        logger.info("Succesfully killed runs {}".format(data["successful_run_ids"]))
        if not quiet:
            if len(data["final_state_run_ids"]) > 0:
                click.echo("| Already finished: {}".format(" ".join([str(i) for i in data["final_state_run_ids"]])))
            if len(data["non_existent_run_ids"]) > 0:
                click.echo("| Run ID does not exist: {}"
                           .format(" ".join([str(i) for i in data["non_existent_run_ids"]])))
            if len(data["successful_run_ids"]) > 0:
                click.echo("| Successfully killed: {}".format(" ".join([str(i) for i in data["successful_run_ids"]])))
            if len(data["failed_run_ids"]) > 0:
                logger.error("Failed to kill: {} (For more information, contact Spell)"
                             .format(" ".join([str(i) for i in data["failed_run_ids"]])))
