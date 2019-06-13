import sys
import time
from cloudinterface import NodeInterface

class CloudManager:
  def __init__(self, configuration_file):
    self.configuration_file = configuration_file
    self.initialiseConfiguration()

  def initialiseConfiguration(self):
    self.configuration_dict = {}
    try:
      external_eval = file(self.configuration_file).read()
    except IOError:
      pass
    else:
      try:
        self.configuration_dict = eval(external_eval)
      except:
        pass

    if type(self.configuration_dict) != type({}):
      self.configuration_dict = {}
    for k in 'key', 'secret':
      if k not in self.configuration_dict:
        self.configuration_dict[k] = ''
      elif type(self.configuration_dict[k]) != type(''):
        self.configuration_dict[k] = ''
    if 'node_list' not in self.configuration_dict:
      self.configuration_dict['node_list'] = []
    if type(self.configuration_dict['node_list']) != type([]):
      self.configuration_dict['node_list'] = []

  def run(self):
    print 'Run begin...'
    started = stopped = destroyed = unsupported = 0
    self.key = self.configuration_dict['key']
    self.secret = self.configuration_dict['secret']
    for node in self.configuration_dict['node_list']:
      node_object = NodeInterface(self.key, self.secret, node['service'],
          node['location'], node['node_uuid'], node['ssh_key'])
      if node['requested_state'] == 'started':
        print 'Starting %r' % node['node_uuid']
        if node_object.start():
          started += 1
        else:
          unsupported += 1
      elif node['requested_state'] == 'stopped':
        print 'Stopping %r' % node['node_uuid']
        if node_object.stop():
          stopped += 1
        else:
          unsupported += 1
      elif node['requested_state'] == 'destroyed':
        print 'Destroying %r' % node['node_uuid']
        if node_object.destroy():
          destroyed +=1
        else:
          unsupported += 1
      else:
        print 'Unsupported state %r for node %r' % (node['requested_state'],
            node['node_uuid'])
        unsupported += 1
    print 'Run finished', dict(started=started, stopped=stopped,
        destroyed=destroyed, unsupported=unsupported)


def main():
  while True:
    CloudManager(sys.argv[1]).run()
    time.sleep(5)
