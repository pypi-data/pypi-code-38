#!/usr/bin/python

__author__      = "Sander Granneman"
__copyright__   = "Copyright 2019"
__version__     = "1.6.2"
__credits__     = ["Sander Granneman"]
__maintainer__  = ["Sander Granneman"]
__email__       = "sgrannem@ed.ac.uk"
__status__      = "beta"

import sys

try:
	from setuptools import setup
	from setuptools.command import easy_install
	sys.stdout.write("Python development and setuptools have been installed...\n")
except:
	sys.stderr.write("Python development and setuptools have not been installed on this machine\nPlease contact the admin of this computer to install these modules\n")
	exit()
	
setup(name='GenomeBrowser',
	version='%s' % __version__,
	description='Python classes for making Genomebrowser snapshots.',
	author='Sander Granneman',
	author_email='sgrannem@ed.ac.uk',
	url='https://git.ecdf.ed.ac.uk/sgrannem/genomebrowser',
	install_requires=['pyCRAC >= 1.4.4','matplotlib >= 3.0','pandas','numpy'],
	packages=['GenomeBrowser','GenomeBrowser.Classes'],
	classifiers=[   'Development Status :: 5 - Production/Stable',
					'Environment :: Console',
					'Intended Audience :: Education',
					'Intended Audience :: Developers',
					'Intended Audience :: Science/Research',
					'License :: Freeware',
					'Operating System :: MacOS :: MacOS X',
					'Operating System :: POSIX',
					'Programming Language :: Python :: 3.6',
					'Topic :: Scientific/Engineering :: Bio-Informatics',
					'Topic :: Software Development :: Libraries :: Application Frameworks'
				]
			)
