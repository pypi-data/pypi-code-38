import sys
from .run_portainer_stack_up import run_portainer_stack_up

def api_rm_with_portainer(files_compose, env_vars, args=[]):
  process = run_portainer_stack_up(files_compose, env_vars, ['-a','undeploy', args])
  if(process.returncode != 0):
      sys.exit(process.returncode)