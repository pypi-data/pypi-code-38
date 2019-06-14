# Copyright (c) Jeremías Casteglione <jrmsdev@gmail.com>
# See LICENSE file.

from os import path, makedirs, chmod
from shutil import chown

from _sadm.plugin.utils.cmd import call, call_check

__all__ = ['deploy']

def deploy(env):
	dbdir = env.settings.get('service.munin', 'db.dir')
	makedirs(dbdir, mode = 0o755, exist_ok = True)
	chmod(dbdir, 0o750)

	dbuser = env.settings.get('service.munin', 'dbdir.user')
	dbgroup = env.settings.get('service.munin', 'dbdir.group')
	chown(dbdir, user = dbuser, group = dbgroup)

	env.log("dbdir %s (%s:%s)" % (dbdir, dbuser, dbgroup))

	if call('service cron status') == 0:
		call_check('service cron reload')
	else:
		call_check('service cron start')

	call('service munin start')
