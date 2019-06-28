import os

from jinja2 import Environment, FileSystemLoader, StrictUndefined

from .paths import get_bundle_j2_compose_file_path, ensure_build_dir_exists
from .get_template import get_template


def build_j2yml(name, env_vars={}, vars_data={}):
  j2 = name + '.j2.yml'
  template = get_template(j2)

  buildj2 = get_bundle_j2_compose_file_path(env_vars, name)

  rendered = template.render(vars_data)
  ensure_build_dir_exists()
  with open(buildj2, "w") as fh:
    fh.write(rendered)


def add_compose_file(name, files_compose=[], env_vars={}, files_compose_src=[], vars_data={}):
  file = name + '.yml'
  file_j2 = name + '.j2.yml'
  if os.path.exists(file):
    files_compose.append(file)
    files_compose_src.append(file)
  elif os.path.exists(file_j2):
    build_j2yml(name, env_vars, vars_data)
    file = get_bundle_j2_compose_file_path(env_vars, name)
    files_compose.append(file)
    files_compose_src.append(file_j2)
  return files_compose

# MAKE DOCKER STACK COMPOSE FILES LIST AND COMPILE JINJA TEMPLATES
def load_compose(
    files_compose=[],
    files_build_compose=[],
    env_vars={},
    files_compose_src=[],
    files_build_compose_src=[],
    vars_data={}
  ):

  file_base = env_vars['STACKD_COMPOSE_FILE_BASE']
  load_compose_files(
    file_base,
    files_compose,
    env_vars,
    files_compose_src,
    vars_data
  )

  file_build_base = env_vars['STACKD_BUILD_COMPOSE_FILE_BASE']
  load_compose_files(
    file_build_base,
    files_build_compose,
    env_vars,
    files_build_compose_src,
    vars_data
  )

def load_compose_files(
    file_base,
    files_compose=[],
    env_vars={},
    files_compose_src=[],
    vars_data={}
  ):
  env_ls = env_vars['STACKD_ENV'].split(',')
  for compose_file_name in file_base.split(','):
    compose_base_name = os.path.splitext(compose_file_name)[0]
    add_compose_file(compose_base_name, files_compose, env_vars, files_compose_src, vars_data)
    for env_key in env_ls:
      add_compose_file(compose_base_name + '.' + env_key, files_compose, env_vars, files_compose_src, vars_data)

