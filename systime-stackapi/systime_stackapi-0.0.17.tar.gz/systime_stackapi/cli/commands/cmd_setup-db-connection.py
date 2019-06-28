import click
import json
import paramiko
import os
import sys
from sshtunnel import SSHTunnelForwarder
from systime_stackapi.cli.stackcli import pass_context, StackHelper
from systime_stackapi.stackService import StackService
from random import randint, choice
from time import sleep

stack_helper = StackHelper()

@click.command('setup-db-connection', short_help='Create connection to Database.')
@click.argument('installation', type=click.Choice(choices=stack_helper.get_installation_name_list(True)), nargs=1)
@click.option('--method', type=click.Choice(choices=['tunnel_only', 'cli', 'gui']), default='tunnel_only', help="What to do with the connection.")
@pass_context
def cli(ctx, installation, method):
    """Create SQL server connection."""

    ssh_username = os.getenv('SYSTIME_STACK_CLI_SSH_USERNAME')
    if ssh_username is None:
        ctx.log('Unable to determine SSH username, please set SYSTIME_STACK_CLI_SSH_USERNAME environment variable.')
        exit(1)

    ssh_keyfile = os.getenv('SYSTIME_STACK_CLI_PATH_TO_SSH_KEYFILE')
    if ssh_keyfile is None:
        ctx.log('Unable to determine SSH keyfile, please set SYSTIME_STACK_CLI_PATH_TO_SSH_KEYFILE environment variable.')
        exit(1)

    installation_parameters = installation
    installation_list = ctx.stack_helper.get_installations()

    db_credentials = {}
    webserver_list = []

    for installation in installation_list:
        if installation['InstallationName'] in installation_parameters:
            db_credentials['database_hostname'] = installation['Context']['DATABASE_HOSTNAME']
            db_credentials['database_name'] = installation['Context']['DATABASE_NAME']
            db_credentials['database_user'] = installation['Context']['DATABASE_USER']
            db_credentials['database_pass'] = installation['Context']['DATABASE_PASS']
            webserver_list = ctx.stack_helper.get_installation_webservers(installation['InstallationName'])

    webserver_hostname = choice(webserver_list)

    local_port = randint(32768, 65535)
    server = create_ssh_tunnel(db_credentials['database_hostname'], db_credentials['database_name'], db_credentials['database_user'], db_credentials['database_pass'], ssh_username, ssh_keyfile, webserver_hostname, local_port)

    if method == 'tunnel_only':
        server.start()
        click.echo('Tunnel opened on 127.0.0.1:{}'.format(local_port))
        click.echo('{}: {}'.format('Database hostname', db_credentials['database_hostname']))
        click.echo('{}: {}'.format('Database name', db_credentials['database_name']))
        click.echo('{}: {}'.format('Database user', db_credentials['database_user']))
        click.echo('{}: {}'.format('Database pass', db_credentials['database_pass']))
        while True:
            try:
                sleep(300)
            except KeyboardInterrupt:
                server.stop()
                sys.exit(0)

    if method == 'gui':
        server.start()
        click.echo('Tunnel opened on 127.0.0.1:{}'.format(local_port))
        click.echo('{}: {}'.format('Database hostname', db_credentials['database_hostname']))
        click.echo('{}: {}'.format('Database name', db_credentials['database_name']))
        click.echo('{}: {}'.format('Database user', db_credentials['database_user']))
        click.echo('{}: {}'.format('Database pass', db_credentials['database_pass']))
        click.echo('Attempting to invoke SequelPro')
        click.launch("mysql://{}:{}@127.0.0.1:{}/{}".format(db_credentials['database_user'], db_credentials['database_pass'], local_port, db_credentials['database_name']))
        while True:
            try:
                sleep(300)
            except KeyboardInterrupt:
                server.stop()
                sys.exit(0)

    if method == 'cli':
        server.start()
        click.echo('Tunnel opened on 127.0.0.1:{}'.format(local_port))
        click.echo('{}: {}'.format('Database hostname', db_credentials['database_hostname']))
        click.echo('{}: {}'.format('Database name', db_credentials['database_name']))
        click.echo('{}: {}'.format('Database user', db_credentials['database_user']))
        click.echo('{}: {}'.format('Database pass', db_credentials['database_pass']))
        click.echo('Starting MySQL CLI')
        os.system("mysql -h {} -u {} -P {} -p{} {}".format('127.0.0.1', db_credentials['database_user'], local_port, db_credentials['database_pass'], db_credentials['database_name']))
        server.stop()
        sys.exit()




def create_ssh_tunnel(database_hostname, database_name, database_user, database_pass, ssh_username, ssh_keyfile, webserver_hostname, local_port):
    server =  SSHTunnelForwarder(
        (webserver_hostname, 22),
        ssh_username=ssh_username,
        ssh_pkey=ssh_keyfile,
        remote_bind_address=(database_hostname, 3306),
        local_bind_address=('127.0.0.1', local_port)
    )

    return server
