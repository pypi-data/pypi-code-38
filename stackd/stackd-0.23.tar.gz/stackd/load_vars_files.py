import os

def load_vars_files(files_vars=[], env_vars={}):
  STACKD_VARS_FILE_BASE = env_vars['STACKD_VARS_FILE_BASE']
  env_ls = env_vars['STACKD_ENV'].split(',')
  for file_name in STACKD_VARS_FILE_BASE.split(','):
    base_name = os.path.splitext(file_name)[0]
    default_name = base_name + '.default.yml'
    if os.path.exists(default_name):
      files_vars.append(default_name)
    if os.path.exists(file_name):
      files_vars.append(file_name)
    for env_key in env_ls:
      file = base_name + '.' + env_key + '.yml'
      if os.path.exists(file):
        files_vars.append(file)
  return files_vars