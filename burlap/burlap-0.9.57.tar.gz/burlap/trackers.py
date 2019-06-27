from __future__ import print_function

import os
import hashlib
import pickle
from copy import deepcopy
try:
    from commands import getoutput
except ImportError:
    from subprocess import getoutput

import six


class BaseTracker:

    def __init__(self, action=None):
        if action:
            assert callable(action), 'Action %s is not callable.' % action
        self.action = action

    def natural_key(self):
        """
        This is a string or sequence that uniquely identifies this tracker.
        """
        raise NotImplementedError

    def get_natural_key_hash(self):
        m = hashlib.md5()
        m.update(pickle.dumps(self.natural_key()))
        return m.digest()

    def get_thumbprint(self):
        """
        Calculates the current thumbprint of the item being tracked.
        """
        raise NotImplementedError

    def is_changed(self, last_thumbprint):
        current_thumbprint = self.get_thumbprint()
        #print('is_changed.tracker:', self)
        #print('is_changed.last_thumbprint:', last_thumbprint)
        #print('is_changed.current_thumbprint:', current_thumbprint)
        return current_thumbprint != last_thumbprint

    def act(self):
        """
        Executes the cached task. This is called by the containing satchel's configure() when `is_changed()` returns True.
        """
        if self.action:
            self.action()


class FilesystemTracker(BaseTracker):
    """
    Tracks changes to a local filesystem directory.

    Has only two custom parameters:

        base_dir = The absolute or relative local directory to search.
        extensions = A space delimited list of extension patterns to limit the search.
            These patterns are feed directly to the `find` command.
    """

    def __init__(self, base_dir='.', extensions='*.*', *args, **kwargs):
        assert os.path.isdir(base_dir), 'Directory %s does not exist.' % base_dir
        extensions = extensions.strip()
        assert extensions, 'No extensions specified.'
        super(FilesystemTracker, self).__init__(*args, **kwargs)
        self.base_dir = base_dir
        self.extensions = extensions

    def __repr__(self):
        return '<%s %s %s>' % (type(self).__name__, self.base_dir, self.extensions)

    def natural_key(self):
        return (self.base_dir, self.extensions)

    def get_thumbprint(self):
        """
        Calculates the current thumbprint of the item being tracked.
        """
        extensions = self.extensions.split(' ')
        name_str = ' -or '.join('-name "%s"' % ext for ext in extensions)
        cmd = 'find ' + self.base_dir + r' -type f \( ' + name_str + r' \) -exec md5sum {} \; | sort -k 2 | md5sum'
        return getoutput(cmd)


class SettingsTracker(BaseTracker):
    """
    Tracks changes to one or more satchel settings.

    Has only two custom parameters:

        satchel = The satchel instance that contains the settings to track.
        names = A comma or space delimited list of setting names. If nothing specified, all names in the satchel will be tracked.
    """

    def __init__(self, satchel, names=None, *args, **kwargs):
        if isinstance(names, six.string_types):
            names = names.replace(',', ' ').split(' ')
        names = names or []
        assert isinstance(names, (tuple, list, set))
        names = sorted(set(_.strip() for _ in names if _.strip()))
        super(SettingsTracker, self).__init__(*args, **kwargs)
        self.satchel = satchel
        self.names = names

    @property
    def names_string(self):
        return ', '.join(self.names)

    def __repr__(self):
        return '<%s %s %s>' % (type(self).__name__, self.satchel.name, self.names_string)

    def natural_key(self):
        return (type(self.satchel).__name__, self.names_string)

    def get_thumbprint(self):
        """
        Calculates the current thumbprint of the item being tracked.
        """
        d = {}
        if self.names:
            names = self.names
        else:
            names = list(self.satchel.lenv)
        for name in self.names:
            d[name] = deepcopy(self.satchel.env[name])
        return d


class ORTracker(BaseTracker):
    """
    Computers a logical OR between two or more other trackers.
    """

    def __init__(self, *trackers, **kwargs):
        assert isinstance(trackers, (tuple, list))
        assert trackers, 'No trackers specified.'
        super(ORTracker, self).__init__(**kwargs)
        self.trackers = list(trackers)

    def __repr__(self):
        return '<%s %s>' % (type(self).__name__, self.trackers)

    def natural_key(self):
        lst = [type(self).__name__]
        for tracker in self.trackers:
            lst.extend(tracker.natural_key())
        return tuple(lst)

    def get_thumbprint(self):
        """
        Calculates the current thumbprint of the item being tracked.
        """
        d = {}
        for tracker in self.trackers:
            d[type(tracker).__name__] = tracker.get_thumbprint()
        return d
