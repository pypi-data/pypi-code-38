from __future__ import print_function

import json
import os
import subprocess
from tempfile import TemporaryFile

from orchestrate.common import safe_format
from orchestrate.core.exceptions import OrchestrateException
from orchestrate.core.services.base import Service


class KubectlError(OrchestrateException):
  def __init__(self, args, return_code, stdout, stderr):
    super(KubectlError, self).__init__()
    self.args = args
    self.return_code = return_code
    self.stdout = stdout.read()
    self.stderr = stderr.read()

  def __str__(self):
    return safe_format(
      'kubectl command {} failed with exit status {}\n'
      'stdout:\n{}\nstderr:\n{}',
      self.args,
      self.return_code,
      self.stdout,
      self.stderr,
    )

class KubectlService(Service):
  kubectl_command = 'kubectl'

  def __init__(self, services):
    super(KubectlService, self).__init__(services)

  def kubectl_pargs(self, args, decode_json):
    pargs = [self.kubectl_command] + args
    if decode_json:
      pargs += ['-o', 'json']
    return pargs

  def kubectl_env(self):
    assert self.kube_config, "The kubectl service has no kubernetes config"
    env = os.environ.copy()
    env.update(dict(
      KUBECONFIG=self.kube_config,
      PATH=safe_format(
        '{}:{}',
        os.path.expanduser('~/.orchestrate/bin'),
        env.get('PATH', ''),
      ).encode(),
    ))
    return env

  def kubectl(self, args, decode_json):
    pargs = self.kubectl_pargs(args, decode_json)
    env = self.kubectl_env()
    with TemporaryFile('w+') as stdout, TemporaryFile('w+') as stderr:
      ps = subprocess.Popen(pargs, env=env, stdout=stdout, stderr=stderr)
      exit_status = ps.wait()
      stdout.seek(0)
      stderr.seek(0)
      if exit_status != 0:
        raise KubectlError(args, exit_status, stdout, stderr)

      if decode_json:
        return json.load(stdout)
      else:
        return stdout.read()

  @property
  def kube_config(self):
    return self.services.kubernetes_service.kube_config
