""" Command line interface for the OnePanel Machine Learning platform

'Login' commands group.
"""

import json
from functools import wraps

import click

from onepanel.utilities.login_helper import login_helper


@click.command(help="Login with email and password")
@click.option('-e', '--email', type=str, help="Email you use to login to the website with.")
@click.option('-u', '--username', type=str, help="The name you see in the top right of the website, once you log in.")
@click.option('-p', '--password', type=str, help="Password you use when logging into the website.")
@click.option('-t', '--token', type=str, help="One of the tokens that was created, from the settings "
                                              "-> tokens and variables page.")
@click.pass_context
def login(ctx, email, username, password, token):
    conn = ctx.obj['connection']
    login_helper(conn,email,username,password,token)


@click.command(help="Pass in the gitlab token to login.",
               name="login-with-token",
               hidden=True
               )
@click.argument('token')
@click.pass_context
def login_with_token(ctx, token):
    conn = ctx.obj['connection']
    url = conn.URL + '/sessions'
    data = {
        'sessions': [
            {
                'token': token,
                'device': 'cli'
            }
        ]
    }

    r = conn.put(url, data=json.dumps(data))
    if r.status_code == 200:
        data = r.json()
        conn.save_credentials(data)
    elif r.status_code == 401 or r.status_code == 422:
        print('Invalid token')
    else:
        print('Error: {}'.format(r.status_code))


@click.command(help="Log out the current user",
               name="logout")
@click.pass_context
def logout(ctx):
    conn = ctx.obj['connection']
    conn.clear_credentials()

    click.echo('You are now logged out')


def login_required(func):
    """ Decorator that checks if the session is opened

    The decorator checks if the session is opened based on current context. Therefore please put the decorator
    after @click.pass_context decorator. For example:
        @click.command('hello')
        @click.option('--format')
        @click.pass_context
        @login_required
        def hello(ctx, format):
            ...
    """

    @wraps(func)
    def wrapper(*args, **kwargs):
        if len(args) == 0:
            print('There is no context in the command. Please add @click.pass_context decorator')
            return

        ctx = args[0]
        conn = ctx.obj['connection']
        if conn.user_uid and conn.token:
            return func(*args, **kwargs)
        else:
            print('You are not logged in, '
                'log in by typing `onepanel login` at command line.')
    return wrapper
