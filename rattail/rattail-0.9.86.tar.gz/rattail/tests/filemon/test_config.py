# -*- coding: utf-8 -*-

from __future__ import unicode_literals

import os
from unittest import TestCase

from fixture import TempIO

from rattail.config import make_config
from rattail.filemon import config
from rattail.filemon import Action
from rattail.exceptions import ConfigurationError


class TestProfile(TestCase):

    def setUp(self):
        self.config = make_config([])
        self.config.set(u'rattail.filemon', u'foo.actions', u'bar')

    def test_empty_config_means_empty_profile(self):
        profile = config.Profile(self.config, u'nonexistent_key')
        self.assertEqual(len(profile.dirs), 0)
        self.assertFalse(profile.watch_locks)
        self.assertTrue(profile.process_existing)
        self.assertFalse(profile.stop_on_error)
        self.assertEqual(len(profile.actions), 0)

    def test_action_must_specify_callable(self):
        self.assertRaises(ConfigurationError, config.Profile, self.config, u'foo')

    def test_action_must_not_specify_both_func_and_class_callables(self):
        self.config.set(u'rattail.filemon', u'foo.action.bar.class', u'baz')
        self.config.set(u'rattail.filemon', u'foo.action.bar.func', u'baz')
        self.assertRaises(ConfigurationError, config.Profile, self.config, u'foo')

    def test_action_with_func_callable(self):
        self.config.set(u'rattail.filemon', u'foo.action.bar.func', u'os:remove')
        profile = config.Profile(self.config, u'foo')
        self.assertEqual(len(profile.actions), 1)
        action = profile.actions[0]
        self.assertEqual(action.spec, u'os:remove')
        self.assertTrue(action.action is os.remove)

    def test_action_with_class_callable(self):
        self.config.set(u'rattail.filemon', u'foo.action.bar.class', u'rattail.filemon:Action')
        profile = config.Profile(self.config, u'foo')
        self.assertEqual(len(profile.actions), 1)
        action = profile.actions[0]
        self.assertEqual(action.spec, u'rattail.filemon:Action')
        self.assertTrue(isinstance(action.action, Action))

    def test_action_with_args(self):
        self.config.set(u'rattail.filemon', u'foo.action.bar.func', u'shutil:move')
        self.config.set(u'rattail.filemon', u'foo.action.bar.args', u'/dev/null')
        profile = config.Profile(self.config, u'foo')
        self.assertEqual(len(profile.actions), 1)
        action = profile.actions[0]
        self.assertEqual(len(action.args), 1)
        self.assertEqual(action.args[0], u'/dev/null')

    def test_action_with_kwargs(self):
        self.config.set(u'rattail.filemon', u'foo.action.bar.func', u'rattail.filemon.actions:raise_exception')
        self.config.set(u'rattail.filemon', u'foo.action.bar.kwarg.message', u"Hello World")
        profile = config.Profile(self.config, u'foo')
        self.assertEqual(len(profile.actions), 1)
        action = profile.actions[0]
        self.assertEqual(len(action.kwargs), 1)
        self.assertEqual(action.kwargs[u'message'], u"Hello World")

    def test_action_with_default_retry(self):
        self.config.set(u'rattail.filemon', u'foo.action.bar.func', u'rattail.filemon.actions:noop')
        profile = config.Profile(self.config, u'foo')
        self.assertEqual(len(profile.actions), 1)
        action = profile.actions[0]
        self.assertEqual(action.retry_attempts, 1)
        self.assertEqual(action.retry_delay, 0)

    def test_action_with_valid_configured_retry(self):
        self.config.set(u'rattail.filemon', u'foo.action.bar.func', u'rattail.filemon.actions:noop')
        self.config.set(u'rattail.filemon', u'foo.action.bar.retry_attempts', u'42')
        self.config.set(u'rattail.filemon', u'foo.action.bar.retry_delay', u'100')
        profile = config.Profile(self.config, u'foo')
        self.assertEqual(len(profile.actions), 1)
        action = profile.actions[0]
        self.assertEqual(action.retry_attempts, 42)
        self.assertEqual(action.retry_delay, 100)

    def test_action_with_invalid_configured_retry(self):
        self.config.set(u'rattail.filemon', u'foo.action.bar.func', u'rattail.filemon.actions:noop')
        self.config.set(u'rattail.filemon', u'foo.action.bar.retry_attempts', u'-1')
        self.config.set(u'rattail.filemon', u'foo.action.bar.retry_delay', u'-1')
        profile = config.Profile(self.config, u'foo')
        self.assertEqual(len(profile.actions), 1)
        action = profile.actions[0]
        self.assertEqual(action.retry_attempts, 1)
        self.assertEqual(action.retry_delay, 0)

    def test_normalize_dirs(self):
        tmp = TempIO()
        dir1 = tmp.mkdir(u'dir1')
        # dir2 will be pruned due to its not existing
        dir2 = tmp.mkdir(u'dir2')
        os.rmdir(dir2)
        # file1 will be pruned due to its not being a directory
        file1 = tmp.putfile(u'file1', u'')
        self.config.set(u'rattail.filemon', u'foo.action.bar.func', u'os:remove')
        self.config.set(u'rattail.filemon', u'foo.dirs', u' '.join([u'"{0}"'.format(d) for d in [dir1, dir2, file1]]))
        profile = config.Profile(self.config, u'foo')
        self.assertEqual(len(profile.dirs), 1)
        self.assertEqual(profile.dirs[0], dir1)


