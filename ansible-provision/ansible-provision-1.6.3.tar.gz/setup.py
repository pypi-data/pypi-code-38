from subprocess import *
from setuptools import setup, find_packages
from setuptools.command.install import install
from ansible_deploy import __version__
import os
from itertools import groupby
from os.path import isfile

__name__ = 'ansible-provision'
role_name = __name__.split('-')[1]
cwd = os.getcwd()
base = '/etc/ansible/roles/%s' % role_name
data_files = []
_files = []
for dir in ['library', 'meta', 'filter_plugins', 'templates', 'defaults', 'tasks', 'roles']:
  for root, dirs, files in os.walk(dir, topdown=False):
    for name in files:
      if name.startswith('.') or root.startswith('./.'):
        continue
      _files.append((root,name) )

for k, g in groupby(_files, key=lambda e: e[0] ):
  data_files.append(("%s/%s" % (role_name, k), ["%s/%s" % (k, f[1]) for f in g]))

class link_role(install):
  def run(self):
      install.run(self)
      dist = self.install_data + "/" + role_name
      if not dist.startswith('/'):
        dist = "%s/%s" % (os.getcwd(), dist)
      role = "/etc/ansible/roles/%s" % role_name
      if os.path.isdir(dist):
        print ("Renaming %s to %s" % (dist, role))
        if os.path.isdir(role):
          shutil.rmtree(role)
        os.makedirs("/etc/ansible/roles/")
        os.renames(dist, role)

setup(
    name = __name__,
    version = __version__,
    packages = [__name__.replace("-", "_")],
    cmdclass = {'install': link_role},
    data_files = data_files,
    url = 'https://www/github.com/moshloop/ansible-provision',
    author = 'Moshe Immerman', author_email = 'moshe.immerman@gmail.com'
)