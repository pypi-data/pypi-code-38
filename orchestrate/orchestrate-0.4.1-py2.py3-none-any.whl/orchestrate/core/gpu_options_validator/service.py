from __future__ import print_function

import six

from orchestrate.common import safe_format
from orchestrate.core.exceptions import PromptFailedException, UnsupportedOptionException
from orchestrate.core.services.base import Service


DEFAULT_CPU_FRAMEWORK = 'python'
DEFAULT_GPU_FRAMEWORK = 'cuda'
FRAMEWORK_OPTION = 'framework'
RESOURCES_OPTION = 'resources_per_model'

def is_gpu_framework(framework):
  return framework != 'python'

def get_confirmation(msg, confirmation_msg='Would you like to continue?'):
  confirmation = ''
  try:
    while confirmation not in ('y', 'n'):
      print(msg)
      confirmation = six.moves.input(safe_format('{} (Y/n):', confirmation_msg)).lower()
  except EOFError:
    raise PromptFailedException(msg)
  else:
    if confirmation == 'n':
      raise PromptFailedException(msg)

class GpuOptionsValidatorService(Service):
  def check_gpu_support(self, gpus, local_run):
    if gpus:
      if local_run:
        raise UnsupportedOptionException(safe_format(
          "Local runs with GPUs are not supported at this time."
          " If you really want to proceed, please add {resources_option}:gpus:0 to your YAML file.",
          resources_option=RESOURCES_OPTION,
        ))
      else:
        self.services.kubernetes_service.check_gpu_nodes(gpus)

  def get_framework_confirmation(self, framework, gpus):
    if not gpus and is_gpu_framework(framework):
      get_confirmation(
        safe_format(
          'You chose {framework_option}:{framework} with {resources_option}:gpus:{gpus}.'
          ' It is recommended that you use GPUs with this {framework_option},',
          ' or choose the {default_cpu_framework} {framework_option}.',
          default_cpu_framework=DEFAULT_CPU_FRAMEWORK,
          framework=framework,
          framework_option=FRAMEWORK_OPTION,
          gpus=gpus,
          resources_option=RESOURCES_OPTION,
        ),
        confirmation_msg=safe_format(
          'Would you like to continue with {framework_option}:{framework}?',
          framework=framework,
          framework_option=FRAMEWORK_OPTION,
        ),
      )
    elif gpus and not is_gpu_framework(framework):
      get_confirmation(
        safe_format(
          'You chose {framework_option}:{framework} with {resources_option}:gpus:{gpus}.'
          ' It is recommended that you use another {framework_option} for GPUs.'
          ' Check out the {framework_option} section of the orchestrate docs: {docs_url}',
          docs_url='https://app.sigopt.com/docs/orchestrate/deep_dive#experiment_config',
          framework=framework,
          framework_option=FRAMEWORK_OPTION,
          gpus=gpus,
          resources_option=RESOURCES_OPTION,
        ),
        confirmation_msg=safe_format(
          'Would you like to continue with {framework_option}:{framework}?',
          framework=framework,
          framework_option=FRAMEWORK_OPTION,
        ),
      )

  def get_framework_and_resource_options(self, orchestrate_options, local_run):
    framework = orchestrate_options.get(FRAMEWORK_OPTION)
    resource_options = orchestrate_options.get(RESOURCES_OPTION, {})
    gpus = resource_options.get('gpus')
    gpus = gpus and int(gpus)
    if framework is None:
      if gpus:
        framework = DEFAULT_GPU_FRAMEWORK
      else:
        framework = DEFAULT_CPU_FRAMEWORK
    else:
      if is_gpu_framework(framework) and gpus is None:
        gpus = 1

    self.check_gpu_support(gpus, local_run)
    self.get_framework_confirmation(framework, gpus)

    if gpus is not None:
      resource_options = resource_options.copy()
      resource_options['gpus'] = gpus
    return framework, resource_options
