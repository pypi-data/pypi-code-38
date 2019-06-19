import errno
import glob
import os
import subprocess
import sys

from contextlib import contextmanager
from hashlib import sha256
from zc.buildout.configparser import parse


@contextmanager
def CwdContextManager(path):
  """
  Context Manager for executing code in a given directory.
  There is no need to provide fallback or basic checks
  in this code, as these checkes should exist in the code
  invoking this Context Manager.
  If someone needs to add checks here, I'm pretty sure
  it means that they are trying to hide legitimate errors.
  See tests to see examples of invokation
  """
  old_path = os.getcwd()
  try:
    os.chdir(path)
    yield
  finally:
    os.chdir(old_path)


def getExcludePathList(path):
  excluded_path_list = [
    "*.sock",
    "*.socket",
    "*.pid",
    ".installed*.cfg",
  ]

  def append_relative(path_list):
    for p in path_list:
      p = p.strip()
      if p:
        excluded_path_list.append(os.path.relpath(p, path))

  for partition in glob.glob(os.path.join(path, "instance", "slappart*")):
    if not os.path.isdir(partition):
      continue

    with CwdContextManager(partition):
      try:
        with open("srv/exporter.exclude") as f:
          exclude = f.readlines()
      except IOError as e:
        if e.errno != errno.ENOENT:
          raise
      else:
        append_relative(exclude)
      for installed in glob.glob(".installed*.cfg"):
        try:
          with open(installed) as f:
            installed = parse(f, installed)
        except IOError as e:
          if e.errno != errno.ENOENT:
            raise
        else:
          for section in installed.itervalues():
            append_relative(section.get(
              '__buildout_installed__', '').splitlines())

  return excluded_path_list


def getSlappartSignatureMethodDict():
  slappart_signature_method_dict = {}
  for partition in glob.glob("./instance/slappart*"):
    if os.path.isdir(partition):
      script_path = os.path.join(partition, 'srv', '.backup_identity_script')
      if os.path.exists(script_path):
        slappart_signature_method_dict[partition] = script_path
  return slappart_signature_method_dict


def read_file_by_chunk(path, chunk_size=1024 * 1024):
  with open(path, 'rb') as f:
    chunk = f.read(chunk_size)
    while chunk:
      yield chunk
      chunk = f.read(chunk_size)


def getSha256Sum(file_path_list):
  result_list = []

  for file_path in file_path_list:
    hash_sum = sha256()
    for chunk in read_file_by_chunk(file_path):
      hash_sum.update(chunk)
    result_list.append("%s  %s" % (hash_sum.hexdigest(), file_path))

  return result_list


def writeSignatureFile(slappart_signature_method_dict, runner_working_path, signature_file_path='backup.signature'):
  special_slappart_list = slappart_signature_method_dict.keys()
  signature_list = []

  for dirpath, dirname_list, filename_list in os.walk('.'):
    if dirpath == '.' or not filename_list:
      continue

    # Find if special signature function should be applied
    signature_process = None
    for special_slappart in special_slappart_list:
      backup_identity_script_path = os.path.join(
        runner_working_path,
        slappart_signature_method_dict[special_slappart]
      )

      if dirpath.startswith('./' + os.path.relpath(os.path.join('./runner', special_slappart))):
        signature_process = subprocess.Popen(
          backup_identity_script_path,
          stdin=subprocess.PIPE,
          stdout=subprocess.PIPE,
        )
        break

    # construct list of file path and remove broken symlink
    filepath_list = filter(os.path.isfile, [os.path.join(dirpath, filename) for filename in filename_list])

    if signature_process:
      (output, error_output) = signature_process.communicate(
        '\0'.join(filepath_list)
      )

      if signature_process.returncode != 0:
        print(
          "An issue occured when calculating the custom signature"
          " with %s :\n%s\n%s" % (
            backup_identity_script_path, output, error_output
          )
        )
        sys.exit(1)

      # We have to rstrip as most programs return an empty line
      # at the end of their output
      signature_list.extend(output.strip('\n').split('\n'))
    else:
      signature_list.extend(
        getSha256Sum(filepath_list)
      )

  # Write the signatures in file
  with open(signature_file_path, 'w+') as signature_file:
    signature_file.write("\n".join(sorted(signature_list)))
