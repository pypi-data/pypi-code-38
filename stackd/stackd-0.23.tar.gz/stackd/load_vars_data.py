import os

import yaml

from .get_template import get_template

def load_vars_data(files_vars, vars_data={}):
  for file in files_vars:
    if os.path.isfile(file):
      template = get_template(file)
      str = template.render(vars_data)
      data = yaml.safe_load(str)
      vars_data.update(data)
  return vars_data
