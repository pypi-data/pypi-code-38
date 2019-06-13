from slapos.cloudmgr.lib import getDriverInstance, getNode
from libcloud.types import NodeState
import sys
def destroy(key, secret, service, node_uuid):
  driver = getDriverInstance(service, key, secret)
  node = getNode(driver, node_uuid)
  if node is None:
    return False
  if node.state in [NodeState.RUNNING, NodeState.REBOOTING, NodeState.PENDING]:
    return node.destroy()
  else:
    return False

def main():
  print destroy(sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4])
