# Copyright (c) Jeremías Casteglione <jrmsdev@gmail.com>
# See LICENSE file.

import subprocess as proc

__all__ = ['call']

def call(cmd):
	shell = False
	if isinstance(cmd, str):
		shell = True
	return proc.call(cmd, shell = shell)

def call_check(cmd):
	shell = False
	if isinstance(cmd, str):
		shell = True
	return proc.check_call(cmd, shell = shell)
