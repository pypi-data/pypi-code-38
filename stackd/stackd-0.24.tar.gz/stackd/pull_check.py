import subprocess
from .run_shell import run_shell
from .get_required_images import get_required_images
from .pull_check_display_result import pull_check_display_result

def pull_check(files_compose=[], force=False, verbose=False):
  required_images = get_required_images(files_compose)
  images = {}
  error = False
  for image in required_images:
    image_id = subprocess.check_output([
      'docker','image','ls','-q',
      '--filter','reference='+image
    ]).decode("utf-8").strip()
    if(image_id and not force):
      images[image] = 'ok'
    else:
      print('Pulling required image: "' + image + '"')
      process = run_shell(['docker', 'pull', image])
      if(process.returncode != 0):
        images[image] = 'error'
        error = True
      else:
          images[image] = 'pulled'

  result = {}
  result['images'] = images
  result['error'] = error

  if(verbose):
    pull_check_display_result(result)
  return result