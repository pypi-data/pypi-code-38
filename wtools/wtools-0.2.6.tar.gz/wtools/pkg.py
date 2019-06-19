#!/usr/bin/env python3
# -*- encoding: utf-8 -*-

import os, tempfile, shutil, json, subprocess, tarfile
import waflib
from waflib import Logs, Build, Scripting, Errors, Context


def set_pkg_default(conf, key, value):
	if key in os.environ.keys():
		value = os.environ[key]
	conf.env[key] = value


def options(opt):
	opt.add_option('--pkg-type', dest='pkg_type', default=None, action='store', help='packaging type (rpm|deb|ipkg)')
	opt.add_option('--pkg-recipe', dest='pkg_recipe', default=None, action='store', help='packaging recipe file')
	opt.add_option('--pkg-nostrip', dest='pkg_nostrip', default=False, action='store_true', help='do not strip binaries in packages')
	opt.add_option('--pkg-outdir', dest='pkg_outdir', default=None, action='store', help='location to store packages')


def configure(conf):
	if not conf.options.pkg_nostrip:
		conf.find_program('strip', var='STRIP', mandatory=False)

	conf.find_program('rpmbuild', var='RPMBUILD_BIN', mandatory=False)
	conf.find_program('dpkg-deb', var='DPKG_DEB_BIN', mandatory=False)
	conf.find_program('ipkg-build', var='IPKG_BUILD_BIN', mandatory=False)

	# configure packaging type to be used
	pkg_type = get_pkg_type(conf)
	if pkg_type:
		conf.env.PKG_TYPE = pkg_type

	# define out location for created package(s)
	if conf.options.pkg_outdir:
		pkg_outdir = conf.options.pkg_outdir
	else:
		pkg_outdir = getattr(Context.g_module, Context.TOP, conf.srcnode.abspath())
	
	pkg_outdir = os.path.abspath(pkg_outdir)
	if not os.path.exists(pkg_outdir):
		conf.fatal('Package outdir(%s) does not exist' % pkg_outdir)
	conf.env.PKG_OUTDIR = pkg_outdir

	# detect cross compiler prefix (if any) and/or target platform
	if 'RPM_TARGET' in os.environ:
		conf.env.PKG_RPM_TARGET = str(os.environ['RPM_TARGET'])
	if 'ARCH' in os.environ:
		conf.env.PKG_ARCH = str(os.environ['ARCH'])
	else:
		arch = str(conf.env.DEST_CPU)
		if arch in ('x86_64', 'x86-64'):
			arch = 'amd64'
		conf.env.PKG_ARCH = arch

	# define default packaging settings
	conf.env.PKG_NAME = getattr(Context.g_module, Context.APPNAME, 'noname')
	conf.env.PKG_VERSION = getattr(Context.g_module, Context.VERSION, '1.0')
	set_pkg_default(conf, 'PKG_SUMMARY', '')
	set_pkg_default(conf, 'PKG_RELEASE', '1')
	set_pkg_default(conf, 'PKG_LICENSE', 'GPLv2')
	set_pkg_default(conf, 'PKG_GROUP', 'Development/tools')
	set_pkg_default(conf, 'PKG_URL', '')
	set_pkg_default(conf, 'PKG_RELOCATIONS', '')
	set_pkg_default(conf, 'PKG_DESCRIPTION', '')
	set_pkg_default(conf, 'PKG_REQUIRES', '') # MUST be RPM style dependencies use comma separators
	set_pkg_default(conf, 'PKG_SECTION', 'misc')
	set_pkg_default(conf, 'PKG_MAINTAINER', '')

	# use recipe file containing packaging meta-information
	parse_pkg_recipe(conf, conf.options.pkg_recipe)

	# overwrite recipe with environment variables
	parse_pkg_environment(conf)

	# determine DEBIAN style dependencies when not defined yet
	if not 'PKG_DEPENDS' in conf.env:
		conf.env.PKG_DEPENDS = debian_get_depends(conf, conf.env.PKG_REQUIRES)


def get_pkg_type(ctx):
	pkg_type = ctx.options.pkg_type
	if not pkg_type:
		return None
		
	pkg_type = pkg_type.lower().lstrip('.')
	if pkg_type not in ('rpm', 'deb', 'opkg', 'ipkg', 'ipk'):
		ctx.fatal('Illegal packaging type: %s' % ctx.options.pkg_type)
	
	if pkg_type in ('opkg', 'ipkg', 'ipk'):
		pkg_type = 'ipkg'
		
	return pkg_type


