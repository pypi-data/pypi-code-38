import yaml
from .docker_compose_config import docker_compose_config

def get_required_images(files_compose=[],force=False):
  images = set([])
  yaml_dump = docker_compose_config(files_compose, no_interpolate=False)
  config = yaml.safe_load(yaml_dump)
  if(config['services']):
    for service_name,service_def in config['services'].items():
      # image = service_def['image']
      if 'image' in service_def:
        images.add(service_def['image'])
  return images
