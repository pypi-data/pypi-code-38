from libcloud.types import Provider
from libcloud.providers import get_driver
import paramiko
import StringIO

driver_list = {
    'DUMMY': get_driver(Provider.DUMMY),
    'EC2_US_EAST': get_driver(Provider.EC2_US_EAST),
    'EC2_US_WEST': get_driver(Provider.EC2_US_WEST),
    'EC2_EU_WEST': get_driver(Provider.EC2_EU_WEST),
    'RACKSPACE': get_driver(Provider.RACKSPACE),
    'SLICEHOST': get_driver(Provider.SLICEHOST),
    'GOGRID': get_driver(Provider.GOGRID),
    'VPSNET': get_driver(Provider.VPSNET),
    'LINODE': get_driver(Provider.LINODE),
    'VCLOUD': get_driver(Provider.VCLOUD),
    'RIMUHOSTING': get_driver(Provider.RIMUHOSTING),
    'ECP': get_driver(Provider.ECP),
    'IBM': get_driver(Provider.IBM),
    'OPENNEBULA': get_driver(Provider.OPENNEBULA),
    'DREAMHOST': get_driver(Provider.DREAMHOST),
  }
def getDriverInstance(driverName, key, secret=None, secure=True, host=None,
    port=None):
  return driver_list.get(driverName)(key, secret, secure, host, port)

def getSSHConnection(driver, hostname, private_key):
  client = paramiko.SSHClient()
  client.load_system_host_keys()
  client.set_missing_host_key_policy(paramiko.WarningPolicy())
  #TODO if exception : try DSSKey
  pkey = paramiko.RSAKey.from_private_key(StringIO.StringIO(private_key))
  client.connect(hostname=hostname, username='root', pkey=pkey,
        look_for_keys=False)
  return client
  
def getNode(driver, node_uuid):
  node_list = [node for node in driver.list_nodes() if node_uuid in node.uuid]
  if len(node_list) == 0:
    return None
  if len(node_list) != 1:
    raise IndexError('Several nodes with the uuid %r exist.' % node_uuid)
  return node_list[0]
