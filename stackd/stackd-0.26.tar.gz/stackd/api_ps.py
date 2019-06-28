import sys
from .run_shell import run_shell

def api_ps(env_vars, args=[]):
  process = run_shell(['docker','stack','ps',env_vars['STACKD_STACK_NAME'],args])
  if(process.returncode != 0):
      sys.exit(process.returncode)
