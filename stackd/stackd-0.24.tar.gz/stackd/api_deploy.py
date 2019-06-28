import sys
from distutils.util import strtobool
from .pull_check import pull_check
from .run_shell import run_shell

def api_deploy(files_compose=[], env_vars={}, args=[]):
  enabled_pull_check = strtobool(env_vars['STACKD_DEPLOY_PULL_CHECK'])
  if(enabled_pull_check):
    pull_check_result = pull_check(files_compose, verbose=True)
    if(pull_check_result['error']):
      print("\nError: unable to pull missing required images")
      sys.exit(1)

  parameters = env_vars['STACKD_DEPLOY_PARAMETERS']
  prune = strtobool(env_vars['STACKD_DEPLOY_PRUNE'])
  if(prune):
    parameters += " --prune"
  regauth = strtobool(env_vars['STACKD_DEPLOY_WITH_REGISTRY_AUTH'])
  if(regauth):
    parameters += " --with-registry-auth"

  process = run_shell([
    'docker','stack','deploy',
    parameters,
    list(map(lambda c: ['-c' ,c], files_compose)),
    env_vars['STACKD_STACK_NAME'],
    args,
  ])
  if(process.returncode != 0):
    sys.exit(process.returncode)
