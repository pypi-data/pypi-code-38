#!/usr/bin/env python3
# -*- encoding: utf-8 -*-
# Michel Mooij, michel.mooij@dynniq.com


'''
Summary
-------
Create a development/release sandbox

TODO: NOT FINISHED YET, WORK IN PROGRESS

Description
-----------
Gets a set of remote components (SVN, GIT) and creates a working development and/or
release environment based on the specified recipe

Usage
-----
Command syntax:

    wbox [options]

Available options:
    -s | --setup=<recipe.json|recipe-name>
        create a new sandbox using the recipe name or file

    -f | --pull
        pull latest revisions from origin

    -p | --push=<commit-message>
        commit all changes in packages using provided commit message
        and push all changes to origin

    -c | --config=[dev|develop|D|rel|release|R]
	    configure the sandbox package for 'development' or 'release'

    -e | --exec=<waf-commands-and-arguments>
	    comma separated list of 'waf' commands and arguments to execute
		on each package in the sandbox

    -t | --target=<target>
	    configure target type; i.e. 'host'. use ls=targets to get a
		list of possible build targets

    -I | --init=<admin.json>
        path to database administration initialization file.

    -S | --sync
	    synchronize administration cache with origin

    -L | --ls=[workspaces|plans|targets]
	    list available workspace, (release) plans and target from
		administration cache

    -v | --version
        returns current version

    -h | --help
        prints this help message.
'''

import os, sys, getopt, logging, subprocess, shutil, pickle, json
import wtools


BOX_C4CHE	= '.c4che'
BOX_LOCK	= '.lock-box'

BOX_CMD_SETUP			= 'setup'
BOX_CMD_PULL			= 'pull'
BOX_CMD_PUSH    		= 'push'
BOX_CMD_CONFIG			= 'config'
BOX_CMD_EXEC			= 'exec'
BOX_CMD_INIT    		= 'init'
BOX_CMD_SYNC			= 'sync'
BOX_CMD_LS			= 'ls'


def usage():
	print(__doc__)


def fetch_git(prefix, name, pkg, git):
	top = os.path.join(prefix, name)
	env = os.environ
	cmd = []

	if not 'GITUSER' in env:
		try:
			p = subprocess.run(['git', 'config', 'user.name'], stdout=subprocess.PIPE)
			user = p.stdout.decode('utf-8').splitlines()[0]
		except Exception as e:
			logging.error('failed to detect git user.name. define it as environment variable GITUSER or configure using git')
			raise e
		env['GITUSER'] = user

	if os.path.exists(top):
		cmd.append((top, ['git', 'pull']))
	else:
		cmd.append((prefix, ['git', 'clone', os.path.expandvars(pkg['uri']), name]))

	if 'checkout' in pkg:
		cmd.append((top, ['git', 'checkout', os.path.expandvars(pkg['checkout'])]))

	try:
		for (t, c) in cmd:
			logging.info('cd %s; %s' % (t, ' '.join(c)))
			subprocess.run(c, check=True, env=env, cwd=t)

	except subprocess.CalledProcessError as e:
		logging.error('failed to get package(%s); %r' % (name, e))
		raise e


def fetch_svn(prefix, name, pkg, svn=None):
	top = os.path.join(prefix, name)
	env = os.environ
	cmd = []

	if not 'SVNROOT' in env:
		if 'root' in pkg:
			env['SVNROOT'] = pkg['root']
		elif 'root' in svn:
			env['SVNROOT'] = svn['root']

	if os.path.exists(top):
		cmd.append((top, ['svn', 'up']))
	else:
		cmd.append((prefix, ['svn', 'co', os.path.expandvars(pkg['uri']), name]))

	if 'revision' in pkg:
		cmd.append((top, ['svn', 'up', '-R', os.path.expandvars(pkg['revision'])]))

	try:
		for (t, c) in cmd:
			logging.info('cd %s; %s' % (t, ' '.join(c)))
			subprocess.run(c, check=True, env=env, cwd=t)

	except subprocess.CalledProcessError as e:
		logging.error('failed to get package(%s); %r' % (name, e))
		raise e


def fetch(prefix, pkg, git, svn):
	if 'name' not in pkg:
		raise Exception("missing package name")
	name = pkg['name']
	logging.info('fetching(%s) ...' % name)
	if 'git' in pkg:
		fetch_git(prefix, name, pkg['git'], git)
	elif 'svn' in pkg:
		fetch_svn(prefix, name, pkg['svn'], svn)
	else:
		raise Exception("missing 'svn' or 'git' entry in package")


def sandbox_setup(prefix, name):
	if name.endswith('.json') and not os.path.exists(name):
		raise Exception("file '%s' does not exist" % name)

	prefix = prefix.rstrip(os.sep)
	name = os.path.splitext(os.path.basename(name))[0]
	print("TODO: SETUP(%s, %s)" % (prefix, name))


def sandbox_pull(prefix):
	print("TODO: PULL(%s)" % (prefix))


def sandbox_push(prefix, msg):
	print("TODO: PUSH(%s, %s)" % (prefix, msg))


def sandbox_config(prefix, config, target):
	print("TODO: CONFIG(%s, %s)" % (prefix, config, target))


def sandbox_exec(prefix, args):
	print("TODO: EXEC(%s, %s)" % (prefix, args))


