import yaml
import hashlib
import re
import os

from .export_env import export_env
from .parse_yaml import parse_yaml

# Immutables (configs, secrets)
version_global_namespace = "STACKD"
def version_file_gethash(file, var_namespace, working_dir):
  if not file:
    return False
  path = os.path.join(working_dir, file)
  if not os.path.exists(file):
    print('Expected file not found: "' + file + '"')
    return False
  with open(path, 'rb') as secret_file:
    version = hashlib.sha1(secret_file.read()).hexdigest()[0:26]
  return version

def version_iter_vars(env_vars, immutable_vars, var_namespace, working_dir):
  for var_key, value in immutable_vars:
    variable = var_key.upper()
    variable, _ = re.subn('[^A-Z0-9_]', '_', variable)
    variable = '_'.join([version_global_namespace,var_namespace,'NAME',variable])
    if('file' in value):
      file = value.get('file')
      file = os.path.expandvars(file) # expand env vars
      version = version_file_gethash(file, var_namespace, working_dir)
      if version:
        immutable_name = '_'.join([ env_vars['STACKD_STACK_NAME'], var_key, version ])
        yield variable, immutable_name

def version_iter_yaml(env_vars, yaml_file, working_dir):
  if 'secrets' in yaml_file:
    yield from version_iter_vars(env_vars, yaml_file['secrets'].items(), 'SECRET', working_dir)

  if 'configs' in yaml_file:
    yield from version_iter_vars(env_vars, yaml_file['configs'].items(), 'CONFIG', working_dir)

# LOAD HASH STACK_CONFIG_NAME_* AND STACKD_SECRET_NAME_*
def load_hash_versions(files_compose=[], env_vars={}):
  for file in files_compose:
    parsed = parse_yaml(file)

    for key, value in version_iter_yaml(env_vars, parsed, '.'):
      env_vars[key] = value

    export_env(env_vars)