# Copyright (C) 2013-2019 Team tiramisu (see AUTHORS for all contributors)
#
# This program is free software: you can redistribute it and/or modify it
# under the terms of the GNU Lesser General Public License as published by the
# Free Software Foundation, either version 3 of the License, or (at your
# option) any later version.
#
# This program is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
# FOR A PARTICULAR PURPOSE.  See the GNU Lesser General Public License for more
# details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
# ____________________________________________________________

"""Config's informations are, by default, volatiles. This means, all values and
settings changes will be lost.

The storage is the system Tiramisu uses to communicate with various DB.
You can specified a persistent storage.

Storage is basic components used to set Config informations in DB.
"""


from time import time
from random import randint
from os import environ
from os.path import split
from typing import Dict
from ..error import ConfigError
from ..i18n import _


DEFAULT_STORAGE = MEMORY_STORAGE = 'dictionary'
MODULE_PATH = split(split(split(__file__)[0])[0])[1]


class Storage:
    """Object to store storage's type. If a Config is already set,
    default storage is store as selected storage. You cannot change it
    after.
    """
    def __init__(self,
                 **kwargs: Dict[str, str]) -> None:
        self.storage_type = None
        self.mod = None
        self.setting(**kwargs)

    def get(self):
        if self.storage_type is None:
            self.storage_type = environ.get('TIRAMISU_STORAGE', DEFAULT_STORAGE)
        if self.mod is None:
            modulepath = '{0}.storage.{1}'.format(MODULE_PATH,
                                                  self.storage_type)
            try:
                mod = __import__(modulepath)
            except ImportError:  # pragma: no cover
                raise SystemError(_('cannot import the storage {0}').format(
                    self.storage_type))
            for token in modulepath.split(".")[1:]:
                mod = getattr(mod, token)
            self.mod = mod
        return self.mod

    def setting(self,
                **kwargs: Dict[str, str]) -> None:
        if 'engine' in kwargs:
            name = kwargs['engine']
            if self.storage_type is not None and self.storage_type != name:  # pragma: no cover
                raise ConfigError(_('storage_type is already set, '
                                    'cannot rebind it'))
            self.storage_type = name
            del kwargs['engine']
        if kwargs:  # pragma: no cover
            mod = self.get()
            for key, value in kwargs.items():
                setattr(mod.SETTING, key, value)

    def is_persistent(self):
        mod = self.get()
        return mod.PERSISTENT


default_storage = Storage()
memory_storage = Storage(engine=MEMORY_STORAGE)


def gen_storage_id(session_id,
                   config):
    if session_id is not None:
        return session_id
    return 'c' + str(id(config)) + str(int(time())) + str(randint(0, 500))


def get_storages(context,
                 session_id,
                 persistent,
                 storage):
    session_id = gen_storage_id(session_id,
                                context)
    if storage is None:
        storage = default_storage
    imp = storage.get()
    imp_storage = imp.Storage(session_id,
                              persistent)
    properties = imp.Properties(imp_storage)
    permissives = imp.Permissives(imp_storage)
    values = imp.Values(imp_storage)
    return properties, permissives, values, session_id


def get_default_values_storages():
    imp = memory_storage.get()
    storage = imp.Storage('__validator_storage', persistent=False, test=True)
    return imp.Values(storage)


def get_default_settings_storages():
    imp = memory_storage.get()
    storage = imp.Storage('__validator_storage', persistent=False, test=True)
    properties = imp.Properties(storage)
    permissives = imp.Permissives(storage)
    return properties, permissives


def list_sessions(storage=default_storage):
    """List all available session (persistent or not persistent)
    """
    return storage.get().list_sessions()


def delete_session(session_id, storage=default_storage):
    """Delete a selected session, be careful, you can deleted a session
    use by an other instance
    :params session_id: id of session to delete
    """
    storage_module = storage.get()
    session = storage_module.storage.getsession()
    storage_module.value.delete_session(session_id)
    storage_module.storage.delete_session(session_id)
    if session:  # pragma: no cover
        session.commit()
    del(session)


__all__ = ('list_sessions', 'delete_session')
