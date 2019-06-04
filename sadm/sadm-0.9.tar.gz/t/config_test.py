# Copyright (c) Jeremías Casteglione <jrmsdev@gmail.com>
# See LICENSE file.

from configparser import ConfigParser
from os import path
from pytest import raises

from _sadm import cfg
from _sadm.errors import ProfileError

def test_cfg():
	assert cfg._DEFAULT['name'] == ''
	assert cfg._DEFAULT['profile'] == 'default'
	assert cfg._DEFAULT['env'] == 'default'
	c = cfg.new()
	assert isinstance(c, ConfigParser)
	assert c.name() == 'sadmtest'
	assert c.filename().endswith(path.join('tdata', 'sadm.cfg'))
	assert len(c.defaults()) == 5
	assert c.get('default', 'name') == 'sadmtest'
	assert c.get('default', 'profile') == 'testing'
	assert c.get('default', 'env') == 'testing'
	assert c.get('default', 'dir') == '.'
	assert c.listPlugins('testing') == ['sadm', 'os', 'testing']
	assert len(c.sections()) == 2
	assert c.has_section('testing')
	assert c.get('testing', 'dir') == './tdata'
	assert c.get('testing', 'env.testing') == 'testing/config.ini'
	assert sorted(c.listProfiles()) == ['envsetup', 'testing']
	assert sorted(c.listEnvs('testing')) == ['testing', 'testing.nodir']

def test_profile_error():
	c = cfg.new()
	with raises(ProfileError, match = 'config profile noprofile not found'):
		c.listEnvs('noprofile')

def test_default_plugins():
	assert tuple(sorted(cfg._enablePlugins)) == ('sadm', 'sadmenv')

def test_name():
	c = cfg.new()
	assert c.name() == 'sadmtest'
	assert c._getName() == 'tdata'

def test_file_not_found():
	fn = path.join('tdata', 'testing', 'noconfig.ini')
	with raises(ProfileError, match = 'noconfig.ini file not found'):
		c = cfg.new(cfgfile = fn)

def test_noname():
	fn = path.join('tdata', 'testing', 'config-noname.ini')
	c = cfg.new(cfgfile = fn)
	assert c.name() == 'testing'
