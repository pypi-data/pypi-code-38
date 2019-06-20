from pathlib import Path

import click

from .api import (sc_export_pub_key_pem, sc_export_x509_pem, sc_is_present,
                  sc_session, sc_sign_rsa_pkcs_pss_sha256)
from .exceptions import SmartCardError


@click.group()
def oll_sc():
  """oll-sc tool CLI"""


@oll_sc.command()
@click.argument('key_id', type=int)
@click.argument('pin')
@click.option('--output-path', '-o', type=click.Path(), default=None,
              help='The output file path to write public key pem to.')
def public_key(key_id, pin, output_path=None):
  """Extract public key from smart card in PEM format."""
  try:
    pub_key_pem_bytes = sc_export_pub_key_pem((key_id,), pin)
    pub_key_pem = pub_key_pem_bytes.decode('utf-8')

    if output_path:
      with open(output_path, 'w') as out:
        out.write(pub_key_pem)
    else:
      click.echo(pub_key_pem)

  except SmartCardError as e:
    click.echo(e)


@oll_sc.command()
def inserted():
  """Check if smart card is inserted."""
  if sc_is_present():
    click.echo('Smart card is inserted.')
  else:
    click.echo('Smart card is not inserted.')


@oll_sc.command()
@click.argument('pin')
def check_pin(pin):
  """Check smart card PIN."""
  try:
    with sc_session(pin):
      pass
    click.echo('PIN OK.')
  except SmartCardError as e:
    click.echo(e)


@oll_sc.command()
@click.argument('key_id', type=int)
@click.argument('pin')
@click.option('--input-path', '-i', type=click.Path(), default=None,
              help='Path of a file to sign.')
@click.option('--input-data', '-d', type=str, default=None,
              help='Data to sign.')
@click.option('--output-path', '-o', type=click.Path(), default=None,
              help='Path of a file to write signature to.')
def sign_rsa_pkcs_pss_sha256(key_id, pin, input_path, input_data, output_path):
  """Sign input using SHA256_RSA_PKCS_PSS mechanism."""
  # Input path overrides input data
  if input_path is not None:
    input_path = Path(input_path)
    if input_path.is_file():
      input_data = input_path.read_bytes()

  if input_data is None:
    click.echo('\nError: Missing option "--input-data" or "--input-path".')
    return

  try:
    signature = sc_sign_rsa_pkcs_pss_sha256(input_data, (key_id,), pin)

    if output_path:
      with open(output_path, 'wb') as out:
        out.write(signature)
    else:
      click.echo(signature)

  except SmartCardError as e:
    click.echo(e)


@oll_sc.command()
@click.argument('key_id', type=int)
@click.argument('pin')
@click.option('--output-path', '-o', type=click.Path(), default=None,
              help='The output file path to write public key pem to.')
def x509(key_id, pin, output_path=None):
  """Extract x509 certificate from smart card in PEM format."""
  try:
    x509_cert_bytes = sc_export_x509_pem((key_id,), pin)
    x509_cert = x509_cert_bytes.decode('utf-8')

    if output_path:
      with open(output_path, 'w') as out:
        out.write(x509_cert)
    else:
      click.echo(x509_cert)

  except SmartCardError as e:
    click.echo(e)
