#!/usr/bin/env python3
# -*- encoding: utf-8 -*-

import os, tempfile, shutil, platform, tarfile
import waflib
from waflib import Logs, Build, Scripting, Errors, Context


def options(opt):
	opt.add_option('--bundle-type', dest='bundle_type', default='gz', action='store', help='bundle compression type (tgz|tbz2|zip)')
	opt.add_option('--bundle-outdir', dest='bundle_outdir', default=None, action='store', help='location to store the bundle')
	opt.add_option('--bundle-include', dest='bundle_include', default=None, action='store', help='path to additional files to include')


def configure(conf):
	# configure compression type to be used
	bundle_type = get_bundle_type(conf)
	if bundle_type:
		conf.env.BUNDLE_TYPE = bundle_type

	# define output location for the created bundle
	if conf.options.bundle_outdir:
		bundle_outdir = conf.options.bundle_outdir
	else:
		bundle_outdir = getattr(Context.g_module, Context.TOP, conf.srcnode.abspath())
	
	bundle_outdir = os.path.abspath(bundle_outdir)
	if not os.path.exists(bundle_outdir):
		conf.fatal('Bundle outdir(%s) does not exist' % bundle_outdir)
	conf.env.BUNDLE_OUTDIR = bundle_outdir

	# configure additional files to be included
	if conf.options.bundle_include:
		if not os.path.exists(conf.options.bundle_include):
			conf.fatal('Bundle include(%s) does not exist' % conf.options.bundle_include)
		conf.env.BUNDLE_INCLUDE = os.path.abspath(conf.options.bundle_include)
	
	# define default packaging settings
	name = getattr(Context.g_module, Context.APPNAME, 'noname')
	version = getattr(Context.g_module, Context.VERSION, '1.0')
	host = os.getenv('HOST')
	if not host:
		host = get_bundle_host(conf)
	conf.env.BUNDLE_RELEASE = "%s-%s-%s" % (name, version, host)


def get_bundle_type(ctx):
	bundle_type = ctx.options.bundle_type
	if not bundle_type:
		return None
		
	bundle_type = bundle_type.lower().lstrip('.')
	if bundle_type not in ('gz', 'tgz', 'tar.gz', 'bz2', 'tbz2', 'tar.bz2'):
		ctx.fatal('Illegal bundling type: %s' % ctx.options.bundle_type)
	
	if bundle_type in ('gz', 'tgz', 'tar.gz'):
		bundle_type = 'gz'
		
	elif bundle_type in ('bz2', 'tbz2', 'tar.bz2'):
		bundle_type = 'bz2'

	else:
		ctx.fatal("Illegal bundle type '%s' specified!" % bundle_type)
		
	return bundle_type


def get_bundle_host(conf):
	try:
		import distro
		host = "-".join(distro.linux_distribution()[:2])
	except:
		if hasattr(platform, 'dist'):
			host = "-".join(platform.dist()[:2])
		else:
			host = "%s-%s" % (conf.env.DEST_OS, conf.env.DEST_CPU)

	return host.replace(' ', '_').lower()


class BundleContext(Build.InstallContext):
	'''bundle binary build results as archive (tar.gz, tar.bz2).'''
	cmd = 'bundle'

	def __init__(self, **kw):
		super(BundleContext, self).__init__(**kw)

	def _get_task_generators(self):
		tgens = []
		for group in self.groups:
			for tg in group:
				tgens.append(tg)
		return list(set(tgens))

	def execute(self):
		self.restore()
		if not self.all_envs:
			self.load_envs()

		tmp = tempfile.mkdtemp()
		try:
			self.bundle(tmp)
		finally:
			shutil.rmtree(tmp)			

	def bundle(self, tmp):
		bundle_type = get_bundle_type(self) if self.options.bundle_type else self.env.BUNDLE_TYPE
		if not bundle_type:
			self.fatal("No bundle type specified!")

		release = self.env.BUNDLE_RELEASE
		destdir = os.path.join(tmp, release)
		outdir = self.env.BUNDLE_OUTDIR
		incdir = self.env.BUNDLE_INCLUDE
		ext = 'tar.gz' if bundle_type == 'gz' else 'tar.bz2'

		# (0) display BUNDLING variables
		if self.options.verbose >= 2:
			for key in self.env.keys():
				if not key.startswith('BUNDLE_'):
					continue
				Logs.info('%20s : %s' % (key, self.env[key]))
		
		# (1) build component files and install in temporary directory
		self.options.destdir=destdir
		self.execute_build()

		# (2) copy additional files to release directory
		if incdir and os.path.exists(incdir):
			quiet = None if self.options.verbose else Context.STDOUT
			self.cmd_and_log('cp -a %s/* %s\n' % (incdir, destdir), quiet=quiet)
			Logs.info("+copy %s/* (to %s)" % (incdir, destdir))
		
		# (3) create tar file with requested compression type
		fname = os.path.join(tmp, '%s.%s' % (release, ext))
		with tarfile.open(fname, 'w:%s' % bundle_type) as tar:
			tar.add(destdir, arcname=release)

		# (4) move bundle to output directory
		quiet = None if self.options.verbose else Context.STDOUT
		self.cmd_and_log('mv %s %s\n' % (fname, outdir), quiet=quiet)
		Logs.info("+install %s/%s (from %s)" % (outdir, os.path.basename(fname), os.path.dirname(fname)))

		# (5) export a list of what the bundle provides
		fname = os.path.join(outdir, '%s.provides' % (release))
		with open(fname, "w+") as f:
			for root, dirs, files in os.walk(destdir):
				for fname in files:
					f.write('%s\n' % os.path.relpath(os.path.join(root, fname), destdir))

