from getprivatekey import getprivatekey
from libcloud.types import NodeState
from slapos.cloudmgr.lib import getDriverInstance, getSSHConnection, getNode
from paramiko import SSHException
import sys

def stop(key, secret, service, node_uuid, ssh_key=None):
  """Stops node"""
  driver = getDriverInstance(service, key, secret)
  node = getNode(driver, node_uuid)
  # Checks state
  if node.state not in [NodeState.RUNNING, NodeState.REBOOTING,
      NodeState.PENDING]:
    return False
  # Good state : connects
  if ssh_key is None:
    ssh_key = getprivatekey(key, secret, service, node_uuid)
  public_ip = node.public_ip[0]
  if not public_ip:
    raise Exception('Node is started but has no IP.')
  try:
    ssh = getSSHConnection(driver, public_ip, ssh_key)
    print('Stopping instance...')
    stdin, stdout, stderr = ssh.exec_command('halt')
  except SSHException, e:
    print('unable to stop')
    raise e
  error_log = stderr.read()
  if error_log:
    raise Exception('''Unable to stop : error log is : 
%r
output is : %r''' % (error_log, stdout.read()))
  return True

def main():
  print stop(sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4])
