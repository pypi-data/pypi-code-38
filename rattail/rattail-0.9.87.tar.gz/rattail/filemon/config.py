# -*- coding: utf-8; -*-
################################################################################
#
#  Rattail -- Retail Software Framework
#  Copyright © 2010-2018 Lance Edgar
#
#  This file is part of Rattail.
#
#  Rattail is free software: you can redistribute it and/or modify it under the
#  terms of the GNU General Public License as published by the Free Software
#  Foundation, either version 3 of the License, or (at your option) any later
#  version.
#
#  Rattail is distributed in the hope that it will be useful, but WITHOUT ANY
#  WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
#  FOR A PARTICULAR PURPOSE.  See the GNU General Public License for more
#  details.
#
#  You should have received a copy of the GNU General Public License along with
#  Rattail.  If not, see <http://www.gnu.org/licenses/>.
#
################################################################################
"""
File Monitor Configuration
"""

from __future__ import unicode_literals, absolute_import

import os
import re
import getpass
import warnings
import logging

from rattail.config import parse_list
from rattail.util import load_object
from rattail.exceptions import ConfigurationError
from rattail.filemon.actions import CommandAction


log = logging.getLogger(__name__)


class ProfileAction(object):
    """
    Simple class to hold configuration for a particular action defined within a
    monitor :class:`Profile`.  Each instance has the following attributes:

    .. attribute:: spec

       The original "spec" string used to obtain the action callable.

    .. attribute:: action

       A reference to the action callable.

    .. attribute:: args

       A sequence of positional arguments to be passed to the callable (in
       addition to the file path) when invoking the action.

    .. attribute:: kwargs

       A dictionary of keyword arguments to be passed to the callable (in
       addition to the positional arguments) when invoking the action.

    .. attribute:: retry_attempts

       Number of attempts to make when invoking the action.  Defaults to ``1``,
       meaning the first attempt will be made but no retries will happen.

    .. attribute:: retry_delay

       Number of seconds to pause between retry attempts, if
       :attr:`retry_attempts` is greater than one.  Defaults to ``0``.
    """

    spec = None
    action = None
    args = []
    kwargs = {}
    retry_attempts = 1
    retry_delay = 0


class Profile(object):
    """
    Simple class to hold configuration for a file monitor "profile".  The
    profile determines which folders to watch, which actions to take when new
    files appear, etc.  Each instance of this class has the following
    attributes:

    .. attribute:: config

       Reference to the underlying configuration object from which the profile
       derives its other attributes.

    .. attribute:: key

       String which differentiates this profile from any others which may exist
       within the configuration.

    .. attribute:: dirs

       List of directory paths which should be watched by the file monitor on
       behalf of this profile.

    .. attribute:: watch_locks

       Whether the file monitor should watch for new files, or disappearance of
       file locks.

       If ``False`` (the default), the file monitor will not use any special
       logic and will simply be on the lookout for any new files to appear;
       when they do, the configured action(s) will be invoked.

       If this setting is ``True``, then the simple appearance of a new file
       will not in itself cause any action(s) being taken.  Instead, the file
       monitor will only watch for the *disappearance* of file "locks",
       i.e. any file or directory whose name ends in ``".lock"``.  When the
       disappearance of such a lock is noticed, the configured action(s) will
       be invoked.

    .. attribute:: process_existing

       Whether any pre-existing files present in the watched folder(s) should
       be automatically added to the processing queue.

       If this is ``True`` (the default), then when the file monitor first
       starts, it will examine each watched folder to see if it already
       contains files.  If it does, then each file will be added to the
       processing queue exactly as if the monitor had just noticed the file
       appear.  The files will be added in order of creation timestam, in an
       effort to be consistent with the real-time behavior.

       If this setting is ``False``, any files which happen to exist when the
       file monitor first starts will be ignored.

    .. attribute:: stop_on_error

       Whether the file monitor should halt processing for all future files, if
       a single error is encountered.

       If this is ``True``, then if a single file action raises an exception,
       all subsequent files to appear will be effectively ignored.  No further
       actions will be taken for any of them.

       If this is ``False`` (the default), then a single file error will only
       cause processing to halt for that particular file.  Subsequent files
       which appear will still be processed as normal.

    .. attribute:: actions

       List of :class:`ProfileAction` instances representing the actions to be
       invoked when new files are discovered.
    """

    def __init__(self, config, key):
        self.config = config
        self.key = key

        self.dirs = self.normalize_dirs(self._config_list(u'dirs'))
        self.watch_locks = self._config_boolean(u'watch_locks', False)
        self.process_existing = self._config_boolean(u'process_existing', True)
        self.stop_on_error = self._config_boolean(u'stop_on_error', False)

        # These are only relevant on Windows, as of this writing.
        self.fallback_watcher_enable = self._config_boolean('fallback_watcher_enable', False)
        self.fallback_watcher_delay = self._config_int('fallback_watcher_delay', minimum=1)
        self.fallback_watcher_maxage = self._config_int('fallback_watcher_maxage', minimum=1)
        self.fallback_watcher_minage = self._config_int('fallback_watcher_minage', minimum=1)

        self.actions = []
        for action in self._config_list(u'actions'):
            self.actions.append(self._config_action(action))

    def _config_action(self, name):
        function = self._config_string('action.{}.func'.format(name))
        class_ = self._config_string('action.{}.class'.format(name))
        cmd = self._config_string('action.{}.cmd'.format(name))

        specs = [1 if spec else 0 for spec in (function, class_, cmd)]
        if sum(specs) != 1:
            raise ConfigurationError(
                "File monitor profile '{}' (action '{}') must have exactly one of: "
                "function, class, command".format(self.key, name))

        action = ProfileAction()
        action.config = self.config

        if function:
            action.spec = function
            action.action = load_object(action.spec)
        elif class_:
            action.spec = class_
            action.action = load_object(action.spec)(self.config)
        elif cmd:
            action.spec = cmd
            action.action = CommandAction(self.config, cmd)

        action.args = self._config_list(u'action.{0}.args'.format(name))

        action.kwargs = {}
        pattern = re.compile(r'^{0}\.action\.{1}\.kwarg\.(?P<keyword>\w+)$'.format(self.key, name), re.IGNORECASE)
        for option in self.config.options(u'rattail.filemon'):
            match = pattern.match(option)
            if match:
                action.kwargs[match.group(u'keyword')] = self.config.get(u'rattail.filemon', option)

        action.retry_attempts = self._config_int(u'action.{0}.retry_attempts'.format(name), minimum=1)
        action.retry_delay = self._config_int(u'action.{0}.retry_delay'.format(name), minimum=0)
        return action

    def _config_boolean(self, option, default=None):
        return self.config.getbool('rattail.filemon', '{0}.{1}'.format(self.key, option),
                                   default=default)

    def _config_int(self, option, minimum=0):
        option = u'{0}.{1}'.format(self.key, option)
        if self.config.has_option(u'rattail.filemon', option):
            value = self.config.getint(u'rattail.filemon', option)
            if value < minimum:
                log.warning(u"config value {0} is too small; falling back to minimum "
                            u"of {1} for option: {2}".format(value, minimum, option))
                value = minimum
        else:
            value = minimum
        return value

    def _config_list(self, option):
        return parse_list(self._config_string(option))

    def _config_string(self, option):
        return self.config.get(u'rattail.filemon', u'{0}.{1}'.format(self.key, option))

    def normalize_dirs(self, dirs):
        """
        Normalize a list of directory paths.  Converts all to absolute paths,
        and prunes those which do not exist or do not refer to directories.
        """
        normalized = []
        user = getpass.getuser()
        for path in dirs:
            path = os.path.abspath(path)
            if not os.path.exists(path):
                log.warning("pruning folder which does not exist (or perhaps is "
                            "just not visible? check perms for '%s' user!) for "
                            "profile '%s': %s", user, self.key, path)
                continue
            if not os.path.isdir(path):
                log.warning(u"pruning folder which is not a directory for profile "
                            u"{0}: {1}".format(repr(self.key), repr(path)))
                continue
            normalized.append(path)
        return normalized


