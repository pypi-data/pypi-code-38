import os

# MAKE DOCKER STACK COMPOSE FILES LIST
def load_compose(files_compose=[],env_vars={}):
  STACKD_COMPOSE_FILE_BASE = env_vars['STACKD_COMPOSE_FILE_BASE']
  env_ls = env_vars['STACKD_ENV'].split(',')
  for compose_file_name in STACKD_COMPOSE_FILE_BASE.split(','):
    compose_base_name = os.path.splitext(compose_file_name)[0]
    files_compose.append(compose_file_name)
    for env_key in env_ls:
      compose_extend_file = compose_base_name + '.' + env_key + '.yml'
      if os.path.exists(compose_extend_file):
        files_compose.append(compose_extend_file)