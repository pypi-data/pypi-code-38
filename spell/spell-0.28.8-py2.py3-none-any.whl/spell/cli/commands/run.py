# -*- coding: utf-8 -*-
import os

import click
import git
import requirements

from spell.api.models import RunRequest
from spell.cli.api_constants import get_frameworks
from spell.cli.exceptions import (
    api_client_exception_handler,
    ExitException,
    SPELL_INVALID_CONFIG,
    SPELL_BAD_REPO_STATE,
)
from spell.cli.commands.logs import logs
from spell.cli.log import logger
from spell.cli.utils import LazyChoice, git_utils, parse_utils, with_emoji, ellipses
from spell.cli.utils.parse_utils import ParseException
from spell.cli.utils.command_options import (
    dependency_params,
    workspace_spec_params,
    machine_config_params,
    cli_params,
    description_param,
    background_option,
    docker_image_option,
    idempotent_option
)


@click.command(name="run",
               short_help="Execute a new run")
@click.argument("command")
@click.argument("args", nargs=-1)
@idempotent_option
@machine_config_params
@docker_image_option
@dependency_params()
@workspace_spec_params
@description_param
@cli_params
@background_option
@click.option("--distributed", type=int, metavar="N",
              help="Execute a distributed run using N machines of the specified machine type.")
@click.pass_context
def run(ctx, command, args, machine_type, pip_packages, requirements_file, apt_packages,
        docker_image, framework, python2, python3, commit_ref, description, envvars, raw_resources, background,
        conda_file, force, verbose, idempotent, provider, distributed, run_type="user", **kwargs):
    """
    Execute COMMAND remotely on Spell's infrastructure

    The run command is used to create runs and is likely the command you'll use most
    while using Spell. It is intended to be emulate local development. Any code,
    software, binaries, etc., that you can run locally on your computer can be run
    on Spell - you simply put `spell run` in front of the same commands you would use
    locally and they will run remotely. The various options can be used to customize
    the environment in which COMMAND will run.
    """
    logger.info("starting run command")

    run_req = create_run_request(ctx, command, args, machine_type, pip_packages, requirements_file, apt_packages,
                                 docker_image, framework, python2, python3, commit_ref, description, envvars,
                                 raw_resources, conda_file, force, verbose, idempotent, provider, run_type,
                                 distributed=distributed, **kwargs)

    # execute the run
    client = ctx.obj["client"]
    logger.info("sending run request to api")
    with api_client_exception_handler():
        run = client.run(run_req)

    utf8 = ctx.obj["utf8"]
    if run.already_existed:
        click.echo(with_emoji(u"♻️", "Idempotent: Found existing run {}".format(run.id), utf8) + ellipses(utf8))
    else:
        click.echo(with_emoji(u"💫", "Casting spell #{}".format(run.id), utf8) + ellipses(utf8))
    if background:
        click.echo("View logs with `spell logs {}`".format(run.id))
    else:
        click.echo(with_emoji(u"✨", "Stop viewing logs with ^C", utf8))
        ctx.invoke(logs, run_id=str(run.id), follow=True, verbose=verbose, run_warning=True)


