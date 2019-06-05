import shutil
import click
import pathlib

from gip import logger
from gip import util
from gip import exceptions
from gip import model
from gip import sources

LOG = logger.get_logger(__name__)


@click.command()
@click.pass_context
@click.option(
    '--upgrade',
    help='Bring versions to what is specified in requirements.yml',
    type=bool
)
@click.option(
    '--requirements',
    '-r',
    help='Requirements file to install',
    type=click.Path(
        exists=True,
    )
)
def install(ctx, upgrade, requirements):
    """
    Install dependencies, if already present just skips when version checking is required, pass --upgrade.  # noqa:E501

    :param ctx: click object containing the arguments from global
    :param upgrade: boolean whenever upgrading is enabled
    :param requirements: click path object poiting to requirements file
    """
    args = ctx.obj.get('args')

    # Parse requirements file to Python object
    requirements = _parse_and_validate(
        path=requirements,
        type='requirements'
    )

    # After parsing check if a token is mandatory or advised
    if (any(d['type'] == 'gitlab' for d in requirements) and
            not args['gitlab_token']):
        util.sysexit_with_message(
            "Gitlab repo in requirements but no token passed, \
            use --gitlab-token"
        )
    if (any(d['type'] == 'github' for d in requirements) and
            not args['github_token']):
        util.sysexit_with_message(
            "Github repo in requirements but no token passed, \
            use --github-token"
        )

    # Init lockfile
    locks_path = pathlib.Path(args['lock_file']).resolve()

    # Init current_lock list
    current_lock = {}
    if locks_path.is_file():
        current_lock = _parse_and_validate(
            path=locks_path,
            type='locks'
        )
    else:
        LOG.info("Lock file does not exist, will be created at {path}".format(
            path=locks_path)
        )

    # Init new_lock list
    new_lock = {}
    # Loop requirements for downloading
    for requirement in requirements:
        if requirement['name'] in current_lock and not upgrade:
            LOG.info("{requirement} already installed, skipping".format(
                requirement=requirement['name'])
            )
        else:
            try:
                if requirement['type'] == 'gitlab':
                    # Init Gitlab object
                    source = sources.gitlab.Gitlab(
                        repo=requirement['repo'],
                        version=requirement.get('version'),
                        token=args['gitlab_token']
                    )
                elif requirement['type'] == 'github':
                    # Init Github object
                    source = sources.github.Github(
                        repo=requirement['repo'],
                        version=requirement.get('version'),
                        token=args['github_token']
                    )
            except (exceptions.RepoNotFound,
                    exceptions.HttpError,
                    exceptions.AuthenticationError) as e:
                util.sysexit_with_message(str(e))

            try:
                commit_sha = source.get_commit_hash()
            except exceptions.CommitHashNotFound as e:
                util.sysexit_with_message(str(e))

            if commit_sha == current_lock.get(requirement['name']):
                LOG.info(
                    "{requirement} already the current version, "
                    "skipping".format(
                        requirement=requirement['name'])
                    )
            else:
                # Convert dest to absolute path
                dest = pathlib.Path(requirement.get('dest', '')).resolve()
                # Create archive name (ex. ansible-role-plex.tar.gz)
                archive_name = "{}.tar.gz".format(requirement['name'])
                # Append name to destination directory
                archive_dest = dest.joinpath(archive_name)

                # Remove old versions if existing
                test = dest.joinpath(requirement['name'])
                if test.is_dir():
                    shutil.rmtree(test)

                # Get the archive
                try:
                    source.get_archive(
                        dest=archive_dest
                    )
                except (exceptions.DirectoryDoesNotExist,
                        exceptions.AuthenticationError,
                        exceptions.ArchiveNotFound) as e:
                    # Write current state to lock
                    _write_lock_file(
                        path=locks_path,
                        current_lock=current_lock,
                        new_lock=new_lock
                    )
                    util.sysexit_with_message(str(e))

                # Extract archive to location
                try:
                    source.extract_archive(
                        src=archive_dest,
                        dest=dest,
                        name=requirement['name']
                    )
                except (exceptions.DirectoryDoesNotExist,
                        TypeError,
                        FileNotFoundError) as e:
                    # Write current state to lock
                    _write_lock_file(
                        path=locks_path,
                        current_lock=current_lock,
                        new_lock=new_lock
                    )
                    # Cleanup archive
                    util.remove_file(archive_dest)
                    # Exit with message
                    util.sysexit_with_message(str(e))

                # No exceptions add to new_lock since succesfull download
                if requirement['name'] in current_lock:
                    LOG.success("{requirement} successfully updated to \
                        {version}".format(
                            requirement=requirement['name'],
                            version=source.version
                        )
                    )
                else:
                    LOG.success("{requirement} successfully installed".format(
                        requirement=requirement['name'])
                    )

                try:
                    new_lock[requirement['name']] = source.get_commit_hash()
                except exceptions.CommitHashNotFound as e:
                    util.sysexit_with_message(str(e))

    # End for loop
    _write_lock_file(
        path=locks_path,
        current_lock=current_lock,
        new_lock=new_lock
    )


def _write_lock_file(path, current_lock, new_lock):
    """
    Write current state to lock file

    :param path: path of the current lock file and where to write to
    :param current_lock: dict containing the lock before executing gip
    :param new_lock: dict container the new lock
    """
    # Check if new_lock has data
    if new_lock:
        # No current lock just write to file
        if not current_lock:
            util.write_yaml(
                path=path,
                data=new_lock
            )
        else:
            # Current lock, merge the two and write to file
            util.write_yaml(
                path=path,
                data=util.merge_dicts(current_lock, new_lock)
            )


def _parse_and_validate(path, type):
    """
    Parse and validate file against Cerberus scheme

    :param path: path to file
    :param type: one of the modeltypes available in model.scheme
    :return: parsed and validated data
    """
    try:
        data = util.read_yaml(path=path)
    except exceptions.ParserError as e:
        util.sysexit_with_message(str(e))

    # Validate requirements file
    try:
        model.scheme.validate(
            type=type,
            data=data
        )
    except exceptions.ValidationError as e:
        util.sysexit_with_message(
            "Parsing failed for {file} due to {errors}".format(
                file=path,
                errors=e.errors
            )
        )

    # Return parsed and validated data
    return data
