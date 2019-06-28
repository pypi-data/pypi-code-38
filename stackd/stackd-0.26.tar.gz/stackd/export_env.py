import os

def export_env(env_vars):
  for key, val in env_vars.items() :
    os.environ[key] = val