import click

from gip import command


@click.group()
@click.option(
    '--debug/--no-debug',
    default=False,
    help='Enable or disable debug mode. Default is disabled.'
)
@click.option(
    '--gitlab-token',
    envvar='GIP_GITLAB_TOKEN',
    default=False,
    help='Provide the private token for the Gitlab API. \
        Can be set as environment variable GIP_GITLAB_TOKEN'
)
@click.option(
    '--github-token',
    envvar='GIP_GITHUB_TOKEN',
    default=False,
    help='Provide the private token for the Github API. \
        Can be set as environment variable GIP_GITHUB_TOKEN'
)
@click.option(
    '--lock-file',
    default='.giplock.yml',
    help='Provide the path to the lockfile, defaults to \
        .giplock.yml in the current working directory',
    type=click.Path(
        writable=True
    )
)
@click.version_option(version='0.0.1')
@click.pass_context
def main(ctx, debug, gitlab_token, github_token, lock_file):
    """
    \b
     _______ __
    |     __|__|.-----.
    |    |  |  ||  _  |
    |_______|__||   __|
                |__|
    Gip is a language agnostic dependency manager
    which uses API calls to pull repositories.

    Enable autocomplete for Bash (.bashrc):
      eval "$(_GIP_COMPLETE=source gip)"

    Enable autocomplete for ZSH (.zshrc):
      eval "$(_GIP_COMPLETE=source_zsh gip)"
    """
    ctx.obj = {}
    ctx.obj['args'] = {}
    ctx.obj['args']['debug'] = debug
    ctx.obj['args']['gitlab_token'] = gitlab_token
    ctx.obj['args']['github_token'] = github_token
    ctx.obj['args']['lock_file'] = lock_file


main.add_command(command.install.install)
