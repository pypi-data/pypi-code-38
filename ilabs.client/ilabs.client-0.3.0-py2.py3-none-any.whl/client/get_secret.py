from __future__ import absolute_import, unicode_literals

import os
try:
    import configparser
except ImportError:
    import ConfigParser as configparser

_SECTIONS = ['ilabs', 'default']


def get_secret():
    '''Implements strategy for obtaining user key from the runtime context:

    1. Environment variables ILABS_USER_KEY, ILABS_DATAVAULT_KEY
    2. User config file in `~/.config/ilabs/ilabs.conf` (in `[ilabs]` section
        or `[default]` section)
    3. System-wide config file `/etc/ilabs.conf` (in `[ilabs]` section
       or `[default]` section)

    Sample config file:

        [default]
        ilabs_user_key=1234567890
        ilabs_datavault_key=asdnasfsdafsdfbsdfbsdb

    '''

    return dict(
        ilabs_user_key=_get('ILABS_USER_KEY'),
        ilabs_datavault_key=_get('ILABS_DATAVAULT_KEY')
    )


def _get(key):
    value = os.environ.get(key.upper())
    if value is not None:
        return value

    config = configparser.ConfigParser()
    config.read([
        '/etc/ilabs.conf',
        os.path.expanduser(r'~/.config/ilabs/ilabs.conf')
    ])

    for section in _SECTIONS:
        try:
            return config.get(section, key.lower())
        except configparser.NoSectionError:
            pass
        except configparser.NoOptionError:
            pass
