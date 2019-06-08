# Copyright (c) Jeremías Casteglione <jrmsdev@gmail.com>
# See LICENSE file.

from subprocess import check_call as call

from .check import check

__all__ = ['deploy']

def deploy(env):
	env.log('os user')
	for diff in check(env):
		user = diff[0]
		uid = diff[1]
		cmd = ['useradd', '-m', '-U', '-u', str(uid)]

		fullname = env.settings.get("os.user.%s" % user, 'fullname', fallback = '').strip()
		if fullname != '':
			cmd.append('-c')
			cmd.append(fullname)

		shell = env.settings.get("os.user.%s" % user, 'shell', fallback = '/bin/bash').strip()
		cmd.append('-s')
		cmd.append(shell)

		cmd.append(user)
		call(cmd)
		env.log("%d %s user created" % (uid, user))