def get_pkg_value(conf, key, pkg):
	val = pkg[key]
	key = key.lower()

	if key == 'name': # special treatment for package name
		if not len(val) or val.isspace():
			val = str(conf.env.PKG_NAME) 
		return val.replace(' ', '').replace('--', '-').replace('_', '-')
	elif key == 'requires': # join RPM requires
		return ', '.join(val)
	else:
		return val


def parse_pkg_recipe(conf, fname):
	if not fname or not os.path.exists(fname):
		return
	with open(fname) as f:
		s = json.load(f)
	if 'global' not in s:
		conf.fatal("Missing mandatory section '%s' in package recipe file '%s'" % ('global', fname))		
	for k in s['global'].keys():
		conf.env['PKG_%s' % k.upper()] = s['global'][k]

	if 'packages' in s:
		packages = s['packages']
		if not isinstance(packages, list):
			conf.fatal("Illegal packages section in '%s'; entry must be of type 'list'" % (fname))
		conf.env.PKG_COUNT = str(len(packages))
		i = 0
		for pkg in packages:
			i += 1
			for k in ("description", "requires", "name", "ignores"):
				if k in pkg:
					conf.env['PKG%i_%s' % (i, k.upper())] = get_pkg_value(conf, k, pkg)
			if 'requires' in pkg and 'depends' not in pkg:
				conf.env['PKG%i_DEPENDS' % i] = debian_get_depends(conf, conf.env['PKG%i_REQUIRES' % i])


def parse_pkg_environment(conf):
	pre = ['']
	env = os.environ
	try:
		num = int(env['PKG_NUM'])
		if num > 1:
			pre += [str(i) for i in range(1, num+1)]
	except:
		pass

	for k in env.keys():
		for p in pre:
			if k.startswith('PKG%s_' % p):
				conf.env[k.upper()] = env[k]

	for p in pre:
		d = 'PKG%s_DEPENDS' % p
		if d not in conf.env.keys():
			conf.env[d] = debian_get_depends(conf, conf.env['PKG%s_REQUIRES' % p])


def debian_get_depends(conf, v):
	if not v:
		return ''
	else:
		s = [i.split() for i in v.split(',')]
		keys = [i[0] for i in s]
		values = []
		for vals in [i[1:] for i in s]:
			vals = ['<<' if v=='<' else v for v in vals]
			vals = ['>>' if v=='>' else v for v in vals]
			values.append(vals)
		s = []
		for k,v in zip(keys,values):
			s.append("%s (%s)" % (k,' '.join(v)))
		return ', '.join(s)


