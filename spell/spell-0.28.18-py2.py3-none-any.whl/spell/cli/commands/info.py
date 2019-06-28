import click

from spell.api import models
from spell.cli.exceptions import (
    api_client_exception_handler,
    ExitException,
)
from spell.cli.utils import (
    prettify_timespan,
    tabulate_rows,
)


@click.command(name="info",
               short_help="Describes a run. Displays info such as start and end time as well as "
               "run parameters such as apts, pips, and mounts.")
@click.argument("run_id")
@click.pass_context
def info(ctx, run_id):
    """
    Displays information about a run including the start and end time as well run parameters such as
    apts, pips, and mounts.
    """
    def format_env_var(name, value):
        return "{}={}".format(name, value)

    def format_mount(resource, path):
        return "{} at {}".format(resource, path)

    format_hyper_param = format_env_var

    run = None
    with api_client_exception_handler():
        client = ctx.obj["client"]
        run = client.get_run(run_id)
        if isinstance(run, models.Error):
            raise ExitException(run.status)

    lines = []
    if run.workspace:
        lines.append(('Repository', run.workspace.name))
    if run.git_commit_hash:
        lines.append(('Git Commit', run.git_commit_hash))
    exit_code_string = ' ({})'.format(run.user_exit_code) if run.user_exit_code is not None else ''
    lines.append(('Status', '{}{}'.format(run.status, exit_code_string)))
    lines.append(('Command', run.command))
    lines.append(('Creator', run.creator.user_name))
    lines.append(('Machine Type', run.gpu))
    lines.append(('Framework', run.framework.split('@')[0]))
    if run.docker_image:
        lines.append(('Docker Image', run.docker_image.split('@')[0]))
    if run.github_url:
        lines.append(('GitHub URL', run.github_url))
    if run.started_at is not None:
        lines.append(('Start Time', "{:%Y-%m-%d %H:%M:%S}".format(run.started_at)))
    if run.ended_at is not None:
        lines.append(('End Time', "{:%Y-%m-%d %H:%M:%S}".format(run.ended_at)))
        if run.started_at is not None:
            lines.append(('Duration', prettify_timespan(run.started_at, run.ended_at)))

    if run.attached_resources:
        resources = list(run.attached_resources.keys())
        lines.append(('Mounts', format_mount(resources[0], run.attached_resources[resources[0]])))
        for resource in resources[1:]:
            lines.append(('', format_mount(resource, run.attached_resources[resource])))

    if run.environment_vars:
        names = list(run.environment_vars.keys())
        lines.append(('Environment Vars', format_env_var(names[0], run.environment_vars[names[0]])))
        for name in names[1:]:
            lines.append(('', format_env_var(name, run.environment_vars[name])))

    if run.pip_packages:
        lines.append(('Pip Packages', run.pip_packages[0]))
        for pip in run.pip_packages[1:]:
            lines.append(('', pip))

    if run.apt_packages:
        lines.append(('Apt Packages', run.apt_packages[0]))
        for apt in run.apt_packages[1:]:
            lines.append(('', apt))

    if run.hyper_params:
        hyper_params = [format_hyper_param(k, v) for k, v in run.hyper_params.items()]
        lines.append(('Hyper Parameters', hyper_params[0]))
        for h in hyper_params[1:]:
            lines.append(('', h))

    tabulate_rows(lines)
