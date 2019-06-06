def api_shellenv(env_vars):
  for env_key in env_vars:
    print('export ' + env_key + '=' + env_vars[env_key])