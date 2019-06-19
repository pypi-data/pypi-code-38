from __future__ import print_function

import argparse
import subprocess

from .runner_utils import *

def parsePostNotificationRunArgumentList():
  parser = argparse.ArgumentParser()
  parser.add_argument('--srv-path', required=True)
  parser.add_argument('--backup-path', required=True)
  parser.add_argument('--diff-file', required=True)
  parser.add_argument('--proof-signature-file', required=True)

  return parser.parse_args()

def postNotificationRun():
  args = parsePostNotificationRunArgumentList()

  runner_working_path = os.path.join(args.srv_path, 'runner')

  with CwdContextManager(runner_working_path):
    slappart_signature_method_dict = getSlappartSignatureMethodDict()

  with CwdContextManager(args.backup_path):
    writeSignatureFile(slappart_signature_method_dict, runner_working_path, args.proof_signature_file)

    try:
      diff_output = subprocess.check_output(['diff',  '-ruw', 'backup.signature', args.proof_signature_file])
    except subprocess.CalledProcessError as e:
      diff_output = e.output
    finally:
      with open(args.diff_file, 'w') as f:
        f.write(diff_output)
