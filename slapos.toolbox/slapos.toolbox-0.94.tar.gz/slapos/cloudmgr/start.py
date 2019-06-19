from slapos.cloudmgr.lib import getDriverInstance, getNode
import sys
def start(key, secret, service, node_uuid):
  """Starts node"""
  driver = getDriverInstance(service, key, secret)
  node = getNode(driver, node_uuid)
  if node is None:
    return False
  if node.state in [0, 1]:
    return True
  elif node.state == 3:
    return node.reboot()
  else:
    return False
  return True

def main():
  print start(sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4])
