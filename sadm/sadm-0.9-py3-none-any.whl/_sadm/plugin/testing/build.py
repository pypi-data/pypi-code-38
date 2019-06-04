# Copyright (c) Jeremías Casteglione <jrmsdev@gmail.com>
# See LICENSE file.

def build(env):
	env.log('build')
	testing_error = env.settings.get('testing', 'testing.error', fallback = '')
	if testing_error == 'env_session_error':
		env.session.start()
