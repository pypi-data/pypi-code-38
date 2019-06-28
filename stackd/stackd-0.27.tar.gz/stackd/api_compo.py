from .docker_compose_config import docker_compose_config

def api_compo(files_compose):
  out = docker_compose_config(files_compose, no_interpolate=True)
  print(out)