from update import update
from destroy import destroy
from start import start
from stop import stop
from list import uuidlist
from getpubliciplist import getpubliciplist

class NodeInterface:
  def __init__(self, key, secret, service, location, node_uuid=None,
      ssh_key=None):
    self.key = key
    self.location = location
    self.node_uuid = node_uuid
    self.ssh_key = ssh_key
    self.secret = secret
    self.service = service

  def update(self, image, size, security_group):
    result = update(self.key, self.secret, self.service, self.location,
        self.node_uuid, self.ssh_key, image, size, security_group)
    self.node_uuid = result['node_uuid']
    self.ssh_key = result['ssh_key']
    return result

  def stop(self):
    stop(self.key, self.secret, self.service, self.node_uuid, self.ssh_key)

  def start(self):
    start(self.key, self.secret, self.service, self.node_uuid)

  def destroy(self):
    destroy(self.key, self.secret, self.service, self.node_uuid)

  def getPublicIpList(self):
    return getpubliciplist(self.key, self.secret, self.service, self.node_uuid)

  def getNodeUuidList(self):
    return uuidlist(self.key, self.secret, self.service)