class TestLoadProfiles(TestCase):

    def setUp(self):
        self.tmp = TempIO()
        self.config = make_config([])
        self.config.set(u'rattail.filemon', u'monitor', u'foo, bar')
        self.config.set(u'rattail.filemon', u'foo.dirs', u'"{0}"'.format(self.tmp))
        self.config.set(u'rattail.filemon', u'foo.actions', u'delete')
        self.config.set(u'rattail.filemon', u'foo.action.delete.func', u'os:remove')
        self.config.set(u'rattail.filemon', u'bar.dirs', u'"{0}"'.format(self.tmp))
        self.config.set(u'rattail.filemon', u'bar.actions', u'delete')
        self.config.set(u'rattail.filemon', u'bar.action.delete.func', u'os:remove')

    def test_returns_all_profiles_specified_in_monitor_option(self):
        monitored = config.load_profiles(self.config)
        self.assertEqual(len(monitored), 2)
        # leave profiles intact but replace monitor option with one key only
        self.config.set(u'rattail.filemon', u'monitor', u'foo')
        monitored = config.load_profiles(self.config)
        self.assertEqual(len(monitored), 1)

    def test_monitor_option_must_be_specified(self):
        # TODO: This seems hacky.
        self.config.parser.remove_option('rattail.filemon', 'monitor')
        self.assertRaises(ConfigurationError, config.load_profiles, self.config)

    def test_profiles_which_define_no_watched_folders_are_pruned(self):
        monitored = config.load_profiles(self.config)
        self.assertEqual(len(monitored), 2)
        # remove foo's watched folder(s)
        # TODO: This seems hacky.
        self.config.parser.remove_option('rattail.filemon', 'foo.dirs')
        monitored = config.load_profiles(self.config)
        self.assertEqual(len(monitored), 1)

    def test_profiles_which_define_no_actions_are_pruned(self):
        monitored = config.load_profiles(self.config)
        self.assertEqual(len(monitored), 2)
        # remove foo's actions
        # TODO: This seems hacky.
        self.config.parser.remove_option('rattail.filemon', 'foo.actions')
        monitored = config.load_profiles(self.config)
        self.assertEqual(len(monitored), 1)

    def test_fallback_to_legacy_mode(self):
        # replace 'monitor' option with 'monitored' and update profiles accordingly
        # TODO: This seems hacky.
        self.config.parser.remove_option('rattail.filemon', 'monitor')
        self.config.set(u'rattail.filemon', u'monitored', u'foo, bar')
        self.config.set(u'rattail.filemon', u'foo.dirs', u"['{0}']".format(self.tmp))
        self.config.set(u'rattail.filemon', u'foo.actions', u"['os:remove']")
        self.config.set(u'rattail.filemon', u'bar.dirs', u"['{0}']".format(self.tmp))
        self.config.set(u'rattail.filemon', u'bar.actions', u"['os:remove']")
        monitored = config.load_profiles(self.config)
        self.assertEqual(len(monitored), 2)
        profiles = list(monitored.values())
        self.assertTrue(isinstance(profiles[0], config.LegacyProfile))
        self.assertTrue(isinstance(profiles[1], config.LegacyProfile))


