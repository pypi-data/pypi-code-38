"""
Hans Roh 2015 -- http://osp.skitai.com
License: BSD
"""
import re
import sys
import os
import shutil, glob
from warnings import warn
try:
	from setuptools import setup
except ImportError:
	from distutils.core import setup

with open('rs4/__init__.py', 'r') as fd:
	version = re.search(r'^__version__\s*=\s*"(.*?)"',fd.read(), re.M).group(1)
	
if sys.argv[-1] == 'publish':
	buildopt = ['sdist', 'upload']
	if os.name == "nt":
		buildopt.insert (0, 'bdist_wheel')		
	os.system('python setup.py %s' % " ".join (buildopt))
	#os.system('twine upload dist/rs-%s*' % version)
	for each in os.listdir ("dist"):
		os.remove (os.path.join ('dist', each))
	sys.exit()

elif sys.argv[-1] == 'link':
	import site
	if os.name == "nt":
		linkdir = [each for each in site.getsitepackages() if each.endswith ("-packages")][0]		
	else:
		linkdir = [each for each in site.getsitepackages() if each.find ("/local/") !=- 1 and each.endswith ("-packages")][0]		
	target = os.path.join (os.path.join (os.getcwd (), os.path.dirname (__file__)), "rs4")
	link = os.path.join (linkdir, "rs4")
	if os.name == "nt":
		os.system ("mklink /d {} {}".format (link, target))
	else:		
		os.system ("ln -s {} {}".format (target, link))	
	sys.exit ()
	
classifiers = [
  'License :: OSI Approved :: MIT License',
  'Development Status :: 4 - Beta',  
  'Topic :: Utilities',
	'Environment :: Console',	
	'Topic :: Software Development :: Libraries :: Python Modules',
	'Intended Audience :: Developers',	
	'Programming Language :: Python',	
	'Programming Language :: Python :: 3'
]

PY_MAJOR_VERSION = sys.version_info [0]
if PY_MAJOR_VERSION == 3:
	if os.path.isfile ("rs4/lib/py2utils.py"):
		os.remove ("rs4/lib/py2utils.py")
		try: os.remove ("rs4/lib/py2utils.pyc")
		except OSError: pass		
else:
	if not os.path.isfile ("rs4/lib/py2utils.py"):
		with open ("rs4/lib/py2utils.py", "w") as f:
			f.write ("def reraise(type, value, tb):\n\traise type, value, tb\n")			

packages = [
	'rs4',
  	'rs4.psutil',
	'rs4.webkit',
	'rs4.nets',
	'rs4.nets.ipsec',
	'rs4.nets.proxy',
	'rs4.apis',
	'rs4.apis.aws',
	'rs4.apis.google',
	'rs4.apis.etri',
]

package_dir = {'rs4': 'rs4'}
package_data = {}

install_requires = [	
	"psutil",	
	"html2text", # need from siesta
	"requests",
	"colorama",
	"tqdm",
	"event_bus==1.0.2"
]

if os.name == "posix":
	install_requires.append ("setproctitle")
	install_requires.append ("ujson")

with open ('README.rst', encoding='utf-8') as f:
	long_description = f.read()
	
setup(
	name='rs4',
	version=version,
	description='Utility Pack',
	long_description = long_description,
	url = 'https://gitlab.com/hansroh/rs4',
	author='Hans Roh',	
	author_email='hansroh@gmail.com',	
	packages=packages,
	package_dir=package_dir,
	package_data = package_data,
	license='MIT',
	platforms = ["posix", "nt"],
	download_url = "https://pypi.python.org/pypi/rs4",
	install_requires = install_requires,
	classifiers=classifiers
)