def dummy():
	if not prefix.endswith(name):
		prefix = os.path.join(prefix, name)
	created = not os.path.exists(prefix)

	for p in ('workspace', 'out', 'downloads'):
		try:
			os.makedirs(os.path.join(prefix, p))
		except:
			pass
	
	logging.info("command: %s %s" % (os.path.basename(argv[0]), " ".join(argv[1:])))

	try:
		with open(fname, 'r') as f:
			s = json.load(f)
			packages = s['packages']
			git = s['git'] if 'git' in s else None
			svn = s['svn'] if 'svn' in s else None
	except Exception as e:
		logging.error(repr(e))
		sys.exit(2)

	for pkg in packages:
		fetch(os.path.join(prefix, 'workspace'), pkg, git, svn)

	logging.info("sandbox(%s) %s" % (prefix, "created" if created else "updated"))


def admin_init(fname):
	if not os.path.exists(fname):
		raise Exception("administration initialization file '%s' does not exist" % fname)

	pkg = dict()
	pkg['name'] = BOX_C4CHE

	with open(fname, 'r') as f:
		s = json.load(f)
		if 'git' in s:
			pkg['git'] = s['git']
		if 'svn' in s:
			pkg['svn'] = s['svn']

	lock = os.path.join(wtools.location, BOX_LOCK)
	if os.path.exists(lock):
		os.remove(lock)

	c4che = os.path.join(wtools.location, BOX_C4CHE)
	if os.path.exists(c4che):
		shutil.rmtree(c4che)

	fetch(wtools.location, pkg, None, None)
	with open(os.path.join(wtools.location, BOX_LOCK), 'wb') as f:
		pickle.dump(pkg, f)


def admin_sync():
	lock = os.path.join(wtools.location, BOX_LOCK)
	if not os.path.exists(lock):
		raise Exception("administration lock file does not exist, init first?")

	c4che = os.path.join(wtools.location, BOX_C4CHE)
	if not os.path.exists(c4che):
		raise Exception("administration cache does not exist, init first?")

	with open(lock, 'rb') as f:
		pkg = pickle.load(f)

	fetch(wtools.location, pkg, None, None)


def admin_list(arg):
	if arg not in ('workspaces', 'plans', 'release_plans', 'release-plans', 'release plans', 'targets'):
		print("unknown argument '%s' for command ls" % arg)
		sys.exit(2)

	c4che = os.path.join(wtools.location, BOX_C4CHE)
	if not os.path.exists(c4che):
		print("administration cache does not exist, init first?")
		sys.exit(2)

	if arg == 'plans':
		arg = 'release_plans'
	arg = arg.replace('-', '_').replace(' ', '_')

	if arg == 'targets':
		fname = os.path.join(c4che, 'env', 'targets.json')
		with open(fname, 'r') as f:
			s = json.load(f)
		for t in s['targets']:
			print(t['name'])

	else:
		for _, _, files in os.walk(os.path.join(c4che, arg)):
			for f in files:
				print(f.rstrip('.json'))
			break


def main(argv=sys.argv, level=logging.INFO):
	logging.basicConfig(level=level, format='wbox [%(levelname)s] %(message)s')

	prefix = os.getcwd()
	fname = None
	created = True
	cmd = None
	msg = None
	config = None
	target = None
	waf = None
	args = []

	try:
		opts, _ = getopt.getopt(argv[1:], 's:fp:c:e:t:I:SL:vh', [
			'setup=', 'pull', 'push=', 'config=', 'exec=', 'target=', 'init=', 'sync', 'ls=', 'version', 'help'])

		for opt, arg in opts:
			if opt in ('-s', '--setup'):
				cmd = BOX_CMD_SETUP
				fname = arg

			elif opt in ('-p', '--pull'):
				cmd = BOX_CMD_PULL

			elif opt in ('-P', '--push'):
				cmd = BOX_CMD_PUSH
				msg = arg

			elif opt in ('-c', '--config'):
				cmd = BOX_CMD_CONFIG
				config = arg

			elif opt in ('-e', '--exec'):
				cmd = BOX_CMD_EXEC
				args = arg.split(',')

			elif opt in ('-t', '--target'):
				target = arg

			elif opt in ('-I', '--init'):
				cmd = BOX_CMD_INIT
				fname = arg

			elif opt in ('-S', '--sync'):
				cmd = BOX_CMD_SYNC

			elif opt in ('-L', '--ls'):
				admin_list(arg)
				sys.exit()

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

	logging.info("command: %s %s" % (os.path.basename(argv[0]), " ".join(argv[1:])))

	try:
		if cmd == BOX_CMD_SETUP:
			sandbox_setup(prefix, fname)

		elif cmd == BOX_CMD_PULL:
			sandbox_pull(prefix)

		elif cmd == BOX_CMD_PUSH:
			sandbox_push(prefix, msg)

		elif cmd == BOX_CMD_CONFIG:
			sandbox_config(prefix, config, target)

		elif cmd == BOX_CMD_EXEC: ## build, install, clean, distclean, bundle, pkg, clean, eclipse
			sandbox_exec(prefix, args)

		elif cmd == BOX_CMD_INIT:
			admin_init(fname)

		elif cmd == BOX_CMD_SYNC:
			admin_sync()

	except Exception as e:
		logging.error('%s' % e)
		sys.exit(2)

	logging.info("done")


if __name__ == "__main__":
	main(argv=sys.argv, level=logging.DEBUG)

