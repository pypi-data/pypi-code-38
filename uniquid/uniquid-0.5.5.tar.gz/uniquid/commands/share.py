# Copyright (c) 2018. Uniquid Inc. or its affiliates. All Rights Reserved.
#
# License is in the "LICENSE" file accompanying this file.
# See the License for the specific language governing permissions and limitations under the License.

import click
import json
from uniquid.core.login_manager import LoginManager
from uniquid.core.cli_console import CliConsole
from uniquid.core.shares import Shares
import uniquid.core.constants as constants
import uniquid.commands.common as common


@click.command(name='list-shares')
@click.option('--direction', '-d',
              default=constants.SHARE_DIR_BOTH,
              type=click.Choice(constants.SHARE_DIR_ALL),
              help=('Direction of sharing of devices to be listed.'),
              required=False)
@click.option('--org', '-x',
              default=None,
              type=click.STRING,
              help=('Organization ID to filter shared devices by.'),
              required=False)
@click.option('--output', '-o',
              default=constants.FORMAT_TEXT,
              type=click.Choice(constants.FORMAT_ALL),
              help=('Format used to print data to the console. Valid options'
                    ' are: ') + str(constants.FORMAT_ALL),
              required=False)
def list_shares(direction, org, output):
    """Show a list of all of the shared devices.

        Devices can be those you have shared with other organizations or
        those shared with you by other organizations.
    """
    cc = CliConsole(click.echo, common.print_error,
                    output, click.ClickException,
                    click.confirm, click.prompt)
    lm = LoginManager(cc)
    shares = Shares(cc, lm)
    shares.list_shares(direction, org)
    cc.happy_exit()


@click.command(name='create-shares')
@click.option('--input-json', '-j',
              default=None,
              type=click.STRING,
              help=('JSON object describing the share.'),
              required=False)
@click.option('--input-json-file', '-i',
              default=None,
              type=click.File(mode='r'),
              help=('Path to file containing a list of JSON'
                    ' share objects.'),
              required=False)
def create_shares(input_json, input_json_file):
    """Share multiple devices with another Uniquid Organization.

        Devices to be shared must be owned by the user.
    """
    if (input_json is None) == (input_json_file is None):
        raise click.ClickException(constants.ERR_SINGLE_OPTION)
    cc = CliConsole(click.echo, common.print_error,
                    constants.FORMAT_TEXT, click.ClickException,
                    click.confirm, click.prompt)
    lm = LoginManager(cc)
    shares = Shares(cc, lm)
    json_string = input_json
    if input_json_file:
        json_string = input_json_file.read()
    shares.create_shares(json_string)
    cc.happy_exit()


@click.command(name='delete-shares')
@click.argument('shareids', nargs=-1)  # variadic
@click.option('--input-json', '-j',
              default=None,
              type=click.STRING,
              help=('JSON array with IDs of shares to be deleted.'),
              required=False)
@click.option('--input-json-file', '-i',
              default=None,
              type=click.File(mode='r'),
              help=('Path to file containing a JSON array of the IDs'
                    ' of the shares to be deleted.'),
              required=False)
def delete_shares(shareids, input_json, input_json_file):
    """Remove the sharing of devices which have Share IDs SHAREIDS.

        Devices to be shared must be owned by the user therefore the devices
        which will have their sharing status removed must be owned by the user.
    """
    if ((input_json is None) == (input_json_file is None) and
            (shareids is None or len(shareids) == 0)):
        raise click.ClickException(constants.ERR_SINGLE_OPTION)
    cc = CliConsole(click.echo, common.print_error,
                    constants.FORMAT_TEXT, click.ClickException,
                    click.confirm, click.prompt)
    lm = LoginManager(cc)
    shares = Shares(cc, lm)
    json_string = input_json
    if input_json_file:
        json_string = input_json_file.read()
    # if user passed one+ arguments, these take priority over a JSON array.
    if(len(shareids) > 0):
        id_list = list()
        for id in shareids:
            id_list.append(str(id))
        json_string = json.dumps(id_list)
    shares.delete_shares(json_string)
    cc.happy_exit()
