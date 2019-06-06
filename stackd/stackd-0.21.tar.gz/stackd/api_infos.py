from .style import style

def api_infos(files_compose, files_env, env_vars):
  print('STACKD ENVIRONMENT 🦊:')
  print('\n'+style.UNDERLINE('stack name:') + ' ' + env_vars['STACKD_STACK_NAME'])

  print('\n'+style.UNDERLINE('.env files:'))
  for file in files_env:
    print(file)

  print('\n'+style.UNDERLINE('compose files:'))
  for file in files_compose:
    print(file)

  print('\n'+style.UNDERLINE('variables:'))

  for key, val in env_vars.items() :
    print(key + '=' + val)
