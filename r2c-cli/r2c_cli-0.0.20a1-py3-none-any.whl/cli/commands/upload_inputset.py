import json
import os

import click

from r2c.cli.commands.cli import cli
from r2c.cli.logger import get_logger, print_error_exit, print_msg, print_success
from r2c.cli.network import auth_post, get_base_url, handle_request_with_error_message
from r2c.cli.util import set_debug_flag, set_verbose_flag

logger = get_logger()


@cli.command()
@click.argument("input_set_file")
@click.option(
    "--verbose",
    "-v",
    is_flag=True,
    help="Show extra output, error messages, and exception stack traces with INFO filtering",
    default=False,
)
@click.option(
    "--debug",
    "-d",
    is_flag=True,
    help="Show extra output, error messages, and exception stack traces with DEBUG filtering",
    default=False,
    hidden=True,
)
@click.pass_context
def upload_inputset(ctx, input_set_file, verbose, debug):
    """
    Uploads INPUT_SET_FILE to the r2c analysis platform as a custom input set.
    """
    if verbose == True:  # allow passing --verbose to run as well as globally
        set_verbose_flag(ctx, True)
    if debug == True:
        set_debug_flag(ctx, True)
    print_msg(f"Uploading {input_set_file}...")
    with open(input_set_file) as f:
        input_set = json.load(f)
    r = auth_post(f"{get_base_url()}/api/v1/input/", input_set)
    data = handle_request_with_error_message(r)
    print_success("Uploaded new input set successfully")
