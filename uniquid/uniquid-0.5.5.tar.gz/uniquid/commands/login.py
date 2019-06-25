# Copyright (c) 2018. Uniquid Inc. or its affiliates. All Rights Reserved.
#
# License is in the "LICENSE" file accompanying this file.
# See the License for the specific language governing permissions and limitations under the License.

import click
from uniquid.core.login_manager import LoginManager
from uniquid.core.cli_console import CliConsole
import uniquid.core.constants as constants
import uniquid.commands.common as common


@click.command()
@click.argument('org',
                required=False)
@click.option('--credentials-file', '-c',
              envvar='UNIQUID_CRED_FILE',
              help=('Path to a credentials file.'
                    ' Option is available to allow the user to specify the'
                    ' path to a file containing the user\'s login credentials.'
                    ' By default, if this option is not passed, the tool will'
                    ' search for the credential file at'
                    ' \".uniquid/credentials.json\" in the user\'s'
                    ' home directory.'
                    ' The path can also be set using the environment'
                    ' variable UNIQUID_CRED_FILE.'),
              required=False)
@click.option('--user', '-u',
              envvar='UNIQUID_USER',
              help=('UniquID Username. Provided during account registration.'
                    ' The Username must be provided if no crediantials file'
                    ' is provided.'
                    ' The option can also be set using the environment'
                    ' variable UNIQUID_USER.'),
              required=False)
@click.option('--access-key', '-a',
              envvar='UNIQUID_ACCESS_KEY',
              help=('UniquID Access Key. Provided after account registration.'
                    ' The Access Key must be provided if no crediantials file'
                    ' is provided.'
                    ' The option can also be set using the environment'
                    ' variable UNIQUID_ACCESS_KEY.'),
              required=False)
@click.option('--login-url', '-l',
              envvar='UNIQUID_LOGIN_URL',
              help=('UniquID server URL for the Login. Option is available to'
                    ' allow the user to specify the URL of the login server.'
                    ' This is not normally required. The URL'
                    ' must be in the format <ip address>:<port number>. The'
                    ' inclusion of the port number is optional.'
                    ' The option can also be set using the environment'
                    ' variable UNIQUID_LOGIN_URL.'),
              required=False)
@click.option('--org-url', '-o',
              envvar='UNIQUID_ORG_URL',
              help=('UniquID server URL for the user\'s Organization. Option'
                    ' is available to'
                    ' allow the user to specify the URL of their assigned'
                    ' server. This is not normally required. The URL'
                    ' must be in the format <ip address>:<port number>. The'
                    ' inclusion of the port number is optional.'
                    ' The option can also be set using the environment'
                    ' variable UNIQUID_ORG_URL.'),
              required=False)
def login(org, access_key, user, login_url, org_url, credentials_file):
    """Login to the Uniquid system, passing the organization identifier ORG.

    When first logging into the system, the user must pass the location of
    the credentials file they downloaded during registration, using the
    "--credentials-file" option. If they saved the credentials file at
    "<home directory>/.uniquid/credentials.json" then they do not need to
    pass the file path as the file will be automatically detected by the login
    command.
    If the user does not want to use the credentials file then they can
    pass the organization identifier, user and access key using command line
    options.  If the user specified the organization on the command line, then
    after the first successful login, they no longer need to pass the
    organization unless they want to change the organization account which
    they are using.
    If no credentials file is being used, the user must always pass the
    user identifier and the access key.
    """
    cc = CliConsole(click.echo, common.print_error,
                    constants.FORMAT_TEXT, click.ClickException,
                    click.confirm, click.prompt)
    lm = LoginManager(cc)
    lm.connect(org, access_key, user, login_url, org_url, credentials_file)
    cc.happy_exit()


@click.command()
def logout():
    """Logout from the Uniquid system."""
    cc = CliConsole(click.echo, common.print_error,
                    constants.FORMAT_TEXT, click.ClickException,
                    click.confirm, click.prompt)
    lm = LoginManager(cc)
    lm.disconnect()
    cc.happy_exit()


@click.command()
@click.option('--verbose', '-v',
              is_flag=True,
              default=False,
              help=('Print more detailed status information about'
                    ' the connection to the Uniquid system.'),
              required=False)
@click.option('--output', '-o',
              default=constants.FORMAT_TEXT,
              type=click.Choice(constants.FORMAT_ALL),
              help=('Format used to print data to the console. Valid options'
                    ' are: ') + str(constants.FORMAT_ALL),
              required=False)
def status(verbose, output):
    """Print the status of the connection to Uniquid system."""
    cc = CliConsole(click.echo, common.print_error,
                    output, click.ClickException,
                    click.confirm, click.prompt)
    lm = LoginManager(cc)
    cc.begin_list()
    lm.print_status(verbose)
    cc.end_list()
    cc.happy_exit()
