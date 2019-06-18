from copy import deepcopy

from guillotina import configure
from guillotina.component import get_utility
from guillotina.db.factory import PostgresqlDatabaseManager
from guillotina.db.factory import _convert_dsn
from guillotina.db.interfaces import IDatabaseManager
from guillotina.event import notify
from guillotina.events import DatabaseInitializedEvent
from guillotina.interfaces import IApplication
from guillotina.interfaces import IDatabase
from guillotina.interfaces import IDatabaseConfigurationFactory
from guillotina.utils import apply_coroutine


app_settings = {
}


@configure.adapter(
    for_=IApplication,  # noqa: N801
    provides=IDatabaseManager,
    name='prefixed-table')
class PrefixedDatabaseManager(PostgresqlDatabaseManager):
    _connection_managers = {}  # shared on all instances

    def get_dsn(self, name: str = None) -> str:
        if isinstance(self.config['dsn'], str):
            return self.config['dsn']
        else:
            return _convert_dsn(self.config['dsn'])

    async def get_names(self) -> list:
        conn = await self.get_connection()
        try:
            result = await conn.fetch('''
SELECT table_name FROM information_schema.tables WHERE table_schema='public'
''')
            return [
                item['table_name'].replace('_objects', '') for item in result
                if item['table_name'].endswith('_objects')]
        finally:
            await conn.close()
        return []

    async def create(self, name: str) -> bool:
        # creates db here...
        db = await self.get_database(name)
        return db is not None

    async def delete(self, name: str) -> bool:
        if name in self.app:
            await self.app[name].finalize()
            del self.app[name]

        conn = await self.get_connection()
        try:
            for table_name in ('blobs', 'objects'):
                await conn.execute(
                    'DROP TABLE IF EXISTS {}_{}'.format(name, table_name))
            return True
        finally:
            await conn.close()
        return False

    async def get_database(self, name: str) -> IDatabase:
        if name not in self.app:
            config = deepcopy(self.config)
            config.update({
                'dsn': self.get_dsn(name),
                'objects_table_name': name + '_objects',
                'blobs_table_name': name + '_blobs'
            })
            if self.config['storage_id'] in self._connection_managers:
                config['connection_manager'] = self._connection_managers[
                    self.config['storage_id']]
            factory = get_utility(
                IDatabaseConfigurationFactory, name=config['storage'])
            self.app[name] = await apply_coroutine(factory, name, config)

            if self.config['storage_id'] not in self._connection_managers:
                storage = self.app[name].storage
                self._connection_managers[
                    self.config['storage_id']] = storage.connection_manager
                self._connection_managers[
                    self.config['storage_id']]._closable = False
            await notify(DatabaseInitializedEvent(self.app[name]))

        return self.app[name]

    async def exists(self, name: str) -> bool:
        conn = await self.get_connection()
        try:
            result = await conn.fetch('''
select * FROM information_schema.tables
WHERE table_schema='public' and table_name = '{}_objects'
        '''.format(name))
            return len(result) > 0
        finally:
            await conn.close()
        return False


def includeme(root):
    """
    """
    pass
