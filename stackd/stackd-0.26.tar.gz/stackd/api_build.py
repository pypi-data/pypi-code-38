import sys
from .run_shell import run_shell

def api_build(files_build_compose=[], env_vars={}, args=[]):
  parameters = env_vars['STACKD_BUILD_PARAMETERS']
  process = run_shell([
    'docker-compose',
    list(map(lambda c: ['-f' ,c], files_build_compose)),
    parameters,
    'build',
    args,
  ])
  if(process.returncode != 0):
    sys.exit(process.returncode)