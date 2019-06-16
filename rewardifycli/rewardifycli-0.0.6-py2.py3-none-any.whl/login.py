"""
CHANGELOG

Added 15.06.2019
"""
# third party
import click

# third party
from rewardify.main import Rewardify

# local
from rewardifycli.util import Templater, UserCredentials


@click.command('login')
@click.argument('username')
@click.argument('password')
def login(password, username):
    facade: Rewardify = Rewardify.instance()
    templater: Templater = Templater.instance()

    # The templates will display the username for more personalized messages
    context = {'username': username}

    if not facade.exists_user(username):
        templater.echo_template('user_not_exists.jinja2', context)
        raise click.Abort()

    if not facade.user_check_password(username, password):
        templater.echo_template('wrong_password.jinja2', context)
        raise click.Abort()

    # The UserCredentials singleton provides easy access to the credentials saved in the temp file. After the username
    # and password have been checked the new credentials can be saved persistently, so that every command after this
    # one has access to them
    credentials: UserCredentials = UserCredentials.instance()
    credentials.save(username, password)

    templater.echo_template('login_success.jinja2', context)
