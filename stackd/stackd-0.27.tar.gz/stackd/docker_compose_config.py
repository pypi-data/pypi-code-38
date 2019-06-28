import sys
import os
import subprocess
import tempfile

from .flatten import flatten
from .style import style
from .printError import printError
from .which import which

def docker_compose_config(files, no_interpolate=True):

  if no_interpolate:

    # require docker-compose 1.25 minimum
    # process = subprocess.run(
    #   flatten([
    #     'docker-compose',
    #     list(map(lambda f: ['-f', f], files)),
    #     'config',
    #     '--no-interpolate'
    #   ]),
    #   universal_newlines=True,
    #   stdout=subprocess.PIPE,
    #   stderr=subprocess.PIPE
    # )

    if not which('docker-compose-merge'):
      printError(
        'docker-compose-merge is required to run this command'
        +' run "npm install -g docker-compose-merge" to install it, more details here: https://gitlab.com/youtopia.earth/bin/docker-compose-merge'
      )
      sys.exit(1)

    process = subprocess.run(
      flatten([
        'docker-compose-merge',
        '-i',
        list(map(lambda f: [f], files))
      ]),
      universal_newlines=True,
      stdout=subprocess.PIPE,
      stderr=subprocess.PIPE
    )

    out = process.stdout

  else:
    if not which('docker-compose'):
      printError(
        'docker-compose is required to run this command'
        +' run "pip install --user docker-compose" to install it, more details here: https://docs.docker.com/compose/install/'
      )
      sys.exit(1)

    process = subprocess.run(
      flatten([
        'docker-compose',
        list(map(lambda f: ['-f', f], files)),
        'config'
      ]),
      universal_newlines=True,
      stdout=subprocess.PIPE,
      stderr=subprocess.PIPE
    )
    out = process.stdout

  stderr = ''
  for line in process.stderr.split('\n') :
     if 'Compose does not support' not in line:
       stderr += line + '\n'
  stderr = stderr.strip()
  if(stderr != ''):
    if(process.returncode != 0):
      error_label = style.RED('ERROR')
    else:
      error_label = style.YELLOW('WARNING')
    sys.stderr.write(error_label+': '+stderr+'\n\n')
    sys.stderr.flush()

  if(process.returncode != 0):
    sys.exit(process.returncode)

  return out