def create_run_request(ctx, command, args, machine_type, pip_packages, requirements_file, apt_packages,
                       docker_image, framework, python2, python3, commit_ref, description, envvars,
                       raw_resources, conda_file, force, verbose, idempotent, provider, run_type,
                       github_url, github_ref, distributed=None, **kwargs):
    framework_version = None
    if framework is not None:
        split = framework.split("==")
        framework = LazyChoice(get_frameworks).convert(split[0],
                                                       None, ctx)
        framework_version = split[1] if len(split) > 1 else None

    if command is None:
        cmd_with_args = None
    else:
        cmd_with_args = " ".join((command,) + args)

    git_repo = None
    if github_url is None:
        try:
            git_repo = git.Repo(os.getcwd(), search_parent_directories=True)
        except git.exc.InvalidGitRepositoryError:
            pass
    if git_repo is None:
        if github_url is None:
            if force:
                logger.warn("No git repository found! Running without a workspace.")
            else:
                click.confirm("Could not find a git repository, so no user files will be available. "
                              "Continue anyway?", default=True, abort=True)
        local_root = None
        workspace_id = None
        commit_hash = None
        relative_path = None
        root_directory = None
    else:
        # Get relative path from git-root to CWD.
        local_root = git_repo.working_dir
        relative_path = os.path.relpath(os.getcwd(), local_root)
        root_directory = os.path.basename(local_root)

        try:
            next(git_repo.iter_commits(max_parents=0))
        except ValueError:
            raise ExitException("The repository " + git_repo.working_dir + " has no commits! Please commit all files "
                                "necessary to run this project before continuing.", SPELL_BAD_REPO_STATE)

        if len(git_repo.submodules) > 0:
            logger.warn("Spell does not currently support Git submodules. "
                        "Files within submodules will not be available within the run.")

        workspace_id, commit_hash, commit_message = git_utils.push_workspace(ctx, git_repo, commit_ref, force=force)
        if description is None:
            description = commit_message

    source_spec = sum(1 for x in (framework, docker_image, conda_file) if x is not None)
    if source_spec > 1:
        raise ExitException("Only one of the following options can be specified: --framework, --from, --conda-file",
                            SPELL_INVALID_CONFIG)

    if docker_image is not None and (pip_packages or apt_packages or requirements_file):
        raise ExitException("--apt, --pip, or --pip-req cannot be specified when --from is provided."
                            " Please install packages from the specified Dockerfile.",
                            SPELL_INVALID_CONFIG)

    if kwargs.get("conda_env"):
        logger.warn("the --conda-env option is deprecated and being ignored. You only need to provide --conda-file.")
    if conda_file is not None and (pip_packages or requirements_file):
        raise ExitException("--pip or --pip-req cannot be specified when using a conda environment. "
                            "You can include the pip installs in the conda environment file instead.")
    if conda_file is not None and (python2 or python3):
        raise ExitException("--python2 or --python3 cannot be specified when using a conda environment. "
                            "Please include the python version in your conda environment file instead.")
    # Read the conda file
    conda_file_contents = None
    if conda_file is not None:
        with open(conda_file) as conda_f:
            conda_file_contents = conda_f.read()

    if requirements_file:
        if not os.path.isfile(requirements_file):
            raise ExitException("--pip-req file not found: "+requirements_file)
        pip_packages = list(pip_packages)
        with open(requirements_file, 'r') as rf:
            for req in requirements.parse(rf):
                pip_packages.append(req.line)

    if python2 and python3:
        raise ExitException("--python2 and --python3 cannot both be specified")

    # extract envvars into a dictionary
    curr_envvars = parse_utils.parse_env_vars(envvars)

    # extract attached resources
    try:
        attached_resources = parse_utils.parse_attached_resources(raw_resources)
    except ParseException as e:
        raise ExitException(click.wrap_text(
            "Incorrect formatting of mount '{}', it must be <resource_path>[:<mount_path>]".format(e.token)),
            SPELL_INVALID_CONFIG)

    return RunRequest(
        machine_type=machine_type,
        command=cmd_with_args,
        workspace_id=workspace_id,
        commit_hash=commit_hash,
        cwd=relative_path,
        root_directory=root_directory,
        pip_packages=pip_packages,
        apt_packages=apt_packages,
        docker_image=docker_image,
        framework=framework,
        framework_version=framework_version,
        python2=python2 if (python2 or python3) else None,
        description=description,
        envvars=curr_envvars,
        attached_resources=attached_resources,
        conda_file=conda_file_contents,
        run_type=run_type,
        idempotent=idempotent,
        provider=provider,
        local_root=local_root,
        github_url=github_url,
        github_ref=github_ref,
        distributed=distributed,
    )
