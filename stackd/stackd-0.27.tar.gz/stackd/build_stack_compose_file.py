from .docker_compose_config import docker_compose_config
from .paths import ensure_build_dir_exists, get_bundle_stack_compose_file_path

def build_stack_compose_file(files_compose, env_vars):
  yaml_dump = docker_compose_config(files_compose, no_interpolate=True)
  BUILD_STACK_COMPOSE_FILE = get_bundle_stack_compose_file_path(env_vars)
  ensure_build_dir_exists()
  f = open(BUILD_STACK_COMPOSE_FILE, 'w+')
  f.write(yaml_dump)
  f.close()