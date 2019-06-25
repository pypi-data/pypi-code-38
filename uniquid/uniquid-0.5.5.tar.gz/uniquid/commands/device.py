# Copyright (c) 2018. Uniquid Inc. or its affiliates. All Rights Reserved.
#
# License is in the "LICENSE" file accompanying this file.
# See the License for the specific language governing permissions and limitations under the License.

import click
from uniquid.core.login_manager import LoginManager
from uniquid.core.cli_console import CliConsole
from uniquid.core.devices import Devices
import uniquid.core.constants as constants
import uniquid.commands.common as common


@click.command(name='show-device')
@click.argument('xpub',
                required=True)
@click.option('--output', '-o',
              default=constants.FORMAT_TEXT,
              type=click.Choice(constants.FORMAT_ALL),
              help=('Format used to print data to the console. Valid options'
                    ' are: ') + str(constants.FORMAT_ALL),
              required=False)
def show_device(xpub, output):
    """Show information about a single device, identified by XPUB."""
    cc = CliConsole(click.echo, common.print_error,
                    output, click.ClickException,
                    click.confirm, click.prompt)
    lm = LoginManager(cc)
    devices = Devices(cc, lm)
    devices.show_device(xpub)
    cc.happy_exit()


@click.command(name='list-devices')
@click.option('--sort', '-s',
              default=None,
              type=click.STRING,
              help='Field name to sort output in ascending order.',
              required=False)
@click.option('--sort-desc', '-d',
              default=None,
              type=click.STRING,
              help='Field name to sort output in descending order.',
              required=False)
@click.option('--output', '-o',
              default=constants.FORMAT_TEXT,
              type=click.Choice(constants.FORMAT_ALL),
              help=('Format used to print data to the console. Valid options'
                    ' are: ') + str(constants.FORMAT_ALL),
              required=False)
def list_devices(sort, sort_desc, output):
    """Show a list of all devices."""
    cc = CliConsole(click.echo, common.print_error,
                    output, click.ClickException,
                    click.confirm, click.prompt)
    lm = LoginManager(cc)
    devices = Devices(cc, lm)
    sort_by = None
    is_sort_asc = True
    if sort is not None:
        sort_by = sort
    elif sort_desc:
        sort_by = sort_desc
        is_sort_asc = False
    devices.list_devices(sort_by, is_sort_asc)
    cc.happy_exit()
