import click

from spell.cli.exceptions import api_client_exception_handler
from spell.cli.log import logger
from spell.cli.utils import prettify_time, tabulate_rows, HiddenOption


# display order of columns
COLUMNS = [
    "name",
    "creator_name",
    "pretty_created_at",
    "pretty_updated_at",
]

# title lookup
TITLES = {
    "name": "NAME",
    "creator_name": "CREATOR",
    "pretty_created_at": "CREATED",
    "pretty_updated_at": "UPDATED",
}


@click.command(name="repos",
               short_help="List repositories")
@click.option("--raw", is_flag=True,
              help="Display output in raw format", cls=HiddenOption)
@click.pass_context
def repos(ctx, raw):
    """
    List all owner repositories

    A repository is defined by the root commit of a git repository. Thus, the family of
    all Git commits that originate from the same root commit belong to the same repository.
    Repositories do not need to be managed or created -- they are created by the run command
    when necessary.
    """
    # grab the repos from the API
    repos = []
    client = ctx.obj["client"]
    with api_client_exception_handler():
        logger.info("Retrieving repository information from Spell")
        repos = client.get_workspaces()

    # prepare objects for display
    for repo in repos:
        repo.id = str(repo.id)
        repo.creator_name = repo.creator.user_name
        repo.pretty_created_at = prettify_time(repo.created_at)
        repo.pretty_updated_at = prettify_time(repo.updated_at)

    # build the rows for tabulate
    sorted_rows = sorted(repos, key=lambda x: x.updated_at, reverse=True)
    tabulate_rows(sorted_rows,
                  headers=[TITLES[col] for col in COLUMNS],
                  columns=COLUMNS,
                  raw=raw)
