import sys

# import pprint
import yaml

from .style import style

def api_infos(files_compose, files_build_compose, files_env, env_vars, files_compose_src, files_build_compose_src, files_vars, vars_data):
  print('STACKD ENVIRONMENT 🦊:')
  print('\n'+style.UNDERLINE('stack name:') + ' ' + env_vars['STACKD_STACK_NAME'])

  print('\n'+style.UNDERLINE('.env files:'))
  for file in files_env:
    print(file)

  print('\n'+style.UNDERLINE('vars files:'))
  for file in files_vars:
    print(file)

  print('\n'+style.UNDERLINE('stack compose files:'))
  i = 0
  for file in files_compose_src:
    print(file+' ('+files_compose[i]+')')
    i = i+1

  print('\n'+style.UNDERLINE('build compose files:'))
  i = 0
  for file in files_build_compose_src:
    print(file+' ('+files_build_compose[i]+')')
    i = i+1

  print('\n'+style.UNDERLINE('jinja variables:'))
  # pp = pprint.PrettyPrinter(indent=2)
  # pp.pprint(vars_data)
  yaml.safe_dump(vars_data, sys.stdout, default_flow_style=False, indent=2)

  print('\n'+style.UNDERLINE('env variables:'))
  for key, val in env_vars.items() :
    print(key + '=' + val)
