from slapos.cloudmgr.lib import getDriverInstance, getNode
from libcloud.types import NodeState
import time
import sys

def getpubliciplist(key, secret, service, node_uuid):
  """Gets public ip(s), can wait for the first IP to appear"""
  public_ip_list = []
  for i in range(100):
    driver = getDriverInstance(service, key, secret)
    node = getNode(driver, node_uuid)
    if node.state not in [NodeState.RUNNING, NodeState.REBOOTING,
        NodeState.PENDING]:
      break
    if node.public_ip[0]:
      public_ip_list = node.public_ip
      break
    else:
      time.sleep(5)

  return dict(
    public_ip_list = public_ip_list
  )

def main():
  print getpubliciplist(sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4])
