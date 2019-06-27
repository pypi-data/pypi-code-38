"""Misc plugin for VSS CLI (vss-cli)."""
import logging

import click
from vss_cli.cli import pass_context
from vss_cli.config import Configuration


_LOGGING = logging.getLogger(__name__)


@click.group(
    'misc',
    short_help='Miscellaneous utilities.'
)
@pass_context
def cli(ctx):
    """Miscellaneous utilities."""


@cli.command(
    'hash-string',
    short_help='Hashes string using SHA-512'
)
@click.argument(
    'string_to_hash',
    type=click.STRING,
    required=False
)
@pass_context
def misc_hash_string(
        ctx: Configuration, string_to_hash
):
    """Hashes string using SHA-512. If string_to_hash argument
    not provided, input will be prompted. Useful to create hashed
    passwd entries."""
    from pyvss.helper import hash_string
    string_to_hash = string_to_hash or click.prompt(
        'String', show_default=False, hide_input=True,
        confirmation_prompt=True)
    click.echo(
        hash_string(string_to_hash)
    )


@cli.command(
    'gz-b64e',
    short_help='Compresses and encodes a given string'
)
@click.argument(
    'string_gz_encode',
    type=click.STRING,
    required=True
)
@pass_context
def misc_encode_gz(
        ctx: Configuration, string_gz_encode
):
    """Compresses (gz) and encodes in base64 a given string."""
    from pyvss.helper import compress_encode_string
    click.echo(
        compress_encode_string(string_gz_encode)
    )


@cli.command(
    'b64d-gz',
    short_help='Decompress and decodes a given string'
)
@click.argument(
    'string_gz_encoded',
    type=click.STRING, required=True
)
@pass_context
def misc_decodes_ugz(
        ctx: Configuration, string_gz_encoded
):
    """Compresses (gz) and encodes in base64 a given string."""
    from pyvss.helper import decode_uncompress_string
    click.echo(
        decode_uncompress_string(string_gz_encoded)
    )
