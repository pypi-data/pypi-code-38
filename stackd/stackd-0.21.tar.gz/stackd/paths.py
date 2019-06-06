import os

def get_build_dir():
  return 'build'

def get_build_stack_compose_file_path(env_vars):
  return get_build_dir() + '/' + env_vars['STACKD_STACK_NAME'] + '.stack.yml'

def get_build_stack_env_file_path(env_vars):
  return get_build_dir() + '/' + env_vars['STACKD_STACK_NAME'] + '.env'

def ensure_build_dir_exists():
  build_dir = get_build_dir()
  if not os.path.exists(build_dir):
    os.makedirs(build_dir)