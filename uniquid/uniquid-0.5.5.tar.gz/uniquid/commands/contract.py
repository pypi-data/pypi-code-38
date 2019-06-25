# Copyright (c) 2018. Uniquid Inc. or its affiliates. All Rights Reserved.
#
# License is in the "LICENSE" file accompanying this file.
# See the License for the specific language governing permissions and limitations under the License.

import click
import json
from uniquid.core.login_manager import LoginManager
from uniquid.core.cli_console import CliConsole
from uniquid.core.contracts import Contracts
import uniquid.core.constants as constants
import uniquid.commands.common as common


@click.command(name='create-contracts')
@click.option('--input-json', '-j',
              default=None,
              type=click.STRING,
              help=('JSON object describing the contract.'),
              required=False)
@click.option('--input-json-file', '-i',
              default=None,
              type=click.File(mode='r'),
              help=('Path to file containing a list of JSON'
                    ' contract objects.'),
              required=False)
def create_contracts(input_json, input_json_file):
    """Create a new Access contract or multiple contracts.

        Access contracts grant permissions for \"User\" devices to
        use the services provided by \"Provider\" devices. The contract or
        contracts must be specified in JSON format and passed to the
        command, either on the command line or as a file.

        The \"User\" and \"Provider\" devices are identified by their
        uniquid XPUB public key values.  The type of services being provided
        by the \"Provider\" device are specified by the function IDs.

        The format of the JSON is:

        \b
        [
            {
                \"provider\": \"tpubXXXXXXXXXX\",
                \"user\": \"tpubYYYYYYYYYY\",
                \"functions\": [38, 39]
            },
            {
                \"provider\": \"tpubXXXXXXXXXX\",
                \"user\": \"tpubZZZZZZZZZZ\",
                \"functions\": [38, 39]
            }
        ]

        If the JSON is passed using the --input-json option, then no line breaks
        should be included.
    """
    if (input_json is None) == (input_json_file is None):
        raise click.ClickException(constants.ERR_SINGLE_OPTION)
    cc = CliConsole(click.echo, common.print_error,
                    constants.FORMAT_TEXT, click.ClickException,
                    click.confirm, click.prompt)
    lm = LoginManager(cc)
    contracts = Contracts(cc, lm)
    json_string = input_json
    if input_json_file:
        json_string = input_json_file.read()
    contracts.create_contracts(json_string)
    cc.happy_exit()


@click.command(name='list-contracts')
@click.option('--output', '-o',
              default=constants.FORMAT_TEXT,
              type=click.Choice(constants.FORMAT_ALL),
              help=('Format used to print data to the console. Valid options'
                    ' are: ') + str(constants.FORMAT_ALL),
              required=False)
def list_contracts(output):
    """Show a list of all the existing contracts."""
    cc = CliConsole(click.echo, common.print_error,
                    output, click.ClickException,
                    click.confirm, click.prompt)
    lm = LoginManager(cc)
    contracts = Contracts(cc, lm)
    contracts.list_contracts()
    cc.happy_exit()


@click.command(name='show-contract')
@click.argument('txid', nargs=1)
@click.option('--output', '-o',
              default=constants.FORMAT_TEXT,
              type=click.Choice(constants.FORMAT_ALL),
              help=('Format used to print data to the console. Valid options'
                    ' are: ') + str(constants.FORMAT_ALL),
              required=False)
def show_contract(txid, output):
    """Show a single contract, identified by transaction identifier TXID."""
    cc = CliConsole(click.echo, common.print_error,
                    output, click.ClickException,
                    click.confirm, click.prompt)
    lm = LoginManager(cc)
    contracts = Contracts(cc, lm)
    contracts.show_contract(txid)
    cc.happy_exit()


@click.command(name='delete-contracts')
@click.argument('txids', nargs=-1)  # variadic
@click.option('--input-json', '-j',
              default=None,
              type=click.STRING,
              help=('JSON array with TXIDs of contracts to be deleted.'),
              required=False)
@click.option('--input-json-file', '-i',
              default=None,
              type=click.File(mode='r'),
              help=('Path to file containing a JSON array of the TXIDs'
                    ' of the contracts to be deleted.'),
              required=False)
def delete_contracts(txids, input_json, input_json_file):
    """Delete all of the contracts which are identified by their
        transaction IDs being in the argument list TXIDS.

        A list of transaction IDs can be passed as command line arguments:

        \b
        uniquid delete-contracts XXXX YYYY ZZZZ

        The list of transaction IDs of the contracts to be deleted can also
        be expressed in JSON format.  The format of the JSON is:

        \b
        [
            "XXXX", "YYYY", "ZZZZ"
        ]

    If the JSON is passed using the --input-json option, then no line breaks
    should be included.
    """
    if ((input_json is None) == (input_json_file is None) and
            (txids is None or len(txids) == 0)):
        raise click.ClickException(constants.ERR_SINGLE_OPTION)
    cc = CliConsole(click.echo, common.print_error,
                    constants.FORMAT_TEXT, click.ClickException,
                    click.confirm, click.prompt)
    lm = LoginManager(cc)
    contracts = Contracts(cc, lm)
    json_string = input_json
    if input_json_file:
        json_string = input_json_file.read()
    # if user passed one+ arguments, these take priority over a JSON array.
    if(len(txids) > 0):
        txid_list = list()
        for txid in txids:
            txid_list.append(str(txid))
        json_string = json.dumps(txid_list)
    contracts.delete_contract(json_string)
    cc.happy_exit()
