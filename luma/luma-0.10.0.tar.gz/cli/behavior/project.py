"""
    This behavior file contains the logic for a subset of commands. Logic specific to
    commands should be implamented in corresponding behavior files.
"""

import pyqrcode as qrc
from cli import pyke
import requests
import urllib3
import click
import json
import os

verify_tls = os.environ.get('LUMA_CLI_VERIFY_TLS', None)
if verify_tls == 'false' or verify_tls == 'False':
  verify_tls = False
  urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
else:
  verify_tls = None

class ProjectBehavior:
  def __init__(self, **kwargs):
    profile = kwargs.get('profile')
    self.util = pyke.Util(profile=profile)
    if profile is not None:
      self.context = pyke.auth.load_cache()

  def read_config(self):
    pass

  def write_config(self):
    pass


  def init(self):
    cs = pyke.Checksum()
    cs.make_tarfile('ignore_config.tar.gz', os.getcwd())
    click.echo(cs.get_checksum(f'{os.getcwd()}/ignore_config.tar.gz'))

  def display_qr(self):
    url = qrc.create('https://google.com')
    url.svg('qr-activation.svg', scale=8)
    click.echo(url.terminal(quiet_zone=2))
