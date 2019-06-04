from setuptools import setup,find_packages,Command
from uforgecli.utils.constants import *
import os
import sys
import datetime

ROOT_DIR = os.path.dirname(os.path.realpath(__file__))

# Declare your packages' dependencies here, for eg:
requires=[
    'uforge_python_sdk==' + PROJECT_VERSION,
    'httplib2==0.9',
    'cmd2==0.6.7',
    'texttable>=0.8.1',
    'progressbar==2.3',
    'argparse',
    'pyparsing==2.0.2',
    'hurry.filesize==0.9',
    'termcolor==1.1.0',
    'xmlrunner==1.7.7',
    'ussclicore==1.0.11']

if os.name != "nt":
	if not "linux" in sys.platform:
		#mac os
	        requires.append('readline')
else:   #On Windows
        requires.append('pyreadline==2.0')

test_requires=['mock']

class CleanCommand(Command):
    """Custom clean command to tidy up the project root."""
    user_options = []
    def initialize_options(self):
        pass
    def finalize_options(self):
        pass
    def run(self):
        os.system('rm -vrf '+ROOT_DIR+'/build '+ROOT_DIR+'/dist '+ROOT_DIR+'/*.pyc '+ROOT_DIR+'/*.egg-info')
        os.system('find '+ROOT_DIR+' -iname "*.pyc" -exec rm {} +')

setup (

  install_requires=requires,
  tests_require = test_requires,

  # Fill in these to make your Egg ready for upload to
  # PyPI
  name = PROJECT_NAME,
  version = PROJECT_VERSION,
  description='',
  long_description='',
  packages = find_packages(),
  author = 'UShareSoft',
  author_email = 'contact@usharesoft.com',
  license="Apache License 2.0",
  url = '',
  classifiers=(
        'Development Status :: 4 - Beta',
        'Environment :: Console',
        'Intended Audience :: Developers',
        'Intended Audience :: System Administrators',
        'Natural Language :: English',
        'Operating System :: MacOS :: MacOS X',
        'Operating System :: Microsoft :: Windows',
        'Operating System :: POSIX',
        'License :: OSI Approved :: Apache Software License',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
    ),

  # ... custom build command
  cmdclass={
    'clean': CleanCommand,
  },

  #long_description= 'Long description of the package',
  scripts = ['bin/uforge', 'bin/uforge.bat'],

)
