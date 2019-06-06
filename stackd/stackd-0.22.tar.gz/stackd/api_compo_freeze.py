from .docker_compose_config import docker_compose_config

def api_compo_freeze(files_compose):
  out = docker_compose_config(files_compose, no_interpolate=False)
  print(out)