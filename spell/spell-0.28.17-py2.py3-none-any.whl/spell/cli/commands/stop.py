import click

from spell.cli.exceptions import (
    api_client_exception_handler,
)
from spell.cli.log import logger


@click.command(name="stop",
               short_help="Stop a run with status 'Running'")
@click.argument("run_ids", nargs=-1, required=True, type=int)
@click.option("-q", "--quiet", is_flag=True,
              help="Suppress logging")
@click.pass_context
def stop(ctx, run_ids, quiet):
    """
    Stop runs currently in the "Running" state specified by 'run_ids'.

    A stopped run is sent a stop signal that ends current execution and
    transitions to the "Saving" state once the signal has been received. Stopped
    runs will execute any and all steps after being stopped, so a stopped run will,
    for example, execute both the "Pushing" and "Saving" steps after stopping.
    If "stop" is called on a run that has not yet entered the "Running" state, the
    run is killed (see documentation of "kill" for more details).
    """

    client = ctx.obj["client"]

    run_ids = [i for i in run_ids if i > 0]
    if len(run_ids) <= 0:
        logger.info("No valid run ids specified")
    elif len(run_ids) == 1:
        run_id = run_ids[0]
        with api_client_exception_handler():
            client.stop_run(run_id)
        if not quiet:
            click.echo("Stopping run {}. Use 'spell logs -f {}' to view logs while the job finishes."
                       .format(run_id, run_id))
    else:
        with api_client_exception_handler():
            data = client.stop_runs(run_ids)
        click.echo("Executing batch stop... Use 'spell logs -f RUN_ID' to view logs for a run while the job finishes.")
        if not quiet:
            if len(data["post_running_run_ids"]) > 0:
                click.echo("| Already finished: {}".format(" ".join([str(i) for i in data["post_running_run_ids"]])))
            if len(data["non_existent_run_ids"]) > 0:
                click.echo("| Run ID does not exist: {}"
                           .format(" ".join([str(i) for i in data["non_existent_run_ids"]])))
            if len(data["successful_run_ids"]) + len(data["pre_running_run_ids"]) > 0:
                click.echo("--------------------------------------")
                if len(data["successful_run_ids"]) > 0:
                    click.echo("| Successfully stopping: {}. Any outputs will be pushed and saved."
                               .format(" ".join([str(i) for i in data["successful_run_ids"]])))
                if len(data["pre_running_run_ids"]) > 0:
                    click.echo("| Successfully killed: {}. Execution was not initiated."
                               .format(" ".join([str(i) for i in data["pre_running_run_ids"]])))
            if len(data["failed_run_ids"]) > 0:
                logger.error("Failed to stop: {} (For more information, contact Spell)"
                             .format(" ".join([str(i) for i in data["failed_run_ids"]])))
