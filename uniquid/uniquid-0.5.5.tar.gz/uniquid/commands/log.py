# Copyright (c) 2019. Uniquid Inc. or its affiliates. All Rights Reserved.
#
# License is in the "LICENSE" file accompanying this file.
# See the License for the specific language governing permissions and limitations under the License.

import click
from uniquid.core.login_manager import LoginManager
from uniquid.core.cli_console import CliConsole
from uniquid.core.log_watcher import LogWatcher
import uniquid.core.constants as constants
import uniquid.commands.common as common

@click.command()
def log():
    """Start watching logs from the Uniquid system."""
    cc = CliConsole(click.echo, common.print_error,
                    constants.FORMAT_TEXT, click.ClickException,
                    click.confirm, click.prompt)
    lm = LoginManager(cc)
    cc.nolog('Starting watching realtime log')
    watcher = LogWatcher(cc, lm)
    watcher.start()
    cc.happy_exit()