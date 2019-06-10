# -*- coding: utf-8 -*-
# Copyright 2017 - 2019 ibelie, Chen Jie, Joungtao. All rights reserved.
# Use of this source code is governed by The MIT License
# that can be found in the LICENSE file.

import os
import properform
from setuptools import setup

path = os.path.dirname(os.path.abspath(__file__))

with open(os.path.join(path, 'README.rst')) as f:
	readme = f.read()

setup(
	name = 'properform',
	version = properform.__version__,
	url = 'http://github.com/ibelie/properform/python',
	keywords = ('profile', 'properform'),
	description = 'Submit profile data to properform.',
	long_description = readme,

	author = properform.__author__,
	author_email = 'joungtao@gmail.com',
	license = 'MIT License',

	install_requires = [
		'docker >= 4.0.1',
	],

	classifiers = [
		# 'Development Status :: 3 - Alpha',
		'Development Status :: 4 - Beta',
		# 'Development Status :: 5 - Production/Stable',
		'Environment :: Console',
		'Natural Language :: English',
		'Operating System :: OS Independent',
		'License :: OSI Approved :: MIT License',
		'Intended Audience :: Developers',
		'Intended Audience :: Science/Research',
		'Intended Audience :: Education',
		'Topic :: Software Development :: Libraries',
		'Programming Language :: Python :: 2.7',
		'Programming Language :: Python :: 3.6',
	],
	packages = ['properform'],
)
