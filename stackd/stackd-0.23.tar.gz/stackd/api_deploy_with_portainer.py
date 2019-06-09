import sys
from .run_portainer_stack_up import run_portainer_stack_up

def api_deploy_with_portainer(files_compose, env_vars, args=[]):
  enabled_pull_check = strtobool(env_vars['STACKD_DEPLOY_PULL_CHECK'])
  if(enabled_pull_check):
    pull_check_result = pull_check(files_compose, verbose=True)
    if(pull_check_result['error']):
      print("\nError: unable to pull missing required images")
      sys.exit(1)

  process = run_portainer_stack_up(files_compose, env_vars, ['-a','deploy', args])
  if(process.returncode != 0):
      sys.exit(process.returncode)