from .build_stack_compose_file import build_stack_compose_file
from .build_stack_env_file import build_stack_env_file
from .paths import get_bundle_dir

def api_bundle(files_compose, env_vars={}):
  build_stack_compose_file(files_compose, env_vars)
  build_stack_env_file(env_vars)
  print('bundle created in "'+get_bundle_dir()+'"')