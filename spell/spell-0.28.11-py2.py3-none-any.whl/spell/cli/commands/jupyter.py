# -*- coding: utf-8 -*-
import webbrowser

import click

from spell.cli.exceptions import api_client_exception_handler
from spell.cli.commands.run import create_run_request
from spell.cli.log import logger
from spell.cli.utils import with_emoji, ellipses
from spell.cli.utils.command_options import (
    dependency_params,
    workspace_spec_params,
    machine_config_params,
    cli_params,
    description_param
)
from spell.api.models import Environment


@click.command(name="jupyter", short_help="Create a jupyter workspace")
@click.argument("name", required=True)
@click.option("--lab", is_flag=True, help="Use Jupyter Lab (default: Jupyter Notebook)")
@machine_config_params
@dependency_params(include_python_version=False)
@workspace_spec_params
@description_param
@cli_params
@click.pass_context
def jupyter(ctx, name, lab, machine_type, pip_packages, requirements_file, apt_packages,
            framework, commit_ref, description, envvars, raw_resources,
            conda_file, force, verbose, github_url, github_ref, provider, **kwargs):
    """
    Create a Jupyter workspace on Spell.

    The jupyter command is used to create a Jupyter workspace. If executed from within a git respository,
    the HEAD commit (or optionally a different commit specified with --commit-ref) will be copied into
    the Jupyter workspace.  Alternatively, the --github-url option can be used to specify a GitHub
    repository to copy into the workspace. The other options can be used to further configure the
    Jupyter workspace environment.  Once created, the local web browser will open to the
    Jupyter workspace in the Spell web console.
    """
    logger.info("starting jupyter command")
    utf8 = ctx.obj["utf8"]

    # create a run request
    # Note(Brian): We don't actually need a run request (nor are we creating a run); however,
    # create_run_request does some useful validation of common inputs so we call it here.
    run_req = create_run_request(ctx, machine_type=machine_type, pip_packages=pip_packages,
                                 requirements_file=requirements_file, apt_packages=apt_packages, framework=framework,
                                 commit_ref=commit_ref, description=description, envvars=envvars,
                                 raw_resources=raw_resources, conda_file=conda_file, force=force, verbose=verbose,
                                 github_url=github_url, github_ref=github_ref,
                                 command=None, args=None, docker_image=None, python2=None, python3=None,
                                 idempotent=False, provider=provider, run_type=None,
                                 distributed=None, **kwargs)

    # create an Environment object
    apt, pip = run_req.apt_packages, run_req.pip_packages
    if apt:
        apt = [convert_name_version_pair(x) for x in apt]
    if pip:
        pip = [convert_name_version_pair(x) for x in pip]
    framework = {"name": run_req.framework, "version": run_req.framework_version}
    env = Environment(framework=framework, apt=apt, pip=pip, env_vars=run_req.envvars,
                      conda_file=run_req.conda_file)

    # create the Jupyter workspace
    client = ctx.obj["client"]
    logger.info("sending jupyter workspace request to api")
    with api_client_exception_handler():
        workspace = client.new_jupyter_workspace(name=name, description=description, machine_type=machine_type, lab=lab,
                                                 attached_resources=run_req.attached_resources, environment=env,
                                                 github_url=run_req.github_url, github_ref=run_req.github_ref,
                                                 commit_hash=run_req.commit_hash, workspace_id=run_req.workspace_id)
    click.echo(with_emoji(u"💫", "Opening Jupyter workspace '{}'".format(workspace["name"]), utf8) + ellipses(utf8))
    url = "{}/web_redirect/{}/workspace_exec/{}".format(ctx.obj["client_args"]["base_url"],
                                                        ctx.obj["owner"], workspace["id"])
    webbrowser.open(url)


def convert_name_version_pair(package):
    split = package.split("==")
    return {"name": split[0], "version": split[1] if len(split) > 1 else None}
