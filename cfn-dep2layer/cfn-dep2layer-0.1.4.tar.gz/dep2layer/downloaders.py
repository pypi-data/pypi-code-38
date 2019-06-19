import subprocess
import hashlib
import os
import shutil
import json


class PackagerBase:
  image = None
  _rundir = None # Need "run.sh" in this dir
  prefix = None
  depfiles = []
  
  def __init__(self, resource, basedir):
    self.resource = resource
    self.basedir = basedir
    self.hash = None
  
  def isdepfilesexists(self):
    for f in self.depfiles:
      if not os.path.isfile(os.path.join(self.basedir, self.resource['Properties']['CodeUri'], f)):
        return False
    return True
    
  def getdeplist(self):
    pass
    
  @property
  def rundir(self):
    return os.path.abspath(os.path.join(os.path.realpath(__file__), '..', self._rundir))
    
  
    
  def gethash(self):
    if self.hash is None:
      sha = hashlib.sha256()
      sha.update('|'.join(self.getdeplist()).encode('utf8'))
      self.hash = sha.hexdigest()
    return self.hash
  
  def package(self, tempdir):
    # Copy code to temp dir to share with Docker VM
    runtempdir = os.path.join(tempdir, '.packager')
    shutil.copytree(self.rundir, runtempdir)
    
    commands = [ 'docker', 'run', '--rm', '--entrypoint', '', \
      '-v', '{}:/var/task/packager:ro'.format(runtempdir), \
      '-v', '{}:/var/task/src:ro'.format(os.path.join(self.basedir, self.resource['Properties']['CodeUri'])), \
      '-v', '{}:/tmp'.format(tempdir), \
      self.image, 'bash', '/var/task/packager/run.sh']
    
    print('Run command:', commands)
    proc = subprocess.Popen(commands)
    proc.wait()
    
    shutil.rmtree(runtempdir)
    
    return proc.returncode == 0

class Python37Packager(PackagerBase):
  image = 'lambci/lambda:python3.7'
  _rundir = 'python'
  prefix = 'Python37'
  depfiles = ['requirements.txt']
  
  def getdeplist(self):
    requirementpath = os.path.join(self.basedir, self.resource['Properties']['CodeUri'], 'requirements.txt')
    deplist = [i.strip() for i in open(requirementpath).readlines()]
    deplist.sort()
    return deplist

class Python36Packager(Python37Packager):
  image = 'lambci/lambda:python3.6'
  prefix = 'Python36'

class Python27Packager(Python37Packager):
  image = 'python:2.7' #There is no pip command in lambci/lambda:python2.7
  prefix = 'Python27'
  

class NodeJS810Packager(PackagerBase):
  image = 'lambci/lambda:nodejs8.10'
  _rundir = 'nodejs'
  prefix = 'NodeJS810'
  depfiles = ['package.json']
  
  def getdeplist(self):
    packagepath = os.path.join(self.basedir, self.resource['Properties']['CodeUri'], 'package.json')
    depmap = json.load(open(packagepath)).get('dependencies', {})
    deplist = ['{}:{}'.format(k, v) for k, v in depmap.items()]
    deplist.sort()
    
    lockpath = os.path.join(self.basedir, self.resource['Properties']['CodeUri'], 'package-lock.json')
    if os.path.isfile(lockpath):
      lockmap = json.load(open(lockpath)).get('dependencies', {})
      locklist =  ['{}:{}'.format(k, v.get('version', [])) for k, v in lockmap.items()]
      locklist.sort()
      deplist = deplist + ['==package-lock=='] + locklist
      
    return deplist
    

class NodeJS610Packager(NodeJS810Packager):
  image = 'lambci/lambda:nodejs6.10'
  _rundir = 'nodejs'
  prefix = 'NodeJS610'

cls = {
  'python3.7': Python37Packager,
  'python3.6': Python36Packager,
  'python2.7': Python27Packager,
  'nodejs8.10': NodeJS810Packager,
  'nodejs6.10': NodeJS610Packager,
}