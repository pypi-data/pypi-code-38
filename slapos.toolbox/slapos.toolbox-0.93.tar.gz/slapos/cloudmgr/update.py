from slapos.cloudmgr.lib import getDriverInstance
import sys
import uuid
from libcloud.types import NodeState

def update(key, secret, service, location, node_uuid=None, ssh_key=None,
    image=None, size=None, security_group=None):
  """Update or create node"""

  if node_uuid is not None:
    driver = getDriverInstance(service, key, secret)
    found_node_list = [node for node in driver.list_nodes() if node.uuid==node_uuid]
    if len(found_node_list) == 0:
      # node_uuid relates to not available one, recreate
      node_uuid = None
    elif len(found_node_list) == 1:
      node = found_node_list[0]
      if node.state not in [NodeState.RUNNING, NodeState.REBOOTING,
        NodeState.PENDING]:
        # node_uuid relates to destroyed one, recreate
        node_uuid = None

  if not node_uuid:
    if not image or not size or not location:
      raise Exception("Node can not be created because of lacking informations")
      # XXX-Cedric : what exception?
    # Creates node
    return install(key, secret, service, image, size, location, security_group)
  else:
    return dict(
      ssh_key = ssh_key,
      node_uuid = node_uuid
    )

def install(key, secret, service, image_id, size_id, location_id,
    security_group):
  driver = getDriverInstance(service, key, secret)
  # Defines a dict that will be used to create our node(s)
  argument_list = dict()
  
  argument_list['image'] = [image for image in driver.list_images() if
      image_id in image.id][0]
  argument_list['size'] = [size for size in driver.list_sizes() if
      size_id in size.id][0]
  # We can create uour own images and sizes
  #image = NodeImage(id=self.options['image_id'],
  #                  name=self.options['image_name'],
  #                  driver=driver)
  #size = NodeSize(self.options['size_id'], self.options['size_name'], None,
  #    None, None, None, driver=driver)
  
  argument_list['location'] = [location for location in
      driver.list_locations() if location_id in location.id][0]
  
  # If we are in ec2 : adding ssh key manually
  if 'EC2' in service:
    try:
      unique_keyname = str(uuid.uuid1())
      keypair = driver.ex_create_keypair(unique_keyname)
      ssh_key = keypair['keyMaterial']
      argument_list['ex_keyname'] = unique_keyname
    except Exception, e:
      # XX-Cedric : what to do here?
      if e.args[0].find("InvalidKeyPair.Duplicate") == -1:
        # XXX-Cedric : our unique key was not so unique...Do something
        raise e
      else:
        raise e
  # Prepares ssh key deployment and/or postflight script
  # NOT IMPLEMENTED
  #if self.options.get('ssh_key') or self.options.get('script'):
  #  deployment_argument_list = []
  #  if self.options.get('ssh_key'):
  #    deployment_argument_list.append(SSHKeyDeployment(
  #        self.options['ssh_key']))
  #  if self.options.get('script'):
  #    script_to_run = ScriptDeployment(self.options['script'])
  #    deployment_argument_list.append(script_to_run)
  #  argument_list['deploy'] = MultiStepDeployment(deployment_argument_list) 

  # If ec2, creates group, adds rules to it.
  if 'EC2' in service:
    try:
      driver.ex_create_security_group(security_group, security_group)
    except Exception, e:
      if e.args[0].find("InvalidPermission.Duplicate") == -1:
        pass #It's okay, don't worry.
    driver.ex_authorize_security_group_permissive(security_group)
    argument_list['ex_securitygroup'] = security_group
          
  # Installs node
  node = driver.create_node(**argument_list)#deploy_node(**argument_list)
  node_uuid = node.uuid
  
  return {'node_uuid': node_uuid, 'ssh_key': ssh_key}

def main():
  try:
    node_uuid = sys.argv[4]
  except IndexError:
    node_uuid = None
  update(sys.argv[1], sys.argv[2], sys.argv[3], node_uuid)