class PackageContext(Build.InstallContext):
	'''package binary build results using DPKG, RPM or IPKG.'''
	cmd = 'pkg'

	def __init__(self, **kw):
		super(PackageContext, self).__init__(**kw)

	def _get_task_generators(self):
		tgens = []
		for group in self.groups:
			for tg in group:
				tgens.append(tg)
		return list(set(tgens))

	def get_pkg_environment(self, c):
		env = dict()
		for k in self.env:
			if not k.startswith('PKG_'):
				continue
			env[k] = self.env[k]
		if c:
			for k in self.env:
				pre = 'PKG%i_' % c
				if not k.startswith(pre):
					continue
				env[k.replace(pre, 'PKG_')] = self.env[k]
		return env

	def get_pkg_environments(self):
		cnt = []
		try:
			cnt = int(self.env.PKG_COUNT)
			cnt = [i for i in range(1, cnt+1)]
		except:
			cnt = [0]
		envs = []
		for c in cnt:
			envs.append(self.get_pkg_environment(c))
		return envs

	def execute(self):
		self.restore()
		if not self.all_envs:
			self.load_envs()

		try:
			srcdir = tempfile.mkdtemp()
			self.options.destdir=srcdir
			self.execute_build()

			for env in self.get_pkg_environments():
				try:
					tmp = tempfile.mkdtemp()
					self.package(srcdir, tmp, env)
				finally:
					shutil.rmtree(tmp)
		finally:
			shutil.rmtree(srcdir)

	def get_pkg_prefixes(self):
		try:
			c = int(self.env.PKG_COUNT)
			pre = [''] + [str(i) for i in range(1, c+1)]
			return ['PKG%s_' % p for p in pre]
		except:
			return ['PKG_']

	def package(self, srcdir, tmp, env):
		pkg_type = get_pkg_type(self) if self.options.pkg_type else self.env.PKG_TYPE
		name = env['PKG_NAME']
		version = env['PKG_VERSION']
		release = '%s-%s' % (name, version)

		# (0) define destination directory; i.e. 'waf --destdir'
		if pkg_type == 'rpm':
			destdir = os.path.join(tmp, release)
		elif pkg_type == 'deb':
			destdir = os.path.join(tmp, 'debian')
		elif pkg_type == 'ipkg':
			destdir = os.path.join(tmp, 'ipkg')
		elif not pkg_type:
			self.fatal("No packaging type (e.g. --pkg-type=deb) configured or specified!")
		else:
			self.fatal("Illegal packaging type '%s' specified!" % pkg_type)
		
		# (0) display packaging variables
		if self.options.verbose >= 2:
			for key in self.env.keys():
				for pre in self.get_pkg_prefixes():
					if key.startswith(pre):
						Logs.info('%20s : %s' % (key, self.env[key]))
		
		# (1) copy installed files to temporary directory
		if 'PKG_IGNORES' in env:
			ignores = env['PKG_IGNORES']
			if isinstance(ignores, str):
				ignores = [ignores]
			ignore_patterns = shutil.ignore_patterns(*ignores)
		else:
			ignore_patterns = None

		shutil.copytree(srcdir, destdir, ignore=ignore_patterns)

		# (2) strip debug/uneeded symbols from binaries and shared libraries
		self.strip_symbols(destdir)
		
		# (3) create actual package
		if pkg_type == 'rpm':
			self.rpm_create(tmp, env, destdir, release)
		elif pkg_type == 'deb':
			self.deb_create(tmp, env, destdir, name, version)
		elif pkg_type == 'ipkg':
			self.ipkg_create(tmp, env, destdir, release)

	def strip_symbols(self, path):
		'''Remove debug symbols and relocation information'''
		if not self.env.STRIP or self.options.pkg_nostrip:
			return

		quiet = None if self.options.verbose else Context.STDOUT
		cmd = self.env.STRIP
		if isinstance(cmd, list):
			cmd = cmd[0]
		cmd += " --strip-all"

		def isbin(fname):
			if os.path.islink(fname):
				return False
			with subprocess.Popen(['file', fname], stdout=subprocess.PIPE) as proc:
				s = proc.stdout.read().decode('UTF-8')
				return '%s: ELF ' % name in s

		for root, _, files in os.walk(path, topdown = False):
			for name in files:
				fname = os.path.join(root, name)
				if not isbin(fname):
					continue
				self.cmd_and_log('%s %s\n' % (cmd, fname), quiet=quiet)

	def deb_create(self, tmp, env, destdir, name, version):
		'''Create DEBIAN style package (.deb)'''
		dpkg = destdir
		cmd = self.env.DPKG_DEB_BIN
		if not cmd:
			self.fatal("Cannot create package; 'dpkg-deb' command not found.")
		if isinstance(cmd, list):
			cmd = cmd[0]

		# (1) create package staging directries
		for d in ('DEBIAN', ):
			os.makedirs(os.path.join(dpkg, d))
		
		# (2) copy archive to package staging
		self.debian_export_control(os.path.join(dpkg, 'DEBIAN'), tmp, env, destdir)

		# (3) detect config files and add to DEBIAN/conffiles
		conffiles = []
		for root, _, files in os.walk(destdir, topdown = False):
			if os.path.basename(root) != 'etc':
				continue
			etc = root[len(destdir):]
			for f in files:
				conffiles.append('.%s/%s' % (etc,f))
		if len(conffiles):
			with open(os.path.join(dpkg, 'DEBIAN', 'conffiles'), 'w+') as f:
				f.write('\n'.join(conffiles))
				f.write('\n')

		# (4) remove symlinks to shared libraries in DEBIAN/preinst and DEBIAN/postrm
		preinst = []
		for root, _, files in os.walk(destdir, topdown = False):
			if os.path.basename(root) != 'lib':
				continue
			lib = root[len(destdir):]
			for f in files:
				if os.path.islink(os.path.join(root,f)):
					preinst.append('[ -f {0}/{1} ] %% rm {0}/{1}'.format(lib,f))
					preinst.append('true')
		if len(preinst):
			fname = os.path.join(dpkg, 'DEBIAN', 'preinst')
			with open(fname, 'w+') as f:
				f.write('\n'.join(preinst))
				f.write('\n')
			os.chmod(fname, 0o755)

			fname = os.path.join(dpkg, 'DEBIAN', 'postrm')
			with open(fname, 'w+') as f:
				f.write('\n'.join(preinst))
				f.write('\n')
			os.chmod(fname, 0o755)

		# (5) add services from /etc/init.d to DEBIAN/postinst and DEBIAN/prerm
		services = []
		for root, _, files in os.walk(destdir, topdown = False):
			if not root.endswith('/etc/systemd'):
				continue
			for f in files:
				if not os.path.islink(os.path.join(root,f)):
					services.append(f)
		if len(services):
			fname = os.path.join(dpkg, 'DEBIAN', 'postinst')
			with open(fname, 'w+') as f:
				for service in services:
					f.write('#!/bin/sh\n')
					f.write('systemctl enable %s\n' % service)
					f.write('systemctl start %s\n' % service)
					f.write('\n')
			os.chmod(fname, 0o755)

			fname = os.path.join(dpkg, 'DEBIAN', 'prerm')
			with open(fname, 'w+') as f:
				for service in services:
					f.write('#!/bin/sh\n')
					f.write('systemctl stop %s\n' % service)
					f.write('systemctl disable %s\n' % service)
					f.write('\n')
			os.chmod(fname, 0o755)

		# (6) create actual DEB and save result
		release = env['PKG_RELEASE']
		arch = env['PKG_ARCH']
		cmd += " --build debian %s/%s_%s-%s_%s.deb" % (tmp, name, version, release, arch)
		quiet = None if self.options.verbose else Context.BOTH
		res = self.cmd_and_log(cmd, cwd=tmp, quiet=quiet)

		try:
			deb = res.split()[-1]
			deb = deb.rstrip('.').strip('\'').strip('`')
		except Exception as e:
			Logs.error('[ERROR] fatal internal error; %s' % repr(e))
			raise(e)

		quiet = None if self.options.verbose else Context.STDOUT
		dest = env['PKG_OUTDIR']
		self.cmd_and_log('mv %s %s\n' % (deb, dest), quiet=quiet)
		Logs.info("+install %s/%s (from %s)" % (dest, os.path.basename(deb), os.path.dirname(deb)))

	def debian_export_control(self, path, tmp, env, destdir):
		'''Exports DEBIAN control file'''
		control = str(DEBIAN_CONTROL)

		for k in env:
			v = str(env[k])
			if k == 'PKG_DEPENDS':
				v = self.debian_get_depends(v)
			control = control.replace('__%s__' % k, v) 

		fname = os.path.join(path, 'control')

		if self.options.verbose >= 3:
			Logs.info("========================================")
			Logs.info("DEBIAN CONTROL FILE (%s):" % fname)
			Logs.info(control)
			Logs.info("========================================")
		
		with open(fname, 'w+') as f:
			f.write(control)

		return fname

	def debian_get_depends(self, v):
		if not v:
			return ''
		else:
			return '\nDepends: %s' % v

	def ipkg_create(self, tmp, env, destdir, release):
		'''Create IPKG/OPKG style package (.ipk)'''
		ipkg = destdir
		cmd = self.env.IPKG_BUILD_BIN
		if not cmd:
			self.fatal("Cannot create package; 'ipkg-build' command not found.")
		if isinstance(cmd, list):
			cmd = cmd[0]

		# (1) create package staging directries
		for d in ('CONTROL', ):
			os.makedirs(os.path.join(ipkg, d))

		# (2) create package recipe's and meta files
		self.ipkg_export_control(os.path.join(ipkg, 'CONTROL'), tmp, env, destdir)

		# (3) detect config files and add to CONTROL/conffiles
		conffiles = []
		for root, _, files in os.walk(destdir, topdown = False):
			if os.path.basename(root) != 'etc':
				continue
			etc = root[len(destdir):]
			for f in files:
				conffiles.append('.%s/%s' % (etc,f))
		if len(conffiles):
			with open(os.path.join(ipkg, 'CONTROL', 'conffiles'), 'w+') as f:
				f.write('\n'.join(conffiles))
				f.write('\n')

		# (4) remove symlinks to shared libraries in CONTROL/preinst and CONTROL/postrm
		preinst = []
		for root, _, files in os.walk(destdir, topdown = False):
			if os.path.basename(root) != 'lib':
				continue
			lib = root[len(destdir):]
			for f in files:
				if os.path.islink(os.path.join(root,f)):
					preinst.append('[ -f {0}/{1} ] %% rm {0}/{1}'.format(lib,f))
					preinst.append('true')
		if len(preinst):
			with open(os.path.join(ipkg, 'CONTROL', 'preinst'), 'w+') as f:
				f.write('\n'.join(preinst))
				f.write('\n')
			with open(os.path.join(ipkg, 'CONTROL', 'postrm'), 'w+') as f:
				f.write('\n'.join(preinst))
				f.write('\n')

		# (5) add services from /etc/init.d to CONTROL/postinst and CONTROL/prerm
		services = []
		for root, _, files in os.walk(destdir, topdown = False):
			if not root.endswith('/etc/init.d'):
				continue
			for f in files:
				if not os.path.islink(os.path.join(root,f)):
					services.append(f)
		if len(services):
			with open(os.path.join(ipkg, 'CONTROL', 'postinst'), 'w+') as f:
				for service in services:
					f.write('#!/bin/sh\n')
					f.write('/%s enable\n' % service)
					f.write('/%s start\n' % service)
					f.write('\n')
			with open(os.path.join(ipkg, 'CONTROL', 'prerm'), 'w+') as f:
				for service in services:
					f.write('#!/bin/sh\n')
					f.write('/%s stop\n' % service)
					f.write('/%s disable\n' % service)
					f.write('\n')

		# (6) create actual IPKG and save result
		cmd += " -oroot -groot ipkg %s" % (tmp)
		quiet = None if self.options.verbose else Context.BOTH
		res = self.cmd_and_log(cmd, cwd=tmp, quiet=quiet)

		try:
			ipk = res.split()[-1]
		except Exception as e:
			Logs.error('[ERROR] fatal internal error; %s' % repr(e))
			raise(e)

		quiet = None if self.options.verbose else Context.STDOUT
		dest = env['PKG_OUTDIR']
		self.cmd_and_log('mv %s %s\n' % (ipk, dest), quiet=quiet)
		Logs.info("+install %s/%s (from %s)" % (dest, os.path.basename(ipk), os.path.dirname(ipk)))

	def ipkg_export_control(self, path, tmp, env, destdir):
		'''Exports IPKG control file'''
		control = str(IPKG_CONTROL)

		for k in env:
			v = str(env[k])
			if k == 'PKG_DEPENDS':
				v = self.ipkg_get_depends(v)
			control = control.replace('__%s__' % k, v) 

		fname = os.path.join(path, 'control')

		if self.options.verbose >= 3:
			Logs.info("========================================")
			Logs.info("IPKG CONTROL FILE (%s):" % fname)
			Logs.info(control)
			Logs.info("========================================")
		
		with open(fname, 'w+') as f:
			f.write(control)

		return fname

	def ipkg_get_depends(self, v):
		if not v:
			return ''
		else:
			return '\nDepends: %s' % v

	def rpm_create(self, tmp, env, destdir, release):
		'''Create Red Hat style package (.rpm)'''
		rpmbuild = os.path.join(tmp, 'rpmbuild')
		cmd = self.env.RPMBUILD_BIN
		if not cmd:
			self.fatal("Cannot create package; 'rpmbuild' command not found.")
		if isinstance(cmd, list):
			cmd = cmd[0]
		
		# (1) create package staging directries
		for d in ('BUILD','RPMS','SOURCES','SPECS','SRPMS'):
			os.makedirs(os.path.join(rpmbuild, d))
		
		# (2) copy archive to package staging
		self.rpm_create_archive(rpmbuild, release, destdir)

		# (3) create package recipe's and meta files
		spec = self.rpm_export_spec(os.path.join(rpmbuild, 'SPECS'), tmp, env, destdir)

		# (4) create actual RPM and save result
		target = self.env.PKG_RPM_TARGET
		quiet = None if self.options.verbose else Context.BOTH
		cmd += " -bb %s" % (spec)
		if target:
			cmd += " --target=%s" % (target)
		cmd += " --define='_topdir %s'\n" % (rpmbuild)
		res = self.cmd_and_log(cmd, quiet=quiet)

		try:
			rpm = [r for r in res.splitlines() if r.startswith('Wrote:')]
			rpm = rpm[0].split()[1]
		except Exception as e:
			Logs.error('[ERROR] fatal internal error; %s' % repr(e))
			raise(e)

		quiet = None if self.options.verbose else Context.STDOUT
		dest = env['PKG_OUTDIR']
		self.cmd_and_log('mv %s %s\n' % (rpm, dest), quiet=quiet)
		Logs.info("+install %s/%s (from %s)" % (dest, os.path.basename(rpm), os.path.dirname(rpm)))

	def rpm_create_archive(self, rpmtop, release, destdir):
		fname = os.path.join(rpmtop, 'SOURCES', '%s.tar.gz' % release)
		with tarfile.open(fname, 'w:gz') as tar:
			tar.add(destdir, arcname=release)

	def rpm_get_requires(self, v):
		if not v:
			return ''
		else:
			s = 'Requires: %s' % v
			return s
		
	def rpm_export_spec(self, path, tmp, env, destdir):
		'''Exports RPM specification file'''
		spec = str(RPM_SPEC)

		for k in env:
			v = str(env[k])
			if k == 'PKG_REQUIRES':
				v = self.rpm_get_requires(v)
			spec = spec.replace('__%s__' % k, v)

		for root, _, files in os.walk(destdir, topdown = False):
			if os.path.basename(root) != 'etc':
				continue

			etc = root[len(destdir):]
			for f in files:
				spec += '%config(noreplace) {}/{}\n'.format(etc, f) 

		fname = os.path.join(path, '%s.spec' % env['PKG_NAME'])

		if self.options.verbose >= 3:
			Logs.info("========================================")
			Logs.info("RPM SPEC FILE (%s):" % fname)
			Logs.info(spec)
			Logs.info("========================================")
		
		with open(fname, 'w+') as f:
			f.write(spec)

		return fname


