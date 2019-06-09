import os
from distutils.util import strtobool
import glob

from jinja2 import Environment, FileSystemLoader, StrictUndefined

def filter_env(key, default_value=None):
  return os.getenv(key, default_value)

def filter_bool(str):
  return strtobool(str) == 1

def filter_fileglob(pathname):
  return glob.glob(pathname)

def get_template(template_file_name):
  jinja = Environment(loader=FileSystemLoader("."), undefined=StrictUndefined)
  jinja.filters['env'] = filter_env
  jinja.filters['fileglob'] = filter_fileglob
  jinja.filters['bool'] = filter_bool
  return jinja.get_template(template_file_name)