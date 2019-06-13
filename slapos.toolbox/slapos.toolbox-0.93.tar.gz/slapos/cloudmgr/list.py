# Original work by Cedric de Saint Martin, adapted by Lukasz Nowak
import sys
from slapos.cloudmgr.lib import getDriverInstance

def nodelist(key, secret, service):
  driver = getDriverInstance(service, key, secret)
  node_list = driver.list_nodes()
  return node_list

def uuidlist(key, secret, service):
  return [q.uuid for q in nodelist(key, secret, service)]

def main():
  node_list = nodelist(*sys.argv[1:])
  print 'Available nodes (%s):' % len(node_list)
  for node in node_list:
    print node
