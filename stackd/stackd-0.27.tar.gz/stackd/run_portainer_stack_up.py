import os
from .build_stack_compose_file import build_stack_compose_file
from .build_stack_env_file import build_stack_env_file
from .paths import get_bundle_stack_compose_file_path, get_bundle_stack_env_file_path
from .run_shell import run_shell

psu_path = 'portainer-stack-up'
# os.environ['PATH'] = os.environ['PATH'] + ':~/.local/bin'
os.environ['PATH'] = os.environ['PATH'] + ':' + os.environ['HOME'] + '/.local/bin'

def run_portainer_stack_up(files_compose, env_vars, args):
  env = os.environ.copy()

  build_stack_compose_file(files_compose, env_vars)
  build_stack_env_file(env_vars)

  env['PORTAINER_STACK_NAME'] = env_vars['STACKD_STACK_NAME']
  env['DOCKER_COMPOSE_FILE'] = get_bundle_stack_compose_file_path(env_vars)
  env['ENVIRONMENT_VARIABLES_FILE'] = get_bundle_stack_env_file_path(env_vars)
  env['HTTPIE_VERIFY_SSL'] = os.environ.get('HTTPIE_VERIFY_SSL') or 'no'
  env['VERBOSE_MODE'] = os.environ.get('VERBOSE_MODE') or 'true'
  env['PORTAINER_USER'] = os.environ.get('PORTAINER_USER') or 'admin'
  env['PORTAINER_PASSWORD'] = os.environ.get('PORTAINER_PASSWORD') or 'admin'
  env['PORTAINER_URL'] = os.environ.get('PORTAINER_URL') or 'http://localhost'

  process = run_shell([psu_path, args], env=env)
  return process
