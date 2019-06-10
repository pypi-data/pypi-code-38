import click

from spell.cli.exceptions import api_client_exception_handler
from spell.cli.utils import HiddenOption, prettify_time, tabulate_rows


# display order of columns
USER_COLUMNS = [
    "user_name",
    "email",
    "created_at",
    "last_logged_in",
]

ORG_COLUMNS = [
    "name",
    "role",
    "created_at",
]

# title lookup
USER_TITLES = {
    "created_at": "CREATED",
    "email": "EMAIL",
    "user_name": "USER NAME",
    "last_logged_in": "LAST LOG IN",
}

ORG_TITLES = {
    "name": "ORGANIZATION",
    "role": "ROLE",
    "created_at": "JOINED",
}


@click.command(name="whoami",
               short_help="Display current user information")
@click.option("--raw", help="Display output in raw format.", is_flag=True, default=False, cls=HiddenOption)
@click.pass_context
def me(ctx, raw):
    """
    Display current user information.

    Display information about the currently logged in user, such as username, email, and various other metadata.
    """
    client = ctx.obj["client"]

    with api_client_exception_handler():
        user = client.get_user_info()

    if raw:
        click.echo("\n".join(["{},{}".format(x, y) for x, y in [val for val in user.__dict__.items()]]))
    else:
        user.last_logged_in = prettify_time(user.last_logged_in)
        user.created_at = prettify_time(user.created_at)
        tabulate_rows([user], headers=[USER_TITLES[col] for col in USER_COLUMNS], columns=USER_COLUMNS)

        if user.memberships:
            for m in user.memberships:
                m.name = m.organization.name
                m.created_at = prettify_time(m.created_at)
            click.echo()
            tabulate_rows(user.memberships, headers=[ORG_TITLES[col] for col in ORG_COLUMNS], columns=ORG_COLUMNS)
