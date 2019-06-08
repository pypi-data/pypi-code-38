# Copyright (c) Jeremías Casteglione <jrmsdev@gmail.com>
# See LICENSE file.

from configparser import ConfigParser
from os import path
from pytest import raises

from _sadm.env.settings import Settings
from _sadm.errors import SettingsError

def test_settings(testing_env):
	env = testing_env()
	assert isinstance(env.settings, Settings)
	assert isinstance(env.settings, ConfigParser)

def test_plugins(testing_settings):
	s = testing_settings()
	assert sorted([p[0] for p in s.plugins('configure')]) == ['os', 'sadm', 'testing']

def test_parsing_error(testing_settings):
	with raises(SettingsError, match = 'Source contains parsing errors: '):
		testing_settings(cfgfile = 'config-parsing-error.ini')

def test_getlist_fallback(testing_settings):
	s = testing_settings()
	l = s.getlist('testing', 'test.notset.list', fallback = None)
	assert l is None
	with raises(SettingsError,
		match = 'No option \'test.notset.list\' in section: \'testing\''):
		s.getlist('testing', 'test.notset.list')

def test_getlist(testing_settings):
	s = testing_settings(cfgfile = 'config-settings-getlist.ini')
	l = s.getlist('testing', 'test.list.empty')
	assert isinstance(l, tuple)
	assert len(l) == 0

def test_getlist_comma(testing_settings):
	s = testing_settings(cfgfile = 'config-settings-getlist.ini')
	l = s.getlist('testing', 'test.list.comma')
	assert l == ('v0', 'v1', 'v2', 'v3')

def test_getlist_order(testing_settings):
	s = testing_settings(cfgfile = 'config-settings-getlist.ini')
	l = s.getlist('testing', 'test.list.order')
	assert l == ('v1', 'v3', 'v2', 'v0')

def test_getlist_lines(testing_settings):
	s = testing_settings(cfgfile = 'config-settings-getlist.ini')
	l = s.getlist('testing', 'test.list.lines')
	assert l == ('v0', 'v1', 'v2', 'v3')

def test_getlist_combined(testing_settings):
	s = testing_settings(cfgfile = 'config-settings-getlist.ini')
	l = s.getlist('testing', 'test.list.combined')
	assert l == ('v0', 'v1', 'v2', 'v3', 'v4', 'v5', 'v6')

def test_merge(testing_settings):
	cfgfn = path.join('tdata', 'testing', 'config-merge.ini')
	s = testing_settings()
	assert sorted(s.sections()) == ['os', 'sadm', 'testing']
	assert s.options('testing') == []
	cfg = Settings()
	with open(cfgfn, 'r') as fh:
		cfg.read_file(fh)
	s.merge(cfg, 'nosection', ('opt0', 'opt1'))
	assert sorted(s.sections()) == ['os', 'sadm', 'testing']
	s.merge(cfg, 'newsection', ('opt0', 'opt1'))
	assert sorted(s.sections()) == ['newsection', 'os', 'sadm', 'testing']
	s.merge(cfg, 'testing', ('noopt0', 'noopt1', 'noopt2'))
	assert s.options('testing') == []
	s.merge(cfg, 'testing', ('opt0', 'opt1', 'opt2'))
	assert sorted(s.options('testing')) == ['opt0', 'opt1', 'opt2']