class TestLegacyProfile(TestCase):

    def setUp(self):
        self.config = make_config([])

    def test_empty_config_means_empty_profile(self):
        profile = config.LegacyProfile(self.config, u'nonexistent_key')
        self.assertEqual(len(profile.dirs), 0)
        self.assertFalse(profile.watch_locks)
        self.assertTrue(profile.process_existing)
        self.assertFalse(profile.stop_on_error)
        self.assertEqual(len(profile.actions), 0)

    def test_action_with_spec_only(self):
        self.config.set(u'rattail.filemon', u'foo.actions', u"['os:remove']")
        profile = config.LegacyProfile(self.config, u'foo')
        self.assertEqual(len(profile.actions), 1)
        spec, action, args, kwargs = profile.actions[0]
        self.assertEqual(spec, u'os:remove')
        self.assertTrue(action is os.remove)

    def test_action_with_spec_and_args(self):
        self.config.set(u'rattail.filemon', u'foo.actions', u"[('shutil:move', u'/dev/null')]")
        profile = config.LegacyProfile(self.config, u'foo')
        self.assertEqual(len(profile.actions), 1)
        spec, action, args, kwargs = profile.actions[0]
        self.assertEqual(spec, u'shutil:move')
        self.assertEqual(len(args), 1)
        self.assertEqual(args[0], u'/dev/null')

    def test_normalize_dirs(self):
        tmp = TempIO()
        dir1 = tmp.mkdir(u'dir1')
        # dir2 will be pruned due to its not existing
        dir2 = tmp.mkdir(u'dir2')
        os.rmdir(dir2)
        # file1 will be pruned due to its not being a directory
        file1 = tmp.putfile(u'file1', u'')
        self.config.set(u'rattail.filemon', u'foo.dirs', u"[{0}]".format(u', '.join([u"'{0}'".format(d) for d in [dir1, dir2, file1]])))
        profile = config.LegacyProfile(self.config, u'foo')
        self.assertEqual(len(profile.dirs), 1)
        self.assertEqual(profile.dirs[0], dir1)


class TestLoadLegacyProfiles(TestCase):

    def setUp(self):
        self.tmp = TempIO()
        self.config = make_config([])
        self.config.set(u'rattail.filemon', u'monitored', u'foo, bar')
        self.config.set(u'rattail.filemon', u'foo.dirs', u"['{0}']".format(self.tmp))
        self.config.set(u'rattail.filemon', u'foo.actions', u"['os:remove']")
        self.config.set(u'rattail.filemon', u'bar.dirs', u"['{0}']".format(self.tmp))
        self.config.set(u'rattail.filemon', u'bar.actions', u"['os:remove']")

    def test_returns_all_profiles_specified_in_monitor_option(self):
        monitored = config.load_legacy_profiles(self.config)
        self.assertEqual(len(monitored), 2)
        # leave profiles intact but replace monitored option with one key only
        self.config.set(u'rattail.filemon', u'monitored', u'foo')
        monitored = config.load_legacy_profiles(self.config)
        self.assertEqual(len(monitored), 1)

    def test_monitor_option_must_be_specified(self):
        # TODO: This seems hacky.
        self.config.parser.remove_option('rattail.filemon', 'monitored')
        self.assertRaises(ConfigurationError, config.load_legacy_profiles, self.config)

    def test_profiles_which_define_no_watched_folders_are_pruned(self):
        monitored = config.load_legacy_profiles(self.config)
        self.assertEqual(len(monitored), 2)
        # remove foo's watched folder(s)
        # TODO: This seems hacky.
        self.config.parser.remove_option('rattail.filemon', 'foo.dirs')
        monitored = config.load_legacy_profiles(self.config)
        self.assertEqual(len(monitored), 1)

    def test_profiles_which_define_no_actions_are_pruned(self):
        monitored = config.load_legacy_profiles(self.config)
        self.assertEqual(len(monitored), 2)
        # remove foo's actions
        # TODO: This seems hacky.
        self.config.parser.remove_option('rattail.filemon', 'foo.actions')
        monitored = config.load_legacy_profiles(self.config)
        self.assertEqual(len(monitored), 1)
