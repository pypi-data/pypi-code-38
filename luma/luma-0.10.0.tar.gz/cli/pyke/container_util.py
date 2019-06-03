"""
    The primary use of the ContainerUtil class is to connect to and communicate with
    the running docker daemon.
"""

from pathlib import Path
import docker
import shutil
import click
import gzip
import time
import sys
import os

class ContainerUtil:
  def __init__(self):
    try:
      self.client = docker.Client(base_url='unix://var/run/docker.sock')
    except Exception as e:
      raise click.ClickException(click.style("Error communicating with the docker daemon. Are you sure it's running? {}".format(e), fg='red'))

  def save_image(self, image_name):
    image = self.client.get_image(image_name)
    file_path = '{}/{}'.format(str(Path.home()), image_name.replace('/', '_').replace('.', '_').replace(':', '_'))

    with open(file_path, 'w+b') as image_tar:
      image_tar.write(image.data)

    zipped_file_path = self.zip_image(file_path)

    # Cleanup
    os.remove(file_path)

    return zipped_file_path

  def zip_image(self, file_path):
    with open(file_path, 'rb') as f_in:
      with gzip.open('{}.tar.gz'.format(file_path), 'w+b') as f_out:
        shutil.copyfileobj(f_in, f_out)

    return '{}.tar.gz'.format(file_path)
