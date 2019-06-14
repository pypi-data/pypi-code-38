#!/usr/bin/env python3

# Copyright (c) Jeremías Casteglione <jrmsdev@gmail.com>
# See LICENSE file.

import sys
from os import system

upload = '--upload' in sys.argv

if upload:
	system('rm -vf dist/sadm-*.*')

system('python3 setup.py clean')
system('python3 setup.py dist')
system('pip freeze | grep bottle >requirements.txt')

if upload:
	system('twine upload -s -i jrmsdev@gmail.com dist/sadm-*.*')

sys.exit(0)
