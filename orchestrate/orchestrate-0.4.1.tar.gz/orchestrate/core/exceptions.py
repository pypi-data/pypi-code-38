from __future__ import print_function

from orchestrate.common import safe_format


class OrchestrateException(Exception):
  pass

class CheckExecutableError(OrchestrateException):
  pass

class CheckConnectionError(OrchestrateException):
  pass

class AwsClusterSharePermissionError(OrchestrateException):
  pass

class AwsPermissionsError(OrchestrateException):
  def __init__(self, error):
    super(AwsPermissionsError, self).__init__(safe_format(
      "Looks like you have encountered the below AWS permissions error."
      " Please check out our documentation and ensure you have granted yourself the correct AWS permissions"
      " to use SigOpt Orchestrate:"
      " https://app.sigopt.com/docs/orchestrate/deep_dive#aws_permissions"
      "\n\n{}",
      str(error),
    ))

class UnsupportedOptionException(OrchestrateException):
  pass

class MissingGpuNodesException(OrchestrateException):
  pass

class PromptFailedException(OrchestrateException):
  pass

class ModelPackingError(OrchestrateException):
  def __init__(self, error_str, dockerfile):
    super(ModelPackingError, self).__init__(safe_format(
      '{}\nDockerfile: {}\nIf you suspect that you are out of space, run `sigopt clean` and try again.',
      error_str,
      dockerfile,
    ))

class ClusterDestroyError(OrchestrateException):
  def __init__(self, exc_stacktraces):
    print('The following exceptions occurred during cluster destroy:\n')
    for e in exc_stacktraces:
      print(e[1])
    super(ClusterDestroyError, self).__init__()

class NodesNotReadyError(OrchestrateException):
  pass

class FileAlreadyExistsError(OrchestrateException):
  def __init__(self, filename):
    self.filename = filename

    super(FileAlreadyExistsError, self).__init__(safe_format(
      'We are attempting to write a file, but it already exists on your system: {}.'
      ' Please delete the file and try your request again.',
      filename,
    ))
