#!/usr/bin/env python3
# -*- encoding: utf-8 -*-
# Michel Mooij, michel.mooij@dynniq.com


'''
Summary
-------
Installs WAF meta build system

Description
-----------
Gets and installs the WAF meta build system in the most appropriate location, i.e.
install in:

    - '/usr/bin' when user is root (or sudo), 
    - '$VIRTUAL_ENV/bin' when run from an virtual environment
    - '$HOME/bin' when run from a Cloud9 environment
    - '$HOME/.local/bin' by default

If the waf version is not specified from command line the environment variable 
$WAFVER will be used if it exists otherwise the latest version that has been tested 
with wtools will be used.

Usage
-----
Command syntax:

    waf-get [options]

Available options:
    -w | --waf
        WAF version to be installed

    -v | --version
        returns current version

    -h | --help
        prints this help message.
'''

import os, sys, getopt, logging, tarfile, tempfile, subprocess, shutil, site, glob

import urllib
from urllib import request

import wtools


VERSION = '1.9.14'
URL = 'https://codeload.github.com/waf-project/waf/tar.gz'


def usage():
	print(__doc__)


def main(argv=sys.argv, level=logging.INFO):
	logging.basicConfig(level=level, format='waf-get [%(levelname)s] %(message)s')

	args = None

	if 'WAFVER' in os.environ:
		version = os.environ['WAFVER']
	else:
		version = VERSION

	try:
		opts, _ = getopt.getopt(argv[1:], 'w:vh', ['waf=', 'version', 'help'])

		for opt, arg in opts:
			if opt in ('-w', '--waf'):
				version = arg

			elif opt in ('-v', '--version'):
				print(wtools.version)
				sys.exit()

			if opt in ('-h', '--help'):
				usage()
				sys.exit()

	except getopt.GetoptError as err:
		print(str(err))
		usage()
		sys.exit(2)

	release = 'waf-waf-%s' % version
	url = '%s/waf-%s' % (URL, version)

	logging.info("wget %s" % (url))
	tgz, _ = urllib.request.urlretrieve(url)

	tmp = tempfile.mkdtemp()

	logging.info("tar xvf %s -C %s" % (tgz, tmp))
	with tarfile.open(tgz, 'r:gz') as tar:
		tar.extractall(tmp)

	py3 = shutil.which('python3')
	cmd = [py3, 'waf-light', '--interpreter=#!{}'.format(py3)]
	if args:
		cmd.extend(args)
	logging.info("cmd: %s" % ' '.join(cmd))

	try:
		subprocess.run(cmd, cwd=os.path.join(tmp, release))

	except subprocess.CalledProcessError as err:
		logging.error("command failed: %s" % err)

	if os.getuid() == 0:
		wafbin = '/usr/local/bin'
		wafsite = None

	elif 'USER' in os.environ and os.environ['USER'] == 'root':
		wafbin = '/usr/local/bin'
		wafsite = None

	elif 'VIRTUAL_ENV' in os.environ:
		wafbin = '%s/bin' % os.environ['VIRTUAL_ENV']
		wafsite = sys.path[-1]
	
	else:
		home = os.path.expanduser("~")

		if os.path.exists(os.path.join(home, '.c9')):
			wafbin = os.path.join(home, 'bin')
		else:
			wafbin = os.path.join(home, '.local', 'bin')

		wafsite = site.USER_SITE

		if 'WAFDIR' in os.environ:
			logging.info("WAFDIR already set to: %s" % os.environ['WAFDIR'])
		else:
			profile = os.path.join(home, '.profile')
			if os.path.exists(profile):
				with open(profile, 'r') as f:
					s = f.read()
				s += 'WAFDIR=%s\n' % wafsite
				with open(profile, 'w+') as f:
					f.write(s)

	if not os.path.exists(wafbin):
		os.makedirs(wafbin, mode=0o755)

	for d in glob.glob(os.path.join(wafbin, '.waf*')):
		shutil.rmtree(d)

	shutil.copy(os.path.join(tmp, release, 'waf'), wafbin)

	if wafsite:
		waflib = os.path.join(wafsite, 'waflib')
		if os.path.exists(waflib):
			shutil.rmtree(waflib)
		if not os.path.exists(wafsite):
			os.makedirs(wafsite, mode=0o755)
		shutil.copytree(os.path.join(tmp, release, 'waflib'), waflib)

	logging.info("done")


if __name__ == "__main__":
	main(argv=sys.argv, level=logging.DEBUG)

