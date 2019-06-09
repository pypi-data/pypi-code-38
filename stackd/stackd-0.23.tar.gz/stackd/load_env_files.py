from .load_env_file import load_env_file

def load_env_files(files_env = [], env_vars={}):
  load_env_file('.env.default', files_env, env_vars)
  load_env_file('.env', files_env, env_vars)
  env_ls = env_vars['STACKD_ENV'].split(',')
  for env_key in env_ls:
    load_env_file('.env.' + env_key, files_env, env_vars)
  return files_env