#------------------------------------------------------------------------------
RPM_SPEC = '''
%define        __spec_install_post %{nil}
%define          debug_package %{nil}
%define        __os_install_post %{_dbpath}/brp-compress

Summary: __PKG_SUMMARY__
Name: __PKG_NAME__
Version: __PKG_VERSION__
Release: __PKG_RELEASE__
License: __PKG_LICENSE__
Group: __PKG_GROUP__
Source: %{name}-%{version}.tar.gz
AutoReq: no
__PKG_REQUIRES__
URL: __PKG_URL__
BuildRoot: %{_tmppath}/%{name}-%{version}-%{release}-root
__PKG_RELOCATIONS__

%description
__PKG_DESCRIPTION__

%prep
%setup -q

%build
# Empty section.

%install
rm -rf %{buildroot}
mkdir -p  %{buildroot}
cp -a * %{buildroot}

# Only post, preun and postun if any systemd service.
%if 0%{?rpm_systemd_services:1}

# See https://fedoraproject.org/wiki/Packaging:Scriptlets for the order and
# conditions.

# On upgrade only (before new install and old uninstall)
%pre
    if [ "$1" -eq 2 ]
    then
        systemctl disable --now %rpm_systemd_services
    fi

# On uninstall only, not on upgrade
%preun
    if [ "$1" -eq 0 ]
    then
        systemctl disable --now %rpm_systemd_services
    fi

%postun
    systemctl daemon-reload

# After new install and old uninstall
%posttrans
    echo "posttrans: $1"
    systemctl daemon-reload
    systemctl enable --now %rpm_systemd_services

%endif # End of rpm_sytemd_services


%clean
rm -rf %{buildroot}

%files
%defattr(-,root,root,-)
/


'''


#------------------------------------------------------------------------------
IPKG_CONTROL = '''
Package: __PKG_NAME__
Version: __PKG_VERSION__
Architecture: __PKG_ARCH__
Section: __PKG_SECTION__
Priority: optional __PKG_DEPENDS__
Maintainer: __PKG_MAINTAINER__
Description: __PKG_SUMMARY__
Source: __PKG_URL__
'''


#------------------------------------------------------------------------------
DEBIAN_CONTROL = '''
Package: __PKG_NAME__
Version: __PKG_VERSION__
Architecture: __PKG_ARCH__
Section: __PKG_SECTION__
Priority: optional __PKG_DEPENDS__
Maintainer: __PKG_MAINTAINER__
Description: __PKG_SUMMARY__
Source: __PKG_URL__
'''

