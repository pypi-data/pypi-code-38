"""
Hans Roh 2015 -- http://osp.skitai.com
License: BSD
"""
import re
import sys
import os
import shutil, glob
import codecs
from warnings import warn
try:
	from setuptools import setup
except ImportError:
	from distutils.core import setup

with open('atila/__init__.py', 'r') as fd:
	version = re.search(r'^__version__\s*=\s*"(.*?)"',fd.read(), re.M).group(1)

if sys.argv[-1] == 'publish':
	buildopt = ['sdist', 'upload']	
	if os.name == "nt":
		buildopt.insert (0, 'bdist_wheel')
	os.system('python setup.py %s' % " ".join (buildopt))
	for each in os.listdir ("dist"):
		os.remove (os.path.join ('dist', each))
	sys.exit()
	
classifiers = [
  'License :: OSI Approved :: MIT License',
  'Development Status :: 4 - Beta',  	
	'Topic :: Internet :: WWW/HTTP :: WSGI',
	'Environment :: Console',	
	'Topic :: Internet',
	'Topic :: Software Development :: Libraries :: Python Modules',
	'Intended Audience :: Developers',	
	'Programming Language :: Python :: 3',
]

packages = [
	'atila',
	'atila.app',
	'atila.patches'	
]

package_dir = {'atila': 'atila'}
package_data = {
	"atila": [
		"contrib/templates/*"
	]
}

install_requires = [
	"skitai"
]

with codecs.open ('README.rst', 'r', encoding='utf-8') as f:
	long_description = f.read()
    
setup (
	name='atila',
	version=version,
	description='Atila Framework',
	long_description=long_description,
	url = 'https://gitlab.com/hansroh/atila',
	author='Hans Roh',
	author_email='hansroh@gmail.com',	
	packages=packages,
	package_dir=package_dir,
	package_data = package_data,
	entry_points = {},
	license='MIT',
	platforms = ["posix", "nt"],
	download_url = "https://pypi.python.org/pypi/atila",
	install_requires = install_requires,
	classifiers=classifiers	
)
