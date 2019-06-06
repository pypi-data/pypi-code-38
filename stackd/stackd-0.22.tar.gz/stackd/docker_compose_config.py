import sys
import os
import subprocess
import tempfile

from .flatten import flatten
from .style import style
from .printError import printError

def docker_compose_config(files, no_interpolate=True):

  if no_interpolate:

    # uncomment when docker-compose 1.25 will be released
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
    # out = process.stdout

    # remove the following block when docker-compose 1.25 will be released
    escaped_files = []
    for f in files:
      tmpfile = tempfile.NamedTemporaryFile(delete=False)
      escaped_files.append(tmpfile)
      out = subprocess.check_output(['sed', 's/\$/\$\$/g', f]).decode("utf-8")
      # print(out)
      tmpfile.write(out.encode())
      tmpfile.close()

    cmd = flatten([
      'docker-compose',
      list(map(lambda f: ['-f', f.name], escaped_files)),
      'config'
    ])
    process = subprocess.run(
      cmd,
      universal_newlines=True,
      stdout=subprocess.PIPE,
      stderr=subprocess.PIPE
    )

    for f in escaped_files:
      os.unlink(f.name)

    tmpfile = tempfile.NamedTemporaryFile(delete=False)
    tmpfile.write(process.stdout.encode())
    tmpfile.close()

    out = subprocess.check_output(['sed', 's/\$\$/\$/g', tmpfile.name]).decode("utf-8")
    os.unlink(tmpfile.name)

  else:
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