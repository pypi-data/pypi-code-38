import json
import os
import shutil

from orchestrate.common import TemporaryDirectory, safe_format
from orchestrate.core.lib.types import *
from orchestrate.core.services.base import Service
from orchestrate.version import DOCKER_IMAGE_VERSION


LANGUAGE_MAP = {
  'python3.6': 'python3.6',
  'python3': 'python3.6',
  'python2.7': 'python2.7',
  'python2': 'python2.7',
  'python': 'python2.7',
}
PYTHON_VERSION_MAP = {
  'python3.6': '3.6',
  'python2.7': '2.7',
}
FRAMEWORK_MAP = {
  'python': 'python',
  'cuda': 'cuda-9.0',
  'tensorflow': 'tensorflow-gpu',
  'theano': 'theano-gpu',
  'keras': 'keras-gpu',
  'pytorch': 'pytorch-gpu',
  'mxnet': 'mxnet-gpu',
}
SUPPORTED_LANGUAGES = sorted(set(LANGUAGE_MAP.values()))

def sanitize_command(cmd):
  return '' if cmd is None else str(cmd)

def sanitize_command_str_or_list(cmds):
  if cmds:
    return [sanitize_command(cmd) for cmd in cmds] if is_sequence(cmds) else [sanitize_command(cmds)]
  else:
    return []

class ModelPackerService(Service):
  def build_image(
    self,
    repository,
    tag,
    directory,
    install_commands,
    run_command,
    optimization_options,
    language,
    framework,
    pythonpath,
    quiet=False,
  ):
    if not run_command:
      raise Exception(safe_format(
        "Please specify run commands in the `run` section of your experiment configuration file."
      ))
    actual_language = LANGUAGE_MAP.get(language or 'python')
    actual_framework = framework or 'python'
    if actual_language is None:
      raise Exception(safe_format(
        "The language {} is not currently supported by orchestrate. Supported languages are {}.",
        language,
        ", ".join(SUPPORTED_LANGUAGES),
      ))
    python_version = PYTHON_VERSION_MAP[actual_language]
    base_image = safe_format(
      'orchestrate/{}-{}:{}',
      FRAMEWORK_MAP[actual_framework],
      python_version,
      DOCKER_IMAGE_VERSION,
    )

    with TemporaryDirectory() as root_dirname:
      source_directory = directory
      destination_directory = os.path.join(root_dirname, 'orchestrate')
      bin_dirname = os.path.join(root_dirname, 'bin')
      etc_dirname = os.path.join(root_dirname, 'etc', 'orchestrate')
      var_dirname = os.path.join(root_dirname, 'var', 'orchestrate')
      shutil.copytree(source_directory, destination_directory)
      for dirname in (bin_dirname, etc_dirname, var_dirname):
        os.makedirs(dirname)

      config = {
        'run_command': sanitize_command_str_or_list(run_command),
      }
      with open(os.path.join(etc_dirname, 'config.json'), 'w') as config_fp:
        json.dump(config, config_fp)

      return self.services.docker_service.build(
        tag=self.services.docker_service.format_image_name(repository, tag),
        directory=root_dirname,
        dockerfile_contents=self.services.template_service.render_template_from_file(
          'model_packer/Dockerfile.ms',
          dict(
            base_image=base_image,
            install_commands=sanitize_command_str_or_list(install_commands),
            pythonpath=pythonpath,
          ),
        ),
        quiet=quiet,
        show_all_logs=True,
      )
