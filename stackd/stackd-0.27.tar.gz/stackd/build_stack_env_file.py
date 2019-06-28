from .paths import get_bundle_stack_env_file_path, ensure_build_dir_exists

def build_stack_env_file(env_vars):
  BUILD_STACK_ENV_FILE = get_bundle_stack_env_file_path(env_vars)
  ensure_build_dir_exists()
  f = open(BUILD_STACK_ENV_FILE, 'w+')
  for key, val in env_vars.items() :
    f.write(key + '=' + val + '\n')
  f.close()