import os
import shlex
import subprocess
from .export_env import export_env

def load_env_file(file, files_env=[], env_vars={}):
  if os.path.exists(file):
    files_env.append(file)

    is_x =  os.access(file, os.X_OK)

    if is_x:
      command = shlex.split("bash -c 'set -o allexport && source "+ file +" && set +o allexport && env'")
      proc = subprocess.Popen(command, stdout = subprocess.PIPE, env=env_vars)
      lines = proc.stdout
      for line in lines:
        line = line.decode('utf-8').strip()
        key, val = line.split('=', 1)
        if key in ['_','SHLVL','PWD']:
          continue
        env_vars[key]=val
    else:
      with open(file, 'r') as content_file:
        content = content_file.read()
      lines=content.splitlines()
      for line in lines:
        line = line.strip()
        if line == '' or line[0:1] == '#':
          continue
        key, val = line.split('=', 1)
        val = os.path.expandvars(val) # expand env vars
        env_vars[key]=val

    export_env(env_vars)