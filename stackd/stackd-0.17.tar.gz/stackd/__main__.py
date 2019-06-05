import sys
import os

from .load_env_files import load_env_files
from .load_compose import load_compose
from .load_hash_versions import load_hash_versions

from .api_shellenv import api_shellenv
from .api_infos import api_infos
from .api_getname import api_getname
from .api_deploy import api_deploy
from .api_rm import api_rm
from .api_ls import api_ls
from .api_ps import api_ps
from .api_help import api_help
from .api_compo import api_compo
from .api_compo_freeze import api_compo_freeze
from .api_pull import api_pull
from .api_getimagelist import api_getimagelist
from .api_printenv import api_printenv
from .api_deploy_with_portainer import api_deploy_with_portainer
from .api_rm_with_portainer import api_rm_with_portainer
from .api_config_prune import api_config_prune

from .printError import printError

CWD = os.getcwd()

ENV_VARS = {}
FILES_ENV = []
FILES_COMPOSE = []

# DEFAULTS
ENV_VARS['STACKD_STACK_NAME'] = os.environ.get('STACKD_STACK_NAME') or os.path.basename(CWD)
ENV_VARS['STACKD_COMPOSE_FILE_BASE'] = os.environ.get('STACKD_COMPOSE_FILE_BASE') or "docker-stack.yml"
ENV_VARS['STACKD_ENV'] = os.environ.get('STACKD_ENV') or ""
ENV_VARS['STACKD_DEPLOY_PULL_CHECK'] = os.environ.get('STACKD_DEPLOY_PULL_CHECK') or "true"
ENV_VARS['STACKD_DEPLOY_WITH_REGISTRY_AUTH'] = os.environ.get('STACKD_DEPLOY_WITH_REGISTRY_AUTH') or "true"
ENV_VARS['STACKD_DEPLOY_PRUNE'] = os.environ.get('STACKD_DEPLOY_PRUNE') or "true"
ENV_VARS['STACKD_DEPLOY_PARAMETERS'] = os.environ.get('STACKD_DEPLOY_PARAMETERS') or ""

main_api = {
  'shellenv': lambda args: api_shellenv(ENV_VARS),
  'infos': lambda args: api_infos(FILES_COMPOSE, FILES_ENV, ENV_VARS),
  'getname': lambda args: api_getname(ENV_VARS),
  'deploy': lambda args: api_deploy(FILES_COMPOSE, ENV_VARS, args),
  'up': lambda args: api_deploy(FILES_COMPOSE, ENV_VARS, args),
  'rm': lambda args: api_rm(ENV_VARS, args),
  'remove': lambda args: api_rm(ENV_VARS, args),
  'ls': lambda args: api_ls(args),
  'ps': lambda args: api_ps(ENV_VARS, args),
  'compo': lambda args: api_compo(FILES_COMPOSE),
  'compo-freeze': lambda args: api_compo_freeze(FILES_COMPOSE),
  'pull': lambda args: api_pull(FILES_COMPOSE),
  'getimagelist': lambda args: api_getimagelist(FILES_COMPOSE),
  'printenv': lambda args: api_printenv(),
  'deploy-with-portainer': lambda args: api_deploy_with_portainer(FILES_COMPOSE, ENV_VARS, args),
  'rm-with-portainer': lambda args: api_rm_with_portainer(FILES_COMPOSE, ENV_VARS, args),
  'config-prune': lambda args: api_config_prune(args[0]),
}

def main():
  args=sys.argv.copy()
  cws=args.pop(0)
  cmd=args.pop(0) if len(args) > 0 else 'help'

  if(cmd=='help' or cmd=='h'):
    api_help()
    sys.exit(0)

  if(cmd not in main_api):
    printError('ERROR: unkown command "stackd ' + cmd + '"')
    api_help()
    sys.exit(1)

  load_env_files(FILES_ENV, ENV_VARS)
  load_compose(FILES_COMPOSE, ENV_VARS)
  load_hash_versions(FILES_COMPOSE, ENV_VARS)

  main_api[cmd](args)

if __name__ == '__main__':
  main()