def load_profiles(config):
    """
    Load all active file monitor profiles defined within configuration.
    """
    # Make sure we have a top-level directive.
    keys = config.get(u'rattail.filemon', u'monitor')
    if not keys:

        # No?  What about with the old syntax?
        keys = config.get(u'rattail.filemon', u'monitored')
        if keys:
            return load_legacy_profiles(config)

        # Still no?  That's no good..
        raise ConfigurationError(
            u"The file monitor configuration does not specify any profiles "
            u"to be monitored.  Please defined the 'monitor' option within "
            u"the [rattail.filemon] section of your config file.")

    monitored = {}
    for key in parse_list(keys):
        profile = Profile(config, key)
        if not profile.dirs:
            log.warning(u"profile '{0}' has no valid directories to watch".format(key))
            continue
        if not profile.actions:
            log.warning(u"profile '{0}' has no valid actions to invoke".format(key))
            continue
        monitored[key] = profile

    return monitored


class LegacyProfile(Profile):
    """
    This is a file monitor profile corresponding to the first generation of
    configuration syntax.  E.g. it only supports function-based actions, and
    does not support keyword arguments.

    .. note::
       This profile type will be deprecated at some point in the future.  All
       new code should assume use :class:`Profile` instead.
    """

    def __init__(self, config, key):
        self.config = config
        self.key = key

        dirs = self._config_string(u'dirs')
        if dirs:
            self.dirs = eval(dirs)
        else:
            self.dirs = []
        self.dirs = self.normalize_dirs(self.dirs)

        actions = self._config_string(u'actions')
        if actions:
            actions = eval(actions)
        else:
            actions = []

        self.actions = []
        for action in actions:
            if isinstance(action, tuple):
                spec = action[0]
                args = list(action[1:])
            else:
                spec = action
                args = []
            action = load_object(spec)
            self.actions.append((spec, action, args, {}))

        self.watch_locks = self._config_boolean(u'locks', False)
        self.process_existing = self._config_boolean(u'process_existing', True)
        self.stop_on_error = self._config_boolean(u'stop_on_error', False)


def load_legacy_profiles(config):
    """
    Load all active *legacy* file monitor profiles defined within
    configuration.
    """
    warnings.warn(u"The use of legacy profiles is deprecated, and should be "
                  u"avoided.  Please update your configuration to use the new "
                  u"syntax as soon as possible.", DeprecationWarning)

    monitored = {}

    # Read monitor profile(s) from config.
    keys = config.get(u'rattail.filemon', u'monitored')
    if not keys:
        raise ConfigurationError(
            u"The file monitor configuration does not specify any profiles "
            u"to be monitored.  Please defined the 'monitor' option within "
            u"the [rattail.filemon] section of your config file.")
    keys = keys.split(u',')
    for key in keys:
        key = key.strip()
        log.debug(u"loading profile: {0}".format(key))
        monitored[key] = LegacyProfile(config, key)

    for key in list(monitored):
        profile = monitored[key]

        # Prune any profiles with no valid folders to monitor.
        if not profile.dirs:
            log.warning(u"profile has no folders to monitor, "
                        u"and will be pruned: {0}".format(key))
            del monitored[key]

        # Prune any profiles with no valid actions to perform.
        elif not profile.actions:
            log.warning(u"profile has no actions to perform, "
                        u"and will be pruned: {0}".format(key))
            del monitored[key]

    return monitored
