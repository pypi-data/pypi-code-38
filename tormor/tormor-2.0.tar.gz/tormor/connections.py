import asyncpg
import asyncio
from tormor.exceptions import SchemaNotPresent

class Connection(object):
    
    def __init__(self, dsn):
        try:
            self.loop = asyncio.get_event_loop()
            self.conn = self.loop.run_until_complete(asyncpg.connect(dsn))
            self._modules = set()
        except Exception as e:
            raise e

    async def execute_in_transaction(self, sql_queries):
        async with self.conn.transaction(isolation='serializable'):
            await self.conn.execute(sql_queries)

    def execute(self, sql_queries):
        self.loop.run_until_complete(self.execute_in_transaction(sql_queries))

    async def fetch_in_transaction(self, sql_queries):
        async with self.conn.transaction(isolation='serializable'):
            result = await self.conn.fetch(sql_queries)
            return result

    def fetch(self, sql_queries):
        return self.loop.run_until_complete(self.fetch_in_transaction(sql_queries))

    def load_modules(self):
        try:
            name_records = self.fetch("SELECT name FROM module")
            self._modules = set(each_record.get("name") for each_record in name_records)
        except asyncpg.UndefinedTableError:
            raise SchemaNotPresent
        return self._modules

    def assert_module(self, module):
        if module not in self.load_modules():
            raise ModuleNotFoundError

    def close(self):
        self.loop.run_until_complete(self.conn.close()) 