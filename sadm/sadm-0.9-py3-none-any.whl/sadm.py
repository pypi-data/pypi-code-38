# Copyright (c) Jeremías Casteglione <jrmsdev@gmail.com>
# See LICENSE file.

from _sadm.cmd import build as build_cmd
from _sadm.cmd import deploy as deploy_cmd
from _sadm.cmd import web as web_cmd

__all__ = ['build', 'deploy', 'web']

build = build_cmd.main
deploy = deploy_cmd.main
web = web_cmd.main
